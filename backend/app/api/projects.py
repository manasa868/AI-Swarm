"""Project Management and Swarm Orchestration Endpoints."""
import os
import uuid
import datetime
import json
import zipfile
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.database.models import Project, Task, AgentRun, TestResult, Review, Document
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.file_service import FileService
from app.services.uml_service import (
    DIAGRAMS,
    generate_project_diagrams,
    get_diagram_path,
    render_diagram_export,
)
from app.config import settings

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_project_or_404(project_id: str, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/diagrams/generate")
def generate_uml_diagrams(project_id: str, db: Session = Depends(get_db)):
    """Analyze the generated source and create the project's five UML diagrams."""
    project = _get_project_or_404(project_id, db)
    try:
        diagrams = generate_project_diagrams(project.id, project.name, project.description)
    except (OSError, ValueError, SyntaxError) as exc:
        raise HTTPException(status_code=422, detail=f"Could not generate UML diagrams: {exc}") from exc
    return {"project_id": project_id, "diagrams": list(diagrams.values())}


@router.get("/{project_id}/diagrams")
def list_uml_diagrams(project_id: str, db: Session = Depends(get_db)):
    """Retrieve generated UML diagram metadata for a project."""
    _get_project_or_404(project_id, db)
    manifest_path = settings.GENERATED_DIR / project_id / "uml" / "manifest.json"
    if not manifest_path.is_file():
        raise HTTPException(status_code=404, detail="UML diagrams have not been generated yet.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=500, detail="Saved UML diagram manifest is unreadable.") from exc
    return manifest


@router.get("/{project_id}/diagrams/{diagram_id}")
def get_uml_diagram(project_id: str, diagram_id: str, db: Session = Depends(get_db)):
    """Serve the rendered SVG for one project-specific UML diagram."""
    _get_project_or_404(project_id, db)
    try:
        diagram_path = get_diagram_path(project_id, diagram_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(diagram_path, media_type="image/svg+xml")


@router.get("/{project_id}/diagrams/{diagram_id}/export")
def export_uml_diagram(
    project_id: str,
    diagram_id: str,
    format: str = "svg",
    db: Session = Depends(get_db),
):
    """Download a rendered UML diagram as SVG, PNG, or PDF."""
    _get_project_or_404(project_id, db)
    if format not in {"svg", "png", "pdf"}:
        raise HTTPException(status_code=400, detail="Export format must be svg, png, or pdf.")
    try:
        svg_path = get_diagram_path(project_id, diagram_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    try:
        output = render_diagram_export(svg_path, format)
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=500, detail=f"Could not render {format.upper()} export: {exc}") from exc
    media_type = {
        "svg": "image/svg+xml",
        "png": "image/png",
        "pdf": "application/pdf",
    }[format]
    return Response(
        content=output,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{diagram_id}.{format}"'},
    )


@router.get("/{project_id}/diagrams/export/all")
def download_all_uml_diagrams(project_id: str, db: Session = Depends(get_db)):
    """Download all five rendered UML diagrams in SVG, PNG, and PDF formats."""
    _get_project_or_404(project_id, db)
    archive_path = settings.DOCUMENTS_DIR / f"{project_id}_uml_diagrams.zip"
    try:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for diagram_id in DIAGRAMS:
                svg_path = get_diagram_path(project_id, diagram_id)
                for export_format in ("svg", "png", "pdf"):
                    archive.writestr(
                        f"{diagram_id}.{export_format}",
                        render_diagram_export(svg_path, export_format),
                    )
    except (ImportError, OSError, ValueError, KeyError, RuntimeError) as exc:
        raise HTTPException(status_code=404, detail=f"Could not package UML diagrams: {exc}") from exc
    return FileResponse(
        archive_path,
        media_type="application/zip",
        filename=f"{project_id}_uml_diagrams.zip",
    )


@router.post("", response_model=ProjectResponse)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new AI Swarm project."""
    project_id = f"proj_{uuid.uuid4().hex[:10]}"
    project = Project(
        id=project_id,
        name=data.name,
        description=data.description,
        project_type=data.project_type,
        technologies=data.technologies,
        status="PENDING",
        progress=0.0,
        retry_count=0,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """List all projects ordered by creation date."""
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get project details and execution status."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/stop")
def stop_project(project_id: str, db: Session = Depends(get_db)):
    """Cancel project execution."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.status = "CANCELLED"
    db.commit()
    return {"message": "Project execution cancelled", "status": "CANCELLED"}


@router.get("/{project_id}/files")
def get_project_files(project_id: str):
    """Retrieve hierarchical file tree of the generated project."""
    tree = FileService.get_file_tree(project_id)
    return {"project_id": project_id, "file_tree": tree}


@router.get("/{project_id}/files/content")
def get_file_content(project_id: str, path: str):
    """Read the source code content of a generated file."""
    try:
        content = FileService.read_file_content(project_id, path)
        return {"project_id": project_id, "path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{project_id}/download")
def download_project_archive(project_id: str):
    """Download the complete generated project repository as a ZIP archive."""
    try:
        zip_path = FileService.create_zip_archive(project_id)
        return FileResponse(
            path=str(zip_path),
            filename=f"{project_id}_codebase.zip",
            media_type="application/zip",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create archive: {str(e)}")


@router.get("/{project_id}/documentation")
def get_project_documentation(project_id: str, db: Session = Depends(get_db)):
    """Retrieve full dynamic markdown documentation and section structure."""
    doc = db.query(Document).filter(Document.project_id == project_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documentation not yet generated.")
    return {
        "title": doc.title,
        "content_markdown": doc.content_markdown,
        "sections": doc.sections,
        "created_at": doc.created_at,
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload project requirement file (PDF, TXT, CSV, DOCX, Code)."""
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension .{ext} not permitted. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )
    
    file_id = f"up_{uuid.uuid4().hex[:8]}_{file.filename}"
    save_path = settings.UPLOADS_DIR / file_id
    
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)
        
    return {
        "filename": file.filename,
        "saved_as": file_id,
        "size_bytes": len(content),
        "status": "UPLOADED"
    }

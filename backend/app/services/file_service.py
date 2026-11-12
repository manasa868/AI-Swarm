"""File Service for Project Generation, File Tree Exploration, and Archiving."""
import os
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Any, List
from app.config import settings


class FileService:
    @staticmethod
    def get_project_dir(project_id: str) -> Path:
        pdir = settings.GENERATED_DIR / project_id
        pdir.mkdir(parents=True, exist_ok=True)
        return pdir

    @staticmethod
    def write_project_files(project_id: str, files: Dict[str, str]) -> Path:
        """Write a dictionary of {relative_path: content} to the project directory."""
        project_dir = FileService.get_project_dir(project_id)
        for rel_path, content in files.items():
            file_path = project_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        return project_dir

    @staticmethod
    def get_file_tree(project_id: str) -> List[Dict[str, Any]]:
        """Return hierarchical file tree of the generated project."""
        project_dir = FileService.get_project_dir(project_id)
        if not project_dir.exists():
            return []

        def build_tree(path: Path) -> Dict[str, Any]:
            is_dir = path.is_dir()
            node = {
                "name": path.name,
                "path": str(path.relative_to(project_dir)).replace("\\", "/"),
                "is_dir": is_dir,
            }
            if is_dir:
                children = []
                for child in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                    # skip pycache or hidden files
                    if child.name.startswith(".") or child.name == "__pycache__":
                        continue
                    children.append(build_tree(child))
                node["children"] = children
            else:
                node["size"] = path.stat().st_size
                node["extension"] = path.suffix.lstrip(".")
            return node

        tree = []
        for item in sorted(project_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            if item.name.startswith(".") or item.name == "__pycache__":
                continue
            tree.append(build_tree(item))
        return tree

    @staticmethod
    def read_file_content(project_id: str, relative_path: str) -> str:
        """Safely read content of a generated file."""
        project_dir = FileService.get_project_dir(project_id)
        target = (project_dir / relative_path).resolve()
        # Security: prevent directory traversal
        if not str(target).startswith(str(project_dir.resolve())):
            raise ValueError("Unauthorized path traversal attempt.")
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"File not found: {relative_path}")
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    @staticmethod
    def create_zip_archive(project_id: str) -> Path:
        """Create a zip archive of the generated project."""
        project_dir = FileService.get_project_dir(project_id)
        zip_path = settings.DOCUMENTS_DIR / f"{project_id}_project.zip"
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(project_dir):
                for file in files:
                    if "__pycache__" in root or file.startswith("."):
                        continue
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(project_dir)
                    zipf.write(full_path, arcname=str(rel_path))
        return zip_path

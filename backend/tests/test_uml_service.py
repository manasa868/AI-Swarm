"""Tests for source-driven UML diagram generation and vector exports."""
import xml.etree.ElementTree as ET

from fastapi.testclient import TestClient

from app.database.models import Project
from app.database.session import SessionLocal
from app.main import app
from app.services import uml_service


client = TestClient(app)


def test_uml_diagrams_reflect_generated_classes_and_render_as_svg(tmp_path, monkeypatch):
    project_id = "uml_test_project"
    project_dir = tmp_path / project_id
    (project_dir / "src").mkdir(parents=True)
    (project_dir / "src" / "models.py").write_text(
        "class Account:\n"
        "    def __init__(self, account_id: str):\n"
        "        self.account_id = account_id\n"
        "    def close(self):\n"
        "        return None\n\n"
        "class PremiumAccount(Account):\n"
        "    def __init__(self, account_id: str, tier: str):\n"
        "        super().__init__(account_id)\n"
        "        self._tier = tier\n",
        encoding="utf-8",
    )
    (project_dir / "src" / "service.py").write_text(
        "from src.models import Account\n\n"
        "def load_account(account_id: str) -> Account:\n"
        "    return Account(account_id)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(uml_service.settings, "GENERATED_DIR", tmp_path)

    manifest = uml_service.generate_project_diagrams(project_id, "Account Platform")

    assert set(manifest) == {"use_case", "class", "sequence", "activity", "component"}
    assert manifest["class"]["classes"] == ["Account", "PremiumAccount"]
    assert len(manifest["component"]["source_files"]) == 2
    for diagram_id in manifest:
        svg_path = uml_service.get_diagram_path(project_id, diagram_id)
        root = ET.parse(svg_path).getroot()
        assert root.tag.endswith("svg")
        assert root.attrib["width"]
        assert root.attrib["height"]
        assert uml_service.render_diagram_export(svg_path, "png").startswith(b"\x89PNG")
        assert uml_service.render_diagram_export(svg_path, "pdf").startswith(b"%PDF")

    class_svg = (project_dir / "uml" / "class.svg").read_text(encoding="utf-8")
    assert "PremiumAccount" in class_svg
    assert "account_id" in class_svg
    assert "close()" in class_svg


def test_project_diagram_api_exports_all_formats(tmp_path, monkeypatch):
    project_id = "uml_api_test_project"
    monkeypatch.setattr(uml_service.settings, "GENERATED_DIR", tmp_path)
    monkeypatch.setattr(uml_service.settings, "DOCUMENTS_DIR", tmp_path)
    db = SessionLocal()
    project = Project(
        id=project_id,
        name="UML API test",
        description="Build a project with source classes for UML generation.",
        project_type="general",
        technologies=[],
        status="PENDING",
    )
    db.add(project)
    db.commit()
    db.close()
    (tmp_path / project_id).mkdir()
    (tmp_path / project_id / "core.py").write_text(
        "class Core:\n    def run(self):\n        return True\n",
        encoding="utf-8",
    )

    try:
        generated = client.post(f"/api/projects/{project_id}/diagrams/generate")
        assert generated.status_code == 200
        diagrams = generated.json()["diagrams"]
        assert len(diagrams) == 5

        for diagram in diagrams:
            svg = client.get(diagram["svg_url"])
            assert svg.status_code == 200
            assert svg.headers["content-type"].startswith("image/svg+xml")
            for export_format, mime_type in (
                ("svg", "image/svg+xml"),
                ("png", "image/png"),
                ("pdf", "application/pdf"),
            ):
                exported = client.get(f'{diagram["export_url"]}?format={export_format}')
                assert exported.status_code == 200
                assert exported.headers["content-type"].startswith(mime_type)
                expected_signature = {"svg": b"<svg", "png": b"\x89PNG", "pdf": b"%PDF"}[export_format]
                assert exported.content.startswith(expected_signature)

        archive = client.get(f"/api/projects/{project_id}/diagrams/export/all")
        assert archive.status_code == 200
        assert archive.headers["content-type"].startswith("application/zip")
    finally:
        db = SessionLocal()
        db.query(Project).filter(Project.id == project_id).delete()
        db.commit()
        db.close()

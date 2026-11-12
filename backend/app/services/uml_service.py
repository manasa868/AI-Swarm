"""Generate project-specific UML diagrams from generated source files."""
import ast
import html
import json
import re
import textwrap
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import xml.etree.ElementTree as ET

import resvg_py
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.config import settings


DIAGRAMS = {
    "use_case": ("Use Case Diagram", "Actors and capabilities available in the generated AI Swarm project."),
    "class": ("Class Diagram", "Classes, members, inheritance, and relationships extracted from project source."),
    "sequence": ("Sequence Diagram", "The project generation workflow, including test failures and correction."),
    "activity": ("Activity Diagram", "The execution and test-correction decisions from request to delivery."),
    "component": ("Component Diagram", "Generated source modules, backend services, storage, and model integration."),
}


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _wrap(value: str, width: int = 25) -> List[str]:
    lines = textwrap.wrap(str(value), width=width, break_long_words=True, break_on_hyphens=True)
    return lines or [""]


def _svg_start(title: str, description: str, width: int, height: int) -> List[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
        "<title id=\"title\">" + _escape(title) + "</title>",
        "<desc id=\"description\">" + _escape(description) + "</desc>",
        """<defs>
<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#94a3b8"/></marker>
<marker id="inherit" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L10,6 L0,12 z" fill="#0f172a" stroke="#38bdf8" stroke-width="1"/></marker>
<marker id="aggregation" markerWidth="14" markerHeight="14" refX="1" refY="7" orient="auto"><path d="M1,7 L7,1 L13,7 L7,13 z" fill="#08111f" stroke="#a78bfa" stroke-width="1.5"/></marker>
<marker id="composition" markerWidth="14" markerHeight="14" refX="1" refY="7" orient="auto"><path d="M1,7 L7,1 L13,7 L7,13 z" fill="#a78bfa" stroke="#a78bfa" stroke-width="1.5"/></marker>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#020617" flood-opacity=".35"/></filter>
</defs>
<style>
text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e2e8f0}
.title{font-size:25px;font-weight:700;fill:#f8fafc}.label{font-size:15px}.small{font-size:12px;fill:#cbd5e1}.muted{fill:#94a3b8}.node{fill:#111c31;stroke:#334155;stroke-width:1.5}.accent{stroke:#38bdf8}.edge{fill:none;stroke:#94a3b8;stroke-width:1.7;marker-end:url(#arrow)}.dash{stroke-dasharray:7 6}.actor{stroke:#38bdf8;stroke-width:2;fill:none}.class-head{fill:#12304a;stroke:#38bdf8;stroke-width:1.5}.component-head{fill:#12304a;stroke:#38bdf8;stroke-width:1.5}.decision{fill:#3a2a12;stroke:#f59e0b;stroke-width:1.7}.success{fill:#0c312b;stroke:#34d399}.error{fill:#351b28;stroke:#fb7185}
</style>
<rect width="100%" height="100%" fill="#08111f"/>
""",
        f'<text class="title" x="36" y="42">{_escape(title)}</text>',
    ]


def _text(lines: List[str], x: float, y: float, value: str, css: str = "label", anchor: str = "start", line_height: int = 18) -> None:
    wrapped = _wrap(value)
    lines.append(f'<text class="{css}" x="{x}" y="{y}" text-anchor="{anchor}">')
    for index, line in enumerate(wrapped):
        lines.append(f'<tspan x="{x}" dy="{0 if index == 0 else line_height}">{_escape(line)}</tspan>')
    lines.append("</text>")


def _project_files(project_id: str) -> Tuple[Path, List[Path]]:
    root = (settings.GENERATED_DIR / project_id).resolve()
    if not root.is_relative_to(settings.GENERATED_DIR.resolve()):
        raise ValueError("Invalid project identifier.")
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Generated source directory not found for project {project_id}.")
    files = [
        path for path in root.rglob("*.py")
        if "uml" not in path.relative_to(root).parts and "__pycache__" not in path.parts
    ]
    return root, sorted(files)


def _parse_source(files: Iterable[Path], root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]], List[str]]:
    classes: List[Dict[str, Any]] = []
    modules: Dict[str, List[str]] = {}
    source_names: List[str] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        module = relative[:-3].replace("/", ".")
        source_names.append(relative)
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=relative)
        except (OSError, SyntaxError):
            continue
        imported_modules: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module.split(".")[0])
        modules[module] = sorted(set(imported_modules))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            attributes: List[str] = []
            methods: List[str] = []
            relationships: List[Dict[str, str]] = []
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if member.name.startswith("__") and member.name.endswith("__") and member.name != "__init__":
                        continue
                    arguments = [arg.arg for arg in member.args.args if arg.arg != "self"]
                    visibility = "-" if member.name.startswith("_") else "+"
                    methods.append(f"{visibility} {member.name}({', '.join(arguments)})")
                    if member.name == "__init__":
                        argument_types = {
                            argument.arg: ast.unparse(argument.annotation)
                            for argument in member.args.args
                            if argument.arg != "self" and argument.annotation is not None
                        }
                        for item in ast.walk(member):
                            if isinstance(item, (ast.Assign, ast.AnnAssign)):
                                targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                                for target in targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                        visibility = "-" if target.attr.startswith("_") else "+"
                                        value = item.value
                                        annotation = ""
                                        relationship_kind = "association"
                                        if isinstance(value, ast.Name):
                                            annotation = argument_types.get(value.id, "")
                                        elif isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
                                            annotation = value.func.id
                                            relationship_kind = "composition"
                                        if isinstance(item, ast.AnnAssign):
                                            annotation = ast.unparse(item.annotation)
                                        suffix = f": {annotation}" if annotation else ""
                                        attributes.append(f"{visibility} {target.attr}{suffix}")
                                        if annotation:
                                            targets_in_type = re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", annotation)
                                            for target_type in targets_in_type:
                                                relationships.append({
                                                    "target": target_type,
                                                    "kind": "aggregation" if any(token in annotation for token in ("List[", "list[", "Set[", "set[", "Dict[", "dict[")) else relationship_kind,
                                                    "multiplicity": "0..*" if any(token in annotation for token in ("List[", "list[", "Set[", "set[", "Dict[", "dict[")) else "1",
                                                })
                elif isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name):
                    visibility = "-" if member.target.id.startswith("_") else "+"
                    annotation = ast.unparse(member.annotation)
                    attributes.append(f"{visibility} {member.target.id}: {annotation}")
                    for target_type in re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", annotation):
                        relationships.append({
                            "target": target_type,
                            "kind": "aggregation" if any(token in annotation for token in ("List[", "list[", "Set[", "set[", "Dict[", "dict[")) else "association",
                            "multiplicity": "0..*" if any(token in annotation for token in ("List[", "list[", "Set[", "set[", "Dict[", "dict[")) else "1",
                        })
            bases = [ast.unparse(base).split(".")[-1] for base in node.bases]
            classes.append({
                "name": node.name,
                "module": module,
                "attributes": list(dict.fromkeys(attributes))[:8],
                "methods": list(dict.fromkeys(methods))[:8],
                "bases": bases,
                "relationships": relationships,
            })
    return classes, modules, source_names


def _use_case_svg(project_name: str, width: int = 1320, height: int = 790) -> str:
    lines = _svg_start("Use Case Diagram", f"Use cases for {project_name}", width, height)
    lines.append('<rect class="node" x="290" y="92" width="820" height="650" rx="18"/>')
    _text(lines, 700, 124, f"{project_name} System", "label", "middle")
    actor_specs = [("User", 125, 265), ("Administrator", 125, 515), ("AI Agents", 1170, 385)]
    for label, x, y in actor_specs:
        lines.append(f'<circle class="actor" cx="{x}" cy="{y - 28}" r="16"/>')
        lines.append(f'<path class="actor" d="M{x} {y - 12}v48m-25 -26h50m-25 26-21 30m21-30 21 30"/>')
        _text(lines, x, y + 80, label, "small", "middle")
    use_cases = [
        ("Submit project request", 420, 190),
        ("Configure project & files", 700, 190),
        ("Monitor agent workflow", 980, 190),
        ("Generate project code", 420, 340),
        ("Test & correct code", 700, 340),
        ("Review generated output", 980, 340),
        ("View project files", 420, 500),
        ("Download project & diagrams", 700, 500),
        ("Manage projects & users", 980, 500),
        ("Generate documentation", 700, 650),
    ]
    for label, x, y in use_cases:
        lines.append(f'<ellipse class="node accent" cx="{x}" cy="{y}" rx="112" ry="38"/>')
        _text(lines, x, y + 5, label, "small", "middle")
    for x, y in [(420, 190), (700, 190), (980, 190), (420, 500), (700, 500), (700, 650)]:
        lines.append(f'<path class="edge" d="M150 265 C210 265 235 {y} {x - 116} {y}"/>')
    for x, y in [(980, 500), (980, 340), (700, 340)]:
        lines.append(f'<path class="edge" d="M150 515 C220 515 230 {y} {x - 116} {y}"/>')
    for x, y in [(420, 340), (700, 340), (980, 340), (700, 650)]:
        lines.append(f'<path class="edge" d="M1148 385 C1115 385 1110 {y} {x + 116} {y}"/>')
    lines.append('<path class="edge dash" d="M532 340H588"/>')
    _text(lines, 560, 326, "«include»", "small", "middle")
    lines.append('<path class="edge dash" d="M812 340H868"/>')
    _text(lines, 840, 326, "«extend»", "small", "middle")
    lines.append("</svg>")
    return "".join(lines)


def _class_svg(project_name: str, classes: List[Dict[str, Any]], width: int = 1600) -> str:
    if not classes:
        classes = [{"name": "SourceModule", "module": "generated project", "attributes": ["+ source files"], "methods": ["+ generated()"], "bases": [], "relationships": []}]
    columns = 3
    card_width = 460
    gap_x = 38
    gap_y = 40
    cards: List[Dict[str, Any]] = []
    for index, item in enumerate(classes):
        attrs = item["attributes"] or ["(no declared attributes)"]
        methods = item["methods"] or ["(no declared methods)"]
        card_height = 88 + (len(attrs) + len(methods)) * 20
        cards.append({
            **item,
            "x": 40 + (index % columns) * (card_width + gap_x),
            "y": 92 + (index // columns) * 470,
            "width": card_width,
            "height": card_height,
        })
    rows = (len(cards) + columns - 1) // columns
    height = max(420, 150 + rows * 470)
    lines = _svg_start("Class Diagram", f"Classes parsed from {project_name} generated source", width, height)
    by_name = {item["name"]: item for item in cards}
    for item in cards:
        for base in item["bases"]:
            parent = by_name.get(base)
            if parent:
                x1 = item["x"] + item["width"] / 2
                y1 = item["y"]
                x2 = parent["x"] + parent["width"] / 2
                y2 = parent["y"] + parent["height"]
                lines.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#inherit)"/>')
        for relation in item["relationships"]:
            target = by_name.get(relation["target"])
            if target and target["name"] != item["name"]:
                marker = "aggregation" if relation["kind"] == "aggregation" else "composition" if relation["kind"] == "composition" else None
                marker_attr = f' marker-start="url(#{marker})"' if marker else ""
                edge_class = "edge dash" if relation["kind"] == "association" else "edge"
                lines.append(f'<path class="{edge_class}" d="M{item["x"] + item["width"]} {item["y"] + 48} C{item["x"] + item["width"] + 18} {item["y"] + 48} {target["x"] - 18} {target["y"] + 48} {target["x"]} {target["y"] + 48}"{marker_attr}/>')
                _text(lines, (item["x"] + item["width"] + target["x"]) / 2, item["y"] + 42, relation["multiplicity"], "small", "middle")
    for item in cards:
        x, y, w, h = item["x"], item["y"], item["width"], item["height"]
        lines.append(f'<rect class="node" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>')
        lines.append(f'<rect class="class-head" x="{x}" y="{y}" width="{w}" height="60" rx="8"/>')
        _text(lines, x + w / 2, y + 22, item["module"], "small muted", "middle")
        _text(lines, x + w / 2, y + 43, item["name"], "label", "middle")
        divider1 = y + 60
        lines.append(f'<line x1="{x}" y1="{divider1}" x2="{x+w}" y2="{divider1}" stroke="#334155"/>')
        cursor = divider1 + 20
        for attribute in item["attributes"]:
            _text(lines, x + 14, cursor, attribute, "small")
            cursor += 20
        lines.append(f'<line x1="{x}" y1="{cursor+2}" x2="{x+w}" y2="{cursor+2}" stroke="#334155"/>')
        cursor += 22
        for method in item["methods"]:
            _text(lines, x + 14, cursor, method, "small")
            cursor += 20
    lines.append("</svg>")
    return "".join(lines)


def _sequence_svg(project_name: str, width: int = 1850, height: int = 1450) -> str:
    participants = ["User", "Coordinator", "Planner", "Research Agent", "Coding Agent", "Testing Agent", "Reviewer", "Documentation Agent"]
    lines = _svg_start("Sequence Diagram", f"Agent execution sequence for {project_name}", width, height)
    spacing = width / (len(participants) + 1)
    positions = [spacing * (index + 1) for index in range(len(participants))]
    for x, name in zip(positions, participants):
        lines.append(f'<rect class="node accent" x="{x-88}" y="80" width="176" height="54" rx="8"/>')
        _text(lines, x, 112, name, "small", "middle")
        lines.append(f'<line x1="{x}" y1="134" x2="{x}" y2="1000" stroke="#64748b" stroke-dasharray="7 7"/>')
    messages = [
        (0, 1, "Submit project request", False),
        (1, 2, "Analyze requirements", False),
        (2, 1, "Return dependency-mapped plan", True),
        (1, 3, "Research requirements & patterns", False),
        (3, 1, "Return research findings", True),
        (1, 4, "Generate source code", False),
        (4, 1, "Save generated source files", True),
        (1, 5, "Execute tests", False),
        (5, 1, "Return test results", True),
    ]
    y = 180
    for source, target, label, response in messages:
        x1, x2 = positions[source], positions[target]
        lines.append(f'<rect x="{x1-7}" y="{y-2}" width="14" height="54" fill="#0e7490" opacity=".8" rx="4"/>')
        dash = ' stroke-dasharray="7 5"' if response else ""
        lines.append(f'<line x1="{x1}" y1="{y+34}" x2="{x2}" y2="{y+34}" stroke="#38bdf8" stroke-width="2"{dash} marker-end="url(#arrow)"/>')
        _text(lines, (x1 + x2) / 2, y + 17, label, "small", "middle")
        y += 86
    left = positions[4] - 34
    right = positions[5] + 34
    lines.append(f'<rect x="{left}" y="{y-8}" width="{right-left}" height="400" fill="none" stroke="#f59e0b" stroke-width="1.5" rx="8"/>')
    _text(lines, left + 14, y + 18, "alt: tests pass / tests fail", "small")
    y += 45
    lines.append(f'<line x1="{positions[5]}" y1="{y}" x2="{positions[1]}" y2="{y}" stroke="#fb7185" stroke-width="2" marker-end="url(#arrow)"/>')
    _text(lines, (positions[5] + positions[1]) / 2, y - 10, "Failure diagnostics (if tests fail)", "small", "middle")
    y += 65
    lines.append(f'<line x1="{positions[1]}" y1="{y}" x2="{positions[4]}" y2="{y}" stroke="#f59e0b" stroke-width="2" marker-end="url(#arrow)"/>')
    _text(lines, (positions[1] + positions[4]) / 2, y - 10, "Correct code and request re-test", "small", "middle")
    y += 65
    lines.append(f'<line x1="{positions[1]}" y1="{y}" x2="{positions[5]}" y2="{y}" stroke="#f59e0b" stroke-width="2" marker-end="url(#arrow)"/>')
    _text(lines, (positions[1] + positions[5]) / 2, y - 10, "Re-run tests (up to 3 corrections)", "small", "middle")
    lines.append(f'<line x1="{positions[1]}" y1="{y+76}" x2="{positions[6]}" y2="{y+76}" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>')
    _text(lines, (positions[1] + positions[6]) / 2, y + 66, "Successful test results forwarded for review", "small", "middle")
    lines.append(f'<line x1="{positions[6]}" y1="{y+126}" x2="{positions[7]}" y2="{y+126}" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>')
    _text(lines, (positions[6] + positions[7]) / 2, y + 116, "Approved source and review", "small", "middle")
    lines.append(f'<line x1="{positions[7]}" y1="{y+176}" x2="{positions[0]}" y2="{y+176}" stroke="#34d399" stroke-width="2" marker-end="url(#arrow)"/>')
    _text(lines, (positions[0] + positions[7]) / 2, y + 166, f"Deliver {project_name} and documentation", "small", "middle")
    lines.append("</svg>")
    return "".join(lines)


def _activity_svg(project_name: str, width: int = 1250, height: int = 1320) -> str:
    lines = _svg_start("Activity Diagram", f"Activity flow for {project_name}", width, height)
    x = width / 2
    nodes = [
        ("start", "Start", 90),
        ("round", "User submits project request", 165),
        ("round", "Coordinator analyzes requirements", 245),
        ("round", "Planner decomposes into tasks", 325),
        ("round", "Research agent analyzes architecture", 405),
        ("round", "Coding agent generates project files", 485),
        ("round", "Testing agent executes test suite", 565),
    ]
    for kind, label, y in nodes:
        if kind == "start":
            lines.append(f'<circle cx="{x}" cy="{y}" r="19" fill="#38bdf8"/>')
        else:
            lines.append(f'<rect class="node accent" x="{x-190}" y="{y-27}" width="380" height="54" rx="24"/>')
            _text(lines, x, y+5, label, "small", "middle")
    for y in [110, 192, 272, 352, 432, 512]:
        lines.append(f'<line class="edge" x1="{x}" y1="{y}" x2="{x}" y2="{y+28}"/>')
    decision_y = 665
    lines.append(f'<path class="decision" d="M{x} {decision_y-46} l145 46 -145 46 -145-46z"/>')
    _text(lines, x, decision_y+5, "Tests pass?", "small", "middle")
    lines.append(f'<line class="edge" x1="{x}" y1="592" x2="{x}" y2="{decision_y-46}"/>')
    _text(lines, x+165, decision_y-12, "No", "small")
    lines.append(f'<rect class="node error" x="{x+245}" y="742" width="315" height="62" rx="12"/>')
    _text(lines, x+402, 778, "Capture errors & traceback", "small", "middle")
    lines.append(f'<path class="edge" d="M{x+120} {decision_y+16} C{x+235} {decision_y+16} {x+235} 772 {x+245} 772"/>')
    lines.append(f'<rect class="node" x="{x+245}" y="850" width="315" height="62" rx="12"/>')
    _text(lines, x+402, 886, "Coding agent fixes generated code", "small", "middle")
    lines.append(f'<line class="edge" x1="{x+402}" y1="804" x2="{x+402}" y2="850"/>')
    lines.append(f'<path class="edge" d="M{x+245} 881 C{x+40} 970 {x-225} 850 {x-190} 565"/>')
    _text(lines, x+17, 955, "Retest (max 3 correction attempts)", "small")
    _text(lines, x-165, decision_y-12, "Yes", "small", "end")
    lines.append(f'<line class="edge" x1="{x}" y1="{decision_y+46}" x2="{x}" y2="780"/>')
    for y, label in [(815, "Reviewer validates code quality"), (895, "Generate documentation & UML diagrams"), (975, "Package project files for delivery")]:
        lines.append(f'<rect class="node success" x="{x-220}" y="{y}" width="440" height="54" rx="22"/>')
        _text(lines, x, y+33, label, "small", "middle")
        lines.append(f'<line class="edge" x1="{x}" y1="{y-35}" x2="{x}" y2="{y}"/>')
    lines.append(f'<line class="edge" x1="{x}" y1="1029" x2="{x}" y2="1080"/>')
    lines.append(f'<rect class="node success" x="{x-220}" y="1080" width="440" height="54" rx="22"/>')
    _text(lines, x, 1113, f"Deliver {project_name} to user", "small", "middle")
    lines.append(f'<line class="edge" x1="{x}" y1="1134" x2="{x}" y2="1190"/>')
    lines.append(f'<circle cx="{x}" cy="1212" r="20" fill="#34d399"/><circle cx="{x}" cy="1212" r="13" fill="none" stroke="#08111f" stroke-width="2"/>')
    lines.append("</svg>")
    return "".join(lines)


def _component_svg(project_name: str, modules: Dict[str, List[str]], width: int = 1500, height: int = 920) -> str:
    lines = _svg_start("Component Diagram", f"System components and generated source modules for {project_name}", width, height)
    components = [
        ("React Frontend", 55, 150, 265, 100),
        ("FastAPI Backend API", 420, 150, 280, 100),
        ("Coordinator Agent", 800, 95, 250, 85),
        ("Planner Agent", 800, 205, 250, 85),
        ("Research Agent", 800, 315, 250, 85),
        ("Coding Agent", 800, 425, 250, 85),
        ("Testing Agent", 800, 535, 250, 85),
        ("Reviewer Agent", 800, 645, 250, 85),
        ("SQLite Database", 1210, 150, 240, 100),
        ("Generated File Storage", 1210, 355, 240, 100),
        ("External AI Model/API", 1210, 575, 240, 100),
    ]
    module_nodes = []
    for index, module in enumerate(modules):
        y = 410 + index * 76
        module_nodes.append((module, 60, y, 320, 56))
    for label, x, y, w, h in components:
        lines.append(f'<rect class="node" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>')
        lines.append(f'<rect class="component-head" x="{x+12}" y="{y-10}" width="48" height="20" rx="3"/>')
        _text(lines, x+w/2, y+h/2+5, label, "small", "middle")
    for module, x, y, w, h in module_nodes:
        lines.append(f'<rect class="node accent" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>')
        _text(lines, x+w/2, y+34, module, "small", "middle")
        lines.append(f'<path class="edge" d="M{x+w} {y+h/2} C395 {y+h/2} 395 200 420 200"/>')
    connections = [
        (320, 200, 420, 200, "REST / SSE"),
        (700, 200, 800, 137, "dispatch"),
        (925, 180, 925, 205, "plan"),
        (925, 290, 925, 315, "research"),
        (925, 400, 925, 425, "source"),
        (925, 510, 925, 535, "tests"),
        (925, 620, 925, 645, "review"),
        (1050, 140, 1210, 200, "persistence"),
        (1050, 465, 1210, 405, "generated files"),
        (1050, 355, 1210, 625, "optional LLM"),
    ]
    for x1, y1, x2, y2, label in connections:
        lines.append(f'<path class="edge" d="M{x1} {y1} L{x2} {y2}"/>')
        _text(lines, (x1+x2)/2, (y1+y2)/2-8, label, "small muted", "middle")
    lines.append("</svg>")
    return "".join(lines)


def generate_project_diagrams(project_id: str, project_name: str, description: str = "") -> Dict[str, Dict[str, Any]]:
    root, source_files = _project_files(project_id)
    classes, modules, file_names = _parse_source(source_files, root)
    diagram_dir = root / "uml"
    diagram_dir.mkdir(parents=True, exist_ok=True)
    rendered = {
        "use_case": _use_case_svg(project_name),
        "class": _class_svg(project_name, classes),
        "sequence": _sequence_svg(project_name),
        "activity": _activity_svg(project_name),
        "component": _component_svg(project_name, modules),
    }
    manifest: Dict[str, Dict[str, Any]] = {}
    for diagram_id, svg in rendered.items():
        if not svg.startswith("<svg ") or "</svg>" not in svg:
            raise ValueError(f"Generated {diagram_id} diagram is not valid SVG.")
        file_path = diagram_dir / f"{diagram_id}.svg"
        file_path.write_text(svg, encoding="utf-8")
        title, explanation = DIAGRAMS[diagram_id]
        manifest[diagram_id] = {
            "id": diagram_id,
            "title": title,
            "description": explanation,
            "svg_url": f"/api/projects/{project_id}/diagrams/{diagram_id}",
            "export_url": f"/api/projects/{project_id}/diagrams/{diagram_id}/export",
            "classes": [item["name"] for item in classes],
            "source_files": file_names,
        }
    (diagram_dir / "manifest.json").write_text(
        json.dumps({"project_id": project_id, "diagrams": manifest}, indent=2),
        encoding="utf-8",
    )
    return manifest


def get_diagram_path(project_id: str, diagram_id: str) -> Path:
    if diagram_id not in DIAGRAMS:
        raise KeyError(f"Unknown UML diagram '{diagram_id}'.")
    root, _ = _project_files(project_id)
    path = (root / "uml" / f"{diagram_id}.svg").resolve()
    if not path.is_relative_to((root / "uml").resolve()) or not path.is_file():
        raise FileNotFoundError(f"UML diagram '{diagram_id}' has not been generated.")
    return path


def render_diagram_export(svg_path: Path, output_format: str) -> bytes:
    """Render a saved SVG into a downloadable PNG or PDF."""
    if output_format == "svg":
        return svg_path.read_bytes()
    if output_format not in {"png", "pdf"}:
        raise ValueError(f"Unsupported UML export format: {output_format}")

    png = resvg_py.svg_to_bytes(svg_path=str(svg_path), zoom=2)
    if output_format == "png":
        return png

    root = ET.parse(svg_path).getroot()
    view_box = root.attrib.get("viewBox", "").split()
    if len(view_box) != 4:
        raise ValueError("UML SVG has no valid viewBox for PDF export.")
    width = float(view_box[2])
    height = float(view_box[3])
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=(width * 0.75, height * 0.75), pageCompression=1)
    pdf.drawImage(
        ImageReader(BytesIO(png)),
        0,
        0,
        width=width * 0.75,
        height=height * 0.75,
        preserveAspectRatio=True,
    )
    pdf.showPage()
    pdf.save()
    return output.getvalue()

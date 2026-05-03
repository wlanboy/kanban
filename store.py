import json
from pathlib import Path
from model import Workspace, Lane, Card, Severity, ArchivedCard, ProjectEntry

STORAGE_FILE   = Path.home() / ".kanbantabs"
ARCHIVE_FILE   = Path.home() / ".kanbantabs_archive"
PROJECTS_FILE  = Path.home() / ".kanbantabs_projects"


def _parse_workspace(raw: dict) -> Workspace:
    lanes = [
        Lane(
            UUID=b["UUID"],
            Name=b["Name"],
            Items=[
                Card(ID=i["ID"], Name=i["Name"], Severity=Severity(i.get("Severity", 0)),
                     Description=i.get("Description", ""), DueDate=i.get("DueDate", ""))
                for i in b.get("Items", [])
            ],
        )
        for b in raw.get("Lanes", [])
    ]
    return Workspace(Name=raw.get("Name", "Kanban"), NextID=raw.get("NextID", 1), Lanes=lanes)


def _build_workspace_dict(ws: Workspace) -> dict:
    return {
        "Name":   ws.Name,
        "NextID": ws.NextID,
        "Lanes": [
            {
                "UUID":  lane.UUID,
                "Name":  lane.Name,
                "Items": [
                    {"ID": c.ID, "Name": c.Name, "Severity": int(c.Severity),
                     "Description": c.Description, "DueDate": c.DueDate}
                    for c in lane.Items
                ],
            }
            for lane in ws.Lanes
        ],
    }


def load() -> Workspace:
    return load_from(str(STORAGE_FILE))


def save(ws: Workspace) -> None:
    save_to(ws, str(STORAGE_FILE))


def load_from(path: str) -> Workspace:
    p = Path(path).expanduser()
    if not p.exists():
        return Workspace()
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return Workspace()
    return _parse_workspace(raw)


def save_to(ws: Workspace, path: str) -> None:
    p = Path(path).expanduser()
    p.write_text(json.dumps(_build_workspace_dict(ws), indent=2, ensure_ascii=False), encoding="utf-8")
    p.chmod(0o640)


def load_projects() -> list[ProjectEntry]:
    if not PROJECTS_FILE.exists():
        default = [ProjectEntry(name="Kanban", path=str(STORAGE_FILE))]
        save_projects(default)
        return default
    try:
        raw = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return [ProjectEntry(name="Kanban", path=str(STORAGE_FILE))]
    return [ProjectEntry(name=e["name"], path=e["path"]) for e in raw]


def save_projects(projects: list[ProjectEntry]) -> None:
    data = [{"name": p.name, "path": p.path} for p in projects]
    PROJECTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    PROJECTS_FILE.chmod(0o640)


def load_archive() -> list[ArchivedCard]:
    if not ARCHIVE_FILE.exists():
        return []
    try:
        raw = json.loads(ARCHIVE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    return [
        ArchivedCard(
            ID=e["ID"],
            Name=e["Name"],
            Severity=Severity(e.get("Severity", 0)),
            Description=e.get("Description", ""),
            LaneName=e.get("LaneName", ""),
            DueDate=e.get("DueDate", ""),
            ArchivedAt=e.get("ArchivedAt", ""),
        )
        for e in raw
    ]


def save_archive(archive: list[ArchivedCard]) -> None:
    data = [
        {
            "ID":          c.ID,
            "Name":        c.Name,
            "Severity":    int(c.Severity),
            "Description": c.Description,
            "LaneName":    c.LaneName,
            "DueDate":     c.DueDate,
            "ArchivedAt":  c.ArchivedAt,
        }
        for c in archive
    ]
    ARCHIVE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    ARCHIVE_FILE.chmod(0o640)

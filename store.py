import json
from pathlib import Path
from model import Workspace, Lane, Card, Severity, ArchivedCard

STORAGE_FILE  = Path.home() / ".kanbantabs"
ARCHIVE_FILE  = Path.home() / ".kanbantabs_archive"


def load() -> Workspace:
    if not STORAGE_FILE.exists():
        return Workspace()
    try:
        raw = json.loads(STORAGE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return Workspace()
    lanes = [
        Lane(
            UUID=b["UUID"],
            Name=b["Name"],
            Items=[
                Card(ID=i["ID"], Name=i["Name"], Severity=Severity(i.get("Severity", 0)), Description=i.get("Description", ""))
                for i in b.get("Items", [])
            ],
        )
        for b in raw.get("Lanes", [])
    ]
    return Workspace(Name=raw.get("Name", "Kanban"), NextID=raw.get("NextID", 1), Lanes=lanes)


def save(ws: Workspace) -> None:
    data = {
        "Name":   ws.Name,
        "NextID": ws.NextID,
        "Lanes": [
            {
                "UUID":  lane.UUID,
                "Name":  lane.Name,
                "Items": [
                    {"ID": c.ID, "Name": c.Name, "Severity": int(c.Severity), "Description": c.Description}
                    for c in lane.Items
                ],
            }
            for lane in ws.Lanes
        ],
    }
    STORAGE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    STORAGE_FILE.chmod(0o640)


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
            "ArchivedAt":  c.ArchivedAt,
        }
        for c in archive
    ]
    ARCHIVE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    ARCHIVE_FILE.chmod(0o640)

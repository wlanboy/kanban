import json
from pathlib import Path
from model import Workspace, Lane, Card, Severity

STORAGE_FILE = Path.home() / ".kanbantabs"


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

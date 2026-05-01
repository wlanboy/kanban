import uuid
from copy import deepcopy
from model import Workspace, Lane, Card, Severity


class UndoStack:
    def __init__(self, max_size: int = 20):
        self._stack: list[Workspace] = []
        self._max = max_size

    def push(self, ws: Workspace) -> None:
        self._stack.append(deepcopy(ws))
        if len(self._stack) > self._max:
            self._stack.pop(0)

    def pop(self) -> Workspace | None:
        return self._stack.pop() if self._stack else None

    def can_undo(self) -> bool:
        return bool(self._stack)


def add_lane(ws: Workspace, name: str) -> None:
    name = name.strip()[:20]
    if len(name) < 2:
        raise ValueError("Lane-Name muss mindestens 2 Zeichen haben.")
    ws.Lanes.append(Lane(UUID=str(uuid.uuid4()), Name=name))


def delete_lane(ws: Workspace, lane_index: int) -> None:
    ws.Lanes.pop(lane_index)


def add_card(ws: Workspace, lane_index: int, name: str, severity: Severity = Severity.LOW) -> None:
    name = name.strip()[:20]
    if len(name) < 2:
        raise ValueError("Card-Name muss mindestens 2 Zeichen haben.")
    card = Card(ID=ws.NextID, Name=name, Severity=severity)
    ws.NextID += 1
    ws.Lanes[lane_index].Items.append(card)


def delete_card(ws: Workspace, card_id: int) -> None:
    for lane in ws.Lanes:
        lane.Items = [c for c in lane.Items if c.ID != card_id]


def move_card_next(ws: Workspace, card_id: int) -> None:
    for i, lane in enumerate(ws.Lanes):
        for card in lane.Items:
            if card.ID == card_id:
                lane.Items.remove(card)
                if i + 1 < len(ws.Lanes):
                    ws.Lanes[i + 1].Items.append(card)
                return


def move_card_prev(ws: Workspace, card_id: int) -> None:
    for i, lane in enumerate(ws.Lanes):
        for card in lane.Items:
            if card.ID == card_id:
                lane.Items.remove(card)
                if i - 1 >= 0:
                    ws.Lanes[i - 1].Items.append(card)
                return


def move_card_to(ws: Workspace, card_id: int, target_lane_index: int) -> None:
    card = None
    for lane in ws.Lanes:
        for c in lane.Items:
            if c.ID == card_id:
                card = c
                lane.Items.remove(c)
                break
        if card:
            break
    if card:
        ws.Lanes[target_lane_index].Items.append(card)


def rename_card(ws: Workspace, card_id: int, new_name: str) -> None:
    for lane in ws.Lanes:
        for card in lane.Items:
            if card.ID == card_id:
                card.Name = new_name.strip()[:20]
                return


def cycle_severity(ws: Workspace, card_id: int) -> None:
    for lane in ws.Lanes:
        for card in lane.Items:
            if card.ID == card_id:
                card.Severity = Severity((int(card.Severity) + 1) % 3)
                return

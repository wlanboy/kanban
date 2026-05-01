# KanbanTabs TUI

Ein leichtgewichtiges, dateibasiertes Kanban-Board für das Terminal — vollständig in Python geschrieben mit [Textual](https://github.com/Textualize/textual).


```
 KanbanTabs                                                    [?] Hilfe
┌─────────────────────┬─────────────────────┬─────────────────────┐
│  todo         [✕]   │  working      [✕]   │  done         [✕]   │  [+ Lane]
│  ─────────────────  │  ─────────────────  │  ─────────────────  │
│ ▶ [1] chromebook    │    [3] kanbanTUI    │    [4] k3s   ●●     │
│   [2] hazelcast  ●  │                     │    [6] chromebook   │
│                     │                     │                     │
│                     │                     │                     │
│   [+ Card]          │   [+ Card]          │   [+ Card]          │
└─────────────────────┴─────────────────────┴─────────────────────┘
  n:Neu  d:Löschen  →:Weiter  m:Verschieben  r:Umbenennen  u:Undo  ?:Hilfe
```

---

## Features

- **Board-Ansicht** — alle Lanes und Cards in farbigen Spalten, immer sichtbar
- **Tastatur-Navigation** — Vim-Bindings (`j`/`k`, `h`/`l`) und Pfeiltasten
- **Card-Operationen** — anlegen, löschen, umbenennen, Priorität setzen, verschieben
- **Lane-Operationen** — anlegen, löschen
- **Freies Verschieben** — Card direkt in beliebige Lane per Modal
- **Prioritäten** — LOW / MEDIUM `●` / HIGH `●●` mit Farbindikator
- **Undo** — bis zu 20 Schritte rückgängig
- **Suche** — Filter über alle Card-Namen in Echtzeit
- **Hilfe-Overlay** — vollständige Tastatur-Referenz per `?`
- **Persistenz** — automatisches Speichern nach jeder Aktion in `~/.kanbantabs` (JSON)
- **Go-Kompatibilität** — dieselbe Datei wie die Go-CLI-Version `kanbantabs`

---

## Voraussetzungen

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (empfohlen) oder pip

---

## Starten

```bash
# Mit uv
uv run python main.py

# Mit aktiviertem venv
python main.py

# Mit Live-Reload (Entwicklung)
uv run textual run --dev main.py
```

---

## Tutorial

### Erste Schritte

Beim ersten Start ist das Board leer. Lege zunächst ein paar Lanes an:

1. Drücke `a` — ein Dialog öffnet sich
2. Gib einen Lane-Namen ein, z. B. `todo`
3. Drücke `Enter` oder klicke `Anlegen`
4. Wiederhole für weitere Lanes, z. B. `doing` und `done`

```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│  todo         [✕]   │  doing        [✕]   │  done         [✕]   │  [+ Lane]
│                     │                     │                     │
│   [+ Card]          │   [+ Card]          │   [+ Card]          │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

---

### Cards anlegen

1. Drücke `n` (oder klicke `[+ Card]` in der gewünschten Lane)
2. Gib einen Namen ein (2–20 Zeichen)
3. Wähle die Ziel-Lane
4. Wähle eine Priorität: `LOW`, `MEDIUM` oder `HIGH`
5. Drücke `Enter`

**Prioritäten im Überblick:**

| Symbol | Bedeutung |
|--------|-----------|
| `·` (grau) | LOW — normale Aufgabe |
| `●` (gelb) | MEDIUM — erhöhte Priorität |
| `●●` (rot) | HIGH — dringend |

---

### Navigation

Bewege den Fokus mit der Tastatur durch das Board:

| Taste | Aktion |
|-------|--------|
| `j` / `↓` | Card nach unten |
| `k` / `↑` | Card nach oben |
| `Tab` | Nächste Lane |
| `Shift+Tab` | Vorherige Lane |

Die aktuell fokussierte Card wird mit einem dicken blauen Rahmen hervorgehoben.

---

### Cards bearbeiten

Fokussiere eine Card (Navigation s. o.) und nutze dann:

| Taste | Aktion |
|-------|--------|
| `→` / `l` | Card in nächste Lane verschieben |
| `←` / `h` | Card in vorherige Lane verschieben |
| `m` | Card in beliebige Lane verschieben (Modal) |
| `r` | Card umbenennen |
| `s` | Priorität zyklisch wechseln (LOW → MEDIUM → HIGH → LOW) |
| `d` | Card löschen (mit Bestätigung) |

> **Hinweis:** Wird eine Card aus der letzten Lane mit `→` verschoben, wird sie gelöscht — das entspricht dem Abschluss einer Aufgabe.

---

### Lanes verwalten

| Taste | Aktion |
|-------|--------|
| `a` | Neue Lane anlegen |
| `D` | Fokussierte Lane löschen (mit Bestätigung) |
| `[✕]` | Lane über den Button im Header löschen |

---

### Suche

Drücke `/` um die Suchleiste zu öffnen. Das Board filtert sofort während der Eingabe — nicht passende Cards werden ausgegraut. Drücke `Escape` oder nochmals `/` um die Suche zu schließen.

---

### Undo

Jede Aktion (Anlegen, Löschen, Verschieben, Umbenennen, Priorität ändern) kann mit `u` rückgängig gemacht werden. Der Stack hält bis zu 20 Schritte.

---

### Hilfe

Drücke `?` jederzeit für das vollständige Tastatur-Overlay. `Escape` schließt es wieder.

---

## Datenspeicherung

Alle Daten werden automatisch in `~/.kanbantabs` gespeichert — eine einzelne JSON-Datei:

```json
{
  "Name": "Kanban",
  "NextID": 7,
  "Lanes": [
    {
      "UUID": "a1b2c3d4-...",
      "Name": "todo",
      "Items": [
        { "ID": 1, "Name": "mein task", "Severity": 0 }
      ]
    }
  ]
}
```

Die Datei ist vollständig kompatibel mit der Go-CLI-Version `kanbantabs` — beide Tools können dieselbe Datei lesen und schreiben.

---

## Entwicklung

```bash
# Abhängigkeiten inkl. Dev-Tools installieren
uv sync --group dev

# App mit Live-Reload und DOM-Inspector
uv run textual run --dev main.py

# Linting
uv run ruff check .

# Typprüfung
uv run pyright .
```

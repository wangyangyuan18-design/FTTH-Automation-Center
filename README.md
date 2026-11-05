# FTTH Automation Center

Portable Windows desktop controller for repeatable FTTH/ODN workflows.

## Architecture

- `desktop/`: Python + PySide6 controller.
- `qgis_bridge/`: QGIS plugin that executes commands inside the QGIS process.
- Local-only HTTP bridge on `127.0.0.1:47831`; no external network listener.
- Each workflow is independent. A failed workflow does not start another workflow.
- Workflow implementations must validate inputs, create backups before edits, verify outputs, and return structured reports.

## Current status

**Framework scaffold — not yet connected to the production ODN naming implementation.**

Workflow 01 currently performs a safe preflight and reports that the naming adapter is not configured. It deliberately does not modify layer names or attributes until the exact callable entry points and fixed parameters from the user's working ODN_Tools_Pro package have been inspected.

## Development

Python 3.11+ recommended for the desktop controller:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m desktop.main
```

Install the `qgis_bridge` folder as a QGIS plugin named `FTTH_Automation_Bridge`, enable it, and restart QGIS.

## Safety

- Never write to source layers before preflight and backup succeed.
- Workflow 01 is isolated and may be rerun independently.
- The bridge binds only to localhost.
- Do not assume plugin APIs from older ODN_Tools_Pro versions; integrate against the user's current working ZIP and test in QGIS.

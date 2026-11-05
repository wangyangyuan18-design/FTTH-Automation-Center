"""Windows UI Automation probe for QGIS. Inspection/focus only; no edits or clicks."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from pywinauto import Desktop

def find_qgis_windows():
    found = []
    try:
        for win in Desktop(backend="uia").windows():
            try:
                title = win.window_text() or ""
                if "qgis" in title.lower():
                    found.append(("uia", win, title))
            except Exception:
                continue
    except Exception:
        pass
    return found

def inspect_qgis():
    windows = find_qgis_windows()
    if not windows:
        return {"ok": False, "message": "没有发现标题包含 QGIS 的窗口。请确认 QGIS 已打开。", "windows": []}
    output = []
    for backend, win, title in windows:
        item = {"backend": backend, "title": title, "rect": _rect(win), "controls": []}
        try:
            for control in win.descendants():
                try:
                    info = {
                        "type": control.element_info.control_type,
                        "name": control.window_text() or "",
                        "automation_id": control.element_info.automation_id or "",
                        "class_name": control.element_info.class_name or "",
                        "enabled": bool(control.is_enabled()),
                        "visible": bool(control.is_visible()),
                        "rect": _rect(control),
                    }
                    if info["name"] or info["automation_id"]:
                        item["controls"].append(info)
                except Exception:
                    pass
        except Exception as exc:
            item["inspection_error"] = str(exc)
        output.append(item)
    return {"ok": True, "message": f"发现 {len(output)} 个 QGIS 窗口。", "windows": output}

def focus_qgis():
    windows = find_qgis_windows()
    if not windows:
        return {"ok": False, "message": "没有发现 QGIS 窗口。"}
    _, win, title = windows[0]
    win.set_focus()
    return {"ok": True, "message": f"已将 QGIS 窗口置于前台：{title}"}

def save_desktop_report(data):
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path.home()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = desktop / f"FTTH_QGIS_UI_Report_{stamp}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)

def _rect(control):
    try:
        r = control.rectangle()
        return {"left": r.left, "top": r.top, "right": r.right, "bottom": r.bottom}
    except Exception:
        return None

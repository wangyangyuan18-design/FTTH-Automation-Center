"""QGIS-side localhost bridge. HTTP threads enqueue work; QGIS API runs on GUI thread."""
from __future__ import annotations

import json
import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from qgis.PyQt.QtCore import QTimer
from qgis.core import Qgis, QgsProject, QgsApplication


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class FTTHAutomationBridge:
    HOST = "127.0.0.1"
    PORT = 47831

    def __init__(self, iface):
        self.iface = iface
        self.jobs = queue.Queue()
        self.health_snapshot = {
            "ok": True, "qgis_version": Qgis.QGIS_VERSION,
            "project": "读取中", "project_layer_count": 0,
        }
        self.server = None
        self.server_thread = None
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._drain_jobs)

    def initGui(self):
        self._start_server()
        self.timer.start()
        self.iface.messageBar().pushMessage(
            "FTTH Automation Bridge", "本机通信服务已启动",
            level=Qgis.Info, duration=4
        )

    def unload(self):
        self.timer.stop()
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def _start_server(self):
        plugin = self

        class Handler(BaseHTTPRequestHandler):
            def _send(self, status, obj):
                body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path != "/health":
                    return self._send(404, {"ok": False, "error": "not_found"})
                # Read a GUI-thread snapshot only; never call PyQGIS from this HTTP thread.
                self._send(200, dict(plugin.health_snapshot))

            def do_POST(self):
                if self.path != "/task/run":
                    return self._send(404, {"ok": False, "error": "not_found"})
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    if size <= 0 or size > 65536:
                        raise ValueError("invalid_payload_size")
                    payload = json.loads(self.rfile.read(size).decode("utf-8"))
                    if payload.get("workflow") != "01_point_line_naming":
                        return self._send(400, {"ok": False, "error": "unknown_workflow"})
                    job_id = plugin._enqueue(payload)
                    self._send(202, {"ok": True, "job_id": job_id, "state": "QUEUED"})
                except Exception as exc:
                    self._send(400, {"ok": False, "error": str(exc)})

            def log_message(self, *_args):
                pass

        self.server = _Server((self.HOST, self.PORT), Handler)
        self.server_thread = threading.Thread(
            target=self.server.serve_forever, name="FTTHBridgeHTTP", daemon=True
        )
        self.server_thread.start()

    def _enqueue(self, payload):
        import uuid
        job_id = uuid.uuid4().hex[:12]
        self.jobs.put((job_id, payload))
        return job_id

    def _drain_jobs(self):
        # QGIS project access is confined to this QTimer callback on the GUI thread.
        project = QgsProject.instance()
        self.health_snapshot = {
            "ok": True,
            "qgis_version": Qgis.QGIS_VERSION,
            "project": project.fileName() or "未保存/未打开",
            "project_layer_count": len(project.mapLayers()),
        }
        while not self.jobs.empty():
            job_id, payload = self.jobs.get()
            try:
                result = self._run_workflow_01()
                self.iface.messageBar().pushMessage(
                    "FTTH 功能01", result,
                    level=Qgis.Warning, duration=10
                )
            except Exception as exc:
                self.iface.messageBar().pushMessage(
                    "FTTH 功能01失败", str(exc),
                    level=Qgis.Critical, duration=0
                )

    def _run_workflow_01(self):
        """Safe first-stage implementation: preflight only; no layer edits yet."""
        project = QgsProject.instance()
        if not project.mapLayers():
            return "检查未通过：当前 QGIS 工程没有图层。未修改任何数据。"

        # The production naming adapter is intentionally not guessed.
        # It will be wired after inspecting the user's current working ODN_Tools_Pro ZIP.
        return (
            f"预检查完成：检测到 {len(project.mapLayers())} 个图层。"
            "命名执行器尚未接入；为保护原始数据，本次未修改任何要素。"
            "请提供当前正常使用的 ODN_Tools_Pro ZIP 以完成适配。"
        )

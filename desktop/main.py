"""FTTH Automation Center desktop controller."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton, QTextEdit,
    QVBoxLayout, QWidget, QHBoxLayout
)

BRIDGE = "http://127.0.0.1:47831"


def request(path: str, payload: dict | None = None, timeout: float = 3.0):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE + path, data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if data is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTTH Automation Center")
        self.resize(760, 500)
        self.status = QLabel("QGIS Bridge: 未连接")
        self.status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        check_btn = QPushButton("检查 QGIS 连接")
        check_btn.clicked.connect(self.check_bridge)
        run_btn = QPushButton("运行功能 01：点线命名")
        run_btn.clicked.connect(self.run_workflow_01)

        row = QHBoxLayout()
        row.addWidget(check_btn)
        row.addWidget(run_btn)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("FTTH Automation Center"))
        layout.addWidget(self.status)
        layout.addLayout(row)
        layout.addWidget(self.log)
        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)
        self.write_log("控制器已启动。功能01是独立任务，不会自动启动其他功能。")

    def write_log(self, message: str):
        self.log.append(message)

    def check_bridge(self):
        try:
            result = request("/health")
            self.status.setText(
                f"QGIS Bridge: 已连接 | QGIS {result.get('qgis_version', '未知')} "
                f"| 项目：{result.get('project', '未保存/未打开')}"
            )
            self.write_log("Bridge 连接正常。")
        except Exception as exc:
            self.status.setText("QGIS Bridge: 未连接")
            self.write_log(f"连接失败：{exc}")

    def run_workflow_01(self):
        try:
            result = request("/task/run", {"workflow": "01_point_line_naming"})
            self.write_log(f"功能01已提交：{result}")
        except urllib.error.URLError as exc:
            self.write_log(f"功能01未启动：无法连接 QGIS Bridge（{exc}）")
        except Exception as exc:
            self.write_log(f"功能01提交失败：{exc}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""FTTH Automation Center - Windows UI control prototype."""
from __future__ import annotations
import json, sys, traceback
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QSplitter
from desktop import ui_control

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTTH Automation Center - QGIS 控制测试")
        self.resize(1050, 720)
        self.status = QLabel("状态：等待检测 QGIS")
        self.status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.preview = QLabel("屏幕截图将在这里显示")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(420, 260)
        self.preview.setStyleSheet("QLabel { background: #20242a; color: #d7dde5; border: 1px solid #59616d; }")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        detect_btn = QPushButton("① 检测 QGIS 窗口")
        detect_btn.clicked.connect(self.inspect_qgis)
        focus_btn = QPushButton("② 控制测试：切换到 QGIS")
        focus_btn.clicked.connect(self.focus_qgis)
        screen_btn = QPushButton("③ 获取当前屏幕截图")
        screen_btn.clicked.connect(self.capture_screen)
        self.configure_btn = QPushButton("④ 自动填写「接入点命名」配置")
        self.configure_btn.setEnabled(False)
        self.configure_btn.setToolTip("先读取当前 QGIS 对话框的真实控件信息，再实现自动填写，避免误操作。")
        self.configure_btn.clicked.connect(self.configure_naming)
        top = QHBoxLayout()
        for btn in (detect_btn, focus_btn, screen_btn, self.configure_btn): top.addWidget(btn)
        left = QVBoxLayout(); left.addWidget(QLabel("桌面控制预览")); left.addWidget(self.preview, 1)
        left_widget = QWidget(); left_widget.setLayout(left)
        right = QVBoxLayout(); right.addWidget(QLabel("运行日志 / 控件诊断")); right.addWidget(self.log, 1)
        right_widget = QWidget(); right_widget.setLayout(right)
        split = QSplitter(Qt.Horizontal); split.addWidget(left_widget); split.addWidget(right_widget); split.setSizes([520, 500])
        layout = QVBoxLayout()
        layout.addWidget(QLabel("FTTH Automation Center")); layout.addWidget(self.status); layout.addLayout(top); layout.addWidget(split, 1)
        root = QWidget(); root.setLayout(layout); self.setCentralWidget(root)
        self.write_log("控制测试原型已启动。当前版本只检测窗口、读取控件信息、切换前台和截图；不会点击 QGIS 命令或修改工程数据。")
        self.write_log("读取对话框控件树后，再针对真实控件实现接入点命名配置。")

    def write_log(self, message): self.log.append(message)

    def inspect_qgis(self):
        try:
            result = ui_control.inspect_qgis()
            self.status.setText("状态：" + result["message"]); self.write_log(result["message"])
            if result.get("ok"):
                for win in result["windows"]:
                    self.write_log(f"窗口：{win['title']} | 控件数：{len(win['controls'])}")
                    for c in win["controls"]:
                        self.write_log(f"  [{c['type']}] name={c['name']!r} | auto_id={c['automation_id']!r} | class={c['class_name']!r}")
                report = ui_control.save_desktop_report(result)
                self.write_log(f"诊断报告已保存：{report}")
            else: self.write_log(json.dumps(result, ensure_ascii=False))
        except Exception: self.write_log("检测异常：\n" + traceback.format_exc())

    def focus_qgis(self):
        try:
            result = ui_control.focus_qgis()
            self.status.setText("状态：" + result["message"]); self.write_log(result["message"])
        except Exception: self.write_log("切换窗口失败：\n" + traceback.format_exc())

    def capture_screen(self):
        try:
            import pyautogui
            path = Path.home() / "FTTH_Automation_QGIS_Screen.png"
            pyautogui.screenshot().save(path)
            pix = QPixmap(str(path))
            self.preview.setPixmap(pix.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.write_log(f"截图已保存：{path}"); self.status.setText("状态：截图成功")
        except Exception: self.write_log("截图失败：\n" + traceback.format_exc())

    def configure_naming(self):
        self.write_log("自动配置尚未启用：需要先根据控件诊断确认控件映射，避免误操作。")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__": main()

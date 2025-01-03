import sys
import cv2
import numpy as np
import time
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QTimer

class RTSPStreamApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RTSP Stream Viewer")
        self.setGeometry(100, 100, 1280, 720)

        self.main_layout = QVBoxLayout()
        self.input_layout = QHBoxLayout()
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter RTSP URL here")

        font = QFont()
        font.setPointSize(14)
        self.start_button = QPushButton("Start Streaming")
        self.start_button.setFont(font)
        self.url_input.setFont(font)

        button_height = 60
        self.start_button.setFixedHeight(button_height)
        self.url_input.setFixedHeight(button_height)

        self.input_layout.addWidget(self.url_input)
        self.input_layout.addWidget(self.start_button)

        self.time_label = QLabel("Stream Time: 0 seconds")
        self.time_label.setFont(font)

        self.video_label = QLabel()
        self.video_label.setScaledContents(True)
        self.video_label.setFixedSize(1280, 720)

        # 종료 버튼
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close_application)
        self.quit_button.setFont(font)

        # 레이아웃
        self.main_layout.addLayout(self.input_layout) 
        self.main_layout.addWidget(self.time_label)
        self.main_layout.addWidget(self.video_label)
        self.main_layout.addWidget(self.quit_button)
        self.setLayout(self.main_layout)

        # 타이머
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.update_frame)
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.cap = None
        self.start_time = 0
        self.start_button.clicked.connect(self.start_streaming)

    def start_streaming(self):
        rtsp_url = self.url_input.text()
        if rtsp_url:
            self.cap = cv2.VideoCapture(rtsp_url)
            if not self.cap.isOpened():
                print("스트림을 열 수 없습니다.")
            else:
                self.frame_timer.start(30)
                self.start_time = time.time()
                self.time_timer.start(100)

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def update_time(self):
        elapsed_time = int(time.time() - self.start_time)
        self.time_label.setText(f"Stream Time: {elapsed_time} seconds")

    def close_application(self):
        if self.cap:
            self.cap.release()
        self.frame_timer.stop()
        self.time_timer.stop()
        self.close()         

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RTSPStreamApp()
    window.show()
    sys.exit(app.exec_())
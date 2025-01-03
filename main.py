import sys
import cv2
import numpy as np
import time
import os
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QTimer
from datetime import datetime  # 날짜 및 시간 사용을 위한 모듈

class RTSPStreamApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RTSP Stream Viewer")
        self.setGeometry(100, 100, 1280, 720)
        self.main_layout = QVBoxLayout()

        # URL 입력
        self.input_layout = QHBoxLayout()
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("Enter IP address here(Don't Enter 'rtsp://')")

        font = QFont()
        font.setPointSize(14)
        self.start_button = QPushButton("Start Streaming")
        self.start_button.setFont(font)
        self.ip_input.setFont(font)

        button_height = 60
        self.start_button.setFixedHeight(button_height)
        self.ip_input.setFixedHeight(button_height)

        # 입력 버튼
        self.input_layout.addWidget(self.ip_input)
        self.input_layout.addWidget(self.start_button)

        # 스트리밍 경과 시간
        self.time_label = QLabel("Stream Time: 0 seconds")
        self.time_label.setFont(font)

        # 비디오 스트림
        self.video_label = QLabel()
        self.video_label.setScaledContents(True)
        self.video_label.setFixedSize(1280, 720)

        # 종료 버튼
        self.quit_button = QPushButton("Quit")
        self.quit_button.setFixedHeight(button_height)
        self.quit_button.clicked.connect(self.close_application)
        self.quit_button.setFont(font)

        # 녹화 시작 버튼
        self.record_button = QPushButton("Start Recording")
        self.record_button.setFixedHeight(button_height)
        self.record_button.setFont(font)
        self.record_button.clicked.connect(self.start_recording)

        # 녹화 중지 버튼
        self.stop_record_button = QPushButton("Stop Recording")
        self.stop_record_button.setFixedHeight(button_height)
        self.stop_record_button.setFont(font)
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.stop_record_button.setEnabled(False)

        # 레이아웃
        self.main_layout.addLayout(self.input_layout)  # IP 입력
        self.main_layout.addWidget(self.time_label)    # 경과
        self.main_layout.addWidget(self.video_label)   # 비디오 스트림
        self.main_layout.addWidget(self.record_button) # 녹화 시작 버튼
        self.main_layout.addWidget(self.stop_record_button) # 녹화 중지 버튼
        self.main_layout.addWidget(self.quit_button)   # 종료 버튼

        self.setLayout(self.main_layout)

        # 프레임 업데이트
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.update_frame)

        # 스트리밍 시간
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)

        # 초기화
        self.cap = None
        self.out = None
        self.start_time = 0
        self.recording = False

        # 버튼 이벤트 연결
        self.start_button.clicked.connect(self.start_streaming)

    def start_streaming(self):
        ip_address = self.ip_input.text()
        rtsp_url = f"rtsp://{ip_address}"

        if rtsp_url:
            self.cap = cv2.VideoCapture(rtsp_url)
            if not self.cap.isOpened():
                print("스트림을 열 수 없습니다.")
            else:
                # timer
                self.frame_timer.start(30)
                self.start_time = time.time()
                self.time_timer.start(100)

    def start_recording(self):
        if self.cap and self.cap.isOpened():
            if not os.path.exists('Record'):
                os.makedirs('Record')

            current_time = datetime.now().strftime("%y%m%d-%H-%M-%S")
            file_name = f"Record/{current_time}.avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out = cv2.VideoWriter(file_name, fourcc, 20.0, (int(self.cap.get(3)), int(self.cap.get(4))))
            self.recording = True
            self.record_button.setEnabled(False)
            self.stop_record_button.setEnabled(True)

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.out.release()
            self.record_button.setEnabled(True)
            self.stop_record_button.setEnabled(False)

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_image))
                if self.recording:
                    self.out.write(frame)

    def update_time(self):
        elapsed_time = int(time.time() - self.start_time)
        self.time_label.setText(f"Stream Time: {elapsed_time} seconds")

    def close_application(self):
        if self.cap:
            self.cap.release()
        if self.recording:
            self.out.release()
        self.frame_timer.stop()
        self.time_timer.stop()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RTSPStreamApp()
    window.show()
    sys.exit(app.exec_())
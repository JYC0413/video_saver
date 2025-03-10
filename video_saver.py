import sys
import os
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, QTimer, Qt
from threading import Thread

class VideoSaver(QWidget):
    def __init__(self):
        super().__init__()

        # ✅ 在 initUI 之前先定义 media_player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.current_index = 0
        self.video_list = self.load_video_links('urls_list.txt')

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 视频播放窗口
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        # ✅ 设置视频输出
        self.media_player.setVideoOutput(self.video_widget)

        # 控制按钮
        button_layout = QHBoxLayout()
        self.mute_btn = QPushButton('静音')
        self.music_btn = QPushButton('音乐')
        self.voice_btn = QPushButton('人声')
        self.mix_btn = QPushButton('人声混合音乐')
        self.noise_btn = QPushButton('噪音')

        button_layout.addWidget(self.mute_btn)
        button_layout.addWidget(self.music_btn)
        button_layout.addWidget(self.voice_btn)
        button_layout.addWidget(self.mix_btn)
        button_layout.addWidget(self.noise_btn)

        layout.addLayout(button_layout)

        # 绑定按钮
        self.mute_btn.clicked.connect(lambda: self.save_video('sound/mute'))
        self.music_btn.clicked.connect(lambda: self.save_video('sound/music'))
        self.voice_btn.clicked.connect(lambda: self.save_video('sound/voice'))
        self.mix_btn.clicked.connect(lambda: self.save_video('sound/mix'))
        self.noise_btn.clicked.connect(lambda: self.save_video('sound/noise'))

        self.setLayout(layout)
        self.setWindowTitle('Video Saver')
        self.setGeometry(200, 200, 800, 600)

        # 播放第一个视频
        QTimer.singleShot(0, self.play_next_video)

    def load_video_links(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            QMessageBox.critical(self, '错误', f'未找到文件: {file_path}')
            sys.exit(1)

    def play_next_video(self):
        if self.current_index < len(self.video_list):
            video_url = self.video_list[self.current_index]
            print(f"正在播放视频：{video_url}")
            self.media_player.setMedia(QMediaContent(QUrl(video_url)))
            self.media_player.play()
        else:
            QMessageBox.information(self, '完成', '所有视频已播放完成！')


    def convert_to_wav(self, video_file, audio_file):
        try:
            command = f'ffmpeg -y -i "{video_file}" "{audio_file}" && rm "{video_file}"'
            os.system(command)
            print(f'转换成功: {audio_file}')
        except Exception as e:
            QMessageBox.critical(self, '转换失败', f'转换失败: {e}')
    def save_video(self, folder):
        if self.current_index >= len(self.video_list):
            QMessageBox.warning(self, '警告', '没有视频可保存')
            return

        video_url = self.video_list[self.current_index]
        Thread(target=self.download_and_convert_video, args=(video_url, folder, self.current_index)).start()
        self.current_index += 1
        QTimer.singleShot(0, self.play_next_video)


    def download_and_convert_video(self, url, folder, current_index):
                try:
                    if not os.path.exists(folder):
                        os.makedirs(folder)

                    video_file_name = os.path.join(folder, f'video_{current_index + 1}.mp4')
                    audio_file_name = os.path.join(folder, f'video_{current_index + 1}.wav')
                    print(f'正在保存 {video_file_name}...')

                    response = requests.get(url, stream=True)
                    response.raise_for_status()

                    with open(video_file_name, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    print(f'保存成功: {video_file_name}')
                    self.convert_to_wav(video_file_name, audio_file_name)

                except Exception as e:
                    QMessageBox.critical(self, '保存失败', f'保存失败: {e}')

    def closeEvent(self, event):
        # ✅ 停止播放器，防止崩溃
        self.media_player.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoSaver()
    player.show()
    sys.exit(app.exec_())

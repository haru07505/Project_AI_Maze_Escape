import sys, pygame
from playsound import playsound
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem, QMessageBox
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtMultimedia import QSoundEffect
from StartUI import Ui_MainWindow  # Import class giao diện từ StartUI.py
import map

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  # Khởi tạo giao diện
        self.ui.setupUi(self) 
        self.scene = QGraphicsScene()
        self.ui.imageLevelView.setScene(self.scene)
        self.ui.inforLabel.hide()

        self.current_level = 1  
        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile("arrowclick.wav"))  
        self.click_sound.setVolume(0.5) 
        self.select_sound = QSoundEffect()
        self.select_sound.setSource(QUrl.fromLocalFile("algorthm.wav"))
        self.select_sound.setVolume(0.5)  

        # Kết nối các nút với hành động
        self.ui.startButton.clicked.connect(self.start_game)
        self.ui.exitButton.clicked.connect(self.close)
        self.ui.leftButton.clicked.connect(self.prev_level)
        self.ui.leftButton.clicked.connect(lambda: self.click_sound.play())  
        self.ui.rightButton.clicked.connect(lambda: self.click_sound.play())  
        self.ui.rightButton.clicked.connect(self.next_level)
        self.ui.inforButton.clicked.connect(self.show_info)

        self.ui.startButton.clicked.connect(lambda: self.click_sound.play())  
        self.ui.inforButton.clicked.connect(lambda: self.click_sound.play())
          
        original_alg = self.ui.algoCbBox.showPopup
        def custom_showPopup():
            self.click_sound.play()         
            original_alg()
        self.ui.algoCbBox.showPopup = custom_showPopup
        combo_view = self.ui.algoCbBox.view()
        combo_view.entered.connect(lambda: self.select_sound.play())
        # Hiển thị hình ảnh level đầu tiên
        self.update_level_display("level1_image.png")
        self.game_window = None

    def show_info(self):
        if self.ui.inforLabel.isHidden():
            self.ui.inforLabel.show()
        else:
            self.ui.inforLabel.hide()

    def start_game(self):   
        self.selected_algorithm = self.ui.algoCbBox.currentText() 
        pygame.init()
        if self.game_window is None:
            if self.current_level == 1:
                self.game_window = map.Game("maze_level1.tmx", self.selected_algorithm, 720)
            elif self.current_level == 2:
                self.game_window = map.Game("maze_level2.tmx", self.selected_algorithm, 960)
            elif self.current_level == 3:
                self.game_window = map.Game("maze_level3.tmx", self.selected_algorithm, 960)
            self.game_window.run()
        self.game_window = None

    def prev_level(self):      
        if self.current_level > 1:
            self.current_level -= 1
            self.ui.levelLabel.setText(f"Level {self.current_level}")
            self.update_level_display(f"level{self.current_level}_image.png")

    def next_level(self):
        if self.current_level < 3:
            self.current_level += 1
            self.ui.levelLabel.setText(f"Level {self.current_level}")  
            self.update_level_display(f"level{self.current_level}_image.png")
        else:
            QMessageBox.information(self, "Notice", "No new level yet!")

    def update_level_display(self, file_image):
        self.scene.clear()
        pixmap = QPixmap(file_image)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)
        self.ui.imageLevelView.setScene(self.scene)
        self.ui.imageLevelView.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.ui.imageLevelView.fitInView(pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
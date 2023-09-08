import sys
from os.path import splitext, split, abspath, join, exists

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, QApplication
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt
from widgets import *
from app import MainWindowUi

app = QApplication(sys.argv)

app_data_path = join(os.environ['APPDATA'], 'Object Creator')

main_window = MainWindowUi(app_data_path)

view = SpriteTab(main_window)
view.show()
app.exec_()

import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from MainWindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
  def __init__ (self, *args, obj = None, **kwargs):
    super(MainWindow, self).__init__(*args, **kwargs)
    self.setupUi(self)

def main ():
  app = QtWidgets.QApplication([])
  window = MainWindow()
  window.show()
  sys.exit(app.exec())

main()

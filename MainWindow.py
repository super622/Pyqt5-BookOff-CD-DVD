import re
import xlwt
import sqlite3

import action

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QSettings, QSize
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QProgressBar
from pyqtspinner import WaitingSpinner

class RequestThread(QThread):
	request_completed = pyqtSignal(str)

	def __init__(self, handler, price_diff):
		super().__init__()
		self.ui_handler = handler
		self.total_count = 300000
		self.price_diff = price_diff

	def run(self):
		self.request_completed.emit("start")
		
		if(self.price_diff != ''):
			self.ui_handler.price_diff = self.price_diff

			# result = self.ui_handler.product_list_download_from_amazon()
			# print(type(result) == str)
			# if(type(result) == str):
			# 	self.request_completed.emit(result)
			# 	self.request_completed.emit("stop")
			
			# print(result)
			# total = result['total']
			# document_id = result['filepath']

			# self.request_completed.emit("reading")
			# result = self.ui_handler.read_product_list_from_file(document_id)
			# if(result != 'success'):
			# 	self.request_completed.emit(result)
			# 	self.request_completed.emit('stop')

		cur_position = 0
		while cur_position < self.total_count:
			if not self.ui_handler.main_window.isStop:
				try:
					cur_position += 1
					if(cur_position == 150000):
						self.ui_handler.cur_page = 0

					self.ui_handler.cur_page += 1
					# product_list = self.ui_handler.get_product_info_by_product_list(cur_position)
					product_list = self.ui_handler.get_products_list(cur_position)

					if(len(product_list) == 0 and int(self.ui_handler.temp_arr) == 0):
						cur_position = 150000
						self.ui_handler.cur_page = 0
						self.ui_handler.end_flag += 1
					
					if self.ui_handler.end_flag == 2:
						break

					# key_arr = [['4580128895130', '', '', '10000'], ['4580128895383', '', '', '10000'], ['4988067000125', '', '', '10000']]
					for product in product_list:
						cur_position += 1
						if(product[0] != ''):
							self.ui_handler.get_product_url(product, cur_position)

						progress = 100 / self.total_count * cur_position
						self.request_completed.emit(str(progress))
				except Exception as e:
					self.request_completed.emit(e)
			else:
				self.request_completed.emit("stop")
				self.quit()
				break

		self.request_completed.emit("stop")
		self.quit()

class Ui_MainWindow(object):
	keyword_arr = []

	def __init__(self):
		super().__init__()
		self.total_count = 300000
		self.spinner = None
		self.progressBar = None
		self.statusLabel = None
		self.tbl_dataview = None
		self.btn_start = None
		self.horizontalLayout = None
		self.horizontalLayout_2 = None
		self.horizontalLayout_3 = None
		self.btn_export = None
		self.lbl_price_diff = None
		self.txt_price_diff = None
		self.gridLayout = None
		self.centralwidget = None
		self.verticalLayout = None
		self.isStop = True
		self.settings = None
		self.cmb_export_type = None
		self.request_thread = None
		self.ui_handler = action.ActionManagement(self)

	# create GUI
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
		MainWindow.setEnabled(True)
		MainWindow.resize(820, 600)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
		MainWindow.setSizePolicy(sizePolicy)
		MainWindow.setMinimumSize(QtCore.QSize(820, 600))
		MainWindow.setAcceptDrops(False)
		MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
		MainWindow.setAutoFillBackground(True)
		MainWindow.setAnimated(False)
		MainWindow.setDocumentMode(False)
		MainWindow.setTabShape(QtWidgets.QTabWidget.Triangular)
		MainWindow.setDockNestingEnabled(False)
		MainWindow.setUnifiedTitleAndToolBarOnMac(False)

		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setEnabled(True)

		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())

		self.centralwidget.setSizePolicy(sizePolicy)
		self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
		self.centralwidget.setObjectName("centralwidget")
		self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
		self.gridLayout.setObjectName("gridLayout")

		self.verticalLayout = QtWidgets.QVBoxLayout()
		self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
		self.verticalLayout.setContentsMargins(0, 0, 0, 0)
		self.verticalLayout.setObjectName("verticalLayout")

		self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_2.setSpacing(12)
		self.horizontalLayout_2.setObjectName("horizontalLayout_2")
		self.btn_start = QtWidgets.QPushButton(self.centralwidget)
		self.btn_start.setMinimumSize(QtCore.QSize(16777215, 30))
		self.btn_start.setMaximumSize(QtCore.QSize(16777215, 30))
		self.btn_start.setObjectName("btn_start")
		self.btn_start.setText("開始")
		self.btn_start.clicked.connect(self.handle_btn_start_clicked)
		self.horizontalLayout_2.addWidget(self.btn_start)

		self.btn_export = QtWidgets.QPushButton(self.centralwidget)
		self.btn_export.setMinimumSize(QtCore.QSize(16777215, 30))
		self.btn_export.setMaximumSize(QtCore.QSize(16777215, 30))
		self.btn_export.setObjectName("btn_export")
		self.btn_export.setText("出力")
		self.btn_export.setEnabled(False)
		self.btn_export.clicked.connect(self.savefile)
		self.horizontalLayout_2.addWidget(self.btn_export)

		self.lbl_price_diff = QtWidgets.QLabel(self.centralwidget)
		self.lbl_price_diff.setFixedHeight(30)
		self.lbl_price_diff.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.lbl_price_diff.setText("価格差の％数を入力してください。(デフォルト：35％)")
		self.horizontalLayout_2.addWidget(self.lbl_price_diff)

		self.txt_price_diff = QtWidgets.QLineEdit(self.centralwidget)
		self.txt_price_diff.setObjectName("txt_price_diff")
		self.txt_price_diff.setValidator(QtGui.QIntValidator())
		self.txt_price_diff.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.txt_price_diff.setMaxLength(2)
		self.txt_price_diff.setFixedHeight(30)
		self.txt_price_diff.setFixedWidth(100)
		self.horizontalLayout_2.addWidget(self.txt_price_diff)

		self.verticalLayout.addLayout(self.horizontalLayout_2)
		
		self.horizontalLayout = QtWidgets.QHBoxLayout()
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.tbl_dataview = QtWidgets.QTableView(self.centralwidget)
		self.tbl_dataview.setObjectName("tbl_dataview")
		self.tbl_dataview.setMaximumWidth(16777215)
		self.tbl_dataview.setMinimumWidth(16777215)
		self.tbl_dataview.doubleClicked.connect(self.handle_cell_click)
		header_labels = ["JAN", "URL", "在庫", "サイト価格", "Amazonの価格", "価格差"]
		model = QtGui.QStandardItemModel(0, 5)
		model.setHorizontalHeaderLabels(header_labels)
		self.tbl_dataview.setModel(model)
		self.horizontalLayout.addWidget(self.tbl_dataview)
		self.verticalLayout.addLayout(self.horizontalLayout)

		self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_3.setObjectName('horizontalLayout_3')
		self.statusLabel = QtWidgets.QLabel(self.centralwidget)
		self.statusLabel.setMinimumSize(QtCore.QSize(16777215, 20))
		self.statusLabel.setMaximumSize(QtCore.QSize(16777215, 50))
		self.statusLabel.setVisible(True)
		self.horizontalLayout_3.addWidget(self.statusLabel)
		self.verticalLayout.addLayout(self.horizontalLayout_3)

		self.progressBar = QProgressBar(self)
		self.progressBar.setVisible(False)
		self.verticalLayout.addWidget(self.progressBar)
		self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
		MainWindow.setCentralWidget(self.centralwidget)
		self.spinner = WaitingSpinner(
				parent = self.tbl_dataview,
				disable_parent_when_spinning = False,
				roundness = 100,
				fade = 88,
				radius = 29,
				lines = 58,
				line_length = 11,
				line_width = 14,
				speed = 1,
				color = QColor(0, 0, 0, 255)
		)
		self.spinner.setObjectName("spinner")
		self.retranslateUi(MainWindow)
		MainWindow.setWindowIcon(QtGui.QIcon('delivery.ico'))
		QtCore.QMetaObject.connectSlotsByName(MainWindow)
		self.loadSettings()

	def closeEvent(self, event):
		self.saveSettings()
		event.accept()

	def loadSettings(self):
		# Load the previous settings using QSettings
		settings = QSettings("YourCompany", "YourApp")
		self.resize(settings.value("WindowSize", QSize(800, 600)))
		for col in range(self.tbl_dataview.model().columnCount()):
			width = settings.value(f"columnWidth_{col}", type = int, defaultValue = 100)  # Set a default width if not found
			self.tbl_dataview.setColumnWidth(col, width)

	def saveSettings(self):
		# Save the current window size and column state using QSettings
		settings = QSettings("YourCompany", "YourApp")
		settings.setValue("WindowSize", self.size())
		for col in range(self.tbl_dataview.model().columnCount()):
			width = self.tbl_dataview.columnWidth(col)
			settings.setValue(f"columnWidth_{col}", width)

	def handle_cell_click(self, index):
		row = index.row()
		col = index.column()
		if col == 1 and self.ui_handler.products_list[row] != "":
			import webbrowser
			webbrowser.open(self.ui_handler.products_list[row]['url'])

	def handle_btn_start_clicked(self):
		if self.isStop:
			self.btn_start.setEnabled(False)
			self.ui_handler.products_list = []
			price_diff = self.txt_price_diff.text()
			self.request_thread = RequestThread(self.ui_handler, price_diff)
			self.request_thread.request_completed.connect(self.handle_request_completed)
			self.request_thread.start()
			self.isStop = False
		else:
			self.isStop = True
			self.statusLabel.setVisible(True)
			self.progressBar.setVisible(False)
			self.btn_start.setEnabled(False)
			self.spinner.stop()
			self.request_thread.exit()

	def savefile(self):
		filename, _ = QFileDialog.getSaveFileName(self, 'Save File', '', ".xls(*.xls)")
		if filename:
			wbk = xlwt.Workbook()
			sheet = wbk.add_sheet("sheet", cell_overwrite_ok = True)
			style = xlwt.XFStyle()
			font = xlwt.Font()
			font.bold = True
			style.font = font
			model = self.tbl_dataview.model()
			
			sheet.write(0, 0, 'JAN', style = style)
			sheet.write(0, 1, 'URL', style = style)
			sheet.write(0, 2, '在庫', style = style)
			sheet.write(0, 3, 'サイト価格', style = style)
			sheet.write(0, 4, 'Amazonの価格', style = style)
			sheet.write(0, 5, '価格差', style = style)

			row_count = 0
			for r in range(model.rowCount()):
				sheet.write((row_count + 1), 0, model.data(model.index(row_count, 0)), style = style)
				sheet.write((row_count + 1), 1, model.data(model.index(row_count, 1)), style = style)
				sheet.write((row_count + 1), 2, model.data(model.index(row_count, 2)), style = style)
				sheet.write((row_count + 1), 3, model.data(model.index(row_count, 3)), style = style)
				sheet.write((row_count + 1), 4, model.data(model.index(row_count, 4)), style = style)
				sheet.write((row_count + 1), 5, model.data(model.index(row_count, 5)), style = style)
				row_count += 1
			
			# conn = sqlite3.connect('database.db')
			# cur = conn.cursor()
			# cur.execute("SELECT * FROM history")
			# rows = cur.fetchall()
			# conn.close()

			# for row in rows:
			# 	sheet.write((row_count + 1), 0, row[0], style = style)
			# 	sheet.write((row_count + 1), 1, row[1], style = style)
			# 	sheet.write((row_count + 1), 2, row[2], style = style)
			# 	sheet.write((row_count + 1), 3, row[3], style = style)
			# 	sheet.write((row_count + 1), 4, row[4], style = style)
			# 	sheet.write((row_count + 1), 5, row[5], style = style)
			# 	row_count += 1

			wbk.save(filename)
			return
	
	def handle_request_completed(self, response_text):
		if response_text == "start":
			self.statusLabel.setText("ダウンロード中...")
			self.spinner.start()
		elif response_text == "stop":
			self.spinner.stop()
			self.btn_start.setText("開始")
			self.btn_export.setEnabled(True)
			self.btn_start.setEnabled(True)
			self.isStop = True
		elif response_text == "reading":
			self.progressBar.setValue(0)
			self.statusLabel.setText("ファイルを読んでいます...")
		elif response_text != "start" and response_text != 'stop' and response_text != 'reading' and re.findall(r'\d+', response_text) == False:
			self.spinner.stop()
			self.statusLabel.setText(response_text)
		else:
			self.spinner.stop()
			cur_position = float(response_text) / (100 / self.total_count)
			self.statusLabel.setText(f"{self.total_count} 個中 {round(cur_position)} 個処理済み")
			self.progressBar.setVisible(True)
			self.btn_export.setEnabled(True)
			self.progressBar.setValue(round(float(response_text)))

	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "Amazon - BookOff ( DVD, CD )"))
		self.btn_start.setText(_translate("MainWindow", "開始"))

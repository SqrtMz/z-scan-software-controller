from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QApplication, QGroupBox
from PySide6.QtGui import QPixmap, QDesktopServices
from PySide6.QtCore import Qt


class AboutDialog(QDialog):
	def __init__(self, parent):
		super().__init__(parent)
		self.setWindowTitle("About Zscanner")
		self.setFixedSize(800, 600)

		images_layout = QVBoxLayout()
		images_layout.setSpacing(50)
		images_layout.setContentsMargins(20, 0, 0, 0)
		images_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

		images_layout.addStretch()

		for path in ["assets/geoel.png", "assets/ua.webp"]:
			img_label = QLabel()
			pixmap = QPixmap(path)

			# img_label.setText("[missing image]")					# DEBUGGING
			# img_label.setFixedSize(256, 256)
			# img_label.setStyleSheet("border: 1px solid gray;")
			# img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

			img_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
			images_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignCenter)

		images_layout.addStretch()

		text_layout = QVBoxLayout()
		text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
		text_layout.setContentsMargins(40, 0, 20, 20)

		text_layout.addStretch()

		text_label = QLabel(
			"<h1>Zcanner v1.0.0</h1>"
			"<p>Zcanner is a GUI utility to automate the process of performing the Z-Scan technique and control its setup through a microcontroller.</p>"

			"<h2>Author</h2>"
			"<p>Carlos A. Vesga</p>"

			"<h4>In collaboration of</h4>"
			"<ul>"
				"<li>Universidad del Atlántico</p>"
				"<li>Grupo de espectroscopía óptica de emisión y láser (GEOEL)</p>"
			"</ul>"

			"<h2>Source</h2>"
			"<a href='https://github.com/SqrtMz/z-scan-software'>https://github.com/SqrtMz/z-scan-software/</a>"
			"<br>"
			"<br>"
			"<a href='https://github.com/SqrtMz/z-scan-microcontroller'>https://github.com/SqrtMz/z-scan-microcontroller/</a>"

			"<h2>License</h2>"
			"<a href='https://raw.githubusercontent.com/SqrtMz/z-scan-software/main/LICENSE'>GNU GPLv2 Only<a>"
		)

		text_label.setStyleSheet("margin: 0px; padding: 0px; qproperty-alignment: 'AlignJustify';")
		text_label.setOpenExternalLinks(True)
		text_label.setWordWrap(True)
		text_label.setTextFormat(Qt.RichText)
		text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
		text_layout.addWidget(text_label)

		text_layout.addStretch()

		content_layout = QHBoxLayout()
		content_layout.addLayout(images_layout)
		content_layout.addLayout(text_layout)

		buttons_layout = QHBoxLayout()

		button_box = QDialogButtonBox(QDialogButtonBox.Ok)
		button_box.accepted.connect(self.accept)

		qt_button = QPushButton("About Qt")
		qt_button.clicked.connect(QApplication.aboutQt)

		bokeh_button = QPushButton("About Bokeh")
		bokeh_button.clicked.connect(lambda: QDesktopServices.openUrl("https://bokeh.org/"))

		pyserial_button = QPushButton("About PySerial")
		pyserial_button.clicked.connect(lambda: QDesktopServices.openUrl("https://github.com/pyserial/pyserial"))

		buttons_layout.addWidget(qt_button, alignment=Qt.AlignmentFlag.AlignLeft)
		buttons_layout.addWidget(bokeh_button, alignment=Qt.AlignmentFlag.AlignLeft)
		buttons_layout.addWidget(pyserial_button, alignment=Qt.AlignmentFlag.AlignLeft)

		buttons_layout.addStretch()

		buttons_layout.addWidget(button_box, alignment=Qt.AlignmentFlag.AlignRight)

		group_box = QGroupBox()
		group_layout = QVBoxLayout(group_box)
		group_layout.addLayout(content_layout)
		group_layout.addLayout(buttons_layout)

		main_layout = QVBoxLayout(self)
		main_layout.addWidget(group_box)
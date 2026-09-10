import re
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QGroupBox, QFileDialog, QCheckBox
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
import pandas as pd

class PlotOptions(QWidget):
	def __init__(self, home_parent, port):
		super().__init__()

		self.home_parent = home_parent

		self.plotted_data = []

		self.main_layout = QHBoxLayout(self)
		
		self.plot_group = QGroupBox("Plot")
		plot_layout = QVBoxLayout()
		self.plot_group.setLayout(plot_layout)
		self.main_layout.addWidget(self.plot_group)

		self.plot = QWebEngineView()
		self.plot.setUrl(f"http://localhost:{port}/")
		plot_layout.addWidget(self.plot)
		profile = QWebEngineProfile.defaultProfile()
		profile.downloadRequested.connect(self.capture_plot)

		plot_actions_layout = QVBoxLayout()
		plot_actions_row1 = QHBoxLayout()

		self.sensor1 = QCheckBox("Sensor 1")
		self.sensor1.setChecked(True)
		self.sensor1.setStyleSheet("color: #FF0000; font-weight: bold")
		self.sensor1.clicked.connect(self.toggle_sensor)
		plot_actions_row1.addWidget(self.sensor1)

		self.sensor2 = QCheckBox("Sensor 2")
		self.sensor2.setChecked(True)
		self.sensor2.setStyleSheet("color: #0000FF; font-weight: bold")
		self.sensor2.clicked.connect(self.toggle_sensor)
		plot_actions_row1.addWidget(self.sensor2)

		plot_actions_row1.addStretch()

		self.save_plot_data_button = QPushButton("Save plot data")
		self.save_plot_data_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.save_plot_data_button.clicked.connect(self.save_plot_data)
		plot_actions_row1.addWidget(self.save_plot_data_button)

		self.reset_plot_button = QPushButton("Reset plot")
		self.reset_plot_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.reset_plot_button.clicked.connect(self.reset_plot)
		plot_actions_row1.addWidget(self.reset_plot_button)

		plot_actions_layout.addLayout(plot_actions_row1)
		plot_layout.addLayout(plot_actions_layout)


	def capture_plot(self, download):
		default_filename = download.suggestedFileName()

		path, _ = QFileDialog.getSaveFileName(self, "Save File As", default_filename + ".png", "PNG Image (*.png);; All Files (*)")
		
		if path:
			download.setDownloadFileName(path)
			download.accept()

	def save_plot_data(self):
		if len(self.plotted_data) > 0:
			self.df = pd.DataFrame(self.plotted_data)

		path, selection = QFileDialog.getSaveFileName(self, "Save File As", "data.csv", "CSV Files (*.csv);; TXT Files (*.txt);; DAT Files (*.dat);; All Files (*)")

		match = re.search(r'\(\*(\.[a-zA-Z0-9]+)\)', selection)
		extension = match.group(1) if match else ''

		if path:
			path = path + extension if not path.endswith(extension) else path
			self.df.to_csv(path, index=False)

	def reset_plot(self):
		self.plotted_data = []
		self.df = pd.DataFrame(data=None, columns=['x', "y1", "y2"])

		def clear():
			for i in range(len(self.home_parent.bokeh_plot.sources)):
				self.home_parent.bokeh_plot.sources[i].data = dict(x=[], y=[])

		self.home_parent.bokeh_plot.doc.add_next_tick_callback(clear)

	def toggle_sensor(self):
		def toggle_sensors():
			self.home_parent.bokeh_plot.renderer1.visible = self.sensor1.isChecked()
			self.home_parent.bokeh_plot.renderer2.visible = self.sensor2.isChecked()

		self.home_parent.bokeh_plot.doc.add_next_tick_callback(toggle_sensors)
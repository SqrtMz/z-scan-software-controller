from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QDoubleSpinBox, QGroupBox, QSizePolicy, QPushButton, QLabel, QVBoxLayout, QSpacerItem, QHBoxLayout, QFileDialog, QRadioButton, QButtonGroup, QMessageBox
from app.gui.form_cell_units import FormCellUnits
import numpy as np
import pandas as pd

class Calculation(QGroupBox):
	def __init__(self, home_parent):
		super().__init__()

		self.home_parent = home_parent
		self.n2 = 0

		self.setTitle("Calculations")
		self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

		layout = QVBoxLayout(self)
		self.setLayout(layout)

		form_layout = QFormLayout()

		file_picker_layout = QHBoxLayout()

		file_picker_label = QLabel("Select a data file:")
		file_picker_label.setFixedSize(175, 15)
		file_picker_layout.addWidget(file_picker_label)

		self.file_picker_button = QPushButton("No file selected...")
		self.file_picker_button.clicked.connect(self.load_file)

		file_picker_layout.addWidget(self.file_picker_button)

		form_layout.addRow(file_picker_layout)

		self.laser_wavelength = FormCellUnits("Laser wavelength:", QDoubleSpinBox(), "nm", input_widget_value=0)
		form_layout.addRow(self.laser_wavelength)

		self.laser_power = FormCellUnits("Laser power:", QDoubleSpinBox(), "mW")
		form_layout.addRow(self.laser_power)

		self.sample_length = FormCellUnits("Sample length:", QDoubleSpinBox(), "mm")
		form_layout.addRow(self.sample_length)

		self.aperture_transmittance = FormCellUnits("Aperture transmittance:", QDoubleSpinBox(), input_widget_value=0.01)
		form_layout.addRow(self.aperture_transmittance)

		form_layout.addRow(QLabel("Curve:"))

		calculate_layout = QHBoxLayout()
		form_layout.addRow(calculate_layout)

		self.calculate_button_group = QButtonGroup()
		
		calculate_sensor1 = QRadioButton("Sensor 1")
		calculate_sensor1.setStyleSheet("color: #FF0000; font-weight: bold")
		self.calculate_button_group.addButton(calculate_sensor1, 0)
		calculate_layout.addWidget(calculate_sensor1)

		calculate_sensor2 = QRadioButton("Sensor 2")
		calculate_sensor2.setStyleSheet("color: #0000FF; font-weight: bold")
		self.calculate_button_group.addButton(calculate_sensor2, 1)
		calculate_layout.addWidget(calculate_sensor2)

		form_layout.addRow(QLabel("Normalize curve with:"))

		normalize_layout = QHBoxLayout()
		form_layout.addRow(normalize_layout)

		self.normalize_button_group = QButtonGroup()
		
		normalize_sensor1 = QRadioButton("Sensor 1")
		normalize_sensor1.setStyleSheet("color: #FF0000; font-weight: bold")
		self.normalize_button_group.addButton(normalize_sensor1, 0)
		normalize_layout.addWidget(normalize_sensor1)

		normalize_sensor2 = QRadioButton("Sensor 2")
		normalize_sensor2.setStyleSheet("color: #0000FF; font-weight: bold")
		self.normalize_button_group.addButton(normalize_sensor2, 1)
		normalize_layout.addWidget(normalize_sensor2)

		normalize_far_field = QRadioButton("Far field")
		self.normalize_button_group.addButton(normalize_far_field, 2)
		normalize_layout.addWidget(normalize_far_field)

		layout.addLayout(form_layout)

		layout.addStretch()

		result_layout = QFormLayout()

		self.calculate_button = QPushButton("Calculate non-linear refraction index")
		self.calculate_button.clicked.connect(self.calculate_n2)
		result_layout.addRow(self.calculate_button)

		self.n2_label = QLabel(f"n₂ index: {self.n2} m²/W")
		self.n2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.n2_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
		result_layout.addRow(self.n2_label)

		layout.addLayout(result_layout)

	def load_file(self):
		try:
			path, _ = QFileDialog.getOpenFileName(self, "Open data file", '', "CSV Files (*.csv);; TXT Files (*.txt);; DAT Files (*.dat);; All Files (*)")

			if not path:
				return

			loaded_df = pd.read_csv(path)
		
			self.home_parent.plot_options.df = loaded_df

			def plot():
				for i in range(len(self.home_parent.bokeh_plot.sources)):
					self.home_parent.bokeh_plot.sources[i].data = dict(x=loaded_df['x'], y=loaded_df['y' + str(i + 1)])

			self.home_parent.bokeh_plot.doc.add_next_tick_callback(plot)

		except Exception as e:
			QMessageBox.warning(self, "There was an error reading a file", f"There was an error trying to read the file:\n{e}")
			return

	def calculate_n2(self):
		df = pd.DataFrame(self.home_parent.plot_options.plotted_data)

		match self.calculate_button_group.checkedId():
			case 0:
				curve = df.iloc[:, 1].to_numpy()
			case 1:
				curve = df.iloc[:, 2].to_numpy()

			case _:
				QMessageBox.warning(self, "Invalid curve data source", "Please select a source for the curve data")
				return

		match self.normalize_button_group.checkedId():
			case 0:
				normalization_data = df.iloc[:, 1].to_numpy()
			case 1:
				normalization_data = df.iloc[:, 2].to_numpy()
			case 2:
				normalization_data = [curve[-1]]
				
			case _:
				QMessageBox.warning(self, "Invalid normalization data source", "Please select a source for the normalization data")
				return

		normalized_curve = []
		for i in range(len(curve)):
			if len(normalization_data) == 1:
				normalized_curve.append(curve[i] / normalization_data[0])
			else:
				normalized_curve.append(curve[i] / normalization_data[i])

		distance = df.iloc[:, 0].to_numpy()

		transmittance_diff_p_v = max(normalized_curve) - min(normalized_curve)

		distance_diff_p_v = (distance[np.argmax(normalized_curve)] - distance[np.argmin(normalized_curve)]) * 10**-2

		n2 = (transmittance_diff_p_v * ((self.laser_wavelength.value() * 10**-9)**2) * distance_diff_p_v) / (0.406 * ((1 - self.aperture_transmittance.value())**0.25) * 4 * np.pi * (self.laser_power.value() * 10**-3) * (self.sample_length.value() * 10**-3) * 1.7)

		self.n2_label.setText(f"n₂ index: {n2:.5e} m²/W")
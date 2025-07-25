from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QSizePolicy, QGroupBox, QFormLayout, QComboBox, QSlider
from serial import Serial
from serial.serialutil import SerialException

class Settings(QWidget):
	def __init__(self, home_parent):
		super().__init__()

		self.home_parent = home_parent
		self.state = "Standby"

		self.main_layout = QVBoxLayout(self)		

		information_group = QGroupBox("Information")
		information_layout = QFormLayout()
		information_group.setLayout(information_layout)

		self.selected_device = QLabel("Select a device")
		information_layout.addRow(self.selected_device)

		self.current_position = QLabel()
		self.current_position.setText("NA")
		information_layout.addRow(QLabel("Current position:"), self.current_position)

		self.motor_state = QLabel(f"Current state: {self.state}")
		information_layout.addRow(self.motor_state)

		self.main_layout.addWidget(information_group)

		distance_group = QGroupBox("Distance options")
		distance_group_layout = QFormLayout()
		distance_group.setLayout(distance_group_layout)

		self.move_to = QLineEdit()
		distance_group_layout.addRow(QLabel("Move to:"), self.move_to)

		self.main_layout.addWidget(distance_group)

		movement_group = QGroupBox("Movement options")
		movement_layout = QFormLayout()
		movement_group.setLayout(movement_layout)

		self.step_size_selector = QComboBox()
		self.step_size_selector.addItems(["Full step", "1/2 step", "1/4 step", "1/8 step"])
		movement_layout.addRow(QLabel("Motor step size:"), self.step_size_selector)

		self.motor_speed = QSlider(Qt.Orientation.Horizontal)
		distance_group_layout.addRow(QLabel("Motor speed:"), self.motor_speed)

		self.main_layout.addWidget(movement_group)

		actions_group = QGroupBox("Actions")
		actions_layout = QVBoxLayout()
		actions_group.setLayout(actions_layout)

		actions_row1 = QHBoxLayout()

		self.execute = QPushButton("Execute")
		self.execute.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.execute.clicked.connect(self.start_execution)
		actions_row1.addWidget(self.execute)

		self.go_to_start_button = QPushButton("Go to start")
		self.go_to_start_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.go_to_start_button.clicked.connect(self.go_to_start)
		actions_row1.addWidget(self.go_to_start_button)

		self.go_to_end_button = QPushButton("Go to end")
		self.go_to_end_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.go_to_end_button.clicked.connect(self.go_to_end)
		actions_row1.addWidget(self.go_to_end_button)

		actions_layout.addLayout(actions_row1)

		actions_row2 = QHBoxLayout()

		self.stop = QPushButton("Stop")
		self.stop.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.stop.clicked.connect(self.stop_data_collection)
		actions_row2.addWidget(self.stop)

		self.TEST = QPushButton("TEST")
		self.TEST.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.TEST.clicked.connect(self.test_fn)
		actions_row2.addWidget(self.TEST)

		actions_layout.addLayout(actions_row2)

		self.main_layout.addWidget(actions_group)


	def send_serial_command(self, command: str):

		if self.home_parent.device == None:
			self.home_parent.statusBar().showMessage("No device selected")
			return
		
		try:
			ser = Serial(self.home_parent.device, 115200)
			ser.write(command.encode("utf-8"))
			ser.close()
		
		except SerialException:
			self.home_parent.statusBar().showMessage("Invalid device, please check the device selected")
			return

	def start_execution(self):
		if self.home_parent.device == None:
			self.home_parent.statusBar().showMessage("No device selected")
			return
		
		try:
			ser = Serial(self.home_parent.device, 115200)
			ser.close()

		except SerialException:
			self.home_parent.statusBar().showMessage("Invalid device, please check the device selected")
			return
		
		try:
			new_position = str(int(self.move_to.text())) + ','
			step_size = str(self.step_size_selector.currentIndex()) + ','
			motor_speed = str(self.motor_speed.value())

		except ValueError:
			self.home_parent.statusBar().showMessage("Invalid position")
			return

		print("execute," + new_position + step_size + motor_speed)
		self.send_serial_command("execute," + new_position + step_size + motor_speed)

		self.go_to_start()
		self.start_data_collection()

	def test_fn(self):
		self.send_serial_command("TEST,Debug,pan")

	def go_to_start(self):
		self.send_serial_command("go_to_start")

	def go_to_end(self):
		self.send_serial_command("go_to_end")

	def go_to_distance(self):
		return

	def start_data_collection(self):
		if self.home_parent.plot_settings.callback_id == None:

			def add_callback():
				self.home_parent.plot_settings.callback_id = self.home_parent.plot_settings.doc.add_periodic_callback(self.home_parent.plot_settings.update_function, 1)

			self.home_parent.plot_settings.doc.add_next_tick_callback(add_callback)
				

	def stop_data_collection(self):
		if self.home_parent.plot_settings.callback_id != None:

			def remove_callback():
				self.home_parent.plot_settings.doc.remove_periodic_callback(self.home_parent.plot_settings.callback_id)
				self.home_parent.plot_settings.callback_id = None

			self.home_parent.plot_settings.doc.add_next_tick_callback(remove_callback)
from PySide2.QtCore import Qt
from PySide2.QtCore import Signal
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMainWindow, QMessageBox
from PySide2.QtWidgets import QAction, QMenu
from PySide2.QtWidgets import QGridLayout, QGroupBox, QSizePolicy, QVBoxLayout, QHBoxLayout, QFormLayout
from PySide2.QtWidgets import QCheckBox, QDoubleSpinBox, QLineEdit, QLabel
from PySide2.QtWidgets import QPushButton, QSlider, QWidget

from DoubleSlider import DoubleSlider


def toggleControlEnable(control: QWidget):
    control.setEnabled(not control.isEnabled())


def createReadOnlyLineEdit(content: str):
    lineEdit = QLineEdit(content)
    lineEdit.setAlignment(Qt.AlignCenter)
    lineEdit.setReadOnly(True)
    return lineEdit


def createDoubleSpinBox():
    spinbox = QDoubleSpinBox()
    spinbox.setDecimals(3)
    spinbox.setValue(0.000)
    spinbox.setAlignment(Qt.AlignCenter)
    return spinbox


def createPositionLabel(name: str):
        positionLabel = QLabel(name)
        positionLabel.setAlignment(Qt.AlignCenter)
        positionLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return positionLabel


def updateConnectionStatusLineEdit(lineEdit: QLineEdit, connectionStatus: bool):
    lineEdit.setText("Connected" if connectionStatus else "Disconnected")


def updatePositionLineEdit(lineEdit: QLineEdit, newPosition: float):
    lineEdit.setText(f"{newPosition:+8.3f}")


class MainView(QMainWindow):
    applicationClosed = Signal()

    def __init__(self):
        super().__init__()

        menuBar = self.menuBar()
        menuBar.addMenu(self.createFileMenu())
        menuBar.addMenu(self.createSettingsMenu())
        menuBar.addMenu(self.createHelpMenu())

        self.statusBar().showMessage("Ready")

        connectionStatusGroupBox = self.createConnectionStatusGroup()
        positionIndicationGroupBox = self.createPositionIndicationGroup()
        turnTableControlGroupBox = self.createTurnTableControlGroup()

        mainWidgetLayout = QVBoxLayout()
        mainWidgetLayout.addWidget(connectionStatusGroupBox)
        mainWidgetLayout.addWidget(positionIndicationGroupBox)
        mainWidgetLayout.addWidget(turnTableControlGroupBox)

        mainWidgetGroup = QGroupBox()
        mainWidgetGroup.setLayout(mainWidgetLayout)

        self.setCentralWidget(mainWidgetGroup)


#------------------------------------------------------------------------------
# Interface Creation Helper Functions
#------------------------------------------------------------------------------
    def createFileMenu(self):
        self.loadZeroPositionDataAction = QAction("Load Zero Position", self)
        self.saveZeroPositionDataAction = QAction("Save Zero Position", self)
        exitAction = QAction(
            "E&xit", 
            self, 
            shortcut="Ctrl+Q", 
            statusTip="Exit the application", 
            triggered=self.close
        )

        fileMenu = QMenu("File")
        fileMenu.addAction(self.loadZeroPositionDataAction)
        fileMenu.addAction(self.saveZeroPositionDataAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        return fileMenu


    def createSettingsMenu(self):
        self.applicationSettingsAction = QAction("Settings", self)

        settingsManagerMenu = QMenu("Settings")
        settingsManagerMenu.addAction(self.applicationSettingsAction)

        return settingsManagerMenu


    def createHelpMenu(self):
        helpViewAction = QAction("Help", self)
        aboutViewAction = QAction("About", self)

        helpMenu = QMenu("Help")
        helpMenu.addAction(helpViewAction)
        helpMenu.addAction(aboutViewAction)

        return helpMenu


    def createPositionIndicationGroup(self):
        self.currentPositionLineEdit = createReadOnlyLineEdit("+0.000")
        self.targetPositionLineEdit = createReadOnlyLineEdit("+0.000")
        self.positionErrorLineEdit = createReadOnlyLineEdit("+0.000")

        self.setCurrentPositionAsZeroButton = QPushButton("Set As Zero")        
        self.resetZeroPositionButton = QPushButton("Reset Zero")

        positionInformationLayout = QGridLayout()
        positionInformationLayout.addWidget(createPositionLabel("Current"), 0, 0)
        positionInformationLayout.addWidget(createPositionLabel("Target"), 0, 1)
        positionInformationLayout.addWidget(createPositionLabel("Error"), 0, 2)
        positionInformationLayout.addWidget(self.currentPositionLineEdit, 1, 0)
        positionInformationLayout.addWidget(self.targetPositionLineEdit, 1, 1)
        positionInformationLayout.addWidget(self.positionErrorLineEdit, 1, 2)
        positionInformationLayout.addWidget(self.setCurrentPositionAsZeroButton, 2, 0)
        positionInformationLayout.addWidget(self.resetZeroPositionButton, 3, 0)

        positionGroupBox = QGroupBox("Azimuth")
        positionGroupBox.setLayout(positionInformationLayout)

        return positionGroupBox


    def createTurnTableControlGroup(self):
        self.gotoPositionSpinBox = createDoubleSpinBox() 
        self.stepSizeSpinBox = createDoubleSpinBox()

        self.goPushButton = QPushButton("Go")
        self.goPushButton.setEnabled(False)
        self.goPushButton.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_G))

        self.stepPushButton = QPushButton("Step")
        self.stepPushButton.setEnabled(False)
        self.stepPushButton.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))

        self.enableSteppingCheckBox = QCheckBox("Enable Stepping")
        self.enableSteppingCheckBox.setEnabled(False)
        self.enableSteppingCheckBox.clicked.connect(self.stepPushButton.setEnabled)

        self.stopPushButton = QPushButton("STOP")
        self.stopPushButton.setEnabled(False)
        self.stopPushButton.pressed.connect(lambda: self.motorVoltageSlider.setValue(0.000))
        self.stopPushButton.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_T))

        turnTableVoltageControlGroup = self.createTurnTableVoltageControlGroup()

        turnTableControlGridLayout = QGridLayout()
        turnTableControlGridLayout.addWidget(QLabel("Go To Position:"), 0, 0)
        turnTableControlGridLayout.addWidget(self.gotoPositionSpinBox, 0, 1)
        turnTableControlGridLayout.addWidget(self.goPushButton, 0, 2)
        turnTableControlGridLayout.addWidget(QLabel("Step Size:"), 1, 0)
        turnTableControlGridLayout.addWidget(self.stepSizeSpinBox, 1, 1)
        turnTableControlGridLayout.addWidget(self.stepPushButton, 1, 2)
        turnTableControlGridLayout.addWidget(self.enableSteppingCheckBox, 1, 3)
        turnTableControlGridLayout.addWidget(self.stopPushButton, 2, 3)
        turnTableControlGridLayout.addWidget(turnTableVoltageControlGroup, 3, 0, 3, 4)

        turnTableGroupBox = QGroupBox("Turn Table Controls")
        turnTableGroupBox.setLayout(turnTableControlGridLayout)

        return turnTableGroupBox


    def createTurnTableVoltageControlGroup(self):
        self.motorVoltageSlider = DoubleSlider(orientation=Qt.Orientation.Horizontal)
        self.motorVoltageSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.motorVoltageSlider.setTickInterval(200)
        self.motorVoltageSlider.setEnabled(False)

        self.motorVoltageSliderValueSpinBox = createDoubleSpinBox()
        self.motorVoltageSliderValueSpinBox.setEnabled(False)

        self.motorVoltageSliderValueSpinBox.valueChanged.connect(self.motorVoltageSlider.setValue)
        self.motorVoltageSlider.doubleValueChanged.connect(self.motorVoltageSliderValueSpinBox.setValue)

        self.resetVoltageButton = QPushButton("Reset")
        self.resetVoltageButton.setEnabled(False)
        self.resetVoltageButton.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_R))
        self.resetVoltageButton.pressed.connect(lambda: self.motorVoltageSlider.setValue(0.000))

        sliderGridLayout = QGridLayout()
        sliderGridLayout.addWidget(QLabel("Min Voltage"), 0, 0, 1, 1)
        sliderGridLayout.addWidget(QLabel("Max Voltage"), 0, 4, 1, 1)
        sliderGridLayout.addWidget(self.motorVoltageSlider, 1, 0, 1, 5)
        sliderGridLayout.addWidget(self.motorVoltageSliderValueSpinBox, 2, 1, 1, 1)
        sliderGridLayout.addWidget(self.resetVoltageButton, 2, 4, 1, 1)

        voltageControlGroupBox = QGroupBox()
        voltageControlGroupBox.setLayout(sliderGridLayout)

        return voltageControlGroupBox


    def createConnectionStatusGroup(self):
        connectionStatusGroup = QGroupBox("Connection Status")

        self.shaftEncoderConnectionStatusLineEdit = createReadOnlyLineEdit("Disconnected")
        self.motorControllerConnectionStatusLineEdit = createReadOnlyLineEdit("Disconnected")
        self.watchDogConnectionStatusLineEdit = createReadOnlyLineEdit("Disconnected")
        self.tcpServerConnectionStatusLineEdit = createReadOnlyLineEdit("Disconnected")

        self.connectButton = QPushButton("Connect")

        self.disconnectButton = QPushButton("Disconnect")
        self.disconnectButton.setEnabled(False)

        connectionButtonLayout = QHBoxLayout()
        connectionButtonLayout.addWidget(self.connectButton)
        connectionButtonLayout.addWidget(self.disconnectButton)

        connectionStatusLayout = QFormLayout()
        connectionStatusLayout.addRow(QLabel("Shaft Encoder: "), self.shaftEncoderConnectionStatusLineEdit)
        connectionStatusLayout.addRow(QLabel("Motor Controller: "), self.motorControllerConnectionStatusLineEdit)
        connectionStatusLayout.addRow(QLabel("Watchdog: "), self.watchDogConnectionStatusLineEdit)
        connectionStatusLayout.addRow(QLabel("TCP Server: "), self.tcpServerConnectionStatusLineEdit)
        connectionStatusLayout.addRow(connectionButtonLayout)

        connectionStatusGroup.setLayout(connectionStatusLayout)

        return connectionStatusGroup


    def closeEvent(self, event):
        messageBox = QMessageBox()
        messageBox.setText("The Turn Table is currently still running.")
        messageBox.setInformativeText("Are you sure you want to exit?")
        messageBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        messageBox.setDefaultButton(QMessageBox.Cancel)
        
        response = messageBox.exec_()

        if response == QMessageBox.Ok:
            self.applicationClosed.emit()
            event.accept()
        elif response == QMessageBox.Cancel:
            event.ignore()


#------------------------------------------------------------------------------
# Callback functions for handling GUI events
#------------------------------------------------------------------------------
    def updatePositionLineEdits(self, newPosition):
        updatePositionLineEdit(self.currentPositionLineEdit, newPosition.current)
        updatePositionLineEdit(self.targetPositionLineEdit, newPosition.target)
        updatePositionLineEdit(self.positionErrorLineEdit, newPosition.error)


    def updateConnectionStatusLineEdits(self, shaftEncoder: bool, motorController: bool, watchdog: bool, tcpServer: bool):
        updateConnectionStatusLineEdit(self.shaftEncoderConnectionStatusLineEdit, shaftEncoder)
        updateConnectionStatusLineEdit(self.motorControllerConnectionStatusLineEdit, motorController)
        updateConnectionStatusLineEdit(self.watchDogConnectionStatusLineEdit, watchdog)
        updateConnectionStatusLineEdit(self.tcpServerConnectionStatusLineEdit, tcpServer)


    def toggleControls(self):
        toggleControlEnable(self.enableSteppingCheckBox)
        toggleControlEnable(self.stopPushButton)
        toggleControlEnable(self.goPushButton)
        toggleControlEnable(self.connectButton)
        toggleControlEnable(self.disconnectButton)
        toggleControlEnable(self.motorVoltageSlider)
        toggleControlEnable(self.motorVoltageSliderValueSpinBox)
        toggleControlEnable(self.resetVoltageButton)
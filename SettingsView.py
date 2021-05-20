from dataclasses import dataclass

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QFormLayout, QGroupBox, QHBoxLayout,
                               QTabWidget, QVBoxLayout,
                               QWidget)
from PySide2.QtWidgets import QLabel, QLineEdit
from PySide2.QtWidgets import QPushButton

from ConfigurationManager import ConfigurationManager


def createLineEdit(value):
    tempValue = str(value) if not isinstance(value, str) else value
    lineEdit = QLineEdit(tempValue)
    lineEdit.setAlignment(Qt.AlignCenter)

    return lineEdit

def getNumberFromLineEdit(lineEdit: QLineEdit, type: str):
    return lineEdit.text().toInt if type == 'int' else lineEdit.text().toFloat()

class SettingsView(QWidget):
    def __init__(self, configManager: ConfigurationManager):
        super().__init__()
        self.configManager = configManager
        self.createSettingsView()

    def createTurnTableControllerTabWidget(self):
        ipAddressLabel = QLabel("IP Address: ")
        self.ipAddressLineEdit = createLineEdit(self.configManager.turnTableIPAddress)

        self.watchdogPortLineEdit = createLineEdit(self.configManager.watchdogPort)
        self.shaftEncoderPortLineEdit = createLineEdit(self.configManager.shaftEncoderPort)
        self.motorControllerPortLineEdit = createLineEdit(self.configManager.motorControllerPort)

        portSettingsLayout = QFormLayout()
        portSettingsLayout.addRow(QLabel("Watchdog Port: "), self.watchdogPortLineEdit)
        portSettingsLayout.addRow(QLabel("Shaft Encoder Port: "), self.shaftEncoderPortLineEdit)
        portSettingsLayout.addRow(QLabel("Motor Controller Port: "), self.motorControllerPortLineEdit)

        portsGroupBox = QGroupBox("Ports")
        portsGroupBox.setLayout(portSettingsLayout)

        ipAddressLayout = QHBoxLayout()
        ipAddressLayout.addWidget(ipAddressLabel)
        ipAddressLayout.addWidget(self.ipAddressLineEdit)

        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(ipAddressLayout)
        settingsLayout.addWidget(portsGroupBox)

        connectionSettingsGroupBox = QGroupBox("Connection Settings")
        connectionSettingsGroupBox.setLayout(settingsLayout)

        self.proportionalGainLineEdit = createLineEdit(self.configManager.controlProportionalGain)
        self.integralGainLineEdit = createLineEdit(self.configManager.controlIntegralGain)
        self.derivativeGainLineEdit = createLineEdit(self.configManager.controlDerivativeGain)
        self.minimumControlSignalLineEdit = createLineEdit(self.configManager.minimumControlSignalValue)

        pidControllerSettingsLayout = QFormLayout()
        pidControllerSettingsLayout.addRow(QLabel("Proportional Gain: "), self.proportionalGainLineEdit)
        pidControllerSettingsLayout.addRow(QLabel("Integral Gain: "), self.integralGainLineEdit)
        pidControllerSettingsLayout.addRow(QLabel("Derivative Gain: "), self.derivativeGainLineEdit)
        pidControllerSettingsLayout.addRow(QLabel("Minimum Control Signal: "), self.minimumControlSignalLineEdit)

        pidControllerSettingsGroupBox = QGroupBox("PID Controller")
        pidControllerSettingsGroupBox.setLayout(pidControllerSettingsLayout)

        self.minimumGotoPositionLineEdit = createLineEdit(self.configManager.minimumGotoPosition)
        self.maximumGotoPositionLineEdit = createLineEdit(self.configManager.maximumGotoPosition)
        self.minimumStepSizeLineEdit = createLineEdit(self.configManager.minimumStepSize)
        self.maximumStepSizeLineEdit = createLineEdit(self.configManager.maximumStepSize)

        positionSettingsLayout = QFormLayout()
        positionSettingsLayout.addRow(QLabel("Minimum Goto Position: "), self.minimumGotoPositionLineEdit)
        positionSettingsLayout.addRow(QLabel("Maximum Goto Position: "), self.maximumGotoPositionLineEdit)
        positionSettingsLayout.addRow(QLabel("Minimum Step Size: "), self.minimumStepSizeLineEdit)
        positionSettingsLayout.addRow(QLabel("Maximum Step Size: "), self.maximumStepSizeLineEdit)

        positionSettingsGroupBox = QGroupBox("Position Settings")
        positionSettingsGroupBox.setLayout(positionSettingsLayout)

        settingsLayout = QVBoxLayout()
        settingsLayout.addWidget(connectionSettingsGroupBox)
        settingsLayout.addWidget(pidControllerSettingsGroupBox)
        settingsLayout.addWidget(positionSettingsGroupBox)

        settingsTabWidget = QWidget()
        settingsTabWidget.setLayout(settingsLayout)

        return settingsTabWidget


    def createMotorControllerTabWidget(self):
        self.maximumVoltageLineEdit = createLineEdit(self.configManager.maximumVoltage)
        self.minimumVoltageLineEdit = createLineEdit(self.configManager.minimumVoltage)
        self.maximumVoltageStepLineEdit = createLineEdit(self.configManager.maximumVoltageStep)
        self.minimumVoltageStepLineEdit = createLineEdit(self.configManager.minimumVoltageStep)
        self.voltageStepLineEdit = createLineEdit(self.configManager.voltageStep)
        self.voltageSamplePeriodLineEdit = createLineEdit(self.configManager.voltageSamplePeriod)
        self.voltageUpdatePeriodLineEdit = createLineEdit(self.configManager.voltageUpdatePeriod)

        motorControllerSettingsLayout = QFormLayout()
        motorControllerSettingsLayout.addRow(QLabel("Minimum Voltage: "), self.minimumVoltageLineEdit)
        motorControllerSettingsLayout.addRow(QLabel("Maximum Votlage: "), self.maximumVoltageLineEdit)
        motorControllerSettingsLayout.addRow(QLabel("Minimum Voltage Step: "), self.minimumVoltageStepLineEdit)
        motorControllerSettingsLayout.addRow(QLabel("Maximum Voltage Step: "), self.maximumVoltageStepLineEdit)
        motorControllerSettingsLayout.addRow(QLabel("Voltage Step: "), self.voltageStepLineEdit)
        motorControllerSettingsLayout.addRow(QLabel("Voltage Sample Period: "), self.voltageSamplePeriodLineEdit)
        motorControllerSettingsLayout.addRow(QLabel("Voltage Update Period: "), self.voltageUpdatePeriodLineEdit)

        settingsTabWidget = QWidget()
        settingsTabWidget.setLayout(motorControllerSettingsLayout)

        return settingsTabWidget


    def createWatchdogTabWidget(self):
        self.watchdogTriggerPeriodLineEdit = createLineEdit(self.configManager.watchdogTriggerPeriod)

        watchdogSettingslayout = QFormLayout()
        watchdogSettingslayout.addRow(QLabel("Trigger Period: "), self.watchdogTriggerPeriodLineEdit)

        settingsWidget = QWidget()
        settingsWidget.setLayout(watchdogSettingslayout)

        return settingsWidget


    def createShaftEncoderTabWidget(self):
        self.postionSamplePeriodLineEdit = createLineEdit(self.configManager.positionSamplePeriod)

        shaftEncoderSettingsLayout = QFormLayout()
        shaftEncoderSettingsLayout.addRow(QLabel("Position Sample Period: "), self.postionSamplePeriodLineEdit)

        settingsWidget = QWidget()
        settingsWidget.setLayout(shaftEncoderSettingsLayout)

        return settingsWidget


    def createTCPServerTabWidget(self):
        self.tcpServerIPAddressLineEdit = createLineEdit(self.configManager.tcpServerIPAddress)
        self.tcpServerPortLineEdit = createLineEdit(self.configManager.tcpServerPort)
        self.tcpServerPollingDelayLineEdit = createLineEdit(self.configManager.pollDelay)

        tcpServerSettingsLayout =  QFormLayout()
        tcpServerSettingsLayout.addRow(QLabel("TCP Server IP Addres: "), self.tcpServerIPAddressLineEdit)
        tcpServerSettingsLayout.addRow(QLabel("TCP Server Port: "), self.tcpServerPortLineEdit)
        tcpServerSettingsLayout.addRow(QLabel("Poll Delay: "), self.tcpServerPollingDelayLineEdit)

        settingsWidget = QWidget()
        settingsWidget.setLayout(tcpServerSettingsLayout)

        return settingsWidget


    def saveTurnTableControllerSettings(self):
        self.configManager.turnTableIPAddress = self.ipAddressLineEdit.text()
        self.configManager.shaftEncoderPort = getNumberFromLineEdit(self.shaftEncoderPortLineEdit, 'int')
        self.configManager.motorControllerPort = getNumberFromLineEdit(self.motorControllerPortLineEdit, 'int') 
        self.configManager.watchdogPort = getNumberFromLineEdit(self.watchdogPortLineEdit, 'int')

        self.configManager.controlProportionalGain = getNumberFromLineEdit(self.proportionalGainLineEdit, 'float')
        self.configManager.controlIntegralGain = getNumberFromLineEdit(self.integralGainLineEdit, 'float')
        self.configManager.controlDerivativeGain = getNumberFromLineEdit(self.derivativeGainLineEdit, 'float')
        self.configManager.minimumControlSignalValue = getNumberFromLineEdit(self.minimumControlSignalLineEdit, 'float')

        self.configManager.minimumGotoPosition = getNumberFromLineEdit(self.minimumGotoPositionLineEdit, 'float')
        self.configManager.maximumGotoPosition = getNumberFromLineEdit(self.maximumGotoPositionLineEdit, 'float')
        self.configManager.minimumStepSize = getNumberFromLineEdit(self.minimumStepSizeLineEdit, 'float')
        self.configManager.maximumStepSize = getNumberFromLineEdit(self.maximumStepSizeLineEdit, 'float')


    def saveMotorControllerSettings(self):
        self.configManager.minimumVoltage = getNumberFromLineEdit(self.minimumVoltageLineEdit, 'float')
        self.configManager.maximumVoltage = getNumberFromLineEdit(self.maximumVoltageLineEdit, 'float')
        self.configManager.minimumVoltageStep = getNumberFromLineEdit(self.minimumVoltageStepLineEdit, 'float')
        self.configManager.maximumVoltageStep = getNumberFromLineEdit(self.maximumVoltageStepLineEdit, 'float')
        self.configManager.voltageStep = getNumberFromLineEdit(self.voltageStepLineEdit, 'float')
        self.configManager.voltageSamplePeriod = getNumberFromLineEdit(self.voltageSamplePeriodLineEdit, 'float')
        self.configManager.voltageUpdatePeriod = getNumberFromLineEdit(self.voltageUpdatePeriodLineEdit, 'float')


    def saveShaftEncoderSettings(self):
        self.configManager.positionSamplePeriod = getNumberFromLineEdit(self.postionSamplePeriodLineEdit, 'float')
        
    
    def saveWatchdogSettings(self):
        self.configManager.watchdogTriggerPeriod = getNumberFromLineEdit(self.watchdogTriggerPeriodLineEdit, 'float')


    def saveTCPServerSettings(self):
        self.configManager.tcpServerIPAddress = self.tcpServerIPAddressLineEdit.text()
        self.configManager.tcpServerIPPort = getNumberFromLineEdit(self.tcpServerPortLineEdit, 'int')
        self.configManager.tcpServerPollingDelay = getNumberFromLineEdit(self.tcpServerPollingDelayLineEdit, 'float')


    def saveSettings(self):
        self.saveTurnTableControllerSettings()
        self.saveMotorControllerSettings()
        self.saveShaftEncoderSettings()
        self.saveWatchdogSettings()
        self.saveTCPServerSettings()

        self.configManager.writeConfigFile()


    def createSettingsView(self):
        reloadSettingsButton = QPushButton("Reload")
        reloadSettingsButton.clicked.connect(self.configManager.readConfigFile)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.hide)
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.saveSettings)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(reloadSettingsButton)
        buttonsLayout.addWidget(saveButton)
        buttonsLayout.addWidget(cancelButton)

        settingsTabWidget = QTabWidget()
        settingsTabWidget.addTab(self.createTurnTableControllerTabWidget(), 'Turntable')
        settingsTabWidget.addTab(self.createMotorControllerTabWidget(), 'Motor Contoller')
        settingsTabWidget.addTab(self.createShaftEncoderTabWidget(), 'Shaft Encoder')
        settingsTabWidget.addTab(self.createWatchdogTabWidget(), 'Watchdog')
        settingsTabWidget.addTab(self.createTCPServerTabWidget(), 'TCP Server')

        layout = QVBoxLayout()
        layout.addWidget(settingsTabWidget)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)

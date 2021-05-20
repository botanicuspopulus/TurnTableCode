import logging
import math
import re
import time
from threading import Event, Thread
from dataclasses import dataclass

from ConfigurationManager import ConfigurationManager
from ZeroPointManager import ZeroPointManager
from JobThread import TimedJobThread
from LANConnection import LANConnection
from MainView import MainView
from SettingsView import SettingsView
from MotorControllerModel import MotorControllerModel
from ShaftEncoderModel import ShaftEncoderModel
from TCPServer import TCPServer, TCPCallbacks
from ZeroPointViews import LoadZeroPointView, SaveZeroPoint


def isValidIPAddress(ipAddress: str) -> bool:
    ipAddressRegex = re.compile("(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])")
    return bool(re.search(ipAddressRegex, ipAddress))


def stopTimedJobThread(jobThread: TimedJobThread):
    if jobThread is not None:
        jobThread.stop()


@dataclass
class ControllerThreads:
    gotoPosition: TimedJobThread = None
    updateGUI: TimedJobThread = None


@dataclass
class Position:
    _current: float = 0.000
    target: float = 0.000
    offset: float = 0.000

    @property
    def current(self):
        return self._current + self.offset

    @current.setter
    def current(self, newPosition):
        self._current = newPosition

    @property
    def error(self):
        return self.current - self.target


#------------------------------------------------------------------------------
# Turn Table Controller
#------------------------------------------------------------------------------
class TurnTableController:
    def __init__(self, settingsManager: ConfigurationManager, zeroPointManager: ZeroPointManager):
        self._settingsManager = settingsManager
        self._zeroPointManager = zeroPointManager
        self._stopTurnTableEvent = Event()
        self._jobThreads = ControllerThreads()
        self._position = Position()

        def connectionFactory(port: int, name: str) -> LANConnection:
            return LANConnection(
                self._settingsManager.turnTableIPAddress,
                port,
                name=name,
                timeout=self._settingsManager.timeout
            )

        callbacks = TCPCallbacks(
            getAzimuth=self.getCurrentPosition, 
            getElevation=self.getCurrentPosition, 
            setAzimuth=self.createGotoPositionJob, 
            setElevation=self.createGotoPositionJob, 
            stop=self.stop,
        )
        self._tcpServer = TCPServer(callbacks=callbacks, settingsManager=self._settingsManager)

        self._shaftEncoder = ShaftEncoderModel(
            connectionFactory(self._settingsManager.shaftEncoderPort, "Shaft Encoder Connection"), 
            settingsManager=settingsManager)
        self._motorController = MotorControllerModel(
            watchdogConnection=connectionFactory(self._settingsManager.watchdogPort, "Watchdog Connection"), 
            motorControllerConnection=connectionFactory(self._settingsManager.motorControllerPort, "Motor Controller Connection"),
            settingsManager=settingsManager,
        )

        self._mainView = MainView()
        self._settingsManagerView = SettingsView(self._settingsManager)
        self.showMainView()


    def showMainView(self):
        self._mainView.stepSizeSpinBox.setRange(self._settingsManager.minimumStepSize, self._settingsManager.maximumStepSize)
        self._mainView.gotoPositionSpinBox.setRange(self._settingsManager.minimumGotoPosition, self._settingsManager.maximumGotoPosition)
        self._mainView.motorVoltageSliderValueSpinBox.setRange(self._settingsManager.minimumVoltage, self._settingsManager.maximumVoltage)
        self._mainView.motorVoltageSlider.setRange(self._settingsManager.minimumVoltage, self._settingsManager.maximumVoltage)

        self._mainView.applicationSettingsAction.triggered.connect(self._settingsManagerView.show)
        self._mainView.loadZeroPositionDataAction.triggered.connect(self.loadZeroPosition)
        self._mainView.saveZeroPositionDataAction.triggered.connect(self.saveZeroPosition)
        self._mainView.connectButton.clicked.connect(self.connect)
        self._mainView.disconnectButton.clicked.connect(self.disconnect)
        self._mainView.goPushButton.clicked.connect(self.createGotoPositionJob)
        self._mainView.motorVoltageSlider.doubleValueChanged.connect(self.setMotorVoltage)
        self._mainView.resetVoltageButton.clicked.connect(self.resetMotorVoltage)
        self._mainView.stopPushButton.clicked.connect(self.stopMotion)
        self._mainView.stepPushButton.clicked.connect(self.stepPosition)
        self._mainView.resetZeroPositionButton.clicked.connect(self.resetPositionOffest)
        self._mainView.setCurrentPositionAsZeroButton.clicked.connect(self.setPositionOffset)
        self._mainView.applicationClosed.connect(self.stop)

        self._mainView.motorVoltageSlider.setValue(0.000)

        self._mainView.show()


#------------------------------------------------------------------------------
# Starting and Stopping Methods
#------------------------------------------------------------------------------
    def start(self):
        self._jobThreads.updateGUI = TimedJobThread(
            self._settingsManager.GUIUpdatePeriod, 
            self.updateGUI
        )
        self._jobThreads.updateGUI.start()


    def stop(self):
        logging.debug("Stopping Turn Table Controller")
        self.stopMotion()
        self.disconnect()
        logging.debug("Turn Table Controller Stopped...")


    def stopMotion(self):
        if self._jobThreads.gotoPosition is not None:
            self._stopTurnTableEvent.set()
            self._jobThreads.gotoPosition = None

        if self._motorController.getCurrentVoltage() != 0.000:
            self.resetMotorVoltage()


#------------------------------------------------------------------------------
# Connection Handling Methods
#------------------------------------------------------------------------------
    def connect(self):
        self._motorController.start()
        self._shaftEncoder.start()
        self._tcpServer.connect()

        if self._motorController.isWatchdogConnected() and self._motorController.isMotorControllerConnected() and self._shaftEncoder.isConnected() and self._tcpServer.isConnected():
            self._mainView.toggleControls()


    def disconnect(self):
        self._motorController.stop()
        self._shaftEncoder.stop()
        self._tcpServer.disconnect()

        if self._motorController.isWatchdogConnected() and self._motorController.isMotorControllerConnected() and self._shaftEncoder.isConnected() and self._tcpServer.isConnected():
            self._mainView.toggleControls()


#------------------------------------------------------------------------------
# Position Helper Methods
#------------------------------------------------------------------------------
    def setPositionOffset(self):
        self._position.offset = -self._shaftEncoder.currentPosition


    def resetPositionOffest(self):
        self._position.offset = 0.000


    def getCurrentPosition(self) -> float:
        self._position.current = self._shaftEncoder.currentPosition
        return self._position.current


#------------------------------------------------------------------------------
# GUI Update Helper Methods
#------------------------------------------------------------------------------
    def updateGUI(self):
        shaftEncoderConnectionStatus = self._shaftEncoder.isConnected()
        motorControllerConnectionStatus = self._motorController.isMotorControllerConnected()
        watchdogConnectionStatus = self._motorController.isWatchdogConnected()
        tcpServerConnectionStatus = self._tcpServer.isConnected()

        self._mainView.updateConnectionStatusLineEdits(
            shaftEncoderConnectionStatus, 
            motorControllerConnectionStatus, 
            watchdogConnectionStatus, 
            tcpServerConnectionStatus)
        self._mainView.updatePositionLineEdits(self._position)


#------------------------------------------------------------------------------
# Motor Control Methods
#------------------------------------------------------------------------------
    def setMotorVoltage(self, newVoltage: float):
        if (not self._motorController.isEnabled()) and (newVoltage != 0.000):
            self._motorController.toggleEnable()
        self._motorController.setVoltage(newVoltage=newVoltage)


    def resetMotorVoltage(self):
        if self._motorController.isEnabled():
            self._motorController.toggleEnable()
        self._motorController.setVoltage(0.000)


    def createGotoPositionJob(self, targetPosition: float):
        self._jobThreads.gotoPosition = Thread(target=self.gotoPosition, args=(targetPosition,))
        self._jobThreads.gotoPosition.start()


    def stepPosition(self, step: float):
        currentPosition = self.getCurrentPosition()
        self.createGotoPositionJob(currentPosition + step)


    def gotoPosition(self, targetPosition: float):
        maxVoltage = self._settingsManager.maximumVoltage
        updatePeriod = self._settingsManager.voltageUpdatePeriod
        KP = self._settingsManager.controlProportionalGain
        KI = self._settingsManager.controlIntegralGain
        KD = self._settingsManager.controlDerivativeGain
        minimumControlSignalValue = self._settingsManager.minimumControlSignalValue
        maximumAllowedError = self._settingsManager.maximumAllowedError

        self._position.target = targetPosition

        if not self._motorController.isEnabled():
            self._motorController.toggleEnable()

        previousError = 0

        if self._stopTurnTableEvent.is_set():
            self._stopTurnTableEvent.clear()

        while True:
            error = self._position.error

            if (abs(error) < maximumAllowedError) or (self._stopTurnTableEvent.is_set()):
                self._motorController.setVoltage(0.000)
                self._motorController.toggleEnable()
                break

            errorDelta = error - previousError
            previousError = error

            voltageControlSignal = (KP*error + KI*error*updatePeriod + KD*errorDelta/updatePeriod)
            voltageControlSignal = sorted((-maxVoltage, voltageControlSignal, maxVoltage))[1]
            voltageControlSignal = math.copysign(max(abs(voltageControlSignal), minimumControlSignalValue), voltageControlSignal)

            self._motorController.setVoltage(voltageControlSignal)
            time.sleep(updatePeriod)


    def saveZeroPosition(self):
        saveZeroPoint = SaveZeroPoint(self._position.offset, self._zeroPointManager)
        saveZeroPoint.exec_()


    def loadZeroPosition(self):
        loadZeroPoint = LoadZeroPointView(self._zeroPointManager)
        loadZeroPoint.exec_()
        self._position.offset = self._zeroPointManager.getOffset()
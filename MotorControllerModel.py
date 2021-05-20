import logging
from dataclasses import dataclass
from enum import Enum
from threading import Lock

from ConfigurationManager import ConfigurationManager
from ConnectionInterface import ConnectionInterface
from JobThread import TimedJobThread
from Watchdog import Watchdog


# ------------------------------------------------------------------------------
# Enumeration Constants
# ------------------------------------------------------------------------------
class RampDirection(Enum):
    DOWN = -1
    UP = 1

    def __str__(self):
        return self.name


class MotorState(Enum):
    RAMPING_UP = 0
    RAMPING_DOWN = 1
    RUNNING = 2
    STOPPED = 3

    def __str__(self):
        return self.name


# ------------------------------------------------------------------------------
# Voltage Data Class
# ------------------------------------------------------------------------------
@dataclass
class Voltage:
    current: float
    step: float


# ------------------------------------------------------------------------------
# Auxiliary Data Classes
# ------------------------------------------------------------------------------
@dataclass
class Jobs:
    updateVoltage: TimedJobThread


# ------------------------------------------------------------------------------
# Motor Controller Model Class
# ------------------------------------------------------------------------------
class MotorControllerModel:
    def __init__(
        self, motorControllerConnection: ConnectionInterface, 
        watchdogConnection: ConnectionInterface, 
        settingsManager: ConfigurationManager):

        self._settingsManager = settingsManager
        
        self._serialAddress = '01'
        self._serialChannel = '0'
        self._getVoltageCommand = f"${self._serialAddress}8{self._serialChannel}\r".encode(self._settingsManager.Encoding)

        self._voltage = Voltage(current=0.000, step=self._settingsManager.voltageStep)
        self._motorState = MotorState.STOPPED

        self._connection = motorControllerConnection
        self._watchdog = Watchdog(watchdogConnection, settingsManager=self._settingsManager)
        
        self._jobs = Jobs(
            updateVoltage=TimedJobThread(self._settingsManager.voltageUpdatePeriod, self._updateCurrentVoltage)
        )
        self._lock = Lock()


#------------------------------------------------------------------------------
# Static Methods
#------------------------------------------------------------------------------
    @staticmethod
    def updateMotorState(targetVoltage: float, minimumVoltage: float) -> MotorState:
        return MotorState.RUNNING if (abs(targetVoltage) > minimumVoltage) else MotorState.STOPPED

#------------------------------------------------------------------------------
# Start and Stop Commands
#------------------------------------------------------------------------------
    def start(self):
        if not self._connection.isConnected():
            logging.info("Connecting to the Motor Controller")
            if self._connection.connect():
                logging.info("Succesfully connected tothe Motor Controller")
            else:
                logging.error("Failed to connect to the Motor Controller")
                return

        if self._connection.isConnected():
            logging.info("Motor Controller is connected. Starting the Watchdog Timer")
            self.setVoltage(0.000)
            self._watchdog.start()

            if self._jobs.updateVoltage is None:
                logging.info("Starting the Motor Controller Voltage Update Thread")
                self._jobs.updateVoltage = TimedJobThread(self._settingsManager.voltageUpdatePeriod, self._updateCurrentVoltage)
                self._jobs.updateVoltage.start()


    def stop(self):
        if self._connection.isConnected():
            self.setVoltage(0.000)

            logging.info("Stopping the Motor Controller Voltage Update Thread")
            self._jobs.updateVoltage.stop()
            self._jobs.updateVoltage = None

            logging.info("Stopping the Watchdog Timer")
            self._watchdog.stop()

            logging.info("Disconnecting from the Motor Controller")
            self._connection.disconnect()


    def emergencyStop(self):
        if self.isWatchdogConnected() and self.isMotorControllerConnected():
            self._watchdog.stop()
            self._connection.disconnect()


#------------------------------------------------------------------------------
#   Getter and Setter Functions
#------------------------------------------------------------------------------
    def getCurrentVoltage(self) -> float:
        return self._voltage.current


    @property
    def voltageSamplePeriod(self) -> float:
        return self._settingsManager.voltageSamplePeriod


    @voltageSamplePeriod.setter
    def voltageSamplePeriod(self, newSamplePeriod: float):
        self._settingsManager.voltageSamplePeriod = max(self._settingsManager.minimumVoltageSamplePeriod, newSamplePeriod)


    @property
    def voltageUpdatePeriod(self) -> float:
        return self._settingsManager.voltageUpdatePeriod


    @voltageUpdatePeriod.setter
    def voltageUpdatePeriod(self, newUpdatePeriod: float):
        self._settingsManager.voltageUpdatePeriod = max(self._settingsManager.minimumVoltageUpdatePeriod, newUpdatePeriod)


    def isEnabled(self) -> bool:
        return self._watchdog.isEnabled()


    def isMotorControllerConnected(self) -> bool:
        return self._connection.isConnected()


    def isWatchdogConnected(self) -> bool:
        return self._watchdog.isConnected()


    def getState(self) -> MotorState:
        return self._motorState


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
    def _sendCommandAndGetResponse(self, command: bytes) -> str:
        with self._lock:
            try:
                response = self._connection.getResponse() if self._connection.sendCommand(command) else None
            except TimeoutError as timeoutError:
                logging.exception("Unable to get a response from the Motor Controller. Aborting attempt and turning off the Motor Controller", exc_info=timeoutError)
                self.stop()
                return None

        return None if (response is None) else response.decode(self._settingsManager.Encoding)


    def _updateCurrentVoltage(self):
        response = self._sendCommandAndGetResponse(self._getVoltageCommand)

        if (response is None) or ((response[0] != '!') and (response[-1] != '\r')):
            logging.debug(f"Command Sent: {self._getVoltageCommand}")
            logging.error(f"Bad response received from the Motor Controller on {self._connection}: {response}")
            logging.warning("Turning off the Motor Controller")
            self.stop()
            return

        self._voltage.current = float(response[3:-2])


#------------------------------------------------------------------------------
# 
#------------------------------------------------------------------------------
    def toggleEnable(self):
        if self.isWatchdogConnected():
            logging.debug("Watchdog is not connected")
            return

        self._watchdog.toggleEnable()


    def stepMotorVoltage(self):
        if not self.isMotorControllerConnected():
            logging.debug("Motor Controller is not connectec")
            return

        currentVoltage = self._voltage.current
        newVoltage = currentVoltage + self._voltage.step

        if (self._settingsManager.minimumVoltage <= newVoltage <= self._settingsManager.maximumVoltage):
            self.setVoltage(newVoltage=newVoltage)


    def setVoltage(self, newVoltage):
        """
        Just some Pythonic source-ry to clamp the newVoltage value to the MAXIMUM or MINIMUM voltage values
        It works by taking a list of values [MINIMUM, valueOfInterest, MAXIMUM] and sorting the values in Ascending order
        Once the values are sorted, we select the middle value.
        For example:
        If newVoltage < MINIMUM_VOLTAGE: 
            sorted([MINIMUM_VOLTAGE, newVoltage, MAXIMUM_VOLTAGE]) = [newVoltage, MINIMUM_VOLTAGE, MAXIMUM_VOlTAGE][1] => MINIMUM_VOLTAGE
        if newVoltage > MAXIMUM_VOLTAGE:
            sorted([MINIMUM_VOLTAGE, newVoltage, MAXIMUM_VOLTAGE]) = [MINIMUM_VOLTAGE, MAXIMUM_VOLTAGE, newVoltage][1] => MAXIMUM_VOLTAGE
        if MINIMUM_VOLTAGE <= newVoltage <= MAXIMUM_VOLTAGE:
            sorted([MINIMUM_VOLTAGE, newVoltage, MAXIMUM_VOLTAGE]) = [MINIMUM_VOLTAGE, newVoltage, MAXIMUM_VOLTAGE][1] => newVoltage
        """
        if not self.isMotorControllerConnected():
            logging.debug("Motor Controller is not Connected")
            return

        newVoltage = sorted((self._settingsManager.minimumVoltage, newVoltage, self._settingsManager.maximumVoltage))[1]

        command = f"#{self._serialAddress}{self._serialChannel}{newVoltage:+07.3f}\r".encode(self._settingsManager.Encoding)
        response = self._sendCommandAndGetResponse(command)
        
        if (response is None) or (response != ">\r"):
            logging.error("Bad response received from the Motor Controller")
            self.stop()
            self._motorState = MotorState.STOPPED

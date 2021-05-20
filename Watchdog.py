import logging

from enum import Enum
from threading import Lock

from ConnectionInterface import ConnectionInterface
from JobThread import TimedJobThread
from ConfigurationManager import ConfigurationManager

#------------------------------------------------------------------------------
# Mask Enumerations
#------------------------------------------------------------------------------
class MASKS(Enum):
    TOGGLE_ENABLE = 1
    TOGGLE_WATCHDOG_TRIGGER_STATE = 2


#------------------------------------------------------------------------------
# Watchdog Class
#------------------------------------------------------------------------------False
class Watchdog:
    DEFAULT_ENCODING = "utf-8"
    DEFAULT_BYTE_ORDER = "big"
    
    STOP_COMMAND = int.from_bytes(b"\x18\x00\x00\x00", byteorder=DEFAULT_BYTE_ORDER)
    DEFAULT_TRIGGER_COMMAND = int.from_bytes(b"\x18\x00\x00\x02", byteorder=DEFAULT_BYTE_ORDER)
    
    def __init__(self, connection: ConnectionInterface, settingsManager: ConfigurationManager):
        self._settingsManager = settingsManager
        self._triggerCommand = self.DEFAULT_TRIGGER_COMMAND

        self._connection = connection
        self._job = None
        self._lock = Lock()

#------------------------------------------------------------------------------
# Static Methods
#------------------------------------------------------------------------------
    @staticmethod
    def _translateCommand(command: int) -> bytes:
        return f"{command:0>8X}".encode(Watchdog.DEFAULT_ENCODING)

#------------------------------------------------------------------------------
# Class Properties
#------------------------------------------------------------------------------
    def isEnabled(self) -> bool:
        return (self._triggerCommand & MASKS.TOGGLE_ENABLE.value) == MASKS.TOGGLE_ENABLE.value


#------------------------------------------------------------------------------
# Start and Stop methods
#------------------------------------------------------------------------------
    def start(self):
        if not self._connection.isConnected():
            logging.info("Connecting to the Watchdog Timer")
            if self._connection.connect():
                logging.info("Connection to the Watchdog successfully started")
            else:
                logging.error("Failed to connect to the Watchdog")
                return
            
        if self._job is None:
            logging.info(f"Creating a Timed Thread Job to trigger the Watchdog Timer every {self._triggerPeriod} seconds")
            self._job = TimedJobThread(self._settingsManager.watchdogTriggerPeriod, self._trigger)

        if self._connection.isConnected() and (self._job is not None):
            logging.info("Starting the Watchdog Timer Timed Trigger")
            self._triggerCommand = self.DEFAULT_TRIGGER_COMMAND
            self._job.start()


    def stop(self):
        if self._connection.isConnected():
            if self._job is not None:
                logging.info("Stopping the Watchdog Timer Timed Trigger Job")
                self._job.stop()
                self._job = None
            
            self._triggerCommand = self.STOP_COMMAND

            logging.info("Sending the STOP_COMMAND to turn off all the Watchdog Timer Outputs")
            if not self._sendCommandAndGetResponse(self._triggerCommand):
                logging.error("Unable to send the command to disable the Watchdog. The Watchdog is going to be disabled in an unsafe state")

            logging.info("Disconnecting from the Watchdog Timer")
            self._connection.disconnect()


#------------------------------------------------------------------------------
# Getter and Setter Functions
#------------------------------------------------------------------------------
    @property
    def triggerPeriod(self) -> float:
        return self._settingsManager.watchdogTriggerPeriod


    @triggerPeriod.setter
    def triggerPeriod(self, newTriggerPeriod: float):
        self._triggerPeriod = max(self._settingsManager.minimumWatchdogTriggerPeriod, newTriggerPeriod)


    def isConnected(self) -> bool:
        return self._connection.isConnected()


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
    def _sendCommandAndGetResponse(self, command: int) -> bool:
        if not self._connection.isConnected():
            logging.error("Not connected to the Watchdog. Commands cannot be sent to the Watchdog in this state")
            return False

        try:
            self._connection.sendCommand(self._translateCommand(command))
            response = self._connection.getResponse()
        except TimeoutError as timeoutError:
            logging.exception("The communication attempt with the Watchdog timed out. Aborting attempt and disconnecting", exc_info=timeoutError)
            self.stop()
            return False

        if (response is None) or (response.decode(self.DEFAULT_ENCODING) != "OK\r\n"):
            logging.error(f"A bad response was received from the Watchdog Controller on {self._connection.connectionDetails()}. Stopping and disabling the Watchdog")
            self.stop()
            return False
        return True


    def _trigger(self):
        with self._lock:
            self._triggerCommand ^= MASKS.TOGGLE_WATCHDOG_TRIGGER_STATE.value

            if not self._sendCommandAndGetResponse(self._triggerCommand):
                logging.error("Failure in the _trigger method of the Watchdog. Stopping and disabling the Watchdog")
                self.stop()


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
    def toggleEnable(self):
        with self._lock:
            self._triggerCommand ^= MASKS.TOGGLE_ENABLE.value

            if not self._sendCommandAndGetResponse(self._triggerCommand):
                logging.error("Failure in the toggleEnable method of the Watchdog. Stopping and disabling the Watchdog")
                self._triggerCommand ^= MASKS.TOGGLE_ENABLE.value
                self.stop()
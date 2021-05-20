import logging
from dataclasses import dataclass

from ConfigurationManager import ConfigurationManager
from ConnectionInterface import ConnectionInterface
from JobThread import TimedJobThread


#------------------------------------------------------------------------------
# Mask Enumerations
#------------------------------------------------------------------------------
@dataclass
class MASKS:
    REVOLUTIONS = int.from_bytes(b"\x00\x00\xFF\xFF\x00\x00\x00\x00", byteorder="big")
    STEPS = int.from_bytes(b"\x00\x00\x00\x00\xFF\xFF\x00\x00", byteorder="big")
    ERROR_CHECK = int.from_bytes(b"\x00\x00\x00\x00\x00\x00\xFF\x00", byteorder="big")


#------------------------------------------------------------------------------
# Position Dataclass
#------------------------------------------------------------------------------
@dataclass
class Position:
    STEPS_PER_REVOLUTION = 8192
    MAXIMUM_REVOLUTIONS = 4096
    DEGREES_PER_STEP = 360.0/(STEPS_PER_REVOLUTION-1)
    GEARBOX_REDUCTION = 73

    step: int = 0
    revolution: int = 0

    @property
    def angle(self) -> float:
        step = self.step
        revolution = self.revolution

        # Here we are changing the revolution and step values so that it is possible to account for negative angles.
        # This is accomplished by using the Revolution count from the encoder to determine whether we are going in the positive or negative direction.
        # If the turn count is in the count range of 0-2047, the angle is considered to be positive. If we are in the range of 2048-4095, the angle is considered to be negative
        # This ends up halving the number of turns we can track, but this is find, since we will still be able to track 28 turns in the positive direction or 28 turns in the negative direction

        # Furthermore, to ensure that the negative angle calculations are performed correctly, we offset the revolution count by 1 when it is negative. This ensures that the negative angles do
        # not start at -360, as opposed to 0
        # We also need to make sure that if we are moving in the negative direction that we count the steps down as the steps in the negative direction will start from 8191 and count downwards,
        # thus we offset the step count by 8192 when the revolutions are negative
        revolution = (revolution - 2048) if (revolution > 2047) else revolution
        revolution = (revolution + 1)  if (revolution < 0) else revolution
        step = (step - 8192) if (revolution < 0) else step

        return -(step * self.DEGREES_PER_STEP + (revolution * 360))/self.GEARBOX_REDUCTION


#------------------------------------------------------------------------------
# Shaft Encoder Model
#------------------------------------------------------------------------------
class ShaftEncoderModel:
    def __init__(self, connection: ConnectionInterface, settingsManager: ConfigurationManager):
        self._settingsManager = settingsManager
    
        self._serialAddress = '02'
        self._positionUpdateCommand = bytes.fromhex(f"0180{self._serialAddress}8004")
        self._responseValidityCheckMask = int.from_bytes(bytes.fromhex(f"01{self._serialAddress}000000000004"), byteorder=self._settingsManager.byteOrder)

        self._connection = connection
        self.position = Position()

        self._positionUpdateJob = None


#------------------------------------------------------------------------------
# Start and Stop Methods
#------------------------------------------------------------------------------
    def start(self):
        if not self._connection.isConnected():
            logging.info("Connecting to the Shaft Encoder")
            if self._connection.connect():
                logging.info("Successfully connected to the Shaft Encoder")
            else:
                logging.error("Unable to connect to the Shaft Encoder")
                return

        if self._connection.isConnected() and (self._positionUpdateJob is None):
            logging.info("Starting the Shaft Encoder Position Update Thread")
            self._positionUpdateJob = TimedJobThread(self._settingsManager.positionSamplePeriod, self._updateCurrentPosition)
            self._positionUpdateJob.start()


    def stop(self):
        if self._connection.isConnected():
            if self._positionUpdateJob is not None:
                logging.info("Stopping ShaftEncoder Position Update Thread")
                self._positionUpdateJob.stop()
                self._positionUpdateJob = None

            logging.info("Disconnecting from the Shaft Encoder")
            self._connection.disconnect()


#------------------------------------------------------------------------------
# Getter and Setter functions
#------------------------------------------------------------------------------
    @property
    def currentPosition(self) -> float:
        return self.position.angle


    @property
    def samplePeriod(self) -> float:
        return self._settingsManager.positionSamplePeriod


    @samplePeriod.setter
    def samplePeriod(self, newUpdatePeriod: float):
        self._settingsManager.positionSamplePeriod = max(self._settingsManager.minimumPositionSamplePeriod, newUpdatePeriod)


    def isConnected(self) -> bool:
        return self._connection.isConnected()


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
    def _sendCommandAndGetResponse(self, command: bytes) -> int:
        if not self._connection.isConnected():
            logging.error(f"Unable to send command to the Shaft Encoder in {self._connection}, because the application is not connected")
            return None

        try:
            response = self._connection.getResponse() if self._connection.sendCommand(command) else None
        except TimeoutError as timeoutError:
            logging.exception("There was no response from the Shaft Encoder. Aborting attempt to communicate and disconnecting", exc_info=timeoutError)
            self.stop()
            return None

        return None if (response is None) else int.from_bytes(response, byteorder=self._settingsManager.byteOrder)


    def _checkReceivedDataValidity(self, data: int) -> bool:
        """
        The function performs a check on the data received from the Shaft Encoder, as outlined in the documentation of the Baumer GXM7W-RS485
        The documentation outlines the following packet structure for a received response:
        [SOH][EAD][MT_H][MT_L][ST_H][ST_L][LRC][EOT]
        Each set of square brackets represents an 8-bit byte.
        To perform the validity check, we need to extract the LRC byte, which represents the error check byte. This is done by shifting masking the LRC bits and shifting the masked bits 
        8 bits to the right
        After that, we need to extract the remaining [EAD][MT_H][MT_L][ST_H][ST_L] bytes by shifting the bytes the necessary number of bits to the right and then masking it.
        All the bytes are then XORed together to obtain a single byte value which is then compared to the LRC byte extracted earlier. If the two values match, the data received is valid.
        """
        responseLRC = (data & MASKS.ERROR_CHECK) >> 8
        calculatedLRC = ((data >> 16) & 0xFF) ^ ((data >> 24) & 0xFF) ^ ((data >> 32) & 0xFF) ^ ((data >> 40) & 0xFF) ^ ((data >> 48) & 0xFF)
        return (responseLRC == calculatedLRC) and ((data & self._responseValidityCheckMask) == self._responseValidityCheckMask)


    def _updateCurrentPosition(self):
        response = self._sendCommandAndGetResponse(self._positionUpdateCommand)

        if (response is None):
            logging.error(f"A bad response was received from the Shaft Encoder on {self._connection}")
            return

        if not self._checkReceivedDataValidity(response):
            logging.error("An error in the received data from the Shaft Encoder was detected")
            return

        revolution = ((response & MASKS.REVOLUTIONS) >> 32) & 0xFFFF
        step = ((response & MASKS.STEPS) >> 16) & 0xFFFF

        self.position.revolution = revolution
        self.position.step = step

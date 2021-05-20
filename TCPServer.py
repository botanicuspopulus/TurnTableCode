import logging
import time
import re

from threading import Thread
from socketserver import BaseRequestHandler, ThreadingTCPServer
from typing import NamedTuple, Callable

from ConfigurationManager import ConfigurationManager


class TCPCallbacks(NamedTuple):
    getAzimuth: Callable
    getElevation: Callable
    setAzimuth: Callable
    setElevation: Callable
    stop: Callable


class Commands(NamedTuple):
    getPosition=re.compile("GET_(AZIMUTH|ELEVATION)")
    setPosition=re.compile("SET_(AZIMUTH|ELEVATION) (\d{1,3}(\.\d{3})?)")
    stop=re.compile("STOP")
    halt=re.compile("HALT")
    

class Matches(NamedTuple):
     HALT: re.Match
     STOP: re.Match
     GETPOSITION: re.Match
     SETPOSITION: re.Match


def commandHandlerFactory(callbacks: TCPCallbacks, settingsManager: ConfigurationManager) -> Callable:
	def createCommandHandler(*args, **kwargs):
		return CommandHandler(callbacks, settingsManager, *args, **kwargs)
	return createCommandHandler


class TCPServer(ThreadingTCPServer):
    def __init__(self, settingsManager: ConfigurationManager, callbacks: TCPCallbacks):
        self._callbacks = callbacks
        self._settingsManager = settingsManager
        
        ipAddress = self._settingsManager.tcpServerIPAddress
        port = self._settingsManager.tcpServerPort
        super().__init__((ipAddress, port), commandHandlerFactory(self._callbacks, settingsManager=settingsManager))
        self._thread = None
        self._connected = False


    def connect(self):
        if not self._connected:
            self._thread = Thread(target=self.serve_forever)
            self._thread.start()
            self._connected = True


    def disconnect(self):
        if self._connected:
            self.shutdown()
            self.server_close()
            self._thread = None
            self._connected = True


    def isConnected(self):
        return self._connected


class CommandHandler(BaseRequestHandler):
    def __init__(self, callbacks: TCPCallbacks, settingsManager: ConfigurationManager, *args, **kwargs):
        self._callbacks = callbacks
        self._settingsManager = settingsManager
        BaseRequestHandler.__init__(self, *args, **kwargs)


    def handle(self):
        while True:
            receivedCommand = self.request.recv(50).decode('latin1').strip()
        
            if receivedCommand is None:
                continue
        
            logging.debug(f"Received Request: {receivedCommand}")
            
            matches = Matches(
                HALT=re.match(Commands.halt, receivedCommand),
                STOP=re.match(Commands.stop, receivedCommand),
                GETPOSITION=re.match(Commands.getPosition, receivedCommand),
                SETPOSITION=re.match(Commands.setPosition, receivedCommand),
            )
            
            if matches.HALT:
                self._callbacks.stop()
                self.server.shutdown()
                break
            
            if matches.STOP:
                self._callbacks.stop()
                continue
            
            if matches.GETPOSITION:
                planeName = matches.GETPOSITION.groups(1)
                angle = self._callbacks.getAzimuth() if (planeName == "AZIMUTH") else self._callbacks.getElevation()
                self.sendResponse(f"CURRENT_{planeName} {angle:.3f}")
                continue
            
            if matches.SETPOSITION:
                planeName = matches.SETPOSITION.groups(1)
            
                try:
                    logging.debug(f"{matches.SETPOSITION.group(2)}")
                    value = float(matches.SETPOSITION.group(2))
                    
                except ValueError as valueError:
                    logging.exception(f"Unable to parse value received from {self.client_address}", exc_info=valueError)
                    value = self._callbacks.getAzimuth() if (planeName == "AZIMUTH") else self._callbacks.getElevation()
                
                def SetPosition(positionQueryCallback):
                    while abs(positionQueryCallback() - value) > self._settingsManager.maximumAllowedError:
                        time.sleep(self._settingsManager.pollDelay)
                    
                    response = f"AZIMUTH_FOUND {positionQueryCallback():.3f}"
                    logging.debug("Triggered")
                    self.sendResponse(response)
                
                if planeName == "AZIMUTH":
                    self._callbacks.setAzimuth(value)
                    jobThread = Thread(target=SetPosition, args=(self._callbacks.getAzimuth,))
                else:
                    self._callbacks.setElevation(value)
                    jobThread = Thread(target=SetPosition, args=(self._callbacks.getElevation,))
                    
                jobThread.start()
                continue

            self.sendResponse("UNKNOWN_COMMAND")

    def sendResponse(self, response):
        response = '\n' + response + '\r'
        self.request.sendall(response.encode(self._settingsManager.Encoding))
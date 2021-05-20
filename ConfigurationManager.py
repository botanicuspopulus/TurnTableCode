import os
import configparser


class ConfigurationManager:
    def __init__(self, configFilePath: str):
        self.configFilePath = configFilePath
        self.userConfig = configparser.ConfigParser()
        self.readConfigFile()

    @property
    def maximumGotoPosition(self) -> float:
        return self.userConfig['TurnTableController'].getfloat('MAXIMUM_GOTO_POSITION', 720.000)

    @maximumGotoPosition.setter
    def maximumGotoPosition(self, value: float):
        self.userConfig['TurnTableController']['MAXIMUM_GOTO_POSITION'] = str(value)

    @property
    def minimumGotoPosition(self) -> float:
        return self.userConfig['TurnTableController'].getfloat('MINIMUM_GOTO_POSITION', -720.000)

    @minimumGotoPosition.setter
    def minimumGotoPosition(self, value: float):
        self.userConfig['TurnTableController']['MINIMUM_GOTO_POSITION'] = str(value)

    @property
    def minimumPositionSamplePeriod(self) -> float:
        return self.userConfig['ShaftEncoder'].getfloat('MINIMUM_SAMPLE_PERIOD', 0.05)

    @minimumPositionSamplePeriod.setter
    def minimumPositionSamplePeriod(self, value: float):
        self.userConfig['ShaftEncoder']['MINIMIMUM_SAMPLE_PERIOD'] = str(value)

    @property
    def voltageSamplePeriod(self) -> float:
        return self.userConfig['MotorController'].getfloat('VOLTAGE_SAMPLE_PERIOD', 0.05)

    @property
    def Encoding(self) -> str:
        return self.userConfig['GENERAL'].get('ENCODING')

    @Encoding.setter
    def Encoding(self, value: str):
        self.userConfig['GENERAL']['ENCODING'] = value

    @property
    def timeout(self) -> float:
        return self.userConfig['TurnTableController'].getfloat('TIMEOUT', 1.000)

    @timeout.setter
    def timeout(self, value: float):
        self.userConfig['TurnTableController']['TIMEOUT'] = str(value)

    @property
    def maximumVoltage(self) -> float:
        return self.userConfig['MotorController'].getfloat('MAXIMUM_VOLTAGE', 5.000)

    @maximumVoltage.setter
    def maximumVoltage(self, value: float):
        self.userConfig['MotorController']['MAXIMUM_VOLTAGE'] = str(value)

    @property
    def minimumVoltage(self) -> float:
        return self.userConfig['MotorController'].getfloat('MINIMUM_VOLTAGE', -5.000)

    @minimumVoltage.setter
    def minimumVoltage(self, value: float):
        self.userConfig['MotorController']['MINIMUM_VOLTAGE'] = str(value)

    @property
    def maximumVoltageStep(self) -> float:
        return self.userConfig['MotorController'].getfloat('MAXIMUM_VOLTAGE_STEP', 5.000)

    @maximumVoltageStep.setter
    def maximumVoltageStep(self, value: float):
        self.userConfig['MotorController']['MAXIMUM_VOLTAGE_STEP'] = str(value)

    @property
    def minimumVoltageStep(self) -> float:
        return self.userConfig['MotorController'].getfloat('MIMIMUM_VOLTAGE_STEP', 0.3)

    @minimumVoltageStep.setter
    def minimumVoltageStep(self, value: float):
        self.userConfig['MotorController']['MINIMUM_VOLTAGE_STEP'] = str(value)

    @property
    def minimumVoltageUpdatePeriod(self) -> float:
        return self.userConfig['MotorController'].getfloat('MINIMUM_VOLTAGE_UPDATE_PERIOD', 0.03)

    @minimumVoltageUpdatePeriod.setter
    def minimumVoltageUpdatePeriod(self, value: float):
        self.userConfig['MotorController']['MINIMUM_VOLTAGE_UPDATE_PERIOD'] = str(value)

    @property
    def minimumVoltageSamplePeriod(self) -> float:
        return self.userConfig['MotorController'].getfloat('MINIMUM_VOLTAGE_SAMPLE_PERIOD', 0.03)

    @minimumVoltageSamplePeriod.setter
    def minimumVoltageSamplePeriod(self, value: float):
        self.userConfig['MotorController']['MINIMUM_VOLTAGE_SAMPLE_PERIOD'] = str(value)

    @voltageSamplePeriod.setter
    def voltageSamplePeriod(self, value: float):
        self.userConfig['MotorController']['VOLTAGE_SAMPLE_PERIOD'] = str(value)

    @property
    def voltageUpdatePeriod(self) -> float:
        return self.userConfig['MotorController'].getfloat('VOLTAGE_UPDATE_PERIOD', 0.05)

    @voltageUpdatePeriod.setter
    def voltageUpdatePeriod(self, value: float):
        self.userConfig['MotorController']['VOLTAGE_UPDATE_PERIOD'] = str(value)

    @property
    def voltageStep(self) -> float:
        return self.userConfig['MotorController'].getfloat('VOLTAGE_STEP', 0.3)

    @voltageStep.setter
    def voltageStep(self, value: float):
        self.userConfig['MotorController']['VOLTAGE_STEP'] = str(value)

    @property
    def positionSamplePeriod(self) -> float:
        return self.userConfig['ShaftEncoder'].getfloat('POSITION_SAMPLE_PERIOD', 0.05)

    @positionSamplePeriod.setter
    def positionSamplePeriod(self, value: float):
        self.userConfig['ShaftEncoder']['POSITION_SAMPLE_PERIOD'] = str(value)

    @property
    def turnTableIPAddress(self) -> str:
        return self.userConfig['TurnTableController'].get('TURNTABLE_IP_ADDRESS', '127.0.0.1')

    @turnTableIPAddress.setter
    def turnTableIPAddress(self, value: str):
        self.userConfig['TurnTableController']['TURNTABLE_IP_ADDRESS'] = value

    @property
    def tcpServerIPAddress(self) -> str:
        return self.userConfig['TCPServer'].get('IP_ADDRESS', '127.0.0.1')

    @tcpServerIPAddress.setter
    def tcpServerIPAddress(self, value:str):
        self.userConfig['TCPServer']['IP_ADDRESS'] = value

    @property
    def shaftEncoderPort(self) -> int:
        return self.userConfig['ShaftEncoder'].getint('PORT', 10003)

    @shaftEncoderPort.setter
    def shaftEncoderPort(self, port: int):
        self.userConfig['ShaftEncoder']['PORT'] = str(port)

    @property
    def motorControllerPort(self) -> int:
        return self.userConfig['MotorController'].getint('PORT', 10002)

    @motorControllerPort.setter
    def motorControllerPort(self, port: int):
        self.userConfig['MotorController']['PORT'] = str(port)

    @property
    def watchdogPort(self):
        return self.userConfig['Watchdog'].getint('PORT', 10000)

    @watchdogPort.setter
    def watchdogPort(self, port: int):
        self.userConfig['Watchdog']['PORT'] = str(port)

    @property
    def tcpServerPort(self):
        return self.userConfig['TCPServer'].getint('PORT', 10180) 

    @tcpServerPort.setter
    def tcpServerPort(self, port: int):
        self.userConfig['TCPServer']['PORT'] = str(port)

    @property
    def controlProportionalGain(self) -> float:
        return self.userConfig['TurnTableController'].getfloat('CONTROL_PROPORTIONAL_GAIN', 1.000)

    @controlProportionalGain.setter
    def controlProportionalGain(self, value: float):
        self.userConfig['TurnTableController']['CONTROL_PROPORTIONAL_GAIN'] = str(value)

    @property
    def controlIntegralGain(self) -> float:
        return self.userConfig['TurnTableController'].getfloat('CONTROL_INTEGRAL_GAIN', 0.100)

    @controlIntegralGain.setter
    def controlIntegralGain(self, value: float):
        self.userConfig['TurnTableController']['CONTROL_INTEGRAL_GAIN'] = str(value)

    @property
    def controlDerivativeGain(self):
        return self.userConfig['TurnTableController'].getfloat('CONTROL_DERIVATIVE_GAIN', 0.100)

    @controlDerivativeGain.setter
    def controlDerivativeGain(self, value: float):
        self.userConfig['TurnTableController']['CONTROL_DERIVATIVE_GAIN'] = str(value)

    @property
    def maximumAllowedError(self) -> float:
        return self.userConfig['TurnTableController'].getfloat('MAXIMUM_ALLOWED_ERROR', 0.025)

    @maximumAllowedError.setter
    def maximumAllowedError(self, value: float):
        self.userConfig['TurnTableController']['MAXIMUM_ALLOWED_ERROR'] = str(value)

    @property
    def minimumControlSignalValue(self) -> float:
        return self.userConfig['TurnTableController'].getfloat('MINIMUM_CONTROL_SIGNAL_VALUE', 0.3)

    @minimumControlSignalValue.setter
    def minimumControlSignalValue(self, value: float):
        self.userConfig['TurnTableController']['MINIMUM_CONTROL_SIGNAL_VALUE'] = str(value)

    @property
    def GUIUpdatePeriod(self) -> float:
        return self.userConfig['GUI'].getfloat('UPDATE_PERIOD', 0.1)

    @GUIUpdatePeriod.setter
    def GUIUpdatePeriod(self, value: float):
        self.userConfig['GUI']['UPDATE_PERIOD'] = str(value)

    @property
    def pollDelay(self) -> float:
        return self.userConfig['TCPServer'].getfloat('POLL_DELAY')

    @pollDelay.setter
    def pollDelay(self, value: float):
        self.userConfig['TCPServer']['POLL_DELAY'] = str(value)
        
    @property
    def byteOrder(self) -> str:
        return self.userConfig['GENERAL']['BYTE_ORDER']

    @byteOrder.setter
    def byteOrder(self, value: str):
        self.userConfig['GENERAL']['BYTE_ORDER'] = value

    @property
    def minimumStepSize(self) -> float:
        return self.userConfig['TurnTableController'].getfloat('MINIMUM_STEP_SIZE', 0.05)

    @minimumStepSize.setter
    def minimumStepSize(self, value: float):
        self.userConfig['TurnTableController']['MINIMUM_STEP_SIZE'] = str(value)

    @property
    def maximumStepSize(self) -> float:
        return self.userConfig['TurnTableController'].getfloat('MAXIMUM_STEP_SIZE', 360.000)

    @maximumStepSize.setter
    def maximumStepSize(self, value: float):
        self.userConfig['TurnTableController']['MAXIMUM_STEP_SIZE'] = str(value)

    @property
    def watchdogTriggerPeriod(self) -> float:
        return self.userConfig['Watchdog'].getfloat('TRIGGER_PERIOD', 0.5)

    @watchdogTriggerPeriod.setter
    def watchdogTriggerPeriod(self, value: float):
        self.userConfig['Watchdog']['TRIGGER_PERIOD'] = str(value)

    @property
    def minimumWatchdogTriggerPeriod(self) -> float:
        return self.userConfig['Watchdog'].getfloat("MINIMUM_TRIGGER_PERIOD", 0.05)

    @minimumWatchdogTriggerPeriod.setter
    def minimumWatchdogTriggerPeriod(self, value: float):
        self.userConfig['Watchdog']['MINIMUM_RIGGER_PERIOD'] = str(value)

    def createDefaultConfigFile(self):
        self.userConfig['MotorController'] = {
            'PORT': '10002',
            'MAXIMUM_VOLTAGE': '7.000',
            'MINIMUM_VOLTAGE': '-7.000',
            'MAXIMUM_VOLTAGE_STEP': '7.000',
            'MINIMUM_VOLTAGE_STEP': '1.200',
            'MINIMUM_VOLTAGE_SAMPLE_PERIOD': '0.03',
            'MINIMUM_VOLTAGE_UPDATE_PERIOD': '0.03',
            'VOLTAGE_STEP': '0.1',
            'VOLTAGE_SAMPLE_PERIOD': '0.05',
            'VOLTAGE_UPDATE_PERIOD': '0.05',
        }

        self.userConfig['ShaftEncoder'] = {
            'PORT': '10003',
            'POSITION_SAMPLE_PERIOD': '0.05',
            'MINIMUM_SAMPLE_PERIOD': '0.03',
        }

        self.userConfig['Watchdog'] = {
            'PORT': '10000',
            'MINIMUM_TRIGGER_PERIOD': '0.05',
            'TRIGGER_PERIOD': '0.5',
        }

        self.userConfig['TurnTableController'] = {
            'TURNTABLE_IP_ADDRESS': '192.168.22.22',
            'TIMEOUT': '1',
            'CONTROL_PROPORTIONAL_GAIN': '1.000',
            'CONTROL_INTEGRAL_GAIN': '0.100',
            'CONTROL_DERIVATIVE_GAIN': '0.100',
            'MAXIMUM_ALLOWED_ERROR': '0.025',
            'MINIMUM_CONTROL_SIGNAL_VALUE': '1.2',
            'MINIMUM_GOTO_POSITION': '-720.000',
            'MAXIMUM_GOTO_POSITION': '720.000',
            'MINIMUM_STEP_SIZE': '0.05',
            'MAXIMUM_STEP_SIZE': '360.000',
        }

        self.userConfig['TCPServer'] = {
            'PORT': '10180',
            'IP_ADDRESS': 'localhost',
            'POSITION_ERROR': '0.05',
            'POLL_DELAY': '0.5',
        }

        self.userConfig['GUI'] = {
            'UPDATE_PERIOD': '0.1',
        }

        self.userConfig['GENERAL'] = {
            'Encoding': 'utf-8',
            'BYTE_ORDER': 'big'
        }

        self.writeConfigFile()


    def writeConfigFile(self):
        with open(self.configFilePath, 'w') as configFile:
            self.userConfig.write(configFile)

    def readConfigFile(self):
        if not os.path.exists(self.configFilePath):
            self.createDefaultConfigFile()
        else:
            self.userConfig.read(self.configFilePath)
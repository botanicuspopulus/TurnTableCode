import os
import sys
import logging

sys.path.insert(0, os.getcwd())
os.environ["PYTHONPATH"] = os.getcwd()


from PySide2.QtWidgets import QApplication

from TurnTableController import TurnTableController
from ConfigurationManager import ConfigurationManager
from ZeroPointManager import ZeroPointManager

from ZeroPointViews import LoadZeroPointView, SaveZeroPoint

LOG_FILE_PATH = os.getcwd() + "\\Logs"
LOG_FILE_NAME = "logs.txt"

def main(argv):
    if not os.path.exists(LOG_FILE_PATH):
        os.makedirs(LOG_FILE_PATH)
    
    logging.basicConfig(
        level=logging.DEBUG)
    
    settingsManager = ConfigurationManager('./config.ini')
    zeroPointManager = ZeroPointManager('./zero_points.xml')
    application = QApplication()
    turnTableController = TurnTableController(settingsManager=settingsManager, zeroPointManager=zeroPointManager)
    turnTableController.start()


    exitStatusCode = application.exec_()
    logging.debug(f"Exit Status Code: {exitStatusCode}")

    sys.exit(exitStatusCode)


if __name__ == "__main__":
    main(sys.argv[1:])
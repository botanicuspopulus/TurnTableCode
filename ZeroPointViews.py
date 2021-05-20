from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QLabel, QLineEdit, QListWidget, QListWidgetItem
from PySide2.QtWidgets import QDialogButtonBox
from PySide2.QtWidgets import QFormLayout

from ZeroPointManager import ZeroPointManager


def SaveZeroPoint(offset: float, zeroPointManager: ZeroPointManager):
    dialog = QDialog()
    dialog.setWindowTitle("Save Zero Position")
    
    zeroPositionNameLineEdit = QLineEdit("Default Name: ")
    zeroPositionOffsetLineEdit = QLineEdit(str(offset))
    zeroPositionOffsetLineEdit.setEnabled(False)

    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

    def createNewZeroPoint():
        zeroPointManager.createZeroPoint(zeroPositionNameLineEdit.text(), float(zeroPositionOffsetLineEdit.text()))
        dialog.close()

    buttonBox.accepted.connect(createNewZeroPoint)
    buttonBox.rejected.connect(dialog.reject)
    
    layout = QFormLayout()
    layout.addRow(QLabel("Name: "), zeroPositionNameLineEdit)
    layout.addRow(QLabel("Offset: "), zeroPositionOffsetLineEdit)
    layout.addRow(buttonBox)

    dialog.setLayout(layout)
    return dialog


class LoadZeroPointView(QDialog):
    def __init__(self, zeroPointManager: ZeroPointManager):
        super().__init__()
        self.setWindowTitle("Load Zero Point")

        self._zeroPointManager = zeroPointManager
        self._listWidget = QListWidget()

        for zeroPoint in self._zeroPointManager.getZeroPoints():
            listItem = QListWidgetItem(f"{zeroPoint.name} : {zeroPoint.offset}")
            self._listWidget.addItem(listItem)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.setZeroPoint)
        buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        layout.addRow(self._listWidget)
        layout.addRow(buttonBox)

        self.setLayout(layout)


    def setZeroPoint(self):
        index = self._listWidget.indexFromItem(self._listWidget.selectedItems()[0]).row()
        self._zeroPointManager.setNewActiveZeroPoint(index)
        self.close()
from dataclasses import dataclass
from xml.etree import ElementTree as ET


@dataclass
class ZeroPoint:
    number: int
    name: str
    offset: float


class ZeroPointManager:
    def __init__(self, zeroPointFilePath):
        self._zeroPointFilePath = zeroPointFilePath
        self.readZeroPoints()
        self.setNewActiveZeroPoint(0)


    def setNewActiveZeroPoint(self, index: int):
        zeroPoint = self._zeroPoints.findall('ZeroPoint')[index]
        self._activeZeroPoint = ZeroPoint(int(zeroPoint[0].text), zeroPoint[1].text, float(zeroPoint[2].text))


    def readZeroPoints(self):
        self._zeroPoints = ET.parse(self._zeroPointFilePath)


    def getOffset(self) -> float:
        return self._activeZeroPoint.offset


    def createZeroPoint(self, name: str, offset: float):
        zeroPoints = self._zeroPoints.getroot()
        zeroPointCount = len(zeroPoints.findall('ZeroPoint')) + 1
        zeroPoint = ET.SubElement(zeroPoints, 'ZeroPoint')
        zeroPointNumber = ET.SubElement(zeroPoint, 'Number')
        zeroPointNumber.text = str(zeroPointCount)
        zeroPointName = ET.SubElement(zeroPoint, 'Name')
        zeroPointName.text = name
        zeroPointOffset = ET.SubElement(zeroPoint, 'Offset')
        zeroPointOffset.text = str(offset)

        with open(self._zeroPointFilePath, 'wb') as xmlFile:
            xmlFile.write(ET.tostring(self._zeroPoints.getroot()))


    def getZeroPoints(self):
        return [ZeroPoint(int( zeroPoint[0].text ), zeroPoint[1].text, float( zeroPoint[2].text )) for zeroPoint in self._zeroPoints.findall('ZeroPoint')]
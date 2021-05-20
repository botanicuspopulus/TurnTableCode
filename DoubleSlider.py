from PySide2.QtWidgets import QSlider
from PySide2.QtCore import Signal

class DoubleSlider(QSlider):
    doubleValueChanged = Signal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.decimals = 4
        self._max_int = 10**self.decimals

        super().setMinimum(0)
        super().setMaximum(self._max_int)

        self._min_value = 0.0
        self._max_value = 1.0

        super().valueChanged.connect(lambda: self.doubleValueChanged.emit(self.value()))


    @property
    def _value_range(self) -> float:
        return self._max_value - self._min_value


    def value(self) -> float:
        return float(super().value() / self._max_int * self._value_range + self._min_value)


    def setValue(self, value: float):
        super().setValue(int((value - self._min_value) / self._value_range * self._max_int))


    def setMinimum(self, value: float):
        if value > self._max_value:
            raise ValueError("Minimum limit cannot be higher than the maximum")

        self._min_value = value
        self.setValue(self.value())


    def setMaximum(self, value: float):
        if value < self._min_value:
            raise ValueError("Maximum limit cannot be less than the minimum")

        self._max_value = value
        self.setValue(self.value())

    def setRange(self, minimum: float, maximum: float):
        self.setMinimum(minimum)
        self.setMaximum(maximum)


    def minimum(self) -> float:
        return self._min_value


    def maximum(self) -> float:
        return self._max_value
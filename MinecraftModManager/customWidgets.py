import PyQt5.QtWidgets as Qt


class SeparationLine(Qt.QFrame):
    def __init__(self):
        """a horizontal separation line"""
        super().__init__()
        self.setFrameShape(Qt.QFrame.HLine)
        self.setFrameShadow(Qt.QFrame.Sunken)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.setFixedHeight(10)

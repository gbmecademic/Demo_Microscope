from PyQt5.QtWidgets import QPushButton


class AutoButton(QPushButton):
    def __init__(self, args, *kwargs):
        super().__init__(args, *kwargs)
        self.setCheckable(True)
        self.setStyleSheet("background-color : lightgray")
        self.setText("AutoMode")

        self.clicked.connect(self.on_toggle)
    
    def on_toggle(self):
        if self.isChecked():
            self.setStyleSheet("background-color : green")
        else:
            self.setStyleSheet("background-color : lightgray")
    
    def on_disable(self):
        pass

    def on_enable(self):
        pass

class CustomToggle(QPushButton):
    def __init__(self, args, *kwargs):
        super().__init__(args, *kwargs)
        self.setCheckable(True)
        self.setStyleSheet("background-color : lightgray")

    def on_toggle(self):
        if self.isChecked:
            pass
        else:
            pass
    
    def on_disable(self):
        pass

    def on_enable(self):
        pass
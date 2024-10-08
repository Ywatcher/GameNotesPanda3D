from PyQt5.QtWidgets import QWidget, QApplication
class QObserved:
    def __init__(self):
        if not hasattr(self, "isQObservedInit"):
            self.aObservers = []
            self.isQObservedInit = True

    def register_qobs(self, obsvr):
        self.aObservers.append(obsvr)

    def rm_qobs(self, obsvr):
        pass

    def send_qevent(self, evt):
        for obsvr in self.aObservers:
            QApplication.sendEvent(obsvr, evt)
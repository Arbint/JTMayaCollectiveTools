import maya.OpenMayaUI as omui
import maya.cmds as mc
if int(mc.about(v=True)) <= 2024:
    from shiboken2 import wrapInstance
    from PySide2.QtWidgets import QMainWindow, QWidget
    from PySide2.QtCore import Qt
else:
    from shiboken6 import wrapInstance
    from PySide6.QtWidgets import QMainWindow, QWidget
    from PySide6.QtCore import Qt

def GetMayaMainWindow():
    mayaMainUI = omui.MQtUtil.mainWindow() 
    return wrapInstance(int(mayaMainUI), QMainWindow)

def RemoveWidgetWithName(name):
    mayaMainWindow: QMainWindow = GetMayaMainWindow()
    for existing in mayaMainWindow.findChildren(QWidget, name):
        existing.deleteLater()
    
class QMayaWidget(QWidget):
    def __init__(self):
        RemoveWidgetWithName(self.GetWidgetHash())
        super().__init__(parent=GetMayaMainWindow())
        
        self.setObjectName(self.GetWidgetHash())
        self.setWindowFlags(Qt.WindowType.Window)


    def GetWidgetHash(self):
        return "1231341231231314342131123413123123123125"
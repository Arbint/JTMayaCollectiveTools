import maya.cmds as mc
import maya.mel as mel

from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QListWidget, QFormLayout, QLineEdit
from MayaUtilities import QMayaWidget

class MultiParent:
    def __init__(self):
        self.currentPropCtrl = 'ac_axe_global'
        self.leftHandIKCtrl = ''
        self.rightHandIKCtrl = 'ikArm_R'


    def MakePinnerController(self, name, size):
        mel.eval(f"curve -d 1 -n {name} -p -0.5 0.5 0.5 -p -0.5 -0.0130096 0.5 -p -0.5 -0.0130096 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.0130096 0.5 -p -0.5 -0.0130096 0.5 -p -0.5 -0.0130096 -0.5 -p 0.5 -0.0130096 -0.5 -p 0.5 -0.0130096 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.0130096 -0.5 -p 0 -0.502633 0 -p -0.5 -0.0130096 0.5 -p 0.5 -0.0130096 0.5 -p 0 -0.502633 0 -p -0.5 -0.0130096 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 ;")
        mc.scale(size, size, size, name)
        mc.makeIdentity(name, apply=True)
        offsetGrpName = name + "_offset_grp"
        mc.group(name, n=offsetGrpName) 
        grpName = name + "_grp"
        mc.group(offsetGrpName, n=grpName)

        return name, grpName, offsetGrpName

    def AssignSelectionAsCurrentPropCtrl(self):
        self.currentPropCtrl = mc.ls(sl=True)[0]
        return self.currentPropCtrl

    def AssignSelectionAsRightHandIkCtrl(self):
        self.rightHandIKCtrl = mc.ls(sl=True)[0]
        return self.rightHandIKCtrl

class MultiParentWidget(QMayaWidget):
    def __init__(self):
        super().__init__()

        self.multiParent = MultiParent()

        self.setWindowTitle("Multi Parent")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.CreateSelectionSection()


    def CreateSelectionSection(self):
        sectionLayout = QGridLayout()
        self.masterLayout.addLayout(sectionLayout)
        
        propCurrentCtrlLabel = QLabel("current prop controller:")
        self.propCurrentCtrlLineEdit = QLineEdit()
        self.propCurrentCtrlLineEdit.setEnabled(False)
        self.propCurrentCtrlLineEdit.setText(self.multiParent.currentPropCtrl)
        assignPropCurrentCtrlBtn = QPushButton("Pick Current Ctrl") 
        assignPropCurrentCtrlBtn.clicked.connect(
            lambda : self.propCurrentCtrlLineEdit.setText(self.multiParent.AssignSelectionAsCurrentPropCtrl())
            )
    
        sectionLayout.addWidget(propCurrentCtrlLabel, 0, 0)
        sectionLayout.addWidget(self.propCurrentCtrlLineEdit, 0, 1)
        sectionLayout.addWidget(assignPropCurrentCtrlBtn, 0, 2)

        rightHandCtrlLabel = QLabel("right hand ik controller:")
        self.rightHandIKCtrlLineEdit = QLineEdit()
        self.rightHandIKCtrlLineEdit.setEnabled(False)
        self.rightHandIKCtrlLineEdit.setText(self.multiParent.rightHandIKCtrl)
        assignRightHandIKCtrlBtn = QPushButton("Pick Right Hand ik Ctrl") 
        assignRightHandIKCtrlBtn.clicked.connect(
            lambda : self.rightHandIKCtrlLineEdit.setText(self.multiParent.AssignSelectionAsRightHandIkCtrl())
            )
    
        sectionLayout.addWidget(rightHandCtrlLabel, 1, 0)
        sectionLayout.addWidget(self.rightHandIKCtrlLineEdit, 1, 1)
        sectionLayout.addWidget(assignRightHandIKCtrlBtn, 1, 2)




MultiParentWidget().show()

        


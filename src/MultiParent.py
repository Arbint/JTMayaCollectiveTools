import maya.cmds as mc
import maya.mel as mel

from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QListWidget, QFormLayout, QLineEdit
from PySide2.QtCore import Signal
from MayaUtilities import QMayaWidget


class MultiParent:
    def __init__(self):
        self.currentPropCtrl = 'ac_axe_global'
        self.leftHandIKCtrl = ''
        self.rightHandIKCtrl = 'ikArm_R'
        self.leftHandJnt = ''
        self.rightHandJnt = ''


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

    def AssignSelectionAsleftHandIkCtrl(self):
        self.leftHandIKCtrl = mc.ls(sl=True)[0]
        return self.leftHandIKCtrl

    def AssignSelectionAsRightHandJnt(self):
        self.rightHandJnt = mc.ls(sl=True)[0]
        return self.rightHandJnt

    def AssignSelectionAsLeftHandJnt(self):
        self.leftHandJnt = mc.ls(sl=True)[0]
        return self.leftHandJnt

class InfoAssignWidget(QWidget):
    def __init__(self, infoName, startVal, InfoPickedCallback):
        super().__init__()
        masterLayout = QGridLayout()
        self.setLayout(masterLayout)

        label = QLabel(f"{infoName}:")
        self.propCurrentCtrlLineEdit = QLineEdit()
        self.propCurrentCtrlLineEdit.setEnabled(False)
        self.propCurrentCtrlLineEdit.setText(startVal)
        assignPropCurrentCtrlBtn = QPushButton(f"Pick {infoName}") 
        assignPropCurrentCtrlBtn.clicked.connect(
            lambda : self.propCurrentCtrlLineEdit.setText(self.multiParent.AssignSelectionAsCurrentPropCtrl())
            )
    
        masterLayout.addWidget(propCurrentCtrlLabel, 0, 0)
        masterLayout.addWidget(self.propCurrentCtrlLineEdit, 0, 1)
        masterLayout.addWidget(assignPropCurrentCtrlBtn, 0, 2)
        



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

        leftHandCtrlLabel = QLabel("left hand ik controller:")
        self.leftHandIKCtrlLineEdit = QLineEdit()
        self.leftHandIKCtrlLineEdit.setEnabled(False)
        self.leftHandIKCtrlLineEdit.setText(self.multiParent.leftHandIKCtrl)
        assignleftHandIKCtrlBtn = QPushButton("Pick left Hand ik Ctrl") 
        assignleftHandIKCtrlBtn.clicked.connect(
            lambda : self.leftHandIKCtrlLineEdit.setText(self.multiParent.AssignSelectionAsleftHandIkCtrl())
            )
    
        sectionLayout.addWidget(leftHandCtrlLabel, 2, 0)
        sectionLayout.addWidget(self.leftHandIKCtrlLineEdit, 2, 1)
        sectionLayout.addWidget(assignleftHandIKCtrlBtn, 2, 2)


        rightHandJntLabel = QLabel("right hand ik controller:")
        self.rightHandJntLineEdit = QLineEdit()
        self.rightHandJntLineEdit.setEnabled(False)
        self.rightHandJntLineEdit.setText(self.multiParent.rightHandJnt)
        assignRightHandJntBtn = QPushButton("Pick Right Hand ik Ctrl") 
        assignRightHandJntBtn.clicked.connect(
            lambda : self.rightHandJntLineEdit.setText(self.multiParent.AssignSelectionAsRightHandJnt())
            )
    
        sectionLayout.addWidget(rightHandJntLabel, 1, 0)
        sectionLayout.addWidget(self.rightHandJntLineEdit, 1, 1)
        sectionLayout.addWidget(assignRightHandJntBtn, 1, 2)

        leftHandJntLabel = QLabel("left hand ik controller:")
        self.leftHandJntLineEdit = QLineEdit()
        self.leftHandJntLineEdit.setEnabled(False)
        self.leftHandJntLineEdit.setText(self.multiParent.leftHandJnt)
        assignleftHandJntBtn = QPushButton("Pick left Hand ik Ctrl") 
        assignleftHandJntBtn.clicked.connect(
            lambda : self.leftHandJntLineEdit.setText(self.multiParent.AssignSelectionAsleftHandJnt())
            )
    
        sectionLayout.addWidget(leftHandJntLabel, 2, 0)
        sectionLayout.addWidget(self.leftHandJntLineEdit, 2, 1)
        sectionLayout.addWidget(assignleftHandJntBtn, 2, 2)


MultiParentWidget().show()

        


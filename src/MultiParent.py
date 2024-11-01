import maya.cmds as mc
import maya.mel as mel

from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QListWidget, QFormLayout, QLineEdit
from PySide2.QtCore import Signal
from MayaUtilities import QMayaWidget


class MultiParent:
    def __init__(self):
        self.currentPropCtrl = 'ac_axe_global'
        self.leftHandIKCtrl = 'IKArm_L'
        self.rightHandIKCtrl = 'IkArm_R'
        self.leftHandJnt = 'Wrist_L'
        self.rightHandJnt = 'Wrist_R'

        self.weaponPinningAttrName = "weaponPinning"
        self.pinnerControllerOptions = ["global", "singleHanded", "rightHandDriven", "weaponDrivesHands"]
        self.rightHandToWeaponWeightAttrName = "rightHandToWeapon"
        self.leftHandToWeaponWeightAttrName = "leftHandToWeapon"

        self.pinnedController = ""

    def BuildMultiparentSystem(self):
        self.pinnedController = self.MakePinnerController("weaponPinner", 10)
        print(f"duplicating: {self.currentPropCtrl}")
        mc.select(self.currentPropCtrl)
        weaponFollowsHandCtrl = self.currentPropCtrl + ""


        

    def MakePinnerController(self, name, size):
        mel.eval(f"curve -d 1 -n {name} -p -0.5 0.5 0.5 -p -0.5 -0.0130096 0.5 -p -0.5 -0.0130096 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.0130096 0.5 -p -0.5 -0.0130096 0.5 -p -0.5 -0.0130096 -0.5 -p 0.5 -0.0130096 -0.5 -p 0.5 -0.0130096 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.0130096 -0.5 -p 0 -0.502633 0 -p -0.5 -0.0130096 0.5 -p 0.5 -0.0130096 0.5 -p 0 -0.502633 0 -p -0.5 -0.0130096 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 ;")
        mc.scale(size, size, size, name)
        mc.makeIdentity(name, apply=True)
        offsetGrpName = name + "_offset_grp"
        mc.group(name, n=offsetGrpName) 
        grpName = name + "_grp"
        mc.group(offsetGrpName, n=grpName)

        mc.addAttr(name, ln=self.weaponPinningAttrName, at="enum", en= ":".join(self.pinnerControllerOptions) + ":", k=True)
        mc.addAttr(name, ln=self.rightHandToWeaponWeightAttrName, at="float", min=0, max=1, k=True)
        mc.addAttr(name, ln=self.leftHandToWeaponWeightAttrName, at="float", min=0, max=1, k=True)
        self.LockAndHideTransform(name)
        self.LockAndHideVisiblity(name)
        return name, grpName, offsetGrpName

    def LockAndHideTransform(self, objName):
        lockAndHideAttrs = [".tx", ".ty", '.tz','.rx', '.ry', '.rz', '.sx', '.sy', '.sz']
        for attr in lockAndHideAttrs:
            mc.setAttr(objName + attr, channelBox=False, keyable=False, lock=True)

    def LockAndHideVisiblity(self, objName):
        mc.setAttr(objName + ".v", channelBox=False, keyable=False, lock=True)

    def AssignSelectionAsCurrentPropCtrl(self):
        self.currentPropCtrl = mc.ls(sl=True)[0]
        return self.currentPropCtrl

    def AssignSelectionAsRightHandIkCtrl(self):
        self.rightHandIKCtrl = mc.ls(sl=True)[0]
        return self.rightHandIKCtrl

    def AssignSelectionAsLeftHandIkCtrl(self):
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
        self.infoLineEdit = QLineEdit()
        self.infoLineEdit.setEnabled(False)
        self.infoLineEdit.setText(startVal)
        assignBtn = QPushButton(f"Pick {infoName}") 
        assignBtn.clicked.connect(
            lambda : self.infoLineEdit.setText(InfoPickedCallback())
            )
    
        masterLayout.addWidget(label, 0, 0)
        masterLayout.addWidget(self.infoLineEdit, 0, 1)
        masterLayout.addWidget(assignBtn, 0, 2)
        
class MultiParentWidget(QMayaWidget):
    def __init__(self):
        super().__init__()

        self.multiParent = MultiParent()

        self.setWindowTitle("Multi Parent")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.CreateInfoGatherSection()
        self.CreateBuildSection()

    def CreateBuildSection(self):
        sectionLayout = QVBoxLayout()
        self.masterLayout.addLayout(sectionLayout)
        
        buildBtn = QPushButton("Build Multi Parent")
        buildBtn.clicked.connect(lambda : self.multiParent.BuildMultiparentSystem())
        sectionLayout.addWidget(buildBtn)

    def CreateInfoGatherSection(self):
        currentProCtrlWidget = InfoAssignWidget("current prop controller", self.multiParent.currentPropCtrl, self.multiParent.AssignSelectionAsCurrentPropCtrl)
        self.masterLayout.addWidget(currentProCtrlWidget)

        rightHandCtrlWidget = InfoAssignWidget("right hand ik controller", self.multiParent.rightHandIKCtrl, self.multiParent.AssignSelectionAsRightHandIkCtrl)
        self.masterLayout.addWidget(rightHandCtrlWidget)

        leftHandCtrlWidget = InfoAssignWidget("left hand ik controller", self.multiParent.leftHandIKCtrl, self.multiParent.AssignSelectionAsLeftHandIkCtrl)
        self.masterLayout.addWidget(leftHandCtrlWidget)

        righHandJntWidget = InfoAssignWidget("right hand jnt", self.multiParent.rightHandJnt, self.multiParent.AssignSelectionAsRightHandJnt)
        self.masterLayout.addWidget(righHandJntWidget)

        leftHandJntWidget = InfoAssignWidget("left hand jnt", self.multiParent.leftHandJnt, self.multiParent.AssignSelectionAsLeftHandJnt)
        self.masterLayout.addWidget(leftHandJntWidget)


MultiParentWidget().show()

        


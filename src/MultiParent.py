import maya.cmds as mc
import maya.mel as mel

from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QListWidget, QFormLayout, QLineEdit, QSlider
from PySide2.QtCore import Signal
from PySide2.QtCore import Qt
from MayaUtilities import QMayaWidget


class MultiParent:
    def __init__(self):
        self.propOrigCtrl = 'ac_axe'
        self.leftHandIKCtrl = 'IKArm_L'
        self.rightHandIKCtrl = 'IKArm_R'
        self.leftHandJnt = 'Wrist_L'
        self.rightHandJnt = 'Wrist_R'
        self.sliderSize = 5
        self.pinnerSize = 1

        self.propPiningAttrName = "pinning"
        self.pinnerControllerOptions = ["global", "singleHanded", "rightHandDriven", "weaponDrivesHands"]
        self.rightHandToWeaponWeightAttrName = "rightHandToWeapon"
        self.leftHandToWeaponWeightAttrName = "leftHandToWeapon"

        self.pinnedController = ""

    def SetPinnerControllerSize(self, newSize):
        self.pinnerSize = newSize

    def SetSliderSize(self, newSize):
        self.sliderSize = newSize

    def SetupControlVarientParentConstraint(self, variantSubfix, variantName, varientFollowGrp):
        constraintSrcs = self.GetControlVariantParentConstraintSources(variantSubfix)
        if not constraintSrcs:
            return

        mc.addAttr(variantName, ln=self.propPiningAttrName, at="enum", en= ":".join(constraintSrcs.keys()) + ":", k=True)
        i = 0
        for optionEnumName, constraintSrc in constraintSrcs.items():
            parentConstraint = mc.parentConstraint(constraintSrc, varientFollowGrp, mo=variantSubfix != "singleHanded")[0]
            mc.expression(s=f"{parentConstraint}.{constraintSrc}W{i}={variantName}.{self.propPiningAttrName}=={i}?1:0;")
            i += 1

    def GetControlVariantParentConstraintSources(self, variantSubfix):
        if variantSubfix == "global" or variantSubfix == "weaponDrivesHands":
            return None

        if variantSubfix == "singleHanded":
            return {"leftHand":self.leftHandJnt, "rightHand":self.rightHandJnt}

        if variantSubfix == "rightHandDriven":
            return {"rightHand":self.rightHandJnt}


    def BuildMultiparentSystem(self):
        self.pinnedController, pinnedControllerGrp, _ = self.MakePinnerController("weaponPinner", 10)

        leftHandFollowGrp,leftHandConstNull = self.CreateHandFollowGrps(self.leftHandIKCtrl)
        rightHandFollowGrp, rightHandConstNull = self.CreateHandFollowGrps(self.rightHandIKCtrl)

        allCtrlGrps = self.propOrigCtrl + "_space_grp"
        mc.group(self.propOrigCtrl, n=allCtrlGrps)

        propOrigionalCtrlFollowGrp = self.propOrigCtrl + "_orig_follow_grp"
        mc.createNode("transform", n = propOrigionalCtrlFollowGrp)
        mc.matchTransform(propOrigionalCtrlFollowGrp, self.propOrigCtrl)

        followParentConstraint = ""
        leftHandFollowPropSlider = ""
        leftHandFollowRightHandSlider = ""
        rightHandSlider = ""
        for i, variantSubfix in enumerate(self.pinnerControllerOptions):
            variantCtrlName, variantCtrlGrpName, variantCtrlOffsetGrpName, variantOutputName = self.MakePropControlVariant(variantSubfix)
            followParentConstraint = mc.parentConstraint(variantOutputName, propOrigionalCtrlFollowGrp)[0]
            mc.expression(s=f"{followParentConstraint}.{variantOutputName}W{i}={self.pinnedController}.{self.propPiningAttrName}=={i}?1:0;")
            mc.expression(s=f"{variantCtrlGrpName}.v={self.pinnedController}.{self.propPiningAttrName}=={i}?1:0;")
            self.SetupControlVarientParentConstraint(variantSubfix, variantCtrlName, variantCtrlOffsetGrpName)

            if variantSubfix == "rightHandDriven" or variantSubfix == "weaponDrivesHands":
                leftSlider, rightSlider = self.MakeHandFollowSliders(variantSubfix, variantCtrlName)
                if rightSlider:
                    rightHandSlider = rightSlider
                    leftHandFollowPropSlider = leftSlider
                else:
                    leftHandFollowRightHandSlider = leftSlider

                
        self.SetupRightHandFollow(rightHandConstNull, rightHandFollowGrp, rightHandSlider) 
        leftHandFollowSliderOutputGrp = self.SetupLeftHandFollow(leftHandConstNull, leftHandFollowGrp, leftHandFollowPropSlider, leftHandFollowRightHandSlider)
        mc.parent(leftHandFollowSliderOutputGrp, allCtrlGrps)

        mc.parent(self.propOrigCtrl, propOrigionalCtrlFollowGrp)
        mc.setAttr(self.propOrigCtrl+".v", 0)
        mc.setAttr(self.propOrigCtrl+".translate", 0, 0, 0)
        mc.parent(propOrigionalCtrlFollowGrp, allCtrlGrps)
        mc.parent(pinnedControllerGrp, propOrigionalCtrlFollowGrp)

    def SetupRightHandFollow(self, rightHandConstNullName, rightHandFollowGrp, rightHandSlider):
        sliderOutput = self.CreateOutputTransform(rightHandSlider)
        parentConstraint = mc.parentConstraint(sliderOutput, rightHandFollowGrp)[0]
        mc.expression(s=f"{parentConstraint}.{rightHandConstNullName}W0=1-({self.pinnedController}.{self.propPiningAttrName}==3?{self.pinnedController}.{self.rightHandToWeaponWeightAttrName}:0);")
        mc.expression(s=f"{parentConstraint}.{sliderOutput}W1={self.pinnedController}.{self.propPiningAttrName}==3?{self.pinnedController}.{self.rightHandToWeaponWeightAttrName}:0;")

    def SetupLeftHandFollow(self, leftHandConstNullName, leftHandFollowGrp, leftHandFollowPropSlider, leftHandFollowRightHandSlider):
        leftHandFollowSliderOutput = leftHandFollowGrp + "_slider_ouput"
        mc.createNode("transform", name = leftHandFollowSliderOutput)
        leftHandFollowSliderOutputGrp = leftHandFollowSliderOutput + "_grp"
        mc.group(leftHandFollowSliderOutput, n=leftHandFollowSliderOutputGrp)
        mc.matchTransform(leftHandFollowSliderOutputGrp, leftHandFollowPropSlider) 

        mc.parentConstraint(leftHandFollowPropSlider, leftHandFollowSliderOutputGrp)
        sliderParentConstraint = mc.parentConstraint(leftHandFollowRightHandSlider, leftHandFollowSliderOutputGrp)[0]
        mc.expression(s=f"{sliderParentConstraint}.{leftHandFollowPropSlider}W0={self.pinnedController}.{self.propPiningAttrName}==3?1:0;")
        mc.expression(s=f"{sliderParentConstraint}.{leftHandFollowRightHandSlider}W1=1-({self.pinnedController}.{self.propPiningAttrName}==3?1:0);")

        parentConstraint = mc.parentConstraint(leftHandFollowSliderOutput, leftHandFollowGrp)[0]
        mc.expression(s=f"{parentConstraint}.{leftHandConstNullName}W0=1-({self.pinnedController}.{self.propPiningAttrName}>=2?{self.pinnedController}.{self.leftHandToWeaponWeightAttrName}:0);")
        mc.expression(s=f"{parentConstraint}.{leftHandFollowSliderOutput}W1={self.pinnedController}.{self.propPiningAttrName}>=2?{self.pinnedController}.{self.leftHandToWeaponWeightAttrName}:0;")

        return leftHandFollowSliderOutputGrp

    def CreateHandFollowGrps(self, handName):
        handNull = handName + "_Null"
        handConstNull = handName + "_ConstNull"
        mc.group(handName, n=handNull)
        mc.group(handNull, n=handConstNull)
        handConstraint = mc.parentConstraint(handConstNull, handNull)[0]
        return handNull, handConstNull

    def MakeHandFollowSliders(self, variantSubFix, varientName):
        leftHandCtrl = None
        rightHandCtrl = None
        if variantSubFix == "rightHandDriven": 
            leftHandCtrl = variantSubFix + "_l_hand_slider"
            self.MakeSlider(varientName, leftHandCtrl)

        if variantSubFix == "weaponDrivesHands":
            leftHandCtrl = variantSubFix + "_l_hand_slider"
            rightHandCtrl = variantSubFix + "_r_hand_slider"
            self.MakeSlider(varientName, leftHandCtrl)
            self.MakeSlider(varientName, rightHandCtrl)

        return leftHandCtrl, rightHandCtrl

    def MakeSlider(self, sliderParent, sliderName):
        mel.eval(f"curve -d 1 -n {sliderName} -p -5 0.5 0.5 -p 5 0.5 0.5 -p 5 -0.5 0.5 -p -5 -0.5 0.5 -p -5 0.5 0.5 -p -5 0.5 -0.5 -p 5 0.5 -0.5 -p 5 0.5 0.5 -p 5 0.5 -0.5 -p 5 -0.5 -0.5 -p 5 -0.5 0.5 -p 5 -0.5 -0.5 -p -5 -0.5 -0.5 -p -5 0.5 -0.5 -p -5 -0.5 -0.5 -p -5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;")

        mc.scale(self.sliderSize, self.sliderSize, self.sliderSize, sliderName)
        mc.makeIdentity(sliderName, apply=True)

        sliderOffsetGrpName = sliderName + "_offset_grp"
        sliderGrpName = sliderName + "_grp"
        mc.group(sliderName, n=sliderOffsetGrpName)
        mc.group(sliderOffsetGrpName, n = sliderGrpName)
        mc.parent(sliderGrpName,sliderParent)
        mc.setAttr(f"{sliderGrpName}.translate", 0, 0, 0)
        mc.setAttr(f"{sliderGrpName}.rotate", 0, 0, 0)
        return sliderName, sliderGrpName, sliderOffsetGrpName

    def CreateOutputTransform(self, controllerName):
        outputName = controllerName + "_output"
        mc.createNode("transform", name = outputName)
        mc.parent(outputName, controllerName)
        mc.setAttr(outputName+".translate", 0, 0, 0)
        mc.setAttr(outputName+".rotate", 0, 0, 0)
        return outputName

    def MakePropControlVariant(self, variantSubfix):
        mc.select(self.propOrigCtrl)
        variantCtrlName = self.propOrigCtrl + f"_{variantSubfix}"
        variantCtrlOffsetGrpName = variantCtrlName + "_offset_grp"
        variantCtrlGrpName = variantCtrlName + "_grp"
        mc.duplicate(n=variantCtrlName)
        mc.group(variantCtrlName, n=variantCtrlOffsetGrpName)
        mc.group(variantCtrlOffsetGrpName, n = variantCtrlGrpName)
        variantOutputName = self.CreateOutputTransform(variantCtrlName) 
        return variantCtrlName, variantCtrlGrpName, variantCtrlOffsetGrpName, variantOutputName
        
    def MakePinnerController(self, name, size):
        mel.eval(f"curve -d 1 -n {name} -p -0.5 0.5 0.5 -p -0.5 -0.0130096 0.5 -p -0.5 -0.0130096 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.0130096 0.5 -p -0.5 -0.0130096 0.5 -p -0.5 -0.0130096 -0.5 -p 0.5 -0.0130096 -0.5 -p 0.5 -0.0130096 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.0130096 -0.5 -p 0 -0.502633 0 -p -0.5 -0.0130096 0.5 -p 0.5 -0.0130096 0.5 -p 0 -0.502633 0 -p -0.5 -0.0130096 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 ;")
        mc.scale(size, size, size, name)
        mc.makeIdentity(name, apply=True)
        offsetGrpName = name + "_offset_grp"
        mc.group(name, n=offsetGrpName) 
        grpName = name + "_grp"
        mc.group(offsetGrpName, n=grpName)

        mc.addAttr(name, ln=self.propPiningAttrName, at="enum", en= ":".join(self.pinnerControllerOptions) + ":", k=True)
        mc.addAttr(name, ln=self.rightHandToWeaponWeightAttrName, at="float", min=0, max=1, k=True)
        mc.addAttr(name, ln=self.leftHandToWeaponWeightAttrName, at="float", min=0, max=1, k=True)

        mc.scale(self.pinnerSize, self.pinnerSize, self.pinnerSize, name)
        mc.makeIdentity(name, apply=True)

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
        self.propOrigCtrl = mc.ls(sl=True)[0]
        return self.propOrigCtrl

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
    
class FloatSliderGroup(QWidget):
    def __init__(self, infoName, startVal, InfoPickedCallback):
        super().__init__()
        self.InfoPickedCallback = InfoPickedCallback
        masterLayout = QHBoxLayout()
        self.setLayout(masterLayout)

        masterLayout.addWidget(QLabel(infoName))
        self.slider = QSlider()
        self.slider.setValue(startVal)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.valueChanged.connect(self.ValueChanged)

        masterLayout.addWidget(self.slider)

        self.valueLabel = QLabel()
        self.valueLabel.setText(str(startVal))
        masterLayout.addWidget(self.valueLabel)

    def ValueChanged(self, newValue):
        self.InfoPickedCallback(newValue)
        self.valueLabel.setText(str(newValue))

        
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
        currentProCtrlWidget = InfoAssignWidget("current prop controller", self.multiParent.propOrigCtrl, self.multiParent.AssignSelectionAsCurrentPropCtrl)
        self.masterLayout.addWidget(currentProCtrlWidget)

        rightHandCtrlWidget = InfoAssignWidget("right hand ik controller", self.multiParent.rightHandIKCtrl, self.multiParent.AssignSelectionAsRightHandIkCtrl)
        self.masterLayout.addWidget(rightHandCtrlWidget)

        leftHandCtrlWidget = InfoAssignWidget("left hand ik controller", self.multiParent.leftHandIKCtrl, self.multiParent.AssignSelectionAsLeftHandIkCtrl)
        self.masterLayout.addWidget(leftHandCtrlWidget)

        righHandJntWidget = InfoAssignWidget("right hand jnt", self.multiParent.rightHandJnt, self.multiParent.AssignSelectionAsRightHandJnt)
        self.masterLayout.addWidget(righHandJntWidget)

        leftHandJntWidget = InfoAssignWidget("left hand jnt", self.multiParent.leftHandJnt, self.multiParent.AssignSelectionAsLeftHandJnt)
        self.masterLayout.addWidget(leftHandJntWidget)

        self.masterLayout.addWidget(FloatSliderGroup("Pinner Controller Size", self.multiParent.pinnerSize, self.multiParent.SetPinnerControllerSize))
        self.masterLayout.addWidget(FloatSliderGroup("Slider Size", self.multiParent.sliderSize, self.multiParent.SetSliderSize))

MultiParentWidget().show()

        


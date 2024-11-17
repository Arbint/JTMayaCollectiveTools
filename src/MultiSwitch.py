import maya.cmds as mc
import maya.mel as mel

from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QListWidget, QFormLayout, QLineEdit, QSlider, QListWidgetItem
from PySide2.QtCore import Signal
from PySide2.QtCore import Qt, Signal
from MayaUtilities import QMayaWidget

class MultiEntry:
    def __init__(self, name: str, items: list[str]):
        self.entryName = name
        self.items = items

    def addSelectedToEntry(self):
        sel = mc.ls(sl=True, fl=True)
        for item in sel:
            if item in self.items:
                continue
            self.items.append(item)

    def removeSelectFromEntry(self):
        sel = mc.ls(sl=True, fl=True)
        for item in sel:
            self.items.remove(item)

    def rename(self, newName):
        self.entryName = newName

    def __str__(self):
        items = []
        if self.items:
            items = self.items
        return f"{self.entryName}: {','.join(items)}"

class MultiSwitch:
    def __init__(self):
        self.items = []
        self.controllerName = "ac_switch"
        self.switchAttr="switch"

    def SetControllerName(self, newName: str):
        self.controllerName = newName
        
    def AddSelectionAsEntry(self, entryName):
        sel = mc.ls(sl=True, fl=True)
        newEntry = MultiEntry(entryName, sel)
        self.items.append(newEntry)
        return newEntry

    def RemoveEntry(self, multiEntry):
        self.items.remove(multiEntry)
        for item in self.items:
            print(item)

    def BuildSwitch(self):
        command = f"curve -d 1 -n {self.controllerName} -p -1 1 0 -p -3 1 0 -p -3 -1 0 -p -1 -1 0 -p -1 -3 0 -p 1 -3 0 -p 1 -1 0 -p 3 -1 0 -p 3 1 0 -p 1 1 0 -p 1 3 0 -p -1 3 0 -p -1 1 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12;"
        print(command)
        mel.eval(command)
        switchGrpName = self.controllerName + "_grp"
        mc.group(self.controllerName, n = switchGrpName)

        names = []
        for item in self.items:
            names.append(item.entryName)

        mc.addAttr(self.controllerName, ln=self.switchAttr, at="enum", en= ":".join(names) +":all" + ":", k=True)
        for i, item in enumerate(self.items):
            item: MultiEntry = item
            entryObjects = item.items
            for entryObj in entryObjects:
                # mc.expression(s=f"{entryObj}.sx={self.controllerName}.{self.switchAttr}=={i}?1:0;")
                # mc.expression(s=f"{entryObj}.sy={self.controllerName}.{self.switchAttr}=={i}?1:0;")
                # mc.expression(s=f"{entryObj}.sz={self.controllerName}.{self.switchAttr}=={i}?1:0;")
                # mc.expression(s=f"{entryObj}.v={self.controllerName}.{self.switchAttr}=={i}?1:0;")
                self.CreateSwithCtrlExpression(entryObj, i)

    def CreateSwithCtrlExpression(self, entryObj, index):
        switchAttr = f"{self.controllerName}.{self.switchAttr}"
        allIndex = len(self.items)
        command = f"{entryObj}.sx={entryObj}.sy={entryObj}.sz={entryObj}.v={switchAttr}=={allIndex}?1:({switchAttr}=={index}?1:0);"
        mc.expression(s=command)


class EntryWidget(QWidget):
    onDeleted = Signal(QListWidgetItem, MultiEntry) 
    def __init__(self, entry: MultiEntry, item: QListWidgetItem):
        super().__init__()
        self.entry = entry
        self.item = item

        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        self.entryNameLineEdit = QLineEdit()
        self.entryItemsLabel = QLabel()
        addBtn = QPushButton("+")
        removeBtn = QPushButton("-")
        deleteBtn = QPushButton("x")

        self.masterLayout.addWidget(self.entryNameLineEdit)
        self.masterLayout.addWidget(self.entryItemsLabel)
        self.masterLayout.addWidget(addBtn)
        self.masterLayout.addWidget(removeBtn)
        self.masterLayout.addWidget(deleteBtn)
        
        addBtn.clicked.connect(self.AddButtonClicked)
        removeBtn.clicked.connect(self.RemoveButtonClicked)
        deleteBtn.clicked.connect(self.DeleteButtonClicked)
        self.entryNameLineEdit.editingFinished.connect(self.NameLineEditChange)
        self.RefreshWidgetEntryLabel()

    def NameLineEditChange(self):
        self.entry.rename(self.entryNameLineEdit.text())

    def AddButtonClicked(self):
        self.entry.addSelectedToEntry()
        self.RefreshWidgetEntryLabel()

    def RemoveButtonClicked(self):
        self.entry.removeSelectFromEntry()
        self.RefreshWidgetEntryLabel()

    def DeleteButtonClicked(self):
        self.onDeleted.emit(self.item, self.entry)

    def RefreshWidgetEntryLabel(self):
        self.entryItemsLabel.setText(", ".join(self.entry.items))


class MultiSwitchGUI(QMayaWidget):
    def __init__(self):
        super().__init__()
        self.multiSwitch = MultiSwitch()
        self.setWindowTitle("Multi Switch")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        addEntryBtn = QPushButton("Add Selection")
        addEntryBtn.clicked.connect(self.AddEntryButtonClicked)
        self.masterLayout.addWidget(addEntryBtn)

        self.entryList = QListWidget()
        self.masterLayout.addWidget(self.entryList)

        switchNameLabel = QLabel("Switch Name:")
        self.masterLayout.addWidget(switchNameLabel)

        self.switchControllerNameLineEdit = QLineEdit(self.multiSwitch.controllerName)
        self.switchControllerNameLineEdit.editingFinished.connect(self.ControllerNameUpdated)
        self.masterLayout.addWidget(self.switchControllerNameLineEdit)

        buildSwitchBtn = QPushButton("Build")
        buildSwitchBtn.clicked.connect(self.multiSwitch.BuildSwitch)
        self.masterLayout.addWidget(buildSwitchBtn)

    def ControllerNameUpdated(self):
        self.multiSwitch.SetControllerName(self.switchControllerNameLineEdit.text())

    def AddEntryButtonClicked(self):
        newEntry = self.multiSwitch.AddSelectionAsEntry("")
        newEntryItem = QListWidgetItem()
        newEntryWidget = EntryWidget(newEntry, newEntryItem)
        newEntryItem.setSizeHint(newEntryWidget.sizeHint())
        self.entryList.addItem(newEntryItem)
        self.entryList.setItemWidget(newEntryItem, newEntryWidget)
        newEntryWidget.onDeleted.connect(self.DeleteEntry)

    def DeleteEntry(self, entryListItem, multiEntry):
        print(f"deleting: {entryListItem}, and entry: {multiEntry}")
        self.multiSwitch.RemoveEntry(multiEntry)
        entryWidget = self.entryList.itemWidget(entryListItem)
        self.entryList.takeItem(self.entryList.row(entryListItem))
        if entryWidget:
            entryWidget.deleteLater()

def Run():
    MultiSwitchGUI().show() 


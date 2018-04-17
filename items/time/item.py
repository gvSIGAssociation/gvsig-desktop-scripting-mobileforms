# encoding: utf-8
import gvsig

from gvsig.libs.formpanel import FormPanel
from gvsig import getResource

from addons.mobileforms import factories
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItem
from addons.mobileforms.items.item import MobileFormItemPanel

from org.gvsig.tools.swing.api import ToolsSwingLocator

from java.util import Date

from java.text import DateFormat

class MobileFormItemTimeFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"time","Time")

  def create(self):
    return MobileFormItemTime(self)

  def createPreviewPanel(self):
    return MobileFormItemTimePreviewPanel(self)
    
  def createPropertiesPanel(self):
    return MobileFormItemTimePropertiesPanel(self)

class MobileFormItemTime(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)
    self.__value = ""

  def getValue(self):
    return self.__value
    
  def setValue(self, value):
    self.__value = str(value)
    
  def fromDict(self, item):
    MobileFormItem.fromDict(self,item)
    self.setValue(item.get("value"))

  def asDict(self):
    d = MobileFormItem.asDict(self)
    d["value"] = self.getValue()
    return d

class MobileFormItemTimePropertiesPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "properties.xml"))
    self.translateUI()
    
  def translateUI(self):
    manager = ToolsSwingLocator.getToolsSwingManager()
    for component in ( self.lblType,
        self.lblKey,
        self.lblLabel,
        self.lblValue,
        self.lblIsLabel,
        self.lblMandatory
      ):
      manager.translate(component)

  def put(self, item):
    self.txtType.setText(item.getFactory().getID())
    self.txtKey.setText(item.getKey())
    self.txtLabel.setText(item.getLabel())
    self.chkMandatory.setSelected(item.isMandatory())
    self.chkIsLabel.setSelected(item.isLabel())

    self.txtValue.setText(str(item.getValue()))

  def fetch(self,item):
    item.setKey(self.txtKey.getText())
    item.setLabel(self.txtLabel.getText())
    item.setMandatory(self.chkMandatory.isSelected())
    item.setIsLabel(self.chkIsLabel.isSelected())

    item.setValue(self.txtValue.getText())

class MobileFormItemTimePreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getCaption())
    v = item.getValue()
    if v in ("",None):
      v = DateFormat.getTimeInstance(DateFormat.SHORT).format(Date())
    self.btnDo.setText(v)

  def fetch(self,item):
    pass    
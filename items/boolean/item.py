# encoding: utf-8

import gvsig

from gvsig.libs.formpanel import FormPanel
from gvsig import getResource

from addons.mobileforms import factories
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItem
from addons.mobileforms.items.item import MobileFormItemPanel

from org.gvsig.tools.swing.api import ToolsSwingLocator

class MobileFormItemBooleanFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"boolean","Boolean")

  def create(self):
    return MobileFormItemBoolean(self)

  def createPreviewPanel(self):
    return MobileFormItemBooleanPreviewPanel(self)
    
  def createPropertiesPanel(self):
    return MobileFormItemBooleanPropertiesPanel(self)

class MobileFormItemBoolean(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)
    self.__value = False

  def getValue(self):
    return self.__value

  def setValue(self, value):
    if value in (True, False):
      self.__value = value
    elif value == None:
      self.__value = False
    else:
      self.__value =  (str(value).lower() == "true")
    
  def fromDict(self, item):
    MobileFormItem.fromDict(self,item)
    self.setValue(item.get("value"))

  def asDict(self):
    d = MobileFormItem.asDict(self)
    if self.getValue():
      d["value"] = "true"
    else:
      d["value"] = "false"
    return d

class MobileFormItemBooleanPropertiesPanel(MobileFormItemPanel, FormPanel):
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

    if item.getValue():
      self.cboValue.setSelectedItndex(0)
    else:
      self.cboValue.setSelectedItndex(1)
    #self.cboValue.setSelectedItem(str(item.getValue()))

  def fetch(self,item):
    item.setKey(self.txtKey.getText())
    item.setLabel(self.txtLabel.getText())
    item.setMandatory(self.chkMandatory.isSelected())
    item.setIsLabel(self.chkIsLabel.isSelected())

    item.setValue(self.cboValue.getSelectedItem())


class MobileFormItemBooleanPreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getCaption())
    self.chkValue.setSelected(item.getValue())

  def fetch(self,item):
    item.setValue(self.chkValue.isSelected())
    
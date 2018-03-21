# encoding: utf-8
import gvsig

from gvsig.libs.formpanel import FormPanel
from gvsig import getResource
from numbers import Number

from addons.mobileforms import factories
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItem
from addons.mobileforms.items.item import MobileFormItemPanel

class MobileFormItemDoubleFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"double","Double")

  def create(self):
    return MobileFormItemDouble(self)

  def createPreviewPanel(self):
    return MobileFormItemDoublePreviewPanel(self)

  def createPropertiesPanel(self):
    return MobileFormItemDoublePropertiesPanel(self)

class MobileFormItemDouble(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)
    self.__value = 0.0

  def getValue(self):
    return self.__value
    
  def setValue(self, value):
    if isinstance(value,Number):
      self.__value = float(value)
      return
    try:
      self.__value = float(str(value))
    except:
      pass
    
  def fromDict(self, item):
    MobileFormItem.fromDict(self,item)
    self.setValue(item.get("value"))

  def asDict(self):
    d = MobileFormItem.asDict(self)
    d["value"] = str(self.getValue())
    return d

class MobileFormItemDoublePropertiesPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "properties.xml"))

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

class MobileFormItemDoublePreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getCaption())
    self.txtValue.setText(str(item.getValue()))

  def fetch(self,item):
    item.setValue(self.txtValue.getText())
    
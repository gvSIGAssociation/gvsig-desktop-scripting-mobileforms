# encoding: utf-8
import gvsig

from gvsig.libs.formpanel import FormPanel
from gvsig import getResource

from addons.mobileforms import factories
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItem
from addons.mobileforms.items.item import MobileFormItemPanel

class MobileFormItemPrimaryKeyFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"primary_key","Primary key")

  def create(self):
    return MobileFormItemPrimaryKey(self)

  def createPreviewPanel(self):
    return None
    
  def createPropertiesPanel(self):
    return MobileFormItemPrimaryKeyPropertiesPanel(self)

class MobileFormItemPrimaryKey(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)
    self.__value = True

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

class MobileFormItemPrimaryKeyPropertiesPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "properties.xml"))

  def put(self, item):
    self.txtType.setText(item.getFactory().getID())
    self.txtKey.setText(item.getKey())
    self.chkMandatory.setSelected(item.isMandatory())
    self.txtValue.setText(str(item.getValue()))

  def fetch(self,item):
    item.setKey(self.txtKey.getText())
    item.setMandatory(self.chkMandatory.isSelected())
    item.setValue(self.txtValue.getText())

    
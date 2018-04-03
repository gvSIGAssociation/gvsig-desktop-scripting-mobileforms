# encoding: utf-8
import gvsig

from gvsig.libs.formpanel import FormPanel
from gvsig import getResource

from addons.mobileforms import factories
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItem
from addons.mobileforms.items.item import MobileFormItemPanel

from org.gvsig.tools.swing.api import ToolsSwingLocator

class MobileFormItemMapFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"map","Map")

  def create(self):
    return MobileFormItemMap(self)

  def createPreviewPanel(self):
    return MobileFormItemMapPreviewPanel(self)
    
  def createPropertiesPanel(self):
    return MobileFormItemMapPropertiesPanel(self)

class MobileFormItemMap(MobileFormItem):
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

class MobileFormItemMapPropertiesPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "properties.xml"))
    self.translateUI()
    
  def translateUI(self):
    manager = ToolsSwingLocator.getToolsSwingManager()
    for component in ( self.lblType,
        self.lblKey,
        self.lblLabel,
        self.lblMandatory
      ):
      manager.translate(component)

  def put(self, item):
    self.txtType.setText(item.getFactory().getID())
    self.txtKey.setText(item.getKey())
    self.txtLabel.setText(item.getLabel())
    self.chkMandatory.setSelected(item.isMandatory())

    #self.txtValue.setText(str(item.getValue()))

  def fetch(self,item):
    item.setKey(self.txtKey.getText())
    item.setLabel(self.txtLabel.getText())
    item.setMandatory(self.chkMandatory.isSelected())

    #item.setValue(self.txtValue.getText())

class MobileFormItemMapPreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getCaption())
    #self.txtValue.setText(str(item.getValue()))

  def fetch(self,item):
    pass
    #item.setValue(self.txtValue.getText())
    
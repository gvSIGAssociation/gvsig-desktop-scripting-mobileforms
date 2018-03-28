# encoding: utf-8
import gvsig

from gvsig.libs.formpanel import FormPanel
from gvsig import getResource

from addons.mobileforms import factories
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItem
from addons.mobileforms.items.item import MobileFormItemPanel

from org.gvsig.tools.swing.api import ToolsSwingLocator

class MobileFormItemSketchFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"sketch","Sketch")

  def create(self):
    return MobileFormItemSketch(self)

  def createPreviewPanel(self):
    return MobileFormItemSketchPreviewPanel(self)
    
  def createPropertiesPanel(self):
    return MobileFormItemSketchPropertiesPanel(self)

class MobileFormItemSketch(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)

  def fromDict(self, item):
    MobileFormItem.fromDict(self,item)

  def asDict(self):
    d = MobileFormItem.asDict(self)
    return d

class MobileFormItemSketchPropertiesPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "properties.xml"))
    self.translateUI()
    
  def translateUI(self):
    manager = ToolsSwingLocator.getToolsSwingManager()
    for component in ( self.lblType,
        self.lblKey,
        self.lblLabel,
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

  def fetch(self,item):
    item.setKey(self.txtKey.getText())
    item.setLabel(self.txtLabel.getText())
    item.setMandatory(self.chkMandatory.isSelected())
    item.setIsLabel(self.chkIsLabel.isSelected())

class MobileFormItemSketchPreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getCaption())

  def fetch(self,item):
    pass
    
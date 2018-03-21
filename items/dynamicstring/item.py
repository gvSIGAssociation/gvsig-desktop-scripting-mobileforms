# encoding: utf-8
import gvsig

from gvsig.libs.formpanel import FormPanel
from gvsig import getResource

from addons.mobileforms import factories
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItemPanel
from addons.mobileforms.items.string.item import MobileFormItemString
from addons.mobileforms.items.string.item import MobileFormItemStringPropertiesPanel

from javax.swing import DefaultListModel

from java.awt import Dimension

class MobileFormItemDynamicStringFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"dynamicstring","Dynamic string")

  def create(self):
    return MobileFormItemDynamicString(self)

  def createPreviewPanel(self):
    return MobileFormItemDynamicStringPreviewPanel(self)
    
  def createPropertiesPanel(self):
    return MobileFormItemDynamicStringPropertiesPanel(self)

class MobileFormItemDynamicString(MobileFormItemString):
  def __init__(self, factory, label=None):
    MobileFormItemString.__init__(self,factory, label)

class MobileFormItemDynamicStringPropertiesPanel(MobileFormItemStringPropertiesPanel):
  def __init__(self, factory):
    MobileFormItemStringPropertiesPanel.__init__(self,factory)

class MobileFormItemDynamicStringPreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getCaption())
    model = DefaultListModel()
    for line in item.getValue().split(";"):
      model.addElement(line.strip())
    self.lstValues.setModel(model)
    h = self.lstValues.getFixedCellHeight() * model.getSize()
    d = self.lstValues().getPreferredSize()
    self.lstValues.setPreferredsize(Dimension(d.width, h))
    

  def fetch(self,item):
    pass
    
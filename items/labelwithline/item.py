# encoding: utf-8
import gvsig

from gvsig.libs.formpanel import FormPanel
from gvsig import getResource

from addons.mobileforms import factories
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.label.item import MobileFormItemLabel
from addons.mobileforms.items.label.item import MobileFormItemLabelPropertiesPanel
from addons.mobileforms.items.label.item import MobileFormItemLabelPreviewPanel

class MobileFormItemLabelWithLineFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"labelwithline","LabelWithLine")

  def create(self):
    return MobileFormItemLabelWithLine(self)

  def createPreviewPanel(self):
    return MobileFormItemLabelWithLinePreviewPanel(self)
    
  def createPropertiesPanel(self):
    return MobileFormItemLabelWithLinePropertiesPanel(self)

class MobileFormItemLabelWithLine(MobileFormItemLabel):
  def __init__(self, factory, label=None):
    MobileFormItemLabel.__init__(self,factory, label)

class MobileFormItemLabelWithLinePropertiesPanel(MobileFormItemLabelPropertiesPanel):
  def __init__(self, factory):
    MobileFormItemLabelPropertiesPanel.__init__(self,factory)

class MobileFormItemLabelWithLinePreviewPanel(MobileFormItemLabelPreviewPanel):
  def __init__(self, factory):
    MobileFormItemLabelPreviewPanel.__init__(self,factory)
    
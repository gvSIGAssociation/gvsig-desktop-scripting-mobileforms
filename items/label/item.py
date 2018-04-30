# encoding: utf-8
import gvsig

from gvsig.libs.formpanel import FormPanel
from gvsig import getResource

from addons.mobileforms import factories
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItem
from addons.mobileforms.items.item import MobileFormItemPanel

from numbers import Number

from org.gvsig.tools.swing.api import ToolsSwingLocator

class MobileFormItemLabelFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"label","Label")

  def create(self):
    return MobileFormItemLabel(self)

  def createPreviewPanel(self):
    return MobileFormItemLabelPreviewPanel(self)
    
  def createPropertiesPanel(self):
    return MobileFormItemLabelPropertiesPanel(self)

class MobileFormItemLabel(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)
    self.__value = True
    self.__size = 20
    self.__url = ""

  def getValue(self):
    return self.__value
    
  def setValue(self, value):
    self.__value = str(value)
    
  def getUrl(self):
    return self.__url
    
  def setUrl(self, url):
    self.__url = str(url)
    
  def getSize(self):
    return self.__size
    
  def setSize(self, size):
    if isinstance(size,Number):
      self.__size = int(size)
      return
    try:
      self.__size = int(str(size))
    except:
      pass
    
  def fromDict(self, item):
    MobileFormItem.fromDict(self,item)
    self.setValue(item.get("value",""))
    self.setSize(item.get("size",20))
    self.setSize(item.get("url",""))

  def asDict(self):
    d = MobileFormItem.asDict(self)
    d["value"] = self.getValue()
    d["size"] = str(self.getSize())
    if not self.getUrl() in ("",None):
      d["url"] = str(self.getUrl())
    return d

class MobileFormItemLabelPropertiesPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "properties.xml"))
    self.translateUI()
    
  def translateUI(self):
    manager = ToolsSwingLocator.getToolsSwingManager()
    for component in ( self.lblType,
        self.lblValue,
        self.lblSize,
        self.lblUrl
      ):
      manager.translate(component)

  def put(self, item):
    self.txtType.setText(item.getFactory().getID())
    self.txtValue.setText(str(item.getValue()))
    self.txtSize.setText(str(item.getSize()))
    self.txtUrl.setText(str(item.getUrl()))

  def fetch(self,item):
    item.setValue(self.txtValue.getText())
    item.setSize(self.txtSize.getText())
    item.setUrl(self.txtUrl.getText())

class MobileFormItemLabelPreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getValue())
    self.lblLabel.setFont(self.lblLabel.getFont().deriveFont(float(item.getSize())))
    
  def fetch(self,item):
    pass
    
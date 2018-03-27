# encoding: utf-8
import gvsig

from collections import OrderedDict

from gvsig import getResource
from gvsig.commonsdialog import confirmDialog
from gvsig.commonsdialog import QUESTION
from gvsig.commonsdialog import YES
from gvsig.commonsdialog import YES_NO
from gvsig.commonsdialog import inputbox
from gvsig.libs.formpanel import FormPanel
import sys

from addons.mobileforms.mobileformsutil import getTitle
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItem
from addons.mobileforms.items.item import MobileFormItemPanel


class MobileFormItemMultiStringComboFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"multistringcombo","Combo multi-string")

  def create(self):
    return MobileFormItemMultiStringCombo(self)

  def createPreviewPanel(self):
    return MobileFormItemMultiStringComboPreviewPanel(self)
    
  def createPropertiesPanel(self):
    return MobileFormItemMultiStringComboPropertiesPanel(self)

class MobileFormItemMultiStringCombo(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)
    self.__value = True
    self.__values = list()

  def getValue(self):
    return self.__value
    
  def setValue(self, value):
    self.__value = str(value)

  def getValues(self):
    return self.__values
    
  def fromDict(self, item):
    try:
      MobileFormItem.fromDict(self,item)
      self.__values = list()
      self.setValue(item.get("value"))
      items = item.get("values").get("items")
      for value in items:
        self.__values.append(str(value.get("item")))
    except:
      print "Can't get values from stringcombo: ", repr(item)
      print sys.exc_info()[1]
      
  def asDict(self):
    d = MobileFormItem.asDict(self)
    d["value"] = self.getValue()
    items = list()
    for item in self.__values:
      d2 = OrderedDict()
      d2["item"] = item
      items.append(d2)
    d3 = OrderedDict()
    d3["items"] = items
    d["values"] = d3
    return d

class MobileFormItemMultiStringComboPropertiesPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "properties.xml"))

  def put(self, item):
    self.txtType.setText(item.getFactory().getID())
    self.txtKey.setText(item.getKey())
    self.txtLabel.setText(item.getLabel())
    self.chkMandatory.setSelected(item.isMandatory())
    self.chkIsLabel.setSelected(item.isLabel())

    model = self.lstValues.getModel()
    model.removeAllElements()
    for value in item.getValues():
      model.addElement(str(value))
    self.lstValues.setSelectedValue(str(item.getValue()), True)
    self.txtValue.setText(str(item.getValue()))

  def fetch(self,item):
    item.setKey(self.txtKey.getText())
    item.setLabel(self.txtLabel.getText())
    item.setMandatory(self.chkMandatory.isSelected())
    item.setIsLabel(self.chkIsLabel.isSelected())

    values = item.getValues()
    del values[:]
    item.setValue(self.txtValue.getText())
    model = self.lstValues.getModel()
    for value in model.elements():
      values.append(value)

  def lstValues_change(self, event):
    if event.getValueIsAdjusting() :
      return
    value = self.lstValues.getSelectedValue()
    if value == None:
      value = ""
    self.txtValue.setText(str(value))
    
  def btnClearValue_click(self, *args):
    self.txtValue.setText("")
    self.lstValues.clearSelection()
        
  def btnUp_click(self, *args):
    model = self.lstValues.getModel()
    index = self.lstValues.getSelectedIndex()
    if index < 1:
      return
    x = model.getElementAt(index)
    model.removeElementAt(index)
    model.insertElementAt(x,index-1)
    self.lstValues.setSelectedIndex(index-1)
    
  def btnDown_click(self, *args):
    model = self.lstValues.getModel()
    index = self.lstValues.getSelectedIndex()
    if index >= model.getSize()-1:
      return
    x = model.getElementAt(index)
    model.removeElementAt(index)
    model.insertElementAt(x,index+1)
    self.lstValues.setSelectedIndex(index+1)
    
  def btnDelete_click(self, *args):
    model = self.lstValues.getModel()
    index = self.lstValues.getSelectedIndex()
    if index < 0:
      return
    if confirmDialog(
      u"¿ Seguro que desea eliminar el elemento seleccionado ?",
      getTitle(), 
      optionType=YES_NO, 
      messageType=QUESTION) != YES:
      return
    model.removeElementAt(index)
    self.lstValues.setSelectedIndex(index)
    
  def btnAdd_click(self, *args):
    model = self.lstValues.getModel()
    index = self.lstValues.getSelectedIndex()
    item = inputbox(
      "Item",
      getTitle(),
      messageType=QUESTION, 
      initialValue="item %s" % index
    )
    model.addElement(item)

class MobileFormItemMultiStringComboPreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getCaption())
    
  def fetch(self,item):
    pass

  
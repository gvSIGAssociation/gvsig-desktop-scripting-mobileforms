# encoding: utf-8
import gvsig

from collections import OrderedDict

from gvsig import getResource
from gvsig.commonsdialog import confirmDialog
from gvsig.commonsdialog import QUESTION
from gvsig.commonsdialog import YES
from gvsig.commonsdialog import YES_NO
from gvsig.commonsdialog import inputbox
from gvsig.libs.formpanel import FormPanel, FormComponent
import sys

from addons.mobileforms.mobileformsutil import getTitle
from addons.mobileforms.items.item import MobileFormItemFactory
from addons.mobileforms.items.item import MobileFormItem
from addons.mobileforms.items.item import MobileFormItemPanel
from addons.mobileforms.mobileformsutil import isEmpty

MIN_COMBOS=1
MAX_COMBOS=3

class MobileFormItemConnectedStringComboFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"connectedstringcombo","Connected combo string")

  def create(self):
    return MobileFormItemConnectedStringCombo(self)

  def createPreviewPanel(self):
    return MobileFormItemConnectedStringComboPreviewPanel(self)
    
  def createPropertiesPanel(self):
    return MobileFormItemConnectedStringComboPropertiesPanel(self)

class MobileFormItemConnectedStringCombo(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)
    self.__value = None # string
    self.__values = None # list of list of string

  def getValue(self):
    return self.__value
    
  def setValue(self, value):
    self.__value = value
      
  def getValues(self):
    return self.__values
    
  def fromDict(self, item):
    try:
      MobileFormItem.fromDict(self,item)
      self.__values = list()
      self.setValue(item.get("value"))

      allvalues = item["values"].values()
      for values in allvalues:
        l = list()
        for items in values:
          l.append(str(items.get("item","")))
        self.__values.append(l)
      
    except:
      print "Can't get values from stringcombo: ", repr(item)
      print sys.exc_info()[1]
      
  def asDict(self):
    d = MobileFormItem.asDict(self)
    n = 1
    values = OrderedDict()
    for items in self.__values:
      key = "items %s" % n
      values[key] = list() 
      for item in items:
        values[key].append({"item": item})
      n+=1    
    d["values"] = values
    return d


class OneCombo(FormComponent):
  def __init__(self, form, index, lstValues, btnUp, btnDown, btnDelete, btnAdd):
    FormComponent.__init__(self)
    self.form = form
    self.index = index
    self.lstValues = lstValues
    self.btnUp = btnUp
    self.btnDown = btnDown
    self.btnDelete = btnDelete
    self.btnAdd = btnAdd
    self.autobind()
    
  def setVisible(self, visible):
    self.lstValues.setVisible(visible)
    self.lstValues.getParent().getParent().setVisible(visible) # JScrollPane
    self.btnUp.setVisible(visible)
    self.btnDown.setVisible(visible)
    self.btnDelete.setVisible(visible)
    self.btnAdd.setVisible(visible)
    
  def setValues(self,values):
    model = self.lstValues.getModel()
    model.removeAllElements()
    for value in values:
      model.addElement(str(value))

  def getValues(self):
    model = self.lstValues.getModel()
    values = list()
    for value in model.elements():
      values.append(value)
    return values

  def getValue(self):
    x = self.lstValues.getSelectedValue()
    if x==None:
      x = ""
    return x
    
  def setValue(self, value):
    if isEmpty(value):
      self.lstValues.clearSelection()
    else:
      self.lstValues.setSelectedValue(value,True)
    
  def isEmpty(self):
    return self.lstValues.getModel().getSize()==0

  def clearSelection(self):
    self.lstValues.clearSelection()
    
  def lstValues_change(self, event):
    if event.getValueIsAdjusting() :
      return
    value = self.lstValues.getSelectedValue()
    if isEmpty(value):
      return
    self.form.updateValue("Items %s#%s" % (self.index, value))
    
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
    
class MobileFormItemConnectedStringComboPropertiesPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "properties.xml"))
    self.__combos = list()
    for n in range(MIN_COMBOS,MAX_COMBOS+1):
      combo = OneCombo(
        self,
        n,
        getattr(self,"lstValues"+str(n)), 
        getattr(self,"btnUp"+str(n)), 
        getattr(self,"btnDown"+str(n)), 
        getattr(self,"btnDelete"+str(n)), 
        getattr(self,"btnAdd"+str(n))
      )
      combo.setVisible(False)
      self.__combos.append(combo)
      
  def updateValue(self, value):
    self.txtValue.setText(value)
    
  def btnClearValue_click(self, *args):
    self.txtValue.setText("")
    for combo in self.__combos:
      combo.clearSelection()
          
  def put(self, item):
    self.txtType.setText(item.getFactory().getID())
    self.txtKey.setText(item.getKey())
    self.txtLabel.setText(item.getLabel())
    self.chkMandatory.setSelected(item.isMandatory())
    self.chkIsLabel.setSelected(item.isLabel())

    allvalues = item.getValues()

    selecteds = item.getValue()
    if isEmpty(selecteds):
      selecteds = [None]*len(allvalues)
    else:
      selecteds = selecteds.split("#")
      if len(selecteds) != len(allvalues):
        selecteds = [None]*len(allvalues)
        
    n = 1
    self.__combos = list()
    for values in allvalues:
      combo = OneCombo(
        self,
        n,
        getattr(self,"lstValues"+str(n)), 
        getattr(self,"btnUp"+str(n)), 
        getattr(self,"btnDown"+str(n)), 
        getattr(self,"btnDelete"+str(n)), 
        getattr(self,"btnAdd"+str(n))
      )
      combo.setValues(values)
      combo.setVisible(True)
      combo.setValue(selecteds[n-1])
      self.__combos.append(combo)
      n+=1

  def fetch(self,item):
    item.setKey(self.txtKey.getText())
    item.setLabel(self.txtLabel.getText())
    item.setMandatory(self.chkMandatory.isSelected())
    item.setIsLabel(self.chkIsLabel.isSelected())

    values = item.getValues()
    del values[:]
    for combo in self.__combos:    
      if not combo.isEmpty():
        values.append(combo.getValues())
        
class MobileFormItemConnectedStringComboPreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getCaption())
    self.btnClose.setVisible(False)
    allvalues = item.getValues()
    for n in range(MIN_COMBOS,MAX_COMBOS+1):
      combo = getattr(self,"cboValues%s"%n,None)
      if combo == None:
        continue
      if n > len(allvalues):
        combo.setVisible(False)
        continue
      combo.setVisible(True)
      model = combo.getModel()
      model.removeAllElements()
      for value in allvalues[n-1]:
        model.addElement(str(value))
 
  def fetch(self,item):
    pass

  
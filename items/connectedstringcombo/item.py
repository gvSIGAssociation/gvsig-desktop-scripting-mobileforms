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

from org.gvsig.tools.swing.api import ToolsSwingLocator

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

class ItemWithSubitems(list):
  def __init__(self, value=None):
    list.__init__(self)
    self.__value = value

  def setValue(self, value):
    self.__value = value

  def getValue(self):
    return self.__value
    
  def __repr__(self):
    return self.__value

  __str__ = __repr__
    
class MobileFormItemConnectedStringCombo(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)
    self.__availableValues = list() # ItemWithSubitems
    self.__selectedValue = None
    
  def getSelectedValue(self):
    return self.__selectedValue

  def setSelectedValue(self,value):
    self.__selectedValue = value
    
  def getAvailableValues(self):
    return self.__availableValues
    
  def fromDict(self, rawitem):
    try:
      MobileFormItem.fromDict(self,rawitem)
      self.__availableValues = list()
      rawitems = rawitem.get("values")
      for rawvalue, rawsubitems in rawitems.items():
        item = ItemWithSubitems(rawvalue)
        for x in rawsubitems:
          item.append(x["item"])
        self.__availableValues.append(item)
      self.__selectedValue = rawitem["value"]
      
    except:
      print "Can't get values from connectedstringcombo: ", repr(rawitem)
      print sys.exc_info()[1]
      
  def asDict(self):
    d = MobileFormItem.asDict(self)
    values = OrderedDict()
    for items in self.__availableValues:
      rawsubitems = list()
      for subitem in items:
        if subitem in ( " ", None):
          subitem = ""
        rawsubitems.append({"item": subitem})
      values[items.getValue()] = rawsubitems
    d["values"] = values
    d["value"] = self.__selectedValue
    return d


class BaseCombo(FormComponent):
  def __init__(self, form, lstValues, btnUp, btnDown, btnDelete, btnAdd):
    FormComponent.__init__(self)
    self.form = form
    self.lstValues = lstValues
    self.btnUp = btnUp
    self.btnDown = btnDown
    self.btnDelete = btnDelete
    self.btnAdd = btnAdd
    
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
      model.addElement(value)

  def getValues(self):
    model = self.lstValues.getModel()
    values = list()
    for value in model.elements():
      values.append(value)
    return values

  def getValue(self):
    x = self.lstValues.getSelectedValue()
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

  def btnUp_click(self, event):
    model = self.lstValues.getModel()
    index = self.lstValues.getSelectedIndex()
    if index < 1:
      return
    x = model.getElementAt(index)
    model.removeElementAt(index)
    model.insertElementAt(x,index-1)
    self.lstValues.setSelectedIndex(index-1)
    
  def btnDown_click(self, event):
    model = self.lstValues.getModel()
    index = self.lstValues.getSelectedIndex()
    if index >= model.getSize()-1:
      return
    x = model.getElementAt(index)
    model.removeElementAt(index)
    model.insertElementAt(x,index+1)
    self.lstValues.setSelectedIndex(index+1)
    
  def btnDelete_click(self, event):
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
    
  def setSelected(self, value):
    n = 0
    value = str(value)
    model = self.lstValues.getModel()
    for curvalue in model.elements():
      if value == str(curvalue):
        self.lstValues.setSelectedIndex(n)
        return
      n+=1

class MainCombo(BaseCombo):
  def __init__(self, form, subcombo, lstValues, btnUp, btnDown, btnDelete, btnAdd):
    BaseCombo.__init__(self, form, lstValues, btnUp, btnDown, btnDelete, btnAdd)
    self.autobind()

  def lstValues_change(self, event):
    if event.getValueIsAdjusting() :
      return
    self.form.putValuesInSubcombo()
    self.form.updateValue()
  
  def btnAdd_click(self, *args):
    model = self.lstValues.getModel()
    index = model.getSize()+1
    item = inputbox(
      "Item",
      getTitle(),
      messageType=QUESTION, 
      initialValue="item %s" % index
    )
    if item==None:
      return
    newItem = ItemWithSubitems(item)
    model.addElement(newItem)
    self.lstValues.setSelectedIndex(index-1)
    self.form.putValuesInSubcombo()

class SubCombo(BaseCombo):
  def __init__(self, form, lstValues, btnUp, btnDown, btnDelete, btnAdd):
    BaseCombo.__init__(self, form, lstValues, btnUp, btnDown, btnDelete, btnAdd)
    self.autobind()

  def lstValues_change(self, event):
    if event.getValueIsAdjusting() :
      return
    value = self.lstValues.getSelectedValue()
    if isEmpty(value):
      return
    self.form.updateValue()
  
  def btnUp_click(self, event):
    BaseCombo.btnUp_click(self,event)
    self.form.fetchValuesFromSubcombo()
    
  def btnDown_click(self, event):
    BaseCombo.btnDown_click(self,event)
    self.form.fetchValuesFromSubcombo()
    
  def btnDelete_click(self, event):
    BaseCombo.btnDelete_click(self,event)
    self.form.fetchValuesFromSubcombo()
    
  def btnAdd_click(self, *args):
    model = self.lstValues.getModel()
    index = model.getSize()+1
    item = inputbox(
      "Item",
      getTitle(),
      messageType=QUESTION, 
      initialValue="item %s" % index
    )
    if item == None:
      return
    model.addElement(item)
    self.form.fetchValuesFromSubcombo()

class MobileFormItemConnectedStringComboPropertiesPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "properties.xml"))
    self.__subcombo = SubCombo(
      self,
      getattr(self,"lstValues2"), 
      getattr(self,"btnUp2"), 
      getattr(self,"btnDown2"), 
      getattr(self,"btnDelete2"), 
      getattr(self,"btnAdd2")
    )
    self.__mainCombo = MainCombo(
      self,
      self.__subcombo,
      getattr(self,"lstValues1"), 
      getattr(self,"btnUp1"), 
      getattr(self,"btnDown1"), 
      getattr(self,"btnDelete1"), 
      getattr(self,"btnAdd1")
    )
    self.__mainCombo.setVisible(True)
    self.__subcombo.setVisible(True)
    self.translateUI()
    
  def translateUI(self):
    #manager = ToolsSwingLocator.getToolsSwingManager()
    from addons.mobileforms.patchs.fixtranslatecomponent import TranslateComponent as manager

    for component in ( self.lblType,
        self.lblKey,
        self.lblLabel,
        self.lblValue,
        self.lblIsLabel,
        self.lblMandatory,
        self.lblValues,
        self.btnClearValue,
        self.btnUp1,
        self.btnDown1,
        self.btnDelete1,
        self.btnAdd1,
        self.btnUp2,
        self.btnDown2,
        self.btnDelete2,
        self.btnAdd2
      ):
      manager.translate(component)

  def putValuesInSubcombo(self):
    value = self.__mainCombo.getValue()
    if value==None:
      return
    self.__subcombo.setValues(value)
    
  def fetchValuesFromSubcombo(self):
    mainValue = self.__mainCombo.getValue()
    subValues = self.__subcombo.getValues()
    del mainValue[:]
    if subValues!=None:
      mainValue.extend(subValues)
    
  def updateValue(self):
    mainValue = self.__mainCombo.getValue()
    subValue = self.__subcombo.getValue()
    if mainValue == None:
      self.txtValue.setText("")
      return
    if subValue == None:
      self.txtValue.setText(mainValue.getValue())
      return
    self.txtValue.setText("%s#%s" % (mainValue, subValue))
    
  def btnClearValue_click(self, *args):
    self.txtValue.setText("")
    self.__mainCombo.clearSelection()
    self.__subcombo.clearSelection()
          
  def put(self, item):
    self.txtType.setText(item.getFactory().getID())
    self.txtKey.setText(item.getKey())
    self.txtLabel.setText(item.getLabel())
    self.chkMandatory.setSelected(item.isMandatory())
    self.chkIsLabel.setSelected(item.isLabel())

    self.__mainCombo.setValues(item.getAvailableValues())
    if not item.getSelectedValue() in ("",None):
      x = item.getSelectedValue().split("#")
      if len(x)>0:
        self.__mainCombo.setSelected(x[0])
      if len(x)>1:
        self.__subcombo.setSelected(x[1])

  def fetch(self,item):
    item.setKey(self.txtKey.getText())
    item.setLabel(self.txtLabel.getText())
    item.setMandatory(self.chkMandatory.isSelected())
    item.setIsLabel(self.chkIsLabel.isSelected())

    values = item.getAvailableValues()
    del values[:]
    values.extend(self.__mainCombo.getValues())
    item.setSelectedValue(self.txtValue.getText())
        
class MobileFormItemConnectedStringComboPreviewPanel(MobileFormItemPanel, FormPanel):
  def __init__(self, factory):
    MobileFormItemPanel.__init__(self,factory)
    FormPanel.__init__(self, getResource(__file__, "preview.xml"))

  def put(self, item):
    self.lblLabel.setText(item.getCaption())
    self.btnClose.setVisible(False)


    model = self.cboValues1.getModel()
    model.removeAllElements()
    for value in item.getAvailableValues():
      model.addElement(value)

    if not item.getSelectedValue() in ("",None):
      x = item.getSelectedValue().split("#")
      if len(x)>0:
        self.setSelected(self.cboValues1,x[0])
      if len(x)>1:
        self.setSelected(self.cboValues2,x[1])
     
  def fetch(self,item):
    pass

  def setSelected(self, combo, value):
    value = str(value)
    model = combo.getModel()
    for n in range(0,model.getSize()):
      curvalue = model.getElementAt(n)
      if value == str(curvalue):
        combo.setSelectedIndex(n)
        return

  def cboValues1_change(self, event):
    mainItem = self.cboValues1.getSelectedItem()
    if mainItem == None:
      return
    model = self.cboValues2.getModel()
    model.removeAllElements()
    for value in mainItem:
      model.addElement(value)
    
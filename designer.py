# encoding: utf-8

import gvsig


from gvsig import getResource
from gvsig.commonsdialog import confirmDialog
from gvsig.commonsdialog import inputbox
from gvsig.commonsdialog import msgbox
from gvsig.commonsdialog import openFileDialog
from gvsig.commonsdialog import QUESTION
from gvsig.commonsdialog import saveFileDialog
from gvsig.commonsdialog import WARNING
from gvsig.commonsdialog import YES
from gvsig.commonsdialog import YES_NO
from gvsig.libs.formpanel import FormPanel
from java.awt import BorderLayout
from java.awt.event import ActionListener
from java.io import File
from java.lang import Object
from javax.swing import DefaultCellEditor
from javax.swing import DefaultComboBoxModel
from javax.swing import DefaultListModel
from javax.swing import JMenuItem
from javax.swing import JPanel
from javax.swing import JPopupMenu
from javax.swing import JTextField
from javax.swing.table import DefaultTableColumnModel
from javax.swing.table import DefaultTableModel
from javax.swing.table import TableCellRenderer
from javax.swing.table import TableColumn
from org.gvsig.scripting import ScriptingLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator
import jarray
import os

from org.icepdf.ri.common import SwingController
from org.icepdf.ri.common import SwingViewBuilder

from addons.mobileforms.fixformpanel import fixFormPanelResourceLoader
from addons.mobileforms.mobileformsutil import getTitle
from addons.mobileforms.mobileformsutil import getDataFolder
from addons.mobileforms.mobileformsutil import initDataFolder
from addons.mobileforms.items.item import MobileFormItemUnknown
from addons.mobileforms.factories import getFactories
from addons.mobileforms.factories import registerFactory
from addons.mobileforms.form import Form
from addons.mobileforms.form import Forms
from addons.mobileforms.items.item import MobileFormItemUnknownFactory
from addons.mobileforms.items.boolean.item import MobileFormItemBooleanFactory
from addons.mobileforms.items.string.item import MobileFormItemStringFactory
from addons.mobileforms.items.double.item import MobileFormItemDoubleFactory
from addons.mobileforms.items.date.item import MobileFormItemDateFactory
from addons.mobileforms.items.integer.item import MobileFormItemIntegerFactory
from addons.mobileforms.items.stringcombo.item import MobileFormItemStringComboFactory
from addons.mobileforms.items.multistringcombo.item import MobileFormItemMultiStringComboFactory
from addons.mobileforms.items.time.item import MobileFormItemTimeFactory
from addons.mobileforms.items.sketch.item import MobileFormItemSketchFactory
from addons.mobileforms.items.pictures.item import MobileFormItemPicturesFactory
from addons.mobileforms.items.hidden.item import MobileFormItemHiddenFactory
from addons.mobileforms.items.primary_key.item import MobileFormItemPrimaryKeyFactory
from addons.mobileforms.items.label.item import MobileFormItemLabelFactory
from addons.mobileforms.items.labelwithline.item import MobileFormItemLabelWithLineFactory
from addons.mobileforms.items.dynamicstring.item import MobileFormItemDynamicStringFactory
from addons.mobileforms.items.connectedstringcombo.item import MobileFormItemConnectedStringComboFactory

class FormItemAddListener(ActionListener):
  def __init__(self, designer, factory):
    self.__designer = designer
    self.__factory = factory

  def actionPerformed(self, *args):
    self.__designer.addFormItem(self.__factory)


class FormItemPreviewCellEditor(DefaultCellEditor):
  def __init__(self):
    DefaultCellEditor.__init__(self, JTextField())
    self.__form = None

  def setForm(self, form):
    self.__form = form

  def getTableCellEditorComponent(self, table, value, isSelected, row, column):
    if self.__form == None:
      return DefaultCellEditor.getTableCellEditorComponent(self,table, value, isSelected, row, column)
    item = self.__form[row]
    if isinstance(item, MobileFormItemUnknown):
      return DefaultCellEditor.getTableCellEditorComponent(self,table, value, isSelected, row, column)
    factory = item.getFactory()
    itemPanel = factory.createPreviewPanel()
    if itemPanel == None:
      return self
    itemPanel.put(item)
    panel = itemPanel.asJComponent() 
    table.setRowHeight(row,int(panel.getPreferredSize().getHeight()))
    return panel

class FormItemPreviewCellRenderer(JPanel,TableCellRenderer):
  def __init__(self):
    self.__form = None

  def setForm(self, form):
    self.__form = form

  def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):
    if self.__form == None:
      return self
    item = self.__form[row]
    if isinstance(item, MobileFormItemUnknown):
      return self
    factory = item.getFactory()
    itemPanel = factory.createPreviewPanel()
    if itemPanel == None:
      return self
    itemPanel.put(item)
    panel = itemPanel.asJComponent() 
    table.setRowHeight(row,int(panel.getPreferredSize().getHeight()))
    return panel
    
    
class Designer(FormPanel):
  def __init__(self):
    FormPanel.__init__(self, getResource(__file__, "designer.xml"))
    self.setPreferredSize(700,500)
    self.__forms = None
    self.__lastItem = None
    self.__lastItemPanel = None
    self.__currentFile = None
    self.__currentForm = None
    self.__lastPath = getDataFolder()
    self.newForms()
    self.tblPreviewForm.getParent().getParent().setBorder(None)
    self.tblPreviewForm.getParent().getParent().setViewportBorder(None)
    
  def setForms(self, forms):
    self.clearFormPreview()
    self.__forms = forms
    self.__lastItem = None
    self.__lastItemPanel = None
    self.__currentForm = None
    self.btnFormDelete.setEnabled(False)
    self.btnFormItemAdd.setEnabled(False)
    self.btnFormItemDelete.setEnabled(False)
    self.btnFormItemDown.setEnabled(False)
    self.btnFormItemUp.setEnabled(False)
    self.txtFormsName.setText(forms.getName())
    self.txtFormsDescription.setText(forms.getDescription())
    self.lstFormItems.getModel().clear()
    self.pnlItem.removeAll()
    self.pnlItem.revalidate()
    model = DefaultComboBoxModel()
    for form in self.__forms:
      model.addElement(form)
    self.cboForms.setModel(model)

    model = DefaultListModel()
    for form in self.__forms:
      model.addElement(form)
    self.lstPreviewForms.setModel(model)

    if self.cboForms.getSelectedItem()!=None:
      self.btnFormDelete.setEnabled(True)
      self.cboForms_click(None)

  def loadForms(self, fname):
    forms = Forms()
    forms.load(fname)
    self.setForms(forms)
    self.__currentFile = fname
    self.__lastPath = os.path.dirname(fname)
    self.btnFileSave.setEnabled(True)
    self.txtPathName.setText(self.__currentFile)

  def saveForms(self, fname):
    self.__forms.setName(self.txtFormsName.getText().strip())
    self.__forms.setDescription(self.txtFormsDescription.getText().strip())
    self.__forms.save(fname)
    self.__currentFile = fname
  
  def newForms(self):
    self.__forms = None
    self.__currentFile = None
    self.btnFormDelete.setEnabled(False)
    self.txtPathName.setText("")
    self.setForms(Forms())

  def updateFormsUI(self):
    self.__forms.setName(self.txtFormsName.getText().strip())
    self.__forms.setDescription(self.txtFormsDescription.getText().strip())
    self.setForms(self.__forms)
  
  def createFormItemAddPopup(self):
    popup = JPopupMenu()
    for factory in getFactories():
      if factory.getID()!="unknown":
        entry = JMenuItem(factory.getName())
        entry.addActionListener(FormItemAddListener(self,factory))
        popup.add(entry)
    return popup

  def updateListOfFormItems(self, form):
    self.btnFormItemDelete.setEnabled(False)
    self.btnFormItemUp.setEnabled(False)
    self.btnFormItemDown.setEnabled(False)
    self.btnFormItemAdd.setEnabled(True)
    model = DefaultListModel()
    for item in form:
      model.addElement(item)
    self.lstFormItems.setModel(model)
    if self.lstFormItems.getSelectedValue()!=None:
      self.btnFormItemDelete.setEnabled(True)
      self.btnFormItemUp.setEnabled(True)
      self.btnFormItemDown.setEnabled(True)

  def clearFormPreview(self):
    model = self.tblPreviewForm.getModel()
    model.setRowCount(0)
    model.setColumnCount(1)
    self.tblPreviewForm.getTableHeader().setUI(None)
    
  def fetchLastItemValues(self):
    if self.__lastItem==None or self.__lastItemPanel==None:
      return
    self.__lastItemPanel.fetch(self.__lastItem)
    
  def addFormItem(self, factory):
    item = factory.create()
    form = self.__currentForm
    form.items().append(item)
    self.updateListOfFormItems(form)
    self.lstFormItems.setSelectedIndex(len(form.items())-1)
    
  def cboForms_click(self,*args):
    form = self.cboForms.getSelectedItem()
    if form == None:
      return
    self.updateListOfFormItems(form)
    self.btnFormDelete.setEnabled(True)
    self.btnFormAdd.setEnabled(True)
    self.__currentForm = form
    self.lstPreviewForms.setSelectedValue(form,True)
      
    
  def lstFormItems_change(self, event):
    if event.getValueIsAdjusting() :
      return
    self.pnlItem.removeAll()
    item = self.lstFormItems.getSelectedValue()
    if item == None:
      self.pnlItem.revalidate()
      return 
    self.btnFormItemDelete.setEnabled(True)
    self.btnFormItemUp.setEnabled(True)
    self.btnFormItemDown.setEnabled(True)
    factory = item.getFactory()
    panel = factory.createPropertiesPanel()
    if panel == None:
      self.pnlItem.revalidate()
      return
    self.fetchLastItemValues()
    self.pnlItem.setLayout(BorderLayout())
    self.pnlItem.add(panel.asJComponent(),BorderLayout.CENTER)
    panel.put(item)
    self.__lastItem = item
    self.__lastItemPanel = panel
    self.pnlItem.revalidate()

  def lstPreviewForms_change(self, event):
    if event.getValueIsAdjusting() :
      return
    form = self.lstPreviewForms.getSelectedValue()
    if form == None:
      return 
    model = DefaultTableModel()
    model.addColumn("")
    for item in form:
      row = jarray.array((item,),Object)
      model.addRow(row)
    self.tblPreviewForm.setModel(model)
    renderer = FormItemPreviewCellRenderer()
    renderer.setForm(form)
    editor = FormItemPreviewCellEditor()
    editor.setForm(form)
    model = DefaultTableColumnModel()
    model.addColumn(TableColumn(0,100,renderer, editor))
    self.tblPreviewForm.setColumnModel(model)
    self.tblPreviewForm.getTableHeader().setUI(None)
    self.tblPreviewForm.setVisible(True)

  def btnFileOpen_click(self, *args):
    f = openFileDialog(u"Select the 'Tags' file to open", initialPath=self.__lastPath)
    if f == None:
      return
    self.loadForms(f[0])
    
  def btnFileSave_click(self, *args): 
    name = self.txtFormsName.getText().strip()
    if name == "":
      msgbox(
        u"Debera indicar un nombre.", 
        getTitle(), 
        messageType=WARNING
      )
      return
    if len(self.__forms)<1:
      msgbox(
        u"No ha definidos forms que guardar.", 
        getTitle(), 
        messageType=WARNING
      )
      return
    fname = self.__currentFile
    if fname == None:
      f = saveFileDialog(u"Select the 'Tags' file to write", initialPath=self.__lastPath)
      if f == None:
        return
      fname = f[0]
    self.saveForms(fname)
    
  def btnFileNew_click(self, *args): 
    if confirmDialog(
      u"¿ Seguro que desea abandonar los cambios ?",
      getTitle(),
      optionType=YES_NO, 
      messageType=QUESTION) != YES:
      return
    self.newForms()
    
  def btnFormDelete_click(self, *args):
    index = self.cboForms.getSelectedIndex()
    if index < 0:
      return
    if confirmDialog(
      u"¿ Seguro que desea eliminar el formulario seleccionado (%s) ?" % self.__forms[index],
      getTitle(), 
      optionType=YES_NO, 
      messageType=QUESTION) != YES:
      return
    del self.__forms[index]
    self.updateFormsUI()
    
  def btnFormAdd_click(self, *args):
    if self.__currentForm == None:
      index = 0
    else:
      index = len(self.__forms)
    formName = inputbox(
      "Form name",
      getTitle(),
      messageType=QUESTION, 
      initialValue="Form %s" % index
    )
    if formName == None:
      return
    form = Form(formName)
    self.__forms.append(form)
    self.updateFormsUI()
    self.cboForms.setSelectedIndex(len(self.__forms)-1)

  def btnFormRename_click(self, *args):
    index = self.cboForms.getSelectedIndex()
    if index < 0:
      return
    formName = inputbox(
      "Form name",
      getTitle(),
      messageType=QUESTION, 
      initialValue=self.__currentForm.getName()
    )
    if formName == None:
      return
    self.__forms[index].setName(formName)
    self.updateFormsUI()
    self.cboForms.setSelectedIndex(index)

  def btnFormItemUp_click(self, *args):
    index = self.lstFormItems.getSelectedIndex()
    if index < 1:
      return
    form = self.__currentForm
    items = form.items()
    x = items[index]
    del items[index]
    items.insert(index-1,x)
    self.updateListOfFormItems(form)
    self.lstFormItems.setSelectedIndex(index-1)
    
  def btnFormItemDown_click(self, *args):
    form = self.__currentForm
    items = form.items()
    index = self.lstFormItems.getSelectedIndex()
    if index >= len(items)-1:
      return
    x = items[index]
    del items[index]
    items.insert(index+1,x)
    self.updateListOfFormItems(form)
    self.lstFormItems.setSelectedIndex(index+1)
    
  def btnFormItemDelete_click(self, *args):
    index = self.lstFormItems.getSelectedIndex()
    if index < 0:
      return
    if confirmDialog(
      u"¿ Seguro que desea eliminar el elemento seleccionado ?",
      getTitle(), 
      optionType=YES_NO, 
      messageType=QUESTION) != YES:
      return
    form = self.__currentForm
    items = form.items()
    del items[index]
    self.updateListOfFormItems(form)
    self.lstFormItems.setSelectedIndex(index)
    
  def btnFormItemAdd_click(self, *args):
    popup = self.createFormItemAddPopup()
    p=self.btnFormItemAdd.getLocationOnScreen()
    popup.show(self.asJComponent(),0,0)
    popup.setLocation(p.x+((self.btnFormItemAdd.getWidth()/4)*3),p.y+self.btnFormItemAdd.getHeight())

  def btnHelp_click(self,*args):
    controller = SwingController()
    controller.setIsEmbeddedComponent(True)
    controller.openDocument(File(getResource(__file__, "doc", "mobileforms.pdf")).toURI().toURL())  
    pdfPanel = SwingViewBuilder(controller).buildViewerPanel()
    windowManager = ToolsSwingLocator.getWindowManager()
    windowManager.showWindow(pdfPanel,getTitle(), windowManager.MODE.WINDOW)


def showDesigner():

    fixFormPanelResourceLoader()
    
    initDataFolder()
    
    registerFactory(MobileFormItemUnknownFactory())
    registerFactory(MobileFormItemBooleanFactory())
    registerFactory(MobileFormItemStringFactory())
    registerFactory(MobileFormItemDoubleFactory())
    registerFactory(MobileFormItemDateFactory())
    registerFactory(MobileFormItemIntegerFactory())
    registerFactory(MobileFormItemStringComboFactory())
    registerFactory(MobileFormItemMultiStringComboFactory())
    registerFactory(MobileFormItemTimeFactory())
    registerFactory(MobileFormItemSketchFactory())
    registerFactory(MobileFormItemPicturesFactory())
    registerFactory(MobileFormItemHiddenFactory())
    registerFactory(MobileFormItemPrimaryKeyFactory())
    registerFactory(MobileFormItemLabelFactory())
    registerFactory(MobileFormItemLabelWithLineFactory())
    registerFactory(MobileFormItemDynamicStringFactory())
    registerFactory(MobileFormItemConnectedStringComboFactory())
    
    designer = Designer()
    designer.showWindow(getTitle())
    
        
def main(*args):
  showDesigner()
  
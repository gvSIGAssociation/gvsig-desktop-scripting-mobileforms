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
from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.webbrowser import WebBrowserFactory
import jarray
import os

from org.icepdf.ri.common import SwingController
from org.icepdf.ri.common import SwingViewBuilder

from addons.mobileforms.patchs.fixformpanel import fixFormPanelResourceLoader
from addons.mobileforms.mobileformsutil import getTitle
from addons.mobileforms.mobileformsutil import getDataFolder
from addons.mobileforms.mobileformsutil import initDataFolder
from addons.mobileforms.items.item import MobileFormItemUnknown
from addons.mobileforms.factories import getFactories
from addons.mobileforms.factories import registerFactory
from addons.mobileforms.form import Form
from addons.mobileforms.form import Section
from addons.mobileforms.form import Sections
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
from addons.mobileforms.items.map.item import MobileFormItemMapFactory

from javax.swing import JScrollPane
from javax.swing import JViewport

class TraceFunction(object):
  def __init__(self, fn, name=None):
    self.__fn = fn
    if name == None:
      self.__name = fn.func_name
    else:
      self.__name = name
    
  def __call__(self, *args):
    print "### %s enter" % self.__name, args
    self.__fn(*args)
    print "### %s exit" % self.__name


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
  # pylint: disable=R0904 
  # Too many public methods (%s/%s)
  def __init__(self):
    #self.btnSectionAdd_click = TraceFunction(self.btnSectionAdd_click, "btnSectionAdd_click")
    #self.btnFormAdd_click = TraceFunction(self.btnFormAdd_click, "btnFormAdd_click")
    #self.btnFormDelete_click = TraceFunction(self.btnFormDelete_click, "btnFormDelete_click")
    #self.setForm = TraceFunction(self.setForm)
    #self.setSection = TraceFunction(self.setSection)
    #self.setSections = TraceFunction(self.setSections)
    #self.updateSectionFromUI = TraceFunction(self.updateSectionFromUI)
    #self.updateListOfFormItems = TraceFunction(self.updateListOfFormItems)
    
    FormPanel.__init__(self, getResource(__file__, "designer.xml"))
    self.setPreferredSize(700,500)
    self.__sections = None
    self.__lastItem = None
    self.__lastItemPanel = None
    self.__currentSection = None
    self.__currentForm = None
    self.__lastPath = getDataFolder()
    self.newSections()
    self.tblPreviewForm.getParent().getParent().setBorder(None)
    self.tblPreviewForm.getParent().getParent().setViewportBorder(None)
    self.translateUI()

  def translateUI(self):
    #manager = ToolsSwingLocator.getToolsSwingManager()
    from addons.mobileforms.patchs.fixtranslatecomponent import TranslateComponent as manager
    
    for component in ( self.btnFileNew,
        self.btnFileSave,
        self.btnFileSaveAs,
        self.btnFileOpen,
        self.btnHelp,
        self.lblFile,
        self.lblSection,
        self.lblDescription,
        self.btnSectionDelete,
        self.btnSectionAdd,
        self.btnSectionRename,
        self.btnFormDelete,
        self.btnFormAdd,
        self.btnFormRename,
        self.lblFields,
        self.btnFormItemUp,
        self.btnFormItemDown,
        self.btnFormItemDelete,
        self.btnFormItemAdd,
        self.tabForms
      ):
      manager.translate(component)
      
  def setSections(self, sections):
    self.__sections = sections
    model = DefaultComboBoxModel()
    for section in sections:
      model.addElement(section)
    self.cboSections.setModel(model)
    if len(self.__sections)>0:
      self.setSection(sections[0])
    else:
      self.setSection(None)
      
  def setSection(self, section):    
    self.clearFormPreview()
    self.__lastItem = None
    self.__lastItemPanel = None
    self.__currentSection = section
    self.__currentForm = None
    self.btnSectionDelete.setEnabled(False)
    self.btnSectionAdd.setEnabled(True)
    self.btnSectionRename.setEnabled(False)
    self.btnFormDelete.setEnabled(False)
    self.btnFormAdd.setEnabled(False)
    self.btnFormRename.setEnabled(False)
    self.btnFormItemAdd.setEnabled(False)
    self.btnFormItemDelete.setEnabled(False)
    self.btnFormItemDown.setEnabled(False)
    self.btnFormItemUp.setEnabled(False)
    self.lstFormItems.getModel().clear()
    self.pnlItem.removeAll()
    self.pnlItem.revalidate()
    self.setForm(None)

    if section!=None:
      self.cboSections.setSelectedItem(section)
      self.txtSectionDescription.setText(section.getDescription())
      self.btnSectionDelete.setEnabled(True)
      self.btnSectionRename.setEnabled(True)
      self.btnFormAdd.setEnabled(True)
      model = DefaultComboBoxModel()
      for form in section:
        model.addElement(form)
      self.cboForms.setModel(model)
      model = DefaultListModel()
      for form in section:
        model.addElement(form)
      self.lstPreviewForms.setModel(model)

      if len(section)>0:
        self.setForm(section[0])

  def loadSections(self, fname):
    sections = Sections()
    sections.load(fname)
    self.setSections(sections)
    self.__lastPath = os.path.dirname(fname)
    self.btnFileSave.setEnabled(True)
    self.txtPathName.setText(self.__sections.getFilename())
    unsupported = dict()
    for section in sections:
      for form in section:
        for item in form.items():
          if isinstance(item,MobileFormItemUnknown):
            unsupported[item.getRealType()]=item.getRealType()
     
    if len(unsupported)>0:
      i18n = ToolsLocator.getI18nManager()
      msgbox(
        i18n.getTranslation("_Some_elements_are_not_supported")+"\n"+
          i18n.getTranslation("_Save_in_another_file_to_avoid_losing_those_values")+"\n"+
          str(unsupported.values()), 
        getTitle(), 
        messageType=WARNING
      )
      self.__sections.setFilename(None)
            
  def saveSections(self, fname):
    self.updateSectionFromUI()
    self.__sections.save(fname)
    self.__lastPath = os.path.dirname(fname)
  
  def newSections(self):
    self.__sections = None
    self.btnFormDelete.setEnabled(False)
    self.txtPathName.setText("")
    self.setSections(Sections())

  def updateSectionFromUI(self):
    if self.__currentSection==None:
      self.setSections(self.__sections)
      return
    section = self.__currentSection
    self.__currentSection.setDescription(self.txtSectionDescription.getText().strip())
    self.fetchLastItemValues()
    self.setSections(self.__sections)
    self.setSection(section)
  
  def setForm(self, form):
    self.__currentForm = form
    self.__lastItem = None
    self.__lastItemPanel = None
    self.btnFormDelete.setEnabled(False)
    self.btnFormRename.setEnabled(False)
    self.btnFormItemAdd.setEnabled(False)
    self.btnFormItemDelete.setEnabled(False)
    self.btnFormItemDown.setEnabled(False)
    self.btnFormItemUp.setEnabled(False)
    self.lstFormItems.getModel().clear()
    self.pnlItem.removeAll()
    self.pnlItem.revalidate()
    self.tableSetVisible(self.tblPreviewForm,False)
   
    self.updateListOfFormItems(form)

    if form!=None:
      index = self.__currentSection.find(form)
      if index>=0:
        self.btnFormDelete.setEnabled(True)
        self.btnFormRename.setEnabled(True)
        self.btnFormItemAdd.setEnabled(True)
        self.lstPreviewForms.setSelectedValue(form,True)
        self.cboForms.setEnabled(False)
        self.cboForms.setSelectedIndex(index)
        self.cboForms.setEnabled(True)
        if not form.isEmpty():
          self.tableSetVisible(self.tblPreviewForm,True)

  def createFormItemAddPopup(self):
    popup = JPopupMenu()
    for factory in getFactories():
      if factory.getID()!="unknown":
        entry = JMenuItem(factory.getName())
        entry.addActionListener(FormItemAddListener(self,factory))
        popup.add(entry)
    return popup

  def updateListOfFormItems(self, form):
    isEnabled=self.lstFormItems.isEnabled()
    try:
      self.lstFormItems.setEnabled(False)

      self.btnFormItemDelete.setEnabled(False)
      self.btnFormItemUp.setEnabled(False)
      self.btnFormItemDown.setEnabled(False)
      self.btnFormItemAdd.setEnabled(False)
      model = DefaultListModel()
      if form!=None:
        for item in form:
          model.addElement(item)
      self.lstFormItems.setModel(model)
      self.lstFormItems.setSelectedIndex(-1)
    
    finally:  
      self.lstFormItems.setEnabled(isEnabled)

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
    
  def cboSections_click(self,*args):
    section = self.cboSections.getSelectedItem()
    if section == None:
      return
    self.updateSectionFromUI()
    self.setSection(section)      
    
  def cboForms_click(self,*args):
    if not self.cboForms.isEnabled():
      return
    form = self.cboForms.getSelectedItem()
    if form == None:
      return
    self.setForm(form)
    
  def lstFormItems_change(self, event):
    if not self.lstFormItems.isEnabled() or event.getValueIsAdjusting() :
      return
    self.pnlItem.removeAll()
    item = self.lstFormItems.getSelectedValue()
    if item == None:
      self.pnlItem.revalidate()
      return 
    self.btnFormItemDelete.setEnabled(True)
    self.btnFormItemUp.setEnabled(True)
    self.btnFormItemDown.setEnabled(True)
    self.btnFormItemAdd.setEnabled(True)
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
    if form == None or form.isEmpty():
      self.tableSetVisible(self.tblPreviewForm,False)
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
    self.tableSetVisible(self.tblPreviewForm,True)
    self.cboForms.setSelectedItem(form)

  def tableSetVisible(self, table, isVisible):
    parent = table.getParent()
    if isinstance(parent,JViewport):
      parent = parent.getParent()
    if isinstance(parent,JScrollPane):
      parent.setVisible(isVisible)
    else:
      table.setVisible(isVisible)
      
  def btnFileOpen_click(self, *args):
    i18n = ToolsLocator.getI18nManager()
    f = openFileDialog(
      i18n.getTranslation("_Select_the_Tags_file_to_open"), 
      initialPath=self.__lastPath
    )
    if f == None:
      return
    self.loadSections(f[0])
    
  def btnFileSave_click(self, *args): 
    i18n = ToolsLocator.getI18nManager()
    if self.__sections==None or len(self.__sections)<1:
      msgbox(
        i18n.getTranslation("_You_must_define_some_section_before_saving"), 
        getTitle(), 
        messageType=WARNING
      )
      return
    if self.__currentSection==None or len(self.__currentSection)<1:
      msgbox(
        i18n.getTranslation("_You_must_define_some_form_before_saving"), 
        getTitle(), 
        messageType=WARNING
      )
      return
    fname = self.__sections.getFilename()
    if fname == None:
      f = saveFileDialog(
        i18n.getTranslation("_Select_the_Tags_file_to_write"), 
        initialPath=self.__lastPath
      )
      if f == None:
        return
      fname = f[0]
    self.updateSectionFromUI()
    self.saveSections(fname)
    
  def btnFileSaveAs_click(self, *args): 
    i18n = ToolsLocator.getI18nManager()
    if self.__sections==None or len(self.__sections)<1:
      msgbox(
        i18n.getTranslation("_You_must_define_some_section_before_saving"), 
        getTitle(), 
        messageType=WARNING
      )
      return
    if self.__currentSection==None or len(self.__currentSection)<1:
      msgbox(
        i18n.getTranslation("_You_must_define_some_form_before_saving"), 
        getTitle(), 
        messageType=WARNING
      )
      return
    f = saveFileDialog(
      i18n.getTranslation("_Select_the_Tags_file_to_write"), 
      initialPath=self.__lastPath
    )
    if f == None:
      return
    fname = f[0]
    self.updateSectionFromUI()
    self.saveSections(fname)
    
  def btnFileNew_click(self, *args): 
    i18n = ToolsLocator.getI18nManager()
    if confirmDialog(
      i18n.getTranslation("_Are_you_sure_you_want_to_abandon_the_changes"),
      getTitle(),
      optionType=YES_NO, 
      messageType=QUESTION) != YES:
      return
    self.newSections()

  def btnSectionAdd_click(self, *args):
    i18n = ToolsLocator.getI18nManager()
    if self.__currentSection == None:
      index = 0
    else:
      index = len(self.__sections)
    name = inputbox(
      i18n.getTranslation("_Section_name"),
      getTitle(),
      messageType=QUESTION, 
      initialValue=i18n.getTranslation("_Section_%s") % index
    )
    if name == None:
      return
    section = Section(name)
    self.__sections.append(section)
    self.updateSectionFromUI()
    self.cboSections.setSelectedIndex(len(self.__sections)-1)
    
  def btnSectionRename_click(self, *args):
    i18n = ToolsLocator.getI18nManager()
    index = self.cboSections.getSelectedIndex()
    if index < 0:
      return
    name = inputbox(
      i18n.getTranslation("_Section_name"),
      getTitle(),
      messageType=QUESTION, 
      initialValue=self.__currentSection.getName()
    )
    if name == None:
      return
    self.__sections[index].setName(name)
    self.updateSectionFromUI()
    self.cboSections.setSelectedIndex(index)
    
  def btnSectionDelete_click(self, *args):
    i18n = ToolsLocator.getI18nManager()
    index = self.cboSections.getSelectedIndex()
    if index < 0:
      return
    if confirmDialog(
      i18n.getTranslation("_Are_you_sure_you_want_to_delete_the_selected_section_%s") % self.__sections[index],
      getTitle(), 
      optionType=YES_NO, 
      messageType=QUESTION) != YES:
      return
    del self.__sections[index]
    self.__currentSection = None
    self.updateSectionFromUI()
    
    
  def btnFormDelete_click(self, *args):
    i18n = ToolsLocator.getI18nManager()
    index = self.cboForms.getSelectedIndex()
    if index < 0:
      return
    if confirmDialog(
      i18n.getTranslation("_Are_you_sure_you_want_to_delete_the_selected_form_%s") % self.__currentSection[index],
      getTitle(), 
      optionType=YES_NO, 
      messageType=QUESTION) != YES:
      return
    del self.__currentSection[index]
    self.updateSectionFromUI()
    
  def btnFormAdd_click(self, *args):
    i18n = ToolsLocator.getI18nManager()
    if self.__currentForm == None:
      index = 0
    else:
      index = len(self.__currentSection)
    formName = inputbox(
      i18n.getTranslation("_Form_name"),
      getTitle(),
      messageType=QUESTION, 
      initialValue=i18n.getTranslation("_Form_%s") % index
    )
    if formName == None:
      return
    form = Form(formName)
    self.__currentSection.append(form)
    self.updateSectionFromUI()
    self.cboForms.setSelectedIndex(len(self.__currentSection)-1)

  def btnFormRename_click(self, *args):
    i18n = ToolsLocator.getI18nManager()
    index = self.cboForms.getSelectedIndex()
    if index < 0:
      return
    formName = inputbox(
      i18n.getTranslation("_Form_name"),
      getTitle(),
      messageType=QUESTION, 
      initialValue=self.__currentForm.getName()
    )
    if formName == None:
      return
    self.__currentSection[index].setName(formName)
    self.updateSectionFromUI()
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
    i18n = ToolsLocator.getI18nManager()
    index = self.lstFormItems.getSelectedIndex()
    if index < 0:
      return
    if confirmDialog(
      i18n.getTranslation("_Are_you_sure_you_want_to_delete_the_selected_item"),
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
    #controller = SwingController()
    #controller.setIsEmbeddedComponent(True)
    #controller.openDocument(File(getResource(__file__, "doc", "mobileforms.pdf")).toURI().toURL())  
    #panel = SwingViewBuilder(controller).buildViewerPanel()
    panel = WebBrowserFactory.createWebBrowserPanel()
    panel.setPage(File(getResource(__file__, "doc", "mobileforms.html")).toURI().toURL())
    windowManager = ToolsSwingLocator.getWindowManager()
    windowManager.showWindow(panel,getTitle(), windowManager.MODE.WINDOW)

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
    registerFactory(MobileFormItemMapFactory())
    
    designer = Designer()
    designer.showWindow(getTitle())
    
        
def main(*args):
  
  #i18nManager = ToolsLocator.getI18nManager()
  #i18nManager.addResourceFamily("text",File(getResource(__file__,"i18n")))

  showDesigner()
  
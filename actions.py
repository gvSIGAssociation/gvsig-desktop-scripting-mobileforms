# encoding: utf-8

import gvsig

from gvsig import getResource

from java.io import File
from org.gvsig.andami import PluginsLocator
from org.gvsig.app import ApplicationLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from addons.mobileforms.designer import showDesigner

class MobileFormsExtension(ScriptingExtension):
  def __init__(self):
    pass

  def canQueryByAction(self):
    return True

  def isEnabled(self,action):
    return True

  def isVisible(self,action):
    return True
    
  def execute(self,actionCommand, *args):
    actionCommand = actionCommand.lower()
    if actionCommand == "mobile-forms-designer":
      showDesigner()

def selfRegister():
  application = ApplicationLocator.getManager()

  #
  # Registramos las traducciones
  i18n = ToolsLocator.getI18nManager()
  i18n.addResourceFamily("text",File(getResource(__file__,"i18n")))

  #
  # Registramos los iconos en el tema de iconos
  icon = File(getResource(__file__,"images","mobile-forms-designer.png")).toURI().toURL()
  print "ICON:", icon
  iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
  iconTheme.registerDefault("scripting.MobileFormsExtension", "action", "mobile-forms-designer", None, icon)

  #
  # Creamos la accion 
  extension = MobileFormsExtension()
  actionManager = PluginsLocator.getActionInfoManager()
  action = actionManager.createAction(
    extension, 
    "mobile-forms-designer", # Action name
    "Mobile forms designer", # Text
    "mobile-forms-designer", # Action command
    "mobile-forms-designer", # Icon name
    None, # Accelerator
    650151000, # Position 
    "_Show_mobile_forms_designer" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, "HMachine/GvSIG Mobile-Geopaparazzi/Forms designer")
  
def test():
  pass
      

# encoding: utf-8

import gvsig

from com.jeta.open.registry import JETARegistry
from com.jeta.open.resources import ResourceLoader, AppResourceLoader
from jarray import array
from java.net import URLClassLoader
from java.net import URL

from org.gvsig.scripting import ScriptingLocator

class FormPanelResourceLoader(AppResourceLoader):
  def __init__(self, url):
    AppResourceLoader.__init__(self)
    classloader = URLClassLoader(array((url,), URL))
    self.setClassLoader(classloader)

  def loadImage(self, imageName):
    url = AppResourceLoader.loadImage(self, imageName)
    return url
    
def fixFormPanelResourceLoader():
  appResourceLoader = JETARegistry.lookup(ResourceLoader.COMPONENT_ID)
  if not isinstance(appResourceLoader,FormPanelResourceLoader):
    # Ojo, si no llamamos a este initialize, la primera vez
    # que se carga un formulario no carga los recursos
    from com.jeta.forms.defaults import DefaultInitializer
    DefaultInitializer.initialize()

    url = ScriptingLocator.getManager().getUserFolder().getFile().toURL()
    formPanelResourceLoader = FormPanelResourceLoader(url)
    JETARegistry.rebind(ResourceLoader.COMPONENT_ID, formPanelResourceLoader)


# encoding: utf-8

import gvsig

from javax.swing import AbstractButton
from javax.swing import JLabel
from javax.swing import JTabbedPane
from org.apache.commons.lang3 import StringUtils
from org.gvsig.tools import ToolsLocator

class TranslateComponent(object):

  @staticmethod
  def translate(component):
    #print "translate", component
    
    i18n = ToolsLocator.getI18nManager()
    if isinstance(component,AbstractButton):
      s = component.getText();
      if not StringUtils.isEmpty(s):
        component.setText(i18n.getTranslation(s))
      s = component.getToolTipText()
      if not StringUtils.isEmpty(s):
        component.setToolTipText(i18n.getTranslation(s))
  
    elif isinstance(component,JLabel):
      s = component.getText()
      if not StringUtils.isEmpty(s):
        component.setText(i18n.getTranslation(s))
      s = component.getToolTipText()
      if not StringUtils.isEmpty(s):
        component.setToolTipText(i18n.getTranslation(s))
    
    elif isinstance(component,JTabbedPane):
      for i in range(0,component.getTabCount()):
        text = component.getTitleAt(i)
        if not StringUtils.isEmpty(text):
          component.setTitleAt(i, i18n.getTranslation(text))
        text = component.getToolTipTextAt(i)
        if not StringUtils.isEmpty(text):
          component.setToolTipTextAt(i, i18n.getTranslation(text))
    else:
      print "Component not supportted"
      
def main(*args):
  manager = TranslateComponent
  manager.translate(None)
  
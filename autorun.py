# encoding: utf-8

import gvsig

from gvsig import getResource
from java.io import File
from org.gvsig.tools import ToolsLocator

from addons.mobileforms.actions import selfRegister

def main(*args):
  selfRegister()

  i18nManager = ToolsLocator.getI18nManager()
  i18nManager.addResourceFamily("text",File(getResource(__file__,"i18n")))

# encoding: utf-8

import gvsig


from gvsig import getResource
from org.gvsig.scripting import ScriptingLocator
import os
import shutil

def getDataFolder():
  return ScriptingLocator.getManager().getDataFolder("mobileforms").getAbsolutePath()

def initDataFolder():
    dataFolder = getDataFolder()
    for fname in  ("example_tags.json","Egypt_usecase_tags.json"):
      pathname = os.path.join(dataFolder,fname)
      if not os.path.exists(pathname) :
        shutil.copy(getResource(__file__,"data",fname), pathname)

def getTitle():
  return "Mobile forms designer"
  
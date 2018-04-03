# encoding: utf-8

import gvsig
from collections import OrderedDict

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

from addons.mobileforms.mobileformsutil import isEmpty

class MobileFormItemFactory(object):
  def __init__(self, id, name=None):
    self.__id = id
    if name == None:
      self.__name = id
    else:
      self.__name = name

  def getID(self):
    return self.__id

  def getName(self):
    return self.__name

  def create(self):
    return None

  def createPreviewPanel(self):
    return None
    
  def createPropertiesPanel(self):
    return None
    
class MobileFormItem(object):
  def __init__(self, factory, key=None, label=None, mandatory=False):
    self.__factory = factory
    self.__key = key
    self.__label = label
    self.__isLabel = False
    self.__mandatory = mandatory

  def __str__(self):
    key = self.getKey()
    if isEmpty(key):
      return self.getType()
    return "%s [%s]" % (key, self.getType())

  __repr__ = __str__
  
  def getFactory(self):
    return self.__factory
    
  def getType(self):
    return self.__factory.getID()

  def getKey(self):
    return self.__key

  def setKey(self, key):
    #print "setKey(%s)" % key
    self.__key = key

  def getLabel(self):
    return self.__label

  def setLabel(self, label):
    #print "setLabel(%s)" % label
    self.__label = label

  def isMandatory(self):
    return self.__mandatory

  def getCaption(self):
    caption = self.getLabel()
    if not isEmpty(caption):
      return caption
    caption = self.getKey()
    if not isEmpty(caption):
      return caption.strip()
    return ""

  def setMandatory(self, mandatory):
    if mandatory in ( True, False):
      self.__mandatory = mandatory
    elif mandatory == None:
      self.__mandatory = False
    else:
      self.__mandatory =  (str(mandatory).lower() == "yes")
    #print "setMandatory(%s)" % self.__mandatory
  
  def setIsLabel(self, isLabel):
    if isLabel in (True, False):
      self.__isLabel = isLabel
    elif isLabel == None:
      self.__isLabel = False
    else:
      self.__isLabel =  (str(isLabel).lower() == "true")
    #print "setIsLabel(%s)" % self.__isLabel

  def isLabel(self):
    return self.__isLabel
          
  def fromDict(self, item):
    self.setKey(item.get("key",None))
    self.setLabel(item.get("label", None))
    self.setMandatory(item.get("mandatory", None))
    self.setIsLabel(item.get("islabel",None))

  def asDict(self):
    d = OrderedDict()
    d["type"] = self.getFactory().getID()
    if not isEmpty(self.getKey()):
      d["key"] = self.getKey()
    if self.isLabel():
      d["islabel"] = "true"
    if not isEmpty(self.getLabel()):
      d["label"] = self.getLabel()
    if self.isMandatory():
      d["mandatory"] = "yes"
    return d
    
class MobileFormItemPanel(object):
  def __init__(self, factory):
    self.__factory = factory
  
  def getFactory(self):
    return self.__factory
    
  def getType(self):
    return self.__factory.getID()

  def put(self, item):
    pass

  def fetch(self,item):
    pass

  
class MobileFormItemUnknownFactory(MobileFormItemFactory):
  def __init__(self):
    MobileFormItemFactory.__init__(self,"unknown","Unknown")

  def create(self):
    return MobileFormItemUnknown(self)


class MobileFormItemUnknown(MobileFormItem):
  def __init__(self, factory, label=None):
    MobileFormItem.__init__(self,factory, label)
    self.__values = dict()

  def getRealType(self):
    t = self.__values.get("type",None)
    if t == None:
      return "unknown"
    return t
  
  def getType(self):
    t = self.__values.get("type",None)
    if t == None:
      return "unknown"
    return "unnown(%s)" % t
    
  def fromDict(self, item):
    MobileFormItem.fromDict(self,item)    
    self.__values = dict()
    self.__values.update(item)

  def asDict(self):
    return self.__values


    
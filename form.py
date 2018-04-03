# encoding: utf-8

import gvsig

import json
from collections import OrderedDict

from addons.mobileforms.factories import getFactory

class Sections(list):
  def __init__(self):
    list.__init__(self)
    self.__fname = None

  def load(self,fname):
    f = open(fname,"r")
    rawjson = f.read()
    f.close()
    for rawsection in json.loads(rawjson, object_pairs_hook=OrderedDict):
      section = Section()
      section.fromDict(rawsection)
      self.append(section)
    self.__fname = fname

  def save(self, fname=None):
    if fname == None:
      fname = self.__fname
    if fname == None:
      raise ValueError("Sections.save can need a file name to save the data")
    rawsections = list()
    for section in self:
      rawsection = section.asDict()
      rawsections.append(rawsection)
    rawjson = json.dumps(
      rawsections, 
      sort_keys=False,
      indent=2, 
      separators=(',', ': ')
    )
    f = open(fname,"w")
    f.write(rawjson)
    f.close()
    self.__fname = fname

  def getFilename(self):
    return self.__fname

  def setFilename(self, fname):
    self.__fname = fname

class Section(object):
  def __init__(self, name=None, description=None):
    self.__name = name
    self.__description = description
    self.__forms = list()

  def getName(self):
    return self.__name

  def __str__(self):
    return self.__name

  __repr__ = __str__

  def setName(self,name):
    self.__name = name

  def getDescription(self):
    return self.__description

  def setDescription(self,description):
    self.__description = description

  def forms(self):
    return self.__forms

  def append(self, form):
    self.__forms.append(form)

  def __delitem__(self, index):
    del self.__forms[index]

  def __getitem__(self, index):
    return self.__forms[index]

  def __len__(self):
    return len(self.__forms)
    
  def __iter__(self):
    return self.__forms.__iter__()

  def find(self, form):
    if form==None:
      return -1
    try:
      return self.__forms.index(form)
    except:
      return -1
  
  def fromDict(self, rawsection):
    self.__name = rawsection["sectionname"]
    self.__description = rawsection["sectiondescription"]
    self.__forms = list()
    for rawform in rawsection["forms"]:
      form = Form()
      form.fromDict(rawform)
      self.__forms.append(form)

  def asDict(self):
    rawsection = OrderedDict()
    rawsection["sectionname"] = self.getName()
    rawsection["sectiondescription"] = self.getDescription()
    rawforms = list()
    for form in self.__forms:
      rawforms.append(form.asDict())
    rawsection["forms"] = rawforms  
    return rawsection

class Form(object):
  def __init__(self, name=""):
    self.__name = name
    self.__items = list()

  def __str__(self):
    return self.__name

  __repr__ = __str__

  def setName(self,name):
    self.__name = name

  def getName(self):
    return self.__name

  def asDict(self):
    rawform = OrderedDict()
    rawform["formname"] = self.__name
    rawitems = list()
    for item in self.__items:
      rawitems.append(item.asDict())
    rawform["formitems"] = rawitems
    return rawform
    
  def fromDict(self,rawform):
    self.__name = rawform["formname"]
    for rawitem in rawform["formitems"]:
      id = rawitem.get("type","Unknown")
      factory = getFactory(id)
      item = factory.create()
      item.fromDict(rawitem)
      self.__items.append(item)

  def __getitem__(self, index):
    return self.__items[index]
    
  def items(self):
    return self.__items

  def __iter__(self):
    return self.__items.__iter__()
    
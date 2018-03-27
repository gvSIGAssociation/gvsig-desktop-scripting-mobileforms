# encoding: utf-8

import gvsig

import json
from collections import OrderedDict

from addons.mobileforms.factories import getFactory

class Forms(object):
  def __init__(self):
    self.__name = None
    self.__description = None
    self.__forms = list()

  def getName(self):
    return self.__name

  def __str__(self):
    return self.__name

  __repr__ = __str__

  def load(self,fname):
    f = open(fname,"r")
    s = f.read()
    f.close()
    #d = eval(s)[0]
    #print "eval", d
    d = json.loads(s, object_pairs_hook=OrderedDict)[0]
    #print "json.loads", d
    self.fromDict(d)

  def save(self, fname):
    d = OrderedDict()
    d["sectionname"] = self.getName()
    d["sectiondescription"] = self.getDescription()
    forms = list()
    for form in self.__forms:
      forms.append(form.asDict())
    d["forms"] = forms  
    s = json.dumps(
      [ d ], 
      sort_keys=False,
      indent=2, 
      separators=(',', ': ')
    )
    f = open(fname,"w")
    f.write(s)
    f.close()
            
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
  
  def fromDict(self, d):
    self.__name = d["sectionname"]
    self.__description = d["sectiondescription"]
    self.__forms = list()
    for x in d["forms"]:
      f = Form()
      f.fromDict(x)
      self.__forms.append(f)

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
    d = OrderedDict()
    d["formname"] = self.__name
    items = list()
    for item in self.__items:
      items.append(item.asDict())
    d["formitems"] = items
    return d
    
  def fromDict(self,form):
    self.__name = form["formname"]
    for x in form["formitems"]:
      id = x.get("type","Unknown")
      factory = getFactory(id)
      item = factory.create()
      item.fromDict(x)
      self.__items.append(item)

  def __getitem__(self, index):
    return self.__items[index]
    
  def items(self):
    return self.__items

  def __iter__(self):
    return self.__items.__iter__()
    
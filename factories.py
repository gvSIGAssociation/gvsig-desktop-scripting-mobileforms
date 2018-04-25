# encoding: utf-8

import gvsig

factories = dict()

def registerFactory(factory):
  factories[factory.getID()] = factory  

def getFactories():
  l = factories.values()
  l.sort()
  return l
  
def getFactory(id):
  factory = factories.get(id,None)
  if factory == None:
    factory = factories.get("unknown")
    #print "!!! getFactory(%s) None, factories %s" % (id, repr(factories))
  return factory



  
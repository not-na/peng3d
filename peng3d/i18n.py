#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  i18n.py
#  
#  Copyright 2018 notna <notna@apparat.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

__all__ = [
    "TranslationManager",
]

import glob
import re

from .util import ActionDispatcher

class TranslationManager(ActionDispatcher):
    def __init__(self,peng):
        if not peng.cfg["rsrc.enable"]:
            raise RuntimeError("ResourceManager needs to be enabled to use Translations")
        elif peng.rsrcMgr is None:
            raise RuntimeError("ResourceManager needs to be initialized before TranslationManager")
        
        self.peng = peng
        
        self.lang = self.peng.cfg["i18n.lang"]
        
        self.cache = {} # dict of dicts, first lang, then domain
        
        self.peng.sendEvent("peng3d:i18n.init",{"lang":self.lang,"i18n":self})
        self.setLang(self.peng.cfg["i18n.lang"])
    
    def setLang(self,lang):
        self.lang = lang
        self.peng.cfg["i18n.lang"] = lang
        
        if lang not in self.cache:
            self.cache[lang]={}
        
        self.doAction("setlang")
        self.peng.sendEvent("peng3d:i18n.set_lang",{"lang":self.lang,"i18n":self})
    
    def discoverLangs(self,domain="*"):
        rsrc = self.peng.cfg["i18n.lang.format"].format(domain=domain,lang="*")
        pattern = self.peng.rsrcMgr.resourceNameToPath(rsrc,self.peng.cfg["i18n.lang.ext"])
        files = glob.iglob(pattern)
        
        langs = set()
        r = re.compile(self.peng.cfg["i18n.discover_regex"])
        
        for f in files:
            m = r.fullmatch(f)
            if m is not None:
                langs.add(m.group("lang"))
        
        return list(langs)
    
    def translate(self,key,translate=True,lang=None):
        if lang is None:
            lang = self.lang
        
        if not translate or key.count(":")!=1:
            return key
        domain,name = key.split(":")
        
        if domain not in self.cache[lang]:
            self.loadDomain(domain,lang)
        if name not in self.cache[lang][domain]:
            return key # would just display the key to the user, good enough to be understood
        return self.cache[lang][domain][name]
    t = translate
    def translate_lazy(self,key,translate=True,lang=None):
        return _LazyTranslator(self,key,translate,lang)
    tl = translate_lazy
    
    def loadDomain(self,domain,lang=None):
        if lang is None:
            lang = self.lang
        
        if lang not in self.cache:
            self.cache[lang][domain]={} # prevents errors if function aborts prematurely
        
        rsrc = self.peng.cfg["i18n.lang.format"].format(domain=domain,lang=lang)
        if not self.peng.rsrcMgr.resourceExists(rsrc,self.peng.cfg["i18n.lang.ext"]):
            return # prevents errors
        fname = self.peng.rsrcMgr.resourceNameToPath(rsrc,self.peng.cfg["i18n.lang.ext"])
        try:
            with open(fname,"r") as f:
                data = f.readlines()
        except Exception:
            return # prevents errors
        
        d = {}
        for line in data:
            line.strip()
            if line=="" or line.startswith("#"):
                continue
            ls = line.split("=")
            k = ls.pop(0) # first ever useful application of pop
            v = "=".join(ls).strip()
            d[k]=v
        self.cache[lang][domain]=d
        
        self.doAction("loaddomain")
    
    def __getitem__(self,key):
        return self.translate(key)

class _LazyTranslator(object):
    _dynamic=True
    def __init__(self,i18n,key,translate=True,lang=None):
        self.i18n = i18n
        self.key = key
        self.translate = translate
        self.lang = lang
    def __str__(self):
        return self.i18n.translate(self.key,self.translate,self.lang)
    def __repr__(self):
        return self.i18n.translate(self.key,self.translate,self.lang)
    def __mod__(self,other):
        try:
            return str(self)%other
        except Exception:
            return str(self)
    def format(self,*args,**kwargs):
        try:
            return str(self).format(*args,**kwargs)
        except Exception:
            return str(self)

# -*- coding: utf-8 -*-
'''
Created on 20 févr. 2015

@author: briner
'''
import logging
import re

import mexecutor

my_logger=logging.getLogger('MyLogger')

RE_UPGRADE_STR="^(\d+)\s+(\S+)$"
RE_UPGRADE=re.compile(RE_UPGRADE_STR)

_LEN_OF_ZONE_LIST_ENTRY=10
class CmdZpoolList(mexecutor.ShellCmdWrapped):
    def __new__(self, lzpoolname_or_zpoolname=[]):
        if list == type(lzpoolname_or_zpoolname):
            return str.__new__(self, "zpool list -H %s" % ",".join(lzpoolname_or_zpoolname))
        else:
            return str.__new__(self, "zpool list -H %s" % lzpoolname_or_zpoolname)
    def __init__(self, lzpoolname_or_zpoolname):
        if list == type(lzpoolname_or_zpoolname):
            super(CmdZpoolList, self).__init__("zpool list -H" % ",".join(lzpoolname_or_zpoolname))
        else:
            super(CmdZpoolList, self).__init__("zpool list -H %s" % lzpoolname_or_zpoolname)
    with_construct=True
    def _factory(self,shell_result):
        '''call by Factor'''
        if shell_result.status != 0:
            my_logger.error('the cmd (%s) did not succeed' % self)
            return []
        #
        # parse
        lret=[]
        for line in shell_result.stdout:
            lelem=line.split("\t")
            zpool=Zpool(*lelem)
            lret.append(zpool)
        return lret

class Zpool(object):
    def __init__(self, name, size, alloc, free, cap, dedup, health, altroot):
        self.name=name
        self.size=size
        self.alloc=alloc
        self.free=free
        self.cap=cap
        self.dedup=dedup
        self.healt=health
        self.altroot=altroot
    def __repr__(self):
        return "zpool(%s)" % (self.name)
    @classmethod
    def add_method(cls, name, wrapped_fun):
        fun=wrapped_fun()
#         print "name", name
#         print "wrapped_fun", "type", type(wrapped_fun), "self", wrapped_fun, "dir",dir(wrapped_fun)
#         print "fun", "type", type(fun), "self", fun, "dir",dir(fun)
        setattr(cls, name, fun)
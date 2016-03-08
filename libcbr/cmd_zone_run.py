# -*- coding: utf-8 -*-
'''
Created on 19 févr. 2015

@author: briner
'''

import logging
import re

import mexecutor

my_logger=logging.getLogger('MyLogger')

RE_UPGRADE_STR="^(\d+)\s+(\S+)$"
RE_UPGRADE=re.compile(RE_UPGRADE_STR)

_LEN_OF_ZONE_LIST_ENTRY=10
class CmdZoneRun(mexecutor.ShellCmdWrapped):
    def __new__(self, hostname):
        return str.__new__(self, "zlogin %s hostname" % hostname)
    def __init__(self, hostname):
        super(CmdZoneHostname, self).__init__("zlogin %s hostname" % hostname)
    with_construct=True
    def _factory(self,shell_result):
        '''call by Factor'''
        if shell_result.status != 0:
            my_logger.error('the cmd (%s) did not succeed' % self)
            return []
        hostname=shell_result.stdout[0].rstrip()
        host=Host(hostname)
        return host

class Host(str):
    def __new__(cls, *args, **kw):
        return str.__new__(cls,*args,**kw)
    def __repr__(self):
        return "Host(%s)" % self

def wrapp_hostname():
    "wrapp hostname"
    def fun(self):
        "get hostname"
        exe=mexecutor.Relation.get_exe(self)
        cmd_inst=CmdZoneHostname(self.zonename)
        result=exe.run(cmd_inst)
        return result.outputs
    return fun

from libcbr import cmd_zone_list
cmd_zone_list.Zone.add_method("get_hostname", wrapp_hostname)

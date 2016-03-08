# -*- coding: utf-8 -*-
'''
Created on 4 février. 2015

@author: briner
'''

import logging
import re

import mexecutor

my_logger=logging.getLogger('MyLogger')

RE_UPGRADE_STR="^(\d+)\s+(\S+)$"
RE_UPGRADE=re.compile(RE_UPGRADE_STR)

_LEN_OF_ZONE_LIST_ENTRY=10
class CmdBeadmDestroy(mexecutor.ShellCmdWrapped):
    def __new__(self, bename):
        return str.__new__(self, "beadm destroy -F %s" % bename)
    def __init__(self, bename):
        super(CmdBeadmDestroy, self).__init__("beadm destroy -F %s" % bename)
    with_construct=True
    def _factory(self,shell_result):
        '''call by Factor'''
        if shell_result.status != 0:
            my_logger.error('the cmd (%s) did not succeed' % self)
            return []
        return []

def wrapp_destroy():
    "wrapp destroy"
    def fun(self):
        "destroy"
        exe=mexecutor.Relation.get_exe(self)
        cmd_inst=CmdBeadmDestroy(self.be)
        result=exe.run(cmd_inst)
        return result
    return fun

import cmd_beadm_list
cmd_beadm_list.BeadmListEntry.add_method("destroy", wrapp_destroy)


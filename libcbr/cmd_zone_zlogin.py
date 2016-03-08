# -*- coding: utf-8 -*-
'''
Created on 24 févr. 2015

@author: briner
'''
import logging
import re

import mexecutor

my_logger=logging.getLogger('MyLogger')

RE_UPGRADE_STR="^(\d+)\s+(\S+)$"
RE_UPGRADE=re.compile(RE_UPGRADE_STR)

_LEN_OF_ZONE_LIST_ENTRY=10
class CmdZoneZlogin(mexecutor.ShellCmdWrapped):
    def __new__(self, zonename, cmd_str):
        return str.__new__(self, "zlogin %s %s" % (zonename, cmd_str))
    def __init__(self, zonename, cmd_str):
        super(CmdZoneZlogin, self).__init__("zlogin %s %s" % (zonename, cmd_str))
    with_construct=True
    def _factory(self,shell_result):
        '''call by Factor'''
        if shell_result.status != 0:
            my_logger.error('the cmd (%s) did not succeed' % self)
            return []
        return shell_result.stdout


def wrapp_zlogin():
    "wrapp hostname"
    def fun(self, cmd_str):
        "get hostname"
        exe=mexecutor.Relation.get_exe(self)
        cmd_inst=CmdZoneZlogin(self.zonename, cmd_str)
        result=exe.run(cmd_inst)
        return result.outputs
    return fun

from libcbr import cmd_zone_list
cmd_zone_list.Zone.add_method("zlogin", wrapp_zlogin)
# -*- coding: utf-8 -*-
'''
Created on 27 janv. 2015

@author: briner
'''

import logging
import re

import mexecutor

my_logger=logging.getLogger('MyLogger')

RE_UPGRADE_STR="^(\d+)\s+(\S+)$"
RE_UPGRADE=re.compile(RE_UPGRADE_STR)

_LEN_OF_ZONE_LIST_ENTRY=10
class CmdZfslUpgrade(mexecutor.ShellCmdWrapped):
    def __new__(self):
        return str.__new__(self, "zfs upgrade")
    def __init__(self):
        super(CmdZfsUpgrade, self).__init__("zfs upgrade")
    with_construct=True
    def _factory(self,shell_result):
        '''call by Factor'''
        if shell_result.status != 0:
            my_logger.error('the cmd (%s) did not succeed' % self)
            return []
        lmap_version_zpoolname=[]
        for line in shell_result.stdout:
            match=RE_UPGRADE.search(line)
            if match:
                version,poolname=match.groups()
                poolname_version=PoolnameVersion(poolname, version)
                lmap_version_zpoolname.append(poolname_version)
        return lmap_version_zpoolname

class PoolnameVersion(object):
    def __init__(self, poolname, version):
        self.poolname=poolname
        self.version=version
    def __repr__(self):
        return "pool(%s) version(%s)" % (self.poolname, self.version)


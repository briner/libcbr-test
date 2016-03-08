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
class CmdZpoolList(mexecutor.ShellCmdWrapped):
    def __new__(self):
        return str.__new__(self, "beadm list")
    def __init__(self):
        super(CmdZpoolList, self).__init__("beadm list")
    with_construct=True
    def _factory(self,shell_result):
        '''call by Factor'''
        if shell_result.status != 0:
            my_logger.error('the cmd (%s) did not succeed' % self)
            return []
        #
        # parse
        if not shell_result.stdout > 2:
            return None
        header_line=shell_result.stdout[0]
        seperator_line=shell_result.stdout[1]
        # separator
        lsep_start=[]
        for i, c in enumerate(seperator_line):
            if seperator_line[i-1] != "-" and c=="-":
                lsep_start.append(i)
        lsep_start.append(len(seperator_line))
        # header  
        re_beadm_str="^"
        for i in range(len(lsep_start[:-1])):
            fr=lsep_start[i]
            to=lsep_start[i+1]
            name=header_line[fr:to].rstrip().lower()
            length=to-fr
            re_beadm_str+="(?P<%s>.{%s})" % (name, length)
        re_beadm_str+="$"
        # body
        re_beadm=re.compile(re_beadm_str)
        lret=[]
        for line in shell_result.stdout[2:]:
            ret={}
            for k,v in re_beadm.search(line).groupdict().iteritems():
                ret[k]=v.rstrip()
            lret.append(BeadmListEntry(ret))
        return lret

class BeadmListEntry(object):
    def __init__(self, adict):
        for k,v in adict.iteritems():
            setattr(self, k, v)
    def __repr__(self):
        return "beadm_list_entry(%s)" % (self.be)
    @classmethod
    def add_method(cls, name, wrapped_fun):
        fun=wrapped_fun()
#         print "name", name
#         print "wrapped_fun", "type", type(wrapped_fun), "self", wrapped_fun, "dir",dir(wrapped_fun)
#         print "fun", "type", type(fun), "self", fun, "dir",dir(fun)
        setattr(cls, name, fun)

cmdbeadmlist=CmdZpoolList()
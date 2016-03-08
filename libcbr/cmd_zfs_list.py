# -*- coding: utf-8 -*-
'''
Created on 9 févr. 2015

@author: briner
'''
import logging
import re

import mexecutor

my_logger=logging.getLogger('MyLogger')


ZFS_LIST_CMD_LPROP_VALUE=['name'
                         ,'type'
                         ,'origin'
                         ,'zoned'
                         ,'mountpoint'
                         ,'mounted'
                         ,'readonly'
                         ,'ch.unige:created_by'
                         ,'ch.unige:no_snapshots'
                         ,'ch.unige.dolly:mountpoint'
                         ,'ch.unige.dolly:zone'
                         ,'ch.unige:expiration_datetime'
                         ,'ch.unige.dolly:do_not_keep'
                         ,'ch.unige.dolly:unmount_datetime']



# class CmdZfsList(mexecutor.ShellCmdWrapped):
#     default_fields=
#     def __new__(self, bename):
#         return str.__new__(self, "zfs list -H -o %s -t filesystem,volume,snapshot" % ",".join(fields))
#     def __init__(self, bename):
#         super(CmdBeadmDestroy, self).__init__("beadm destroy -F %s" % bename)
#     with_construct=True
#     def _factory(self,shell_result):
#         '''call by Factor'''
#         if shell_result.status != 0:
#             my_logger.error('the cmd (%s) did not succeed' % self)
#             return []
#         return []
#

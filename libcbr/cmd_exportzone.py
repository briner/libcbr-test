'''
Created on 9 janv. 2015

@author: briner
'''

import logging

# libcbr
import mexecutor


my_logger=logging.getLogger('MyLogger')

class CmdZoneconfigExport(mexecutor.ObjectWrapped):
    def __new__(cls, zonename):
        return str.__new__("zonecfg -z %s export" % zonename)
    def _factory(self,shell_result):
        '''call by Factor'''
        if shell_result.status != 0:
            my_logger.error('the cmd (%s) did not succeed' % self)
            return []
        return zoneCaca(shell_result.stdout)




class zoneCaca(object):
    def __init__(self, output, zone):
        self.output=output
        self.zone=zone
    def __repr__(self):
        return str("%s(%s)" % (self.__class__, self.zone.zonename))





# CmdZonecfgExport("zonecfg -z %(zonename) export")




# 
# def read_zone_config(output):
#     
#     cmd=ZONECFG_EXPORT_CMD % self.zonename
#     proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, cwd='/')
#     lout=proc.stdout.readlines()  
#     retcode=proc.wait()
#     if retcode != 0 : 
#         my_logger.error('the cmd (%s) did not succeed' % cmd)
#     lout=[out.rstrip() for out in lout]    
#     lout_iter=iter(lout)
#     self._lfs=[]
#     for out in lout_iter:
#         if 'add fs' != out:
#             dparameter={}
#             continue
#         for out in lout_iter:
#             if 'end' == out:
#                 self._lfs.append(ZoneFS(**dparameter))
#                 break
#             key, value=out.split(' ')
#             if 'set' == key:
#                 key1,value1=value.split('=')
#                 if key1 == 'dir':
#                     dparameter['fs_dir']=value1
#                 elif key1 == 'special':
#                     dparameter['fs_special']=value1
#                 if key1 == 'type':
#                     dparameter['fs_type']=value1

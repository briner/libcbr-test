'''
Created on 9 janv. 2015

@author: briner
'''

import logging

# libcbr
import cmd_listzone
import mexecutor


my_logger=logging.getLogger('MyLogger')

_LEN_OF_ZONE_LIST_ENTRY=10
class CmdZonecfgExport(mexecutor.CmdWithFactory):
    with_construct=True
    def factory(self,resp):
        '''call by Factor'''
        if resp.status != 0:
            my_logger.error('the cmd (%s) did not succeed' % self)
            return []
        return zoneCaca(resp.stdout)

class Container(object): pass
container=Container()
container.method_name="config_export"
container.class_cmd=CmdZonecfgExport
container.cmd_template_str="zonecfg -z %(zonename) export"
container.lattr=["zonename"]
cmd_listzone.Zone.add_cmd(container)




class zoneCaca(object):
    def __init__(self, output):
        self.output=output
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

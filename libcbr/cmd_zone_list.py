# -*- coding: utf-8 -*-
'''
Created on 9 janv. 2015

@author: briner
'''

import os
import subprocess
import logging
import select

import mexecutor
import mix

my_logger=logging.getLogger('MyLogger')
ZONECFG_EXPORT_CMD="zonecfg -z %s export"


_LEN_OF_ZONE_LIST_ENTRY=10
class CmdZoneList(mexecutor.ShellCmdWrapped):
    def __new__(self):
        return str.__new__(self, "zoneadm list -cp")
    def __init__(self):
        super(CmdZoneList, self).__init__("zoneadm list -cp")
    with_construct=True
    def _factory(self,shell_result):
        '''call by Factor'''
        if shell_result.status != 0:
            my_logger.error('the cmd (%s) did not succeed' % self)
            return []
        lzone=[]
        for line in shell_result.stdout:
            zone=self.from_zoneadm_list_entry(line)
            lzone.append(zone)
        return lzone

    @staticmethod
    def from_zoneadm_list_entry(output_line):
        ''' output_line: "1:grouper3:running:/zones/grouper3_pool/grouper3:40cc68e3-f061-e385-cac9-ec6aefc6ae3a:solaris:excl:-:none:'''
        zone_list_entry=output_line.split(":")
        zone_list_entry=zone_list_entry+(_LEN_OF_ZONE_LIST_ENTRY-len(zone_list_entry))*['']
        return Zone(*zone_list_entry)



class Zone(mexecutor.ObjectWrapped):
    lcmd={}
    def __init__(self,  zoneid, zonename, state, zonepath, uuid, brand, ip_type, r_or_w, file_mac_profile, unused_field):
        self.zoneid=zoneid
        self.zonename=zonename
        self.state=state
        self.zonepath=zonepath
        self.uuid=uuid
        self.brand=brand
        self.ip_type=ip_type
        self.r_or_w=r_or_w
        self.file_mac_profile=file_mac_profile
        self.unused_field=unused_field
        self.is_local=self.zonename != 'global'
        self._lrecipient=None   # this is a lazy list
        self._lfs_info=None # this is a lazy list
#        self._dsm_sys=None
        self._lfs=None
    @classmethod
    def add_method(cls, name, wrapped_fun):
        fun=wrapped_fun()
#         print "name", name
#         print "wrapped_fun", "type", type(wrapped_fun), "self", wrapped_fun, "dir",dir(wrapped_fun)
#         print "fun", "type", type(fun), "self", fun, "dir",dir(fun)
        setattr(cls, name, fun)
    def to_list(self):
        return [self.zoneid \
        ,self.zonename \
        ,self.state \
        ,self.zonepath \
        ,self.uuid \
        ,self.brand \
        ,self.ip_type
        ,self.r_or_w
        ,self.file_mac_profile]
    def _get_rootpath(self):
        if self.zonename=='global':
            return self.zonepath
        else:
            return os.path.join(self.zonepath, 'root')
    rootpath=property(_get_rootpath)
#     @classmethod
#     def add_cmd(cls, method_name, fun):
#         setattr(cls, method_name, fun())
    def _get_uniq_value(self):
        """to comply with UniqList """
        return self.zonename
    uniq_value=property(_get_uniq_value)
    def __str__(self):
        return 'zone(%s)' % (self.zonename)
    __repr__=__str__
    def _get_is_running(self):
        return 'running' == self.state
    is_running=property(_get_is_running)
    def _get_lrecipient(self):
        if not self.is_running:
            msg='zone(%s) not in "running" state, can not _get_lrecipient (%s)' % self.zonename
            my_logger.warning(msg)
            return []
        if self._lrecipient:
            return self._lrecipient
        if [] == self._lrecipient:
            return []
        fn_etc_alias=os.path.join(self.zonepath, 'root/etc/aliases') #
        if not os.path.isfile(fn_etc_alias):
            self._lrecipient=[]
            return self._lrecipient
        #
        # the good case
        fh_etc_alias=open(fn_etc_alias,'r')
        for line in fh_etc_alias.readlines() :
            if line.find('root:') == 0:
                self._lrecipient=[email.rstrip().lstrip() for email in line[len('root:'):].split(',') if -1 != email.find('@')]
        return self._lrecipient
    lrecipient=property(_get_lrecipient)
    def cmp_by_name(self, a,b):
        return mix.cmpAlphaNum(a.zonename, b.zonename)
    cmp_by_name=classmethod(cmp_by_name)
    def __cmp__(self, other):
        return cmp(self.uuid, other.uuid)
    def _get_lfs(self):
        if [] == self._lfs:
            return []
        if self._lfs:
            return self._lfs
        self.read_zone_config()
        return self._lfs
    lfs=property(_get_lfs)
    def read_zone_config(self):
        cmd=ZONECFG_EXPORT_CMD % self.zonename
        proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, cwd='/')
        lout=proc.stdout.readlines()
        retcode=proc.wait()
        if retcode != 0 :
            my_logger.error('the cmd (%s) did not succeed' % cmd)
        lout=[out.rstrip() for out in lout]
        lout_iter=iter(lout)
        self._lfs=[]
        for out in lout_iter:
            if 'add fs' != out:
                dparameter={}
                continue
            for out in lout_iter:
                if 'end' == out:
                    self._lfs.append(ZoneFS(**dparameter))
                    break
                key, value=out.split(' ')
                if 'set' == key:
                    key1,value1=value.split('=')
                    if key1 == 'dir':
                        dparameter['fs_dir']=value1
                    elif key1 == 'special':
                        dparameter['fs_special']=value1
                    if key1 == 'type':
                        dparameter['fs_type']=value1
#     def zlogin(self,  cmd):
#         cmd=ZLOGIN_CMD % (self.zonename,  cmd)
#         my_logger.debug('enter in "Zone.zlogin"')
#         if not self.is_running:
#             msg='zone(%s) not in "running" state, can not execute the zlogin cmd (%s)' % (self.zonename,cmd)
#             my_logger.warning(msg)
#             return
#         proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd='/')
#         read_set=[proc.stdout, proc.stderr]
#         lline_hook=[]
#         send_email=False
#         while read_set:
#             rlist,unused_wlist,unused_xlist=select.select(read_set, [], [])
#             if proc.stdout in rlist:
#                 stdout=proc.stdout.readline()
#                 if stdout == '':
#                     read_set.remove(proc.stdout)
#                 else:
#                     stdout=stdout.rstrip()
#                     msg='hook (out): %s' % stdout
#                     lline_hook.append(msg)
#                     my_logger.debug(msg)
#             if proc.stderr in rlist:
#                 stderr=proc.stderr.readline()
#                 if stderr == '':
#                     read_set.remove(proc.stderr)
#                 else:
#                     send_email=True
#                     stderr=stderr.rstrip()
#                     msg='hook (err): %s' % stderr
#                     my_logger.error(msg)
#                     lline_hook.append(log.getLogStr())
#         if send_email:
#             lbody_email=['zone(%s)' % self.zonename
#                         ,' - hook cmd (%s)' % cmd
#                         ]+ [' - %s' % line for line in lline_hook]
# #lost             notification.notify.add(lbody_email, lrecipient=self.lrecipient)
    def launch_hook_before_snapshot(self):
        my_logger.debug('enter in launch_hook_before_snapshot within the zone(%s)'%self.zonename)
        if not self.is_running:
            msg='zone(%s) not in "running" state, can not launch hook(before_snapshot)' % self.zonename
            my_logger.warning(msg)
            return
        fn_hook_global=os.path.join( self.zonepath, 'root', FN_HOOK_BEFORE_SNAPSHOT_RELATIVE_2_ZONEPATH )
        fn_hook_local=os.path.join( '/', FN_HOOK_BEFORE_SNAPSHOT_RELATIVE_2_ZONEPATH )
        if os.path.isfile(fn_hook_global):
            my_logger.info('execute hook(%s) before snapshot within the zone(%s)' % (fn_hook_local, self.zonename))
            self.zlogin(fn_hook_local)
        else:
            my_logger.info('no hook(%s) before snapshot for zone(%s)' % (fn_hook_local, self.zonename))
    def launch_hook_after_snapshot(self):
        my_logger.debug('enter in launch_hook_after_snapshot within the zone(%s)'%self.zonename)
        if not self.is_running:
            msg='zone(%s) not in "running" state, can not launch hook(after_snapshot)' % self.zonename
            my_logger.warning(msg)
            return
        fn_hook_global=os.path.join( self.zonepath, 'root', FN_HOOK_AFTER_SNAPSHOT_RELATIVE_2_ZONEPATH )
        fn_hook_local=os.path.join( '/', FN_HOOK_AFTER_SNAPSHOT_RELATIVE_2_ZONEPATH )
        if os.access(fn_hook_global, os.X_OK):
            my_logger.info('execute hook(%s) after snapshot for zone(%s)' % (fn_hook_local, self.zonename))
            self.zlogin(fn_hook_local)
        else:
            my_logger.info('no hook(%s) after snapshot for zone(%s)' % (fn_hook_local, self.zonename))

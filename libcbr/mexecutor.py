# -*- coding: utf-8 -*-

'''
Created on 27 nov. 2014

@author: briner
'''
from __future__ import print_function

import os

import subprocess
from multiprocessing import Process, Queue
import urlparse
from collections import OrderedDict



import paramiko
import socket

import mhost
#TODO: DEFAULT_SSH_USER should not be defined here.
DEFAULT_SSH_USER="su"


class Relation():
    _cur_time=1
    _tcc=[]
    @classmethod
    def set_time(cls ,time):
        cls._cur_time=time
    @classmethod
    def get_exe(cls, thisobject):
        issuer=cls.get(issuing=thisobject)[1]
        if isinstance(issuer, Executor):
            return issuer
        return cls.get_exe(issuer)
    @classmethod
    def add_issuer_issuing(cls, issuer, issuing):
        if cls.get(time=cls._cur_time, issuer=issuer, issuing=issuing):
            return
        cls._tcc.append((cls._cur_time, issuer, issuing))
    @classmethod
    def get(cls, time=None, issuer=None, issuing=None, issuing_type=None):
        lret=cls._tcc[:]
        if not time:
            time=cls._cur_time
        lret=[ret for ret in lret if time==ret[0] ]
        if issuer:
            lret=[ret for ret in lret if id(issuer)==id(ret[1]) ]
        if issuing:
            lret=[ret for ret in lret if id(issuing)==id(ret[2]) ]
        if issuing_type:
            lret=[ret for ret in lret if isinstance(ret[2], issuing_type)]
        #
        if issuing:
            if lret:
                return lret[0]
        return lret

    @classmethod
    def delete_time(cls, time):
        cls._tcc=[tcc for tcc in cls._tcc if time!=tcc[0]]
#     did_result={}
#     @classmethod
#     def map_object_with_result(cls, this_object, result):
#         cls.did_result[id(this_object)]=result
#     @classmethod
#     def map_id_with_result(cls, this_id, result):
#         cls.did_result[this_id]=result
#     @classmethod
#     def get_result_for_id(cls, this_id):
#         return cls.did_result.get(this_id,None)
#     @classmethod
#     def get_result_for_object(cls, this_object):
#         return cls.get_result_for_id(id(this_object))

class FactoryFromCmd(object):
    @classmethod
    def create_from_lexe(cls, lexe, cmd):
        lmap_exe_cmd=[(exe, cmd, None) for exe in lexe]
        return cls.create(lmap_exe_cmd)
    @classmethod
    def create_from_lissuing(cls, lissuing, cmd):
        lmap_exe_cmd=[(Relation.get_exe(issuing), cmd) for issuing in lissuing]
        lmap_exe_cmd_result=cls.create(lmap_exe_cmd)
        lmap_issuing_cmd_result=[]
        for i in range(len(lmap_exe_cmd_result)):
            lmap_issuing_cmd_result.append((lissuing[i], cmd, lmap_exe_cmd_result[i][2]))
        return lmap_issuing_cmd_result
    @classmethod
    def create(cls, lmap_exe_cmd_related):
        '''run_parallel is the default run. So run does run run_parallel
        exe: the Executor
        cmd: the command passed
        related: info passed to be join with the result for an easier usage'''
        lmap_exe_cmd_result_related=[]
        queue=Queue()
        lprocess=[]
        index_exe=0
        dindex_execmd={}
        for exe, cmd, related in lmap_exe_cmd_related:
            dindex_execmd[index_exe]=exe,cmd,related
            lprocess.append(Process(target=exe._exe_on_queue, name=exe.url.geturl(), args=(str(cmd), queue, index_exe)))
            index_exe+=1
        [p.start() for p in lprocess]
        [p.join() for p in lprocess]
        while queue.qsize():
            queue_xf=queue.get()
            index_exe, lresult_elem=queue_xf
            exe,cmd,related=dindex_execmd[index_exe]
            lresult_elem.append(cmd)
            if issubclass(cmd.__class__, ShellCmdWrapped):
                result=ShellResultWrapped(*lresult_elem)
            else:
                result=ShellResult(*lresult_elem)
            lmap_exe_cmd_result_related.append((exe, cmd, result, related))
            if issubclass(cmd.__class__, ShellCmdWrapped):
                for output in result.outputs:
                    Relation.add_issuer_issuing(exe, output)
        return lmap_exe_cmd_result_related
    def create_in_serial(self, lmap_exe_cmd):
        pass



class UtilExecutor(object):
    @staticmethod
    def to_lexe(raw):
        if isinstance(raw, ListExecutor):
            lexe=raw
        elif isinstance(raw, list):
            ListExecutor(raw)
        else:
            lexe=ListExecutor([raw])
        return lexe

class FactoryExecutor(object):
    _cache=OrderedDict()
    @classmethod
    def clear_prefix_in_cache(cls):
        cls._cache=OrderedDict()
    @staticmethod
    def _url_or_str_2_url(url_or_str):
        if isinstance(url_or_str, str):
            return urlparse.urlparse(url_or_str)
        elif isinstance(url_or_str, urlparse.ParseResult):
            return url_or_str
        elif None == url_or_str:
            return None
        else:
            raise ValueError("url_or_str(%s) is invalid" % repr(url_or_str))
    @classmethod
    def gen_from_url(cls, url_or_str):
        '''the reference to use Executor'''
        url=cls._url_or_str_2_url(url_or_str)
        tmpexe=cls._cache.get(url, None)
        if not tmpexe:
            tmpexe=Executor(url)
            cls._cache[url]=tmpexe
        return tmpexe
    @classmethod
    def gen_for_hostname(cls,hostname=None):
        '''convenient generator for host'''
        if None == hostname:
            return cls.gen_from_url(None)
        #
        return cls.gen_from_url("ssh://%s@%s" % (DEFAULT_SSH_USER, hostname))
    @classmethod
    def gen_for_ssh_host(cls, hostname, username=None):
        '''convenient generator for ssh host'''
        username=username if username else DEFAULT_SSH_USER
        url=urlparse.urlparse("ssh:%s@%s//" % (username, hostname))
        return cls.gen_from_url(url)
    @classmethod
    def gen_list_from_lprefixhost(cls, lprefixhost, force_refresh=False):
        '''convenient generator for host prefix such as (dropzone)'''
        lexe=[]
        for prefixhost in lprefixhost:
            lhost=mhost.FactoryHost.gen_from_prefix(prefixhost, force_refresh=force_refresh)
            lurl=[cls._url_or_str_2_url("ssh://su@"+host) for host in lhost]
            for url in lurl:
                lexe.append(cls.gen_from_url(url))
        return ListExecutor(lexe)

class ListExecutor(list):
    def run(self, cmd):
        return FactoryFromCmd.create_from_lexe(self, cmd)
#         if issubclass(cmd.__class__, ShellCmdWrapped):
#             lmap_exe_result_elem=self._run(cmd.cmdline)
#             lresult=[]
#             for exe, result_elem in lmap_exe_result_elem:
#                 result_elem[1]=cmd
#                 result=ShellResultWrapped(*result_elem)
#                 if isinstance(result.output, list):
#                     [Relation.add_issuer_issuing(exe, elem) for elem in result.output]
#                 else:
#                     Relation.add_issuer_issuing(exe,result.output)
#                 lresult.append(result)
#             return lresult
#         elif isinstance(cmd, str):
#             return self._run(cmd)
#         else:
#             raise TypeError("cmd must be str or subclass of ShellCmdWrapped")
#     def _run(self, cmd):
#         '''run_parallel is the default run. So run does run run_parallel'''
#         lmap_exe_result=[]
#         queue=Queue()
#         lprocess=[]
#         for exe in self:
#             lprocess.append(Process(target=exe._exe_on_queue, name=exe.url.geturl(), args=(str(cmd), queue)))
#         [p.start() for p in lprocess]
#         [p.join() for p in lprocess]
#         while queue.qsize():
#             index_exe, lresult_elem=queue.get()
#             lmap_exe_result.append((self[index_exe], lresult_elem))
#         return lmap_exe_result



class Executor(object):
    '''
    allow to dissociate execution of bash cmd
    run: allow you to run the command through independentely of the scheme
    '''
    def __init__(self, url=None):
        self.url=url
        self._ssh_client=None # to allow keeps ssh connection used in __load_ssh_client
    @property
    def hostname(self):
        return self.url.netloc.split("@")[1]
    def __repr__(self):
        exe_repr="local" if None == self.url else self.url.geturl()
        return "Executor(%s)" % exe_repr
    def run(self, cmd_str):
        try:
            lresult_elem=self._exe(cmd_str)
        except socket.timeout:
            return None
        lresult_elem.append(cmd_str)
        if issubclass(cmd_str.__class__, ShellCmdWrapped):
            result=ShellResultWrapped(*lresult_elem)
        else:
            result=ShellResult(*lresult_elem)
        #Relation
        if issubclass(cmd_str.__class__, ShellCmdWrapped):
            for output in result.outputs:
                Relation.add_issuer_issuing(self, output)
        # return
        return result
    def _exe(self, cmd_str):
        if None == self.url:
            return self._local_exe(cmd_str)
        elif "ssh" == self.url.scheme:
            return self._ssh_exe(cmd_str)
        else:
            raise NotImplemented("unknown scheme(%s)" % self.url.scheme )
    #
    # in //
    def _exe_on_queue(self, cmd_str, queue, index_exe):
        '''used by ListExecutor to launch execution in //'''
        try:
            lresult_elem=self._exe(cmd_str)
        except socket.timeout:
            # TODO: we should better manage when a ssh target does have a timeout
            #       as says, that this host did not reply, and come back here
            #       to continue our job.
            return
        queue_xf=(index_exe, lresult_elem)
        queue.put(queue_xf)
    #
    # schemes
    def _local_exe(self, cmd_str):
        '''execute locally'''
        process=subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd='/')
        stdout, stderr = process.communicate()
        stdout=[line.rstrip(os.linesep) for line in stdout.rstrip(os.linesep).split(os.linesep)]
        stderr=[line.rstrip(os.linesep) for line in stderr.rstrip(os.linesep).split(os.linesep)]
        status=process.wait()
        lresult_elem=[self.url, stdout, stderr, status]
        return lresult_elem
    #
    def __load_ssh_client(self):
        if None == self._ssh_client:
            username, hostname= self.url.netloc.split("@")
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.load_system_host_keys()
            if username:
                self._ssh_client.connect(hostname, username=username, timeout=3)
            else:
                self._ssh_client.connect(hostname, username=DEFAULT_SSH_USER, timeout=3)
    def _ssh_exe(self, cmd_str):
        '''execute through ssh'''
        self.__load_ssh_client()
        unused_stdin,o,e=self._ssh_client.exec_command(cmd_str)
        status=o.channel.recv_exit_status()
        stdout=[line.rstrip(os.linesep) for line in o.readlines()]
        stderr=[line.rstrip(os.linesep) for line in e.readlines()]
        lresult_elem=[self.url, stdout, stderr, status]
        return lresult_elem

class ShellCmdOutputs(str):
    def __init__(self,lout_err, status):
        pass

class ShellCmd(str):
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)

class ShellCmdWrapped(ShellCmd):
    def _factory(self, shell_result):
        raise NotImplementedError()
    def __repr__(self):
        return self.__class__.__name__



class ShellResult(object):
    def __init__(self, url, stdout, stderr, status, cmd):
        self.url=url
        self.stdout=stdout
        self.stderr=stderr
        self.status=status
        self.cmd=cmd

class ShellResultWrapped(ShellResult):
    def __init__(self, url, stdout, stderr, status, cmd):
        super(ShellResultWrapped, self).__init__(url, stdout, stderr, status, cmd)
        self.shell_cmd_wrapped=cmd
        self.outputs=self.shell_cmd_wrapped._factory(self)

class ObjectWrapped(object):
    pass



# COMNENT IT AS IT SEEMS TO BE SOME SNIPPET PASTE HERE
# import paramiko
# import socket
# import os
# import select
#
# cmd_str='bash -c \'for i in $(seq 10); do if expr $RANDOM % 2 > /dev/null; then echo "${i}out" ; else echo "${i}err" >&2  ; fi;done\''
#
# username, hostname= ("su","dropzone7")
# ssh_client = paramiko.SSHClient()
# ssh_client.load_system_host_keys()
# ssh_client.connect(hostname, username=username, timeout=3)
#
# unused_stdin,o,e=ssh_client.exec_command(cmd_str)
# lline=[]
# read_set=[o.channel, e.channel]
# while read_set:
#     rlist,wlist,xlist=select.select(read_set, [], [])
#     if o.channel in rlist:
#         line=o.readline()
#         if line == '':
#             read_set.remove(o.channel)
#         else:
#             lline.append(("stdout", line))
#     if e.channel in rlist:
#         line=e.readline()
#         if line == '':
#             read_set.remove(e.channel)
#         else:
#             lline.append(("stderr", line))
#
#         # self.url=url
#         # self.cmd=cmd
#         # self.stdout=stdout
#         # self.stderr=stderr
#         # self.status=status

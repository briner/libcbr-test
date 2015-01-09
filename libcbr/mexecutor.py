# -*- coding: utf-8 -*-

'''
Created on 27 nov. 2014

@author: briner
'''
from __future__ import print_function

import subprocess
from multiprocessing import Process, Queue
import urlparse
#pythnon3 from urllib.parse import urlparse, ParseResult
import uuid
from collections import OrderedDict



import paramiko
import socket

import mhost

#TODO: DEFAULT_SSH_USER should not be defined here.
DEFAULT_SSH_USER="su"
class Related():
    did_result={}
    @classmethod
    def map_object_with_result(cls, this_object, result):
        cls.did_result[id(this_object)]=result        
    @classmethod
    def map_id_with_result(cls, this_id, result):
        cls.did_result[this_id]=result        
    @classmethod
    def get_result_for_id(cls, this_id):
        return cls.did_result.get(this_id,None)
    @classmethod
    def get_result_for_object(cls, this_object):
        return cls.get_result_for_id(id(this_object))

# class Cmd(str):
#     with_construct=False

# # this class works a classmethod
# class FactorCmd(Cmd):
#     with_construct=True
#     @classmethod
#     def factor(cls, resp):
#         return cls._factor(resp)
#     @classmethod
#     def set_factor(cls, fun):
#         cls._factor=fun
#     @classmethod
#     def from_resp(cls, resp):
#         lobject=cls._from_resp(resp)
#         for this_object in lobject:
#             Related.map_object_with_result(this_object, resp)
#         return lobject

class FactoryFromCmd(object):
    @classmethod
    def create(cls,executable, cmd):
        if isinstance(executable, ListExecutor):
            lexe=executable
        elif isinstance(executable, Executor):
            lexe=ListExecutor([executable])
        else:
            # find the executor
            res=Related.get_result_for_id(executable)
            exe=FactoryExecutor.gen_from_url(res.url)
            lexe=ListExecutor[exe]         
        #
        lres=lexe.run_parallel(cmd)
        if isinstance(cmd, CmdWithFactory):
            for res in lres:
                res.init_output()
        return lres
 

class Cmd(str): pass
class CmdWithFactory(Cmd): pass

class Result(object):
    def __init__(self, url, cmd, stdout, stderr, status):
        self.url=url
        self.cmd=cmd
        self.stdout=stdout
        self.stderr=stderr
        self.status=status
        self._uuid=uuid.uuid1()
        self._output=None
        self._output_is_constructed=False
    def init_output(self):
        self.output
    @property
    def output(self):
        if self._output_is_constructed:
            return self._output
        self._output_is_constructed=True
        if issubclass(self.cmd.__class__, CmdWithFactory):
            self._output=self.cmd.factory(self)
        return self._output
    @property
    def host(self):
        if self.url:
            return mhost.UtilHost.to_host(self.url.netloc.split("@")[1])
        else:
            return None


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
    def run_parallel(self, cmd):
        lres=[]
        queue=Queue()
        lprocess=[]
        for exe in self:
            lprocess.append(Process(target=exe._exe_on_queue, name=exe.url.geturl(), args=(cmd, queue)))
        [p.start() for p in lprocess]
        [p.join() for p in lprocess]
        while queue.qsize():
            res=queue.get()
            if res:
                lres.append(res)
        [res.init_output() for res in lres]
        return lres
    def run_serial(self, cmd):
        return [exe.run(cmd) for exe in self]
    
class Executor(object):
    '''
    allow to dissociate execution of bash cmd
    run: allow you to run the command through independentely of the scheme
    '''
    def __init__(self, url=None):
        self.url=url
        self._ssh_client=None # to allow keeps ssh connection used in __load_ssh_client
    def __repr__(self):
        exe_repr="local" if None == self.url else self.url.geturl()
        return "Executor(%s)" % exe_repr
    def run(self, cmd):
        try:
            res=self._exe(cmd)
        except socket.timeout:
            return None
        res.enable()
        return res
    def _exe(self, cmd):
        if None == self.url:
            return self._local_exe(cmd)
        elif "ssh" == self.url.scheme:
            return self._ssh_exe(cmd)
        else:
            raise NotImplemented("unknown scheme(%s)" % self.url.scheme )
    #
    # in //
    def _exe_on_queue(self, cmd, queue):
        '''used by ListExecutor to launch execution in //'''
        try:
            res=self._exe(cmd)
        except socket.timeout:
            res=None
        queue.put(res)
    #
    # schemes
    def _local_exe(self, cmd):
        '''execute locally'''
        proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd='/')
        stdout=[line.rstrip() for line in proc.stdout.readlines()]
        stderr=[line.rstrip() for line in proc.stderr.readlines()]
        status=proc.wait()
        result=Result(self.url, cmd, stdout, stderr, status)
        return result
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
    def _ssh_exe(self, cmd):
        '''execute through ssh'''
        self.__load_ssh_client()
        unused_stdin,o,e=self._ssh_client.exec_command(cmd)
        status=o.channel.recv_exit_status()
        stdout=[line.rstrip() for line in o.readlines()]
        stderr=[line.rstrip() for line in e.readlines()]
        result=Result(self.url, cmd, stdout, stderr, status)
        return result
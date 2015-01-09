# -*- coding: utf-8 -*-

'''
Created on 1 dec. 2014

@author: briner
'''
DEFAULT_LIST_PREFIX_ZONE="amazone dropzone calzone canzone twilightzone fanzone webz".split()


import os
import socket
import pickle
import re

class UtilHost(object):
    @staticmethod
    def get_in_dns(hostname):
        try:
            socket.gethostbyname(hostname)
            return True
        except:
            return False
    @staticmethod
    def to_host(raw):
        if isinstance(raw, Host):
            return raw
        elif isinstance(raw, str):
            return Host(raw)
        else:
            raise Exception("UtilHost.to_host must be either a string or a Host")

class FactoryHost(object):
    _cache=None
    _picklefn=os.path.expanduser("~/.cache/ch.unige.host")
    @classmethod
    def clear_prefix_in_cache(cls, prefix):
        if "__all__" == prefix:
            cls._cache=[]
            cls._dump_cache()
        else:
            re_inst=re.compile("^%s\d+$" % prefix)
            lhost=[ host for host in cls._cache if not re_inst.search(host)]
            cls._cache=lhost[:]
            cls._dump_cache()
    @classmethod
    def gen_from_prefix(cls, prefix, force_refresh=False):
        '''prefix = "dropzone" or "amazone"
        force_refresh : tells the clear the cache for this prefix
        '''
        # 
        if None == cls._cache:
            cls._load_cache()
        # 
        re_inst=re.compile("^%s\d+$" % prefix)
        lhost=[ host for host in cls._cache if re_inst.search(host)]
        if 0 == len(lhost):
            not_found=0
            i=-1
            while not_found < 20:
                i+=1
                hostname=prefix+str(i)
                if UtilHost.get_in_dns(hostname):
                    host=Host(hostname)
                else:
                    not_found+=1
                    continue
                lhost.append(host)
                cls._add_cache(host)
                lhost.append(Host(hostname))
            cls._dump_cache()
        return lhost[:]
    @classmethod
    def _add_cache(cls, host):
        if host not in cls._cache:
            cls._cache.append(host)
    @classmethod
    def _del_cache(cls, prefix):
        lnewcache=[]
        # delete this old prefix
        for host in cls._cache:
            if not -1 == host.find(prefix):
                lnewcache.append(host)
        cls._cache=lnewcache[:]
    @classmethod
    def _load_cache(cls):
        try:
            cls._cache=pickle.load(open(cls._picklefn,"r"))
        except:
            cls._cache=[]
    @classmethod
    def _dump_cache(cls):
        pickle.dump(cls._cache,open(cls._picklefn,"w"))

class Host(str):
    def __new__(cls, *args, **kw):
        return str.__new__(cls,*args,**kw)
    def __repr__(self):
        return "Host(%s)" % self
    


if "__main__" == __name__:
    FactoryHost.gen_from_prefix(['dropzone'], force_refresh=True)
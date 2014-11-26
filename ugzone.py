#!/usr/bin/python
# encoding: utf-8
'''
ugzone -- unige.ch zone for solaris

ugzone is a facility to manage zone

It defines classes_and_methods

@author:     Cédric BRINER

@copyright:  2014 University of Geneva. All rights reserved.

@license:    gpl3 and higher

@contact:    Cedric.BRINER@unige.ch
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

import uuid
import socket
import paramiko

from multiprocessing import Process, Queue

from collections import OrderedDict
from mechanize._html import Args

__all__ = []
__version__ = 0.1
__date__ = '2014-11-26'
__updated__ = '2014-11-26'

DEBUG = 0
TESTRUN = 0
PROFILE = 0






class Zone(object):
    def __init__(self,str_zone_list_entry_OR_zone_list_entry):
        if isinstance(str_zone_list_entry_OR_zone_list_entry, basestring):
            zone_list_entry=str_zone_list_entry_OR_zone_list_entry.split(':')
        else:
            zone_list_entry=str_zone_list_entry_OR_zone_list_entry
        if len(zone_list_entry) == 7:
            zone_list_entry=zone_list_entry+['','']
        [self.zoneid \
        ,self.zonename \
        ,self.state \
        ,self.zonepath \
        ,self.uuid \
        ,self.brand \
        ,self.ip_type
        ,self.r_or_w
        ,self.file_mac_profile]=zone_list_entry[:9]
        self.is_local=self.zonename != 'global'
        self._lfs=None
    @classmethod
    def factory_lzone_from_stdout(cls, stdout):
        dzone=OrderedDict()
        for line in stdout:
            zone=cls(line)
            dzone[zone.zonename]=zone
        return dzone
    @staticmethod
    def get_from_cmd_str():
        return "zoneadm list -cp"
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
        raise NotImplemented()
#     def cmp_by_name(self, a,b):
#         return mix.cmpAlphaNum(a.zonename, b.zonename)
#     cmp_by_name=classmethod(cmp_by_name)
       
        




__all__ = []
__version__ = 0.1
__date__ = '2014-11-24'
__updated__ = '2014-11-24'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class Host(str):
    def __new__(cls, *args, **kw):
        return str.__new__(cls,*args,**kw)
    def __repr__(self):
        return "Host(%s)" % self

class Result(object):
    def __init__(self, host, cmd, stdout, stderr, status):
        if isinstance(host, Host):
            self.host=host
        else:
            self.host=Host(host)
        self.host=host
        self.cmd=cmd
        self.stdout=stdout
        self.stderr=stderr
        self.status=status
        self._uuid=uuid.uuid1()
    @property
    def uuid(self):
        return self._uuid

class GroupHost(list):
    def __init__(self, *args):
        super(GroupHost,self).__init__(*args)
    @classmethod
    def create_from(cls,prefix=None):
        lhost=[]
        not_found=0
        i=-1
        while not_found < 20:
            i+=1
            hostname=prefix+str(i)
            try:
                socket.gethostbyname(hostname)
            except:
                not_found+=1
                continue
            lhost.append(Host(hostname))
        group_host=GroupHost(lhost)
        return group_host
    def parallel_exec(self,cmd):
        queue=Queue()        
        lprocess=[]
        for host in self:
            lprocess.append(Process(target=self._qexec, args=(host, cmd, queue)))
        for p in lprocess:
            p.start()
        for p in lprocess:
            p.join()
        # recolte data
        lresult=[]
        while queue.qsize():
            lresult.append(queue.get())
        return lresult
    def serial_exec(self, cmd):
        lresult=[]
        for host in self:
            lresult.append(self._exec(host,cmd))
        return lresult
    def _qexec(self, host, cmd, queue):
        queue.put(self._exec(host, cmd))
    def _exec(self, host, cmd):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(host, username="su")
        unused_i,o,e=client.exec_command(cmd)
        status=o.channel.recv_exit_status()
#         o=o.readlines()
#         e=e.readlines()
        o=[line.rstrip() for line in o.readlines()]
        e=[line.rstrip() for line in e.readlines()]
        result=Result(host,cmd,o,e,status)
        return result
    

    
_cache_lglobalzone=None
def get_list_globalzone():
    global _cache_lglobalzone
    if _cache_lglobalzone != None:
        return _cache_lglobalzone
    _cache_lglobalzone=GroupHost.create_from("dropzone")
    return _cache_lglobalzone
        
def whereis(zonename):
    lhost=[]
    lg=get_list_globalzone()
    for result in lg.parallel_exec("zoneadm list -cp"):
        if result.status:
            print "cmd(%s) on host(%s) failed" % (result.cmd, result.host)
            continue
        dzone=Zone.factory_lzone_from_stdout(result.stdout)
        if zonename in dzone:
            lhost.append(result.host)
    return lhost

def check(*args, **kw):
    pass



#######################################################################$
# MAIN


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Cédric BRINER on %s.
  Copyright 2014 University of Geneva. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
           
        subparsers = parser.add_subparsers(dest="sub", help='sub-command help')
    
        # whereis zonename
        parser_whereis = subparsers.add_parser('whereis', help='on which globalzone is a zone')
        parser_whereis.add_argument("zonename", type=str, help="which zonename to search")
        parser_whereis.set_defaults(func=whereis)
        # checks zonename
        parser_whereis = subparsers.add_parser('check', help='do some checks on the zone')
        parser_whereis.add_argument("zonename", type=str, help="which zonename to search")
        parser_whereis.set_defaults(func=check)
        # ugzone moves --// zone,zone,zone globalzone zone globalzone zone,zone,zone globalzone
    
        # Process arguments
        args = parser.parse_args()
        if "whereis" == args.sub:
            lhost=args.func(args.zonename)
            for host in lhost:
                print host
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
#     if DEBUG:
#         sys.argv.append("-h")
#         sys.argv.append("-v")
#         sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'ugzone_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
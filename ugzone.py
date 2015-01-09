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

from libcbr import mexecutor
from libcbr import mzone


__all__ = []
__version__ = 0.1
__date__ = '2014-11-26'
__updated__ = '2014-11-26'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

#
DEFAULT_LIST_PREFIX_ZONE="amazone dropzone calzone canzone twilightzone fanzone webz".split()
DEFAULT_LIST_PREFIX_ZONE=["dropzone"]

    

# class Host(str):
#     def __new__(cls, *args, **kw):
#         return str.__new__(cls,*args,**kw)
#     def __repr__(self):
#         return "Host(%s)" % self
# 
# class Result(object):
#     def __init__(self, host, cmd, stdout, stderr, status):
#         if isinstance(host, Host):
#             self.host=host
#         else:
#             self.host=Host(host)
#         self.host=host
#         self.cmd=cmd
#         self.stdout=stdout
#         self.stderr=stderr
#         self.status=status
#         self._uuid=uuid.uuid1()
#     @property
#     def uuid(self):
#         return self._uuid
# 
# class GroupHost(list):
#     def __init__(self, *lhost):
#         ltmphost=[]
#         for host in lhost:
#             if not isinstance(host, Host):
#                 ltmphost.append(Host(host))
#             else:
#                 ltmphost.append(host)
#         super(GroupHost,self).__init__(*ltmphost)
#     @classmethod
#     def create_from(cls,prefix=None):
#         lhost=[]
#         not_found=0
#         i=-1
#         while not_found < 20:
#             i+=1
#             hostname=prefix+str(i)
#             try:
#                 socket.gethostbyname(hostname)
#             except:
#                 not_found+=1
#                 continue
#             lhost.append(Host(hostname))
#         group_host=GroupHost(lhost)
#         return group_host
#     def parallel_exec(self,cmd, prefix=None):
#         if prefix:
#             if prefix not in DEFAULT_LIST_PREFIX_ZONE:
#                 raise Exception("prefix(%s) should be in %s" % (prefix, repr(DEFAULT_LIST_PREFIX_ZONE)))
#             
#         queue=Queue()        
#         lprocess=[]
#         for host in self:
#             lprocess.append(Process(target=self._qexec, args=(host, cmd, queue)))
#         for p in lprocess:
#             p.start()
#         for p in lprocess:
#             p.join()
#         # recolte data
#         lresult=[]
#         while queue.qsize():
#             lresult.append(queue.get())
#         return lresult
#     def serial_exec(self, cmd):
#         lresult=[]
#         for host in self:
#             lresult.append(self._exec(host,cmd))
#         return lresult
#     def _qexec(self, host, cmd, queue):
#         queue.put(self._exec(host, cmd))
#     def _exec(self, host, cmd):
#         client = paramiko.SSHClient()
#         client.load_system_host_keys()
#         client.connect(host, username="su")
#         unused_i,o,e=client.exec_command(cmd)
#         status=o.channel.recv_exit_status()
# #         o=o.readlines()
# #         e=e.readlines()
#         o=[line.rstrip() for line in o.readlines()]
#         e=[line.rstrip() for line in e.readlines()]
#         result=Result(host,cmd,o,e,status)
#         return result
# 
# 
# _cache_lglobalzone=None
# def get_list_globalzone(refresh=False):
#     global _cache_lglobalzone
#     pickle_file=os.path.expanduser("~/.cache/ch.unige.ugzone")
#     # 
#     lhost=[]
#     # force it
#     if refresh:
#         for prefix in DEFAULT_LIST_PREFIX_ZONE:
#             lhost+=GroupHost.create_from(prefix)
#         pickle.dump(lhost,open(pickle_file,"w"))
#         _cache_lglobalzone=lhost
#         return _cache_lglobalzone
#     # check the cache
#     if None != _cache_lglobalzone :
#         return _cache_lglobalzone
#     # check the pickle
#     try:
#         lhost=pickle.load(open(pickle_file))
#         _cache_lglobalzone=lhost
#         return _cache_lglobalzone
#     except:
#         pass
#     # do it
#     for prefix in DEFAULT_LIST_PREFIX_ZONE:
#         lhost+=GroupHost.create_from(prefix)
#     pickle.dump(lhost,open(pickle_file,"w"))
#     _cache_lglobalzone=lhost
#     return _cache_lglobalzone

    
def where_are(lzonename):
    lexe=mexecutor.FactoryExecutor.gen_list_from_lprefixhost(DEFAULT_LIST_PREFIX_ZONE)
    lresp=lexe.run_parallel(mzone.cmdlistzone)
    lzone=[]
    for resp in lresp:
        lzone+=resp.output
    lret=[]
    for zone in lzone:
        for zonename in lzonename:
            if zonename==zone.zonename:
                host=mexecutor.Related.get_result_for_object(zone).host
                lret.append((host, zonename))
    return lret

def list_global_local_host(lprefix=DEFAULT_LIST_PREFIX_ZONE):
    lexe=mexecutor.FactoryExecutor.gen_list_from_lprefixhost(lprefix)
    lresp=lexe.run_parallel(mzone.cmdlistzone)
    lzone=[]
    for resp in lresp:
        lzone+=resp.output
    return [(zone, mexecutor.Related.get_result_for_object(zone).host) for zone in lzone if zone.is_local]



# 
#     lg=DEFAULT_LIST_PREFIX_ZONget_list_globalzone()
#     lg=
#     for result in lg.parallel_exec("zoneadm list -cp"):
#         if result.status:
#             print "cmd(%s) on host(%s) failed" % (result.cmd, result.host)
#             continue
#         dzone=Zone.factory_lzone_from_stdout(result.stdout)
#         if zonename in dzone:
#             lhost.append(result.host)
#     return lhost

def execute_shell(cmd, lhostname, lprefixhostname):
    lexe=mexecutor.ListExecutor()
    if None != lprefixhostname:
        lexe=mexecutor.FactoryExecutor.gen_list_from_lprefixhost(lprefixhostname)
    for hostname in lhostname:
        lexe.append(mexecutor.FactoryExecutor.gen_for_hostname(hostname))
    return lexe.run_parallel(mexecutor.Cmd(cmd))

def check(*args, **kw):
    # zfs upgrade
    # zpool upgrade
    # beadm one value
    # no file under a zfs mount
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
        parser_whereis = subparsers.add_parser('where-are', help='on which globalzone is a zone')
        parser_whereis.add_argument("zonenames", type=str, help="which zonenames to search (eg: zone1,zone2)")
        parser_whereis.set_defaults(func=where_are)
        # list global local zone
        parser_whereis = subparsers.add_parser('list-global-local-host', help='list global zonename zonename-host')
        parser_whereis.add_argument("prefixes", type=str, help="on which prefixes (eg:webzone,sapzone for webzone1,2,5 and sapzone1)")
        parser_whereis.set_defaults(func=list_global_local_host)
        # execute
        parser_whereis = subparsers.add_parser('execute-shell', help='execute a shell command')
        parser_whereis.add_argument("--prefixes", type=str, help="on which prefixes (eg:webzone,sapzone for webzone1,2,5 and sapzone1)")
        parser_whereis.add_argument("--hosts", type=str, help="on which hosts (eg:zone1,zone2)")
        parser_whereis.add_argument("cmd", type=str, help="commande to invoke (eg: 'ls -l')")        
        parser_whereis.set_defaults(func=execute_shell)
        # checks zonename
        parser_whereis = subparsers.add_parser('check', help='do some checks on the zone')
        parser_whereis.add_argument("--zonenames", type=str, help="on wich zonename(eg: zone1,zone2)")
        parser_whereis.add_argument("--prefixes", type=str, help="on which prefixes(eg:webzone,sapzone for webzone1,2,5 and sapzone1)")
        parser_whereis.set_defaults(func=check)
        # ugzone moves --// zone,zone,zone globalzone zone globalzone zone,zone,zone globalzone
    
        # Process arguments
        args = parser.parse_args()
        if "where-are" == args.sub:
            lmaphostzonename=args.func(args.zonenames.split(","))
            for host, zonename in lmaphostzonename:
                print (host, zonename)
        elif "list-global-local-host" == args.sub:
            lmapzone_host=args.func(args.prefixes.split(","))
            for zone, host in lmapzone_host:
                print (host, zone.zonename)
        elif "execute-shell"  == args.sub:
            lhostname= [] if None==args.hosts else args.hosts.split(",")
            lprefixhostname= [] if None==args.prefixes else args.prefixes.split(",")
            lresp=args.func(args.cmd, lhostname=lhostname, lprefixhostname=lprefixhostname)
            for resp in lresp:
                print (resp.host)
                print (os.linesep.join(resp.stdout))
        elif "check" == args.sub:
            args.func(args.zonenames.split(","))
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
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
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
import traceback
import re
import time

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from libcbr import mexecutor, cmd_zpool_upgrade, cmd_beadm_list, cmd_zone_hostname, cmd_zpool_list, cmd_zone_zlogin
from libcbr import cmd_zone_list



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



def where_are(lzonename, lprefix=DEFAULT_LIST_PREFIX_ZONE):
    lret=[]
    for hostname, zonename in get_lmap_hostname_zone(lprefix=lprefix):
        if zonename.zonename in lzonename:
            lret.append((hostname, zonename))
    return lret

def get_lmap_hostname_zone(lprefix=DEFAULT_LIST_PREFIX_ZONE):
    lret=[]
    lexe=mexecutor.FactoryExecutor.gen_list_from_lprefixhost(lprefix)
    lmap_exe_cmd_result_related=mexecutor.FactoryFromCmd.create_from_lexe(lexe, cmd_zone_list.CmdListZone())
    lmap_exe_cmd_result_related.sort(lambda x,y:cmp(x[0].url.hostname,y[0].url.hostname))
    for exe, unused_cmd, result, unused_related in lmap_exe_cmd_result_related:
        lzone=result.outputs
        lzone.sort(cmd_zone_list.Zone.cmp_by_name)
        lret+=[(exe.url.hostname, zone) for zone in lzone]
    return lret


def execute_shell(cmd, lhostname, lprefixhostname, is_on_all_zones):
    lret=[]
    # lhostname
    lexe_from_lprefix=mexecutor.FactoryExecutor.gen_list_from_lprefixhost(lprefixhostname)
    # lprefixhostname
    lexe_from_lhost=[mexecutor.FactoryExecutor.gen_for_hostname(hostname) for hostname in lhostname]
    lexe=mexecutor.ListExecutor(list(set(lexe_from_lprefix).union(set(lexe_from_lhost))))
    # lhostname from zone
    # if is_on_all_zones:
    #     lzone=[]
    #     for r in lexe.run(cmd_zone_list.CmdZoneList()):
    #         if r[2].status != 0:
    #             continue
    #         for zone in r[2].outputs:
    #             lzone.append(zone)
    #     print lzone
    #     for zone in lzone:
    #         print zone.get_hostname
    #

    lmap_exe_cmd_result_related=mexecutor.FactoryFromCmd.create_from_lexe(lexe, mexecutor.ShellCmd(cmd))
    lmap_exe_cmd_result_related.sort(lambda x,y:cmp(x[0].url.hostname,y[0].url.hostname))
    for exe, unused_cmd, result, related in lmap_exe_cmd_result_related:
        lret.append(exe.url.hostname+":")
        if result.stdout:
            for line in result.stdout:
                lret.append(" "+line)
    return lret
# def check(lprefix=):
#
#     lexe_from_lprefix=mexecutor.FactoryExecutor.gen_list_from_lprefixhost(lprefix)
#
#     # zfs upgrade
#     lmap_exe_cmd_result=mexecutor.FactoryFromCmd.create_from_lexe(lexe, cmd_zpool_upgrade.CmdZpoolUpgrade())

def check_hostname(hostname):
    class Ret:
        def __init__(self):
            self.value=0
            self.lmsg=[]
    ret=Ret()
    exe=mexecutor.FactoryExecutor.gen_for_hostname(hostname)
    # zpool upgrade
    for poolname_version in exe.run(cmd_zpool_upgrade.CmdZpoolUpgrade()).outputs:
        ret.value+=1
        ret.lmsg.append("zpool uprade: CmdZpoolUpgrade hostname(%s) zpoolname(%s), version(%s)" % (hostname, poolname_version.name, poolname_version.version))
    # zfs upgrade
    for zfsname_version in exe.run(cmd_zpool_upgrade.CmdZpoolUpgrade()).outputs:
        ret.value+=2
        ret.lvalue.append("zfs upgrade: zfs(%s) on version(%s)" % (zfsname_version.poolname, zfsname_version.VERSION))
    # beadm
    res=exe.run(cmd_beadm_list.CmdZpoolList())
    if len(res.outputs) != 1:
        ret.value+=4
        ret.lmsg.append("beadm should have only one entry")
    return ret
    # explorer
    # no file under a zfs mount

def get_lmap_hostingname_zone_hosted(lprefix=DEFAULT_LIST_PREFIX_ZONE):
    lret=[]
    #
    # get the list of zones
    lexe=mexecutor.FactoryExecutor.gen_list_from_lprefixhost(lprefix)
    lmap_exe_cmd_result=mexecutor.FactoryFromCmd.create_from_lexe(lexe, cmd_zone_list.CmdListZone())
    lmap_exe_cmd_result.sort(lambda x,y:cmp(x[0].url.hostname,y[0].url.hostname))
    #
    # for each zone, ask the hostname
    lmap_exe_cmd_related=[]
    for exe, unused_cmd, result, related in lmap_exe_cmd_result:
        for zone in result.outputs:
            if zone.zonename == "global":
                continue
            fun_get_hostname=cmd_zone_hostname.CmdZoneHostname(zone.zonename)
            lmap_exe_cmd_related.append((exe, fun_get_hostname, zone))
    lmap_exe_cmd_result_related=mexecutor.FactoryFromCmd.create(lmap_exe_cmd_related)
    for exe, unused_cmd, result, related in lmap_exe_cmd_result_related:
        lret.append((exe.hostname, related, result.outputs))
    return lret

def move_zonename_to_hostingname(zonename, hostingname):
    print "we are going to move zone(%s) to host(%s)" %(zonename,hostingname)
    #
    lmap_hostname_zone=get_lmap_hostname_zone()
    cur_hostname=None
    for hostname, zone in lmap_hostname_zone:
        if zone.zonename==zonename:
            cur_hostname=hostname
            break
    #
    if not cur_hostname:
        print "unable to find zone(%s)"
        sys.exit(1)
    #
    # check
    print "  - check that zone(%s) is elligible for a move:" % zonename
    hostedname=zone.get_hostname()
    result=check_hostname(hostedname)
    if result.value:
        print "    - zone (%s) did not successfully succeed the check" % zone.zonename
        for line in result.lmsg:
            print "      -  %s" % line
    else:
        print "    - done"
    #
    # move zone
    exe_source=mexecutor.Relation.get_exe(zone)
    res=exe_source.run("df %s" % zone.zonepath)
    zpoolname=re.search("^(\S+)/", res.stdout[1]).groups()[0]
    cmd_export_str="/usr/local/bin/exportzone %s" % zpoolname
    print "  - command *export zone* on host (%s) is: %s" % (exe_source.hostname, cmd_export_str)
    res=exe_source.run(cmd_export_str)
    if res.status:
        print "     error in the exportzone, cmd(%s)" % cmd_export_str
        for line in res.stdout:
            print "      %s" % line
        sys.exit(0)
    print "    - zpool(%s) exported" % zpoolname
    #check exported
    cmd_import_str="/usr/local/bin/importzone %s" % zpoolname
    exe_target=mexecutor.FactoryExecutor.gen_for_hostname(hostingname)
    print "  - command *import zone* on host(%s) is: %s" % (hostingname, cmd_import_str)
    res=exe_target.run(cmd_import_str)
    if res.status:
        print "     error in the importzone, cmd(%s)" % cmd_import_str
        for line in res.stdout:
            print "   %s" % line
        sys.exit(0)
    print "    - zpool(%s) successfully imported on host(%s)" % (zpoolname, hostingname)
    # wait until the zone is up
    print "  - wait that the zone is up"
    print "    - wait that it is running"
    i=0
    max_seconds=30
    while i<max_seconds:
        zone=filter(lambda x:zonename==x.zonename,exe_target.run(cmd_zone_list.CmdListZone()).outputs)[0]
        if zone.state=="running":
            print "     - zone is running"
            break
        i+=1
        time.sleep(1)
    zone=filter(lambda x:zonename==x.zonename,exe_target.run(cmd_zone_list.CmdListZone()).outputs)[0]
    print "    - wait that it is running"
    i=0
    max_seconds=30
    while i<max_seconds:
        if zone.state=="running":
            print "     - zone is running"
            break
        i+=1
        time.sleep(1)
    print "   - connect with zlogin"
    i=0
    max_seconds=5
    while i<max_seconds:
        resp=zone.zlogin("ls -l")
        if 0 == resp.status:
            print "     - success"
            break
        print ".",
        time.sleep(1)




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
        parser_list_zonename = subparsers.add_parser('list-zonename', help='list global zonename zonename-host')
        parser_list_zonename.add_argument("prefixes", type=str, help="on which prefixes (eg:webzone,sapzone for webzone1,2,5 and sapzone1)")
        parser_list_zonename.set_defaults(func=get_lmap_hostname_zone)
        # execute
        parser_shell_this = subparsers.add_parser('execute-shell', help='execute a shell command')
        parser_shell_this.add_argument("--all-zones", action='store_true', help="do also on all zones" )
        parser_shell_this.add_argument("--prefixes", type=str, help="on which prefixes (eg:webzone,sapzone for webzone1,2,5 and sapzone1)")
        parser_shell_this.add_argument("--hosts", type=str, help="on which hosts (eg:zone1,zone2)")
        parser_shell_this.add_argument("cmd", type=str, help="commande to invoke (eg: 'ls -l')")
        parser_shell_this.set_defaults(func=execute_shell)
        # checks zonename
        parser_check_zonename = subparsers.add_parser('check-zonename', help='do some checks on the zone')
        parser_check_zonename.add_argument("--zonenames", type=str, help="on wich zonename(eg: zone1,zone2)")
        parser_check_zonename.add_argument("--prefixes", type=str, help="on which prefixes(eg:webzone,sapzone for webzone1,2,5 and sapzone1)")
        parser_check_zonename.set_defaults(func=check_hostname)
        # get hostname
        parser_list_hostname = subparsers.add_parser('list-hosting-zonename-hosted', help='')
        parser_list_hostname.add_argument("--prefixes", type=str, help="on which prefixes(eg:webzone,sapzone for webzone1,2,5 and sapzone1)")
        parser_list_hostname.set_defaults(func=get_lmap_hostingname_zone_hosted)
        # ugzone moves --// zone,zone,zone globalzone zone globalzone zone,zone,zone globalzone
        parser_move_zone = subparsers.add_parser('move-zone', help='')
        parser_move_zone.add_argument("zonename", type=str, help="zonename (e.g. portail1…)")
        parser_move_zone.add_argument("hostingname", type=str, help="a globalzone where the zone should lands (e.g. dropzone1…)")
        parser_move_zone.set_defaults(func=move_zonename_to_hostingname)

        # Process arguments
        args = parser.parse_args()
        if "where-are" == args.sub:
            lmaphostzone=args.func(args.zonenames.split(","))
            for hostname, zone in lmaphostzone:
                print zone.zonename+" on "+hostname
        elif "list-zonename" == args.sub:
            lmap_hostname_zone=args.func(args.prefixes.split(","))
            for hostname, zone in lmap_hostname_zone:
                print hostname, ":", zone.zonename
        elif "execute-shell"  == args.sub:
            lhostname= [] if None==args.hosts else args.hosts.split(",")
            lprefixhostname= [] if None==args.prefixes else args.prefixes.split(",")
            lresp=args.func(args.cmd, lhostname=lhostname, lprefixhostname=lprefixhostname, is_on_all_zones=args.all_zones)
            print "\n".join(lresp)
        elif "check-zonename" == args.sub:
            for zonename in args.zonenames.split(","):
                args.func(zonename)
        elif "list-hosting-zonename-hosted" == args.sub:
            lprefixhostname= [] if None==args.prefixes else args.prefixes.split(",")
            lresp=args.func(lprefix=lprefixhostname)
            for hostingname, zone, hosted in lresp:
                print hostingname, zone.zonename, hosted
        elif "move-zone" == args.sub:
            args.func(args.zonename, args.hostingname)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_format_exception=traceback.format_exception(exc_type, exc_value
                                                       ,exc_traceback)
        for line in tb_format_exception:
            print line



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

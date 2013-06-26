#!/usr/bin/env python
#
# Stingray Traffic Manager Backend Pool Node checks
# Checks each output of stats perpoolnode and returns an OK/CRIT if
# the pool node is alive/dead. Returns additional performance stats
# as part of the performance data.

__author__ = "Russell Cassidy"
__copyright__ = "Copyright 2012, Iomart Hosting Limited"
__credits__ = "Russell Cassidy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Russell Cassidy"
__email__ = "russell@iomart.com"
__status__ = "Production"

import os
import sys
import json
import subprocess
from pprint import pprint
from StringIO import StringIO

# slb1:~# echo "stats perpoolnode" |/usr/local/zeus/zxtm/bin/zcli --json
# [["per Pool Node statistics"],["Pool / Node","Bytes from","Bytes to","Current","Current Requests","Errors","Failures","Idle","New","Pooled","Max RT","Mean RT","Min RT","State","Total conns"],["ACE Admin HTTP / 192.168.253.11:80",396,336,0,0,0,0,0,1,0,0,0,0,"alive",1],["ACE Admin HTTPS / 192.168.253.11:443",23808,8144,0,0,0,0,0,5,9,0,0,0,"alive",14],["ACE JobSeeker HTTP / 192.168.253.12:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerHealthCare HTTP / 192.168.253.16:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerHigherEd HTTP / 192.168.253.17:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerHousing HTTP / 192.168.253.18:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerLocalGov HTTP / 192.168.253.19:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerPublicLeaders HTTP / 192.168.253.20:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerSchools HTTP / 192.168.253.21:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerSocialCare HTTP / 192.168.253.22:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerSocialEnt HTTP / 192.168.253.23:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerSustainableBus HTTP / 192.168.253.24:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE JobseekerVoluntarySec HTTP / 192.168.253.25:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE Mobile HTTP / 192.168.253.13:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE RecruiterServices HTTP / 192.168.253.14:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE RecruiterServices HTTPS / 192.168.253.14:443",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE UAT HTTP / 192.168.253.27:80",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE UAT HTTPS / 192.168.253.27:443",0,0,0,0,0,0,0,0,0,0,0,0,"alive",0],["ACE WebServices HTTP / 192.168.253.15:80",396,200,0,0,0,0,0,1,0,0,0,0,"alive",1],["ACE WebServices HTTPS / 192.168.253.15:443",0,0,0,0,1,1,0,0,0,0,0,0,"dead",0]]

#[u'Pool / Node',
# u'Bytes from',
# u'Bytes to',
# u'Current',
# u'Current Requests',
# u'Errors',
# u'Failures',
# u'Idle',
# u'New',
# u'Pooled',
# u'Max RT',
# u'Mean RT',
# u'Min RT',
# u'State',
# u'Total conns']

cli = "/usr/local/zeus/zxtm/bin/zcli"
cli_argument = "stats perpoolnode\n"

def get_stats():
    stats = ""
    p = subprocess.Popen([cli, "--json"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write(cli_argument)
    stats = p.stdout.readline()
    return stats

def parse_stats(stats):
    io = StringIO(stats)
    results = json.load(io)
    return results

def main():
    stats = parse_stats(get_stats())
    #pprint(stats)
    for stat in stats[2:]:
        poolnode_name        = stat[0]
        stat_bytes_from      = stat[1]
        stat_bytes_to        = stat[2]
        stat_current         = stat[3]
        stat_current_requests = stat[4]
        stat_errors          = stat[5]
        stat_failures        = stat[6]
        stat_idle            = stat[7]
        stat_new             = stat[8]
        stat_pooled          = stat[9]
        stat_maxrt           = stat[10]
        stat_meanrt          = stat[11]
        stat_minrt           = stat[12]
        stat_state           = stat[13]
        stat_total_conns     = stat[14]

        poolnode_name_fmt = poolnode_name.replace(" ", "_")
        poolnode_state = 3 # unknown

        if stat_state == 'alive':
            poolnode_state = 0 # ok
        elif stat_state == 'dead':
            poolnode_state = 2 # critical

        perf = "bytes_from=%sc|bytes_to=%sc|current=%s|current_requests=%sc|errors=%sc|failures=%sc|"
        perf += "idle=%sc|new=%sc|pooled=%sc|maxrt=%s|meanrt=%s|minrt=%s|total_conns=%sc" 

        perf = perf % (
            stat_bytes_from, stat_bytes_to, stat_current, stat_current_requests, stat_errors,
            stat_failures, stat_idle, stat_new, stat_pooled, stat_maxrt, stat_meanrt, stat_minrt,
            stat_total_conns
            )

        check_response = "%s is %s" % (poolnode_name, stat_state)

        print "%d Stingray_TM_PoolNode_%s %s %s" % (poolnode_state, poolnode_name_fmt, perf, check_response)


if __name__ == "__main__":
    main()


#!/usr/bin/env python
#[root@lb1 ~]# echo "stats session" | /usr/local/zeus/zxtm/bin/zcli --json
#[["ASP session persistence cache"],["Entries","Entries Max","Hit Rate","Hits","Lookups","Misses","Oldest"],[0,2048,0,0,0,0,0],[],["IP session persistence cache"],["Entries","Entries Max","Hit Rate","Hits","Lookups","Misses","Oldest"],[0,2048,0,0,0,0,0],[],["J2EE session persistence cache"],["Entries","Entries Max","Hit Rate","Hits","Lookups","Misses","Oldest"],[0,2048,0,0,0,0,0],[],["SSL session persistence cache"],["Entries","Entries Max","Hit Rate","Hits","Lookups","Misses","Oldest"],[0,2048,0,0,0,0,0],[],["Universal session persistence cache"],["Entries","Entries Max","Hit Rate","Hits","Lookups","Misses","Oldest"],[0,2048,0,0,0,0,0]]

import os
import sys
import json
import subprocess
from StringIO import StringIO

cli = "/usr/local/zeus/zxtm/bin/zcli"
cli_argument = "stats session\n"

def get_session_stats():
	session_stats = ""
	p = subprocess.Popen([cli, "--json"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
	p.stdin.write(cli_argument)
	session_stats = p.stdout.readline()
	return session_stats

def parse_session_stats(session_stats):
	io = StringIO(session_stats)
	json = json.load(io)
	return json

def main():
	session_stats = parse_session_stats(get_session_stats())
	pprint session_stats

main()
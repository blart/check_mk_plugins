#!/usr/bin/env python

""" Zeus Load Balancer license checker for check_mk """

import sys
import os
import time
import datetime
import subprocess
import socket
from pprint import pprint

__author__ = "Hereward Cooper, Russell Cassidy"
__copyright__ = "Copyright 2012, Iomart Hosting Limited"
__credits__ = ["Hereward Cooper", "Russell Cassidy"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Russell Cassidy"
__email__ = "russell@iomart.com"
__status__ = "Production"


# Local IP address - used to bind the licence to the host.
ip = socket.gethostbyname(socket.gethostname())

path = "/usr/local/zeus/zxtm/conf/licensekeys"

dir = os.listdir(path)

def get_license_info():
	licenses = {}
	for file in dir:
		results = {}
		fullpath = path + "/" + file
		p = subprocess.Popen(["/usr/local/zeus/zxtm/bin/zeus.zxtm", "--decodelicense", fullpath], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in p.stdout.readlines():
			field = line.split(':')[0]
			value = line.split(':')[1].strip('\n')
			results[field.lstrip()] = value.lstrip()
		licenses[file]=results
	return licenses

def check_licence_expiry(current_timestamp,expires_timestamp):
	license_life_seconds = expires_timestamp - current_timestamp
	one_week = 86400*7;
	one_month = one_week * 4;
	level = 3
	if (license_life_seconds > one_month ): 
		level = 0
	elif (license_life_seconds <= one_month and license_life_seconds > one_week):
		level = 1
	elif (license_life_seconds <= one_week):
		level = 2
	return level



def parse_licenses(licenses):
	output = ""
	level = 3
	for license in licenses:
		try:
			lic_ip = licenses[license]['IP Address']

			if ip != lic_ip:
				#print "%s not found" % ip
				continue

			if "Key is valid for this machine" in licenses[license]['Status']:
				level = check_licence_expiry(time.time(), int(licenses[license]['Expires']))
				expires_formatted = datetime.datetime.fromtimestamp(int(licenses[license]['Expires'])).strftime('%Y-%m-%d %H:%M:%S')
				output += "Serial %s [%s] - Expires %s, " % (licenses[license]['Serial'], licenses[license]['Status'], expires_formatted)
		except KeyError:
			if "Key is valid for this machine" in licenses[license]['Status']:
				level = check_licence_expiry(time.time(), int(licenses[license]['Expires']))
				expires_formatted = datetime.datetime.fromtimestamp(int(licenses[license]['Expires'])).strftime('%Y-%m-%d %H:%M:%S')
				output += "Serial %s [%s] - Expires %s, " % (licenses[license]['Serial'], licenses[license]['Status'], expires_formatted)

		# If we get to here and no status has been set, default to critical - needs investigation.
		if output == "":
			level = 2
			output += "No valid licenses found - investigation required!"
	return "%i Zeus_Licenses - %s" % (level, output)

def main():
	licenses = get_license_info()
	results = parse_licenses(licenses)
	print results

main()


#!/usr/bin/env python

""" Zeus Load Balancer license checker for check_mk
    Deploy to /usr/lib/check_mk_agent/local/zeus_licenses.py
"""

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
__version__ = "1.0.1"
__maintainer__ = "Russell Cassidy"
__email__ = "russell@iomart.com"
__status__ = "Production"


# Local IP address - used to bind the licence to the host.
ip = socket.gethostbyname(socket.gethostname())

path = "/usr/local/zeus/zxtm/conf/licensekeys"
zcli = "/usr/local/zeus/zxtm/bin/zcli"
zxtm = "/usr/local/zeus/zxtm/bin/zeus.zxtm"

get_license_arg = "System.LicenseKeys.getCurrentLicenseKey\n"

dir = os.listdir(path)

def get_license_id():
	licence_id = "";
	p = subprocess.Popen([zcli, "--json"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.stdin.write(get_license_arg)
	license_id = p.stdout.readline().strip('\n')
	return license_id

def get_license_detail(license_id):
	license_detail = {}
	fullpath = path + "/" + license_id
	p = subprocess.Popen([zxtm, "--decodelicense", fullpath], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		field = line.split(':')[0]
		value = line.split(':')[1].strip('\n')
		license_detail[field.lstrip()] = value.lstrip()
	return license_detail

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

def parse_license(license_detail):
	output = ""
	level = 3
	try:
		lic_ip = license_detail['IP Address']

		if "Key is valid for this machine" in license_detail['Status']:
			level = check_licence_expiry(time.time(), int(license_detail['Expires']))
			expires_formatted = datetime.datetime.fromtimestamp(int(license_detail['Expires'])).strftime('%Y-%m-%d %H:%M:%S')
			output += "Serial %s [%s] - Expires %s" % (license_detail['Serial'], license_detail['Status'], expires_formatted)
	except KeyError:
		if "Key is valid for this machine" in license_detail['Status']:
			level = check_licence_expiry(time.time(), int(license_detail['Expires']))
			expires_formatted = datetime.datetime.fromtimestamp(int(license_detail['Expires'])).strftime('%Y-%m-%d %H:%M:%S')
			output += "Serial %s [%s] - Expires %s" % (license_detail['Serial'], license_detail['Status'], expires_formatted)

		# If we get to here and no status has been set, default to critical - needs investigation.
		if output == "":
			level = 2
			output += "No valid licenses found - investigation required!"
	return "%i Zeus_Licenses - %s" % (level, output)

def main():
	license = get_license_id()
	license_detail = get_license_detail(license)
	results = parse_license(license_detail)
	print results

main()

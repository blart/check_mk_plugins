#!/usr/bin/env python
#
# Quick Nagios check given list of directories and return sizes. Array contains
# list of directories and their warning/critical levels in megabytes. To be used
# as a local check on a host with cmk.
#

''' List of local directories that we want to monitor '''
directories = [
 ("/home/russell/dir", 50, 120),
]

import os

''' Returns total directory size in bytes '''
def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size

''' Returns a nice format '''
def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def main():
    for directory, warning, critical in directories:
        status = 3 #unknown
        remark = 'UNKNOWN'
        size_b = getFolderSize(directory)
        # convert from b to mb and round.
        size = int(size_b/1024/1024)
        if size >= critical:
            status = 2 # critical
            remark = 'CRITICAL'
        elif size >= warning and size < critical:
            status = 1 # warning
            remark = 'WARNING'
        else:
            status = 0
            remark = 'OK'

        message = "%s is %s (size of %s)" % (directory, remark, sizeof_fmt(size))
        print "%d Dir_Size_%s %dMB %s" % (status, directory, size, message)

if __name__ == "__main__":
    main()

# vim:ts=4:shiftwidth=4:expandtab:ai

#!/usr/bin/env python26

""" VMware Host Metrics """

# Instead of checking the VMware host metrics via the cumbersome op5 perl script
# we can use pysphere and only check on the items we actually want. This should 
# on overhead with perl forking.
#
# This is a legacy style Nagios check so needs to return the correct exit codes
# to indicate the status of the check carried out.
#
# Example usage:
# extra_nagios_conf += r"""
#
## ARG1: hostname in vCenter
## ARG2: metric to check
#define command {
#    command_name    check_vi_host_metric
#    command_line    $USER1$/vmware_host_metrics.py $ARG1$ $ARG2$
#}
#"""
#
# legacy_checks += [
#( ( "check_vi_host_metric!hostname!cpu", "VMware Host CPU", True ), [ "vmwarehost"] ),
#]


__author__ = "Russell Cassidy"
__copyright__ = "Copyright 2012, Iomart Hosting Limited"
__credits__ = ["Hereward Cooper", "Russell Cassidy"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Russell Cassidy"
__email__ = "russell@iomart.com"
__status__ = "Production"

# Retrieve our host objects for the specific metric we are after. The host metrics should be configured in the
# vmware_configuration.py.  The VMware vCenter configuration is specified there as well to keep authentication
# out of this script. 
# Returns the properties for the host we require.

def vi_retrieve_host_objects(host,properties):
    s = VIServer()
    s.connect(vi_configuration["VI_HOST"], vi_configuration["VI_USER"], vi_configuration["VI_PASS"])

    # If we can't find this host in the get_hosts() output then it doesn't exist
    # on this vCenter. We catch this with an indexError and return false to be
    # detected upstream. Can we do this quicker? Takes ~2s to retrieve the hosts
    # on a loaded 4.1 vCenter.
    try:
        from_host = [k for k,v in s.get_hosts().items() if v == host][0]
        result = s._retrieve_properties_traversal(property_names=properties,from_node=from_host,obj_type=MORTypes.HostSystem)[0]
    except IndexError:
        result = False
    s.disconnect()
    return result

# Parse results for CPU stats. Return CPU values.
def parse_cpu_results(item):
    hostStats= {} # empty holding var to generate a quick dict list.
    for p in item.PropSet:
        field = p.Name
        value = p.Val
        hostStats[field]=value

    name          = hostStats["name"]
    cpu_cores     = hostStats['hardware.cpuInfo.numCpuCores']
    # casting as floats to prevent integer division leaving us with 0s.
    cpu_per_core  = float(hostStats["hardware.cpuInfo.hz"])
    cpu_usage     = float(hostStats["summary.quickStats.overallCpuUsage"])
    cpu_available = ( cpu_per_core * cpu_cores ) / 1024 / 1024 #from Hz to MHz
    cpu_perc      = (cpu_usage/cpu_available) * 100

    return [cpu_perc, cpu_usage]

# Parse results for Memory stats.
def parse_mem_results(item):
    hostStats= {} # empty holding var to generate a quick dict list.
    for p in item.PropSet:
        field = p.Name
        value = p.Val
        hostStats[field]=value

    # casting as floats to prevent integer division leaving us with 0s.
    mem_usage     = float(hostStats["summary.quickStats.overallMemoryUsage"])
    # Convert from bytes to Mb to match the overallMemoryUsage metric. Consistent! :-(
    mem_available = float(hostStats["hardware.memorySize"])/1024/1024
    mem_perc = ( mem_usage / mem_available ) * 100
    return [mem_perc, mem_usage]

# Take the results, sanity check and then call our individual check.
# This check calculates the status for each metric based on the return.
def parse_results(result,metric):
  
    if result == False:
        status_level = "UNKNOWN"
        perf_data = vi_metrics_status[metric][0] % (0, vi_thresholds[metric][0], vi_thresholds[metric][1])
        status_string = vi_metrics_status[metric][1] % (status_level, "not found - host missing from vCenter")

        return [status_level, perf_data, status_string]

    else:
        
        if metric == 'cpu':
            [cpu_perc, cpu_usage] = parse_cpu_results(result)


            if cpu_perc >= vi_thresholds[metric][1]:
                status_level="CRITICAL"
            elif cpu_perc < vi_thresholds[metric][1] and cpu_perc >= vi_thresholds[metric][0]:
                status_level="WARNING"
            else:
                status_level="OK"

            short_str = "%0.2f%% (%0.2fGHz used)" % (cpu_perc, (cpu_usage/1024)) # format from MHz->GHz for readability

        elif metric == "mem":
            [mem_perc, mem_usage] = parse_mem_results(result)
            if mem_perc >= vi_thresholds[metric][1]:
                status_level="CRITICAL"
            elif mem_perc < vi_thresholds[metric][1] and mem_perc >= vi_thresholds[metric][0]:
                status_level="WARNING"
            else:
                status_level="OK"

            short_str = "%0.2f%% (%0.2fGb used)" % (mem_perc, (mem_usage/1024)) # format from Mb->Gb for readability

        perf_data = vi_metrics_status[metric][0] % (0, vi_thresholds[metric][0], vi_thresholds[metric][1])
        
        status_string = vi_metrics_status[metric][1] % (status_level, short_str)

        return [status_level, perf_data, status_string]

def help():
    print "./vmware_host_metrics.py esxi_host_name metric"
    print "Accepted metrics: %s" % ', '.join(map(str, vi_metrics_accepted))
    sys.exit(vi_nagios_status["UNKNOWN"])

# Main run of the script.
if __name__ == "__main__":

    import sys
    from pysphere import VIServer, MORTypes
    from pysphere.resources import VimService_services as VI
    from vmware_configuration import *

    args = sys.argv

    if len(args) == 3:

        host = args[1]
        metric = args[2]

        # Check the accepted metrics
        try:
            vi_metrics_accepted.index(metric)
        except ValueError:
            help()

        # Substitute the correct stats that we require.
        if metric == "cpu":
            properties = vi_cpu_properties
        elif metric == "mem":
            properties = vi_mem_properties

        result = vi_retrieve_host_objects(host, properties)
        [status_level, perf_data, status_string] = parse_results(result, metric)

        #print status_level
        #print perf_data
        print "%s | %s" % (status_string, perf_data)
        sys.exit(vi_nagios_status[status_level])

    else:
         help()








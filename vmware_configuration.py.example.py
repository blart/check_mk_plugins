#!/usr/bin/env python26
#
# Configuration values for connecting to VMware vCenter and other odds and ends.

# vCenter connection for doing host checks.
vi_configuration = {
	"VI_HOST": "IP",
 	"VI_USER": "Username",
 	"VI_PASS": "Password",
}

# Nagios exit values.
vi_nagios_status = {
    "OK": 0,
    "WARNING": 1,
    "CRITICAL": 2,
    "UNKNOWN": 3
}

# The metrics we accept.
vi_metrics_accepted = ["cpu", "mem"]

# The metric output. Perf status and general message.
vi_metrics_status = {
    "mem": ["vmware_mem=%0.2f%%;%d;%d;0;100", "%s - Memory Utilisation %s"],
    "cpu": ["vmware_cpu=%0.2f%%;%d;%d;0;100", "%s - CPU Utilisation %s"],
}

# Utilisation thresholds. Warning and Critical
vi_thresholds = {
  "mem": [80, 90],
  "cpu": [80, 90],
} 

# VMware API properies for the memory check.
vi_mem_properties = [
    "name",
    "summary.quickStats.overallMemoryUsage",   
    "hardware.memorySize",
]

# VMware API properties to calculate CPU usage.
vi_cpu_properties = [
    "name",
    "summary.quickStats.overallCpuUsage",
    "hardware.cpuInfo.hz",
    "hardware.cpuInfo.numCpuCores",
    "hardware.cpuInfo.numCpuPackages",
    "hardware.cpuInfo.numCpuThreads",
]

if __name__ == "__main__":
        print "This file is not meant to be called directly."
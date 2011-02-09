#!/usr/bin/python
import os
import subprocess
import sys
import threading
import time


added_to_path = False
if '/etc' not in sys.path:
    sys.path.insert(0, '/etc')
    added_to_path = True

try:
    import multicommandconfig
except ImportError:
    print "Couldn't import config. Please create /etc/multicommandconfig.py"
    sys.exit(1)

if added_to_path:
    del sys.path[0]


YELLOW="\x1b[33;40m"
GREEN="\x1b[32;40m"
WHITE="\x1b[0m"

def exec_ssh_command(host, cmd):
    ssh_cmd = """ssh -T %s <<'EOF'
    %s 
EOF""" % (host, cmd)
    p = subprocess.Popen(ssh_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()

def get_systems(host_group):
    return multicommandconfig.hostgroups[host_group]

def list_groups(color=True):
    groups = sorted(multicommandconfig.hostgroups.keys())
    for g in groups:
        if color:
            print "%s%s%s: %s" % (GREEN, g, WHITE,  ",".join(get_systems(g)))
        else:
            print "%s: %s" % (g, ",".join(get_systems(g)))

def issue_command(host_group, command_arg, count=8):
    output_lock = threading.Lock()

    # Here comes a cheesy hack
    try:
        systems = get_systems(host_group)
        states = {}
        for s in systems:
            states[s] = "never ran"

    except KeyError:
        sys.stdout.write("%s is not a valid host group\n" % host_group)
        sys.exit(1)

    class IssueCommandThread ( threading.Thread ):
        def __init__(self, hosts, command):
            self.hosts = hosts
            self.command = command
            threading.Thread.__init__(self)
            self.setDaemon(True)

        def run(self):
            for host in self.hosts:
                states[host] = 'did not finish'
                stdout, stderr = exec_ssh_command(host, self.command)
                output =  "%s===%s===%s\n" % (GREEN, host, WHITE)
                output += stdout
                command_err = stderr
                output_lock.acquire()
                print output
                if command_err:
                    print "====ERRORS===="
                    print command_err
                output_lock.release()
                del states[host]

    if sys.argv.__len__() == 1:
        print "usage: $0 <command to run on remote servers>";
        sys.exit()

    threads = {}
    systems_iter = iter(systems)
    for i in range(count):
        threads[i] = IssueCommandThread(systems_iter, command_arg)
        threads[i].start()

    try:
        for t in threads:
            threads[t].join()
    except KeyboardInterrupt:
        for s in systems:
            try:
                print "%s%s%s %s" % (GREEN, s, WHITE, states[s])
            except KeyError:
                pass

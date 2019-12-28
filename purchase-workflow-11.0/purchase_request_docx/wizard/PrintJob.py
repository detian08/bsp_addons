# chose an implementation, depending on os
import os
import platform
import time

if platform.system() == 'Windows':  # sys.platform == 'win32':
    import win32api
    import win32print
elif platform.system() == 'Linux':
    import subprocess
else:
    raise Exception("Sorry: no implementation for your platform ('%s') available" % platform.system())


def print_job(filename):
    if platform.system() == 'Windows':
        do_print_windows(filename)
    if platform.system() == 'Linux':
        do_print_linux(filename)


def do_print_windows(filename):
    win32api.ShellExecute(
        0,
        "print",
        filename,
        #
        # If this is None, the default printer will
        # be used anyway.
        #
        '/d:"%s"' % win32print.GetDefaultPrinter(),
        ".",
        0
    )


def do_print_linux(filename):
    printer_name = "Epson-L120"
    cmd = '/usr/bin/lpr -P {} {}'.format(printer_name, filename)
    lpr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    lpr.stdin.write(filename)
#
#
# import commands, os, string
# import sys
# import fileinput
# import subprocess
# from subprocess import Popen, PIPE
# import shlex
# cmd = "cat /tmp/test.log"
# args = shlex.split(cmd)
# p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# out, err = p.communicate()
# print out

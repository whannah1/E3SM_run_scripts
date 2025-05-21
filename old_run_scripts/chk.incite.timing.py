#!/usr/bin/env python
#===================================================================================================
#  Nov, 2017 - Walter Hannah - Lawrence Livermore National Lab
#  This script checks the output logs of current E3SM cases (i.e. debug mode, compset, misc flags, etc.)
#===================================================================================================
import sys
import os
import fileinput
from glob import glob
import subprocess
import re
from optparse import OptionParser
parser = OptionParser()
# Set up terminal colors
class bcolor:
    ENDC     = '\033[0m'
    BLACK    = '\033[30m'
    RED      = '\033[31m'
    GREEN    = '\033[32m'
    YELLOW   = '\033[33m'
    BLUE     = '\033[34m'
    MAGENTA  = '\033[35m'
    CYAN     = '\033[36m'
    WHITE    = '\033[37m'
#===================================================================================================
#===================================================================================================
parser.add_option('-n',dest='num_file',default=-1,help='number of files to print')
(opts, args) = parser.parse_args()

# case = 'INCITE2019.GPU.ne120pg2.FC5AV1C-H01A.SP1_64x1_1000m.20191026'
case = 'INCITE2019_TIMING.GPU.ne120pg2.FC5AV1C-H01A.SP1_64x1_1000m.20191026'

param_list = ['Throughput','Run Time    :','ATM Run Time','\"a:crm\"','a:CAM_run3','a:CAM_run4']

# param_list = ['Run Time    :']
# param_list = ['Throughput','TOT Run Time','CPL Run Time:','ATM Run Time','LND Run Time','OCN Run Time','ICE Run Time']

#===================================================================================================
#===================================================================================================

timing_dir = os.getenv('HOME')+'/E3SM/Cases/'+case+'/timing'

# make sure all logs are unzipped
os.system('gunzip '+timing_dir+'/*.gz ')

# print latest stat files
print('\n'+bcolor.MAGENTA+'latest timing files: '+bcolor.ENDC)
cmd = 'ls -t '+timing_dir+'/e3sm_timing* | head -n 2'
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
(msg, err) = proc.communicate()
msg = msg.split('\n')
for line in msg: 
    line = line.replace(os.getenv('HOME')+'/','~/')
    print(line)
print()

for param in param_list :
    # grep for the appropriate line in the stat files
    cmd = 'grep  \''+param+'\'  '+timing_dir+'/*'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    (msg, err) = proc.communicate()
    msg = msg.split('\n')

    stat_file = msg[0].split(':')[0]

    # Clean up message but don't print yet
    for m in range(len(msg)): 
        line = msg[m]
        line = line.replace(timing_dir+'/','')
        line = line.replace('e3sm_timing.'+case+'.','e3sm_timing        ')
        line = line.replace('e3sm_timing_stats.'   ,'e3sm_timing_stats  ')
        msg[m] = line

    # print stat file header with indentation
    if 'a:' in param : 
        head = subprocess.check_output(['head',stat_file],universal_newlines=True).split('\n')
        for line in head: 
            if 'walltotal' in line:
                indent = len(msg[0].split(':')[0])+1
                line = ' '*indent+line
                hline = line
                # Get rid of some dead space
                line = line.replace('name        ','name')
                print(hline)
                break
    
    # set up character indices for color
    if 'a:' in param:
        n1 = hline.find('walltotal')    +len('walltotal')
        n2 = hline.find('wallmax')      +len('wallmax')
        n3 = hline.find('wallmax')      +len('wallmax (proc   thrd  )')
        n4 = hline.find('wallmin')      +len('wallmin')
    else:
        line = msg[0]
        n1 = line.replace(':','', 1).find(':')+2
        num_in_list = re.findall(r'\d+\.\d+', line[n1:])
        n2 = line.find(num_in_list[0])+len(num_in_list[0])

    # print the timing data
    num_file = -int(opts.num_file)-1
    if opts.num_file==-1 : num_file = -len(msg)
    for line in msg[num_file:] : 
        if 'a:' in param : 
            line = line[:n1] \
                  +bcolor.CYAN  +line[n1:n2]+bcolor.ENDC +line[n2:n3] \
                  +bcolor.GREEN +line[n3:n4]+bcolor.ENDC +line[n4:]
            # Get rid of some dead space
            line = line.replace('        ','')
        else:
            line = line[:n1] \
                  +bcolor.GREEN +line[n1:n2]+bcolor.ENDC \
                  +line[n2:]
            # Print conversion to min aand hours for specific params
            offset = len(bcolor.GREEN)
            if param=='Run Time    :' and line[n1+offset:n2+offset]!='' :
                sec = float( line[n1+offset:n2+offset] )
                line = line+'  ('+bcolor.GREEN+f'{sec/60:.2f}'     +bcolor.ENDC+' min)'
                line = line+'  ('+bcolor.GREEN+f'{sec/60/60:.2f}'  +bcolor.ENDC+' hour)'
        print(line)

        # n1 = line.replace(':','', 1).find(':')+2
        # num_in_list = re.findall(r'\d+\.\d+', line[n1:])
        # print(f' {num_in_list[0]}    {float(num_in_list[0])/60:8.2f}    {float(num_in_list[0])/3600:8.2f} ')




#===================================================================================================
#===================================================================================================

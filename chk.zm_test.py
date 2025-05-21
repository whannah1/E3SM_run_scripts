#!/usr/bin/env python3
#=============================================================================================================
#  May, 2018 - Walter Hannah - Lawrence Livermore National Lab
#  This script checks the status of the latest regression test
#=============================================================================================================
import sys
import os
import fileinput
# import numpy as np
from glob import glob
import subprocess as sp
home = os.getenv('HOME')

from optparse import OptionParser
parser = OptionParser()

# parser.add_option('--no-indent',action='store_false', dest='indent_flag', default=True,help='do not indent long variables')
parser.add_option('-n',dest='num_test',default=1,help='sets number of tests to search for. Only considers tests newer than newest baseline.')
parser.add_option('-b',action='store_true', dest='show_base', default=False,help='show recent base status instead of test')
parser.add_option('-t',action='store_true', dest='show_test', default=False,help='show recent test status instead of base')
# parser.add_option('-t',action='store_true', dest='truncate_flag', default=False,help='truncate output for small screens')
parser.add_option('-m',dest='method',default=2,help='Method of checking tests - 0=parse logs, 1=use cs.status script, 2=abbrev. version of 1 ')
parser.add_option('--no-color',action='store_false', dest='use_color', default=True,help='disable colored output')

parser.add_option('--test',dest='user_test',default=None,help='user specified test')
parser.add_option('--base',dest='user_base',default=None,help='user specified base')

(opts, args) = parser.parse_args()
num_test     = int(opts.num_test)
method       = int(opts.method)

#=============================================================================================================
#=============================================================================================================
# Set up terminal colors
class tclr:
    END      = '\033[0m'
    BLACK    = '\033[30m'
    RED      = '\033[31m'
    GREEN    = '\033[32m'
    YELLOW   = '\033[33m'
    BLUE     = '\033[34m'
    MAGENTA  = '\033[35m'
    CYAN     = '\033[36m'
    WHITE    = '\033[37m'

def print_line(line_length=80,char='-'):
    dline = ''
    for c in range(line_length): dline+= char
    print(dline)

def run_cmd(cmd,verbose=False,suppress_output=False,execute=True):
    if suppress_output : cmd = cmd + ' > /dev/null'
    msg = tclr.GREEN + cmd + tclr.END
    if verbose: print(f'\n{msg}')
    if execute:
        (msg,err) = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
        return msg
    else:
        return
#=============================================================================================================
#=============================================================================================================

mach = None
if os.path.exists('/lcrc/group/e3sm/ac.whannah'):   mach='lcrc'
if os.path.exists('/pscratch/sd/w/whannah'):        mach='nersc'

if mach is None: raise ValueError('Unable to detect machine!')

if mach=='lcrc':  test_root = '/lcrc/group/e3sm/ac.whannah/ZM_testing'
if mach=='nersc': test_root = '/pscratch/sd/w/whannah/e3sm_scratch/ZM_testing'

#---------------------------------------------------------------
# Find the most recent test and baseline case directories
#---------------------------------------------------------------
msg = run_cmd(f'ls -1dt {test_root}/* ')

case_dirs = msg.rstrip().split('\n')

test_count = 0
base_count = 0

newest_base_dir = []
newest_test_dir = []

for case_dir in case_dirs :

    if case_dir==f'{test_root}/baselines': continue

    # search "base" directories
    if opts.user_base is None and base_count < num_test :
        if '_base' in case_dir.replace(f'{test_root}/',''):
            newest_base_dir.append(case_dir)
            base_count = base_count+1
    
    # search "test" directories
    if opts.user_test is None and test_count < num_test : 
        if '_test' in case_dir.replace(f'{test_root}/',''):
            newest_test_dir.append(case_dir)
            test_count = test_count+1

#---------------------------------------------------------------

# if no tests found then just show newest baseline
if opts.user_test is None and opts.user_base is None:
    # deal with case where either test or base list is empty
    if len(newest_test_dir)==0 and len(newest_base_dir)>0:
        newest_test_dir.append(newest_base_dir[0])
    if len(newest_base_dir)==0 and len(newest_test_dir)>0:
        newest_base_dir.append(newest_test_dir[0])

    if newest_test_dir[0] is None and newest_base_dir[0] is not None:
        newest_test_dir[0] = newest_base_dir[0]
    else:
        # if baseline is newer then newest test then just use the baseline
        if 'newest_base_dir' in locals():
            for base_dir in newest_base_dir[::-1]:
                test_dir = newest_test_dir[0]
                base_time_code = base_dir.replace(f'{test_root}/','')
                test_time_code = test_dir.replace(f'{test_root}/','')
                base_time_code = base_time_code.replace('_base','').replace('_test','')
                test_time_code = test_time_code.replace('_test','').replace('_base','')
                base_time_code = base_time_code.replace('-','').replace('_','')
                test_time_code = test_time_code.replace('-','').replace('_','')
                base_time_code = int(base_time_code)
                test_time_code = int(test_time_code)
                if base_time_code > test_time_code:
                    print()
                    print('Baseline is newer than most recent test')
                    newest_test_dir = newest_base_dir
        else:
            newest_base_dir = ['NONE']

#---------------------------------------------------------------
# set "current" base/test to be shown
if opts.user_base is None:
    current_base_dir = newest_base_dir#[0]
else:
    current_base_dir = [opts.user_base]

if opts.user_test is None:
    current_test_dir = newest_test_dir#[0]
else:
    current_test_dir = [opts.user_test]

#---------------------------------------------------------------
# print the names of the relevant cases
print()
print(f'base:  {current_base_dir[0]}')
print(f'test:  {current_test_dir[0]}')
print()

#---------------------------------------------------------------
# parse the test status depending on the desired method

if opts.show_base or opts.show_test :
    if opts.show_base and opts.show_test :
        raise ValueError('ERROR: cannot specify both -b and -t flags')
    else:
        if opts.show_base: current_test_dir = current_base_dir
        # if opts.show_test: current_test_dir = current_base_dir

if method in [1,2] :

    # test_dir = current_test_dir
    for test_dir in current_test_dir[::-1] :

        if num_test>1:
            print()
            print_line(line_length=120,char='*')
            print(f'test path: {test_dir}')
            print_line(line_length=120,char='*')
            print()

        msg = run_cmd(f'ls -t {test_dir}/cs.status* ')

        scripts = msg.split('\n')

        # for s in scripts: print(s)
        # exit()

        for script in scripts:

            if num_test==1 : print_line()

            msg = run_cmd(script)

            for line in msg.split('\n') :

                if opts.use_color :
                    clr = ''
                    if 'FAIL'   in line : clr = tclr.RED
                    if 'NLFAIL' in line : clr = tclr.GREEN
                    if 'PASS'   in line : clr = tclr.GREEN
                    if 'PEND'   in line : clr = tclr.YELLOW
                    if 'DIFF'   in line : clr = tclr.MAGENTA
                    line = line.replace('FAIL',  clr+'FAIL'  +tclr.END)
                    line = line.replace('NLFAIL',clr+'NLFAIL'+tclr.END)
                    line = line.replace('PASS',  clr+'PASS'  +tclr.END)
                    line = line.replace('PEND',  clr+'PEND'  +tclr.END)
                    line = line.replace('DIFF',  clr+'DIFF'  +tclr.END)

                if method==1 :
                    if line.strip()!='': print(line)

                if method==2 :
                    # first_word = line.strip().split(' ')[0]
                    test_name = None
                    if 'Overall' in line and line.strip()!='': 
                        line = line.replace(' details:','')
                        # reformat to align status string
                        line_split = line.split(' ')
                        for l,line in enumerate(line_split):
                            if any([x in line for x in ['SMS','ERS','ERP']]):
                                line_split[l] = f'{line_split[l]:80}'
                        line = ' '.join(line_split)
                        test_name = line.strip().split()[0]
                        # if FAIL or DIFF is detected then print some extra stuff
                        mline_list = []
                        if 'FAIL' in line and not 'NLFAIL' in line:
                            for mline in msg.split('\n') :
                                if 'Overall' not in mline and 'FAIL' in mline and f'{test_name} ' in mline: 
                                    if 'MEMLEAK' in mline:
                                        line = f'{line} ({tclr.YELLOW}MEMLEAK{tclr.END})'
                                    elif 'MODEL_BUILD' in mline:
                                        line = f'{line} ({tclr.YELLOW}MODEL_BUILD{tclr.END})'
                                    else:
                                        mline_list.append( mline.replace('FAIL',  tclr.RED+'FAIL'  +tclr.END) )
                        elif 'DIFF' in line:
                            for mline in msg.split('\n') :
                                if 'Overall' not in mline and 'FAIL' in mline and f'{test_name} ' in mline: 
                                    print(line)
                                    mline_list.append( mline.replace('FAIL',  tclr.RED+'FAIL'  +tclr.END) )
                        # print the line
                        print(line)
                        if mline_list!=[]: 
                            for l in mline_list: print(l)

            if method==1 :
                if num_test>1 and script!=scripts[-1]: print_line()

        if method==1 :
            # print name of log file
            msg = run_cmd(f'ls {test_dir}/*log ')
            logs = msg.rstrip().split('\n')
            for log in logs :
                print('    '+log)
            print()

        


elif method==0:

    for test_dir in current_test_dir[::-1] :

        if num_test>1:
            print()
            print_line(line_length=120,char='*')
            print(f'test path: {test_dir}')
            print_line(line_length=120,char='*')
            print()

        msg = run_cmd(f'ls {test_dir}/*log ')
        logs = msg.rstrip().split('\n')

        for log in logs :
            logfile_obj  = open(str(log),'r')
            lines = logfile_obj.read().split('\n')
            num_lines = len(lines)
            cnt = 0
            out_cnt = 0

            lines_out = ''

            line0 = int(1e6)
            test_cnt = 0
            for l,line in enumerate(lines) :
                ### first print dashed line separator
                if cnt==0 and num_test==1 : print_line()

                ### grab list of test names
                if "RUNNING TESTS:" in line:
                    line0 = l
                    test_cnt,test_list,full_test_name = 0,[],[]
                    for n in range(1,100):
                        tline = lines[l+n]
                        if tline[0:2] == '  ':
                            test_list.append(tline.strip())
                            test_cnt += 1
                        else:
                            break
                    for t in test_list: 
                        tdir = glob(f'{test_dir}/{t}*')#[0]
                        if tdir==[]:
                            full_test_name.append('')
                        else:
                            full_test_name.append(tdir[0].replace(f'{test_dir}/',''))

                ### add full test name to line with short name
                tl = (line0+test_cnt)
                if l>line0 and l<=(line0+test_cnt):
                    line = tclr.YELLOW + line + tclr.END
                    line = f'{line:80}  {full_test_name[l-line0-1]}'

                ### add path to TestStatus.log and e3sm.log* files
                if 'Case dir:' in line:
                    case_dir = line.replace('    Case dir: ','')
                    line += '\n'+line.replace('Case dir','Log file')+'/TestStatus.log'
                    os.chdir(case_dir)
                    run_dir = run_cmd('./xmlquery RUNDIR --value')
                    e3sm_logs = run_cmd(f'ls -1t {run_dir}/e3sm.log*')
                    if isinstance(e3sm_logs, list):
                        latest_e3sm_log = e3sm_logs[0]
                    else:
                        latest_e3sm_log = e3sm_logs
                    line += f'\n    E3SM log: {latest_e3sm_log}'

                ### color the output of the log file
                if opts.use_color :
                    clr = ''
                    if 'FAIL'   in line : clr = tclr.RED
                    if 'NLFAIL' in line : clr = tclr.GREEN
                    if 'PASS'   in line : clr = tclr.GREEN
                    if 'DIFF'   in line : clr = tclr.MAGENTA
                    line = line.replace('FAIL', clr+'FAIL'  +tclr.END)
                    line = line.replace('NLFAIL',clr+'NLFAIL'+tclr.END)
                    line = line.replace('PASS',  clr+'PASS'  +tclr.END)
                    line = line.replace('DIFF',  clr+'DIFF'  +tclr.END)

                    for err_str in ['Error','ERROR','error'] :
                        line = line.replace(err_str,tclr.RED+err_str+tclr.END)

                    txt = 'Waiting for tests to finish'
                    line = line.replace(txt,tclr.MAGENTA+txt+tclr.END)

                    if "Starting" in line: continue

                    # if "RUNNING TESTS:" in line:
                    #     line = line.replace("RUNNING TESTS:","RUNNING TESTS:"+tclr.YELLOW)

                    if "Creating test directory" in line:
                        line = line.replace("Creating test directory",tclr.CYAN+"Creating test directory"+tclr.END)

                    if "finished with status" in line:
                        line = line.replace("Test \'","Test \'"+tclr.YELLOW)
                        line = line.replace("\' finished",tclr.END+"\' finished")

                    line = line.replace('Finished',tclr.CYAN+'finished'+tclr.END)
                    if 'finished with status' in line:
                        line = line.replace('finished',tclr.CYAN+'finished'+tclr.END)

                ### consturct the final string
                tline = line
                if opts.truncate_flag and (num_lines-cnt) > 4 : 
                    tline = ''
                    # if cnt==0 : tline = '...\n'
                        
                if tline!='' :
                    if out_cnt>0 : lines_out = lines_out + '\n'
                    lines_out = lines_out + tline 
                    out_cnt = out_cnt + 1

                    # For failed test, print line of section that failed
                    if 'Path: ' in line :
                        status_file = line.replace('    Path: ','')
                        msg = run_cmd(f'grep \'FAIL\' {status_file} ')
                        for msg_line in msg.rstrip().split('\n') :
                            if opts.use_color :
                                msg_line = msg_line.replace('FAIL', tclr.RED+'FAIL'+tclr.END)
                            lines_out = lines_out + '\n' + '      ' + msg_line 
                            out_cnt = out_cnt + 1
                
                cnt = cnt+1

            print(lines_out)

            if num_test>1 and log!=logs[-1]: print_line()

        if opts.show_base : continue

#---------------------------------------------------------------
#---------------------------------------------------------------

print()
# print_line(line_length=60)


#=============================================================================================================
#=============================================================================================================

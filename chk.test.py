#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
import sys, os, fileinput, subprocess as sp, glob
import chk_methods
host = chk_methods.get_host()
home = chk_methods.home
tclr = chk_methods.tclr
#---------------------------------------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser()
# parser.add_option('--no-indent',action='store_false', dest='indent_flag', default=True,help='do not indent long variables')
parser.add_option('-n',dest='num_test',default=1,help='sets number of tests to search for. Only considers tests newer than newest baseline.')
parser.add_option('-b',action='store_true', dest='show_base', default=False,help='show recent baseline status instead of test')
parser.add_option('-t',action='store_true', dest='truncate_flag', default=False,help='truncate output for small screens')
parser.add_option('-m',dest='method',default=0,help='Method of checking tests - 0=parse logs, 1=use cs.status script')
parser.add_option('--no-color',action='store_false', dest='use_color', default=True,help='disable colored output')
(opts, args) = parser.parse_args()
#---------------------------------------------------------------------------------------------------
num_test = int(opts.num_test)
method = int(opts.method)
#---------------------------------------------------------------------------------------------------
def print_line(length=80,char='-'):
    dline = ''
    for c in range(length): dline+= char
    print(dline)
#---------------------------------------------------------------------------------------------------
def run_cmd(cmd,verbose=False,suppress_output=False,execute=True):
    if suppress_output : cmd = cmd + ' > /dev/null'
    msg = tclr.GRN + cmd + tclr.END
    if verbose: print(f'\n{msg}')
    if execute:
        (msg,err) = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
        return msg
    else:
        return
#=============================================================================================================
#=============================================================================================================

# test_top_dir = '/lustre/atlas/proj-shared/cli115/hannah6'
# case_top_dir = home+'/E3SM/test_cases'

case_top_dir = '/lcrc/group/e3sm/whannah/e3sm_scratch/tests'

# /ccs/home/hannah6/E3SM/test_cases/2018-05-07_225340/ERP_Ld3_P96.ne4_ne4.FSP1V1-TEST.titan_pgi.C.20180507_185340_cc07db/TestStatus

# /lustre/atlas/proj-shared/cli115/hannah6/
# ERP_Ld3_P96.ne4_ne4.FSP1V1-TEST.titan_pgi.C.20180507_185340_cc07db
# /run/
# ERP_Ld3_P96.ne4_ne4.FSP1V1-TEST.titan_pgi.C.20180507_185340_cc07db.cpl.hi.0001-01-04-00000.nc.cprnc.out

#---------------------------------------------------------------
# Find the most recent test and baseline case directories
#---------------------------------------------------------------
msg = run_cmd(f'ls -1dt {case_top_dir}/* ')

case_dirs = msg.rstrip().split('\n')

test_count = 0
base_count = 0

for case_dir in case_dirs :
    # if 'newest_base_dir' not in vars():
    if base_count < num_test :
        if '_baseline'     in case_dir : 
            # newest_base_dir = case_dir
            if 'newest_base_dir' not in vars(): newest_base_dir = []
            newest_base_dir.append(case_dir)
            base_count = base_count+1
    
    if test_count < num_test : 
        if '_baseline' not in case_dir: 
            if 'newest_test_dir' not in vars(): newest_test_dir = []
            newest_test_dir.append(case_dir)
            test_count = test_count+1
        
### if no tests then check baseline
if 'newest_test_dir' not in vars() and 'newest_base_dir' in vars() : newest_test_dir = newest_base_dir


### if no valid test case then exit
# if 'newest_test_dir' not in vars(): print('ERROR: no recent test case was found!')      #; exit()
# if 'newest_base_dir' not in vars(): print('ERROR: no recent baseline case was found! ') #; exit()


### if baseline case is newer then just use the baseline
if 'newest_base_dir' in locals():
    for base_dir in newest_base_dir[::-1] :
        base_time_code = int( base_dir.replace(case_top_dir+'/','').replace('_baseline','').replace('-','').replace('_','') )
        test_time_code = int( base_dir.replace(case_top_dir+'/','').replace('_baseline','').replace('-','').replace('_','') )
        if base_time_code > test_time_code:  
            print('\n\nBaseline is newer than most recent test\n\n')
            newest_test_dir = newest_base_dir
else:
    newest_base_dir = ['NONE']

### print the names of the relevant cases
print
print('Most recent baseline:  '+newest_base_dir[0])
print('Most recent test:      '+newest_test_dir[0])
print

#---------------------------------------------------------------
# check the top level log for the most recent test
#---------------------------------------------------------------

if opts.show_base : newest_test_dir = newest_base_dir

if method==1 :

    # test_dir = newest_test_dir
    for test_dir in newest_test_dir[::-1] :

        if num_test>1:
            print()
            print_line(length=120,char='*')
            print(f'test path: {test_dir}')
            print_line(length=120,char='*')
            print()

        msg = run_cmd(f'ls {test_dir}/cs.status* ')

        scripts = msg.split('\n')
        
        for script in scripts:

            if num_test==1 : print_line()

            msg = run_cmd(script)

            lines = msg.split('\n')
            for line in lines :

                if opts.use_color :
                    clr = ''
                    if 'FAIL'   in line : clr = tclr.RED
                    if 'NLFAIL' in line : clr = tclr.GRN
                    if 'PASS'   in line : clr = tclr.GRN
                    if 'PEND'   in line : clr = tclr.YLW
                    if 'DIFF'   in line : clr = tclr.MGN
                    line = line.replace('FAIL',  clr+'FAIL'  +tclr.END)
                    line = line.replace('NLFAIL',clr+'NLFAIL'+tclr.END)
                    line = line.replace('PASS',  clr+'PASS'  +tclr.END)
                    line = line.replace('PEND',  clr+'PEND'  +tclr.END)
                    line = line.replace('DIFF',  clr+'DIFF'  +tclr.END)

                if line.strip()!='': print(line)

            if num_test>1 and script!=scripts[-1]: print_line()

        # print name of log file
        msg = run_cmd(f'ls {test_dir}/*log ')
        logs = msg.rstrip().split('\n')
        for log in logs :
            print('    '+log)
        print


else:

    for test_dir in newest_test_dir[::-1] :

        if num_test>1:
            print()
            print_line(length=120,char='*')
            print(f'test path: {test_dir}')
            print_line(length=120,char='*')
            print()

        # if opts.show_base : 
        #     test_dir = newest_base_dir

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
                        tdir = glob.glob(f'{test_dir}/{t}*')#[0]
                        if tdir==[]:
                            full_test_name.append('')
                        else:
                            full_test_name.append(tdir[0].replace(f'{test_dir}/',''))

                ### add full test name to line with short name
                tl = (line0+test_cnt)
                if l>line0 and l<=(line0+test_cnt):
                    line = tclr.YLW + line + tclr.END
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
                    if 'NLFAIL' in line : clr = tclr.GRN
                    if 'PASS'   in line : clr = tclr.GRN
                    if 'DIFF'   in line : clr = tclr.MGN
                    line = line.replace('FAIL', clr+'FAIL'  +tclr.END)
                    line = line.replace('NLFAIL',clr+'NLFAIL'+tclr.END)
                    line = line.replace('PASS',  clr+'PASS'  +tclr.END)
                    line = line.replace('DIFF',  clr+'DIFF'  +tclr.END)

                    for err_str in ['Error','ERROR','error'] :
                        line = line.replace(err_str,tclr.RED+err_str+tclr.END)

                    txt = 'Waiting for tests to finish'
                    line = line.replace(txt,tclr.MGN+txt+tclr.END)

                    if "Starting" in line: continue

                    # if "RUNNING TESTS:" in line:
                    #     line = line.replace("RUNNING TESTS:","RUNNING TESTS:"+tclr.YLW)

                    if "Creating test directory" in line:
                        line = line.replace("Creating test directory",tclr.CYN+"Creating test directory"+tclr.END)

                    if "finished with status" in line:
                        line = line.replace("Test \'","Test \'"+tclr.YLW)
                        line = line.replace("\' finished",tclr.END+"\' finished")

                    line = line.replace('Finished',tclr.CYN+'finished'+tclr.END)
                    if 'finished with status' in line:
                        line = line.replace('finished',tclr.CYN+'finished'+tclr.END)

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
# print_line(length=60)


#=============================================================================================================
#=============================================================================================================

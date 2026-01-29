#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
import os, fileinput, glob, subprocess as sp
import chk_methods
host = chk_methods.get_host()
home = chk_methods.home
tclr = chk_methods.tclr
#---------------------------------------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--no-indent',action='store_false', dest='indent_flag', default=True,help='do not indent long variables')
parser.add_option("--all",action="store_true", dest="use_all_logs", default=False,help="check all available logs")
parser.add_option("--nstep",action="store_true", dest="nstep_only", default=False,help="only print nstep values")
parser.add_option("--partial",action="store_true", dest="allow_partial_match", default=False,help="allow partial matches of input search strings")
# parser.add_option('-n',dest='num_file',default=5,help='sets number of files to print')
parser.add_option('-n',dest='num_line',default='10',help='sets number of lines to print')
parser.add_option('--alt',dest='alt_search_str',default='E3SM',help='Sets search string (i.e. "E3SM") to use when searching case name')
(opts, args) = parser.parse_args()
num_file = 1
#---------------------------------------------------------------------------------------------------
# specify string lengths for nice formatting
indent_len  = 40
xmlfile_len = 15
param_len   = 20
total_len   = indent_len + xmlfile_len + param_len
# use multiple lines for variables with long values
status_len_limit = 80
#---------------------------------------------------------------------------------------------------

top_dir = chk_methods.get_scratch_path_list()

# make sure list of top dir's don't end with "/"
for t,top_dir_tmp in enumerate(top_dir) :
    if top_dir_tmp[-1]=='/': top_dir[t] = top_dir[t][0:-1]

dirs = []
for top_dir_tmp in top_dir : 
    dirs = dirs + glob.glob(f'{top_dir_tmp}/*')

ndir = len(dirs)

if len(args) < 1 :
    # exit('\nERROR: no search string provided!\n')
    
    cmd = 'ls -1dt '
    for td in top_dir: cmd += f' {td}/*'

    proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True)
    (msg, err) = proc.communicate()
    
    search_strings = [ msg.rstrip().split('\n')[0].split('/')[-1] ]

else :
    search_strings = args

#---------------------------------------------------------------------------------------------------
# Loop through case directories

cnt = 0
for tdir in dirs :
    case = tdir
    for top_dir_tmp in top_dir :
        case = tdir
        case = case.replace(top_dir_tmp+'/','')
        if '/' in case: continue
        
        # if test_case in case: print(f'  {case}  {top_dir_tmp:40}  {tdir}')
    
        is_test_flag = False
        is_test_flag = any( f'{test_type}_' in case for test_type in ['SMS','ERS','ERP'])

        if ('E3SM' in case 
            or 'SCREAM' in case 
            or 'DP.' in case 
            or 'ELM_spinup' in case 
            or 'INCITE' in case 
            or 'DPSCREAM' in case 
            or '.v3alpha' in case
            or 'v3.F2010' in case 
            or 'SOHIP' in case 
            or '2025-EACB' in case 
            or is_test_flag
            or opts.alt_search_str in case) and 'old_' not in case :

            found = True
            if search_strings : 
                found = False
                for sub_string in search_strings :
                    flag = (sub_string.strip() == case.strip())
                    # if test_case in case: print(f'    {sub_string:80}  {case:80}  {flag}')
                    if opts.allow_partial_match:
                        if sub_string in case : found = True
                    else:
                        if sub_string == case : found = True
            # if test_case in case: print(f'\nfound: {found}')

            ### Other conditions might be met, but discard if there's no "run" directory
            if not os.path.isdir(tdir+'/run'): found = False

            ### If we found the to the case run directory, then identify the latest logs and parse
            if found :
                #-------------------------------------------------------
                #-------------------------------------------------------
                
                ### print case name
                case_str = case.ljust(indent_len)
                case_str = tclr.ULN+case_str+tclr.ULNOFF
                case_str = tclr.BLD   +case_str+tclr.END
                print('\n'+case_str+'\n')

                if len( glob.glob(tdir+'/run/e3sm.log*') )==0: 
                    print(tclr.RED+'  NO LOG FILES???'+tclr.END)
                    continue

                ### Get the names of all e3sm logs
                cmd = 'ls  '+tdir+'/run/e3sm.log* | tail -n '+str(num_file)+' '
                proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True)
                (msg, err) = proc.communicate()

                ### Pad each log file name with leading spaces
                file_list = msg.replace(home,'    '+home)

                file_list = file_list.replace('\n','')

                # print(file_list)
                if '.gz' in file_list: 
                    print(tclr.GREEN+'  LOG FILES ZIPPED'+tclr.END+f'  {file_list}')
                    continue

                if opts.use_all_logs :
                    ### get all logs
                    cmd = 'tail -n '+opts.num_line+' '+file_list.replace('e3sm','*')  
                else: 
                    cmd = 'tail -n '+opts.num_line+' '+file_list
                    #cmd = cmd+' '+file_list.replace('e3sm','cpl')  
                    if 'WCYCL' in case : cmd = cmd+' '+file_list.replace('e3sm','ocn')
                    # cmd = cmd+' '+file_list.replace('e3sm','atm')
                    if 'MAML' in case:
                        cmd = cmd+' '+file_list.replace('e3sm','atm_0001')
                    else:
                        cmd = cmd+' '+file_list.replace('e3sm','atm')
                    cmd = cmd+' '+file_list.replace('e3sm','homme_atm')

                    ### only atm log
                    # cmd = 'tail -n '+opts.num_line+' '+file_list.replace('e3sm','atm')
                
                if opts.nstep_only:
                    
                    cmd = 'grep "nstep," '+file_list.replace('e3sm','atm')+' | tail -n '+opts.num_line
                    proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True)
                    (nstep_msg, err) = proc.communicate()
                    msg = nstep_msg.rstrip().split('\n')
                
                else:

                    # print(); print(cmd); print()

                    proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True)
                    # proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True)
                    (msg, err) = proc.communicate()

                    # (msg, err) = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
                    # msg = sp.check_output([cmd],universal_newlines=True)

                    # msg = msg.decode('utf-8','ignore').encode('utf-8')
                    # msg = msg.decode('ascii')
                    # msg = msg.decode('utf-8')

                    # print(); print(msg); print()

                    ### split by line return
                    msg = msg.rstrip().split('\n')

                    if all('nstep, te' not in m for m in msg) :
                        # cmd = ' echo ; grep "nstep" '+file_list.replace('e3sm','atm')+' | tail -n '+opts.num_line
                        cmd = 'grep "nstep" '+str(file_list.replace('e3sm','atm'))+' | tail -n 5 '
                        proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True)
                        (nstep_msg, err) = proc.communicate()
                        if nstep_msg!='' : 
                            msg.append('')
                            msg.append(cmd)
                            msg = msg + nstep_msg.rstrip().split('\n')


                # color the output and print
                for line in msg:
                    if 'atm.log'        in line : line = tclr.MGN + line + tclr.END
                    if 'homme_atm.log'  in line : line = tclr.MGN + line + tclr.END
                    if 'lnd.log'        in line : line = tclr.GRN + line + tclr.END
                    if 'e3sm.log'       in line : line = tclr.CYN + line + tclr.END
                    if 'ocn.log'        in line : line = tclr.BLU + line + tclr.END
                    if '==>'            in line : line = tclr.YLW + line + tclr.END
                    if 'ERROR'          in line : line = tclr.RED + line + tclr.END
                    print('  '+line)

                #-------------------------------------------------------
                #-------------------------------------------------------
                cnt = cnt+1

#---------------------------------------------------------------------------------------------------

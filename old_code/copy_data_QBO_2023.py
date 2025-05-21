#!/usr/bin/env python
import sys,os,subprocess as sp, glob
class tclr: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+tclr.GREEN+cmd+tclr.END) ; os.system(cmd); return
# def run_cmd(cmd): print('  '+tclr.GREEN+cmd+tclr.END) ; return
#---------------------------------------------------------------------------------------------------
case_name,src_path,dst_path = [],[],[]
def add_case(case_in,src_in,dst_in):
  global case_name,src_path,dst_path
  case_name.append(case_in)
  src_path.append(src_in.replace('${CASE}',case_in))
  dst_path.append(dst_in.replace('${CASE}',case_in))

#---------------------------------------------------------------------------------------------------
do_h0, do_h1, do_h2, overwrite = False, False, False, False

# do_h0 = True
do_h1 = True
do_h2 = True

overwrite = False

scratch = '/pscratch/sd/w/whannah/e3sm_scratch'
cfs = '/global/cfs/cdirs/m4310/whannah/E3SM'

add_case('E3SM.QBO-TEST-03.F2010.ne30pg2.L72'      ,scratch+'/pm-cpu/${CASE}/run',cfs+'/${CASE}/run')
add_case('E3SM.QBO-TEST-03.F2010.ne30pg2.L72-nsu40',scratch+'/pm-cpu/${CASE}/run',cfs+'/${CASE}/run')
add_case('E3SM.QBO-TEST-03.F2010.ne30pg2.L72-rlim' ,scratch+'/pm-cpu/${CASE}/run',cfs+'/${CASE}/run')
add_case('E3SM.QBO-TEST-03.F2010.ne30pg2.L72-rscl' ,scratch+'/pm-cpu/${CASE}/run',cfs+'/${CASE}/run')

#---------------------------------------------------------------------------------------------------
for c in range(len(case_name)):
  print(f'case     : {case_name[c]}')

  atm_comp = 'eam'

  if not os.path.exists(dst_path[c]): os.mkdir(dst_path[c])

  hist_files = sorted( glob.glob(f'{src_path[c]}/*eam.h*nc') )

  for f_in in hist_files:

    copy_flag = False
    if do_h0  and f'{atm_comp}.h0' in f_in : copy_flag = True
    if do_h1  and f'{atm_comp}.h1' in f_in : copy_flag = True
    if do_h2  and f'{atm_comp}.h2' in f_in : copy_flag = True

    if copy_flag:

      f_out = f_in.replace(src_path[c],dst_path[c])

      if os.path.isfile(f_out) :
        if overwrite : os.remove(f_out)
        else : continue
      
      run_cmd(f'cp {f_in} {f_out}')

      # exit()


#---------------------------------------------------------------------------------------------------
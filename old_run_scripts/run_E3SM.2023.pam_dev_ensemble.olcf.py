#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => master + updated PAM submodule

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'debug'  # batch / debug 
arch = 'GNUGPU' # GNUCPU / GNUGPU

# compset='FSCM-ARM97-MMF1'
compset='F2010-MMF2'
# compset='FSCM-ARM97-MMF2'
# compset='FSCM-ARM97-MMF2-AWFL'

if queue=='debug': stop_opt,stop_n,resub,walltime = 'nsteps', 20,0,'0:30'
# if queue=='debug': stop_opt,stop_n,resub,walltime = 'ndays', 1,0,'0:30'
# if queue=='batch' and '2010' in compset: stop_opt,stop_n,resub,walltime = 'ndays', 1,0,'1:00'
if queue=='batch' and '2010' in compset: stop_opt,stop_n,resub,walltime = 'ndays', 5,1,'5:00'
if queue=='batch' and 'SCM'  in compset: stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00'
# if queue=='batch': stop_opt,stop_n,resub,walltime = 'ndays',28,0,'2:00'


if 'FSCM'  in compset: 
   ne,npg = 4,0;grid=f'ne{ne}_ne{ne}';        num_nodes=1
else:
   ne,npg,grid = 30,2,'ne30pg2_EC30to60E2r2'; num_nodes = 32
   # ne,npg,grid = 4,2,'ne4pg2_ne4pg2';         num_nodes = 1

#---------------------------------------------------------------------------------------------------
case_list = []
grid_list = []
comp_list = []
cdt_list  = []
gdt_list  = []
dpp_list  = []
ssc_list  = []
hdt_list  = []
accel_flag_list = []
fff_list = []
ens_num_list = []
# ens_num = 0 # initial runs - just find limits of time step and subcycling
# ens_num = 1 # try "exact" dycor interpolation
# ens_num = 2 # exact interpolation + new dry density save/recall
# ens_num = 3 # exact interpolation + disable dry density save/recall
def add_case(ens_num,grid,compset,cdt=None,gdt=None,dpp=None,ssc=None,hdt=None,accel_flag=True,fff=None):
   # if dpp is None: dpp = 2
   # if ssc is None: ssc = 0
   # if hdt is None: hdt = 10
   # tmp_list = ['E3SM','2023-PAM-ENS-00',grid,compset,f'CDT_{cdt:02d}',f'DPP_{dpp:02d}',f'SSC_{ssc:02d}',f'HDT_{hdt:04d}']   
   if not accel_flag:
      # tmp_list = ['E3SM','2023-PAM-ENS-00',grid,compset,'NO-MSA',f'CDT_{cdt:02d}',f'DPP_{dpp:02d}',f'SSC_{ssc:02d}',f'HDT_{hdt:04d}']
      # tmp_list = ['E3SM',f'2023-PAM-ENS-{ens_num:02d}',grid,compset,'NO-MSA-UV',f'CDT_{cdt:02d}',f'DPP_{dpp:02d}',f'SSC_{ssc:02d}',f'HDT_{hdt:04d}']
            tmp_list = ['E3SM',f'2023-PAM-ENS-{ens_num:02d}',grid,compset,'NO-MSA-UV',f'CDT_{cdt:02d}',f'DPP_{dpp:02d}',f'HDT_{hdt:04d}']
   else:
      # tmp_list = ['E3SM',f'2023-PAM-ENS-{ens_num:02d}',grid,compset,         f'CDT_{cdt:02d}',f'DPP_{dpp:02d}',f'SSC_{ssc:02d}',f'HDT_{hdt:04d}']
      tmp_list = ['E3SM',f'2023-PAM-ENS-{ens_num:02d}',grid,compset,         f'CDT_{cdt:02d}',f'DPP_{dpp:02d}',f'HDT_{hdt:04d}']
   if fff is not None: tmp_list.append(f'FFF_{fff}')
   if gdt is not None: tmp_list.append(f'GDT_{gdt}')
   ens_num_list.append(ens_num)
   accel_flag_list.append(accel_flag)
   if debug_mode: tmp_list.append('debug')
   case_list.append('.'.join(tmp_list) )
   grid_list.append(grid)
   comp_list.append(compset)
   cdt_list.append(cdt)
   gdt_list.append(gdt)
   dpp_list.append(dpp)
   ssc_list.append(ssc)
   hdt_list.append(hdt)
   fff_list.append(fff)
#---------------------------------------------------------------------------------------------------

# add_case(grid,compset,cdt= 4,dpp=2,ssc=1,hdt=10)
# add_case(grid,compset,cdt= 6,dpp=2,ssc=1,hdt=10)
# add_case(grid,compset,cdt= 8,dpp=2,ssc=1,hdt=10)
# add_case(grid,compset,cdt=10,dpp=2,ssc=1,hdt=10)

# add_case(grid,compset,cdt= 4,dpp=2,ssc=2,hdt=10)
# add_case(grid,compset,cdt= 6,dpp=2,ssc=2,hdt=10)
# add_case(grid,compset,cdt= 8,dpp=2,ssc=2,hdt=10)
# add_case(grid,compset,cdt=10,dpp=2,ssc=2,hdt=10)

# add_case(grid,compset,cdt= 4,dpp=4,ssc=1,hdt=10)
# add_case(grid,compset,cdt= 6,dpp=4,ssc=1,hdt=10)
# add_case(grid,compset,cdt= 8,dpp=4,ssc=1,hdt=10)
# add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=10)

# add_case(grid,compset,cdt= 4,dpp=4,ssc=2,hdt=10)
# add_case(grid,compset,cdt= 6,dpp=4,ssc=2,hdt=10)
# add_case(grid,compset,cdt= 8,dpp=4,ssc=2,hdt=10)
# add_case(grid,compset,cdt=10,dpp=4,ssc=2,hdt=10)

### 5-sec tests for 10-sec comparison

# add_case(grid,compset,cdt=5,dpp=1,ssc=1,hdt=10) # => compare to cdt=10,dpp=2,ssc=2,hdt=10

# add_case(grid,compset,cdt=5,dpp=2,ssc=1,hdt=30)
# add_case(grid,compset,cdt=5,dpp=4,ssc=1,hdt=30)
# add_case(grid,compset,cdt=5,dpp=2,ssc=1,hdt=60)
# add_case(grid,compset,cdt=5,dpp=4,ssc=1,hdt=60)

### 6-sec tests => MSA factor needs update!

# add_case(grid,compset,cdt=6,dpp=2,ssc=1,hdt=30)
# add_case(grid,compset,cdt=6,dpp=4,ssc=1,hdt=30)
# add_case(grid,compset,cdt=6,dpp=6,ssc=1,hdt=30)
# add_case(grid,compset,cdt=6,dpp=8,ssc=1,hdt=30)

# add_case(grid,compset,cdt=6,dpp=2,ssc=1,hdt=60)
# add_case(grid,compset,cdt=6,dpp=4,ssc=1,hdt=60)
# add_case(grid,compset,cdt=6,dpp=6,ssc=1,hdt=60)
# add_case(grid,compset,cdt=6,dpp=8,ssc=1,hdt=60)

### 8-sec tests

# add_case(grid,compset,cdt=8,dpp=2,ssc=1,hdt=10)
# add_case(grid,compset,cdt=8,dpp=4,ssc=1,hdt=10)
# add_case(grid,compset,cdt=8,dpp=6,ssc=1,hdt=10)
# add_case(grid,compset,cdt=8,dpp=8,ssc=1,hdt=10)

# add_case(grid,compset,cdt=8,dpp=2,ssc=1,hdt=30)
# add_case(grid,compset,cdt=8,dpp=4,ssc=1,hdt=30)
# add_case(grid,compset,cdt=8,dpp=6,ssc=1,hdt=30)
# add_case(grid,compset,cdt=8,dpp=8,ssc=1,hdt=30)

# add_case(grid,compset,cdt=8,dpp=2,ssc=1,hdt=60)
# add_case(grid,compset,cdt=8,dpp=4,ssc=1,hdt=60)
# add_case(grid,compset,cdt=8,dpp=6,ssc=1,hdt=60)
# add_case(grid,compset,cdt=8,dpp=8,ssc=1,hdt=60)

# add_case(grid,compset,cdt=8,dpp=4,ssc=1,hdt=60,gdt=20*60)

### 10-sec tests

# add_case(grid,compset,cdt=10,dpp=2,ssc=1,hdt=10)
# add_case(grid,compset,cdt=10,dpp=2,ssc=2,hdt=10)
# add_case(grid,compset,cdt=10,dpp=2,ssc=1,hdt=60)
# add_case(grid,compset,cdt=10,dpp=2,ssc=2,hdt=60)
# add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=10)
# add_case(grid,compset,cdt=10,dpp=4,ssc=2,hdt=10)
# add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=60)
# add_case(grid,compset,cdt=10,dpp=4,ssc=2,hdt=60)

# add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=60,fff=0.5)

# add_case(grid,compset,cdt=10,dpp=40,ssc=1,hdt=60)

# add_case(grid,compset,cdt=10,dpp=8,ssc=1,hdt=60,gdt=10*60)
# add_case(grid,compset,cdt=10,dpp=20,ssc=1,hdt=60,gdt=20*60)

# add_case(grid,compset,cdt=10,dpp=10,ssc=1, hdt=60,gdt=20*60)
# add_case(grid,compset,cdt=10,dpp=10,ssc=10,hdt=60,gdt=20*60)

# add_case(ens_num=2,grid=grid,compset=compset,cdt= 5,dpp=2,ssc=1,hdt=10*60,gdt=20*60)

# add_case(ens_num=2,grid=grid,compset=compset,cdt= 5,dpp=2,ssc=1,hdt=60,gdt=20*60)
# add_case(ens_num=2,grid=grid,compset=compset,cdt= 5,dpp=4,ssc=1,hdt=60,gdt=20*60)
# add_case(ens_num=2,grid=grid,compset=compset,cdt= 8,dpp=2,ssc=1,hdt=60,gdt=20*60)
# add_case(ens_num=2,grid=grid,compset=compset,cdt= 8,dpp=4,ssc=1,hdt=60,gdt=20*60)
# add_case(ens_num=2,grid=grid,compset=compset,cdt=10,dpp=4,ssc=1,hdt=60,gdt=20*60)

add_case(ens_num=2,grid=grid,compset=compset,cdt=5,dpp=2,hdt=10,gdt=20*60)

# add_case(ens_num=3,grid=grid,compset=compset,cdt=10,dpp=4,ssc=1,hdt=60,gdt=20*60)

# add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=60,gdt=10*60)
# add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=60,gdt= 5*60)
# add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=60,gdt= 2*60)
# add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=60,gdt= 1*60)

# add_case(grid,compset,cdt=10,dpp=6,ssc=1,hdt=10)
# add_case(grid,compset,cdt=10,dpp=6,ssc=2,hdt=10)
# add_case(grid,compset,cdt=10,dpp=6,ssc=1,hdt=60)
# add_case(grid,compset,cdt=10,dpp=6,ssc=2,hdt=60)

# add_case(grid,compset,cdt=10,dpp=8,ssc=1,hdt=60)
# add_case(grid,compset,cdt=10,dpp=8,ssc=2,hdt=60)


# add_case(grid,compset,cdt=10,dpp=2,ssc=1,hdt=30)
# add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=30)
# add_case(grid,compset,cdt=10,dpp=6,ssc=1,hdt=30)
# add_case(grid,compset,cdt=10,dpp=8,ssc=1,hdt=30)


### 12-sec tests - need to change MSA - (1+crm_accel_factor) does not divide equally into nstop: 0100

# add_case(grid,compset,cdt=12,dpp=3,ssc=1,hdt=60)
# add_case(grid,compset,cdt=12,dpp=4,ssc=1,hdt=60)
# add_case(grid,compset,cdt=12,dpp=6,ssc=1,hdt=60)

### 16-sec tests

# add_case(grid,compset,cdt=16,dpp=2,ssc=1,hdt=60)
# add_case(grid,compset,cdt=16,dpp=4,ssc=1,hdt=60)
# add_case(grid,compset,cdt=16,dpp=8,ssc=1,hdt=60)
# add_case(grid,compset,cdt=16,dpp=8,ssc=2,hdt=60)
# add_case(grid,compset,cdt=16,dpp=16,ssc=1,hdt=60)

### 20-sec tests

# add_case(grid,compset,cdt=20,dpp= 2,ssc=1,hdt=60)
# add_case(grid,compset,cdt=20,dpp= 4,ssc=1,hdt=60)
# add_case(grid,compset,cdt=20,dpp= 5,ssc=1,hdt=60)
# add_case(grid,compset,cdt=20,dpp=10,ssc=1,hdt=60)
# add_case(grid,compset,cdt=20,dpp=20,ssc=1,hdt=60)


### tests without MSA
#add_case(grid,compset,cdt= 5,dpp=2,ssc=1,hdt=60,accel_flag=False)
#add_case(grid,compset,cdt= 6,dpp=2,ssc=1,hdt=60,accel_flag=False)
#add_case(grid,compset,cdt= 8,dpp=2,ssc=1,hdt=60,accel_flag=False)
#add_case(grid,compset,cdt=10,dpp=2,ssc=1,hdt=60,accel_flag=False)
#add_case(grid,compset,cdt=12,dpp=2,ssc=1,hdt=60,accel_flag=False)
#add_case(grid,compset,cdt=15,dpp=2,ssc=1,hdt=60,accel_flag=False)

#add_case(grid,compset,cdt=10,dpp=4,ssc=1,hdt=60,accel_flag=False)
#add_case(grid,compset,cdt=12,dpp=4,ssc=1,hdt=60,accel_flag=False)
#add_case(grid,compset,cdt=15,dpp=4,ssc=1,hdt=60,accel_flag=False)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
# def main(case,ens_num,grid,compset,cdt,gdt,dpp,ssc,hdt,accel_flag,fff):
def main(case,ens_num,grid,compset,cdt,gdt,dpp,hdt,accel_flag,fff):
   # if nlev is None: exit(' one or more arguments not provided?')

   # print(case); return

   case_dir = os.getenv('HOME')+'/E3SM/Cases/'
   case_root = f'{case_dir}/{case}'

   print('\n  case : '+case+'\n')
   # exit()
   #------------------------------------------------------------------------------------------------
   if 'FSCM' in compset: 
      max_mpi_per_node,atm_nthrds  =  1,1 ; max_task_per_node = 1
   else:
      # if 'CPU' in arch: max_mpi_per_node,atm_nthrds  =  42,1 ; max_task_per_node = 42
      # if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   6,7 ; max_task_per_node = 6
      # if 'CPU' in arch: max_mpi_per_node,atm_nthrds  =  42,1 ; max_task_per_node = 42
      if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   8,1 ; max_task_per_node = 8
   atm_ntasks = max_mpi_per_node*num_nodes
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      #-------------------------------------------------------
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case_root}'
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      cmd += f' --project {acct} '
      cmd += f' --walltime {walltime} '
      cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -mach frontier-scream-gpu -compiler crayclang-scream  '
      # if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      # if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
      run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
      #-------------------------------------------------------
      # if specifying ncdata, do it here to avoid an error message
      if 'init_file_atm' in globals():
         file = open('user_nl_eam','w'); file.write(f' ncdata = \'{init_file_atm}\' \n'); file.close()
      #-------------------------------------------------------
      # if '2023-PAM-ENS-01' in case:
      if ens_num>=1:run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx 45 -crm_nx_rad 3 \" ')
      if cdt is not None: run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {cdt} \" ')
      #-------------------------------------------------------
      cpp_opt = ''
      # if dpp is not None: cpp_opt += f' -DMMF_PAM_DPP={dpp}'
      if hdt is not None: cpp_opt += f' -DMMF_PAM_HDT={hdt}'
      # if ssc is not None: cpp_opt += f' -DMMF_PAM_SSC={ssc}' 
      if fff is not None: cpp_opt += f' -DMMF_PAM_FFF={fff}'
      if ens_num==2: cpp_opt += f' -DMMF_ALT_DENSITY_RECALL'
      if ens_num==3: cpp_opt += f' -DMMF_DISABLE_DENSITY_RECALL'
      if cpp_opt != '' :
         cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
         cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
         run_cmd(cmd)
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit : 
      #-------------------------------------------------------
      # ATM Namelist
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      # file.write(' nhtfrq    = 0,-1,-1 \n')
      # file.write(' mfilt     = 1,24,24 \n')
      file.write(' nhtfrq    = 0,1,1 \n')
      file.write(' mfilt     = 1,72,72 \n')
      file.write(" fincl2 = 'PS','TS','PSL'")
      file.write(          ",'PRECT','TMQ'")
      file.write(          ",'PRECC','PRECL','PRECSC'")
      file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(          ",'FSNT','FLNT','FLUT'")        # Net TOM heating rates
      file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
      file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
      file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
      file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
      file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
      file.write(          ",'Z300:I','Z500:I'")
      file.write(          ",'OMEGA850:I','OMEGA500:I'")
      file.write(          ",'U200:I','V200:I'")
      file.write('\n')
      # if 'FSCM' in compset: 
      if True:
         # 3D variables
         file.write(" fincl3 = 'PS','TS','PSL'")
         file.write(          ",'T','Q','Z3'")                       # 3D thermodynamic budget components
         file.write(          ",'U','V','OMEGA'")                    # 3D velocity components
         file.write(          ",'QRL','QRS'")                        # 3D radiative heating profiles
         file.write(          ",'CLDLIQ','CLDICE'")                  # 3D cloud fields
         # file.write(          ",'QRLC','QRSC'")
         # file.write(          ",'CRM_QRL','CRM_QRLC'")
         file.write(          ",'CRM_U','CRM_W'")
         file.write(          ",'CRM_T','CRM_QV'")
         file.write(          ",'CRM_QC','CRM_QI'")
         file.write('\n')
      
      # if '.NO-MSA.' in case: file.write(f'use_crm_accel = .false. \n')
      # if not accel_flag: file.write(f'use_crm_accel = .false. \n')
      if not accel_flag: file.write(f'crm_accel_uv = .false. \n')

      file.write(f' MMF_PAM_dyn_per_phys = {dpp} \n')

      if gdt is not None:
         if gdt < 60 :
            file.write(f'dt_tracer_factor = 1 \n')
            file.write(f'dt_remap_factor = 1 \n')
            file.write(f'se_tstep = {gdt} \n')
            file.write(f'hypervis_subcycle_q = 1 \n')
         if gdt == 1*60 or gdt == 2*60 :
            file.write(f'dt_tracer_factor = 1 \n')
            file.write(f'dt_remap_factor = 1 \n')
            file.write(f'se_tstep = 60 \n')
            file.write(f'hypervis_subcycle_q = 1 \n')
      
      # file.write(f' cosp_lite = .true. \n')
      if 'init_file_atm' in globals(): file.write(f' ncdata = \'{init_file_atm}\' \n')
      # file.write(" inithist = \'ENDOFRUN\' \n")
      file.close()
      #-------------------------------------------------------
      # LND namelist
      if 'init_file_lnd' in globals() or 'data_file_lnd' in globals():
         nfile = 'user_nl_elm'
         file = open(nfile,'w')
         if 'init_file_lnd' in globals(): file.write(f' finidat = \'{init_file_lnd}\' \n')
         if 'data_file_lnd' in globals(): file.write(f' fsurdat = \'{data_file_lnd}\' \n')
         # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
         file.close()
      #-------------------------------------------------------
      # SCM defaults to NCPL=12 (2 hour time step) - switch back to MMF default 
      # if 'MMF' in compset and 'dtime' not in globals():
      if gdt is None:
         if 'FSCM' in compset and 'MMF' in compset: dtime = 20*60; ncpl = 86400/dtime
      else:
         ncpl = 86400/gdt
      if 'ncpl' in globals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      #-------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':


   for n in range(len(case_list)):
      # print('-'*80)
      main( case_list[n],
            ens_num_list[n],
            grid_list[n],
            comp_list[n],
            cdt_list[n],
            gdt_list[n],
            dpp_list[n],
            # ssc_list[n],
            hdt_list[n],
            accel_flag_list[n],
            fff_list[n])
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

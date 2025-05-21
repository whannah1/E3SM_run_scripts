#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
# NOTE: The branch (whannah/scidac-2023) started 
# with master @ Aug 7 w/ v3atm/eam/master_MAM5_wetaero_chemdyg:
#     commit 915e929b5118243bc2f15b90c4ca911352985524
#     Merge: 855bd01e21 b3454bb277
#     Author: Wuyin Lin <wlin@bnl.gov>
#     Date:   Mon Aug 7 07:47:35 2023 -0700
# but also includes commits to add the hdepth_scaling_factor namelist parameter
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run,reset_resub,st_archive = False,False,False,False,False,False,False,False

acct = 'm4310'
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4' # branch => whannah/scidac-2023
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/scidac-2023

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True
### reset_resub  = True

disable_bfb = True

# queue = 'batch' # batch / debug
num_nodes   = 22
grid        = 'ne30pg2_EC30to60E2r2'
compset     = 'F20TR' # F20TR / F20TR_chemUCI-Linozv3-mam5
nlev        = 80

# stop_opt,stop_n,resub,walltime = 'nsteps',10,0,'0:30:00' 
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365*4,0,'8:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365*2,3-1,'6:00:00' # 6 years
#stop_opt,stop_n,resub,walltime = 'ndays',365*2,5-1,'6:00:00' # 10 years

gweff_list = []
cfrac_list = []
hdpth_list = []

# gweff_list.append(0.35); cfrac_list.append(10); hdpth_list.append(1.00) #  0 - use defaults
# gweff_list.append(0.10); cfrac_list.append(10); hdpth_list.append(1.50) #  2 L72-run # 16
# gweff_list.append(0.35); cfrac_list.append(20); hdpth_list.append(1.00) #  3 L72-run #  3
# gweff_list.append(0.20); cfrac_list.append(20); hdpth_list.append(1.50) #  4 L72-run # 17
# gweff_list.append(0.10); cfrac_list.append(25); hdpth_list.append(0.25) #  5 L72-run # 25

# gweff_list.append(0.20); cfrac_list.append(25); hdpth_list.append(0.50) #  6 L72-run # 22
# gweff_list.append(0.35); cfrac_list.append(10); hdpth_list.append(0.50) #  7 L72-run #  5 ### final for v3
# gweff_list.append(0.35); cfrac_list.append(10); hdpth_list.append(0.25) #  8 L72-run #  2
# gweff_list.append(0.20); cfrac_list.append(10); hdpth_list.append(1.00) #  9 L72-run #  4
# gweff_list.append(0.20); cfrac_list.append(15); hdpth_list.append(0.50) # 10 L72-run #  7

# gweff_list.append(0.09); cfrac_list.append(20); hdpth_list.append(0.25) # 11 L72-run # 10  
# gweff_list.append(0.20); cfrac_list.append(20); hdpth_list.append(1.25) # 12 L72-run # 18  
# gweff_list.append(0.05); cfrac_list.append(25); hdpth_list.append(0.50) # 13 L72-run # 12  
# gweff_list.append(0.80); cfrac_list.append( 1); hdpth_list.append(1.15) # 14 L72-run # 31  
# gweff_list.append(0.90); cfrac_list.append(20); hdpth_list.append(0.25) # 15 L72-run # 14  

# gweff_list.append(0.59); cfrac_list.append(41); hdpth_list.append(0.55) # 16 L72-run # 40  
# gweff_list.append(0.01); cfrac_list.append( 1); hdpth_list.append(0.70) # 17 L72-run # 28  
# gweff_list.append(0.40); cfrac_list.append(10); hdpth_list.append(1.00) # 18 L72-run #  1  
# gweff_list.append(0.70); cfrac_list.append(25); hdpth_list.append(0.90) # 19 L72-run # 30  
# gweff_list.append(0.60); cfrac_list.append( 7); hdpth_list.append(1.35) # 20 L72-run # 38  

### gweff_list.append(0.10); cfrac_list.append(30); hdpth_list.append(0.63) #  1 L72-run # 44 - outlier - can't finish?

# gweff_list.append(0.18); cfrac_list.append(14); hdpth_list.append(0.52)
# gweff_list.append(0.06); cfrac_list.append(13); hdpth_list.append(0.59)
# gweff_list.append(0.22); cfrac_list.append( 8); hdpth_list.append(0.48)
# gweff_list.append(0.35); cfrac_list.append(11); hdpth_list.append(0.66)
# gweff_list.append(0.52); cfrac_list.append(16); hdpth_list.append(0.89)
# gweff_list.append(0.13); cfrac_list.append(10); hdpth_list.append(0.82)

### new runs to extend ensemble
#   EF   CF   HD
# 0.79 0.12 0.72
# 0.78 0.13 0.67
# 0.77 0.09 0.94
# 0.55 0.10 0.38
# 0.63 0.08 0.62
# 0.14 0.10 1.37
# 0.13 0.22 0.56
# gweff_list.append(0.79); cfrac_list.append(12); hdpth_list.append(0.72)
# gweff_list.append(0.78); cfrac_list.append(13); hdpth_list.append(0.67)
# gweff_list.append(0.77); cfrac_list.append( 9); hdpth_list.append(0.94)
# gweff_list.append(0.55); cfrac_list.append(10); hdpth_list.append(0.38)
# gweff_list.append(0.63); cfrac_list.append( 8); hdpth_list.append(0.62)
# gweff_list.append(0.14); cfrac_list.append(10); hdpth_list.append(1.37)
# gweff_list.append(0.13); cfrac_list.append(22); hdpth_list.append(0.56)

### new runs to extend ensemble - 2024-05-02
#   EF   CF   HD
# 0.31 0.11 1.39
# 0.70 0.21 0.31
# 0.81 0.20 0.39
# 0.11 0.18 0.87
# 0.11 0.23 0.86
# 0.13 0.16 1.22
# 0.33 0.17 0.72
# 0.40 0.15 1.17
# 0.43 0.23 0.60
# 0.45 0.20 1.40
# 0.47 0.17 0.46
# 0.60 0.12 1.03
# 0.60 0.15 1.35
# 0.63 0.22 0.78
# 0.67 0.22 1.18
# 0.69 0.17 0.64
# 0.77 0.18 0.93
# 0.86 0.17 0.29
# gweff_list.append(0.31); cfrac_list.append(0.11); hdpth_list.append(1.39)  BAD BAD BAD 
# gweff_list.append(0.70); cfrac_list.append(0.21); hdpth_list.append(0.31)  BAD BAD BAD 
# gweff_list.append(0.81); cfrac_list.append(0.20); hdpth_list.append(0.39)  BAD BAD BAD 
# gweff_list.append(0.11); cfrac_list.append(0.18); hdpth_list.append(0.87)  BAD BAD BAD 
# gweff_list.append(0.11); cfrac_list.append(0.23); hdpth_list.append(0.86)  BAD BAD BAD 
# gweff_list.append(0.13); cfrac_list.append(0.16); hdpth_list.append(1.22)  BAD BAD BAD 
# gweff_list.append(0.33); cfrac_list.append(0.17); hdpth_list.append(0.72)  BAD BAD BAD 
# gweff_list.append(0.40); cfrac_list.append(0.15); hdpth_list.append(1.17)  BAD BAD BAD 
# gweff_list.append(0.43); cfrac_list.append(0.23); hdpth_list.append(0.60)  BAD BAD BAD 
# gweff_list.append(0.45); cfrac_list.append(0.20); hdpth_list.append(1.40)  BAD BAD BAD 
# gweff_list.append(0.47); cfrac_list.append(0.17); hdpth_list.append(0.46)  BAD BAD BAD 
# gweff_list.append(0.60); cfrac_list.append(0.12); hdpth_list.append(1.03)  BAD BAD BAD 
# gweff_list.append(0.60); cfrac_list.append(0.15); hdpth_list.append(1.35)  BAD BAD BAD 
# gweff_list.append(0.63); cfrac_list.append(0.22); hdpth_list.append(0.78)  BAD BAD BAD 
# gweff_list.append(0.67); cfrac_list.append(0.22); hdpth_list.append(1.18)  BAD BAD BAD 
# gweff_list.append(0.69); cfrac_list.append(0.17); hdpth_list.append(0.64)  BAD BAD BAD 
# gweff_list.append(0.77); cfrac_list.append(0.18); hdpth_list.append(0.93)  BAD BAD BAD 
# gweff_list.append(0.86); cfrac_list.append(0.17); hdpth_list.append(0.29)  BAD BAD BAD 

# relaunch after noticing error in CF values
# gweff_list.append(0.31); cfrac_list.append(11); hdpth_list.append(1.39)
# gweff_list.append(0.70); cfrac_list.append(21); hdpth_list.append(0.31)
# gweff_list.append(0.81); cfrac_list.append(20); hdpth_list.append(0.39)
# gweff_list.append(0.11); cfrac_list.append(18); hdpth_list.append(0.87)
# gweff_list.append(0.11); cfrac_list.append(23); hdpth_list.append(0.86)
# gweff_list.append(0.13); cfrac_list.append(16); hdpth_list.append(1.22)
# gweff_list.append(0.33); cfrac_list.append(17); hdpth_list.append(0.72)
# gweff_list.append(0.40); cfrac_list.append(15); hdpth_list.append(1.17)
# gweff_list.append(0.43); cfrac_list.append(23); hdpth_list.append(0.60)
# gweff_list.append(0.45); cfrac_list.append(20); hdpth_list.append(1.40)
# gweff_list.append(0.47); cfrac_list.append(17); hdpth_list.append(0.46)
# gweff_list.append(0.60); cfrac_list.append(12); hdpth_list.append(1.03)
# gweff_list.append(0.60); cfrac_list.append(15); hdpth_list.append(1.35)
# gweff_list.append(0.63); cfrac_list.append(22); hdpth_list.append(0.78)
# gweff_list.append(0.67); cfrac_list.append(22); hdpth_list.append(1.18)
# gweff_list.append(0.69); cfrac_list.append(17); hdpth_list.append(0.64)
# gweff_list.append(0.77); cfrac_list.append(18); hdpth_list.append(0.93)
# gweff_list.append(0.86); cfrac_list.append(17); hdpth_list.append(0.29)

### failing runs?
# gweff_list.append(0.69); cfrac_list.append(17); hdpth_list.append(0.64)
# gweff_list.append(0.60); cfrac_list.append(12); hdpth_list.append(1.03)
# gweff_list.append(0.45); cfrac_list.append(20); hdpth_list.append(1.40)

### new ensemble extension - 2024-07-09
# EF = 0.12, CF = 16, HD = 0.48
# EF = 0.04, CF = 20, HD = 0.75
gweff_list.append(0.12); cfrac_list.append(16); hdpth_list.append(0.48)
gweff_list.append(0.04); cfrac_list.append(20); hdpth_list.append(0.75)

din_loc_root = '/global/cfs/cdirs/e3sm/inputdata'
init_scratch = '/global/cfs/cdirs/m4310/whannah/HICCUP/data/'

# land_init_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/'
land_data_path = f'{din_loc_root}/lnd/clm2/surfdata_map'
if grid=='ne30pg2_EC30to60E2r2': 
   # land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   if 'F2010' in compset: land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'
   if 'F20TR' in compset: land_data_file = 'surfdata_ne30pg2_simyr1850_c210402.nc'

RUN_REFDATE = '1984-01-01'
REF_SCRATCH = '/global/cfs/cdirs/m4310/whannah/E3SM/'
RUN_REFCASE = '20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(e=None,c=None,h=None):
   if h is None or c is None or e is None: exit(' one or more arguments not provided?')

   case = '.'.join(['E3SM','2023-SCIDAC',grid,'AMIP',f'EF_{e:0.2f}',f'CF_{c:02.0f}',f'HD_{h:0.2f}'])

   # print(case)
   # return

   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'

   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print('\n  case : '+case+'\n')
   atm_ntasks,atm_nthrds = num_nodes*128,1
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      # Check if directory already exists   
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      cmd += f' --machine pm-cpu '
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --project {acct} '
      cmd += f' --walltime {walltime} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   # Configure
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      file=open('user_nl_eam','w');file.write(get_atm_nl_opts(e,c,h));file.close()
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {nlev} \" ')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val=\'-cosp\'')
      #-------------------------------------------------------
      # PE layout mods from Noel
      cpl_stride = 8; cpl_ntasks = atm_ntasks / cpl_stride
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL="{cpl_ntasks}"')
      run_cmd(f'./xmlchange --file env_mach_pes.xml PSTRID_CPL="{cpl_stride}"')
      run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_CPL="0"')
      #-------------------------------------------------------
      # run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   # Build
   if build : 
      run_cmd(f'./xmlchange RUN_TYPE=hybrid,GET_REFCASE=TRUE ')
      run_cmd(f'./xmlchange RUN_REFCASE={RUN_REFCASE},RUN_REFDATE={RUN_REFDATE} ')
      run_cmd(f'./xmlchange RUN_REFDIR={REF_SCRATCH}/{RUN_REFCASE}/archive/rest/{RUN_REFDATE}-00000 ')
      #-------------------------------------------------------
      if 'debug-on' in case : run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   # Write the namelist options and submit the run
   if submit : 
      # run_cmd(f'./xmlchange DIN_LOC_ROOT=/global/cfs/cdirs/e3sm/inputdata')
      #-------------------------------------------------------
      file=open('user_nl_eam','w');file.write(get_atm_nl_opts(e,c,h));file.close()
      file=open('user_nl_elm','w');file.write(get_lnd_nl_opts()     );file.close()
      #-------------------------------------------------------
      run_cmd(f'./xmlchange RUN_STARTDATE={RUN_REFDATE}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      # if 'resub' in globals() and not continue_run: run_cmd(f'./xmlchange RESUBMIT={resub}')
      # if 'resub' in globals() and reset_resub: run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'resub' in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      #-------------------------------------------------------
      if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
      if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
      #-------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
# BTAU_list = ''
BTAU_list = '''
 fincl2 = 'BTAUXSn32_100mb','BTAUXSn31_100mb','BTAUXSn30_100mb','BTAUXSn29_100mb',
          'BTAUXSn28_100mb','BTAUXSn27_100mb','BTAUXSn26_100mb','BTAUXSn25_100mb',
          'BTAUXSn24_100mb','BTAUXSn23_100mb','BTAUXSn22_100mb','BTAUXSn21_100mb',
          'BTAUXSn20_100mb','BTAUXSn19_100mb','BTAUXSn18_100mb','BTAUXSn17_100mb',
          'BTAUXSn16_100mb','BTAUXSn15_100mb','BTAUXSn14_100mb','BTAUXSn13_100mb',
          'BTAUXSn12_100mb','BTAUXSn11_100mb','BTAUXSn10_100mb','BTAUXSn09_100mb',
          'BTAUXSn08_100mb','BTAUXSn07_100mb','BTAUXSn06_100mb','BTAUXSn05_100mb',
          'BTAUXSn04_100mb','BTAUXSn03_100mb','BTAUXSn02_100mb','BTAUXSn01_100mb','BTAUXSp00_100mb',
          'BTAUXSp01_100mb','BTAUXSp02_100mb','BTAUXSp03_100mb','BTAUXSp04_100mb',
          'BTAUXSp05_100mb','BTAUXSp06_100mb','BTAUXSp07_100mb','BTAUXSp08_100mb',
          'BTAUXSp09_100mb','BTAUXSp10_100mb','BTAUXSp11_100mb','BTAUXSp12_100mb',
          'BTAUXSp13_100mb','BTAUXSp14_100mb','BTAUXSp15_100mb','BTAUXSp16_100mb',
          'BTAUXSp17_100mb','BTAUXSp18_100mb','BTAUXSp19_100mb','BTAUXSp20_100mb',
          'BTAUXSp21_100mb','BTAUXSp22_100mb','BTAUXSp23_100mb','BTAUXSp24_100mb',
          'BTAUXSp25_100mb','BTAUXSp26_100mb','BTAUXSp27_100mb','BTAUXSp28_100mb',
          'BTAUXSp29_100mb','BTAUXSp30_100mb','BTAUXSp31_100mb','BTAUXSp32_100mb',
          'BTAUXSn32_50mb','BTAUXSn31_50mb','BTAUXSn30_50mb','BTAUXSn29_50mb',
          'BTAUXSn28_50mb','BTAUXSn27_50mb','BTAUXSn26_50mb','BTAUXSn25_50mb',
          'BTAUXSn24_50mb','BTAUXSn23_50mb','BTAUXSn22_50mb','BTAUXSn21_50mb',
          'BTAUXSn20_50mb','BTAUXSn19_50mb','BTAUXSn18_50mb','BTAUXSn17_50mb',
          'BTAUXSn16_50mb','BTAUXSn15_50mb','BTAUXSn14_50mb','BTAUXSn13_50mb',
          'BTAUXSn12_50mb','BTAUXSn11_50mb','BTAUXSn10_50mb','BTAUXSn09_50mb',
          'BTAUXSn08_50mb','BTAUXSn07_50mb','BTAUXSn06_50mb','BTAUXSn05_50mb',
          'BTAUXSn04_50mb','BTAUXSn03_50mb','BTAUXSn02_50mb','BTAUXSn01_50mb','BTAUXSp00_50mb',
          'BTAUXSp01_50mb','BTAUXSp02_50mb','BTAUXSp03_50mb','BTAUXSp04_50mb',
          'BTAUXSp05_50mb','BTAUXSp06_50mb','BTAUXSp07_50mb','BTAUXSp08_50mb',
          'BTAUXSp09_50mb','BTAUXSp10_50mb','BTAUXSp11_50mb','BTAUXSp12_50mb',
          'BTAUXSp13_50mb','BTAUXSp14_50mb','BTAUXSp15_50mb','BTAUXSp16_50mb',
          'BTAUXSp17_50mb','BTAUXSp18_50mb','BTAUXSp19_50mb','BTAUXSp20_50mb',
          'BTAUXSp21_50mb','BTAUXSp22_50mb','BTAUXSp23_50mb','BTAUXSp24_50mb',
          'BTAUXSp25_50mb','BTAUXSp26_50mb','BTAUXSp27_50mb','BTAUXSp28_50mb',
          'BTAUXSp29_50mb','BTAUXSp30_50mb','BTAUXSp31_50mb','BTAUXSp32_50mb',
          'BTAUXSn32_30mb','BTAUXSn31_30mb','BTAUXSn30_30mb','BTAUXSn29_30mb',
          'BTAUXSn28_30mb','BTAUXSn27_30mb','BTAUXSn26_30mb','BTAUXSn25_30mb',
          'BTAUXSn24_30mb','BTAUXSn23_30mb','BTAUXSn22_30mb','BTAUXSn21_30mb',
          'BTAUXSn20_30mb','BTAUXSn19_30mb','BTAUXSn18_30mb','BTAUXSn17_30mb',
          'BTAUXSn16_30mb','BTAUXSn15_30mb','BTAUXSn14_30mb','BTAUXSn13_30mb',
          'BTAUXSn12_30mb','BTAUXSn11_30mb','BTAUXSn10_30mb','BTAUXSn09_30mb',
          'BTAUXSn08_30mb','BTAUXSn07_30mb','BTAUXSn06_30mb','BTAUXSn05_30mb',
          'BTAUXSn04_30mb','BTAUXSn03_30mb','BTAUXSn02_30mb','BTAUXSn01_30mb','BTAUXSp00_30mb',
          'BTAUXSp01_30mb','BTAUXSp02_30mb','BTAUXSp03_30mb','BTAUXSp04_30mb',
          'BTAUXSp05_30mb','BTAUXSp06_30mb','BTAUXSp07_30mb','BTAUXSp08_30mb',
          'BTAUXSp09_30mb','BTAUXSp10_30mb','BTAUXSp11_30mb','BTAUXSp12_30mb',
          'BTAUXSp13_30mb','BTAUXSp14_30mb','BTAUXSp15_30mb','BTAUXSp16_30mb',
          'BTAUXSp17_30mb','BTAUXSp18_30mb','BTAUXSp19_30mb','BTAUXSp20_30mb',
          'BTAUXSp21_30mb','BTAUXSp22_30mb','BTAUXSp23_30mb','BTAUXSp24_30mb',
          'BTAUXSp25_30mb','BTAUXSp26_30mb','BTAUXSp27_30mb','BTAUXSp28_30mb',
          'BTAUXSp29_30mb','BTAUXSp30_30mb','BTAUXSp31_30mb','BTAUXSp32_30mb',
          'BTAUXSn32_10mb','BTAUXSn31_10mb','BTAUXSn30_10mb','BTAUXSn29_10mb',
          'BTAUXSn28_10mb','BTAUXSn27_10mb','BTAUXSn26_10mb','BTAUXSn25_10mb',
          'BTAUXSn24_10mb','BTAUXSn23_10mb','BTAUXSn22_10mb','BTAUXSn21_10mb',
          'BTAUXSn20_10mb','BTAUXSn19_10mb','BTAUXSn18_10mb','BTAUXSn17_10mb',
          'BTAUXSn16_10mb','BTAUXSn15_10mb','BTAUXSn14_10mb','BTAUXSn13_10mb',
          'BTAUXSn12_10mb','BTAUXSn11_10mb','BTAUXSn10_10mb','BTAUXSn09_10mb',
          'BTAUXSn08_10mb','BTAUXSn07_10mb','BTAUXSn06_10mb','BTAUXSn05_10mb',
          'BTAUXSn04_10mb','BTAUXSn03_10mb','BTAUXSn02_10mb','BTAUXSn01_10mb','BTAUXSp00_10mb',
          'BTAUXSp01_10mb','BTAUXSp02_10mb','BTAUXSp03_10mb','BTAUXSp04_10mb',
          'BTAUXSp05_10mb','BTAUXSp06_10mb','BTAUXSp07_10mb','BTAUXSp08_10mb',
          'BTAUXSp09_10mb','BTAUXSp10_10mb','BTAUXSp11_10mb','BTAUXSp12_10mb',
          'BTAUXSp13_10mb','BTAUXSp14_10mb','BTAUXSp15_10mb','BTAUXSp16_10mb',
          'BTAUXSp17_10mb','BTAUXSp18_10mb','BTAUXSp19_10mb','BTAUXSp20_10mb',
          'BTAUXSp21_10mb','BTAUXSp22_10mb','BTAUXSp23_10mb','BTAUXSp24_10mb',
          'BTAUXSp25_10mb','BTAUXSp26_10mb','BTAUXSp27_10mb','BTAUXSp28_10mb',
          'BTAUXSp29_10mb','BTAUXSp30_10mb','BTAUXSp31_10mb','BTAUXSp32_10mb' 
'''
#---------------------------------------------------------------------------------------------------
def get_atm_nl_opts(gweff,cfrac,hdpth):
   return f'''
 ncdata = '{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.nc'
 
 cosp_lite = .true.

 inithist = 'NONE'

 effgw_beres           = {gweff}
 gw_convect_hcf        = {cfrac}
 hdepth_scaling_factor = {hdpth}

 empty_htapes = .true.
 avgflag_pertape = 'A','A'
 nhtfrq = 0,-24
 mfilt  = 1,30
 fincl1 = 'AODALL', 'AODDUST', 'AODVIS',
          'CLDHGH_CAL', 'CLDLOW_CAL', 'CLDMED_CAL',
          'CLD_MISR', 'CLDTOT_CAL', 'CLMODIS', 'FISCCP1_COSP', 
          'FLDS', 'FLNS', 'FLNSC', 'FLNT', 'FLUT',
          'FLUTC', 'FSDS', 'FSDSC', 'FSNS', 'FSNSC', 'FSNT', 'FSNTOA', 'FSNTOAC', 
          'ICEFRAC', 'LANDFRAC', 'OCNFRAC',
          'OMEGA', 'U', 'V', 'Z3', 'T', 'Q', 'RELHUM', 'O3', 'PSL', 'PS'
          'PRECC', 'PRECL', 'PRECSC', 'PRECSL',
          'QFLX', 'SCO', 'SHFLX', 'SOLIN', 'SWCF', 'LWCF',
          'TAUX', 'TAUY', 'TCO', 'TGCLDLWP', 'TGCLDIWP', 'TMQ', 
          'TS', 'TREFHT', 'TREFMNAV', 'TREFMXAV'
 {BTAU_list} 

'''

# vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,CLDTOT_CAL,CLDHGH_CAL,CLDMED_CAL,CLDLOW_CAL,U,ICEFRAC,LANDFRAC,OCNFRAC,AODALL,AODDUST,AODVIS,PS"

# vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,
# PRECL,PRECSC,PRECSL,TS,TREFHT,CLDTOT,CLDHGH,CLDMED,CLDLOW,U,ICEFRAC,
# LANDFRAC,OCNFRAC,Mass_bc,Mass_dst,Mass_mom,Mass_ncl,Mass_pom,Mass_so4,Mass_soa,
# AODALL,AODBC,AODDUST,AODPOM,AODSO4,AODSOA,AODSS,AODVIS,PS"
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_lnd_nl_opts():
   return f'''
hist_dov2xy = .true.,.true.
hist_fincl1 = 'SNOWDP'
hist_mfilt = 1
hist_nhtfrq = 0
hist_avgflag_pertape = 'A'
check_finidat_year_consistency = .false.
check_dynpft_consistency = .false.
flanduse_timeseries = '{din_loc_root}/lnd/clm2/surfdata_map/landuse.timeseries_ne30np4.pg2_hist_simyr1850-2015_c210113.nc'
fsurdat = \'{land_data_path}/{land_data_file}\'
'''
# finidat = \'{land_init_path}/{land_init_file}\'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
# def get_din_loc_root():
#    (din_loc_root, err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
#                                  stdout=sp.PIPE, shell=True, \
#                                  universal_newlines=True).communicate()
#    return din_loc_root
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(hdpth_list)):
      # print('-'*80)
      main( e=gweff_list[n], c=cfrac_list[n], h=hdpth_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

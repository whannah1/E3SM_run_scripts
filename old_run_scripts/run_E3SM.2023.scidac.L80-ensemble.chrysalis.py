#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--radnx',dest='radnx',default=None,help='sets number of rad columns')
(opts, args) = parser.parse_args()
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'e3sm'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/scidac-2023 =>master @ Aug 7 w/ v3atm/eam/master_MAM5_wetaero_chemdyg

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# queue = 'batch' # batch / debug
num_nodes   = 43 # 22
grid        = 'ne30pg2_EC30to60E2r2'
compset     = 'F20TR' # F20TR / F20TR_chemUCI-Linozv3-mam5
nlev        = 80

stop_opt,stop_n,resub,walltime = 'ndays',365*4,0,'8:00:00'

# gweff_list = [0]
# cfrac_list = [0]
# hdpth_list = [0]

# gweff_list.append(0.10); cfrac_list.append(0.30); hdpth_list.append(0.63) #  1 L72-run # 44  
# gweff_list.append(0.10); cfrac_list.append(0.10); hdpth_list.append(1.50) #  2 L72-run # 16  
# gweff_list.append(0.35); cfrac_list.append(0.20); hdpth_list.append(1.00) #  3 L72-run #  3  
# gweff_list.append(0.20); cfrac_list.append(0.20); hdpth_list.append(1.50) #  4 L72-run # 17  
# gweff_list.append(0.10); cfrac_list.append(0.25); hdpth_list.append(0.25) #  5 L72-run # 25  
# gweff_list.append(0.20); cfrac_list.append(0.25); hdpth_list.append(0.50) #  6 L72-run # 22  
# gweff_list.append(0.35); cfrac_list.append(0.10); hdpth_list.append(0.50) #  7 L72-run #  5  
# gweff_list.append(0.35); cfrac_list.append(0.10); hdpth_list.append(0.25) #  8 L72-run #  2  
# gweff_list.append(0.20); cfrac_list.append(0.10); hdpth_list.append(1.00) #  9 L72-run #  4  
# gweff_list.append(0.20); cfrac_list.append(0.15); hdpth_list.append(0.50) # 10 L72-run #  7  

# gweff_list.append(0.09); cfrac_list.append(0.20); hdpth_list.append(0.25) # 11 L72-run # 10  

# gweff_list.append(0.20); cfrac_list.append(0.20); hdpth_list.append(1.25) # 12 L72-run # 18  
# gweff_list.append(0.05); cfrac_list.append(0.25); hdpth_list.append(0.50) # 13 L72-run # 12  
# gweff_list.append(0.80); cfrac_list.append(0.01); hdpth_list.append(1.15) # 14 L72-run # 31  
# gweff_list.append(0.90); cfrac_list.append(0.20); hdpth_list.append(0.25) # 15 L72-run # 14  
# gweff_list.append(0.59); cfrac_list.append(0.41); hdpth_list.append(0.55) # 16 L72-run # 40  
# gweff_list.append(0.01); cfrac_list.append(0.01); hdpth_list.append(0.70) # 17 L72-run # 28  
# gweff_list.append(0.40); cfrac_list.append(0.10); hdpth_list.append(1.00) # 18 L72-run #  1  
# gweff_list.append(0.70); cfrac_list.append(0.25); hdpth_list.append(0.90) # 19 L72-run # 30  
# gweff_list.append(0.60); cfrac_list.append(0.07); hdpth_list.append(1.35) # 20 L72-run # 38  


# din_loc_root = '/global/cfs/cdirs/e3sm/inputdata'
# init_scratch = '/global/cfs/cdirs/m4310/whannah/HICCUP/data/'

din_loc_root = '/lcrc/group/e3sm/data/inputdata'
init_scratch = '/lcrc/group/e3sm/ac.whannah/HICCUP/data'

# land_init_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/'
# land_data_path = f'{din_loc_root}/lnd/clm2/surfdata_map'
# if grid=='ne30pg2_EC30to60E2r2': 
#    # land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
#    if 'F2010' in compset: land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'
#    if 'F20TR' in compset: land_data_file = 'surfdata_ne30pg2_simyr1850_c210402.nc'

# REF_SCRATCH = '/global/cfs/cdirs/m4310/whannah/E3SM/'
REF_SCRATCH = '/lcrc/group/e3sm/ac.mwu/archive/'
RUN_REFCASE = '20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis'
RUN_REFDATE = '1984-01-01'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(e=None,c=None,h=None):
   if h is None or c is None or e is None: exit(' one or more arguments not provided?')

   # case = '.'.join(['E3SM','2023-SCIDAC',grid,'AMIP',f'EF_{e:0.2f}',f'CF_{c:0.2f}',f'HD_{h:0.2f}'])
   # case = '.'.join(['E3SM','2023-SCIDAC',grid,'AMIP'])
   case = '.'.join(['E3SM','2023-SCIDAC',grid,'AMIP','fix01'])

   # case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   case_root = f'/lcrc/group/e3sm/ac.whannah/E3SMv3_dev/{case}'

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
      # cmd += f' --machine pm-cpu '
      cmd += f' --machine chrysalis '
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
      # file=open('user_nl_elm','w');file.write(get_lnd_nl_opts()     );file.close()
      #-------------------------------------------------------
      run_cmd(f'./xmlchange RUN_STARTDATE={RUN_REFDATE}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      # disable_bfb = False
      # if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
      # if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
# effgw_beres           = {gweff}
# gw_convect_hcf        = {cfrac}
# hdepth_scaling_factor = {hdpth}
def get_atm_nl_opts(gweff,cfrac,hdpth):
   return f'''
 ncdata = '{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.nc'
 cosp_lite = .true.
 inithist = 'NONE'
 empty_htapes = .true.
 avgflag_pertape = 'A','A'
 nhtfrq = 0,0
 mfilt  = 1,1
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

'''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
# def get_lnd_nl_opts():
#    return f'''
# hist_dov2xy = .true.,.true.
# hist_fincl1 = 'SNOWDP'
# hist_mfilt = 1
# hist_nhtfrq = 0
# hist_avgflag_pertape = 'A'
# check_finidat_year_consistency = .false.
# check_dynpft_consistency = .false.
# flanduse_timeseries = '{din_loc_root}/lnd/clm2/surfdata_map/landuse.timeseries_ne30np4.pg2_hist_simyr1850-2015_c210113.nc'
# fsurdat = \'{land_data_path}/{land_data_file}\'
# '''
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
      print('-'*80)
      main( e=gweff_list[n], c=cfrac_list[n], h=hdpth_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

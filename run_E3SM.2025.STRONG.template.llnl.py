#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
''' Notes
# use the python code below to generate a repeatable random list of N-digit seeds
import random
# seed_value, list_length, beg_range, end_range = 42**4, 100, 111111, 999999 # 6-digits
seed_value, list_length, beg_range, end_range = 42**4, 20, 1111111111, 9999999999 # 10-digits
random.seed(seed_value)
numbers = [random.randint(beg_range, end_range) for _ in range(list_length)]
msg = ','.join([f'{n}' for n in numbers])
print(f'[{msg}]')
'''
#---------------------------------------------------------------------------------------------------
project = 'strong'

# code_root = '/usr/workspace/pochedls/E3SM/E3SM_code/' # branch => maint-3.0
# case_root = '/p/vast1/strong/E3SMv3/boost'

code_root = '/g/g19/hannah6/E3SM/E3SM_SRC0' # branch => maint-3.0
case_root = '/p/vast1/strong/hannah6'

newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# just_print_names = True

queue = 'pbatch' # pbatch / pdebug

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',10,0,'2:00:00'

#---------------------------------------------------------------------------------------------------
# build list of cases to run here

# 100-member ensemble - 10x 10-member groups - see note above about seed generation
seed_list = []
seed_list.append([657436,991774,752652,865571,371983,760555,792284,320604,449950,849177])
# seed_list.append([258978,773386,651874,640932,684441,687381,643581,130599,749925,543874])
# seed_list.append([571019,963478,478521,492507,359151,639398,795102,298493,599426,991255])
# seed_list.append([619322,139636,752668,516289,427102,690067,468749,333239,923269,992421])
# seed_list.append([306396,821757,674627,307092,319063,710388,407972,757449,892463,933301])
# seed_list.append([613169,969665,872240,417521,606625,688025,867822,828159,450835,422685])
# seed_list.append([395040,610684,236176,397581,896944,432866,750592,170713,579395,236632])
# seed_list.append([986843,885856,810017,662027,604866,919413,729468,799647,828634,983775])
# seed_list.append([657687,879132,747550,725593,463899,305734,328788,818711,197505,471236])
# seed_list.append([398486,921584,524617,616309,194260,215141,244813,821378,763770,797368])

# loop through seeds to create cases
for sd in seed_list:
   add_case(prefix='v3.2026-STRONG-ENS-00',start='2018-07-04',seed=sd)


#---------------------------------------------------------------------------------------------------
# common settings across all runs
compset     = 'WCYCLSSP245'
grid        = 'ne30pg2_r05_IcoswISC30E3r5'
num_nodes   = 12
#---------------------------------------------------------------------------------------------------
if 'just_print_names' not in globals(): just_print_names = False
if 'newcase'          not in globals(): newcase      = False
if 'config'           not in globals(): config       = False
if 'build'            not in globals(): build        = False
if 'submit'           not in globals(): submit       = False
if 'continue_run'     not in globals(): continue_run = False
#---------------------------------------------------------------------------------------------------
def main(opts):
   global compset, grid, num_nodes
   #----------------------------------------------------------------------------
   if 'seed'   not in opts: raise ValueError('ERROR - RNG seed not provided!')
   if 'start'  not in opts: raise ValueError('ERROR - start date not provided!')
   #----------------------------------------------------------------------------
   ref_case = 'v3.LR.historical_0121'
   ref_root = '/p/vast1/strong/E3SMv3/restarts'
   ref_date = opts["start"]
   ref_dir = f'{ref_root}/{ref_case}_with_eami/archive/rest/{ref_date}-00000'
   #----------------------------------------------------------------------------
   case_list = []
   for key,val in opts.items(): 
      if key in ['prefix']:
         case_list.append(val)
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val}')
   #----------------------------------------------------------------------------
   case = '.'.join(case_list)
   #----------------------------------------------------------------------------
   if just_print_names: print(case); return
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   max_mpi_per_node,atm_nthrds  = 112,1
   atm_ntasks = max_mpi_per_node*num_nodes
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(f'{case_root}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{code_root}/cime/scripts/create_newcase'
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root}/{case} '
      cmd += f' --script-root {case_root}/{case}/case_scripts '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {project} '
      cmd += f' --mach dane --pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/{case}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/{case}/bld')
      run_cmd(f'./xmlchange RUNDIR={case_root}/{case}/run')
      run_cmd(f'./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node}')
      run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={(max_mpi_per_node*atm_nthrds)}')
      #-------------------------------------------------------------------------
      # setup things for branch/hybrid run
      run_cmd(f'./xmlchange RUN_TYPE=hybrid')
      run_cmd(f'./xmlchange RUN_STARTDATE={opts["start"]}')
      run_cmd(f'./xmlchange GET_REFCASE=True')
      run_cmd(f'./xmlchange RUN_REFDIR="{ref_dir}"')
      run_cmd(f'./xmlchange RUN_REFCASE="{ref_case}"')
      run_cmd(f'./xmlchange RUN_REFDATE="{ref_date}"')
      #-------------------------------------------------------------------------
      # # commands to pre-stage data files if GET_REFCASE=FALSE
      # scratch = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
      # run_cmd(f'cp {scratch}/{ref_case}/run/*{ref_date}* {case_root}/{case}/run/')
      # run_cmd(f'cp {scratch}/{ref_case}/run/rpointer* {case_root}/{case}/run/')
      #-------------------------------------------------------------------------
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build :
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      write_atm_nl_opts(opts)
      write_lnd_nl_opts(opts)
      #-------------------------------------------------------------------------
      run_cmd(f'cp /p/vast1/strong/E3SMv3/case_scripts/user_nl_eam {case_root}/{case}/user_nl_eam')
      run_cmd(f'cp /p/vast1/strong/E3SMv3/case_scripts/user_nl_elm {case_root}/{case}/user_nl_elm')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange REST_OPTION="ndays",REST_N=1') # write restarts everyday in case we need them
      #-------------------------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
# 2D variable list
hist_var_2D  = "'PS','PSL','PRECT'"
hist_var_2D += ",'TS','TREFHT','QREFHT'"
hist_var_2D += ",'LHFLX','SHFLX'"                        # surface fluxes
hist_var_2D += ",'FSNT','FLNT','FSNTC','FLNTC'"          # Net TOM heating rates + clear sky
hist_var_2D += ",'FLNS','FSNS','FLDS','FSDS'"            # Surface rad
hist_var_2D += ",'LWCF','SWCF'"                          # cloud radiative foricng
hist_var_2D += ",'TGCLDLWP','TGCLDIWP'"                  # cloud water paths
hist_var_2D += ",'CLDLOW','CLDMED','CLDHGH','CLDTOT'"    # cloud fractions
# hist_var_2D += ",'TUQ','TVQ'"                            # vapor transport for AR identification
hist_var_2D += ",'U90M','V90M'"                          # wind at turbine hub height
hist_var_2D += ",'TBOT','QBOT','UBOT','VBOT'"            # lowest model level
hist_var_2D += ",'T900','Q900','U900','V900'"            # 900mb
hist_var_2D += ",'T850','Q850','U850','V850','OMEGA850'" # 850mb
hist_var_2D += ",'Z500','OMEGA500'"                      # 500mb
hist_var_2D += ",'Z300'"                                 # 300mb
hist_var_2D += ",'AODALL', 'AODDUST', 'AODVIS'"          # aerosol optical depths

# # 3D variable list - include PS for vertical remapping
# hist_var_3D = "'PS','T','Z3','Q','RELHUM','U','V','OMEGA','O3'"

#---------------------------------------------------------------------------------------------------
def get_atm_nl_opts(opts):
   global hist_var_2D
   return f'''
 cosp_lite = .false.
 inithist = 'NONE'
 empty_htapes = .true.
 avgflag_pertape = 'A','A'
 nhtfrq = 0,-1
 mfilt  = 1,24

 fincl2 = {hist_var_2D}

 history_chemdyg_summary           = .false.
 history_gaschmbudget_2D           = .false.
 history_gaschmbudget_2D_levels    = .false.
 history_UCIgaschmbudget_2D        = .false.
 history_UCIgaschmbudget_2D_levels = .false.
 history_aero_optics               = .false.
 history_aerosol                   = .false.
 history_amwg                      = .false.
 history_budget                    = .false.
 history_verbose                   = .false.

 pertlim = 1e-6
 seed_custom = {opts["seed"]}
 new_random = .true.

'''
#---------------------------------------------------------------------------------------------------
def write_atm_nl_opts(opts):
   file=open('user_nl_eam','w')
   file.write(get_atm_nl_opts(opts))
   file.close()
   return
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_lnd_nl_opts(opts):
   return '''
 flanduse_timeseries = "${DIN_LOC_ROOT}/lnd/clm2/surfdata_map/landuse.timeseries_0.5x0.5_hist_simyr1850-2015_c240308.nc"

 hist_dov2xy = .true.,.true.
 hist_fexcl1 = 'AGWDNPP','ALTMAX_LASTYEAR','AVAIL_RETRANSP','AVAILC','BAF_CROP',
               'BAF_PEATF','BIOCHEM_PMIN_TO_PLANT','CH4_SURF_AERE_SAT','CH4_SURF_AERE_UNSAT','CH4_SURF_DIFF_SAT',
               'CH4_SURF_DIFF_UNSAT','CH4_SURF_EBUL_SAT','CH4_SURF_EBUL_UNSAT','CMASS_BALANCE_ERROR','cn_scalar',
               'COL_PTRUNC','CONC_CH4_SAT','CONC_CH4_UNSAT','CONC_O2_SAT','CONC_O2_UNSAT',
               'cp_scalar','CWDC_HR','CWDC_LOSS','CWDC_TO_LITR2C','CWDC_TO_LITR3C',
               'CWDC_vr','CWDN_TO_LITR2N','CWDN_TO_LITR3N','CWDN_vr','CWDP_TO_LITR2P',
               'CWDP_TO_LITR3P','CWDP_vr','DWT_CONV_CFLUX_DRIBBLED','F_CO2_SOIL','F_CO2_SOIL_vr',
               'F_DENIT_vr','F_N2O_DENIT','F_N2O_NIT','F_NIT_vr','FCH4_DFSAT',
               'FINUNDATED_LAG','FPI_P_vr','FPI_vr','FROOTC_LOSS','HR_vr',
               'LABILEP_TO_SECONDP','LABILEP_vr','LAND_UPTAKE','LEAF_MR','leaf_npimbalance',
               'LEAFC_LOSS','LEAFC_TO_LITTER','LFC2','LITR1_HR','LITR1C_TO_SOIL1C',
               'LITR1C_vr','LITR1N_TNDNCY_VERT_TRANS','LITR1N_TO_SOIL1N','LITR1N_vr','LITR1P_TNDNCY_VERT_TRANS',
               'LITR1P_TO_SOIL1P','LITR1P_vr','LITR2_HR','LITR2C_TO_SOIL2C','LITR2C_vr',
               'LITR2N_TNDNCY_VERT_TRANS','LITR2N_TO_SOIL2N','LITR2N_vr','LITR2P_TNDNCY_VERT_TRANS','LITR2P_TO_SOIL2P',
               'LITR2P_vr','LITR3_HR','LITR3C_TO_SOIL3C','LITR3C_vr','LITR3N_TNDNCY_VERT_TRANS',
               'LITR3N_TO_SOIL3N','LITR3N_vr','LITR3P_TNDNCY_VERT_TRANS','LITR3P_TO_SOIL3P','LITR3P_vr',
               'M_LITR1C_TO_LEACHING','M_LITR2C_TO_LEACHING','M_LITR3C_TO_LEACHING','M_SOIL1C_TO_LEACHING','M_SOIL2C_TO_LEACHING',
               'M_SOIL3C_TO_LEACHING','M_SOIL4C_TO_LEACHING','NDEPLOY','NEM','nlim_m',
               'o2_decomp_depth_unsat','OCCLP_vr','PDEPLOY','PLANT_CALLOC','PLANT_NDEMAND',
               'PLANT_NDEMAND_COL','PLANT_PALLOC','PLANT_PDEMAND','PLANT_PDEMAND_COL','plim_m',
               'POT_F_DENIT','POT_F_NIT','POTENTIAL_IMMOB','POTENTIAL_IMMOB_P','PRIMP_TO_LABILEP',
               'PRIMP_vr','PROD1P_LOSS','QOVER_LAG','RETRANSN_TO_NPOOL','RETRANSP_TO_PPOOL',
               'SCALARAVG_vr','SECONDP_TO_LABILEP','SECONDP_TO_OCCLP','SECONDP_vr','SMIN_NH4_vr',
               'SMIN_NO3_vr','SMINN_TO_SOIL1N_L1','SMINN_TO_SOIL2N_L2','SMINN_TO_SOIL2N_S1','SMINN_TO_SOIL3N_L3',
               'SMINN_TO_SOIL3N_S2','SMINN_TO_SOIL4N_S3','SMINP_TO_SOIL1P_L1','SMINP_TO_SOIL2P_L2','SMINP_TO_SOIL2P_S1',
               'SMINP_TO_SOIL3P_L3','SMINP_TO_SOIL3P_S2','SMINP_TO_SOIL4P_S3','SMINP_vr','SOIL1_HR','SOIL1C_TO_SOIL2C','SOIL1C_vr','SOIL1N_TNDNCY_VERT_TRANS','SOIL1N_TO_SOIL2N','SOIL1N_vr',
               'SOIL1P_TNDNCY_VERT_TRANS','SOIL1P_TO_SOIL2P','SOIL1P_vr','SOIL2_HR','SOIL2C_TO_SOIL3C',
               'SOIL2C_vr','SOIL2N_TNDNCY_VERT_TRANS','SOIL2N_TO_SOIL3N','SOIL2N_vr','SOIL2P_TNDNCY_VERT_TRANS',
               'SOIL2P_TO_SOIL3P','SOIL2P_vr','SOIL3_HR','SOIL3C_TO_SOIL4C','SOIL3C_vr',
               'SOIL3N_TNDNCY_VERT_TRANS','SOIL3N_TO_SOIL4N','SOIL3N_vr','SOIL3P_TNDNCY_VERT_TRANS','SOIL3P_TO_SOIL4P',
               'SOIL3P_vr','SOIL4_HR','SOIL4C_vr','SOIL4N_TNDNCY_VERT_TRANS','SOIL4N_TO_SMINN',
               'SOIL4N_vr','SOIL4P_TNDNCY_VERT_TRANS','SOIL4P_TO_SMINP','SOIL4P_vr','SOLUTIONP_vr',
               'TCS_MONTH_BEGIN','TCS_MONTH_END','TOTCOLCH4','water_scalar','WF',
               'wlim_m','WOODC_LOSS','WTGQ'
 hist_fincl1 = 'SNOWDP','COL_FIRE_CLOSS','NPOOL','PPOOL','TOTPRODC'
 hist_fincl2 = 'H2OSNO', 'FSNO', 'QRUNOFF', 'QSNOMELT', 'FSNO_EFF', 'SNORDSL', 'SNOW', 'FSDS', 'FSR', 'FLDS', 'FIRE', 'FIRA'
 hist_nhtfrq = 0,-1
 hist_mfilt = 1,24
 hist_avgflag_pertape = 'A','A'
'''
#---------------------------------------------------------------------------------------------------
def write_lnd_nl_opts(opts):
   file=open('user_nl_elm','w')
   file.write(get_lnd_nl_opts(opts))
   file.close()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

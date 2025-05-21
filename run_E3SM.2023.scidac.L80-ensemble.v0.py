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

acct = 'm4310'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4' # branch => master @ Aug 7 w/ v3atm/eam/master_MAM5_wetaero_chemdyg

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# queue = 'batch' # batch / debug
num_nodes   = 22
grid        = 'ne30pg2_EC30to60E2r2'
compset     = 'F20TR' # F20TR / F20TR_chemUCI-Linozv3-mam5
nlev        = 80

# stop_opt,stop_n,resub,walltime = 'nsteps',10,0,'0:30:00' 
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',365*4,0,'8:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365*2,5-1,'4:00:00' # 10 years

gweff_list = []
cfrac_list = []
hdpth_list = []

gweff_list.append(0.35); cfrac_list.append(10); hdpth_list.append(1.00) #  9 L72-run # default

# gweff_list.append(0.10); cfrac_list.append(30); hdpth_list.append(0.63) #  1 L72-run # 44  
# gweff_list.append(0.10); cfrac_list.append(10); hdpth_list.append(1.50) #  2 L72-run # 16  
# gweff_list.append(0.35); cfrac_list.append(20); hdpth_list.append(1.00) #  3 L72-run #  3  
# gweff_list.append(0.20); cfrac_list.append(20); hdpth_list.append(1.50) #  4 L72-run # 17  
# gweff_list.append(0.10); cfrac_list.append(25); hdpth_list.append(0.25) #  5 L72-run # 25  
# gweff_list.append(0.20); cfrac_list.append(25); hdpth_list.append(0.50) #  6 L72-run # 22  
# gweff_list.append(0.35); cfrac_list.append(10); hdpth_list.append(0.50) #  7 L72-run #  5  
# gweff_list.append(0.35); cfrac_list.append(10); hdpth_list.append(0.25) #  8 L72-run #  2  
# gweff_list.append(0.20); cfrac_list.append(10); hdpth_list.append(1.00) #  9 L72-run #  4  
# gweff_list.append(0.20); cfrac_list.append(15); hdpth_list.append(0.50) # 10 L72-run #  7  
# gweff_list.append(0.09); cfrac_list.append(20); hdpth_list.append(0.25) # 11 L72-run # 10  
# gweff_list.append(0.20); cfrac_list.append(20); hdpth_list.append(1.25) # 12 L72-run # 18  
# gweff_list.append(0.05); cfrac_list.append(25); hdpth_list.append(0.50) # 13 L72-run # 12  
# gweff_list.append(0.80); cfrac_list.append(01); hdpth_list.append(1.15) # 14 L72-run # 31  
# gweff_list.append(0.90); cfrac_list.append(20); hdpth_list.append(0.25) # 15 L72-run # 14  
# gweff_list.append(0.59); cfrac_list.append(41); hdpth_list.append(0.55) # 16 L72-run # 40  
# gweff_list.append(0.01); cfrac_list.append(01); hdpth_list.append(0.70) # 17 L72-run # 28  
# gweff_list.append(0.40); cfrac_list.append(10); hdpth_list.append(1.00) # 18 L72-run #  1  
# gweff_list.append(0.70); cfrac_list.append(25); hdpth_list.append(0.90) # 19 L72-run # 30  
# gweff_list.append(0.60); cfrac_list.append(07); hdpth_list.append(1.35) # 20 L72-run # 38  

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

   case = '.'.join(['E3SM','2023-SCIDAC',grid,'AMIP',f'EF_{e:0.2f}',f'CF_{c:0.2f}',f'HD_{h:0.2f}'])

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
 {BTAU_list} 
 !--------------------------------------
 !--- process coupling namelist --------
 cflx_cpl_opt = 2
 !--------------------------------------
 !--- Namelist flags for ZM and P3 -----
 zmconv_microp = .true.
 zmconv_clos_dyn_adj = .true.
 zmconv_MCSP_heat_coeff = 0.3
 zmconv_tpert_fix = .true.
 zmconv_ke = 2.5e-6
 zmconv_c0_lnd = 0.0020D0   !Update: when ZMmicrophysics is used, this should have no effect
 
 sscav_tuning = .false.
 p3_wbf_coeff = 1.0
 p3_mincdnc=20.D6     ! set minimum drop # conc to 20 cc-1
 p3_nc_autocon_expon = -1.20D0
 nucleate_ice_subgrid   =  1.35
 !--------------------------------------  
 ! dust and sea salt emission tunings
 dust_emis_fact         =  12.8D0
 seasalt_emis_scale     =  0.55D0
 !--------------------------------------
 !--- Ozone hole -----------------------
 linoz_psc_t = 198.0
 !--------------------------------------
 !--- chemUCI settings -----------------
 history_gaschmbudget_num = 6
 tropopause_e90_thrd    = 80.0e-9
 history_chemdyg_summary = .true.
 history_gaschmbudget_2D = .false.
 history_gaschmbudget_2D_levels = .false.
 !--------------------------------------
 rad_climate            = 'A:H2OLNZ:H2O', 'N:O2:O2', 'N:CO2:CO2',
         'A:O3:O3', 'A:N2OLNZ:N2O', 'A:CH4LNZ:CH4',
         'N:CFC11:CFC11', 'N:CFC12:CFC12',
         'M:mam5_mode1:$DIN_LOC_ROOT/atm/cam/physprops/mam4_mode1_rrtmg_aeronetdust_c141106.nc',
         'M:mam5_mode2:$DIN_LOC_ROOT/atm/cam/physprops/mam4_mode2_rrtmg_c130628.nc',
         'M:mam5_mode3:$DIN_LOC_ROOT/atm/cam/physprops/mam4_mode3_rrtmg_aeronetdust_c141106.nc',
         'M:mam5_mode4:$DIN_LOC_ROOT/atm/cam/physprops/mam4_mode4_rrtmg_c130628.nc',
         'M:mam5_mode5:$DIN_LOC_ROOT/atm/cam/physprops/mam5_mode5_rrtmg_sig1.2_dgnl.40_c03072023.nc'
 rad_diag_1 = 'A:H2OLNZ:H2O','N:O2:O2','N:CO2:CO2','A:O3:O3','A:N2OLNZ:N2O','A:CH4LNZ:CH4','N:CFC11:CFC11','N:CFC12:CFC12'
 !---------------------------------------
 !will be used when new linoz v2/v3 vertical interpolation and IO setup are used
 !linoz_data_file = 'linv3_1849-2101_CMIP6_Hist_SSP370_10deg_58km_c20230430.nc'
 !linoz_data_path = '$DIN_LOC_ROOT/atm/cam/chem/trop_mozart/ub' !on chrysalis
 !---------------------------------------
 !--- VBS SOA settings ------------------
 tracer_cnst_cycle_yr   = 1995
 tracer_cnst_datapath   = '$DIN_LOC_ROOT/atm/cam/chem/methane/'
 tracer_cnst_file       = 'ch4_oxid_1.9x2.5_L26_1990-1999clim.c090804.nc'
 tracer_cnst_filelist   = ''
 tracer_cnst_specifier  = 'CH4', 'prsd_O3:O3', 'prsd_NO3:NO3', 'prsd_OH:OH'
 tracer_cnst_type       = 'CYCLICAL' 
 drydep_list            = 'O3','H2O2','CH2O','CH3OOH','NO','NO2','HNO3','HO2NO2','PAN','CO','CH3COCH3','C2H5OOH','CH3CHO','H2SO4','SO2','NO3','N2O5'
 gas_wetdep_list        = 'C2H5OOH','CH2O','CH3CHO','CH3OOH','H2O2','H2SO4','HNO3','HO2NO2','SO2','SOAG0','SOAG15','SOAG24','SOAG35','SOAG34','SOAG33','SOAG32','SOAG31'
 gas_wetdep_method      = 'NEU'
 ext_frc_specifier      = 'NO2    -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_NO2_aircraft_vertical_1750-2015_1.9x2.5_c20170608.nc',
         'SO2    -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so2_elev_1850-2014_c180205_kzm_1850_2014_volcano.nc',
         'SOAG0  -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/emissions-cmip6_e3sm_SOAG0_elev_1850-2014_1.9x2.5_c20230201.nc',
         'bc_a4  -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_bc_a4_elev_1850-2014_c180205.nc',
         'num_a1 -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a1_elev_1850-2014_c180205.nc',
         'num_a2 -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a2_elev_1850-2014_c180205.nc',
         'num_a4 -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a4_elev_1850-2014_c180205.nc',
         'pom_a4 -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_pom_a4_elev_1850-2014_c180205.nc',
         'so4_a1 -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so4_a1_elev_1850-2014_c180205.nc',
         'so4_a2 -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so4_a2_elev_1850-2014_c180205.nc' 
 ext_frc_type           = 'INTERP_MISSING_MONTHS'
 srf_emis_specifier     = 'C2H4     -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_C2H4_surface_1850-2014_1.9x2.5_c20210323.nc', 
         'C2H6     -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_C2H6_surface_1850-2014_1.9x2.5_c20210323.nc', 
         'C3H8     -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_C3H8_surface_1850-2014_1.9x2.5_c20210323.nc',
         'CH2O     -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_CH2O_surface_1850-2014_1.9x2.5_c20210323.nc',
         'CH3CHO   -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_CH3CHO_surface_1850-2014_1.9x2.5_c20210323.nc',
         'CH3COCH3 -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_CH3COCH3_surface_1850-2014_1.9x2.5_c20210323.nc',
         'CO       -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_CO_surface_1850-2014_1.9x2.5_c20210323.nc',       
         'ISOP     -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_ISOP_surface_1850-2014_1.9x2.5_c20210323.nc',
         'ISOP_VBS -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_ISOP_surface_1850-2014_1.9x2.5_c20210323.nc',
         'C10H16   -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_MTERP_surface_1850-2014_1.9x2.5_c20230126.nc',         
         'SOAG0    -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/emissions-cmip6_e3sm_SOAG0_surf_1850-2014_1.9x2.5_c20230201.nc',
         'NO       -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_NO_surface_1850-2014_1.9x2.5_c20220425.nc',    
         'DMS      -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DMSflux.1850-2100.1deg_latlon_conserv.POPmonthlyClimFromACES4BGC_c20160727.nc',
         'SO2      -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so2_surf_1850-2014_c180205.nc',
         'bc_a4    -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_bc_a4_surf_1850-2014_c180205.nc',
         'num_a1   -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a1_surf_1850-2014_c180205.nc',
         'num_a2   -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a2_surf_1850-2014_c180205.nc',
         'num_a4   -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a4_surf_1850-2014_c180205.nc',
         'pom_a4   -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_pom_a4_surf_1850-2014_c180205.nc',
         'so4_a1   -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so4_a1_surf_1850-2014_c180205.nc',
         'so4_a2   -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so4_a2_surf_1850-2014_c180205.nc',
         'E90      -> $DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions_E90_surface_1750-2015_1.9x2.5_c20210408.nc'
 srf_emis_type          = 'INTERP_MISSING_MONTHS'
 !------------------------------------
 !--- MAM5 settings ------------------
 is_output_interactive_volc = .true.
 !------------------------------------
'''
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
      print('-'*80)
      main( e=gweff_list[n], c=cfrac_list[n], h=hdpth_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

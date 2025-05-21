#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC2/'
# src_dir  = top_dir+'E3SM_SRC4/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
queue = 'debug'  # regular / debug

# compset = 'FC5AV1C-L'
# compset = 'F2010SC5-CMIP6'
compset = 'F-MMF1'
# compset = 'F-MMF2'

# if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
if queue=='debug'  : 
   # stop_opt,stop_n,resub,walltime = 'nsteps',20,0,'0:30:00'
   stop_opt,stop_n,resub,walltime = 'ndays',1,4,'0:30:00'
   # if compset=='FC5AV1C-L': stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
if queue=='regular': 
   if compset=='FC5AV1C-L': stop_opt,stop_n,resub,walltime = 'ndays',5,0,'2:00:00'
   if compset=='F-MMF1'   : stop_opt,stop_n,resub,walltime = 'ndays',5,0,'3:00:00'
   if compset=='F-MMF2'   : stop_opt,stop_n,resub,walltime = 'ndays',5,0,'10:00:00'
  
# ne,npg = 30,2
ne,npg = 45,2
res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = res+'_'+res
grid = f'{res}_r05_oECv3'
# grid = f'{res}_r05_oQU240'


# iyr,imn,idy = 2016,8,1
# iyr,imn,idy = 2011,5,20
iyr,imn,idy = 2008,10,1
init_date = f'{iyr}-{imn:02d}-{idy:02d}'
# init_file_dir = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/'
init_file_dir = '/global/cscratch1/sd/whannah/HICCUP/data/'
init_file_sst = f'HICCUP.sst_noaa.{init_date}.nc'


# git_hash = sp.check_output(f'cd {src_dir}; git log -n1 --format=format:"%H"',shell=True,universal_newlines=True)
# case = '.'.join(['E3SM','HINDCAST',init_date,grid,compset,f'mt5555-{git_hash[-6:]}'])
# case = '.'.join(['E3SM','HINDCAST','PREQX',init_date,grid,compset,f'mt5555-{git_hash[-6:]}','00'])  # preqx dycor w/o fix
# case = '.'.join(['E3SM','HINDCAST','THETA-L',init_date,grid,compset,f'mt5555-{git_hash[-6:]}','00'])  # theta-L dycor+SL w/o fix
# case = '.'.join(['E3SM','HINDCAST','THETA-L',init_date,grid,compset,f'mt5555-{git_hash[-6:]}','01'])  # theta-L dycor+SL w/ fix
# case = '.'.join(['E3SM','HINDCAST','THETA-L',init_date,grid,compset,f'mt5555-{git_hash[-6:]}','00'])  # theta-L dycor+SL w/ fix #2

# case = '.'.join(['E3SM','HINDCAST','PREQX',init_date,grid,compset,'NLEV_125','CRMNZ_123','00']) 
# init_file_atm = f'HICCUP.atm_era5.{init_date}.ne{ne}np4.L125.nc'

### variance transport test - E3SM_SRC2
batch = '00'
case_list = ['E3SM','CVT-HC',init_date,grid,compset,'CRMNX_64','CRMDX_2000','CRMDT_5','RADNX_4']
init_file_atm = f'HICCUP.atm_era5.{init_date}.ne{ne}np4.L72.nc'
# case = '.'.join(case_list+       [batch])   # control
# case = '.'.join(case_list+['BCVT',batch])   # bulk variance transport
case = '.'.join(case_list+['SCVT',batch])   # spectral variance transport


# case = '.'.join(['E3SM','HINDCAST','PREQX',init_date,grid,compset,'NLEV_100','CRMNZ_96','00']) 
# init_file_atm = f'HICCUP.atm_era5.{init_date}.ne{ne}np4.L100.nc'

# case = '.'.join(['E3SM','HINDCAST','THETA-L',init_date,grid,compset,'00']) 


# init_file_atm = f'HICCUP.atm_era5.{init_date}.ne{ne}np4.L72.nc'
# init_file_atm = f'HICCUP.atm_era5.{init_date}.ne120np4.L72.nc'
# case = '.'.join(['E3SM','HINDCAST',init_date,grid,compset,'SL','00'])
# case = '.'.join(['E3SM','HINDCAST',init_date,grid,compset,'00'])

# init_file_atm = f'BETACAST.atm_era5.{init_date}.ne30np4.L72.nc'
# case = '.'.join(['E3SM','BETACAST',init_date,grid,compset,'SL','00'])
# case = '.'.join(['E3SM','BETACAST',init_date,grid,compset,'00'])


# case = f'E3SM_HINDCAST_{init_date}_{grid}_{compset}_00'             # control
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_RRTMG_00'       # use RRTMG instead of RRTMGP
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_RADCOL64_00'    # 64 rad cols
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_RADCOL1_00'     # 1 rad col
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_MSA0_00'        # disabled MSA
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_MSA4_00'        # crm_accel_factor=4
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_FLUX-BYPASS_00' # MMF_FLUX_BYPASS
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_ESMT_00'        # MMF_ESMT
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_CRM-AC_00'      # MMF_MOVE_CRM
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_CRM-AC_RAD-AC_00'      # MMF_MOVE_CRM + MMF_MOVE_RAD
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_CRM-AC_ESMT_00' # MMF_MOVE_CRM+MMF_ESMT
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_SGS_00'         # MMF_SGS_TUNE
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_SFC_00'         # MMF_DO_SURFACE
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_SGS_SFC_00'     # MMF_SGS_TUNE + MMF_DO_SURFACE
# case = f'E3SM_HINDCAST_{init_date}_{res}_{compset}_CRM-AC_ESMT_SGS_SFC_00' # 

# case = case+'_debug-on'
# case = case+'_checks-on'

# Specify land initial condition file
# if grid=='ne16pg2_r05_oQU240':land_init_case = f'CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2010-08-01'
# if grid=='ne30pg2_ne30pg2':   land_init_case = f'CLM_spinup.ICRUCLM45.ne30pg2_ne30pg2.15-yr.2010-{imn:02d}-{idy:02d}'
# if grid=='ne30_r05_oECv3':    land_init_case = f'CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2011-05-01'
# if grid=='ne30pg2_r05_oECv3': land_init_case = f'CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2011-05-01'
# if grid=='ne45pg2_r05_oECv3': land_init_case = f'CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2011-05-01'
if grid=='ne45pg2_r05_oECv3': land_init_case = f'CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2010-01-01'
# if grid=='ne120pg2_r05_oECv3':land_init_case = f'CLM_spinup.ICRUCLM45.ne30pg2_r05_oECv3.15-yr.2011-05-01'
# if grid=='ne30pg2_r05_oECv3': land_init_case = '????'
land_init_path = '$SCRATCH/e3sm_scratch/init_files/'   # general init file staging
# land_init_path = '$SCRATCH/e3sm_scratch/cori-knl/{land_init_case}/run/'     # run directories for E3M cases
# land_init_file = f'{land_init_path}/{land_init_case}.clm2.r.2010-{imn:02d}-{idy:02d}-00000.nc'
# land_init_file = f'{land_init_path}/{land_init_case}.clm2.r.{init_date}-00000.nc'
# if grid=='ne16pg2_r05_oQU240':
#    land_init_file = f'{land_init_path}/{land_init_case}.clm2.r.2010-08-01-00000.nc'
# else:   

if grid=='ne45pg2_r05_oECv3': land_init_file = f'{land_init_path}/{land_init_case}.clm2.r.2010-01-01-00000.nc'

if land_init_file=='':print('\nWARNING! land_init_file is disabled!\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# num_dyn = ne*ne*6
# if ne==16: dtime = 20*60
if ne==45: dtime = 20*60
# if '.ESMT.' in case: dtime = 10*60
# if ne==120: dtime = 5*60

if 'dtime' in locals(): ncpl = 86400 / dtime

# Enforce max node limit on debug queue
# if queue=='debug' and num_dyn>(64*32) : num_dyn = 64*32
# if num_dyn==0 : num_dyn = 4000


atm_ntasks = 2720
# atm_ntasks = 1350
if ne==45: atm_ntasks = 5400
#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,YELLOW,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   print('\n'+msg+'\n')
   if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += ' -compset '+compset
   cmd += ' -res '+grid
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   #-------------------------------------------------------
   # Specify CRM and RAD columns
   params = [p.split('_') for p in case.split('.')]
   for p in params:
      if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
      if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
      if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
      if p[0]=='CRMNZ': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nz {p[1]} \" ')
      if p[0]=='CRMDT': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {p[1]} \" ')
      if p[0]=='NLEV' : run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {p[1]} \" ')
   if 'NLEV_125' in case:
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt 5 \" ')
   if any( lev_str in case for lev_str in ['NLEV_125','NLEV_100'] ):
      file = open('user_nl_eam','w') 
      file.write(f' ncdata = \'{init_file_atm}\' \n')
      file.close()
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if '.FLUX-BYPASS.' in case: cpp_opt += ' -DMMF_FLUX_BYPASS'
   if '.ESMT.'        in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   if '.SGS.'         in case: cpp_opt += ' -DMMF_SGS_TUNE'
   if '.SFC.'         in case: cpp_opt += ' -DMMF_DO_SURFACE'
   if '.CRM-AC.'      in case: cpp_opt += ' -DMMF_MOVE_CRM'
   if '.RAD-AC.'      in case: cpp_opt += ' -DMMF_MOVE_RAD'

   if '.SCVT.'     in case: cpp_opt += ' -DMMF_SCVT '
   if '.BCVT.'     in case: cpp_opt += ' -DMMF_BCVT '
   if '.SCVT_MOM.' in case: cpp_opt += ' -DMMF_SCVT -DMMF_SCVT_MOM '
   if '.BCVT_MOM.' in case: cpp_opt += ' -DMMF_BCVT -DMMF_BCVT_MOM '

   # use 1 tracer for eithe variance transport method
   if '.SCVT' in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_ntrc 1 \" ')
   if '.BCVT' in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_ntrc 1 \" ')

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \'-DMMF_DIR_NS {cpp_opt} \'  \" '
      run_cmd(cmd)

   #-------------------------------------------------------
   # Set tasks and threads - disable threading for SP
   #-------------------------------------------------------

   run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val {atm_ntasks} ')

   if 'MMF' in compset:
      run_cmd('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 1 ')
   #-------------------------------------------------------
   # Switch the dycore
   #-------------------------------------------------------
   if '.THETA-L.' in case: os.system('./xmlchange CAM_TARGET=theta-l ' )
   #-------------------------------------------------------
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')

   run_cmd('./xmlquery NTASKS NTHRDS')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : os.system('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : os.system('./case.build --clean')
   os.system('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True).communicate()
   (cam_config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, \
                                     universal_newlines=True).communicate()
   cam_config_opts = ' '.join(cam_config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   # if queue=='debug'  : 
   #    file.write( ' nhtfrq    = 0,1 \n')
   #    file.write(f' mfilt     = 1,{int(ncpl)} \n')
   # else:
   file.write(' nhtfrq    = 0,-3 \n')
   file.write(' mfilt     = 1,8 \n')

   # file.write( ' nhtfrq    = 0,1 \n')
   # file.write(f' mfilt     = 1,48 \n')
   
   file.write(" fincl1    = 'TSMX:X','TSMN:M','TREFHT','QREFHT'")
   # file.write(             ",'DYN_T','DYN_Q','DYN_U','DYN_OMEGA','DYN_PS'")
   # if 'use_SPCAM' in cam_config_opts :
   #    file.write(          ",'SPQPEVP','SPMC','SPMCUP','SPMCDN','SPMCUUP','SPMCUDN'")
   file.write('\n')
   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'UBOT','VBOT'")
   file.write(             ",'TBOT','QBOT'")
   file.write(             ",'OMEGA850','OMEGA500'")
   file.write(             ",'Z100','Z500','Z700'")
   file.write(             ",'T500','T850','Q850'")
   file.write(             ",'T850:I','Q850:I'")                 # 3D radiative heating profiles
   file.write(             ",'U200','U850'")
   file.write(             ",'V200','V850'")
   file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   file.write(             ",'PTTEND','DTCOND','DCQ'")                 # 3D radiative heating profiles
   # if 'use_SPCAM' in cam_config_opts or 'use_MMF' in cam_config_opts :
   #    file.write(         ",'CRM_PREC'")
   #    file.write(         ",'CRM_QRAD'")
   #    file.write(         ",'SPDT','SPDQ'")               # CRM heating/moistening tendencies
   #    file.write(         ",'SPTLS','SPQTLS' ")           # CRM large-scale forcing
   #    file.write(         ",'SPQPEVP','SPMC'")            # CRM rain evap and total mass flux
   #    file.write(         ",'SPMCUP','SPMCDN'")           # CRM saturated mass fluxes
   #    file.write(         ",'SPMCUUP','SPMCUDN'")         # CRM unsaturated mass fluxes
   #    file.write(         ",'SPTKE','SPTKES'")
   #    file.write(         ",'CRM_T','CRM_U'")
   #    file.write(         ",'SPMC','MU_CRM'")
      # if any(x in cam_config_opts for x in ["SP_ESMT","SP_USE_ESMT","SPMOMTRANS"]) : 
      #    file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
      # if "SP_USE_ESMT" in cam_config_opts : file.write(",'U_ESMT','V_ESMT'")
      # if "SPMOMTRANS"  in cam_config_opts : 
   if 'ESMT' in case:
      # file.write(         ",'SPDT','SPDQ'")
      file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
      file.write(",'U_ESMT','V_ESMT'")
      # file.write(",'UCONVMOM','VCONVMOM'")
   file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # if compset=='F-EAMv1-RCEMIP' : 
   # if 'F-EAMv1-RCEMIP' in compset : 
   #    file.write(' prescribed_ozone_type     = \'CYCLICAL\' \n')
   #    file.write(' prescribed_ozone_cycle_yr = 2000 \n')
   #    file.write(' prescribed_ozone_name     = \'O3\' \n')
   #    file.write(' prescribed_ozone_datapath = \'/global/cscratch1/sd/whannah/acme_scratch/init_files/\' \n')
   #    file.write(' prescribed_ozone_file     = \'RCEMIP_ozone.v1.nc\' \n')
   
   # CRM mean-state acceleration (default=2)
   if '.MSA0.' in case: file.write(' use_crm_accel = .false.')
   if '.MSA4.' in case: file.write(' crm_accel_factor = 4')
   
   file.write(' srf_flux_avg = 0 \n')              # disable sfc flux smoothing (normally on for MMF)
   # if 'NLEV_125' in case: file.write(' srf_flux_avg = 1 \n')
   # file.write(' srf_flux_avg = 1 \n')              # Sfc flux smoothing (for SP stability)
   # file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

   # se_nsplit,rsplit = 20,3
   # file.write(" rsplit    = "+str(   rsplit)+" \n")
   # file.write(" se_nsplit = "+str(se_nsplit)+" \n")

   # file.write(' se_fv_phys_remap_alg = 1 \n')

   # if '.NO-SL.' in case:
   #    file.write(' transport_alg = 0 \n')
   #    file.write(' dt_tracer_factor = 1 \n')
   #    file.write(' hypervis_subcycle_q = 1 \n')

   # # Only for SL dycor
   # if '.SL.' in case:
   #    file.write(' hypervis_scaling = 3.2 \n')
   #    file.write(' nu_div = 20e-8 \n')
   #    file.write(' nu_top = 20e-8 \n')
   #    file.write(' nu     = 8e-8 \n')
   #    file.write(' nu_q   = 8e-8 \n')
   #    file.write(' nu_p   = 8e-8 \n')
   #    file.write(' nu_s   = 8e-8 \n')
   #    if 'dtime' and 'ncpl' in locals():
   #       se_tstep = 300
   #       dt_tracer_factor = int( dtime/se_tstep )
   #       file.write(f' dt_tracer_factor={dt_tracer_factor} \n')

   # file.write(" inithist = \'MONTHLY\' \n")
   file.write(' inithist = \'ENDOFRUN\' \n')

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   file.close()


   if ne==120 and npg==2 : os.system('./xmlchange -file env_run.xml      EPS_AGRID=1e-11' )

   # if ne==120 and npg==2 : 
   #    file = open('user_nl_cpl','w') 
   #    file.write(' eps_agrid = 1e-11 \n')
   #    file.close()
   # if ne==120 and npg==2 : 
   #    nfile = 'user_nl_clm'
   #    file = open(nfile,'w')
   #    file.write(' finidat = \'/global/cscratch1/sd/whannah/acme_scratch/cori-knl/E3SM_PG-LAND-SPINUP_ne120pg2_FC5AV1C-H01A_00/run/E3SM_PG-LAND-SPINUP_ne120pg2_FC5AV1C-H01A_00.clm2.r.0004-02-25-00000.nc\' \n')
   #    file.close()

   
   file = open('user_nl_elm','w')
   file.write(' hist_nhtfrq = 0,-3 \n')
   file.write(' hist_mfilt  = 1,24 \n')
   file.write(" hist_fincl2 = 'TBOT','QTOPSOIL','H2OSOI'")
   # file.write(              ",'FGEV','FCEV','FCTR','Rnet'")
   # file.write(              ",'FSH_V','FSH_G','TLAI','ZWT','ZWT_PERCH'")
   # file.write(              ",'QSOIL','QVEGT','QCHARGE'")
   if land_init_file is not None: file.write(f' finidat = \'{land_init_file}\' \n')
   file.close()

   #-------------------------------------------------------
   # Special stuff for hindcast mode
   #-------------------------------------------------------
   os.system(f'./xmlchange -file env_run.xml  RUN_STARTDATE={init_date}')
   os.system(f'./xmlchange -file env_run.xml  SSTICE_DATA_FILENAME={init_file_dir}{init_file_sst}')
   os.system(f'./xmlchange -file env_run.xml  SSTICE_YEAR_ALIGN={iyr}')
   os.system(f'./xmlchange -file env_run.xml  SSTICE_YEAR_START={iyr}')
   os.system(f'./xmlchange -file env_run.xml  SSTICE_YEAR_END={iyr+1}')
   # os.system('./xmlchange -file env_build.xml CALENDAR=GREGORIAN)

   file = open('user_nl_eam','a') 
   file.write(f' ncdata = \'{init_file_dir}{init_file_atm}\'\n')
   file.close()
   
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
   else:
      run_cmd('./xmlchange CONTINUE_RUN=FALSE')
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Done!
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') # Print the case name again
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

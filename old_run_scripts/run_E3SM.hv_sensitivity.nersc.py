#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
### default options for hydrostatic control case  
# &zmconv_nl
#  zmconv_alfa      =  0.14D0
#  zmconv_c0_lnd    =       0.007
#  zmconv_c0_ocn    =       0.007
#  zmconv_cape_cin     = 1
#  zmconv_dmpdz     =       -0.7e-3
#  zmconv_ke     =           1.5E-6
#  zmconv_mx_bot_lyr_adj     = 2
#  zmconv_tau    =  3600
#  zmconv_tiedke_add      = 0.8D0
#  zmconv_tp_fac    =  2.0D0
#  zmconv_trigdcape_ull      =  .true. 
# (not included by default:)
#  zmconv_trig_dcape_only = ?
# &ctl_nl
# dt_remap_factor        = 2
# dt_tracer_factor       = 6
# hypervis_order         = 2
# hypervis_scaling       = 0
# hypervis_subcycle      = 1
# hypervis_subcycle_q    = 6
# hypervis_subcycle_tom  = 1
# nu                     =  1.0e15
# nu_div                 = -1.0
# nu_p                   = -1.0
# nu_q                   = -1.0
# nu_s                   = -1.0
# nu_top                 = 2.5e5
# qsplit                 = -1
# rsplit                 = -1
# se_nsplit              = -1
# se_ftype               = 2
# se_tstep               = 300
# statefreq              = 480
# theta_advect_form      =  1
# theta_hydrostatic_mode = .true.
# transport_alg          =  12
# tstep_type             =  5
# (not included by default:)
# semi_lagrange_hv_q     = 1 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'
case_dir = '/global/homes/w/whannah/E3SM/Cases'
src_dir  = '/global/homes/w/whannah/E3SM/E3SM_SRC1'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True
queue = 'regular'  # regular / debug 

# if queue=='debug': stop_opt,stop_n,resub,walltime = 'nsteps',10,0,'0:30:00'
# if queue=='debug': stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'
# if queue=='debug': stop_opt,stop_n,resub,walltime = 'ndays',18,1,'0:30:00'
if queue!='debug': stop_opt,stop_n,resub,walltime = 'ndays',32*11,0,'6:00:00'


ne,npg  = 30,2; grid = f'ne{ne}pg{npg}_ne{ne}pg{npg}'
# ne,npg  = 30,0; grid = f'ne{ne}_ne{ne}'

compset = 'FC5AV1C-L'
# compset = 'F2010SC5-CMIP6'


# compset = 'WCYCL1850'; ne,npg  = 30,2; grid = f'ne{ne}pg{npg}_EC30to60E2r2'
# case = '.'.join(['E3SM','CPL-TEST',grid,compset,'00'])


### Fixed HV 
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_10e13','hvss_1']) ### crashed
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_25e13','hvss_1'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_5e14','hvss_1'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_2e15','hvss_2'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_4e15','hvss_4'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_8e15','hvss_8'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_16e15','hvss_16'])

# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_1e15' ,'hvss_1' ,'hvsq_2'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_1e15' ,'hvss_2' ,f'hvsq_{(6*2)}'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_1e15' ,'hvss_4' ,f'hvsq_{(6*4)}'])

# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_2e15' ,'hvss_2' ,f'hvsq_{(6*2)}'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_4e15' ,'hvss_4' ,f'hvsq_{(6*4)}'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_8e15' ,'hvss_8' ,f'hvsq_{(6*8)}'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_16e15','hvss_16',f'hvsq_{(6*16)}'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_32e15','hvss_32',f'hvsq_{(6*32)}'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_64e15','hvss_64',f'hvsq_{(6*64)}'])

# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_1e15' ,'hvss_1' ,'hvsq_6' ,'slhq_3'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_1e15' ,'hvss_1' ,'hvsq_6' ,'slhq_8'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_2e15' ,'hvss_2' ,'hvsq_12','slhq_3'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_4e15' ,'hvss_4' ,'hvsq_24','slhq_3'])

### ZM tests
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_1e15' ,'hvss_1' ,'hvsq_6' ,'zmdcull_0_0'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_1e15' ,'hvss_1' ,'hvsq_6' ,'zmdcull_0_1'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','nu_1e15' ,'hvss_1' ,'hvsq_6' ,'zmdcull_1_0'])

# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','iclosure_true'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','zm_alt_prev_state'])

# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','iclosure_true','zm_alt_prev_state'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','iclosure_true','dcapemin_1e-3','zm_alt_prev_state'])

# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','dcapemin_1'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','dcapemin_1e-5'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','dcapemin_1e-4'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','dcapemin_1e-3'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','dcapemin_1e-2'])

# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','dcapemin_1e-5','zm_alt_prev_state'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','dcapemin_1e-4','zm_alt_prev_state'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','dcapemin_1e-3','zm_alt_prev_state'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'control','dcapemin_1e-2','zm_alt_prev_state'])

### non-local dCAPE
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'nonlocal_dcape'])
case = '.'.join(['E3SM','HV-SENS',grid,compset,'nonlocal_dcape','zm_alt_prev_state'])


### Eulerian transport w/ fixed hypervis
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'fixed-HV','txal_0','nu_1e15','hvss_1','hvsq_1','dtrf_2','dttf_2'])

### Tensor HV 
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'tensor-HV','hvs_3','nu_05e-9','hvss_1']) ### crashed
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'tensor-HV','hvs_3','nu_10e-9','hvss_1'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'tensor-HV','hvs_3','nu_20e-9','hvss_1'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'tensor-HV','hvs_3','nu_45e-9'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'tensor-HV','hvs_3','nu_90e-9','hvss_2'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'tensor-HV','hvs_3','nu_18e-8','hvss_4'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'tensor-HV','hvs_3','nu_36e-8','hvss_8'])
# case = '.'.join(['E3SM','HV-SENS',grid,compset,'tensor-HV','hvs_3','nu_72e-8','hvss_16'])

# case = case+'.debug-on'
# case = case+'.checks-on'


### check case name
# params = [p.split('_') for p in case.split('.')]
# for p in params:
#    if len(p)>1:
#       print(f'  {p[0]:12}   {p[1]}')
# exit()

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6
# atm_ntasks = 5400

class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   print(f'\n{msg}')
   if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :

   # Check if directory already exists
   if os.path.isdir(case_dir+case):
      exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd += f' -compset {compset} -res {grid}'
   run_cmd(cmd)

   # Copy this run script into the case directory
   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
   run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_dir}/{case}/')
if config : 
   #-------------------------------------------------------  
   # Set tasks and threads - disable threading for MMF
   if 'atm_ntasks' in locals(): 
      run_cmd(f'./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val {atm_ntasks} ')
   #-------------------------------------------------------
   # Add special CPP flags
   cpp_opt = ''
   if '.iclosure_true'     in case: cpp_opt += ' -DZM_ICLOSURE_ALWAYS_TRUE '
   if '.zm_alt_prev_state' in case: cpp_opt += ' -DZM_ALT_PREV_STATE '
   if '.nonlocal_dcape'    in case: cpp_opt += ' -DZM_NONLOCAL_DCAPE '
   
      
   params = [p.split('_') for p in case.split('.')]
   for p in params:
      if p[0]=='dcapemin': cpp_opt += f' -DZM_DCAPE_MIN={p[1]} '
      

   # if '..' in case: cpp_opt += ' -D '
   # if '..' in case: cpp_opt += ' -D '

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -cppdefs \'{cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------   
   file.write(' nhtfrq    = 0,-1,-3 \n')
   file.write(' mfilt     = 1,24,8 \n')

   file.write('\n')
   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'UBOT','VBOT','TBOT','QBOT'")
   file.write(             ",'OMEGA850','OMEGA500'")
   file.write(             ",'T850','Q850'")
   file.write(             ",'U200','U850'")
   file.write(             ",'V200','V850'")
   file.write('\n')
   #------------------------------
   # Other ATM namelist stuff
   #------------------------------
   if 'atm_ntasks' in locals(): 
      if num_dyn<atm_ntasks: 
         file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')   
   
   # if 'tensor-HV' in case:

   params = [p.split('_') for p in case.split('.')]
   for p in params:
      if p[0]=='nu'  : file.write(f' nu = {p[1]}\n')
      if p[0]=='dtrf': file.write(f' dt_remap_factor       = {p[1]}\n')
      if p[0]=='dttf': file.write(f' dt_tracer_factor      = {p[1]}\n')
      if p[0]=='hvo' : file.write(f' hypervis_order        = {p[1]}\n')
      if p[0]=='hvs' : file.write(f' hypervis_scaling      = {p[1]}\n')
      if p[0]=='hvss': file.write(f' hypervis_subcycle     = {p[1]}\n')
      if p[0]=='hvsq': file.write(f' hypervis_subcycle_q   = {p[1]}\n')
      if p[0]=='hvst': file.write(f' hypervis_subcycle_tom = {p[1]}\n')
      if p[0]=='slhq': file.write(f' semi_lagrange_hv_q    = {p[1]}\n')
      if p[0]=='txal': file.write(f' transport_alg         = {p[1]}\n')

      if p[0]=='zmdcull': 
         if p[1]=='0' and p[2]=='0':
            file.write(f' zmconv_trigdcape_ull         = .false. \n')
            file.write(f' zmconv_trig_dcape_only       = .false. \n')
            file.write(f' zmconv_trig_ull_only         = .false. \n')
         if p[1]=='1' and p[2]=='0': 
            file.write(f' zmconv_trigdcape_ull         = .false. \n')
            file.write(f' zmconv_trig_dcape_only       = .true. \n')
            file.write(f' zmconv_trig_ull_only         = .false. \n')
         if p[1]=='0' and p[2]=='1':
            file.write(f' zmconv_trigdcape_ull         = .false. \n')
            file.write(f' zmconv_trig_dcape_only       = .false. \n')
            file.write(f' zmconv_trig_ull_only         = .true. \n')

   # file.write(f'\n')

   # close atm namelist file
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
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

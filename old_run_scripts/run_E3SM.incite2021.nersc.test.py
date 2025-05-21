#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, numpy as np
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC4/'

print_commands_only = False

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

queue = 'debug'  # regular / debug 

crm_dx,rad_nx = 2000,1

# nlev,crm_dt = 50,10
# nlev,crm_dt = 72, 5


compset,ne,npg = 'F-MMF1',4,2
# crm_nx,crm_ny,use_vt,use_momfb = 32, 1,True,True
# crm_nx,crm_ny,use_vt,use_momfb = 32, 1,False,False
crm_nx,crm_ny,use_vt,use_momfb = 32, 32,True,True

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
stop_opt,stop_n,resub,walltime = 'nstep',5,0,'0:30:00'


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'
grid = f'{res}_{res}'


# case_list = ['E3SM','INCITE2021-MT-TEST',arch,grid,compset]
case_list = ['E3SM','INCITE2021-MT-TEST',grid,compset]

if 'MMF' in compset:
   case_list.append(f'NXY_{crm_nx}x{crm_ny}')
   if use_vt   : case_list.append('BVT')
   if use_momfb: case_list.append('MOMFB')
   # case_list.append(f'NODES_{num_nodes}')
   # if nlev==50: case_list.append('L_50_47')
   # if nlev==72: case_list.append('L_72_58')
   # case_list.append(f'DT_{crm_dt}')
   # else:
   #    if nlev==50: case_list.append('L_50')
   #    if nlev==72: case_list.append('L_72')
case_list.append('00')

case='.'.join(case_list)


# case = case+'.debug-on'
# case = case+'.checks-on'

### specify atmos initial condition file
# init_file_dir = os.getenv('HOME')+'/HICCUP/data_scratch'
# params = [p.split('_') for p in case.split('.')]
# for p in params:
#    if p[0]=='L': 
#       if p[1]!='72': init_file_atm = f'HICCUP.cami_mam3_Linoz_ne{ne}np4.L{p[1]}.nc'

### specify land initial condition file
# land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
# if ne==45: land_init_file = 'CLM_spinup.ICRUELM.ne45pg2_r05_oECv3.20-yr.2010-10-01.elm.r.2006-01-01-00000.nc'


# Impose wall limits for Summit
if 'walltime' not in locals():
   if num_nodes>=  1: walltime =  '2:00'
   if num_nodes>= 46: walltime =  '6:00'
   if num_nodes>= 92: walltime = '12:00'
   if num_nodes>=922: walltime = '24:00'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

dtime = 20*60

if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step

# if arch=='GNUCPU' : task_per_node = 42
# if arch=='GNUGPU' and crm_ny==1 : task_per_node = 24
# if arch=='GNUGPU' and crm_ny >1 : task_per_node = 12

# atm_ntasks = task_per_node*num_nodes

atm_ntasks = 64

if crm_ny>1: 
   atm_ntasks = -999
   if crm_ny==32: atm_ntasks = 64*4

#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   if print_commands_only: 
      print(f'{msg}')
   else:
      print(f'\n{msg}')
      if execute: os.system(cmd)
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :

   # Check if directory already exists
   if not print_commands_only:
      if os.path.isdir(case_dir+case): 
         exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + f' -compset {compset} -res {grid}'
   # cmd = cmd + ' -mach summit '
   # if arch=='GNUCPU' : cmd = cmd + f' -compiler gnu    -pecount {atm_ntasks}x1 '
   # if arch=='GNUGPU' : cmd = cmd + f' -compiler gnugpu -pecount {atm_ntasks}x1 '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   if not print_commands_only: 
      os.chdir(case_dir+case+'/')
   else:
      print(tcolor.GREEN+f'cd {case_dir}{case}/'+tcolor.ENDC)
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )

   # run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {task_per_node} ')
   # run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {task_per_node} ')
else:
   if not print_commands_only: 
      os.chdir(case_dir+case+'/')
   else:
      print(tcolor.GREEN+f'cd {case_dir}{case}/'+tcolor.ENDC)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # set pcols
   # if arch=='GNUGPU': 
   #    pcols = np.ceil( (ne**2*6*npg**2) / (num_nodes*task_per_node) )
   #    run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -pcols {int(pcols)} \" ' )
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      # run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {crm_dt} -crm_dx {crm_dx}  \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: 
         run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
      
      # params = [p.split('_') for p in case.split('.')]
      # for p in params:
      #    if p[0]=='L': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {p[1]} -crm_nz {p[2]} \" ')

   else:
      # non-MMF
      params = [p.split('_') for p in case.split('.')]
      # for p in params:
      #    if p[0]=='L': 
      #       if p[1]!=72: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {p[1]} \" ')

   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

   if  crm_ny==1: cpp_opt += ' -DMMF_DIR_NS'
   if  crm_ny==1 and use_momfb: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   if  crm_ny>1  and use_momfb: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   cmd = './xmlchange -file env_mach_pes.xml '
   # if ne==30: alt_ntask = 1200
   alt_ntask = 120
   if ne==4: alt_ntask = min(atm_ntasks,64)
   cmd += f'NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   cmd += f',NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   # alt_ntask = task_per_node
   alt_ntask = 1
   cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)

   ### don't use threads
   # nthrds = 2
   # cmd = f'./xmlchange -file env_mach_pes.xml '
   # cmd += f'NTHRDS_CPL={nthrds},NTHRDS_CPL={nthrds},'
   # cmd += f'NTHRDS_OCN={nthrds},NTHRDS_ICE={nthrds}'
   # run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large numbers of columns (GCM or CRM)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
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
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')

   #-------------------------------------------------------
   # ATM namelist
   #-------------------------------------------------------
   if not print_commands_only: 
      # Change inputdata from default due to permissions issue
      # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/scratch/hannah6/inputdata ')
      # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')
      
      #-------------------------------------------------------
      # First query some stuff about the case
      #-------------------------------------------------------
      (ncpl        ,err) = sp.Popen('./xmlquery ATM_NCPL        -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      (din_loc_root,err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      (config_opts ,err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
      #-------------------------------------------------------
      # Namelist options
      #-------------------------------------------------------
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      #------------------------------
      # Specify history output frequency and variables
      #------------------------------
      # file.write(' nhtfrq = 0,-3 \n')
      # file.write(' mfilt  = 1, 8 \n')
      file.write(' nhtfrq = 0, 1 \n')
      file.write(' mfilt  = 1,10 \n')

      file.write('\n')
      file.write(" fincl2 = 'PS','TS'")
      file.write(          ",'PRECT','TMQ'")
      file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(          ",'TGCLDLWP','TGCLDIWP'")
      file.write(          ",'TAUX','TAUY'")               # surface stress
      file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
      file.write(          ",'U','V','OMEGA'")             # 3D velocity components
      file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
      # file.write(          ",'PTTEND','PTEQ'")

      file.write(          ",'DUV','DVV'")                # 3D PBL tendencies
      file.write(          ",'RAY_DU','RAY_DV'")          # 3D Rayleigh friction tendencies
      file.write(          ",'GWD_DU','GWD_DV'")          # 3D gravity wave tendencies
      file.write(          ",'TAUTMSX','TAUTMSY'")        # turbulent mountain stress tendencies
      file.write(          ",'DYN_DU','DYN_DV'")          # Dynamics momentum tendencies
      file.write(          ",'TOT_DU','TOT_DV'")          # total momentum tendencies
      

      # DUDT = DYN + CRM + GW + TAU + PBL + R

      if 'MMF' in compset:
         if use_momfb: file.write(",'MMF_DU','MMF_DV'")
         # file.write(       ",'MMF_DT','MMF_DQ'")           # CRM heating/moistening tendencies
         # file.write(       ",'MMF_TLS','MMF_QTLS' ")       # CRM large-scale forcing

      file.write('\n')
      # file.write(" fincl3    =  'T','Q','Z3' ")               # 3D thermodynamic budget components
      # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
      # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
      # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      # file.write('\n')
      #------------------------------
      # Other namelist stuff
      #------------------------------

      # limit dynamics tasks
      if num_dyn<atm_ntasks: 
         file.write(f' dyn_npes = {num_dyn} \n')
         # if num_nodes==1013 and ne==45:
         #    ntask_dyn = 500*task_per_node
         #    file.write(f' dyn_npes = {ntask_dyn} \n')
         # else:
         #    file.write(f' dyn_npes = {num_dyn} \n')

      if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

      # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE

      if 'dtime' in locals():
         if dtime == 20*60 :
            # ne45 is already configured for 20 min time step
            if ne==30 :
               file.write(f'dt_tracer_factor = 4 \n')
               file.write(f'dt_remap_factor = 4 \n')
               file.write(f'se_tstep = 300 \n')
            if ne==4 :
               file.write(f'dt_tracer_factor = 2 \n')
               file.write(f'dt_remap_factor = 2 \n')
               file.write(f'se_tstep = 600 \n')

      if 'init_file_atm' in locals():
         file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

      file.close()

   #-------------------------------------------------------
   # CLM namelist
   #-------------------------------------------------------
   if not print_commands_only: 
      if 'land_init_file' in locals():
         nfile = 'user_nl_elm'
         file = open(nfile,'w')
         file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
         file.close()
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

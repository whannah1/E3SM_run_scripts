#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp#, numpy as np
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli145' # cli115 / cli145

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
# src_dir  = top_dir+'E3SM_SRC3/'

print_commands_only = False

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# compset = 'FC5AV1C-L'
compset = 'F-MMFXX'
# compset = 'F-MMFOMP'


# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,'GNUGPU',1,'nsteps',72*10,0,'1:00'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,'GNUGPU',1,'ndays',1,0,'0:30'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,'GNUGPU',1,'ndays',32,0,'0:30'

# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 30,2,'GNUGPU',128,'ndays',73*2,5-1,'2:00'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 30,2,'GNUGPU',128,'ndays',365,0,'3:00'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 30,2,'GNUGPU',128,'ndays',32,0,'0:30'

ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 30,2,'GNUCPU',128,'ndays',2,0,'0:30'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 30,2,'GNUGPU',128,'ndays',365,1,'3:00'


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'
grid = f'{res}_{res}'
   

### flux injection tests
src_dir = top_dir+'E3SM_SRC1/' # whannah/mmf/sgs-mods-for-boundary-fluxes
# compset = 'F-MMFXX'
compset = 'F-MMF1'
# compset = 'F-MMFOMP'
case = '.'.join(['E3SM','CRM_SFC_FLUX_TEST',arch,grid,compset,'00']) # baseline
# case = '.'.join(['E3SM','CRM_SFC_FLUX_TEST',arch,grid,compset,'01']) # flux injection mods (no change in actual flux)
# case = '.'.join(['E3SM','CRM_SFC_FLUX_TEST',arch,grid,compset,'02']) # flux injection mods + move fluxes
# src_dir = top_dir+'E3SM_BASE/'; case = '.'.join(['E3SM','CRM_SFC_FLUX_TEST',arch,grid,compset,'NLEV_60','00a']) # baseline
# src_dir = top_dir+'E3SM_BASE/'; case = '.'.join(['E3SM','CRM_SFC_FLUX_TEST',arch,grid,compset,'NLEV_72','00a']) # baseline


### precipitating water path tests
# case = '.'.join(['E3SM','WP-TEST',arch,grid,compset,'NLEV_60','CRMNX_128','RADNX_8','BVT','00']) # original test
# case = '.'.join(['E3SM','WP-TEST',arch,grid,compset,'NLEV_60','CRMNX_128','RADNX_8','BVT','01']) # added new monthly output

### test slowing down ice to increase anvil clouds
# case = '.'.join(['E3SM','ICE-FALL-TEST',arch,grid,compset,'RADNX_8','BVT','00']) # control
# case = '.'.join(['E3SM','ICE-FALL-TEST',arch,grid,compset,'RADNX_8','BVT','REDUCE-FALL','00']) # add MMF_REDUCE_ICE_FALL
# case = '.'.join(['E3SM','ICE-FALL-TEST',arch,grid,compset,'RADNX_8','BVT','NO-ICE-FALL','00']) # add MMF_DISABLE_ICE_FALL

### QBO test (use brhillman/mmf/integrate-rrtmgpxx-new to avoid memory leak)
# src_dir=top_dir+'E3SM_SRC1/'; case = '.'.join(['E3SM','QBO-TEST',arch,grid,compset,'00']) # control
# src_dir=top_dir+'E3SM_SRC1/'; case = '.'.join(['E3SM','QBO-TEST',arch,grid,compset,'RRTMGPXX','00']) # control+RRTMGP
# src_dir=top_dir+'E3SM_SRC1/'; case = '.'.join(['E3SM','QBO-TEST',arch,grid,compset,'GWC','GWF','00']) # enable convective and frontal gw
# src_dir=top_dir+'E3SM_SRC1/'; case = '.'.join(['E3SM','QBO-TEST',arch,grid,compset,'GWC','00']) # enable convective gw
# src_dir=top_dir+'E3SM_SRC1/'; case = '.'.join(['E3SM','QBO-TEST',arch,grid,compset,'GWF','00']) # enable frontal gw




# case = case+'.debug-on'
# case = case+'.checks-on'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

# Impose wall limits for Summit
if 'walltime' not in locals():
   if num_nodes>=  1: walltime =  '2:00'
   if num_nodes>= 46: walltime =  '6:00'
   if num_nodes>= 92: walltime = '12:00'
   if num_nodes>=922: walltime = '24:00'


### specify atmos initial condition file
# init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
# init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/'
init_file_dir= '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/atm/cam/inic/homme'
params = [p.split('_') for p in case.split('.')]
for p in params:
   if p[0]=='NLEV': 
      # if p[1]!='72': 
      #    if p[1]=='50': init_file_atm = f'HICCUP.cami_mam3_Linoz_ne{ne}np4.L{p[1]}_c20210623.nc'
      #    if p[1]=='60': init_file_atm = f'HICCUP.cami_mam3_Linoz_ne{ne}np4.L{p[1]}.nc'
      if p[1]=='72': init_file_atm = f'{init_file_dir}/cami_mam3_Linoz_ne30np4_L72_c160214.nc'

# if 'alt_vgrid' in case:
#    init_file_atm = 'HICCUP.cami_mam3_Linoz_ne30np4_L72_alt_c160214.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

num_dyn = ne*ne*6

# dtime = 20*60
if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes

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
      if os.path.isdir(f'{case_dir}/{case}'): 
         exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = src_dir+f'cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid} -mach summit '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='IBMGPU' : cmd += f' -compiler ibmgpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   if not print_commands_only: 
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )
   #-------------------------------------------------------
   #-------------------------------------------------------
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   if not print_commands_only: 
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      # file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      file.write(f' ncdata = \'{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # # explicitly specify rad option
   # if '.RRTMG.'    in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmg \"')
   # if '.RRTMGP.'   in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp \"')
   if '.RRTMGPXX.'   in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp -rrtmgpxx \"')

   params = [p.split('_') for p in case.split('.')]
   for p in params: 
      if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
      if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
      if p[0]=='CRMNY': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_ny {p[1]} \" ')
      if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
      if p[0]=='CRMNZ': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nz {p[1]} \" ')
      if p[0]=='CRMDT': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {p[1]} \" ')
      
      # if p[0]=='NLEV' : run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {p[1]} \" ')
      # if p[0]=='NLEV' and p[1] != '72' : 
      if p[0]=='NLEV' and p[1] != '60' : 
         nlev = p[1]; crm_nz = None
         if nlev== '72': crm_nz =  '58'
         # if nlev== '60': crm_nz =  '50'
         # if nlev=='100': crm_nz =  '95'
         # if nlev=='120': crm_nz = '115'
         if crm_nz is None: raise ValueError('No value of crm_nz specified')
         run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {p[1]} -crm_nz {crm_nz} \" ')
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if '.ESMT.'        in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   if '.MOMFB.'       in case: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

   if '.CRM_SFC_FLUX_TEST.' in case: 
      if '.01' in case: cpp_opt += ' -DMMF_TKE_MOD'
      if '.02' in case: cpp_opt += ' -DMMF_TKE_MOD -DMMF_CRM_SFC_FLUX'

   if 'ICE-FALL-TEST' in case:
      if '.REDUCE-FALL' in case: cpp_opt += ' -DMMF_REDUCE_ICE_FALL'
      if '.NO-ICE-FALL' in case: cpp_opt += ' -DMMF_DISABLE_ICE_FALL'

   # convective variance transport
   if any(x in case for x in ['.BVT.','.FVT']): 
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   if '.FVT' in case: 
      params = [p.split('_') for p in case.split('.')]
      for p in params:
         if p[0]=='FVT': cpp_opt += f' -DMMF_VT_KMAX={p[1]} '

   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \'{cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Switch the dycore
   # if '.THETA-L.' in case: os.system('./xmlchange CAM_TARGET=theta-l ' )
   #-------------------------------------------------------
   # Set tasks and threads
   
   cmd = './xmlchange -file env_mach_pes.xml '
   # cmd += f' NTASKS_ATM={atm_ntasks}'
   # alt_ntask = task_per_node*np.ceil(ne/4)
   if ne==4 : alt_ntask = task_per_node
   if 'GPU' in arch:
      if ne==0  and num_nodes== 64: alt_ntask = 256
      if ne==0  and num_nodes==128: alt_ntask = 256
      if ne==30 and num_nodes== 64: alt_ntask = 256
      if ne==30 and num_nodes== 96: alt_ntask = 576
      if ne==30 and num_nodes==128: alt_ntask = 720
   if 'CPU' in arch:
      if ne==30 and num_nodes== 64: alt_ntask = 1200
      if ne==30 and num_nodes==128: alt_ntask = 1200
   cmd += f'NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   cmd += f',NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   alt_ntask = task_per_node
   cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)


   cmd = './xmlchange -file env_mach_pes.xml '
   if 'GPU' in arch: alt_nthrds = 7
   if 'CPU' in arch: alt_nthrds = 1
   cmd += f'NTHRDS_LND={alt_nthrds},NTHRDS_CPL={alt_nthrds}'
   cmd += f',NTHRDS_OCN={alt_nthrds},NTHRDS_ICE={alt_nthrds}'
   cmd += f',NTHRDS_ROF=1,NTHRDS_WAV=1,NTHRDS_GLC=1,NTHRDS_ESP=1,NTHRDS_IAC=1'
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
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): 
      run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)},LND_NCPL={str(ncpl)},ICE_NCPL={str(ncpl)},OCN_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE=batch,JOB_WALLCLOCK_TIME={walltime}')
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
      run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')
      
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
      if stop_opt=='nsteps' or stop_opt=='nstep' :
         if 'ncpl' in locals(): 
            file.write(' nhtfrq    = 0,1 \n') 
            file.write(f' mfilt    = 1,{int(ncpl)} \n')
         else:
            file.write(' nhtfrq    = 0,1 \n') 
            file.write(' mfilt     = 1,'+str(stop_n)+' \n')
      else:
         file.write(' nhtfrq    = 0,-3 \n')
         file.write(' mfilt     = 1, 8 \n')
      file.write(" fincl1    = 'Z3','CLDLIQ','CLDICE'")
      # file.write(" fincl1    = 'TSMX:X','TSMN:M','TREFHT','QREFHT'")
      # file.write(             ",'TGCLDLWP','TGCLDIWP'")        # cloud water path
      # file.write(             ",'TGPRCLWP','TGPRCIWP'")      # precipitating water path
      # file.write(             ",'ICLDTWP','ICLDLWP','ICLDIWP'")
      # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")
      file.write('\n')
      file.write(" fincl2    = 'PS','TS','PSL'")
      file.write(             ",'PRECT','TMQ'")
      file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(             ",'TGCLDLWP','TGCLDIWP'")       # cloud water path
      # file.write(             ",'TGPRCLWP','TGPRCIWP'")       # precipitating water path
      # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
      # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
      # file.write(             ",'TAUX','TAUY'")               # surface stress
      # variables for TC or AR tracking 
      file.write(          ",'TUQ','TVQ'")                         # vapor transport
      file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
      file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
      file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
      file.write(          ",'Z300:I','Z500:I'")
      file.write(          ",'OMEGA850:I','OMEGA500:I'")
      # file.write(             ",'T','Q','Z3' ")              # 3D thermodynamic budget components
      # file.write(             ",'U','V','OMEGA'")            # 3D velocity components
      # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")  # 3D cloud fields
      # file.write(             ",'QRL','QRS'")                # 3D radiative heating profiles

      file.write(          ",'MMF_TK','MMF_TKE','MMF_TKES'")

      # # if 'ESMT-TEST' in case:
      # #    file.write(",'U','V'")
      # #    file.write(",'MMF_DU','MMF_DV'")
      
      # if 'use_MMF' in config_opts :
      #    file.write(          ",'MMF_DT','MMF_DQ'")           # CRM heating/moistening tendencies
      #    file.write(          ",'MMF_TLS','MMF_QTLS' ")       # CRM large-scale forcing
      #    # if 'use_MMF_VT' in config_opts :
      #    #    file.write(          ",'MMF_VT_T','MMF_VT_Q'")
      #    #    file.write(          ",'MMF_VT_TEND_T','MMF_VT_TEND_Q'")
      #    #    file.write(          ",'MMF_VT_TLS','MMF_VT_QLS'")
      #    # file.write(          ",'CRM_T','CRM_QV','CRM_QC','CRM_QI','CRM_W'")
      #    # file.write(          ",'MMF_SUBCYCLE_FAC'")
      #    # file.write(          ",'MMF_TKE','MMF_TKEW','MMF_TKES'")
      #    # file.write(          ",'CRM_PREC','CRM_QRAD'")
      #    # file.write(          ",'MMF_QPEVP','MMF_MC'")        # CRM rain evap and total mass flux
      #    # file.write(          ",'SPMCUP','SPMCDN'")           # CRM saturated mass fluxes
      #    # file.write(          ",'SPMCUUP','SPMCUDN'")         # CRM unsaturated mass fluxes
      #    # file.write(          ",'SPTKE','SPTKES'")
      #    # file.write(          ",'CRM_T','CRM_U'")
      #    # file.write(          ",'SPMC','MU_CRM'")
      #    # if 'MMF_MOMENTUM_FEEDBACK' in config_opts  :
      #    #    file.write(        ",'MMF_DU','MMF_DV','ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
      #    # if "MMF_USE_ESMT" in config_opts : 
      #    #    file.write(",'MMF_DU','MMF_DV'")
      #    #    # file.write(",'U_ESMT','V_ESMT'")
      #    #    # file.write(",'U_TEND_ESMT','V_TEND_ESMT'")
      # file.write('\n')
      # # file.write(" fincl3    =  'T','Q','Z3' ")               # 3D thermodynamic budget components
      # # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
      # # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
      # # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      file.write('\n')
      #------------------------------
      # Other namelist stuff
      #------------------------------
      # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\'\n')

      if num_dyn>0 and num_dyn<atm_ntasks: 
         file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

      if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

      if 'QBO-TEST' in case: 
         if '.GWC.' in case: file.write(' use_gw_convect = .true. \n')
         if '.GWF.' in case: file.write(' use_gw_front = .true. \n')

      # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE

      if 'dtime' in locals():
         if dtime == 20*60 :
            if ne==4 :
               file.write(f'dt_tracer_factor = 2 \n')
               file.write(f'dt_remap_factor = 2 \n')
               file.write(f'se_tstep = 600 \n')
            if ne==30 :
               file.write(f'dt_tracer_factor = 4 \n')
               file.write(f'dt_remap_factor = 4 \n')
               file.write(f'se_tstep = 300 \n')
         if dtime == 15*60 :
            file.write(f'dt_tracer_factor = 1 \n')
            file.write(f'dt_remap_factor = 1 \n')
            file.write(f'se_tstep = 300 \n')
         if dtime == 10*60 :
            file.write(f'dt_tracer_factor = 1 \n')
            file.write(f'dt_remap_factor = 1 \n')
            file.write(f'se_tstep = 300 \n')
         if dtime == 5*60 :
            file.write(f'dt_tracer_factor = 5 \n')
            file.write(f'dt_remap_factor = 1 \n')
            file.write(f'se_tstep = 60 \n')

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

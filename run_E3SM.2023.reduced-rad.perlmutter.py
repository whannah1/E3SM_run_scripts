#!/usr/bin/env python3
import os, subprocess as sp
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run,fix_config,kill_job = False,False,False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/mmf/2023-reduced-rad-sensitivity

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

disable_bfb = False

compset,num_nodes,arch = 'F2010-MMF1',64,'GNUGPU'

# stop_opt,stop_n,resub,walltime = 'ndays',73,4*5-1,'6:00:00' 

crm_nx_list,crm_dx_list,rad_nx_list,mcica_flag_list  = [],[],[],[]
def add_case(crm_nx_in,crm_dx_in,rad_nx_in,mcica_flag_in):
   crm_nx_list.append(crm_nx_in)
   crm_dx_list.append(crm_dx_in)
   rad_nx_list.append(rad_nx_in)
   mcica_flag_list.append(mcica_flag_in)


# add_case( 128, 1000, 128, True )
# add_case( 128, 1000,  64, True )
# add_case( 128, 1000,  32, True )
# add_case( 128, 1000,  16, True )
# add_case( 128, 1000,   8, True )
# add_case( 128, 1000,   4, True )
# add_case( 128, 1000,   2, True )
# add_case( 128, 1000,   1, True )

# add_case( 128, 1000, 128, False )
# add_case( 128, 1000,  64, False )
# add_case( 128, 1000,  32, False )
# add_case( 128, 1000,  16, False )
# add_case( 128, 1000,   8, False )
# add_case( 128, 1000,   4, False )
# add_case( 128, 1000,   2, False )
# add_case( 128, 1000,   1, False )

add_case(  64, 2000,  64, True )
# add_case(  64, 2000,  32, True )
# add_case(  64, 2000,  16, True )
add_case(  64, 2000,   8, True )
# add_case(  64, 2000,   4, True )
# add_case(  64, 2000,   2, True )
add_case(  64, 2000,   1, True )

add_case(  64, 2000,  64, False )
# add_case(  64, 2000,  32, False )
# add_case(  64, 2000,  16, False )
add_case(  64, 2000,   8, False )
# add_case(  64, 2000,   4, False )
# add_case(  64, 2000,   2, False )
add_case(  64, 2000,   1, False )

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(crm_nx=None,crm_dx=None,rad_nx=None,mcica_flag=None):

   if rad_nx is None: exit('rad_nx argument not provided?')

   ne,npg = 30,2
   crm_ny = 1
   grid = f'ne30pg2_oECv3'

   mcica_str = 'MCICA_ON' if mcica_flag else 'MCICA_OFF'

   case='.'.join(['E3SM','2023-RAD-SENS-00',arch,grid,compset,f'NXY_{crm_nx}x{crm_ny}',f'RNX_{rad_nx}',f'{mcica_str}'])

   print('\n  case : '+case+'\n')
   #------------------------------------------------------------------------------------------------   
   land_init_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/'
   lnd_init_file = f'{land_init_path}/ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   land_data_path = f'/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
   land_data_file = f'{land_data_path}/surfdata_ne30pg2_simyr2010_c210402.nc'
   #------------------------------------------------------------------------------------------------
   if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'

   if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 128,1
   if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =   4,8
   atm_ntasks = max_mpi_per_node*num_nodes
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      cmd += f' --project {acct} '
      cmd += f' --walltime {walltime} '
      if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if fix_config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      os.chdir(f'{case_root}')
      run_cmd(f'mv {case_root}/{case}/bld {case_root}/bld')
      run_cmd(f'mv {case_root}/{case}/run {case_root}/run')
      os.rmdir(f'{case_root}/{case}')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------
      # Set some non-default stuff for all MMF experiments here
      if 'MMF' in compset:
         rad_ny = rad_nx if crm_ny>1 else 1
         # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dx {crm_dx}  \" ')
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      #-------------------------------------------------------
      # Add special MMF options based on case name
      cpp_opt = ''
      if not mcica_flag : cpp_opt += ' -DMMF_MCICA_OFF'
      if cpp_opt != '' :
         cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
         cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
         run_cmd(cmd)
      #-------------------------------------------------------
      # Set tasks for all components
      # if ne>=30:
      #    cmd = './xmlchange --file env_mach_pes.xml '
      #    alt_ntask = 512; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      #    alt_ntask = 512; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
      #    alt_ntask = max_mpi_per_node
      #    cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
      #    cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
      #    run_cmd(cmd)
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if 'debug-on' in case : run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean-all')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   # Write the namelist options and submit the run
   #------------------------------------------------------------------------------------------------
   if submit : 
      #-------------------------------------------------------
      # ATM namelist
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      file.write(' nhtfrq = 0,-3,-24 \n')
      file.write(' mfilt  = 1, 8,1 \n')
      file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
      file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
      file.write(         ",'MMF_MC','MMF_MCUP','MMF_MCDN','MMF_MCUUP','MMF_MCUDN'")
      file.write('\n')
      file.write(" fincl2 = 'PS','TS','PSL'")
      file.write(          ",'PRECT','TMQ'")
      file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(          ",'TGCLDLWP','TGCLDIWP'")
      file.write(          ",'TAUX','TAUY'")               # surface stress
      file.write(          ",'TUQ','TVQ'")                         # vapor transport
      # variables for tracking stuff with TempestExtremes
      file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
      file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
      file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
      file.write(          ",'Z300:I','Z500:I'")
      file.write(          ",'OMEGA850:I','OMEGA500:I'")
      file.write(          ",'U200:I','V200:I'")
      file.write('\n')
      # file.write(" fincl3 =  'PS','PSL'")
      # file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
      # file.write(          ",'U','V','OMEGA'")             # 3D velocity components
      # file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      # file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
      # file.write('\n')
      file.close()
      #-------------------------------------------------------
      # ELM namelist
      if 'lnd_init_file' in globals() or 'lnd_data_file' in globals(): 
         nfile = 'user_nl_elm'
         file = open(nfile,'w')
         if 'lnd_init_file' in globals(): file.write(f' finidat = \'{lnd_init_file}\' \n')
         if 'lnd_data_file' in globals(): file.write(f' fsurdat = \'{lnd_data_file}\' \n')
         file.close()
      #-------------------------------------------------------
      # Set some run-time stuff
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      
      if 'disable_bfb' in globals():
         if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
         if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')

      if 'continue_run' in globals():
         if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
         if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   if kill_job :
      user = os.getenv('USER')
      run_cmd(f'scancel --user={user} --name=run.{case}')
      # Alternate method using jobid
      # cmd = f'squeue --user={user} --format="%i" --name=run.{case}'
      # (msg,err) = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
      # job_id = int(msg.split()[1])
      # run_cmd(f'scancel --user={user} {job_id}')
      
      
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(rad_nx_list)):
      print('-'*80)
      main(crm_nx=crm_nx_list[n],crm_dx=crm_dx_list[n],rad_nx=rad_nx_list[n],mcica_flag=mcica_flag_list[n])


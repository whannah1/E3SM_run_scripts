#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run,reset_resub,st_archive = False,False,False,False,False,False,False,False

acct = 'atm146'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/mmf/pam-updates

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True
### reset_resub  = True

# queue = 'regular' # batch / debug

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'2:00:00' 
stop_opt,stop_n,resub,walltime = 'ndays',32,12-1,'2:00:00'

arch = 'GNUGPU'

#---------------------------------------------------------------------------------------------------
comp_list = []
grid_list = []
node_list = []
pert_list = []
def add_case(comp,grid,node,pert):
   comp_list.append(comp)
   grid_list.append(grid)
   node_list.append(node)
   pert_list.append(pert)
   
#---------------------------------------------------------------------------------------------------

add_case( 'F2010-MMF1', 'ne30pg2_ne30pg2',  32, 0)
add_case( 'F2010-MMF1', 'ne30pg2_ne30pg2',  32, 4)
add_case( 'F2010-MMF2', 'ne30pg2_ne30pg2', 128, 0)
add_case( 'F2010-MMF2', 'ne30pg2_ne30pg2', 128, 4)


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset,grid,num_nodes,sst_pert):

   case_list = ['E3SM','2024-MMF-CESS-00',compset,arch,grid,f'NN_{num_nodes}',f'SSTP_{sst_pert}K']
   
   case='.'.join(case_list)

   # print(case); exit()
   #------------------------------------------------------------------------------------------------
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  =  42,1 ; max_task_per_node = 42
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   6,7 ; max_task_per_node = 6
   atm_ntasks = max_mpi_per_node*num_nodes
   scratch = '/gpfs/alpine2/atm146/proj-shared/hannah6/e3sm_scratch/'
   case_root = f'{scratch}/{case}'
   #------------------------------------------------------------------------------------------------
   print('\n  case : '+case+'\n')
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase : 
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase --case {case}'
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} --walltime {walltime} '
      if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
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
      write_atm_nl_opts(compset)
      #-------------------------------------------------------
      # # update nlev
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 72 \" ')
      #-------------------------------------------------------
      # cpp_opt = ''
      # if cpp_opt != '' :
      #    cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      #    cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      #    run_cmd(cmd)
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   # Build
   if build : 
      if 'debug-on' in case : run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   # Write the namelist options and submit the run
   if submit : 
      write_atm_nl_opts(compset)
      #-------------------------------------------------------
      os.system(f'./xmlchange RUN_STARTDATE=2019-08-01')
      #-------------------------------------------------------
      # SST files and parameters
      DIN_LOC_ROOT = '/gpfs/alpine2/atm146/world-shared/e3sm/inputdata'
      sst_grid_name = f'{DIN_LOC_ROOT}/ocn/docn7/domain.ocn.3600x7200.230522.nc'
      if sst_pert==0:
         sst_file_name = f'{DIN_LOC_ROOT}/atm/cam/sst/sst_ostia_ukmo-l4_ghrsst_3600x7200_20190731_20200901_c20230913.nc'
      if sst_pert==4:
         sst_file_name = f'{DIN_LOC_ROOT}/atm/cam/sst/sst_ostia_ukmo-l4_ghrsst_3600x7200_20190731_20200901_plus4K_c20230916.nc'
      os.system(f'./xmlchange --file env_run.xml SSTICE_DATA_FILENAME={sst_file_name}')
      os.system(f'./xmlchange --file env_run.xml SSTICE_GRID_FILENAME={sst_grid_name}')
      os.system(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_ALIGN --val 2019')
      os.system(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_START --val 2019')
      os.system(f'./xmlchange --file env_run.xml --id SSTICE_YEAR_END --val 2020')
      #-------------------------------------------------------
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      # if 'resub' in globals() and not continue_run: run_cmd(f'./xmlchange RESUBMIT={resub}')
      # if 'resub' in globals() and reset_resub: run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'resub' in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
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
def write_atm_nl_opts(compset):
   nfile = 'user_nl_eam'
   file = open(nfile,'w')
   file.write(' nhtfrq = 0,-1,-1 \n')
   file.write(' mfilt  = 1,24,24 \n')
   file.write('\n')
   file.write(" fincl1 = 'Z3','CLOUD','CLDLIQ','CLDICE'\n")
   file.write(" fincl2 = 'PS','PSL','TS'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
   file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
   # variables for tracking stuff like hurricanes
   file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model level
   file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(          ",'Z300:I','Z500:I'")
   file.write(          ",'OMEGA850:I','OMEGA500:I'")
   file.write(          ",'U200:I','V200:I'")
   file.write('\n')
   # init_root = '/pscratch/sd/w/whannah/HICCUP'
   # init_file = f'{init_root}/eam_i_aquaplanet_ne{ne}np4_L72-mmf_c20240607.nc'
   # file.write(f" ncdata  = '{init_file}' \n")
   # disable all aerosol rad for all cases
   # file.write(f" do_aerosol_rad  = .false. \n")
   file.close()

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(comp_list)):
      # print('-'*80)
      main( comp_list[n], \
            grid_list[n], \
            node_list[n], \
            pert_list[n], \
           )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

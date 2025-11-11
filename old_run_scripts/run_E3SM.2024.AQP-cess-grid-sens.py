#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run,reset_resub,st_archive = False,False,False,False,False,False,False,False

acct = 'm3312'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # whannah/2024-aqua-res-ensemble

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True
### reset_resub  = True

# queue = 'regular' # batch / debug

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'6:00:00' 
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'3:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',32,3-1,'3:00:00'

#---------------------------------------------------------------------------------------------------
comp_list = []
arch_list = []
node_list = []
pert_list = []
ne_list = []
def add_case(comp,ne,arch,node,pert):
   comp_list.append(comp)
   arch_list.append(arch)
   node_list.append(node)
   pert_list.append(pert)
   ne_list.append(ne)
   
#---------------------------------------------------------------------------------------------------

# add_case( 'FAQP-MMF1',  30, 'GNUGPU',   16, 0)
# add_case( 'FAQP-MMF1',  45, 'GNUGPU',   36, 0)
# add_case( 'FAQP-MMF1',  60, 'GNUGPU',   64, 0)
# add_case( 'FAQP-MMF1',  90, 'GNUGPU',  144, 0)
# add_case( 'FAQP-MMF1', 120, 'GNUGPU',  256, 0)
# add_case( 'FAQP-MMF1', 180, 'GNUGPU',  576, 0)
# add_case( 'FAQP-MMF1', 240, 'GNUGPU', 1024, 0)

# add_case( 'FAQP-MMF1',  30, 'GNUGPU',   16, 4)
# add_case( 'FAQP-MMF1',  45, 'GNUGPU',   36, 4)
# add_case( 'FAQP-MMF1',  60, 'GNUGPU',   64, 4)
# add_case( 'FAQP-MMF1',  90, 'GNUGPU',  144, 4)
# add_case( 'FAQP-MMF1', 120, 'GNUGPU',  256, 4)
# add_case( 'FAQP-MMF1', 180, 'GNUGPU',  576, 4)
# add_case( 'FAQP-MMF1', 240, 'GNUGPU', 1024, 4)

# add_case( 'FAQP',       30, 'GNUCPU',   16, 0)
# add_case( 'FAQP',       45, 'GNUCPU',   36, 0)
# add_case( 'FAQP',       60, 'GNUCPU',   64, 0)
# add_case( 'FAQP',       90, 'GNUCPU',  144, 0)
# add_case( 'FAQP',      120, 'GNUCPU',  256, 0)
# add_case( 'FAQP',      180, 'GNUCPU',  576, 0)
# add_case( 'FAQP',      240, 'GNUCPU', 1024, 0)

# add_case( 'FAQP',       30, 'GNUCPU',   16, 4)
# add_case( 'FAQP',       45, 'GNUCPU',   36, 4)
# add_case( 'FAQP',       60, 'GNUCPU',   64, 4)
# add_case( 'FAQP',       90, 'GNUCPU',  144, 4)
# add_case( 'FAQP',      120, 'GNUCPU',  256, 4)
# add_case( 'FAQP',      180, 'GNUCPU',  576, 4)
# add_case( 'FAQP',      240, 'GNUCPU', 1024, 4)



# add_case( 'FAQP-MMF1',  30, 'GNUGPU',   16, 0)
# add_case( 'FAQP-MMF1',  30, 'GNUGPU',   16, 4)
add_case( 'FAQP-MMF1', 120, 'GNUGPU',  256, 0)
add_case( 'FAQP-MMF1', 120, 'GNUGPU',  256, 4)


# add_case( 'FAQP',       30, 'GNUCPU',   16, 0)
# add_case( 'FAQP',       30, 'GNUCPU',   16, 4)
# add_case( 'FAQP',      120, 'GNUCPU',  256, 0)
# add_case( 'FAQP',      120, 'GNUCPU',  256, 4)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset,ne,arch,num_nodes,sst_pert):

   # grid = f'ne{ne}pg2_oRRS18to6v3'
   grid = f'ne{ne}pg2_ne{ne}pg2'
   case_list = ['E3SM','2024-AQP-CESS-00',compset,arch,grid,f'NN_{num_nodes}',f'SSTP_{sst_pert}K']
   
   case='.'.join(case_list)

   # print(case); exit()
   #------------------------------------------------------------------------------------------------
   # if ne== 30: gcm_dt = 20.00*60
   # if ne== 45: gcm_dt = 15.00*60
   # if ne== 60: gcm_dt = 10.00*60
   # if ne== 90: gcm_dt =  7.50*60
   # if ne==120: gcm_dt =  5.00*60
   # if ne==180: gcm_dt =  3.75*60
   # if ne==240: gcm_dt =  2.50*60
   if ne== 30: gcm_dt = 16*60
   if ne== 45: gcm_dt = 12*60
   if ne== 60: gcm_dt =  8*60
   if ne== 90: gcm_dt =  6*60
   if ne==120: gcm_dt =  4*60
   if ne==180: gcm_dt =  3*60
   if ne==240: gcm_dt =  2*60
   
   #------------------------------------------------------------------------------------------------
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   atm_ntasks = max_mpi_per_node*num_nodes
   if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'
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
      if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
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
      write_atm_nl_opts(compset,ne,gcm_dt)
      #-------------------------------------------------------
      # update nlev
      if compset=='FAQP'     : 
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 80 -rad  rrtmgp \" ')
      if compset=='FAQP-MMF1': 
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 72 \" ')
      #-------------------------------------------------------
      # cpp_opt = ''
      # cpp_opt += f' -DAQP_CESS -DAQP_CESS_PERTURBATION={sst_pert}'
      # if cpp_opt != '' :
      #    cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      #    cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      #    run_cmd(cmd)
      #-------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
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
      write_atm_nl_opts(compset,ne,gcm_dt)
      #-------------------------------------------------------
      # # Modified SST file
      # if sst_pert==0:
      #    DIN_LOC_ROOT = '/global/cfs/cdirs/e3sm/inputdata'
      #    # DIN_LOC_ROOT = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'
      #    sst_file_path = f'{DIN_LOC_ROOT}/ocn/docn7/SSTDATA/'
      #    sst_file_name = 'sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821.nc'
      # else:
      #    sst_file_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch'
      #    # sst_file_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
      #    sst_file_name = f'sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821.SSTPERT_{sst_pert}K.nc'
      # os.system(f'./xmlchange --file env_run.xml SSTICE_DATA_FILENAME={sst_file_path}/{sst_file_name}')
      #-------------------------------------------------------
      nfile = 'user_nl_docn'
      file = open(nfile,'w')
      file.write(f' aqua_sst_global_pert = {sst_pert} \n')
      file.close()
      #-------------------------------------------------------
      if gcm_dt is not None: 
         ncpl = int( 86400 / gcm_dt )
         run_cmd(f'./xmlchange ATM_NCPL={ncpl}')
      #-------------------------------------------------------
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      # if 'resub' in globals() and not continue_run: run_cmd(f'./xmlchange RESUBMIT={resub}')
      # if 'resub' in globals() and reset_resub: run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'resub' in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      #-------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./xmlchange --file env_run.xml EPS_AGRID=1e-10' )
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
def write_atm_nl_opts(compset,ne,gcm_dt):
   nfile = 'user_nl_eam'
   file = open(nfile,'w')
   file.write(' nhtfrq = 0,-1,-1 \n')
   file.write(' mfilt  = 1,24,24 \n')
   file.write('\n')
   file.write(" fincl1 = 'Z3','CLOUD','CLDLIQ','CLDICE'\n")
   file.write(" fincl2 = 'PS','PSL','TS'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FLDS','FLNS'")               # sfc LW
   file.write(          ",'FSDS','FSNS'")               # sfc SW
   file.write(          ",'FLDSC','FLNSC'")             # sfc LW clearsky
   file.write(          ",'FSDSC','FSNSC'")             # sfc SW clearsky
   file.write(          ",'FLUTOA','FLNTOA'")           # toa LW
   file.write(          ",'FSUTOA','FSNTOA'")           # toa SW
   file.write(          ",'FLUTOAC','FLNTOAC'")         # toa LW clearsky
   file.write(          ",'FSUTOAC','FSNTOAC'")         # toa SW clearsky
   file.write(          ",'FSNT','FLNT'")               # Net TOM rad
   file.write(          ",'FLNS','FSNS'")               # Net Sfc rad
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
   file.write(          ",'CLDTOT','CLDLOW','CLDMED','CLDHGH'")
   file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
   # variables for tracking stuff like hurricanes
   file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model level
   file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(          ",'Z300:I','Z500:I'")
   file.write(          ",'OMEGA850:I','OMEGA500:I'")
   file.write(          ",'U200:I','V200:I'")
   file.write('\n')
   init_root = '/pscratch/sd/w/whannah/HICCUP'
   if compset=='FAQP':
      init_file = f'{init_root}/eam_i_aquaplanet_ne{ne}np4_L80-eam_c20240607.nc'
   if compset=='FAQP-MMF1':
      init_file = f'{init_root}/eam_i_aquaplanet_ne{ne}np4_L72-mmf_c20240607.nc'
   file.write(f" ncdata  = '{init_file}' \n")
   # disable all aerosol rad for all cases
   file.write(f" do_aerosol_rad  = .false. \n")
   factor = 5
   se_tstep = gcm_dt/factor
   file.write(f'se_tstep = {se_tstep} \n')
   file.write(f'hypervis_subcycle_q = {factor} \n')
   file.write(f'dt_tracer_factor = {factor} \n')
   file.write(f'dt_remap_factor = 1 \n')
   file.close()

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(comp_list)):
      # print('-'*80)
      main( comp_list[n], \
            ne_list[n], \
            arch_list[n], \
            node_list[n], \
            pert_list[n], \
           )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

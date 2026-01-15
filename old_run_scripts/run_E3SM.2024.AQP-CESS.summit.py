#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run,reset_resub,st_archive = False,False,False,False,False,False,False,False

acct = 'atm146'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC5' # whannah/2024-aqua-res-ensemble

# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3' # master @ 2024-06-27
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3' # master @ 2024-06-17
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3' # master @ 2024-06-03

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True
### reset_resub  = True

# queue = 'regular' # batch / debug

disable_bfb = True

debug_mode = False

spinup_mode = False
alt_test = False; test_num = 7

# if spinup_mode:
#    stop_opt,stop_n,resub,walltime = 'ndays',1,1,'0:30'
# else:
#    # stop_opt,stop_n,resub,walltime = 'ndays',1,1,'0:30' 
#    # stop_opt,stop_n,resub,walltime = 'ndays',5,1,'2:00'
#    stop_opt,stop_n,resub,walltime = 'ndays',30,10-1,'2:00'

# stop_opt,stop_n,resub,walltime = 'ndays',20,int(800/20)-1,'6:00'
# stop_opt,stop_n,resub,walltime = 'ndays',20,int(800/20)-1,'2:00'

# walltime = '6:00'

#---------------------------------------------------------------------------------------------------
comp_list = []
arch_list = []
node_list = []
pert_list = []
ne_list = []
alt_ncpl_list = []
def add_case(comp,ne,arch,pert,node=None,alt_ncpl=None):
   comp_list.append(comp)
   arch_list.append(arch)
   # node_list.append(node)
   pert_list.append(pert)
   ne_list.append(ne)
   if ne== 30: nnode =   32
   if ne== 45: nnode =   64
   if ne== 60: nnode =  128
   if ne== 90: nnode =  256
   if ne==120: nnode =  512
   if ne==180: nnode = 1024
   if ne==240: nnode = 1024
   node_list.append(nnode)
   alt_ncpl_list.append(alt_ncpl)
   
   
#---------------------------------------------------------------------------------------------------

alt_init_file = None



# add_case( 'FAQP',       30, 'GNUCPU', 0)
# add_case( 'FAQP',       45, 'GNUCPU', 0)
# add_case( 'FAQP',       60, 'GNUCPU', 0)
# add_case( 'FAQP',       90, 'GNUCPU', 0)
# add_case( 'FAQP',      120, 'GNUCPU', 0)

# add_case( 'FAQP',       30, 'GNUCPU', 4)
# add_case( 'FAQP',       45, 'GNUCPU', 4)
# add_case( 'FAQP',       60, 'GNUCPU', 4)
# add_case( 'FAQP',       90, 'GNUCPU', 4)
# add_case( 'FAQP',      120, 'GNUCPU', 4)

alt_ncpl_tmp = int((24*60*60)/(20*60)) # 72
# add_case( 'FAQP',       30, 'GNUCPU', 0, alt_ncpl=alt_ncpl_tmp)
# add_case( 'FAQP',       45, 'GNUCPU', 0, alt_ncpl=alt_ncpl_tmp)
add_case( 'FAQP',       60, 'GNUCPU', 0, alt_ncpl=alt_ncpl_tmp)
add_case( 'FAQP',       90, 'GNUCPU', 0, alt_ncpl=alt_ncpl_tmp)
add_case( 'FAQP',      120, 'GNUCPU', 0, alt_ncpl=alt_ncpl_tmp)

# add_case( 'FAQP',       30, 'GNUCPU', 4, alt_ncpl=alt_ncpl_tmp)
# add_case( 'FAQP',       45, 'GNUCPU', 4, alt_ncpl=alt_ncpl_tmp)
add_case( 'FAQP',       60, 'GNUCPU', 4, alt_ncpl=alt_ncpl_tmp)
add_case( 'FAQP',       90, 'GNUCPU', 4, alt_ncpl=alt_ncpl_tmp)
add_case( 'FAQP',      120, 'GNUCPU', 4, alt_ncpl=alt_ncpl_tmp)

# add_case( 'FAQP-MMF1',  30, 'GNUGPU', 0)
# add_case( 'FAQP-MMF1',  45, 'GNUGPU', 0)
# add_case( 'FAQP-MMF1',  60, 'GNUGPU', 0)
# add_case( 'FAQP-MMF1',  90, 'GNUGPU', 0)
# add_case( 'FAQP-MMF1', 120, 'GNUGPU', 0)

# add_case( 'FAQP-MMF1',  30, 'GNUGPU', 4)
# add_case( 'FAQP-MMF1',  45, 'GNUGPU', 4)
# add_case( 'FAQP-MMF1',  60, 'GNUGPU', 4)
# add_case( 'FAQP-MMF1',  90, 'GNUGPU', 4)
# add_case( 'FAQP-MMF1', 120, 'GNUGPU', 4)


''' unfinished cases:
E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne60pg2_ne60pg2.NN_128.SSTP_0K
E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne90pg2_ne90pg2.NN_256.SSTP_0K
E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne90pg2_ne90pg2.NN_256.SSTP_4K
x E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne120pg2_ne120pg2.NN_512.SSTP_0K
E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne120pg2_ne120pg2.NN_512.SSTP_4K

E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne45pg2_ne45pg2.NN_64.SSTP_0K
E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne45pg2_ne45pg2.NN_64.SSTP_4K
x E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne60pg2_ne60pg2.NN_128.SSTP_0K
x E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne90pg2_ne90pg2.NN_256.SSTP_0K
E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne90pg2_ne90pg2.NN_256.SSTP_4K <<< still finishing 400 days
x E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne120pg2_ne120pg2.NN_512.SSTP_0K
E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne120pg2_ne120pg2.NN_512.SSTP_4K
'''


# scratch = '/gpfs/alpine2/atm146/proj-shared/hannah6/e3sm_scratch'
# add_case( 'FAQP-MMF1', 120, 'GNUGPU',  512, 4); spinup_case = 'E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne120pg2_ne120pg2.NN_512.SSTP_4K.SPINUP.GDT_15'; adj_init_file = f'{scratch}/{spinup_case}/run/{spinup_case}.eam.i.'


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset,ne,arch,num_nodes,sst_pert,alt_ncpl):

   if 'F2010' in compset: grid = f'ne{ne}pg2_oECv3'
   if 'FAQP'  in compset: grid = f'ne{ne}pg2_ne{ne}pg2'
   case_list = ['E3SM','2024-AQP-CESS-00',compset,arch,grid,f'NN_{num_nodes}',f'SSTP_{sst_pert}K']

   if alt_ncpl is not None: case_list.append(f'ALT-NCPL_{alt_ncpl}')

   case = '.'.join(case_list)

   if alt_test: case = case.replace('2024-AQP-CESS-00',f'2024-AQP-CESS-00-TEST{test_num}')

   if debug_mode: case = case+'.DEBUG'

   # print(case); exit()
   #------------------------------------------------------------------------------------------------
   if ne== 30: gcm_dt = 20.00*60
   if ne== 45: gcm_dt = 15.00*60
   if ne== 60: gcm_dt = 10.00*60
   if ne== 90: gcm_dt =  7.50*60
   if ne==120: gcm_dt =  5.00*60
   if ne==180: gcm_dt =  3.75*60
   if ne==240: gcm_dt =  2.50*60

   # if ne== 30: gcm_dt = 16*60 # these values are problematic for history files!!!
   # if ne== 45: gcm_dt = 12*60 # these values are problematic for history files!!!
   # if ne== 60: gcm_dt =  8*60 # these values are problematic for history files!!!
   # if ne== 90: gcm_dt =  6*60 # these values are problematic for history files!!!
   # if ne==120: gcm_dt =  4*60 # these values are problematic for history files!!!
   # if ne==180: gcm_dt =  3*60 # these values are problematic for history files!!!
   # if ne==240: gcm_dt =  2*60 # these values are problematic for history files!!!

   # base_tstep = 15*60
   # if ne== 30: gcm_dt = base_tstep * 16/16
   # if ne== 45: gcm_dt = base_tstep * 12/16
   # if ne== 60: gcm_dt = base_tstep *  8/16
   # if ne== 90: gcm_dt = base_tstep *  6/16
   # if ne==120: gcm_dt = base_tstep *  4/16
   # if ne==180: gcm_dt = base_tstep *  3/16
   # if ne==240: gcm_dt = base_tstep *  2/16

   if spinup_mode:
      crm_dt = 2
      gcm_dt = gcm_dt / 4
      # gcm_dt = gcm_dt / 8
      case += f'.SPINUP'
      case += f'.GDT_{int(gcm_dt)}'
      case += f'.CDT_{int(crm_dt)}'
   
   # print(case)
   # exit()

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
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} --walltime {walltime} '
      if arch=='GNUCPU' : cmd += f' -mach summit -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -mach summit -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   # Configure
   if config :
      run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
      run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      write_atm_nl_opts(compset,ne,gcm_dt,alt_init_file,alt_ncpl)
      #-------------------------------------------------------
      # update nlev
      if compset=='FAQP'     : 
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 80 -rad  rrtmgp \" ')
      if compset=='FAQP-MMF1':
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 72 -crm_nz 60 \" ')
      #-------------------------------------------------------
      if spinup_mode and compset=='FAQP-MMF1':
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')
      #-------------------------------------------------------
      # cpp_opt = ''
      # cpp_opt += f' -DAQP_CESS -DAQP_CESS_PERTURBATION={sst_pert}'
      # if cpp_opt != '' :
      #    cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      #    cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      #    run_cmd(cmd)
      #-------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      # run_cmd('./xmlchange PIO_VERSION=1 ')
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   # Build
   if build : 
      if debug_mode : run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   # Write the namelist options and submit the run
   if submit : 
      write_atm_nl_opts(compset,ne,gcm_dt,alt_init_file,alt_ncpl)
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
      if not alt_test:
         nfile = 'user_nl_docn'
         file = open(nfile,'w')
         file.write(f' aqua_sst_global_pert = {sst_pert} \n')
         file.close()
      #-------------------------------------------------------
      if gcm_dt is not None:
         ncpl = int( 86400 / gcm_dt )
         if alt_ncpl is not None: ncpl = alt_ncpl
         run_cmd(f'./xmlchange ATM_NCPL={ncpl}')
         run_cmd(f'./xmlchange ROF_NCPL={ncpl}')
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
      if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
      if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
      #-------------------------------------------------------
      run_cmd('./xmlchange --file env_run.xml EPS_AGRID=1e-10' )
      #-------------------------------------------------------
      # run_cmd('./xmlchange SAVE_TIMING_DIR=/gpfs/alpine2/atm146/proj-shared' )
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
def write_atm_nl_opts(compset,ne,gcm_dt,alt_init_file=None,alt_ncpl=None):
   nfile = 'user_nl_eam'
   file = open(nfile,'w')
   file.write(' empty_htapes = .true. \n')
   file.write(' nhtfrq = -240,-1,-1 \n')
   file.write(' mfilt  = 1,24,24 \n')
   file.write('\n')
   file.write(" fincl1 = 'CLDHGH','CLDICE','CLDLIQ','CLDLOW','CLDMED','CLDTOT','CLOUD'")
   file.write(          ",'DCQ','DTCOND','DTENDTH','DTENDTQ'")
   file.write(          ",'FLDS','FLNS','FLNSC','FLNT','FLNTC','FLUT','FLUTC'")
   # file.write(          ",'FREQI','FREQL','FREQR','FREQS'")
   file.write(          ",'FSDS','FSDSC','FSNS','FSNSC','FSNT','FSNTC'")
   file.write(          ",'FSNTOA','FSNTOAC','FSUTOA','FSUTOAC'")
   file.write(          ",'ICEFRAC','LANDFRAC','LHFLX','LWCF','OCNFRAC','OMEGA','OMEGA500','OMEGAT'")
   file.write(          ",'PBLH','PHIS','PRECC','PRECL','PRECSC','PRECSL','PS','PSL'")
   file.write(          ",'Q','QFLX','QREFHT','TREFHT'")
   file.write(          ",'QRL','QRS','RAINQM','RELHUM','SHFLX','SNOWHICE','SNOWHLND'")
   file.write(          ",'SOLIN','SWCF','T','TAUX','TAUY'")
   file.write(          ",'TGCLDCWP','TGCLDIWP','TGCLDLWP','TH7001000','TMQ'")
   file.write(          ",'TROP_P','TROP_T','TS','TSMN','TSMX','TUH','TUQ','TVH','TVQ'")
   file.write(          ",'U','U10','UU','V','VQ','VT','VU','VV','Z3'")
   file.write(          ",'CLOUD','CLDLIQ','CLDICE'")
   file.write('\n')
   file.write(" fincl2 = 'PS','PSL','TS'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FLDS','FLNS'")               # sfc LW
   file.write(          ",'FSDS','FSNS'")               # sfc SW
   file.write(          ",'FLDSC','FLNSC'")             # sfc LW clearsky
   file.write(          ",'FSDSC','FSNSC'")             # sfc SW clearsky
   # file.write(          ",'FLUTOA','FLNTOA'")           # toa LW
   # file.write(          ",'FSUTOA','FSNTOA'")           # toa SW
   # file.write(          ",'FLUTOAC','FLNTOAC'")         # toa LW clearsky
   # file.write(          ",'FSUTOAC','FSNTOAC'")         # toa SW clearsky
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
   if alt_init_file is None:
      # init_root = '/pscratch/sd/w/whannah/HICCUP'
      init_root = '/gpfs/alpine2/atm146/proj-shared/hannah6/HICCUP'
      init_file = None
      if compset=='FAQP':
         init_file = f'{init_root}/eam_i_aquaplanet_ne{ne}np4_L80-eam_c20240607.nc'
      if compset=='FAQP-MMF1':
         init_file = f'{init_root}/eam_i_aquaplanet_ne{ne}np4_L72-mmf_c20240607.nc'
      if init_file is not None:
         file.write(f" ncdata  = '{init_file}' \n")
   else:
      file.write(f" ncdata  = '{alt_init_file}' \n")
   if 'FAQP' in compset:
      # disable all aerosol rad for all cases
      file.write(f" do_aerosol_rad  = .false. \n")

   factor = 6
   se_tstep = gcm_dt/factor

   # for alt_ncpl mode update the factor to maintain original se_tstep
   if alt_ncpl is not None: 
      gcm_dt_alt = int(86400/alt_ncpl)
      se_tstep = gcm_dt/factor
      factor = int(gcm_dt_alt/se_tstep)
   
   file.write(f'se_tstep = {se_tstep} \n')
   file.write(f'hypervis_subcycle_q = {factor} \n')
   file.write(f'dt_tracer_factor = {factor} \n')
   file.write(f'dt_remap_factor = 1 \n')
   if spinup_mode: file.write('inithist = \'ENDOFRUN\' \n')
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
            alt_ncpl_list[n], \
           )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

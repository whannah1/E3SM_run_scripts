#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
'''
source activate e3sm-unified-lite
nohup python -u run_post.2024.AQP-CESS.nersc.py > aqp-cess-post.out & 
nohup python -u run_post.2024.AQP-CESS.nersc.py > aqp-cess-post.lt_archive_create.out & 
'''
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): print(f'\n{clr.GREEN}{cmd}{clr.END}'); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime
st_archive,lt_archive_create,lt_archive_update,cp_post_to_cfs = False,False,False,False

# acct = 'atm146'
acct = 'm3312'

# st_archive        = True
lt_archive_create = True
# lt_archive_update = True
# cp_post_to_cfs    = True
# delete_data       = True

hpss_root = 'E3SM/2024-AQP-CESS'

#---------------------------------------------------------------------------------------------------
compset_list,msst_list,arch_list = [],[],[]
crm_nx_list, crm_ny_list, crm_dx_list = [],[],[]
mem_list = []
def add_case(compset,mem=None,msst=None,crm_nx=None,crm_ny=1,crm_dx=None):
   compset_list.append(compset); msst_list.append(msst)
   crm_nx_list.append(crm_nx)
   crm_ny_list.append(crm_ny)
   crm_dx_list.append(crm_dx)
   arch_list.append('GNUGPU' if 'MMF' in compset else 'GNUCPU')
   mem_list.append(mem)
#---------------------------------------------------------------------------------------------------
add_case('FRCEROT',     mem='01',msst=300,crm_nx=128,crm_dx=1000) 
add_case('FRCEROT',     mem='01',msst=320,crm_nx=128,crm_dx=1000) # add +20K uniformly
# add_case('FRCEROT-MMF1',mem='01',msst=300,crm_nx=128,crm_dx=1000) 
# add_case('FRCEROT-MMF1',mem='01',msst=320,crm_nx=128,crm_dx=1000) # add +20K uniformly

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset,ne,arch,num_nodes,sst_pert,alt_ncpl):
   
   if 'F2010' in compset: grid = f'ne{ne}pg2_oECv3'
   if 'FAQP'  in compset: grid = f'ne{ne}pg2_ne{ne}pg2'
   case_list = ['E3SM','2024-AQP-CESS-00',compset,arch,grid,f'NN_{num_nodes}',f'SSTP_{sst_pert}K']

   if alt_ncpl is not None: case_list.append(f'ALT-NCPL_{alt_ncpl}')

   case = '.'.join(case_list)
   #------------------------------------------------------------------------------------------------
   # scratch = '/gpfs/alpine2/atm146/proj-shared/hannah6/e3sm_scratch/'
   scratch = '/pscratch/sd/w/whannah/2024-AQP-CESS'
   case_root = f'{scratch}/{case}'
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END} \n')
   #------------------------------------------------------------------------------------------------
   if st_archive:
      os.chdir(f'{case_root}/case_scripts')
      run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      run_cmd('./case.st_archive')
   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      # run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee zstash_create_{case}_{timestamp}.log')
      run_cmd(f'zstash create --hpss={hpss_root}/{case} . 2>&1 | tee zstash_create_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee zstash_update_{case}_{timestamp}.log')
      run_cmd(f'zstash update --hpss={hpss_root}/{case}  2>&1 | tee zstash_update_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   # if cp_post_to_cfs:
   #    # os.umask(511)
   #    dst_root = '/global/cfs/cdirs/m4310/whannah/E3SM/2023-SciDAC-L80'
   #    src_dir = f'{case_root}/post/atm/180x360/ts/monthly/10yr'
   #    dst_dir = f'{dst_root}/{case}'
   #    if not os.path.exists(dst_root): os.mkdir(dst_root)
   #    if not os.path.exists(dst_dir):  os.mkdir(dst_dir)
   #    run_cmd(f'cp {src_dir}/U_* {dst_dir}/')
   #------------------------------------------------------------------------------------------------
   if 'delete_data' not in globals(): delete_data = False
   if delete_data:
      file_list = []
      file_list += glob.glob(f'{case_root}/post/atm/180x360/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/90x180/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/glb/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/archive/*/hist/*.nc')
      file_list += glob.glob(f'{case_root}/archive/rest/*/*.nc')
      file_list += glob.glob(f'{case_root}/run/*.nc')
      if len(file_list)>10:
         print()
         for f in file_list: print(f)
         print()
         exit()
      # if len(file_list)>0: 
      #    print(f'  {clr.RED}deleting {(len(file_list))} files{clr.END}')
      #    for f in file_list:
      #       os.remove(f)
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(compset_list)):
      main( compset_list[n], 
            mem_list[n], 
            msst_list[n], 
            arch_list[n], 
            crm_nx_list[n], 
            crm_ny_list[n], 
            crm_dx_list[n],
          )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

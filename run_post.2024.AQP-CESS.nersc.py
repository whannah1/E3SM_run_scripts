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
# cp_post_to_cfs      = True

hpss_root = 'E3SM/2024-AQP-CESS'

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
add_case( 'FAQP',       30, 'GNUCPU', 0)
add_case( 'FAQP',       45, 'GNUCPU', 0)
add_case( 'FAQP',       60, 'GNUCPU', 0)
add_case( 'FAQP',       90, 'GNUCPU', 0)
add_case( 'FAQP',      120, 'GNUCPU', 0)
add_case( 'FAQP',       30, 'GNUCPU', 4)
add_case( 'FAQP',       45, 'GNUCPU', 4)
add_case( 'FAQP',       60, 'GNUCPU', 4)
add_case( 'FAQP',       90, 'GNUCPU', 4)
add_case( 'FAQP',      120, 'GNUCPU', 4)

add_case( 'FAQP',       30, 'GNUCPU', 0, alt_ncpl=int((24*60*60)/(20*60)))
add_case( 'FAQP',       45, 'GNUCPU', 0, alt_ncpl=int((24*60*60)/(20*60)))
add_case( 'FAQP',       60, 'GNUCPU', 0, alt_ncpl=int((24*60*60)/(20*60)))
add_case( 'FAQP',       90, 'GNUCPU', 0, alt_ncpl=int((24*60*60)/(20*60)))
add_case( 'FAQP',      120, 'GNUCPU', 0, alt_ncpl=int((24*60*60)/(20*60)))
add_case( 'FAQP',       30, 'GNUCPU', 4, alt_ncpl=int((24*60*60)/(20*60)))
add_case( 'FAQP',       45, 'GNUCPU', 4, alt_ncpl=int((24*60*60)/(20*60)))
add_case( 'FAQP',       60, 'GNUCPU', 4, alt_ncpl=int((24*60*60)/(20*60)))
add_case( 'FAQP',       90, 'GNUCPU', 4, alt_ncpl=int((24*60*60)/(20*60)))
add_case( 'FAQP',      120, 'GNUCPU', 4, alt_ncpl=int((24*60*60)/(20*60)))

add_case( 'FAQP-MMF1',  30, 'GNUGPU', 0)
add_case( 'FAQP-MMF1',  45, 'GNUGPU', 0)
add_case( 'FAQP-MMF1',  60, 'GNUGPU', 0)
add_case( 'FAQP-MMF1',  90, 'GNUGPU', 0)
add_case( 'FAQP-MMF1', 120, 'GNUGPU', 0)
add_case( 'FAQP-MMF1',  30, 'GNUGPU', 4)
add_case( 'FAQP-MMF1',  45, 'GNUGPU', 4)
add_case( 'FAQP-MMF1',  60, 'GNUGPU', 4)
add_case( 'FAQP-MMF1',  90, 'GNUGPU', 4)
add_case( 'FAQP-MMF1', 120, 'GNUGPU', 4)

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
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(comp_list)):
      main( comp_list[n], \
            ne_list[n], \
            arch_list[n], \
            node_list[n], \
            pert_list[n], \
            alt_ncpl_list[n], \
           )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

import os, subprocess as sp

case_root = os.getenv('HOME')+'/E3SM/Cases'

case_list_home = os.listdir(case_root)
case_list_cpu  = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/'
case_list_gpu  = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/'

case_list_orphan = []

for c in case_list_home:
  if c not in case_list_cpu \
  and c not in case_list_gpu \
  and 'old' not in c:
    print(f'  {c}')
    case_list_orphan.append(f'{case_root}/{c}')


os.system(f'du -shc '+' '.join(case_list_orphan))
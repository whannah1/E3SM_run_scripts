#!/usr/bin/env python3
import sys,os,glob,subprocess as sp
class tclr: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
case_root = '/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch'
# case = 'SCREAM.2025-PC-01.F2010-SCREAMv1-DYAMOND1.ne256pg2.cfr_1'
case = 'SCREAM.2025-PC-01.F2010-SCREAMv1-DYAMOND1.ne1024pg2'
# case = 'SCREAM.2025-PC-01.F2010-SCREAMv1-DYAMOND1.ne1024pg2.cfr_1'
#---------------------------------------------------------------------------------------------------
'''
alterantively we can use this slurm command:
sacct -j 3074977 -XPno nodelist
'''
#---------------------------------------------------------------------------------------------------
# identify the log files
file_path = f'{case_root}/{case}/run/e3sm.log.*'
file_list = sorted(glob.glob(file_path))
print()
for f in file_list: print(f'  {f}')
print()
#---------------------------------------------------------------------------------------------------
# build list of all nodes used by all jobs
node_list = []
for f in file_list:
  file_ptr = open(f)
  contents = file_ptr.read().split()
  for c in contents:
    if 'frontier' in c:
      node_list.append(c)
#---------------------------------------------------------------------------------------------------
# identify nodes shared across the jobs
print()
bad_node_list = []
unique_nodes = list(set(node_list))
for n in unique_nodes:
  cnt = node_list.count(n)
  clr_tmp = tclr.CYAN
  if cnt==len(file_list):
    clr_tmp = tclr.RED
    bad_node_list.append(n)
  # if cnt>1:
  #   print(f'  {n}   cnt: {clr_tmp}{cnt}{tclr.END}')
#---------------------------------------------------------------------------------------------------
print()
if bad_node_list != []:
  print(f'potential bad nodes with {tclr.RED}{len(file_list)}{tclr.END} failures:')
  for n in bad_node_list:
    print(f'  {n}')
print()
#---------------------------------------------------------------------------------------------------
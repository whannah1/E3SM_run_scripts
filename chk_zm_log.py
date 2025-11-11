import numpy as np

# log_file = '/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne30pg2.NN_8.zm_apply_tend_1/run/e3sm.log.41443993.250806-161342'
# log_file = '/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne30pg2.NN_8.zm_apply_tend_1/run/e3sm.log.41472519.250807-084944'
# log_file = '/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne30pg2.NN_8.zm_apply_tend_1/run/e3sm.log.41473578.250807-093232'
# log_file = '/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne30pg2.NN_8.zm_apply_tend_1/run/e3sm.log.41473946.250807-095639'
# log_file = '/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne4pg2.NN_1.zm_apply_tend_1/run/e3sm.log.41476693.250807-105356'
# log_file = '/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne4pg2.NN_1.zm_apply_tend_1/run/e3sm.log.41480847.250807-121131'

# log_file = '/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne4pg2.NN_1.zm_apply_tend_1.debug/run/e3sm.log.41494383.250808-052258'
log_file = '/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne4pg2.NN_1.zm_apply_tend_1.debug/run/e3sm.log.41495243.250808-064058'

max_ncol = 32

cnt = np.zeros(max_ncol,dtype=int)
with open(log_file, 'r') as file:
  for line in file:
    for n in range(max_ncol):
      if f'({n})' in line and f'act: 1' in line: cnt[n] += 1
print()
for n in range(max_ncol):
  if cnt[n]>0:
    print(f' {n:3d}  {cnt[n]:8d}')
print() 


# for rank in range(20):
#   fcnt= np.zeros(max_ncol,dtype=int)
#   ccnt= np.zeros(max_ncol,dtype=int)
#   with open(log_file, 'r') as file:
#     for line in file:
#       for n in range(max_ncol):
#         if f'{rank:3d}:' in line:
#           k = 60
#           if f'F-DEBUG (           {n+1} ,          {k+1:2d} )' in line: fcnt[n] += 1
#           if f'C-DEBUG ({n},{k})'                               in line: ccnt[n] += 1
#   print()
#   for n in range(max_ncol):
#     print(f' {n:3d}  {fcnt[n]:8d}  {ccnt[n]:8d}')
#   print()

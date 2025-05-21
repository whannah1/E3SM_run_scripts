#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
import os, glob#, numpy as np
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
#---------------------------------------------------------------------------------------------------
case_list = []

case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne30pg2_ne30pg2.NN_32.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne30pg2_ne30pg2.NN_32.SSTP_4K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne45pg2_ne45pg2.NN_64.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne45pg2_ne45pg2.NN_64.SSTP_4K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne60pg2_ne60pg2.NN_128.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne60pg2_ne60pg2.NN_128.SSTP_4K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne90pg2_ne90pg2.NN_256.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne90pg2_ne90pg2.NN_256.SSTP_4K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne120pg2_ne120pg2.NN_512.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP-MMF1.GNUGPU.ne120pg2_ne120pg2.NN_512.SSTP_4K')

case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne30pg2_ne30pg2.NN_32.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne30pg2_ne30pg2.NN_32.SSTP_4K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne45pg2_ne45pg2.NN_64.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne45pg2_ne45pg2.NN_64.SSTP_4K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne60pg2_ne60pg2.NN_128.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne60pg2_ne60pg2.NN_128.SSTP_4K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne90pg2_ne90pg2.NN_256.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne90pg2_ne90pg2.NN_256.SSTP_4K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne120pg2_ne120pg2.NN_512.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne120pg2_ne120pg2.NN_512.SSTP_4K')


case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne30pg2_ne30pg2.NN_32.SSTP_0K.ALT-NCPL_72')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne30pg2_ne30pg2.NN_32.SSTP_4K.ALT-NCPL_72')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne45pg2_ne45pg2.NN_64.SSTP_0K.ALT-NCPL_72')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne45pg2_ne45pg2.NN_64.SSTP_4K.ALT-NCPL_72')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne60pg2_ne60pg2.NN_128.SSTP_0K.ALT-NCPL_72')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne60pg2_ne60pg2.NN_128.SSTP_4K.ALT-NCPL_72')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne90pg2_ne90pg2.NN_256.SSTP_0K.ALT-NCPL_72')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne90pg2_ne90pg2.NN_256.SSTP_4K.ALT-NCPL_72')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne120pg2_ne120pg2.NN_512.SSTP_0K.ALT-NCPL_72')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne120pg2_ne120pg2.NN_512.SSTP_4K.ALT-NCPL_72')


scratch = '/gpfs/alpine2/atm146/proj-shared/hannah6/e3sm_scratch/'

#---------------------------------------------------------------------------------------------------
# num_file_list = np.zeros(len(case_list))
num_file_list = [None]*len(case_list)
for c,case in enumerate(case_list):

  file_path = f'{scratch}/{case}/run/*eam.h1*'
  file_list = sorted(glob.glob(file_path))

  num_file_list[c] = len(file_list)

# max_num_files = max(num_file_list)
max_num_files = 800
min_num_files = min(num_file_list)
#---------------------------------------------------------------------------------------------------
for c,case in enumerate(case_list):
  use_clr_max = True if num_file_list[c]>=max_num_files else False
  use_clr_min = True if num_file_list[c]==min_num_files else False
  msg = f'{case:80} '
  n = num_file_list[c]
  if use_clr_max: msg += f'{clr.GREEN}'
  if use_clr_min: msg += f'{clr.RED}'
  msg += f'{n}'
  msg += f'    {(n/365):5.1f}'
  msg += f'{clr.END}'

  print(msg)

#---------------------------------------------------------------------------------------------------



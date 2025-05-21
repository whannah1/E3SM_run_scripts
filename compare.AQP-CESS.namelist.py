#---------------------------------------------------------------------------------------------------
scratch = '/gpfs/alpine2/atm146/proj-shared/hannah6/e3sm_scratch/'
case_list = []
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne30pg2_ne30pg2.NN_32.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne45pg2_ne45pg2.NN_64.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne60pg2_ne60pg2.NN_128.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne90pg2_ne90pg2.NN_256.SSTP_0K')
case_list.append('E3SM.2024-AQP-CESS-00.FAQP.GNUCPU.ne120pg2_ne120pg2.NN_512.SSTP_0K')
#---------------------------------------------------------------------------------------------------
def get_namelist_file_path(case): 
  global scratch
  return f'{scratch}/{case}/run/atm_in'
#---------------------------------------------------------------------------------------------------
def read_param(atm_in_path,param):
  file = open(atm_in_path,'r')
  for line in file.readlines():
    if param in line:
      line_split = line.split()
      if len(line_split)==3: 
        return line_split[2]
      elif len(line_split)>=4: 
        return ' '.join( line_split[2:] )
      else:
        return None
  raise ValueError(f'ERROR: param not found! ({param})')
#---------------------------------------------------------------------------------------------------
param_list = []
file = open(get_namelist_file_path(case_list[0]),'r')
for line in file.readlines():
  if '=' in line:
    param_list.append(line.split()[0])
#---------------------------------------------------------------------------------------------------
for param in param_list:
  if param in ['ncdata','bnd_topo']: continue
  value_list = []
  for c,case in enumerate(case_list):
    atm_in_path = get_namelist_file_path(case)
    value_list.append(read_param(atm_in_path,param))
  if len(set(value_list))>1: print(f'{param:30}  {value_list}')
#---------------------------------------------------------------------------------------------------
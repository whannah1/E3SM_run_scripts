import os, glob
#-------------------------------------------------------------------------------
home = os.getenv('HOME')
host = None
#---------------------------------------------------------------------------------------------------
natsort_found = False
# import importlib
# natsort_spec = None
# natsort_spec = importlib.util.find_spec("natsort")
# natsort_found = natsort_spec is not None
# if natsort_found: from natsort import natsorted, ns
#---------------------------------------------------------------------------------------------------
# Set up terminal colors
class tclr:
  BLU='\033[94m'
  GRN='\033[92m'
  RED='\033[91m'
  MGN='\033[35m'
  CYN='\033[36m'
  YLW='\033[33m'
  BLD='\033[1m'
  ULN='\033[4m'
  ULNOFF='\033[24m'
  END='\033[0m'
#---------------------------------------------------------------------------------------------------
def get_host(verbose=False):
  """
  Get name of current machine
  """
  try: 
    host = sp.check_output(["dnsdomainname"],universal_newlines=True).strip()
  except:
   host = None
  if host=='chn': host = 'nersc' # reset for perlmutter
  if host is not None:
    if 'nersc' in host : host = None
    if host is None or host=='' : host = os.getenv('NERSC_HOST')
  if host is None or host=='' : host = os.getenv('host')
  if host is None or host=='' : host = os.getenv('HOST')
  opsys = os.getenv('os')
  #-----------------------------------------------------------------------------
  if verbose:
    print('\n'+f'  host : {host}')
    print(     f'  opsys: {opsys}\n')
  #-----------------------------------------------------------------------------
  # Make the final setting of host name
  if opsys=='Darwin'      : host = 'mac'
  if 'perlmutter' in host : host = 'nersc'
  if 'aurora'     in host : host = 'alcf'
  if host=='olcf.ornl.gov': host = 'olcf'   # andes
  if host=='lcrc.anl.gov' : host = 'lcrc'   # chrysalis
  if host=='llnl.gov'     : host = 'llnl'   # Livermore Computing
  return host
#---------------------------------------------------------------------------------------------------
def get_scratch_path_list():
  host = get_host()
  all_path_list = []
  all_path_list.append(f'{home}/E3SM/scratch')
  all_path_list.append(f'{home}/E3SM/scratch2')
  all_path_list.append(f'{home}/E3SM/scratch_v3')
  all_path_list.append(f'{home}/E3SM/scratch_pm')
  all_path_list.append(f'{home}/E3SM/scratch_pm-cpu')
  all_path_list.append(f'{home}/E3SM/scratch_pm-gpu')
  all_path_list.append('/pscratch/sd/w/whannah/E3SMv3_dev')
  all_path_list.append(f'{home}/E3SM/scratch-llnl1')
  all_path_list.append(f'{home}/E3SM/scratch-llnl2')
  all_path_list.append(f'{home}/SCREAM/scratch_pm-cpu')
  all_path_list.append(f'{home}/SCREAM/scratch_pm-gpu')
  all_path_list.append(f'{home}/SCREAM/scratch-summit')
  #-----------------------------------------------------------------------------
  # only retain paths that exist
  scratch_path_list = []
  for scratch_path in all_path_list:
    if os.path.exists(scratch_path):
      scratch_path_list.append(scratch_path)
  #-----------------------------------------------------------------------------
  # make sure paths don't end with "/"
  for i,scratch_path in enumerate(scratch_path_list) :
    if scratch_path[-1]=='/':
      scratch_path_list[i] = scratch_path_list[i][0:-1]
  #-----------------------------------------------------------------------------
  return scratch_path_list
#---------------------------------------------------------------------------------------------------

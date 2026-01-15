#!/usr/bin/env python3
import os
class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'

execute = True # if False then just list files

src_top_dir = os.getenv('HOME')+'/SCREAM/scream'
dst_top_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC2'

scream_copy_dir = 'components/eam/src/physics/crm/scream'

#-------------------------------------------------------------------------------
# set list of single files or folders to copy
#-------------------------------------------------------------------------------
path_list = []

# path_list.append('components/cmake/build_scream.cmake')

path_list.append('components/scream/.clang-format')
path_list.append('components/scream/CMakeLists.txt')
path_list.append('components/scream/src/CMakeLists.txt')
path_list.append('components/scream/src/scream_config.h.in')
path_list.append('components/scream/src/physics/CMakeLists.txt')

path_list.append('components/scream/cmake')
path_list.append('components/scream/cmake/machine-files')
path_list.append('components/scream/cmake/tpls')
path_list.append('components/scream/src/physics/p3')
path_list.append('components/scream/src/physics/shoc')
path_list.append('components/scream/src/physics/share')
path_list.append('components/scream/src/share')
path_list.append('components/scream/src/share/util')
path_list.append('components/scream/data')

#-------------------------------------------------------------------------------
# first make sure destination branch has scream folder
#-------------------------------------------------------------------------------
if not os.path.exists(f'{dst_top_dir}/{scream_copy_dir}'): 
  os.makedirs(f'{dst_top_dir}/{scream_copy_dir}')

#-------------------------------------------------------------------------------
# Compile full list of files to copy
#-------------------------------------------------------------------------------
src_file_list = []
dst_file_list = []
for p in path_list:
  
  # if just a single file then do a simple copy
  # create destination subfolder if it doesn't exist
  if os.path.isfile(f'{src_top_dir}/{p}'):
    tmp_path = p.replace('components/scream',scream_copy_dir)
    tmp_dst_path = f'{dst_top_dir}/{tmp_path}'
    tmp_dir = os.path.split(tmp_dst_path)[0]
    if not os.path.exists(tmp_dir): os.makedirs(tmp_dir)
    src_file_list.append(f'{src_top_dir}/{p}')
    dst_file_list.append(f'{dst_top_dir}/{tmp_path}')

  # if path is a folder then copy each file, excluding subfolders
  if os.path.isdir(f'{src_top_dir}/{p}'):
    tmp_path = p.replace('components/scream',scream_copy_dir)
    src_dir = f'{src_top_dir}/{p}'
    dst_dir = f'{dst_top_dir}/{tmp_path}'
    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
    for f in os.listdir(src_dir):
      if os.path.isfile(f'{src_dir}/{f}'):
        src_file_list.append(f'{src_dir}/{f}')
        dst_file_list.append(dst_dir)
#-------------------------------------------------------------------------------
# Copy the files
#-------------------------------------------------------------------------------
max_src_file_len = 0
for f in range(len(src_file_list)):
  if len(src_file_list[f])>max_src_file_len: max_src_file_len = len(src_file_list[f])

for f in range(len(src_file_list)):
  cmd = f'cp {src_file_list[f]:{max_src_file_len+1}} {dst_file_list[f]}/'
  
  if execute:
    print('  '+tcolor.GREEN + cmd + tcolor.ENDC)
    os.system(cmd)
  else:
    print('  '+tcolor.GREEN + src_file_list[f] + tcolor.ENDC)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


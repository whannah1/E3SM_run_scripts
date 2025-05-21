#!/usr/bin/env python
import os
import subprocess as sp
import glob

var = 'H2OSOI'

case = 'E3SM_PG-LAND-SPINUP_ne120pg2_FC5AV1C-H01A_00'

sdir = f'/global/cscratch1/sd/whannah/acme_scratch/cori-knl/{case}/run/'

files = glob.glob(sdir+'*clm2.h0*')


print(f'directory: {sdir} ')
for fi in files :
	if var not in fi :
		fo = fi.replace('.nc',f'.{var}.nc')
		# fi_nodir = fi.replace(sdir,'')
		# fo_nodir = fo.replace(sdir,'')
		# print(f'  {fi_nodir}     {fo_nodir} ')
		print(f'  {fo} ')
		cmd = f'ncks -v {var},area --ovr {fi}  {fo} '
		# print(cmd)
		os.system(cmd)
		exit()
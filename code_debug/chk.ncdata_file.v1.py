
import os, ngl, subprocess as sp, numpy as np, xarray as xr, copy, string
import hapy_common as hc

files,res = [],[]
data_root = '/global/cscratch1/sd/whannah/HICCUP/data'
# files.append(f'{data_root}/cami_rcemip_ne4np4_L60_c20210817.nc')   ; res.append('ne4pg2')
# files.append(f'{data_root}/cami_rcemip_ne30np4_L60_c20210817.nc')  ; res.append('ne30pg2')
# files.append(f'{data_root}/cami_rcemip_ne45np4_L60_c20210817.nc')  ; res.append('ne45pg2')
# files.append(f'{data_root}/cami_rcemip_ne120np4_L60_c20210817.nc') ; res.append('ne120pg2')


files.append(f'{data_root}/cami_rcemip_ne30np4_L60_c20210817.nc')  ; res.append('ne30pg2 L60')
data_root = '/project/projectdirs/e3sm/inputdata/atm/cam/inic/homme'
files.append(f'{data_root}/cami_rcemip_ne30np4_L72_c190919.nc')    ; res.append('ne30pg2 L72')

var,min_val = [],[]
# var.append('Q'); min_val.append(0)
var.append('T'); min_val.append(150)
var.append('pint'); min_val.append(1.005183574463)
# var.append('pmid'); min_val.append(1.005183574463)

print()
for f,file in enumerate(files):
  ds = xr.open_dataset(file)
  print(f'{res[f]:8}')
  for v in range(len(var)):

    if   var[v]=='pint':
      da = ds['hyai'] * ds['P0'] + ds['hybi'] * ds['PS']
    elif var[v]=='pmid':
      da = ds['hyam'] * ds['P0'] + ds['hybm'] * ds['PS']
    else:
      da = ds[var[v]]

    # hc.print_stat(da,name=f'{res[f]:8}   {var[v]:4}',compact=True,indent='  ')
    hc.print_stat(da,name=f'{var[v]:4}',compact=True,indent='  ')

    # neg_count = xr.where(da>min_val[v],0,1).sum().values
    # nan_count = ds[da].isnull().sum().values

    # print(hc.tcolor.MAGENTA+f'  {res[f]:8} - {var[v]:3} # values <  {min_val[v]:2} : {neg_count}'+hc.tcolor.ENDC)
    # print(f'  {res[f]:8} - {var[v]:3} # nan       {""        :2} : {neg_count}')

    print()

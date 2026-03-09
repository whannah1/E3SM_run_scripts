
https://e3sm.atlassian.net/wiki/spaces/EAMXX/pages/6001950744/QBO+Model+Top+Sensitivity


# Vertical Grid Files

```shell
~/E3SM_grid_support/code_vert_grid/2026_EAMv3_QBO_model_top_sensitivity.py
```

```shell
~/E3SM/vert_grid_files/E3SMv3_L80-truncated_20km.nc  nlev_mid = 55
~/E3SM/vert_grid_files/E3SMv3_L80-truncated_25km.nc  nlev_mid = 63
~/E3SM/vert_grid_files/E3SMv3_L80-truncated_30km.nc  nlev_mid = 67
~/E3SM/vert_grid_files/E3SMv3_L80-truncated_35km.nc  nlev_mid = 70
~/E3SM/vert_grid_files/E3SMv3_L80-truncated_40km.nc  nlev_mid = 72
~/E3SM/vert_grid_files/E3SMv3_L80-truncated_45km.nc  nlev_mid = 74
~/E3SM/vert_grid_files/E3SMv3_L80-truncated_50km.nc  nlev_mid = 76
~/E3SM/vert_grid_files/E3SMv3_L80-truncated_55km.nc  nlev_mid = 78
```


# Initial Condition Files

```shell

IC_INPUT_ROOT=/global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme
IC_OUTPUT_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/truncated_L80_initial_conditions
IC_INPUT_FILE=${IC_INPUT_ROOT}/eami_mam4_Linoz_ne30np4_L80_c20231010.nc
VERT_ROOT=~/E3SM/vert_grid_files
VERT_PRFX=E3SMv3_L80-truncated
IC_PRFX=eami_mam4_Linoz_ne30np4_L80_c20231010.truncated_top
TOPKM=20; ncremap --vrt_fl=${VERT_ROOT}/${VERT_PRFX}_${TOPKM}km.nc --ps_nm=PS --in_fl=${IC_INPUT_FILE} --out_fl=${IC_OUTPUT_ROOT}/${IC_PRFX}_${TOPKM}km.nc
TOPKM=25; ncremap --vrt_fl=${VERT_ROOT}/${VERT_PRFX}_${TOPKM}km.nc --ps_nm=PS --in_fl=${IC_INPUT_FILE} --out_fl=${IC_OUTPUT_ROOT}/${IC_PRFX}_${TOPKM}km.nc
TOPKM=30; ncremap --vrt_fl=${VERT_ROOT}/${VERT_PRFX}_${TOPKM}km.nc --ps_nm=PS --in_fl=${IC_INPUT_FILE} --out_fl=${IC_OUTPUT_ROOT}/${IC_PRFX}_${TOPKM}km.nc
TOPKM=35; ncremap --vrt_fl=${VERT_ROOT}/${VERT_PRFX}_${TOPKM}km.nc --ps_nm=PS --in_fl=${IC_INPUT_FILE} --out_fl=${IC_OUTPUT_ROOT}/${IC_PRFX}_${TOPKM}km.nc
TOPKM=40; ncremap --vrt_fl=${VERT_ROOT}/${VERT_PRFX}_${TOPKM}km.nc --ps_nm=PS --in_fl=${IC_INPUT_FILE} --out_fl=${IC_OUTPUT_ROOT}/${IC_PRFX}_${TOPKM}km.nc
TOPKM=45; ncremap --vrt_fl=${VERT_ROOT}/${VERT_PRFX}_${TOPKM}km.nc --ps_nm=PS --in_fl=${IC_INPUT_FILE} --out_fl=${IC_OUTPUT_ROOT}/${IC_PRFX}_${TOPKM}km.nc
TOPKM=50; ncremap --vrt_fl=${VERT_ROOT}/${VERT_PRFX}_${TOPKM}km.nc --ps_nm=PS --in_fl=${IC_INPUT_FILE} --out_fl=${IC_OUTPUT_ROOT}/${IC_PRFX}_${TOPKM}km.nc
TOPKM=55; ncremap --vrt_fl=${VERT_ROOT}/${VERT_PRFX}_${TOPKM}km.nc --ps_nm=PS --in_fl=${IC_INPUT_FILE} --out_fl=${IC_OUTPUT_ROOT}/${IC_PRFX}_${TOPKM}km.nc
```

# Sponge Layer Settings

```shell
# precise pressure values:
z_top = 60 km  =>  tom_sponge_start =   1.00 mb
z_top = 55 km  =>  tom_sponge_start =   3.44 mb
z_top = 50 km  =>  tom_sponge_start =   6.34 mb
z_top = 45 km  =>  tom_sponge_start =  13.30 mb
z_top = 40 km  =>  tom_sponge_start =  25.58 mb
z_top = 35 km  =>  tom_sponge_start =  46.10 mb
z_top = 30 km  =>  tom_sponge_start = 104.66 mb
```

```shell
# round numbers:
z_top = 60 km  =>  tom_sponge_start =   1.0 mb
z_top = 55 km  =>  tom_sponge_start =   3.5 mb
z_top = 50 km  =>  tom_sponge_start =   6.0 mb
z_top = 45 km  =>  tom_sponge_start =  13.0 mb
z_top = 40 km  =>  tom_sponge_start =  25.5 mb
z_top = 35 km  =>  tom_sponge_start =  46.0 mb
z_top = 30 km  =>  tom_sponge_start = 104.5 mb
```
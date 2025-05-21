#!/bin/bash -fe

DATA_ROOT=/p/lustre1/hannah6/2024-nimbus-iraq-data

# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-128x3-pg2_esmfaave.20240618.nc   ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-128x3-pg2_esmfbilin.20240618.nc  ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-128x3-pg2_ncoaave.20240618.nc    ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-128x3-pg2_ncoidw.20240618.nc     ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-128x3-pg2_traave.20240618.nc     ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-128x3-pg2_trbilin.20240618.nc    ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-128x3-pg2_trfv2.20240618.nc      ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-128x3-pg2_trintbilin.20240618.nc ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-128x3_traave.20240618.nc         ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-32x3-pg2_esmfaave.20240618.nc    ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-32x3-pg2_esmfbilin.20240618.nc   ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-32x3-pg2_ncoaave.20240618.nc     ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-32x3-pg2_ncoidw.20240618.nc      ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-32x3-pg2_traave.20240618.nc      ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-32x3-pg2_trbilin.20240618.nc     ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-32x3-pg2_trfv2.20240618.nc       ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-32x3-pg2_trintbilin.20240618.nc  ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-32x3_traave.20240618.nc          ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-64x3-pg2_esmfaave.20240618.nc    ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-64x3-pg2_esmfbilin.20240618.nc   ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-64x3-pg2_ncoaave.20240618.nc     ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-64x3-pg2_ncoidw.20240618.nc      ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-64x3-pg2_traave.20240618.nc      ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-64x3-pg2_trbilin.20240618.nc     ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-64x3-pg2_trfv2.20240618.nc       ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-64x3-pg2_trintbilin.20240618.nc  ; ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_ICOS10_to_2024-nimbus-iraq-64x3_traave.20240618.nc          ; ncks -O --fl_fmt=64bit_data $FILE $FILE

# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-128x3-pg2_to_ICOS10_esmfaave.20240618.nc ;    ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-128x3-pg2_to_ICOS10_esmfbilin.20240618.nc ;   ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-128x3-pg2_to_ICOS10_ncoaave.20240618.nc ;     ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-128x3-pg2_to_ICOS10_ncoidw.20240618.nc ;      ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-128x3-pg2_to_ICOS10_traave.20240618.nc ;      ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-128x3-pg2_to_ICOS10_trbilin.20240618.nc ;     ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-128x3-pg2_to_ICOS10_trfv2.20240618.nc ;       ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-128x3-pg2_to_ICOS10_trintbilin.20240618.nc ;  ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-128x3_to_r0125_traave.20240701.nc ;           ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-32x3-pg2_to_ICOS10_esmfaave.20240618.nc ;     ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-32x3-pg2_to_ICOS10_esmfbilin.20240618.nc ;    ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-32x3-pg2_to_ICOS10_ncoaave.20240618.nc ;      ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-32x3-pg2_to_ICOS10_ncoidw.20240618.nc ;       ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-32x3-pg2_to_ICOS10_traave.20240618.nc ;       ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-32x3-pg2_to_ICOS10_trbilin.20240618.nc ;      ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-32x3-pg2_to_ICOS10_trfv2.20240618.nc ;        ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-32x3-pg2_to_ICOS10_trintbilin.20240618.nc ;   ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-32x3_to_r0125_traave.20240701.nc ;            ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-64x3-pg2_to_ICOS10_esmfaave.20240618.nc ;     ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-64x3-pg2_to_ICOS10_esmfbilin.20240618.nc ;    ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-64x3-pg2_to_ICOS10_ncoaave.20240618.nc ;      ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-64x3-pg2_to_ICOS10_ncoidw.20240618.nc ;       ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-64x3-pg2_to_ICOS10_traave.20240618.nc ;       ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-64x3-pg2_to_ICOS10_trbilin.20240618.nc ;      ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-64x3-pg2_to_ICOS10_trfv2.20240618.nc ;        ncks -O --fl_fmt=64bit_data $FILE $FILE
# FILE=${DATA_ROOT}/files_map/map_2024-nimbus-iraq-64x3-pg2_to_ICOS10_trintbilin.20240618.nc ;   ncks -O --fl_fmt=64bit_data $FILE $FILE

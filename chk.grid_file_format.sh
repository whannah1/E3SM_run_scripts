#!/bin/bash
# Check netCDF format of all E3SM input data files using ncdump -k

DIN_LOC_ROOT=/lcrc/group/acme/public_html/inputdata

FILES=(
  # Domain files
  "$DIN_LOC_ROOT/share/domains/domain.lnd.ne32pg2_RRSwISC6to18E3r5.20251006.nc"
  "$DIN_LOC_ROOT/share/domains/domain.ocn.ne32pg2_RRSwISC6to18E3r5.20251006.nc"
  "$DIN_LOC_ROOT/share/domains/domain.lnd.ne64pg2_RRSwISC6to18E3r5.20251006.nc"
  "$DIN_LOC_ROOT/share/domains/domain.ocn.ne64pg2_RRSwISC6to18E3r5.20251006.nc"
  "$DIN_LOC_ROOT/share/domains/domain.lnd.ne128pg2_RRSwISC6to18E3r5.20251006.nc"
  "$DIN_LOC_ROOT/share/domains/domain.ocn.ne128pg2_RRSwISC6to18E3r5.20251006.nc"

  # Gridmaps - ne32pg2
  "$DIN_LOC_ROOT/cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_traave.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne32pg2_traave.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne32pg2/map_ne32pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_traave.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trfv2.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne32pg2/map_ne32pg2_to_r025_trbilin.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne32pg2/map_r025_to_ne32pg2_traave.20251006.nc"

  # Gridmaps - ne64pg2
  "$DIN_LOC_ROOT/cpl/gridmaps/ne64pg2/map_ne64pg2_to_RRSwISC6to18E3r5_traave.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne64pg2/map_ne64pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne64pg2_traave.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne64pg2/map_ne64pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne64pg2/map_ne64pg2_to_r025_traave.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne64pg2/map_ne64pg2_to_r025_trfv2.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne64pg2/map_ne64pg2_to_r025_trbilin.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne64pg2/map_r025_to_ne64pg2_traave.20251006.nc"

  # Gridmaps - ne128pg2
  "$DIN_LOC_ROOT/cpl/gridmaps/ne128pg2/map_ne128pg2_to_RRSwISC6to18E3r5_traave.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne128pg2/map_ne128pg2_to_RRSwISC6to18E3r5_trbilin.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/RRSwISC6to18E3r5/map_RRSwISC6to18E3r5_to_ne128pg2_traave.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne128pg2/map_ne128pg2_to_RRSwISC6to18E3r5_trfv2.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne128pg2/map_ne128pg2_to_r025_traave.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne128pg2/map_ne128pg2_to_r025_trfv2.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne128pg2/map_ne128pg2_to_r025_trbilin.20251006.nc"
  "$DIN_LOC_ROOT/cpl/gridmaps/ne128pg2/map_r025_to_ne128pg2_traave.20251006.nc"

  # EAM initial conditions
  "$DIN_LOC_ROOT/atm/cam/inic/homme/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne32np4.20251001.nc"
  "$DIN_LOC_ROOT/atm/cam/inic/homme/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne64np4.20251001.nc"
  "$DIN_LOC_ROOT/atm/cam/inic/homme/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne128np4.20251001.nc"

  # SCREAM remapping maps
  "$DIN_LOC_ROOT/atm/scream/maps/map_ne30pg2_to_ne32pg2_traave.20251124.nc"
  "$DIN_LOC_ROOT/atm/scream/maps/map_ne30pg2_to_ne64pg2_traave.20251124.nc"
  "$DIN_LOC_ROOT/atm/scream/maps/map_ne30pg2_to_ne128pg2_traave.20251124.nc"

  # SCREAM initial conditions
  "$DIN_LOC_ROOT/atm/scream/init/eamxxi_ne32np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20251001.nc"
  "$DIN_LOC_ROOT/atm/scream/init/eamxxi_ne64np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20251001.nc"
  "$DIN_LOC_ROOT/atm/scream/init/eamxxi_ne128np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20251001.nc"

  # Topography
  "$DIN_LOC_ROOT/atm/cam/topo/USGS-topo_ne32np4_smoothedx6t_20250904_no-oro-shape.nc"
  "$DIN_LOC_ROOT/atm/cam/topo/USGS-topo_ne64np4_smoothedx6t_20250904_no-oro-shape.nc"
  "$DIN_LOC_ROOT/atm/cam/topo/USGS-topo_ne128np4_smoothedx6t_20250904_no-oro-shape.nc"

  # ELM initial conditions
  "$DIN_LOC_ROOT/lnd/clm2/initdata_map/ne32pg2.elm.r.2013-08-01-00000.64bit.nc"
  "$DIN_LOC_ROOT/lnd/clm2/initdata_map/ne64pg2.elm.r.2013-08-01-00000.64bit.nc"
  "$DIN_LOC_ROOT/lnd/clm2/initdata_map/ne128pg2.elm.r.2013-08-01-00000.64bit.nc"

  # ELM surface data
  "$DIN_LOC_ROOT/lnd/clm2/surfdata_map/surfdata_ne32pg2_simyr2010_c260116.nc"
  "$DIN_LOC_ROOT/lnd/clm2/surfdata_map/surfdata_ne64pg2_simyr2010_c260116.nc"
  "$DIN_LOC_ROOT/lnd/clm2/surfdata_map/surfdata_ne128pg2_simyr2010_c260116.nc"
)

# Counters
PASS=0
FAIL=0
MISSING=0

echo "========================================"
echo "netCDF format check (ncdump -k)"
echo "========================================"
printf "%-12s  %s\n" "FORMAT" "FILE"
echo "----------------------------------------"

for f in "${FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    printf "%-12s  %s\n" "MISSING" "$f"
    (( MISSING++ ))
  else
    fmt=$(ncdump -k "$f" 2>&1)
    if [[ $? -ne 0 ]]; then
      printf "%-12s  %s\n" "ERROR" "$f"
      (( FAIL++ ))
    else
      printf "%-12s  %s\n" "$fmt" "$f"
      (( PASS++ ))
    fi
  fi
done

echo "========================================"
echo "Summary: $PASS ok | $FAIL errors | $MISSING missing"
echo "========================================"
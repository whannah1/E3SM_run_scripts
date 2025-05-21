; Create a topography file for aqua planet experiments
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
; load "$NCARG_ROOT/custom_functions.ncl"
begin 
    
    ; idir = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/topo/"
    idir = "~/ACME/aqua_setup/data/"
    odir = "~/ACME/aqua_setup/data/"

    res = "ne16"

    ; ifile = idir+"cami-mam3_0000-01-01_1.9x2.5_L30_c090306.nc"    ; fv 1.9 x 2.5
    ; ifile = idir+"USGS-gtopo30_1.9x2.5_remap_c050602.nc"
    if res.eq."ne16" then ifile = idir+"USGS-gtopo30_ne16np4_16xconsistentSGH.c20160612.nc" end if
    if res.eq."ne30" then ifile = idir+"USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc"  end if
    ofile = odir+"aqua_topo.v1.nc"

;=============================================================================
; Load CESM default SST input data
;=============================================================================
    infile = addfile(ifile,"r")

    ; printline()

;=============================================================================
; Create outfile and populate with input data
;=============================================================================
    if isfilepresent(ofile) then system("rm "+ofile) end if
    outfile = addfile(ofile,"c")

    vname = getfilevarnames(infile)

    do v = 0,dimsizes(vname)-1
        outfile->$vname(v)$ = infile->$vname(v)$
    end do

    outfile->PHIS         = (/0./)
    outfile->SGH          = (/0./)
    outfile->SGH30        = (/0./)
    outfile->LANDFRAC     = (/0./)
    outfile->LANDM_COSLAT = (/0./)

    ; printline()
    print("")
    print("    "+ofile)
    print("")
;=============================================================================
;=============================================================================
end

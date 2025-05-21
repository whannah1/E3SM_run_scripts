; Create a topography file for aqua planet experiments
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 

    ;idir = "~/Data/Model/CESM/inputdata/atm/cam/inic/fv/"
    idir = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/fv/"
    idir = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/topo/"
    ; idir = "~/E3SM/init_files/"
    odir = "~/E3SM/init_files/"

    ;ifile = idir+"cami-mam3_0000-01-01_1.9x2.5_L30_c090306.nc"    ; fv 1.9 x 2.5
    ; ifile = idir+"USGS-gtopo30_1.9x2.5_remap_c050602.nc"
    ifile = idir+"USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc" ; E3SM se dycore
    ofile = odir+"aqua_topo.v1.nc"

    ;fig_type = "png"
    ;fig_file = odir+"fig.aqua.topo.v1"

;=============================================================================
; Load CESM default SST input data
;=============================================================================
    infile = addfile(ifile,"r")

    printline()

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

    printline()
    print("")
    print("    "+ofile)
    print("")
;=============================================================================
;=============================================================================
end
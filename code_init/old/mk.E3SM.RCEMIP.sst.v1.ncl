; Create an SST input file for the data ocean component (DOCN) of CESM
; Also adds warm pool depending on wp_* parameters
; a figure (fig_file) is output to describe the SST pattern
; v1 - use existing file
; v2 - use existing file only for var names - get grid info from latlon/scrip file
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if

    setfileoption("nc", "Format",  "64BitOffset")

    sst = 300   ; [K]

    res = "ne4"    ; ne4 / ne30
    
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/sst/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/atm/cam/sst/" end if

    
    if res.eq."ne30" then ifile = "sst_HadOIBl_bc_1x1_clim_c101029.nc" end if
    if res.eq."ne4"  then ifile = "sst_HadOIBl_bc_1x1_clim_c101029.nc" end if
    ; ifile = idir+"sst_HadOIBl_bc_1.9x2.5_clim_c061031.nc"    ; fv 1.9x2.5
    ; ifile = idir+"sst_HadOIBl_bc_1.9x2.5_clim_pi_c101028.nc"    ; fv 1.9x2.5

    odir = "~/E3SM/init_files/"
    ofile = "RCEMIP_sst."+res+"."+sst+"K.nc"

;=============================================================================
;=============================================================================
    infile = addfile(idir+ifile,"r")

    lat = infile->lat
    lon = infile->lon

    nlat = dimsizes(lat)
    nlon = dimsizes(lon)

    sst_aqua_out = new((/12,nlat,nlon/),float)
    sst_aqua_out = (/ sst - 273.15 /)

    sst_aqua_out!0 = "time"
    sst_aqua_out!1 = "lat"
    sst_aqua_out!2 = "lon"
    sst_aqua_out&time = infile->time
    sst_aqua_out&lat  = lat
    sst_aqua_out&lon  = lon

    ice = infile->ice_cov
    ice = (/ice*0./)

    sst_aqua_out@long_name = "Idealized Sea Surface Temperature for RCEMIP"
    sst_aqua_out@units     = "deg_C"
;=============================================================================
;=============================================================================


    if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
    outfile = addfile(odir+ofile,"c")
    outfile->date    = infile->date
    outfile->datesec = infile->datesec
    outfile->SST_cpl            = sst_aqua_out
    outfile->SST_cpl_prediddle  = sst_aqua_out
    outfile->ice_cov            = ice
    outfile->ice_cov_prediddle  = ice

    printline()
    print("")
    print("    "+odir+ofile)
    print("")
    printline()
;=============================================================================
;=============================================================================
end

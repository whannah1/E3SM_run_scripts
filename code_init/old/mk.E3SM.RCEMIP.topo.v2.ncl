; Create a topography file for aqua planet experiments
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

    res = "ne8np1"    ; ne4 / ne30
    
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/topo/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/atm/cam/topo/" end if

    ;ifile = idir+"cami-mam3_0000-01-01_1.9x2.5_L30_c090306.nc"    ; fv 1.9 x 2.5
    ; ifile = idir+"USGS-gtopo30_1.9x2.5_remap_c050602.nc"
    ; if res.eq."ne30" then ifile = idir+"USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc" end if
    ; if res.eq."ne4"  then ifile = idir+"USGS-gtopo30_ne4np4_16x.c20160612.nc" end if
    ifile = idir+"USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc" 
    ; ifile = idir+"USGS-gtopo30_ne4np4_16x.c20160612.nc"

    odir = "~/E3SM/init_files/"
    ofile = odir+"RCEMIP_topo."+res+".v1.nc"

;=============================================================================
;=============================================================================
    ;;; latlon and scrip file from HOMME
    lfile = "~/E3SM/data_grid/"+res+"_latlon.nc" 
    rfile = "~/E3SM/data_grid/"+res+"_scrip.nc" 

    latlon_file = addfile(lfile,"r")
    ; area = latlon_file->area
    lat  = latlon_file->lat
    lon  = latlon_file->lon

    ncol = dimsizes( lat )
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

    var = getfilevarnames(infile)

    do v = 0,dimsizes(var)-1 
        
        dim_name := getfilevardims(infile,var(v))

        dims := getfilevardimsizes(infile,var(v))
        ndim := dimsizes(dims)

        if any(dim_name.eq."ncol") then dims( ind(dim_name.eq."ncol") ) = ncol end if

        V_out := new(dims,typeof(infile->$var(v)$))

        if var(v).eq."PHIS"         then V_out = 0. end if
        if var(v).eq."SGH"          then V_out = 0. end if
        if var(v).eq."SGH30"        then V_out = 0. end if
        if var(v).eq."LANDFRAC"     then V_out = 0. end if
        if var(v).eq."LANDM_COSLAT" then V_out = 0. end if

        copy_VarAtts(infile->$var(v)$,V_out)

        ;;; copy coordinate names one by one
        do n = 0,ndim-1
            V_out!n = dim_name(n)
            if isfilevarcoord(infile,var(v),dim_name(n)) .and. dim_name(n).ne."ncol" then
                V_out&$dim_name(n)$ = infile->$var(v)$&$dim_name(n)$
            end if
        end do
        
        outfile->$var(v)$ = V_out

    end do

    print("")
    print("    "+ofile)
    print("")
    printline()
;=============================================================================
;=============================================================================
end
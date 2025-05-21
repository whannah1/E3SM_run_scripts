; Create a "domian" file for the land and ocean components of E3SM
; since this is for an aqua planet, there is all ocean and no land
; v1 - use existing domain files
; v2 - use existing domain files only for var names - get grid info from np4 latlon file
; v3 - similar to v2, but don't convert np4 -> pg1
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
load "~/E3SM/custom_grid_methods.ncl"
begin 

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if

    setfileoption("nc", "Format",  "64BitOffset")


    ; res = "ne4np1" 
    res = "ne8np1" 
    ; res = "ne30np1" 

    
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/share/domains/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/share/domains/" end if
    lnd_ifile = "domain.lnd.ne4np4_oQU240.160614.nc"
    ocn_ifile = "domain.ocn.ne4np4_oQU240.160614.nc"

    odir = "~/E3SM/init_files/"
    ofile_lnd = "RCEMIP_domain.lnd."+res+".nc"
    ofile_ocn = "RCEMIP_domain.ocn."+res+".nc"
    

    print("")
    print("  idir : "+idir)
    print("  odir : "+odir)
    print("")

;==================================================================================================
;==================================================================================================
    ;;; latlon and scrip file from HOMME
    lfile = "~/E3SM/data_grid/"+res+"_latlon.nc" 
    rfile = "~/E3SM/data_grid/"+res+"_scrip.nc" 

    ; latlon_file = addfile(lfile,"r")
    ; area = latlon_file->area
    ; lat  = latlon_file->lat
    ; lon  = latlon_file->lon

    scrip_file = addfile(rfile,"r")
print(scrip_file)
    area = scrip_file->grid_area
    grid_center_lat = scrip_file->grid_center_lat
    grid_center_lon = scrip_file->grid_center_lon
    grid_corner_lat = scrip_file->grid_corner_lat
    grid_corner_lon = scrip_file->grid_corner_lon

;==================================================================================================
; Make new LND domain file
;==================================================================================================

    ncol = dimsizes( grid_corner_lat(:,0) )
    ncor = dimsizes( grid_corner_lat(0,:) )

    printline()

    ofile = ofile_lnd

    print("")
    print("  Land domain files:")
    print("")
    print("    ifile: "+idir+lnd_ifile)
    print("")

    if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
    infile  = addfile(idir+lnd_ifile,"r")
    outfile = addfile(odir+ofile,"c")
    
    var = getfilevarnames(infile)

    do v = 0,dimsizes(var)-1 
        
        dim_name := getfilevardims(infile,var(v))

        dims := getfilevardimsizes(infile,var(v))
        ndim := dimsizes(dims)

        if any(dim_name.eq."ni") then dims( ind(dim_name.eq."ni") ) = ncol end if
        if any(dim_name.eq."nv") then dims( ind(dim_name.eq."nv") ) = ncor end if

        V_out := new(dims,typeof(infile->$var(v)$))

        if var(v).eq."frac" then V_out = 0. end if
        if var(v).eq."mask" then V_out = 0  end if
        if var(v).eq."area" then V_out = area end if
        
        if var(v).eq."xc" then V_out = grid_center_lon end if
        if var(v).eq."yc" then V_out = grid_center_lat end if
        if var(v).eq."xv" then V_out = grid_corner_lat end if
        if var(v).eq."yv" then V_out = grid_corner_lon end if

        copy_VarAtts(infile->$var(v)$,V_out)

        ;;; copy coordinate names one by one
        do n = 0,ndim-1
            V_out!n = dim_name(n)
        end do
        
        outfile->$var(v)$ = V_out

    end do

    ; outfile->frac = 0.
    ; outfile->mask = 0
    
    
    print("    ofile: "+odir+ofile)
    print("")

;==================================================================================================
; Make new OCN domain file (also used for sea ice)
;==================================================================================================
    printline()

    ofile = ofile_ocn

    print("")
    print("  Ocean domain files:")
    print("")
    print("    ifile: "+idir+ocn_ifile)
    print("")

    if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
    infile  = addfile(idir+ocn_ifile,"r")
    outfile = addfile(odir+ofile,"c")
    
    var = getfilevarnames(infile)

    do v = 0,dimsizes(var)-1 
        
        dim_name := getfilevardims(infile,var(v))

        dims := getfilevardimsizes(infile,var(v))
        ndim := dimsizes(dims)

        if any(dim_name.eq."ni") then dims( ind(dim_name.eq."ni") ) = ncol end if
        if any(dim_name.eq."nv") then dims( ind(dim_name.eq."nv") ) = ncor end if

        V_out := new(dims,typeof(infile->$var(v)$))

        if var(v).eq."frac" then V_out = 1. end if
        if var(v).eq."mask" then V_out = 1  end if
        if var(v).eq."area" then V_out = area end if
        
        if var(v).eq."xc" then V_out = grid_center_lon end if
        if var(v).eq."yc" then V_out = grid_center_lat end if
        if var(v).eq."xv" then V_out = grid_corner_lat end if
        if var(v).eq."yv" then V_out = grid_corner_lon end if

        copy_VarAtts(infile->$var(v)$,V_out)

        ;;; copy coordinate names one by one
        do n = 0,ndim-1
            V_out!n = dim_name(n)
        end do
        
        outfile->$var(v)$ = V_out
        
    end do

    ; outfile->frac = 1.
    ; outfile->mask = 1
    

    
    print("    ofile: "+odir+ofile)
    print("")
;==================================================================================================
;==================================================================================================
printline()
end
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 
    
    DD_PI = 3.14159265359
    DIST_THRESHOLD = 1.0D-9

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if

    setfileoption("nc", "Format",  "64BitOffset")

    ne  = 4
    npg = 2
    
    res = "ne"+ne+"pg"+npg
    
    ; if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/share/domains/" end if
    ; if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/share/domains/" end if
    ; idir = "~/E3SM/init_files/"
    ; idir = "~/E3SM/data_grid/"
    
    idir = "~/Tempest/"
    odir = "~/E3SM/data_grid/"

    ifile = "ne"+ne+".g"
    ofile = "ne"+ne+"pg"+npg+"_scrip.nc"

    ; if npg.gt.0 then ifile = str_sub_str(ifile,".g","pg"+npg+".g") end if

    print("")
    print("  ifile : "+idir+ifile)
    print("  ofile : "+odir+ofile)
    print("")
    
;==================================================================================================
;==================================================================================================
    infile  = addfile(idir+ifile,"r")

    x = infile->coord(0,:)
    y = infile->coord(1,:)
    z = infile->coord(2,:)

    ; x := block_avg(x,4)
    ; y := block_avg(y,4)
    ; z := block_avg(z,4)

    ncol = dimsizes(x)
    ;---------------------------------------------------------------------------
    ; subdivide elements
    ;---------------------------------------------------------------------------
    ; if npg.eq.0 then 
        q = new(4,double)
        cx = new(4,double)
        do n = 0,npg-1

            dG = (2.0*n + 1.0) / (2.0 * npg);

            a = dG
            b = dG

            cx(0) = 0.
            cx(1) = 0.
            cx(2) = 1.
            cx(3) = 1.

            dXc = cx(0) * (1.0 - a ) * (1.0 - b ) \
                 +cx(1) *        a   * (1.0 - b ) \
                 +cx(2) *        a   *        b   \
                 +cx(3) * (1.0 - a ) *        b 


            q(0) = ( 1. - a ) * ( 1. - b ) 
            q(1) = ( 1. + a ) * ( 1. - b ) 
            q(2) = ( 1. + a ) * ( 1. + b ) 
            q(3) = ( 1. - a ) * ( 1. + b )

            ; do i = 1,3
                xx = sum(cx(:)*q(:)/4)
            ; end do

            print("dG: "+dG+"  dXc: "+dXc+"   xx: "+xx)
        end do
    ; end if
    exit
    ;---------------------------------------------------------------------------
    ;---------------------------------------------------------------------------
    ncol = dimsizes(x)

    lon = new(ncol,double)
    lat = new(ncol,double)
    ;---------------------------------------------------------------------------
    ;---------------------------------------------------------------------------
    r = sqrt( x^2 + y^2 + z^2 )

    lat = asin( z / r )
    
    do n = 0,ncol-1
        if ( abs(abs(lat(n))-DD_PI/2) .ge. DIST_THRESHOLD ) then
            lon = atan2( y(n), x(n) )
            if lon(n).gt.0. then
                lon(n) = lon(n) + 2.*DD_PI
            end if
        end if
    end do

    print(lat(:3)*180./DD_PI)
    print("")
    ; print( avg(lat(:3)) *180./DD_PI)


;==================================================================================================
;==================================================================================================

exit
    
    if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
    outfile = addfile(odir+ofile,"c")

    outfile->grid_center_lat = element_center_lat
    outfile->grid_center_lon = element_center_lon

    outfile->grid_corner_lat = element_corner_lat
    outfile->grid_corner_lon = element_corner_lon

    outfile->grid_area  = element_area
    outfile->grid_dims  = grid_dims
    outfile->grid_imask = grid_imask

    ; outfile@title = "ne"+ne+"np" + np
    outfile@Created_by = "Walter Hannah - "+cd_string(now(),"%c %d %Y")+" "
    outfile@history    = "Adapted from file: "+ifile
    
;==================================================================================================
;==================================================================================================
end
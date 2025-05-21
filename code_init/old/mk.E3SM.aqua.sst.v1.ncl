; Create an SST input file for the data ocean component (DOCN) of CESM
; Also adds warm pool depending on wp_* parameters
; a figure (fig_file) is output to describe the SST pattern
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 

    ;idir = "~/Data/Model/CESM/inputdata/atm/cam/sst/"
    idir = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/sst/"
    ; odir = "~/E3SM/init_files/"
    odir = "~/E3SM/init_files/"
    
    sst_trop = 27.       ; zonal avg equatorial SST - before adding warm pool
    sst_yc   = 1.8        ; Meridional shape parameter - defualt = 2. - smaller = wider
    sst_exp  = 4.        ; must be even 2 = round zonal mean profile, 4 = more square-ish
    sst_clat = 0        ; Latitude of warmest SST
    wp_clat  = sst_clat
    ;wp_clat  = -5       ; Y Center of warm pool
    wp_clon  = 145.      ; X Center of warm pool
    wp_amp   = 3.        ; warm pool SST amplitude
    wp_xc    = 6.        ; longitudinal shape parameter (default = 4, smaller makes it wider, 0 = zonally sym)
    wp_yc    = 4.        ; latitudinal shape parameter  (default = 4, smaller makes it wider)

    fig_type = "png"
    fmt  = "%2.1f"
    imt  = "%2.2i"
    fig_file = "~/E3SM/figs_init/fig.aqua.sst.v1"

    mod_str = ".sst_yc_"+sprintf(fmt,sst_yc)+".sst_exp_"+sprintf(fmt,sst_exp)+".amp_"+sprintf(fmt,wp_amp)+".xc_"+sprintf(fmt,wp_xc)+".yc_"+sprintf(fmt,wp_yc)
    mod_str = mod_str+".wp_clat_"+sprinti(imt,wp_clat)+".sst_clat_"+sprinti(imt,sst_clat)
    fig_file = fig_file + mod_str

    ifile = "sst_HadOIBl_bc_1x1_clim_c101029.nc"       ; se ne16
    ;ifile = idir+"sst_HadOIBl_bc_1.9x2.5_clim_c061031.nc"    ; fv 1.9x2.5
    ; ifile = idir+"sst_HadOIBl_bc_1.9x2.5_clim_pi_c101028.nc"    ; fv 1.9x2.5
    ofile = "sst_aqua_ideal.v1"
    ofile = ofile + mod_str + ".nc"

    debug = False
;=============================================================================
; Load CESM default SST input data
;=============================================================================
    infile = addfile(idir+ifile,"r")

    lat = infile->lat
    lon = infile->lon

    nlat = dimsizes(lat)
    nlon = dimsizes(lon)

    sst  = infile->SST_cpl

    ; months = (/ 1, 2, 12/)
    ;months = (/ 7, 8,  9/)
    months = ispan(1,12,1)
    
    isst = dim_avg_n_Wrap(sst(months-1,:,:),0)

    sst_zavg = dim_avg_n_Wrap   (isst,1)
    sst_zmin = dim_min_n_Wrap   (isst,1)
    sst_zmax = dim_max_n_Wrap   (isst,1)
    sst_zstd = dim_stddev_n_Wrap(isst,1)
    sst_zavg_up = sst_zavg
    sst_zavg_dn = sst_zavg
    sst_zavg_up = (/ sst_zavg + sst_zstd /)
    sst_zavg_dn = (/ sst_zavg - sst_zstd /)
;=============================================================================
; Create Idealized SST map for aqua-planet experiment
;=============================================================================
    sst_aqua = isst
    ;------------------------------------------------
    ; Construct initial SST field - zonally symmetric
    ;------------------------------------------------
    y = (lat-sst_clat)/max(lat)
    ;shape = cos((lat*pi/180.))
    shape = exp(-1.*(sst_yc*y)^sst_exp) 
    sst_aqua_zavg := shape * (sst_trop+2.) - 2.

    ;sst_aqua = (/0./)
    sst_aqua = (/ tofloat(conform(sst_aqua,sst_aqua_zavg,0)) /) 
    ;------------------------------------------------
    ;------------------------------------------------
    ;sst_aqua_zavg = dim_avg_n_Wrap(sst_aqua,1)
    ;sst_aqua_zmin = dim_min_n_Wrap(sst_aqua,1)
    ;sst_aqua_zmax = dim_max_n_Wrap(sst_aqua,1)
    ;sst_aqua_zstd = dim_stddev_n_Wrap(sst_aqua,1)
    ;------------------------------------------------
    ; add warm pool - using Error function shape
    ;------------------------------------------------
    x = (lon-wp_clon)/max(lon) 
    y = (lat-wp_clat)/max(lat) 

    wpx = exp(-1.*(wp_xc*x)^4.)
    wpy = exp(-1.*(wp_yc*y)^4.)

    wp = new((/dimsizes(wpy),dimsizes(wpx)/),float)
    wp = tofloat( wp_amp * conform(wp,wpy,0) * conform(wp,wpx,1) )
    
    copy_VarCoords(sst_aqua,wp)

    sst_aqua = (/ sst_aqua + wp /)
    ;------------------------------------------------
    ;------------------------------------------------
    sst_aqua_zavg = dim_avg_n_Wrap(sst_aqua,1)
    sst_aqua_zmin = dim_min_n_Wrap(sst_aqua,1)
    sst_aqua_zmax = dim_max_n_Wrap(sst_aqua,1)
    sst_aqua_zstd = dim_stddev_n_Wrap(sst_aqua,1)
    ;------------------------------------------------
    ;------------------------------------------------
    if False then
        ;shape = exp(-1.*(2.*y)^2.) 
        shape = exp(-1.*(sst_y*y)^2.) 
        sst_aqua_zavg := shape * (sst_trop+2.) - 2.
        sst_aqua_ctl = isst
        sst_aqua_ctl = (/ tofloat(conform(sst_aqua,sst_aqua_zavg,0)) /) 

        wp_xc_ctl = 4
        wp_yc_ctl = 4
        wpx_ctl = exp(-1.*(wp_xc_ctl*x)^4.)
        wpy_ctl = exp(-1.*(wp_yc_ctl*y)^4.)

        wp_ctl = new((/dimsizes(wpy_ctl),dimsizes(wpx_ctl)/),float)
        wp_ctl = tofloat( wp_amp * conform(wp,wpy_ctl,0) * conform(wp,wpx_ctl,1) )
        
        copy_VarCoords(sst_aqua_ctl,wp_ctl)

        sst_aqua_ctl = (/ sst_aqua_ctl + wp_ctl /)
        ;------------------------------------------------
        ;------------------------------------------------
        ;printMAM(sst_aqua({0},:)-27.)
        print(avg(sst_aqua({0},:)-27.))
        ;------------------------------------------------
        ;------------------------------------------------
        wks = gsn_open_wks("x11","test")
        plot := new(2,graphic)
            res = setres_contour_fill()
            res@mpCenterLonF         = 180.
            res@cnLevelSelectionMode = "ExplicitLevels"
            res@cnLevels             = ispan(-1,30,1)
            res@gsnLeftString = "Observed SST (DJF)"
        plot(0) = gsn_csm_contour_map(wks,sst_aqua_ctl ,res)
        plot(1) = gsn_csm_contour_map(wks,sst_aqua ,res)
        pres = setres_panel();_labeled()
        gsn_panel(wks,plot,(/2,1/),pres)
        exit 
    end if
;=============================================================================
;=============================================================================    
    if debug then fig_type = "x11" end if
    wks := gsn_open_wks(fig_type,fig_file)
    plot := new(4,graphic)
        res = setres_contour_fill()
        res@mpCenterLonF         = 180.
        res@cnLevelSelectionMode = "ExplicitLevels"
        ;res@cnLevels             = ispan(-1,31,1)
        res@cnLevels             = ispan(-1,30,1)
    ;--------------------------------------------
    ; Plot SST maps
    ;--------------------------------------------
        res@gsnLeftString = "Observed SST (DJF)"
    plot(0) = gsn_csm_contour_map(wks,isst ,res)

        res@gsnLeftString = "Idealized SST"
    plot(2) = gsn_csm_contour_map(wks,sst_aqua,res)
    ;--------------------------------------------
    ; Plot zonal mean SST
    ;--------------------------------------------
        res := setres_default()
        res@xyLineThicknessF    = 3.
        res@xyDashPattern       = 0
        res@xyLineColors        = (/"black","red","blue","orange"/)
        res@vpHeightF           = 0.4
        res@tiXAxisString       = "deg C"
    ;plot(1) = gsn_csm_xy(wks,sst_zavg,lat,res)
    ;plot(3) = gsn_csm_xy(wks,dim_avg_n_Wrap(sst_aqua,1),lat,res)
        ;res@xyLineColors        := (/"black","gray","gray","red","blue","orange"/)
        res@gsnLeftString = "Zonal Mean"
    plot(1) = gsn_csm_xy(wks,(/sst_zavg,sst_aqua_zavg,sst_aqua_zmin,sst_aqua_zmax/),lat,res)
    ;plot(1) = gsn_csm_xy(wks,(/sst_zavg,sst_zmin,sst_zmax,sst_aqua_zavg,sst_aqua_zmin,sst_aqua_zmax/),lat,res)
        res@xyLineColors        := (/"black","red","blue","orange"/)
        res@gsnLeftString = "Zonal Std. Dev."
    plot(3) = gsn_csm_xy(wks,(/sst_zstd,sst_aqua_zstd/),lat,res)
    ;--------------------------------------------
    ; Add line at the equator
    ;--------------------------------------------
    res@gsnLeftString = ""
    res@gsnRightString = ""
    do p = 0,3 
        overlay(plot(p),gsn_csm_xy(wks,(/-1e4,1e4/),(/0,0/),res)) 
    end do
    ;--------------------------------------------
    ; combine plots
    ;--------------------------------------------
        pres = setres_panel();_labeled()
    if debug then 
        gsn_panel(wks,plot(1),(/1,1/),pres)
    else
        gsn_panel(wks,plot,(/2,2/),pres)
    end if
    trimPNG(fig_file)    

    if debug then exit end if
;=============================================================================
;=============================================================================
    sst_aqua_out = new((/12,nlat,nlon/),float)
    sst_aqua_out = conform(sst_aqua_out,sst_aqua,(/1,2/))

    sst_aqua_out!0 = "time"
    sst_aqua_out!1 = "lat"
    sst_aqua_out!2 = "lon"
    sst_aqua_out&time = infile->time
    sst_aqua_out&lat  = lat
    sst_aqua_out&lon  = lon

    ;null_var = sst_aqua_out
    ;null_var = (/ null_var*0. /)
    ice = infile->ice_cov
    ice = (/ice*0./)

    sst_aqua_out@long_name = "Idealized Sea Surface Temperature"
    sst_aqua_out@units     = "deg_C"
;=============================================================================
;=============================================================================
    
    printline()
    printMAM(sst_aqua_out)
    printMAM(ice)
    printline()


    if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
    outfile = addfile(odir+ofile,"c")
    outfile->date    = infile->date
    outfile->datesec = infile->datesec
    outfile->SST_cpl            = sst_aqua_out
    outfile->SST_cpl_prediddle  = sst_aqua_out
    outfile->ice_cov            = ice;null_var
    outfile->ice_cov_prediddle  = ice;null_var

    printline()
    print("")
    print("    "+odir+ofile)
    print("")
    printline()
;=============================================================================
;=============================================================================
end

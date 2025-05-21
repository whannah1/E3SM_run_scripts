load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions_E3SM.ncl"
begin
    
    grid = "ne30pg2"

    ifile = "/global/cscratch1/sd/whannah/acme_scratch/init_files/USGS_"+grid+"_unsmoothed_20190328.nc"

    sfile = "~/E3SM/data_grid/"+grid+"_scrip.nc"

    fig_type = "x11"
    fig_file = "figs_grid/chk.scrip.v1"

    ;===========================================================================
    ;===========================================================================
    print(""+ifile)
    infile = addfile(sfile,"r")
    ncol = dimsizes(infile->grid_area)
    grid_center_lat = infile->grid_center_lat(:ncol-1)
    grid_center_lon = infile->grid_center_lon(:ncol-1)
    grid_corner_lat = infile->grid_corner_lat(:ncol-1,:);(grid_size|:,grid_corners|:)
    grid_corner_lon = infile->grid_corner_lon(:ncol-1,:);(grid_size|:,grid_corners|:)
    


    infile = addfile(ifile,"r")
    data = infile->SGH
    ; data = infile->PHIS
    data@lat = grid_center_lat
    data@lon = grid_center_lon

    printMAM(data)

    ;===========================================================================
    ;===========================================================================
    wks = gsn_open_wks(fig_type,fig_file)
    plot = new(1,graphic)

    res = setres_contour_fill_smalltxt()
    ; res@cnFillMode      = "RasterFill"
    res@cnFillMode      = "CellFill"
    ; res@cnFillPalette   = "WhiteBlueGreenYellowRed"
    res@cnFillPalette   = "OceanLakeLandSnow"

    
    ; res@cnLevelSelectionMode = "ExplicitLevels"
    ; res@cnLevels        := fspan(-1,1,39)

    ; res@mpProjection    = "Aitoff"
    ; res@mpProjection    = "Satellite"
    ; res@mpProjection    = "Stereographic"

    
    ;;; zoom in on polar region
    ; res@mpCenterLatF = 90
    ; res@mpGridAndLimbOn = True
    ; res@mpLimitMode     = "Angles"
    ; if res@mpProjection.eq."Stereographic" then angle = 50. end if
    ; if res@mpProjection.eq."Satellite"     then angle = 1.5 end if
    ; if isvar("angle") then
    ;     res@mpLeftAngleF    = angle
    ;     res@mpRightAngleF   = angle
    ;     res@mpBottomAngleF  = angle
    ;     res@mpTopAngleF     = angle
    ; end if

    ; res@mpLimitMode     = "LatLon"
    ; plat_center = elm_center_lat(0)
    ; plon_center = elm_center_lon(0)
    ; width = 30
    ; res@mpMinLatF = plat_center - width/2.
    ; res@mpMaxLatF = plat_center + width/2.
    ; res@mpMinLonF = plon_center - width/2.
    ; res@mpMaxLonF = plon_center + width/2.

    res@sfYArray      = grid_center_lat ;(:n_pt_plot)
    res@sfXArray      = grid_center_lon ;(:n_pt_plot)
    res@sfYCellBounds = grid_corner_lat ;(:n_pt_plot,:)
    res@sfXCellBounds = grid_corner_lon ;(:n_pt_plot,:)
        
    plot(0) = gsn_csm_contour_map(wks,data,res)

    gsn_panel(wks,plot,(/1,dimsizes(plot)/),False)
    trimPNG(fig_file)

    ;===========================================================================
    ;===========================================================================

end
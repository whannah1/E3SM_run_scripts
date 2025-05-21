load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions_E3SM.ncl"
begin
    
    ; idir = "/global/cscratch1/sd/whannah/acme_scratch/cori-knl/E3SM_TEST_ne4pg2_F-EAMv1-AQP1/run/"
    ; ifile = idir+"ne4pg2_scrip.nc"

    ; ifile = "~/E3SM/data_grid/ne25np4_scrip.nc"
    ifile = "~/E3SM/data_grid/ne30pg2_scrip.nc"

    fig_type = "x11"
    fig_file = "figs_grid/chk.scrip.v1"

    ;===========================================================================
    ;===========================================================================
    print(""+ifile)
    infile = addfile(ifile,"r")

    ncol = dimsizes(infile->grid_area)
    ; ncol = 5

    grid_center_lat = infile->grid_center_lat(:ncol-1)
    grid_center_lon = infile->grid_center_lon(:ncol-1)
    grid_corner_lat = infile->grid_corner_lat(:ncol-1,:);(grid_size|:,grid_corners|:)
    grid_corner_lon = infile->grid_corner_lon(:ncol-1,:);(grid_size|:,grid_corners|:)
    


fmt = "%8.4f"
do i = 0,ncol-1
    ; condition = True
    ; condition = grid_corner_lon(i,2).gt.grid_corner_lon(i,0)

    b1 = calc_great_circle_bearing(grid_corner_lat(i,0),grid_corner_lat(i,1),\
                                   grid_corner_lon(i,0),grid_corner_lon(i,1) )
    b2 = calc_great_circle_bearing(grid_corner_lat(i,1),grid_corner_lat(i,2),\
                                   grid_corner_lon(i,1),grid_corner_lon(i,2) )
    bdiff = (b2-b1)
    if bdiff.gt.180 then bdiff = bdiff-360. end if
    condition = bdiff.gt.0

    if condition then
        print("i:"+i)
        print("  center: "+sprintf(fmt,grid_center_lat(i) )  +"  "+sprintf(fmt,grid_center_lon(i) ) )
        print("")
        print("b1,b2,diff: "+b1+"  "+b2+"   "+(b2-b1))
        do c = 0,3
        print("          "+sprintf(fmt,grid_corner_lat(i,c) )+"  "+sprintf(fmt,grid_corner_lon(i,c) ) )
        end do
        print("")

        X = grid_corner_lon(i,:)
        Y = grid_corner_lat(i,:)
        qpres = setres_default()
        qpres@xyMarkLineMode    = "MarkLines"
        qpres@xyMarker          = 16
        qpres@xyLineThicknessF  = 6.
        qpwks = gsn_open_wks("x11","qplot_xy")
        qplot = gsn_csm_xy(qpwks,X,Y,qpres)
        mkres = True
        mkres@gsMarkerColor = "red"
        mkres@gsMarkerSizeF = 15.
        mkres@gsMarkerIndex = 16
        dum = gsn_add_polymarker(qpwks,qplot,X(0),Y(0),mkres)
        draw(qplot)
        frame(qpwks)
        ; exit
    end if
end do
exit


; grid_corner_lat = where(grid_corner_lat.eq. 90, 89.999,grid_corner_lat)
; grid_corner_lat = where(grid_corner_lat.eq.-90,-89.999,grid_corner_lat)


printMM(grid_corner_lat)
printMM(grid_corner_lon)
; exit

; max_val = 0.d
; do i = 0,ncol-1
;     diff := stddev( grid_corner_lon(i,:) )
;     max_val = max( (/max_val, diff/) )
; end do
; print(max_val)
; exit

    ; data = random_uniform(-1,1,(/ncol/))
    data = random_normal(0,0.4,(/ncol/))
    data@lat = grid_center_lat
    data@lon = grid_center_lon

; printVarSummary(data)
; printMAMS(data)
; exit

    ;===========================================================================
    ;===========================================================================
    wks = gsn_open_wks(fig_type,fig_file)
    plot = new(1,graphic)

    res = setres_contour_fill_smalltxt()
    ; res@cnFillMode      = "RasterFill"
    res@cnFillMode      = "CellFill"
    ; res@cnFillPalette   = "WhiteBlueGreenYellowRed"
    ; res@cnFillPalette   = "OceanLakeLandSnow"
    ; res@cnFillPalette   = "GMT_gray"
    res@cnFillPalette   = "gsdtol"

    
    res@cnLevelSelectionMode = "ExplicitLevels"
    res@cnLevels        := fspan(-1,1,39)

    ; res@mpProjection    = "Aitoff"
    res@mpProjection    = "Satellite"
    ; res@mpProjection    = "Stereographic"

    res@mpCenterLatF = 90
    
    res@mpGridAndLimbOn = True

    res@mpLimitMode     = "Angles"
    if res@mpProjection.eq."Stereographic" then angle = 50. end if
    if res@mpProjection.eq."Satellite"     then angle = 1.5 end if
    if isvar("angle") then
        res@mpLeftAngleF    = angle
        res@mpRightAngleF   = angle
        res@mpBottomAngleF  = angle
        res@mpTopAngleF     = angle
    end if

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
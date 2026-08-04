; Plot the E3SM Spectral Element (SE) grid 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions.ncl"
begin
        
    fig_type = "png"
    fig_file = "~/E3SM/figs_grid/grid.scrip.v1"

    ifile = "/project/projectdirs/e3sm/mapping/grids/conusx4v1np4_chevrons_scrip_c150815.nc"
        
        
;====================================================================================================
;====================================================================================================

    ;----------------------------------------------
    ; Load domain file
    ;----------------------------------------------
    infile = addfile(ifile,"r")
    
    if any(getfilevarnames(infile).eq."grid_center_lat") then
        lat = infile->grid_center_lat
        lon = infile->grid_center_lon
        vlat = infile->grid_corner_lat
        vlon = infile->grid_corner_lon

        ; lat = (/lat*180./3.14159/)
        ; lon = (/lon*180./3.14159/)
        ; vlat = (/vlat*180./3.14159/)
        ; vlon = (/vlon*180./3.14159/)
        
    end if

    if any(getfilevarnames(infile).eq."yc") then
        lat = infile->yc
        lon = infile->xc
        vlat = infile->yv
        vlon = infile->xv
    end if
    
    dims = dimsizes(vlat)
    ndim = dimsizes(dims)
    if ndim.eq.3 then
        lat  := reshape( lat,product(dims(0:1)))
        lon  := reshape( lon,product(dims(0:1)))
        vlat := reshape(vlat,(/product(dims(0:1)),dims(2)/) )
        vlon := reshape(vlon,(/product(dims(0:1)),dims(2)/) )
    end if

    lat@units = "degrees_north"
    lon@units = "degrees_east"
    vlat@units = "degrees_north"
    vlon@units = "degrees_east"

    ncol = dimsizes(lat)

    data = random_normal(0,0.4,(/ncol/))
    data@lat = lat
    data@lon = lon

    ; print(infile)
    print("--------------------------------------------------")

;====================================================================================================
;====================================================================================================
    wks = gsn_open_wks(fig_type,fig_file)

    res = True
    res@gsnDraw                       = False
    res@gsnFrame                      = False
    res@tmXTOn                        = False
    res@tmXBMajorOutwardLengthF       = 0.
    res@tmXBMinorOutwardLengthF       = 0.
    res@tmYLMajorOutwardLengthF       = 0.
    res@tmYLMinorOutwardLengthF       = 0.
    res@tmYLLabelFontHeightF          = 0.015
    res@tmXBLabelFontHeightF          = 0.015
    res@tiXAxisFontHeightF            = 0.02
    res@tiYAxisFontHeightF            = 0.02
    res@tmXBMinorOn                   = False
    res@tmYLMinorOn                   = False
    res@cnFillOn                      = True
    res@cnLinesOn                     = False
    res@cnLineLabelsOn                = False
    res@cnInfoLabelOn                 = False
    res@cnLevelSelectionMode          = "ExplicitLevels"
    res@cnLineThicknessF              = 3.
    res@gsnContourNegLineDashPattern  = 1
    res@gsnContourZeroLineThicknessF  = 6

    res@gsnRightString  = ""
    res@gsnLeftString   = ""

    res@mpLimitMode     = "LatLon"
    res@mpMinLatF       =  30
    res@mpMaxLatF       =  35
    res@mpMinLonF       =  360-95
    res@mpMaxLonF       =  360-90
    

    ; res@cnFillMode      = "RasterFill"

    res@cnFillMode      = "CellFill"
    res@sfXArray        = lon
    res@sfYArray        = lat
    res@sfXCellBounds   = vlon
    res@sfYCellBounds   = vlat
    

    res@cnFillPalette = "BlWhRe" 
    ; res@cnFillPalette = "BlueDarkRed18" 
        
    plot = gsn_csm_contour_map(wks,data,res) 
    ;---------------------------------------------------------------------
    ;---------------------------------------------------------------------
    pres = True
    gsn_panel(wks,plot,(/1,dimsizes(plot)/),pres)

    trimPNG(fig_file)
;====================================================================================================
;====================================================================================================
end

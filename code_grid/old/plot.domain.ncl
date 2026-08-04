; Plot the E3SM Spectral Element (SE) grid 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions.ncl"
begin
        
    fig_type = "png"
    fig_file = "~/E3SM/figs_grid/domain_frac"

    ; ifile = "/global/homes/w/whannah/Tempest/domain.ocn.ne30pg2_oECv3.190806.nc"
    ifile = "/global/homes/w/whannah/Tempest/domain.ocn.ne30pg2_gx1v6.190806.nc"
        
        
;====================================================================================================
;====================================================================================================

    ;----------------------------------------------
    ; Load domain file
    ;----------------------------------------------
    infile = addfile(ifile,"r")
    frac = infile->frac(0,:)

    lat = infile->yc(0,:)
    lon = infile->xc(0,:)

    print(infile)
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

    ; res@mpCenterLonF    = 20.
    ; res@mpCenterLatF    = 25.
    ; res@mpLimitMode     = "LatLon"
    ; res@mpMinLatF       = -10
    ; res@mpMaxLatF       =  50
    ; res@mpMinLonF       =   0
    ; res@mpMaxLonF       =  60

    if isStrSubset(ifile,"ne4")   then sfile = "~/E3SM/data_grid/ne4np4_scrip.nc" end if
    if isStrSubset(ifile,"ne16")  then sfile = "~/E3SM/data_grid/ne16np4_scrip.nc" end if
    if isStrSubset(ifile,"ne30")  then sfile = "~/E3SM/data_grid/ne30np4_scrip.nc" end if
    if isStrSubset(ifile,"ne120") then sfile = "~/E3SM/data_grid/ne120np4_scrip.nc" end if

    if isStrSubset(ifile,"ne4pg2")   then sfile = "~/E3SM/data_grid/ne4pg2_scrip.nc" end if
    if isStrSubset(ifile,"ne16pg2")  then sfile = "~/E3SM/data_grid/ne16pg2_scrip.nc" end if
    if isStrSubset(ifile,"ne30pg2")  then sfile = "~/E3SM/data_grid/ne30pg2_scrip.nc" end if
    if isStrSubset(ifile,"ne120pg2") then sfile = "~/E3SM/data_grid/ne120pg2_scrip.nc" end if
    
    scrip_file = addfile(sfile,"r")

    res@cnFillMode      = "CellFill"
    res@sfXArray        = lon
    res@sfYArray        = lat
    res@sfXCellBounds   = scrip_file->grid_corner_lon(:,:)
    res@sfYCellBounds   = scrip_file->grid_corner_lat(:,:)
    

    res@cnFillPalette = "BlWhRe" 
    ; res@cnFillPalette = "BlueDarkRed18" 
        
    plot = gsn_csm_contour_map(wks,frac,res) 
    ;---------------------------------------------------------------------
    ;---------------------------------------------------------------------
    pres = True
    gsn_panel(wks,plot,(/1,dimsizes(plot)/),pres)

    trimPNG(fig_file)
;====================================================================================================
;====================================================================================================
end

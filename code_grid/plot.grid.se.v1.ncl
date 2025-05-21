; Plot the E3SM Spectral Element (SE) grid 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions_ACME.ncl"
begin
        idir = "~/Research/ACME/data_topo/"
        odir = "~/Research/ACME/figs_grid/"

        fig_type = "png"
        fig_file = odir+"grid.se.v1"
        
        
;====================================================================================================
;====================================================================================================

    ;----------------------------------------------
    ; Load topo data
    ;----------------------------------------------
    ifile = idir+"USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc"
    infile = addfile(ifile,"r")
    topo = infile->PHIS
    land = infile->LANDFRAC

    print(infile)
    printline()

    topo = where(land.gt.0.5,topo,-1e3)

    
    ;----------------------------------------------
    ; Load grid data for corners / nodes
    ;----------------------------------------------    
    ifile =idir+"ne30np4_091226_pentagons.nc"
    infile = addfile(ifile,"r")

    print(infile)
    printline()

    selat = infile->grid_center_lat
    selon = infile->grid_center_lon
    xbound = infile->grid_corner_lon(:,:3)
    ybound = infile->grid_corner_lat(:,:3)

    ; print(ybound(:20,:)+"   "+xbound(:20,:))
    ; exit


;====================================================================================================
;====================================================================================================
    wks = gsn_open_wks(fig_type,fig_file)
    plot = new(2,graphic)
        res = setres_contour()
        res@gsnRightString  = ""
        res@gsnLeftString   = ""
        ;res@mpCenterLonF    = 20.
        ;res@mpCenterLatF    = 25.
        res@mpLimitMode     = "LatLon"
        res@mpMinLatF       = -10
        res@mpMaxLatF       =  50
        res@mpMinLonF       =   0
        res@mpMaxLonF       =  60
        ;res@mpProjection    = "Satellite"
        res@cnFillMode      = "CellFill"
        res@sfXArray        = selon
        res@sfYArray        = selat
        res@sfXCellBounds   = xbound
        res@sfYCellBounds   = ybound
        res@lbLabelBarOn    = False
        res@cnLineLabelsOn  = False
        res@cnInfoLabelOn   = False
        res@mpPerimOn       = True
        res@cnFillPalette   = "OceanLakeLandSnow"
        res@cnLevelSelectionMode = "ExplicitLevels"
        res@cnLevels        = fspan(0,48e3,250)
        
    plot(0) = gsn_csm_contour_map(wks,topo,res) 
    ;---------------------------------------------------------------------
    ;---------------------------------------------------------------------
        lres = True
        lres@gsLineColor      = "red" 
        lres@gsLineThicknessF = 1.0 
    ncol = dimsizes(selat)
    dum = new(ncol,graphic)
    do i = 0,ncol-1
        dum(i)=gsn_add_polyline(wks,plot(0),xbound(i,:),ybound(i,:),lres)
    end do
    ;---------------------------------------------------------------------
    ;---------------------------------------------------------------------
    gsn_panel(wks,plot,(/1,2/),False)
    
    trimPNG(fig_file)
;====================================================================================================
;====================================================================================================
end

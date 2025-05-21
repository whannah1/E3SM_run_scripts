; plot a map of a global column indices
; v1 - 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions_ACME.ncl"
begin

    ifile = "~/ACME/gcol.nc"

    fig_type = "png"
    fig_file = "~/ACME/figs_grid/grid.gcol.v1"

;===================================================================================
;===================================================================================
    infile = addfile(ifile,"r")

    ; print(infile)

    ncol  = infile->ncol
    gcol  = infile->gcol
    alpha = infile->alpha
    selat = infile->lat
    selon = infile->lon

;===================================================================================
;===================================================================================
    wks = gsn_open_wks(fig_type,fig_file)
    plot = new(2,graphic)
        res = setres_contour_fill()
        res@gsnRightString  = ""
        res@gsnLeftString   = ""
        ; res@mpCenterLonF    = 20.
        ; res@mpCenterLatF    = 25.
        
        ; res@mpCenterLonF    = (tofloat(xbound(0,0)))
        ; res@mpCenterLatF    = (tofloat(ybound(0,0)))

        res@mpProjection    = "Satellite"
        ; res@mpProjection    = "Mollweide"
        
        ; res@cnFillMode      = "CellFill"
        res@cnFillMode      = "RasterFill"
        ; res@cnFillMode      = "AreaFill"

        res@sfXArray        = selon
        res@sfYArray        = selat
        ;res@sfXCellBounds   = xbound
        ;res@sfYCellBounds   = ybound
        ; res@lbLabelBarOn    = False
        res@cnLineLabelsOn  = False
        res@cnInfoLabelOn   = False
        res@mpPerimOn       = True
        
        res@cnFillPalette   = "MPL_hsv"

        res@cnLevelSelectionMode = "ExplicitLevels"
        
    ; nclev = 64
    ; res@cnLevels = toint( fspan(max(ncol)/nclev,max(ncol),nclev) )
    ; plot(0) = gsn_csm_contour_map(wks,gcol,res) 

    pi = 3.14159
    alpha = where(alpha.gt.pi,alpha-2*pi,alpha)

    nclev = 64
    rmax = pi / 4.
    res@cnLevels = fspan(-rmax,rmax,nclev) 
    plot(0) = gsn_csm_contour_map(wks,alpha,res) 

    ; plot(0) = gsn_csm_map(wks,res) 
;===================================================================================
;===================================================================================
    gsn_panel(wks,plot,(/1,2/),False)
    
    trimPNG(fig_file)
end
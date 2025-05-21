load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions_E3SM.ncl"
begin
    
    ; idir = "/global/cscratch1/sd/whannah/acme_scratch/cori-knl/E3SM_TEST_ne4pg2_F-EAMv1-AQP1/run/"
    ; ifile = idir+"ne4pg2_scrip.nc"

    ifile = "/project/projectdirs/acme/inputdata/atm/cam/inic/homme/cami_mam3_Linoz_ne30np4_L72_c160214.nc"
    ; ifile = "~/E3SM/init_scratch/cami_mam3_Linoz_ne30_L72_c160214.smoothed.nc"
    ; ifile = "~/E3SM/init_scratch/cami_mam3_Linoz_ne30pg2_L72_c160214.nc"

    ; ifile = "~/E3SM/init_scratch/cami_aquaplanet_ne64np4_L72_c190215.nc"
    ; ifile = "/global/cscratch1/sd/whannah/acme_scratch/init_files/cami_aquaplanet_ne32np4_L72_c190215.nc"
    ; ifile = "/global/cscratch1/sd/whannah/acme_scratch/init_files/cami_aquaplanet_ne30np4_L72_c190215.nc"


    fig_type = "x11"
    fig_file = "figs_init/chk.cami.v1"


    ;===========================================================================
    ;===========================================================================
    print(""+ifile)
    infile = addfile(ifile,"r")

    ; ncol = dimsizes(infile->grid_area)
    
    ;===========================================================================
    ; Check for missing values
    ;===========================================================================
    ; vars = getfilevarnames(infile)
    ; num_v = dimsizes(vars)
    ; do v = 0,num_v-1
    ;     print(""+vars(v))
    ;     X := infile->$vars(v)$
    ;     if isfloat(X).or.isdouble(X) then
    ;         if any(isnan_ieee(X)) then
    ;             print("  NaN found!!!!")
    ;         end if
    ;     end if
    ;     if any(ismissing(X)) then
    ;         print("  missing values!!!!")
    ;     end if
    ; end do
    ; exit
    ;===========================================================================
    ;===========================================================================

    var = "T"
    data = infile->$var$(0,{850},:)

    ; var = "PS"
    ; data = infile->$var$(0,:)

printMAMS(infile->T(0,{850},:))
printMAMS(infile->PS(0,:))
exit

    ; printVarSummary(infile->$var$)

    grid_center_lat = infile->lat
    grid_center_lon = infile->lon
    
    
    ;===========================================================================
    ;===========================================================================
    wks = gsn_open_wks(fig_type,fig_file)
    plot = new(1,graphic)

    res = setres_contour_fill_smalltxt()
    res@cnFillMode      = "RasterFill"
    ; res@cnFillMode      = "CellFill"
    ; res@cnFillPalette   = "WhiteBlueGreenYellowRed"
    ; res@cnFillPalette   = "OceanLakeLandSnow"
    ; res@cnFillPalette   = "gsdtol"

    ; res@cnLevelSelectionMode = "ExplicitLevels"
    ; res@cnLevels        := fspan(-1,1,39)

    ; res@mpProjection    = "Aitoff"
    ; res@mpProjection    = "Satellite"
    ; res@mpProjection    = "Stereographic"
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
    ; res@sfYCellBounds = grid_corner_lat ;(:n_pt_plot,:)
    ; res@sfXCellBounds = grid_corner_lon ;(:n_pt_plot,:)
        
    plot(0) = gsn_csm_contour_map(wks,data,res)

    gsn_panel(wks,plot,(/1,dimsizes(plot)/),False)
    trimPNG(fig_file)

    ;===========================================================================
    ;===========================================================================

end
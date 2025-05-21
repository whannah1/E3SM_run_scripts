; Walter Hannah - Lawrence Livermore National Lab
; Create new SCRIP file for plotting data on whole element, rather than the GLL grid
; v1 - derive grid only from scrip file - takes advantage of default scrip ordering
; v2 - derive grid only from scrip file - NOT WORKING
; v3 - derive grid from "latlon" file   - NOT A VIABLE OPTION - latlon file has issues with "GLLnodes" variable
load "$NCARG_ROOT/custom_functions.ncl"
begin
    
    setfileoption("nc", "Format", "64BitOffset")
    
    debug = False

    res = "ne8"

    idir = "~/E3SM/data_grid/"
    ifile = res+"np4_scrip.nc"

    odir = idir
    ofile = str_sub_str(ifile, res+"np4", res+"np1" )

    ;================================================================================
    ; Print setup info for reference
    ;================================================================================
    print("")
    print("  ifile : "+idir+ifile)
    print("  ofile : "+odir+ofile)
    print("")

    ;================================================================================
    ;================================================================================
    map_file = addfile("~/E3SM/data_grid/np4_to_pg1."+res+".v1.nc","r")

    element_area = map_file->element_area

    element_center_lat  = map_file->element_lat
    element_center_lon  = map_file->element_lon

    element_corner_lon = map_file->element_corner_lon
    element_corner_lat = map_file->element_corner_lat

    ;================================================================================
    ;================================================================================

    element_area@long_name = "area weights"
    element_area!0 = "grid_size"
    delete(element_area@coordinates)

    element_center_lat@units = "degrees"
    element_center_lat@long_name = "latitude"
    element_center_lat!0 = "grid_size"

    element_center_lon@units = "degrees"
    element_center_lon@long_name = "longitude"
    element_center_lon!0 = "grid_size"
    
    element_corner_lat@units = "degrees"
    element_corner_lat@long_name = "latitude"
    element_corner_lat!0 = "grid_size"
    element_corner_lat!1 = "grid_corners"

    element_corner_lon@units = "degrees"
    element_corner_lon@long_name = "longitude"
    element_corner_lon!0 = "grid_size"
    element_corner_lon!1 = "grid_corners"


    ; delete(element_corner_lat@bounds)
    ; delete(element_corner_lon@bounds)

    grid_dims = new(1,integer)
    grid_dims = (/1/)
    grid_dims!0 = "grid_rank"

    ncol = dimsizes(element_area)
    grid_imask = new(ncol,double)
    grid_imask(:) = 1
    grid_imask!0 = "grid_size"


    ;================================================================================
    ; Create output file
    ;================================================================================
    if .not.debug then
        if fileexists(odir+ofile) then system("rm "+odir+ofile) end if
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

    end if
    ;================================================================================
    ;================================================================================
end
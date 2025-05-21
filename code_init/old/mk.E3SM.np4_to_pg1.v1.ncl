; Create a file containing mapping information between np4 and pg1 grids
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 
    
    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if

    setfileoption("nc", "Format",  "64BitOffset")


    ; res = "ne4"
    res = "ne8" 
    ; res = "ne30" 

    
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/share/domains/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/share/domains/" end if
    ; idir = "~/E3SM/init_files/"
    idir = "~/E3SM/data_grid/"

    if res.eq."ne30" then domain_file_name = "domain.ocn.ne30np4_gx1v6_110217.nc" end if
    if res.eq."ne4"  then domain_file_name = "domain.ocn.ne4np4_oQU240.160614.nc" end if
    if res.eq."ne8"  then domain_file_name = "domain.ocn.ne8np4_oQU240.190305.nc" end if
    
    odir = "~/E3SM/data_grid/"
    ofile = "np4_to_pg1."+res+".v1.nc"

    print("")
    print("  ifile : "+idir+domain_file_name)
    print("  ofile : "+odir+ofile)
    print("")
    
;==================================================================================================
;==================================================================================================
    infile  = addfile(idir+domain_file_name,"r")
    lat_in  = infile->yc(0,:)
    lon_in  = infile->xc(0,:)
    area_in = infile->area(0,:)

    num_gll = dimsizes(area_in)
    ;------------------------------------------------------
    ; Set up GLL node groups
    ;------------------------------------------------------
    ;;; Note: the K-means method only works for ne4
    ; kopt = True
    ; kopt@iter = 200
    ; kopt@iseed = 2
    ; kmeans = kmeans_as136( conform_dims((/1,num_gll/),area_in,1) ,3,kopt)
    ; gll_middle_flag = kmeans@id.eq. ( maxind(kmeans(:,0))+1 )
    ; gll_corner_flag = kmeans@id.eq. ( minind(kmeans(:,0))+1 )

    if isStrSubset(res,"ne4")  then 
        gll_center_area_min = 0.018
        gll_corner_area_max = 0.003
    end if
    if isStrSubset(res,"ne8")  then 
        ; num_elm_center = 384
        gll_center_area_min = 0.004
        gll_corner_area_max = 0.0015
    end if
    if isStrSubset(res,"ne30")  then 
        gll_center_area_min = 0.0003 
        gll_corner_area_max = 0.0001
    end if

    gll_middle_flag = area_in.gt.gll_center_area_min
    gll_corner_flag = area_in.lt.gll_corner_area_max

    gll_middle_ind = ind(gll_middle_flag)
    gll_corner_ind = ind(gll_corner_flag)

    num_gll_middle = num(gll_middle_flag)
    num_gll_corner = num(gll_corner_flag)
    num_element = num_gll_middle/4

    gll_middle_lat = lat_in( gll_middle_ind )
    gll_middle_lon = lon_in( gll_middle_ind )

    gll_corner_lat = lat_in( gll_corner_ind )
    gll_corner_lon = lon_in( gll_corner_ind )

    ;------------------------------------------------------
    ; Create output and tmp variables
    ;------------------------------------------------------
    elm_center_lat = new(num_element,double)
    elm_center_lon = new(num_element,double)

    elm_corner_lat = new((/num_element,5/),double)
    elm_corner_lon = new((/num_element,5/),double)

    elm_gll_middle_ind = new((/num_element,4/),integer)
    elm_gll_middle_lat = new((/num_element,4/),double)
    elm_gll_middle_lon = new((/num_element,4/),double)

    gll_found = new(num_gll,logical)
    gll_found = False

    current_elem_ind = -1
    distances = new(num_gll_middle,double)

    elm_gll_corner_ind = new((/num_element,4/),integer)
    elm_gll_corner_lat = new((/num_element,4/),double)
    elm_gll_corner_lon = new((/num_element,4/),double)

    ;;; Extra stuff for finding edges 
    edge_cond = .not.gll_middle_flag.and..not.gll_corner_flag   ; just edges w/o corners
    nedge_per_elem = 8
    ; edge_cond = .not.gll_middle_flag                          ; includes edges + corners
    ; nedge_per_elem = 12

    gll_edge_ind = ind( edge_cond )
    gll_edge_lat = lat_in( gll_edge_ind )
    gll_edge_lon = lon_in( gll_edge_ind )
    elm_gll_edge_lat = new((/num_element,nedge_per_elem/),double)
    elm_gll_edge_lon = new((/num_element,nedge_per_elem/),double)
    elm_gll_edge_ind = new((/num_element,nedge_per_elem/),integer)

    ;+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ; Begin loop over GLL middle nodes
    ;+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    do m = 0,num_gll_middle-1
        if .not.gll_found( gll_middle_ind(m) ) then
            ;--------------------------------------------------
            ; increase element counter
            ;--------------------------------------------------
            current_elem_ind = current_elem_ind + 1
            ;--------------------------------------------------
            ; Calculate distance to all other GLL middle nodes
            ;--------------------------------------------------
            distances := calc_great_circle_distance( gll_middle_lat(m), gll_middle_lat(:), \
                                                     gll_middle_lon(m), gll_middle_lon(:) )
            ;--------------------------------------------------
            ; get permutation vector to sort by distance
            ;--------------------------------------------------
            p_vector := dim_pqsort(distances,1)
            ;--------------------------------------------------
            ; Use GLL middle nodes to define element center
            ;--------------------------------------------------
            current_middle_ind = gll_middle_ind( p_vector(0) + (/0,1,2,3/) )

            elm_gll_middle_ind(current_elem_ind,:) = current_middle_ind

            tmp_gll_lat := lat_in( current_middle_ind )
            tmp_gll_lon := lon_in( current_middle_ind )

            tmp_gll_lon = where((tmp_gll_lon-tmp_gll_lon(0)).gt. 180,tmp_gll_lon-360.,tmp_gll_lon)
            tmp_gll_lon = where((tmp_gll_lon-tmp_gll_lon(0)).lt.-180,tmp_gll_lon+360.,tmp_gll_lon)

            elm_gll_middle_lat(current_elem_ind,:) = tmp_gll_lat
            elm_gll_middle_lon(current_elem_ind,:) = tmp_gll_lon

            elm_center_lat(current_elem_ind) = avg( tmp_gll_lat )
            elm_center_lon(current_elem_ind) = avg( tmp_gll_lon )

            ;--------------------------------------------------
            ; Use GLL corner nodes to define element corners
            ;--------------------------------------------------
            distances := calc_great_circle_distance( elm_center_lat(current_elem_ind), gll_corner_lat(:), \
                                                     elm_center_lon(current_elem_ind), gll_corner_lon(:) )
            
            p_vector := dim_pqsort(distances,1)

            current_corner_ind = p_vector(0:3)

            tmp_gll_ind := gll_corner_ind( current_corner_ind )
            tmp_gll_lat := gll_corner_lat( current_corner_ind )
            tmp_gll_lon := gll_corner_lon( current_corner_ind )

            tmp_gll_lon = where( (tmp_gll_lon-elm_center_lon(current_elem_ind)).gt. 180 ,tmp_gll_lon-360.,tmp_gll_lon)
            tmp_gll_lon = where( (tmp_gll_lon-elm_center_lon(current_elem_ind)).lt.-180 ,tmp_gll_lon+360.,tmp_gll_lon)

            cond := abs(tmp_gll_lat).gt.89.999
            tmp_gll_lon := where(cond,avg(tmp_gll_lon(ind(.not.cond))),tmp_gll_lon)

            bearing := calc_great_circle_bearing( elm_center_lat(current_elem_ind) , tmp_gll_lat , \
                                                  elm_center_lon(current_elem_ind) , tmp_gll_lon   )

            bearing_p_vector := dim_pqsort( bearing ,1) 

            elm_gll_corner_ind(current_elem_ind,:3) = tmp_gll_ind( bearing_p_vector )
            elm_gll_corner_lat(current_elem_ind,:3) = tmp_gll_lat( bearing_p_vector )
            elm_gll_corner_lon(current_elem_ind,:3) = tmp_gll_lon( bearing_p_vector )

            elm_corner_lat(current_elem_ind,:3) = tmp_gll_lat( bearing_p_vector )
            elm_corner_lon(current_elem_ind,:3) = tmp_gll_lon( bearing_p_vector )

            elm_corner_lat(current_elem_ind,4) = elm_corner_lat(current_elem_ind,0)
            elm_corner_lon(current_elem_ind,4) = elm_corner_lon(current_elem_ind,0)

            ;--------------------------------------------------
            ; Finally find the GLL edge nodes
            ;--------------------------------------------------
            distances := calc_great_circle_distance( elm_center_lat(current_elem_ind), gll_edge_lat(:), \
                                                     elm_center_lon(current_elem_ind), gll_edge_lon(:) )
            
            p_vector := dim_pqsort(distances,1)

            current_edge_ind = p_vector(0:nedge_per_elem-1)

            tmp_gll_ind := gll_edge_ind( current_edge_ind )
            tmp_gll_lat := gll_edge_lat( current_edge_ind )
            tmp_gll_lon := gll_edge_lon( current_edge_ind )

            tmp_gll_lon = where( (tmp_gll_lon-elm_center_lon(current_elem_ind)).gt. 180 ,tmp_gll_lon-360.,tmp_gll_lon)
            tmp_gll_lon = where( (tmp_gll_lon-elm_center_lon(current_elem_ind)).lt.-180 ,tmp_gll_lon+360.,tmp_gll_lon)

            cond := abs(tmp_gll_lat).gt.89.999
            tmp_gll_lon := where(cond,avg(tmp_gll_lon(ind(.not.cond))),tmp_gll_lon)

            bearing := calc_great_circle_bearing( elm_center_lat(current_elem_ind) , tmp_gll_lat , \
                                                  elm_center_lon(current_elem_ind) , tmp_gll_lon   )

            bearing_p_vector := dim_pqsort( bearing ,1) 
            
            elm_gll_edge_ind(current_elem_ind,:) = tmp_gll_ind( bearing_p_vector )
            elm_gll_edge_lat(current_elem_ind,:) = tmp_gll_lat( bearing_p_vector )
            elm_gll_edge_lon(current_elem_ind,:) = tmp_gll_lon( bearing_p_vector )

            ;--------------------------------------------------
            ; Mark the current GLL center node as found
            ;--------------------------------------------------
            gll_found( current_middle_ind ) = True

            ; ;--------------------------------------------------
            ; ; Check that points are correct
            ; ;--------------------------------------------------
            ; ; Use the average of corner coordinates compared to 
            ; ; the centroid to determine if corners are correct.
            ; ; If there's a problem, plot the points
            ; lat_cen_diff = abs( avg(elm_corner_lat(current_elem_ind,:)) - elm_center_lat(current_elem_ind) )
            ; lon_cen_diff = abs( avg(elm_corner_lon(current_elem_ind,:)) - elm_center_lon(current_elem_ind) )
            ; ; if isStrSubset(res,"ne30") then cond := any( lat_cen_diff .ge. 0.5 ) .or. any( lon_cen_diff .ge. 1.0 ) end if
            ; ; if cond then
            ;     ; fmt_i = "%2.2i"
            ;     ; fmt_f = "%8.4F"
            ;     ; print( sprinti(fmt_i,current_elem_ind)+"   " \
            ;     ;       +sprintf(fmt_f,elm_center_lat(current_elem_ind))+"   " \
            ;     ;       +sprintf(fmt_f,elm_center_lon(current_elem_ind))+"   " \
            ;     ;       +"  :    " \
            ;     ;       +sprintf(fmt_f,elm_corner_lat(current_elem_ind,0:3))+"   " \
            ;     ;       +sprintf(fmt_f,elm_corner_lon(current_elem_ind,0:3))+"   " \
            ;     ;       +sprintf(fmt_f,lat_cen_diff)+"   " \
            ;     ;       +sprintf(fmt_f,lon_cen_diff)+"   " \
            ;     ;       )
            ;     ; print("")
            ;     ;********************************************************
            ;     ;********************************************************
            ;     ;;; Create some dummy data for coloring the grid
            ;     mod_val = 5 ; ne30
            ;     topo     := ispan(1,num_gll ,1)%mod_val
            ;     plat_center = elm_center_lat(current_elem_ind)
            ;     plon_center = elm_center_lon(current_elem_ind)
            ;     view_width = 30
            ;     ;;; specify the scrip file for the grid
            ;     infile  = addfile("~/Research/E3SM/data_grid/ne30np4_scrip.nc","r")
            ;     ;;; set up plot resources
            ;     wks = gsn_open_wks("x11","domain_test")
            ;     res := setres_contour_fill_smalltxt()
            ;     res@cnFillMode      = "CellFill"
            ;     res@cnLevelSelectionMode = "ExplicitLevels"
            ;     res@cnFillPalette   := "gscyclic"
            ;     res@cnLevels        := fspan(min(topo),max(topo),10)
            ;     ; res@mpProjection    = "Aitoff"
            ;     ; res@mpProjection    = "Satellite"
            ;     ; res@mpProjection    = "Stereographic"
            ;     res@mpLimitMode     = "LatLon"
            ;     res@mpMinLatF = plat_center - view_width/2.
            ;     res@mpMaxLatF = plat_center + view_width/2.
            ;     res@mpMinLonF = plon_center - view_width/2.
            ;     res@mpMaxLonF = plon_center + view_width/2.
            ;     res@sfXArray      = infile->grid_center_lat
            ;     res@sfYArray      = infile->grid_center_lon
            ;     res@sfXCellBounds = infile->grid_corner_lon
            ;     res@sfYCellBounds = infile->grid_corner_lat
            ;     ;;; Plot basic grid
            ;     plot = gsn_csm_contour_map(wks,topo,res) 
            ;     ;;; add markers for current point
            ;     e = current_elem_ind
            ;     dum_c = new(12,graphic)
            ;     mres = True
            ;     mres@gsMarkerIndex = 1
            ;     mres@gsMarkerSizeF = 0.03
            ;     mres@gsMarkerColor = "red"
            ;     dum_e = gsn_add_polymarker(wks,plot(0),elm_center_lon(e),elm_center_lat(e),mres)
            ;     mres@gsMarkerColor = "blue"
            ;     do c = 0,dimsizes(elm_corner_lat(e,:))-1
            ;         dum_c(c) = gsn_add_polymarker(wks,plot(0),elm_corner_lon(e,c),elm_corner_lat(e,c),mres)
            ;     end do
            ;     ;;; finalize plot
            ;     gsn_panel(wks,plot,(/1,dimsizes(plot)/),False)
            ;     ;********************************************************
            ;     ;********************************************************
            ;     exit
            ; ; end if
            ;--------------------------------------------------
            ;--------------------------------------------------
        end if ; .not.gll_found
        if current_elem_ind.eq.(num_element-1) then break end if
    end do ; m
    ;+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ;+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    ;;; Debugging printout
    ; do e = 0,10
    ;     print( e+"    "+ elm_center_lat(e) +"    "+ elm_center_lon(e) )
    ;     do c = 0,3
    ;         print( "        "+ elm_center_ind(e,c) +"    "+ elm_center_member_lat(e,c) +"    "+ elm_center_member_lon(e,c) )
    ;     end do
    ;     print("")
    ; end do


    ; grid_center_lat = elm_center_lat
    ; grid_center_lon = elm_center_lon
    
    ; grid_corner_lat = elm_corner_lat
    ; grid_corner_lon = elm_corner_lon

    ; grid_center_lat@long_name = "grid center latitude"
    ; grid_center_lon@long_name = "grid center longitude"

    ; grid_corner_lat@long_name = "grid corner latitude"
    ; grid_corner_lon@long_name = "grid corner longitude"

    ; printMAM(grid_center_lat)
    ; printMAM(grid_center_lon)
    ; printMAM(grid_corner_lat)
    ; printMAM(grid_corner_lon)
    ; print(grid_center_lat)
    ; exit

;==================================================================================================
; Calculate area of new grid
;==================================================================================================
    area = new(num_element,double)
    do e = 0,num_element-1
        clat := elm_corner_lat(e,:)
        clon := elm_corner_lon(e,:)
        ;;; use 2 triangles
        ; area1 = calc_sphereical_triangle_area( clat(0),clat(1),clat(2) ,clon(0),clon(1),clon(2) )
        ; area2 = calc_sphereical_triangle_area( clat(2),clat(3),clat(0) ,clon(2),clon(3),clon(0) )
        ; area1 = calc_sphereical_triangle_area( clat(0),clat(2),clat(1) ,clon(0),clon(2),clon(1) )
        ; area2 = calc_sphereical_triangle_area( clat(0),clat(2),clat(3) ,clon(0),clon(2),clon(3) )
        ; area(e) = area1 + area2
        ;;; use 4 trianglres if order of corners is uncertain
        area1 = calc_sphereical_triangle_area( clat(1),clat(2),clat(3) ,clon(1),clon(2),clon(3) )
        area2 = calc_sphereical_triangle_area( clat(2),clat(3),clat(0) ,clon(2),clon(3),clon(0) )
        area3 = calc_sphereical_triangle_area( clat(3),clat(0),clat(1) ,clon(3),clon(0),clon(1) )
        area4 = calc_sphereical_triangle_area( clat(0),clat(1),clat(2) ,clon(0),clon(1),clon(2) )
        area(e) = ( area1 + area2 + area3 + area4 )/2.
    end do ; e
    area@coordinates = "xc yc"
    area@long_name   = "area of element"
    area@units       = "radian^2"

    ;;; Check that areas sum to 4*pi
    ; printline()
    ; printMAMS(area)
    ; print("sum     : "+sum(area))
    ; print("4pi     : "+(4*pi) )
    ; print("sum/4pi : "+ ( sum(area)/(4.*pi) ) )
    ; printline()
    ; exit


;==================================================================================================
;==================================================================================================
    elm_gll_middle_ind!0 = "element"
    elm_gll_middle_ind!1 = "gll_middle"
    copy_VarCoords(elm_gll_middle_ind,elm_gll_middle_lat)
    copy_VarCoords(elm_gll_middle_ind,elm_gll_middle_lon)

    elm_gll_corner_ind!0 = "element"
    elm_gll_corner_ind!1 = "gll_corner"
    copy_VarCoords(elm_gll_corner_ind,elm_gll_corner_lat)
    copy_VarCoords(elm_gll_corner_ind,elm_gll_corner_lon)

    elm_gll_edge_ind!0 = "element"
    elm_gll_edge_ind!1 = "gll_edge"
    copy_VarCoords(elm_gll_edge_ind,elm_gll_edge_lat)
    copy_VarCoords(elm_gll_edge_ind,elm_gll_edge_lon)

    elm_corner_lat!0 = "element"
    elm_corner_lat!1 = "element_vertix"
    copy_VarCoords(elm_corner_lat,elm_corner_lon)

    
    if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
    outfile = addfile(odir+ofile,"c")

    ;;; GLL info from domain file
    outfile->gll_area = area_in
    outfile->gll_lat  = lat_in
    outfile->gll_lon  = lon_in

    ;;; Element info
    outfile->element_area = area
    outfile->element_lat  = elm_center_lat
    outfile->element_lon  = elm_center_lon
    ;;; Element corner info
    outfile->element_corner_lat = elm_corner_lat
    outfile->element_corner_lon = elm_corner_lon

    ;;; Middle GLL nodes
    outfile->elm_gll_middle_ind = elm_gll_middle_ind
    outfile->elm_gll_middle_lat = elm_gll_middle_lat
    outfile->elm_gll_middle_lon = elm_gll_middle_lon
    ;;; Corner GLL nodes
    outfile->elm_gll_corner_ind = elm_gll_corner_ind
    outfile->elm_gll_corner_lat = elm_gll_corner_lat
    outfile->elm_gll_corner_lon = elm_gll_corner_lon
    ;;; Edge GLL nodes
    outfile->elm_gll_edge_ind   = elm_gll_edge_ind
    outfile->elm_gll_edge_lat   = elm_gll_edge_lat
    outfile->elm_gll_edge_lon   = elm_gll_edge_lon
    
;==================================================================================================
;==================================================================================================
end
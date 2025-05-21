;==============================================================================
;==============================================================================
undef("convert_np4_To_np1")
procedure convert_np4_To_np1 (area_in, lat_in, lon_in)
local kmeans,kopt
begin
    
    num_gll = dimsizes(area_in)

    if dimsizes(num_gll).gt.1 then printExit("ERROR: convert_np4_To_np1: input area must be 1D") end if
    ;------------------------------------------------------
    ;------------------------------------------------------
    kopt = True
    kopt@iter = 20
    kopt@iseed = 2

    kmeans = kmeans_as136( conform_dims((/1,num_gll/),area_in,1) ,3,kopt)

    gll_middle_flag = kmeans@id.eq.1
    gll_corner_flag = kmeans@id.eq.3

    gll_middle_ind = ind(gll_middle_flag)
    gll_corner_ind = ind(gll_corner_flag)

    num_gll_middle = num(gll_middle_flag)
    num_gll_corner = num(gll_corner_flag)

    num_elm_center = num_gll_middle/4

    ;------------------------------------------------------
    ;------------------------------------------------------

    gll_middle_lat = lat_in(gll_middle_ind)
    gll_middle_lon = lon_in(gll_middle_ind)

    gll_corner_lat = lat_in(gll_corner_ind)
    gll_corner_lon = lon_in(gll_corner_ind)

    ;------------------------------------------------------
    ; Create output and tmp variables
    ;------------------------------------------------------

    elm_center_lat = new(num_elm_center,double)
    elm_center_lon = new(num_elm_center,double)

    elm_corner_lat = new((/num_elm_center,5/),double)
    elm_corner_lon = new((/num_elm_center,5/),double)

    nc = 4
    ; elm_center_member_ind = new((/num_elm_center,nc/),integer)
    ; elm_center_member_lat = new((/num_elm_center,nc/),double)
    ; elm_center_member_lon = new((/num_elm_center,nc/),double)

    gll_found = new(num_gll,logical)
    gll_found = False

    current_elem_ind = -1
    distances = new(num_gll_middle,double)

    ;+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ; Begin loop over GLL middle nodes
    ;+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    m1 = 0
    m2 = num_gll_middle-1

    do m = m1,m2
        if .not.gll_found( gll_middle_ind(m) ) then
            
            ;--------------------------------------------------
            ; increase element counter
            ;--------------------------------------------------
            current_elem_ind = current_elem_ind + 1

            ;--------------------------------------------------
            ; Calculate distance to all other GLL middle nodes
            ;--------------------------------------------------
            distances := calc_great_circle_distance( \
                                gll_middle_lat(m), gll_middle_lat(:), \
                                gll_middle_lon(m), gll_middle_lon(:) )

            ;--------------------------------------------------
            ; get permutation vector to sort by distance
            ;--------------------------------------------------
            p_vector := dim_pqsort(distances,1)
            
            ;--------------------------------------------------
            ; Use GLL middle nodes to define element center
            ;--------------------------------------------------

            current_middle_ind = gll_middle_ind( p_vector(0) + (/0,1,2,3/) )

            ; elm_center_member_ind(current_elem_ind,:) = current_middle_ind

            tmp_gll_lat := lat_in( current_middle_ind )
            tmp_gll_lon := lon_in( current_middle_ind )

            tmp_gll_lon = where((tmp_gll_lon-tmp_gll_lon(0)).gt. 180,tmp_gll_lon-360.,tmp_gll_lon)
            tmp_gll_lon = where((tmp_gll_lon-tmp_gll_lon(0)).lt.-180,tmp_gll_lon+360.,tmp_gll_lon)

            ; elm_center_member_lat(current_elem_ind,:) = tmp_gll_lat
            ; elm_center_member_lon(current_elem_ind,:) = tmp_gll_lon

            elm_center_lat(current_elem_ind) = avg( tmp_gll_lat )
            elm_center_lon(current_elem_ind) = avg( tmp_gll_lon )

            ;--------------------------------------------------
            ; Use GLL corner nodes to define element corners
            ;--------------------------------------------------
            distances := calc_great_circle_distance( \
                                elm_center_lat(current_elem_ind), gll_corner_lat(:), \
                                elm_center_lon(current_elem_ind), gll_corner_lon(:) )
            
            p_vector := dim_pqsort(distances,1)

            current_corner_ind = p_vector(0:3)

            tmp_gll_lat := gll_corner_lat( current_corner_ind )
            tmp_gll_lon := gll_corner_lon( current_corner_ind )

            tmp_gll_lon = where( (tmp_gll_lon-elm_center_lon(current_elem_ind)).gt. 180 ,tmp_gll_lon-360.,tmp_gll_lon)
            tmp_gll_lon = where( (tmp_gll_lon-elm_center_lon(current_elem_ind)).lt.-180 ,tmp_gll_lon+360.,tmp_gll_lon)

            cond := abs(tmp_gll_lat).gt.89.999
            tmp_gll_lon := where(cond,avg(tmp_gll_lon(ind(.not.cond))),tmp_gll_lon)

            bearing := calc_great_circle_bearing( \
                                elm_center_lat(current_elem_ind) , tmp_gll_lat , \
                                elm_center_lon(current_elem_ind) , tmp_gll_lon   )

            bearing_p_vector := dim_pqsort( bearing ,1) 

            elm_corner_lat(current_elem_ind,:3) = tmp_gll_lat( bearing_p_vector )
            elm_corner_lon(current_elem_ind,:3) = tmp_gll_lon( bearing_p_vector )

            elm_corner_lat(current_elem_ind,4) = elm_corner_lat(current_elem_ind,0)
            elm_corner_lon(current_elem_ind,4) = elm_corner_lon(current_elem_ind,0)

            ;--------------------------------------------------
            ; Mark GLL center nodes as found
            ;--------------------------------------------------

            gll_found( current_middle_ind ) = True

            ;--------------------------------------------------
            ;--------------------------------------------------

        end if ; .not.gll_found

        if current_elem_ind.eq.(num_elm_center-1) then break end if

    end do ; m
    ;+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ;+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    

    output = True
    
    output@elm_center_lat = elm_center_lat
    output@elm_center_lon = elm_center_lon
    ; output@elm_corner_lat = elm_corner_lat
    ; output@elm_corner_lon = elm_corner_lon

    return output

end
;==============================================================================
;==============================================================================
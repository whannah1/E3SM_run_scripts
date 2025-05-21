; This isn't realy "version 2", but rather "step 2" to create the aqua planet initialization.
; The "v1" script creates an extremely smoothed version of a standard E3SM input file 
; by smoothing on the native cube sphere grid using a pre-defined area of neighbors within a certain radius. 
; This is needed to deal with the change of topography, especially over the Himalayas.
; This initialization is then used for a "spin-up" run that has very large values for dycor
; tuning parameters, like the vertical remap frequency. That run will produce shocks fronts and 
; whatnot that need to be handled by the dycor to produce a new "cami" file that can be run without 
; special tuning. The purpose of this script is to take this new cami file and symmterize the 
; aerosol and chemistry fields, such as ozone. 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions_ACME.ncl"
begin 

    debug = False

    redo_neighbor_calc  = False
    test_stencil        = False

    ;idir = "~/Data/Model/CESM/inputdata/atm/cam/inic/fv/"
    ; idir = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/"
    idir = "~/E3SM/init_files/"
    odir = "~/E3SM/init_files/"

    ifile = idir+"E3SM_SP1_AQUA_ne30_64x1_4km_wp364_s2_00.cam.i.2000-01-02-36000.nc" 
    ofile = odir+"aqua_init.v2.nc"


    neighbor_file = "~/E3SM/init_files/zonal_band_neighbors.nc"

;=================================================================================================================
;=================================================================================================================
    re   = todouble( 6.37122e06 )               ; radius of earth
    rad  = todouble( 4.0 * atan(1.0) / 180. )   ; factor for converting to radians

    dlat_max = 5. 
    max_neighbors = 10000

    infile = addfile(ifile,"r")

    printline()

    lat  = infile->lat
    lon  = infile->lon
    area = infile->area

    ncol = dimsizes(lat)

    col_index = ispan(0,ncol-1,1)

    if debug then ncol = ncol/6/4 end if
    ;------------------------------------------------------------------------------
    ; Find neighbors within specified radius
    ;------------------------------------------------------------------------------
    if redo_neighbor_calc then 

        print("")
        print("Finding neighbors within symmetric zonal bands...")

        stencil_count := new(ncol,integer)
        stencil_index := new((/ncol,max_neighbors/),integer)

        ;--------------------------------------------------
        ; Find points in stencil to average
        ;--------------------------------------------------
        do i = 0,ncol-1

            ; dlat1 = abs( lat(:) - lat(i) ) * rad
            dlat2 = abs( abs(lat(:)) - abs(lat(i)) )
            
            ; tmp_index := col_index( ind( dlat1.lt.dlat_max .or. dlat2.lt.dlat_max  ) )
            tmp_index := col_index( ind( dlat2.lt.todouble(dlat_max) ) )

            num_s = dimsizes(tmp_index)

            if num_s.gt.max_neighbors then num_s = max_neighbors end if

            stencil_count(i) = num_s

            stencil_index(i,:stencil_count(i)-1) = tmp_index(:stencil_count(i)-1)

        end do

        print("done.")
        print("")
        ;--------------------------------------------------
        ;--------------------------------------------------

        stencil_index@long_name = "stencil indices"
        stencil_count@long_name = "stencil count"

        stencil_index!0 = "column"
        stencil_index!1 = "neighbors"
        stencil_index&column = col_index

        stencil_count!0 = "column"
        stencil_count&column = col_index

        ;--------------------------------------------------
        ;--------------------------------------------------
        print("writing to file: "+neighbor_file)

        if isfilepresent(neighbor_file) then system("rm "+neighbor_file) end if
        outfile = addfile(neighbor_file,"c")
        outfile->stencil_index  = stencil_index
        outfile->stencil_count  = stencil_count
        outfile->stencil_dlat_max = dlat_max
        print("")
    else
        stencil_file = addfile(neighbor_file,"r")
        stencil_index = stencil_file->stencil_index
        stencil_count = stencil_file->stencil_count
    end if

; print("")
; print("  Exiting!!!")
; print("")
; exit 

    ;------------------------------------------------------------------------------
    ; test the effect of the smoothing stencil
    ;------------------------------------------------------------------------------
    if test_stencil then
        infile = addfile(ifile,"r")
        
        ; tmp_in = infile->PS(0,:)
        tmp_in = infile->Q(0,72-1,:)

        tmp_out = tmp_in
        tmp := tmp_out
        do i = 0,ncol-1
            if stencil_count(i).gt.1 then
                vals := stencil_index(i,:stencil_count(i)-1)
                if .not.all(ismissing(vals)) then
                    wgt := area(vals) / sum( area(vals) )
                    tmp_out(i) = sum( tmp( vals ) * wgt ) 
                    ; tmp_out(i) = avg( tmp( vals ) )                     
                end if
            end if
        end do

        printline()
        printMAMS(tmp_in)
        printMAMS(tmp_out)
        
        fig_file = "aqua.init.v2.smoothing"
        wks = gsn_open_wks("x11",fig_file)
        plot = new(2,graphic)
            res = setres_contour_fill()
            res@sfXArray = lon
            res@sfYArray = lat

            mnmxint = nice_mnmxintvl( min(tmp_in), max(tmp_in), 21, False)
            res@cnLevelSelectionMode = "ManualLevels"
            res@cnMinLevelValF       = mnmxint(0)
            res@cnMaxLevelValF       = mnmxint(1)
            res@cnLevelSpacingF      = mnmxint(2)

        plot(0) = gsn_csm_contour_map_ce(wks,tmp_in ,res)
        plot(1) = gsn_csm_contour_map_ce(wks,tmp_out,res)

        gsn_panel(wks,plot,(/dimsizes(plot),1/),setres_panel())
        trimPNG(fig_file)

        exit

    end if
    ;------------------------------------------------------------------------------
    ;------------------------------------------------------------------------------

;=================================================================================================================
;=================================================================================================================
    
    infile = addfile(ifile,"r")
    
    vname = getfilevarnames(infile)

; print(vname)
; exit

    if isfilepresent(ofile) then system("rm "+ofile) end if
    outfile = addfile(ofile,"c")    

    do v = 0,dimsizes(vname)-1

        tmp_in := infile->$vname(v)$

        dims := dimsizes(tmp_in)
        ndim := dimsizes(dims)

        tmp_out := tmp_in

        ;------------------------------------------------------------------------------
        ;------------------------------------------------------------------------------
        if       vname(v).eq."O3"    \
            .or. vname(v).eq."SO2"   \
            .or. vname(v).eq."SOAG"  \
            .or. vname(v).eq."DMS"   \
            .or. vname(v).eq."H2O2"  \
            .or. vname(v).eq."H2SO4" \
            .or. isStrSubset(vname(v),"bc_")  \
            .or. isStrSubset(vname(v),"dst_") \
            .or. isStrSubset(vname(v),"mom_") \
            .or. isStrSubset(vname(v),"ncl_") \
            .or. isStrSubset(vname(v),"num_") \
            .or. isStrSubset(vname(v),"pom_") \
            .or. isStrSubset(vname(v),"so4_") \
            .or. isStrSubset(vname(v),"soa_") \
            then

            print("  "+strpad(vname(v),30)+" <<<<<<<")

            if isdim(tmp_in,"ncol").and.(ndim.ge.2) then
                tmp := tmp_out
                do i = 0,ncol-1
                    if stencil_count(i).gt.1 then
                        vals := stencil_index(i,:stencil_count(i)-1)
                        if .not.all(ismissing(vals)) then
                            ;;; use area weighting
                            wgt := area(vals) / sum( area(vals) )
                            if ndim.eq.2 then tmp_out(:,  i) = dim_sum_n( tmp(:,  vals) * conform(tmp_out(:,  vals),wgt,ndim-1) ,ndim-1) end if
                            if ndim.eq.3 then tmp_out(:,:,i) = dim_sum_n( tmp(:,:,vals) * conform(tmp_out(:,:,vals),wgt,ndim-1) ,ndim-1) end if
                        end if
                    end if
                end do ; i = 0,ncol-1
            end if

        else
            print("  "+strpad(vname(v),30)+"")
        end if
        ;------------------------------------------------------------------------------
        ;------------------------------------------------------------------------------
        
        outfile->$vname(v)$ = tmp_out

    end do

    printline()
    print("")
    print("    "+ofile)
    print("")

;=================================================================================================================
;=================================================================================================================

end
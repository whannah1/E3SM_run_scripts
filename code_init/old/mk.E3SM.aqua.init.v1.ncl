; Create an aqua planet input file that does not resemble a planet with topography
; to view output file, you can regrid with this command:
;    ncremap -m ~/maps/map_ne30np4_to_fv128x256_aave.20160301.nc -i ~/E3SM/init_files/aqua_init.v1.nc -o ~/E3SM/init_files/aqua_init.v1.remap.nc
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions_ACME.ncl"
begin 

    debug = False

    ;idir = "~/Data/Model/CESM/inputdata/atm/cam/inic/fv/"
    idir = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/"
    ; idir = "~/E3SM/init_files/"
    odir = "~/E3SM/init_files/"

    ifile = idir+"cami_mam3_Linoz_ne30np4_L72_c160214.nc" ; E3SM se dycore
    ofile = odir+"aqua_init.v1.nc"

ifile = odir+"aqua_init.v1.nc"
ofile = odir+"aqua_init.v1.xtra_smooth.nc"

    wgt_dir = "/ccs/home/hannah6/NCL/regrid_wgts/"

    nsmooth = 40
    radius  = 400.

    re   = todouble( 6.37122e06 )               ; radius of earth
    rad  = todouble( 4.0 * atan(1.0) / 180. )   ; factor for converting to radians

    max_neighbors = 100

    redo_neighbor_calc = False
    test_stencil       = False

    neighbor_file = "~/E3SM/init_files/neighbors.nc"

;=============================================================================
; Load CESM default SST input data
;=============================================================================
    infile = addfile(ifile,"r")

    printline()

    ; print(infile)
    ; exit

    lat  = infile->lat
    lon  = infile->lon
    area = infile->area

    ncol = dimsizes(area)

    col_index = ispan(0,ncol-1,1)

    if debug then ncol = ncol/6/4 end if

;=================================================================================================================
;=================================================================================================================

    ;------------------------------------------------------------------------------
    ; Find neighbors within specified radius
    ;------------------------------------------------------------------------------
    if redo_neighbor_calc then 

        print("")
        print("Finding nearest neighbors within a "+radius+" km radius...")

        stencil_count := new(ncol,integer)
        stencil_index := new((/ncol,max_neighbors/),integer)

        ;--------------------------------------------------
        ; Find points in stencil to average
        ;--------------------------------------------------
        do i = 0,ncol-1

            dlat = abs( lat(:) - lat(i) ) * rad
            dlon = abs( lon(:) - lon(i) ) * rad

            ;;; great circle distance formula from - https://en.wikipedia.org/wiki/Great-circle_distance
            ;;; D := re * 2.*asin( sqrt( (sin(dlat/2.))^2. + abs( cos(lat(i)) * cos(lat(:)) * (sin(dlon/2.))^2. ) ) )

            d2 = todouble( abs( cos(lat(i)*rad) * cos(lat(:)*rad) * (sin(dlon/2.))^2. ) )
            d1 = todouble( (sin(dlat/2.))^2. )
            D := sqrt( d1 + d2 )
            D = where(D.gt. 1., 1.,D)
            D = where(D.lt.-1.,-1.,D)
            D = re * 2.*asin( D ) 

            D = D / 1e3                 ; convert to km
            
            tmp_index := col_index( ind( D.lt.radius ) )

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
        outfile->stencil_radius = radius
        print("")
    else
        stencil_file = addfile(neighbor_file,"r")
        stencil_index = stencil_file->stencil_index
        stencil_count = stencil_file->stencil_count
    end if

    stencil_count@long_name = "stencil count"
    printMAMS(stencil_count)

    ;------------------------------------------------------------------------------
    ; test the effect of the smoothing stencil
    ;------------------------------------------------------------------------------
    if test_stencil then
        infile = addfile(ifile,"r")
        tmp_in = infile->PS(0,:)

        tmp_out = tmp_in
        do n = 0,nsmooth-1
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
        end do

        printline()
        printMAMS(tmp_in)
        printMAMS(tmp_out)
        
        fig_file = "aqua.init.smoothing"
        wks = gsn_open_wks("png",fig_file)
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
; Create outfile and populate with input data
;=================================================================================================================
    infile = addfile(ifile,"r")

    if isfilepresent(ofile) then system("rm "+ofile) end if
    outfile = addfile(ofile,"c")

    vname = getfilevarnames(infile)

    do v = 0,dimsizes(vname)-1

        print("  "+vname(v))

        tmp_in := infile->$vname(v)$

        dims := dimsizes(tmp_in)
        ndim := dimsizes(dims)

        ;------------------------------------------------------------------------------
        ; Smooth the field
        ;------------------------------------------------------------------------------
        tmp_out := tmp_in
        if isdim(tmp_in,"ncol").and.(ndim.ge.2) then
            do n = 0,nsmooth-1
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
            end do ; n = 0,nsmooth-1
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
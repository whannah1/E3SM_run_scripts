; Walter Hannah - Lawrence Livermore National Lab
; Create a modified initialization file (cami) for the ACME model
; v1 - zero out cloud ice to solve run-time error in ACME-SP
; v2 - modify temperature profile to remove unstable layers near the surface
; v3 - modify vertical grid - remove lowest levels
; load "$NCARG_ROOT/custom_functions.ncl"

; Calculate saturation specific humidity (kg/kg) from temperature (k) and pressure (mb)
undef("calc_Qsat")
function calc_Qsat (Ta,Pa)
local Ta,Pa,Tc,ew,qs
begin
    Tc = Ta - 273.
    ew = 6.1121*(1.0007+3.46e-6*Pa)*exp((17.502*Tc)/(240.97+Tc))          ; in mb
    qs = 0.62197*(ew/(Pa-0.378*ew))                                       ; mb -> kg/kg
    return qs
end

begin

    idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/"
    ; ifile = "cami_mam3_Linoz_ne30np4_L72_c160214.nc"
    ; ifile = "cami_mam3_Linoz_ne16np4_L72_c160614.nc"
    ifile = "cami_mam3_Linoz_ne4np4_L72_c160909.nc"

    ; odir  = "~/ACME/init_files/"
    odir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
    ofile = str_sub_str(ifile,".nc",".v2.nc")

;================================================================================
;================================================================================
    if isfilepresent(ofile) then system("rm "+ofile) end if
    ; if fileexists(ofile) then system("rm "+ofile) end if
    
    infile  = addfile(idir+ifile,"r")
    outfile = addfile(odir+ofile,"c")

    ; exit

    var = getfilevarnames(infile)
;================================================================================
;================================================================================
    ; printline()
    do v = 0,dimsizes(var)-1

        if isatt(infile->$var(v)$,"long_name") then 
            var_name = infile->$var(v)$@long_name 
        else
            var_name = ""
        end if

        ; print("  "+strpad(var(v),20) + "    " + var_name)

        V = infile->$var(v)$

        ; if var(v) .eq. "nbdate" then V = 20000101 end if
        ; if var(v) .eq. "ndcur"  then V = 000 end if
        ; if var(v) .eq. "date"   then V = 20000101 end if

        ;; zero out cloud ice near mode top
        ; if any(var(v) .eq. (/"CLDICE","NUMICE"/) ) then 
        ;     V(:,{:50},:) = 0.
        ; end if
        
        ; skip Q - see below
        if any(var(v) .eq. (/"Q"/) ) then 
            continue
        end if


        if any(var(v) .eq. (/"T"/) ) then 

            lon = infile->lon
            lat = infile->lat

            levsz = dimsizes(infile->lev)

            ; Adjust near surface temperature
            lon1 = 360-90
            lon2 = 360-60
            lat1 = -30
            lat2 = 0
            cond = (lon.ge.lon1).and.(lon.le.lon2).and.(lat.ge.lat1).and.(lat.le.lat2)
            vals = ind(cond)
            ; dVdz_2(:,levsz-2,vals) = avg(dVdz_2(:,levsz-2,vals))
            V2 = V

            do n = 0,2-1
                do kk = 1,1
                    V2(:,levsz-kk,vals) = ( V2(:,levsz-kk,vals) + V2(:,levsz-kk-1,vals) ) / 2.
                end do
            end do

            

            ; Load some other stuff
            
            ; load stuff for lapse rate calculation
            hyam = infile->hyam
            hybm = infile->hybm
            PS = infile->PS
            P0 = infile->P0

            T = V

            ; calculate pressure in Pa
            P = ( conform(V,hyam,1)*P0 + conform(V,hybm,1)*conform(V,PS,(/0,2/)) ) 

            ; Adjust RH 
            Q = infile->Q

            Qsat1 = calc_Qsat(V ,P/1e2)
            Qsat2 = calc_Qsat(V2,P/1e2)

            RH1 = Q / Qsat1
            RH2 = Q / Qsat2

            Q2 = RH1*Qsat2

            ; print("")
            ; print( avg(RH1) )
            ; print( max(RH1) )
            ; print("")
            ; print( avg(RH2) )
            ; print( max(RH2) )
            ; print("")
            ; print( min(RH1-RH2) )
            ; print( max(RH1-RH2) )
            ; exit

            Q_out = Q
            Q_out = (/ where( RH1.ne.RH2 , Q2, Q) /)

            outfile->Q = Q_out

            ; if False then

            ;     ; calculate Z (hydrostatic assumption)
            ;     R = P/(287.*T)
            ;     Z = new(dimsizes(T),double)
            ;     Z(:,levsz-1,:) = 0.
            ;     do k = levsz-2,0,1
            ;         dp = P(:,k,:) - P(:,k+1,:)
            ;         aR = ( R(:,k,:) + R(:,k+1,:) )/2.
            ;         dz = dp/(-aR*9.81)
            ;         Z(:,k,:) = Z(:,k+1,:) + ( dz )
            ;     end do

            ;     ; calculate lapse rate
            ;     zvals = ispan(0,levsz-1,1)      ;
            ;     Bvals = zvals(2:levsz-1)        ; Bottom Values
            ;     Zvals = zvals(1:levsz-2)        ; Center Values
            ;     Tvals = zvals(0:levsz-3)        ; Top Values

            ;     dZ   = new(dimsizes(T),double)
            ;     dVdz = new(dimsizes(T),double)
            ;     dVdz_2 = new(dimsizes(T),double)

            ;     dZ(:,Zvals,:)   = ( ( Z(:,Bvals,:)   + Z(:,Zvals,:)   )/2. - ( Z(:,Tvals,:)   + Z(:,Zvals,:)   )/2. )

            ;     dVdz(:,Zvals,:)   = ( ( V (:,Bvals,:)   + V (:,Zvals,:)   )/2. - ( V (:,Tvals,:)   + V (:,Zvals,:)   )/2. ) / dZ(:,Tvals,:) 

            ;     dVdz_2(:,Zvals,:) = ( ( V2(:,Bvals,:)   + V2(:,Zvals,:)   )/2. - ( V2(:,Tvals,:)   + V2(:,Zvals,:)   )/2. ) / dZ(:,Tvals,:) 

            ;     ; printMAM(dVdz)
            ;     ; vals := ind(dVdz(0,levsz-2,:).lt.-0.01)
            ;     ; print(vals)
            ;     ; print( lon(vals) +"    "+ lat(vals) )
            ;     ; exit

            ;     ; plot lapse rate
            ;     wks = gsn_open_wks("x11","lapse_rate")
            ;     plot = new(4,graphic)
            ;         res                     = setres_contour_fill()
            ;         res@sfXArray            = lon
            ;         res@sfYArray            = lat
            ;         res@cnLevelSelectionMode = "ExplicitLevels"
            ;         res@cnLevels = ispan(-2,10,2)*1e-2
            ;     ; plot = gsn_csm_contour_map_ce(wks,dVdz(0,levsz-2,:),res)
            ;     ; plot = gsn_csm_contour_map_ce(wks,T(0,levsz-2,:),res)
            ;     plot(0) = gsn_csm_contour_map_ce(wks,dVdz(0,levsz-2,:),res)
            ;     ; plot(1) = gsn_csm_contour_map_ce(wks,dVdz(0,levsz-3,:),res)
            ;     plot(2) = gsn_csm_contour_map_ce(wks,dVdz_2(0,levsz-2,:),res)
            ;     ; plot(3) = gsn_csm_contour_map_ce(wks,dVdz_2(0,levsz-3,:),res)
            ;         pres = setres_panel()
            ;         pres@gsnPanelYWhiteSpacePercent         = 5
            ;         gsn_panel(wks,plot,(/2,2/),pres)

            ;     exit
            ; end if

            V = V2

        end if
        
        outfile->$var(v)$ = V

        delete(V)

    end do
    ; printline()
;===========================================================================
;===========================================================================
    print("")
    print("  "+idir+ifile)
    print("  "+odir+ofile)
    print("")

;================================================================================
; regrid for viewing
;================================================================================
    
    mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv128x256_aave.20160301.nc"
    ofile2 = str_sub_str(ofile,".nc",".remap.nc")

    print("")
    print("ncremap  -m "+mfile+" -i  "+odir+ofile+" -o "+odir+ofile2)
    print("")
;================================================================================
;================================================================================

end
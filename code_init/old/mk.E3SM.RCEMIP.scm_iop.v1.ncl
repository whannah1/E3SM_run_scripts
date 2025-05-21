load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/cd_string.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
;===========================================================================
;===========================================================================
; This script creates a custom IOP file for use in the E3SM SCM
; The essential variables are:
;   bdate     Base date
;   time      Time after 0Z on base date
;   lev       pressure levels
;   lat       Latitude
;   lon       Longitude
;   phis      Surface geopotential
;   t         Temperature
;   divt      Horizontal T advective tendency
;   q         Specific humidity
;   divq      Horizontal Q advective tendency
;   ps        Surface pressure
;   omega     Vertical pressure velocity
;   u         U wind
;   v         V windspeed
;   usrf      U wind at surface
;   vsrf      V wind at surface
;   pt        Surface pressure tendency
;===========================================================================
;===========================================================================
begin

    days = 1000                      ; number of days to simulate
    
    tstep   = 30   *60              ; model time step in seconds
    tsz     = days *86400/tstep     ; number of time steps

    lat = 0.
    lon = 0.

    yr1 = 0000

    sst_case = ispan(295,305,5)

    ; nlev = 72

    ztop = 65e3 ; 65e3
    dz   = 100


    debug = False

;===========================================================================
; Specify Constants
;===========================================================================
    zt  = 15e3      ; m

    po      = 1014.8        ; hPa
    g       = 9.79764       ; m/s
    Rd      = 287.04        ; J / (kg K)
    
    G   = 0.0067            ; Lapse Rate [ K/m ]
    
    zq1 = 4e3               ; m
    zq2 = 7.5e3             ; m
    qt  = 10^-11            ; g/kg

    print("")
    print("  tstep  =   "+tstep+" sec    ("+(tstep/60.)+" min)")
    print("  tsz    =   "+tsz+  " steps  ("+(tsz*tstep/86400.)+" days)")
    print("")

;===========================================================================
;===========================================================================
do c = 0,dimsizes(sst_case)-1
    
    sst = sst_case(c)

    ofile = "~/E3SM/init_files/RCE_iopfile.SST_"+sst+"K.nc"

    ;===========================================================================
    ;===========================================================================
        ; if isfilepresent(ofile) then system("rm "+ofile) end if
        if fileexists(ofile) then system("rm "+ofile) end if
        outfile = addfile(ofile,"c")
    ;===========================================================================
    ; Setup time variables
    ;===========================================================================
        bdate       = yr1*1e4 + 0101
        bdate@units = "yyyymmdd"
        bdate!0     = "date"

        ;tsec       = new(floattoint(tsz),integer)  
        tsec        = 00+ispan(0,(tsz-1)*tstep,tstep)
        tsec!0      = "time"
        tsec@units  = "s"


        time = tsec / 86400.
        time!0         = "time"
        time@long_name = "time"
        time@units     = "days since "+yr1+"-01-01 00:00:00"
    ;===========================================================================
    ; Setup physical coordinate variables
    ;===========================================================================
        ;;; Longitude
        lon!0           = "lon"
        lon&lon         = lon
        lon@long_name   = "Longitude"
        lon@units       = "degrees_east"
        
        ;;; Latitude
        lat!0           = "lat"
        lat&lat         = lat
        lat@long_name   = "Latitude"
        lat@units       = "degrees_north"

        zlev = tofloat( ispan(0,toint(ztop),toint(dz)) )

        nlev = dimsizes(zlev)

        ; print("  nlev     =   "+nlev)
        ; print("")
    ;===========================================================================
    ; Temperature, Humidity, Pressure
    ;===========================================================================
        
        ;-----------------------------------------------------
        ; iterate upwards from the surface
        ;-----------------------------------------------------
        Tv = new(nlev,float)
        T  = new(nlev,float)
        q  = new(nlev,float)
        p  = new(nlev,float)

        if sst.eq.295 then qo = 12.00 end if ; g/kg
        if sst.eq.300 then qo = 18.65 end if ; g/kg
        if sst.eq.305 then qo = 24.00 end if ; g/kg
        ; qo = qo/1e3     ; convert to kg/kg

        To  = sst
        Tvo = To*( 1. + 0.608*qo/1e3 )
        Tvt = Tvo - G*zt

        pt = po * ( (Tvt) / Tvo )^(g/Rd/G)      ; hPa

        do k = 0,nlev-1
            z = zlev(k)
            l = nlev-1-k
            ; print("    k = "+k+"    l = "+l)
            ;--------------------------------
            ; Analytic humidity profile
            ;--------------------------------
            if z.le.zt
                q(k) = qo * exp(-1.*z/zq1) * exp(-1.*(z/zq2)^2.)
            else
                q(k) = qt
            end if
            ;--------------------------------
            ; Analytic temperature profile
            ;--------------------------------

            if z.le.zt
                Tv(k) = Tvo - G*z
            else
                Tv(k) = Tvt
            end if

            T(k) = Tv(k) / ( 1.0 + 0.608*q(k)/1e3 )
            ;--------------------------------
            ; Analytic pressure profile
            ;--------------------------------
            if z.le.zt
                p(k) = po * ( (Tvo - G*z) / Tvo )^(g/Rd/G)
            else
                
                p(k) = pt * exp( -1.*( (g*(z-zt))/(Rd*Tvt) ) )
            end if
            ;--------------------------------
            ;--------------------------------
        end do

        qsat = calc_Qsat(T,p) * 1e3
        RH = ( q / qsat ) *100.

        ;;; Limit stuff for plotting convenience
        qsat = where(p.le.10.,min(qsat),qsat)
        RH   = where(p.le.10.,min(RH)  ,RH)

        ;-----------------------------------------------------
        ; flip profiles if necessary
        ;-----------------------------------------------------
        ;T = T(:,::-1)
        ;q = q(:,::-1)

        ;-----------------------------------------------------
        ; Add coordinate information
        ;-----------------------------------------------------
        T@long_name = "Temperature"
        T@units     = "K"

        q@long_name = "Specific Humidity"
        q@units     = "g/kg"

        p@long_name = "Pressure"
        p@units     = "hPa"
        ;-----------------------------------------------------
        ; Print out formatted profiles
        ;-----------------------------------------------------
        if debug then
            fmt = "%8.2f"
            print("-----------------------------------------------")
            print("   z [km]         p [hPa]      T [K]        q [g/kg]     qsat [g/kg] ")
            print("   "+sprintf(fmt,zlev/1e3)+"     "+sprintf(fmt,p)+"     "+sprintf(fmt,T)+"    "+sprintf(fmt,q)+"    "+sprintf(fmt,qsat) )
            print("-----------------------------------------------")
        end if
        ;-----------------------------------------------------
        ; plot analytic profiles (only up to 20km)
        ;-----------------------------------------------------
        if debug then 
        
            wks = gsn_open_wks("x11","RCEMIP_analytic_profiles")
                res = setres_default()
                res@xyLineThicknessF  = 6.
                res@trYMaxF = 20

            plot = new(4,graphic)

            tlev = zlev/1e3

            res@gsnCenterString = "Temperature [K]"
            plot(0) = gsn_csm_xy(wks,T,tlev,res)

            res@gsnCenterString = "Specific Humidity [g/kg]"
            plot(1) = gsn_csm_xy(wks,(/q,qsat/),tlev,res)

            res@gsnCenterString = "Pressure [hPa]"
            plot(2) = gsn_csm_xy(wks,p,tlev,res)

            res@gsnCenterString = "Relative Humidity [%]"
            plot(3) = gsn_csm_xy(wks,RH,tlev,res)


            pres = setres_panel()
            pres@gsnPanelYWhiteSpacePercent = 5
            pres@gsnPanelBottom = 0.1

            ; gsn_panel(wks,plot,(/1,dimsizes(plot)/),pres)
            gsn_panel(wks,plot,(/2,2/),pres)

        end if

    if debug then exit end if
    ;===========================================================================
    ; Initalize data variables
    ;===========================================================================
        vdim_1d = (/tsz/)
        vdim_2d = (/tsz,nlev/)

        ;;; Basic Variables
        T_out   := new(vdim_2d,float)
        q_out   := new(vdim_2d,float)
        phis     = new(vdim_1d,float)
        ps       = new(vdim_1d,float)
        u        = new(vdim_2d,float)
        v        = new(vdim_2d,float)

        ;;; surface Variables
        Tg       = new(vdim_1d,float)
        Tsair    = new(vdim_1d,float)
        vsrf     = new(vdim_1d,float)
        usrf     = new(vdim_1d,float)
        omega    = new(vdim_2d,float)
        TS       = new(vdim_1d,float)
        TSOCN    = new(vdim_1d,float)
        TSICE    = new(vdim_1d,float)
        TSICERAD = new(vdim_1d,float)
        SICTHK   = new(vdim_1d,float)
        ICEFRAC  = new(vdim_1d,float)
        
        ;;; Tendency variables
        divt     = new(vdim_2d,float)
        divq     = new(vdim_2d,float)
        divs     = new(vdim_2d,float)
        dTdt     = new(vdim_2d,float)
        dqdt     = new(vdim_2d,float)
        dsdt     = new(vdim_2d,float)
        Ptend    = new(vdim_1d,float)
        lhflx    = new(vdim_1d,float)
        shflx    = new(vdim_1d,float)

        ;;; Radiation
        ; TOA_LWup = new(vdim_1d,float)
        ; TOA_SWdn = new(vdim_1d,float)
        ; TOA_ins  = new(vdim_1d,float)
        ; NDRsrf   = new(vdim_1d,float)

            
        ; dP = new(nlev,float)
        ; dP(0)  = 0.
        ; dP(1:) = lev(1:nlev-1) - lev(0:nlev-2)
    ;===========================================================================
    ; Copy analytic variables to output
    ;===========================================================================
        plev       := p*1e2
        T_out(:,:)  = conform(T_out,T,1)
        q_out(:,:)  = conform(q_out,q,1)

        ;;; convert q_out to kg/kg
        q_out = (/q_out/1e3/)

        ;;; Flip profiles for model
        plev  = (/ plev (  ::-1) /)
        T_out = (/ T_out(:,::-1) /)
        q_out = (/ q_out(:,::-1) /)

        plev@long_name = "Pressure"
        plev@units     = "Pa"

        T_out@long_name = "Temperature"
        T_out@units     = "K"

        q_out@long_name = "Specific Humidity"
        q_out@units     = "kg/kg"

        plev!0          = "lev" 
        plev&lev        = plev

        T_out!0         = "time"
        T_out!1         = "lev"
        T_out&time      = time
        T_out&lev       = plev
        copy_VarCoords(T_out,q_out)

    ;===========================================================================
    ; Set large-scale tendencies to 0.0 for RCE
    ;===========================================================================
        ;-----------------------------------------------------
        ; Large-scale divergence
        ;-----------------------------------------------------
        divt(:,:) = 0.
        divq(:,:) = 0.
        divs(:,:) = 0.
        divt@long_name  = "Horizontal T advective tendency"
        divq@long_name  = "Horizontal Q advective tendency"
        divs@long_name  = "Horizontal S advective tendency"
        divt@units = "K/s"
        divq@units = "kg/kg/s"
        divs@units = "K/s"
        ;-----------------------------------------------------
        ; Eulerian large-scale tendency (not that important)
        ;-----------------------------------------------------
        dTdt(:,:) = 0.
        dqdt(:,:) = 0.
        dsdt(:,:) = 0.
        dTdt@long_name = "dT/dt"
        dqdt@long_name = "dq/dt"
        dsdt@long_name = "ds/dt"
        dTdt@units = "K/s"
        dqdt@units = "kg/kg/s"
        dsdt@units = "K/s"
        ;-----------------------------------------------------
        ;-----------------------------------------------------
        copy_VarCoords(T_out,divt)
        copy_VarCoords(T_out,divs)
        copy_VarCoords(T_out,divq)
        copy_VarCoords(T_out,dTdt)
        copy_VarCoords(T_out,dqdt)
        copy_VarCoords(T_out,dsdt)
    ;===========================================================================
    ; Set other necessary variables
    ;===========================================================================
        ;-----------------------------------------------------
        ; Set Surface Pressure and geo. height
        ;-----------------------------------------------------
        ps(:) = 1014.8 *1e2
        ps@long_name  = "Surface Pressure"
        ps@units      = "Pa"

        ps!0          = "time"
        ps&time       = time
        
        phis(:)         = 0.
        phis@long_name  = "Surface geopotential"
        phis@units      = "m2/s2"  
        ;-----------------------------------------------------
        ; Set Omega
        ;-----------------------------------------------------
        omega(:,:) = 0.
        omega@long_name = "Vertical pressure velocity"
        omega@units     = "Pa/s"
        ;-----------------------------------------------------
        ; Set wind profile
        ;-----------------------------------------------------
        u(:,:) = 0.
        v(:,:) = 0.
        u@long_name = "U wind"
        u@units     = "m/s" 
        v@long_name = "U wind"
        v@units     = "m/s" 
        ;-----------------------------------------------------
        ; Set Pressure Tendency
        ;-----------------------------------------------------
        Ptend(:)  = 0.
        Ptend@long_name = "Surface pressure tendency"
        Ptend@units     = "Pa/s"
        ;-----------------------------------------------------
        ; Set surface fluxes (or set surface wind)
        ;-----------------------------------------------------
        ;lhflx(:) = 30.
        ;shflx(:) = 30.
        ;lhflx@long_name = "Surface latent heat flux"
        ;lhflx@units     = "W/m2"
        ;shflx@long_name = "Surface sensible heat flux"
        ;shflx@units     = "W/m2"   
        ;-----------------------------------------------------
        ; Set surface variables
        ;-----------------------------------------------------
        Tg(:)       = sst
        Tsair(:)    = sst
        TS(:)       = sst
        TSOCN(:)    = sst
        TSICE(:)    = 271.36
        TSICERAD(:) = 0.
        SICTHK(:)   = 0.
        ICEFRAC(:)  = 0.
        Tg@long_name    = "Ground temperature"
        Tg@units        = "K"
        Tsair@long_name = "Surface air temperature"
        Tsair@units     = "K"
        TS@long_name    = "Surface temperature"
        TS@units        = "K"
        TSOCN@long_name = "Ocean temperature"
        TSOCN@units     = "K"
        TSICE@long_name = "Surface Ice temperature"
        TSICE@units     = "K"
        TSICERAD@long_name = "Radiatively equivalent ice temperature"
        TSICERAD@units     = "K"
        SICTHK@long_name  = "Sea Ice Thickness"
        SICTHK@units      = "m"
        ICEFRAC@long_name = "Fraction of sfc area covered by sea-ice"
        ICEFRAC@units     = "fraction"
        ;-----------------------------------------------------
        ; Set surface wind (which control fluxes)
        ;-----------------------------------------------------
        usrf(:)   = 1.
        vsrf(:)   = 1.
        usrf@long_name  = "Surface U wind"
        usrf@units      = "m/s"
        vsrf@long_name  = "surface V wind"
        vsrf@units      = "m/s"
        ;-----------------------------------------------------
        ; Set radiation variables
        ;-----------------------------------------------------
        ; TOA_LWup(:)   = 260.
        ; TOA_SWdn(:)   = 100.
        ; TOA_ins(:)    = 300.
        ; NDRsrf(:)     = 80.
        ; TOA_LWup@long_name  = "TOA LW up"
        ; TOA_LWup@units      = "W/m2"
        ; TOA_SWdn@long_name  = "TOA SW down"
        ; TOA_SWdn@units      = "W/m2"
        ; TOA_ins@long_name   = "TOA insolation"
        ; TOA_ins@units       = "W/m2"
        ; NDRsrf@long_name    = "Net downwelling radiation at the surface"
        ; NDRsrf@units        = "W/m2"
        ;-----------------------------------------------------
        ;-----------------------------------------------------
        copy_VarCoords(T_out,omega)
        copy_VarCoords(T_out,u)
        copy_VarCoords(T_out,v)
        copy_VarCoords(ps,phis)
        copy_VarCoords(ps,Ptend)
        ;copy_VarCoords(ps,lhflx)
        ;copy_VarCoords(ps,shflx)    
        copy_VarCoords(ps,Tg   )
        copy_VarCoords(ps,Tsair)
        copy_VarCoords(ps,TS)
        copy_VarCoords(ps,TSOCN)
        copy_VarCoords(ps,TSICE)
        copy_VarCoords(ps,TSICERAD)
        copy_VarCoords(ps,TSICE)
        copy_VarCoords(ps,SICTHK)
        copy_VarCoords(ps,ICEFRAC)
        copy_VarCoords(ps,Ptend)
        copy_VarCoords(ps,usrf)
        copy_VarCoords(ps,vsrf)
        ; copy_VarCoords(ps,TOA_LWup)
        ; copy_VarCoords(ps,TOA_SWdn)
        ; copy_VarCoords(ps,TOA_ins)
        ; copy_VarCoords(ps,NDRsrf)

    ;===========================================================================
    ; Write data out to file (path set by ofile)
    ;===========================================================================
        ;-----------------------------------------------------
        ; Coordinates
        ;-----------------------------------------------------
        ; outfile->lev      = plev
        outfile->lat      = lat
        outfile->lon      = lon
        outfile->bdate    = bdate
        outfile->tsec     = tsec
        ;-----------------------------------------------------
        ; Basic variables
        ;-----------------------------------------------------
        outfile->T        = T_out
        outfile->q        = q_out

        outfile->phis     = phis
        outfile->Ps       = ps
        outfile->omega    = omega
        outfile->u        = u
        outfile->v        = v
        ;-----------------------------------------------------
        ; Surface variables
        ;-----------------------------------------------------
        outfile->Tg       = Tg
        outfile->Tsair    = Tsair
        outfile->TS       = TS
        outfile->TSOCN    = TSOCN
        outfile->TSICE    = TSICE
        outfile->TSICE    = TSICERAD
        outfile->SICTHK   = SICTHK
        outfile->ICEFRAC  = ICEFRAC
        outfile->usrf     = usrf
        outfile->vsrf     = vsrf
        ;-----------------------------------------------------
        ; Tendency variables
        ;-----------------------------------------------------
        outfile->Ptend    = Ptend
        outfile->divt     = divt
        outfile->divq     = divq
        ;outfile->divs    = divs
        ;outfile->dTdt    = dTdt
        ;outfile->dqdt    = dqdt
        ;outfile->dsdt    = dsdt
        ;outfile->lhflx   = lhflx
        ;outfile->shflx   = shflx
        ;-----------------------------------------------------
        ; Radiation
        ;-----------------------------------------------------
        ;outfile->TOA_LWup    = TOA_LWup
        ;outfile->TOA_SWdn    = TOA_SWdn
        ;outfile->TOA_ins     = TOA_ins
        ;outfile->NDRsrf      = NDRsrf
    ;===========================================================================
    ; Global attributes
    ;===========================================================================

        outfile@description = "RCE forcing file for E3SM SCM"
        outfile@author      = "Walter Hannah (LLNL)"
        outfile@date        = cd_string(now(),"%c %Y")

        outfile@nco_openmp_thread_number = 1

    ;===========================================================================
    ; use nccopy to convert to "classic" file option
    ;===========================================================================
        tfile = str_sub_str(ofile,".nc","_classic.nc")
        system("nccopy -k classic "+ofile+"  "+tfile)
        system("mv "+tfile+" "+ofile)
    ;===========================================================================
    ; Print output file path
    ;=========================================================================== 
        print("")
        print("   "+ofile)
;===========================================================================
;===========================================================================
end do
print("")
end

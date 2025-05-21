load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
; load "~/NCL/custom_functions.ncl"
begin
    
    ; case = "ACME_ZM_CTL_ne30_01"
    case = "ACME_SP2_CTL_ne30_02"

    ; idir = "scratch/"+case+"/run/"
    idir = "/lustre/atlas1/cli115/scratch/hannah6/"+case+"/run/"

    ; ifile = idir + case+".cam.h1.2000-01-28-00000.remap.nc"
    ifile = idir+case+".cam.h1.2000-01-01-00000.remap.nc"

    ; ofile = "lev.csv"

    xlat = (/  0, 60/)
    xlon = (/180,180/)


;========================================================================
;========================================================================

    infile = addfile(ifile,"r")

    ; print(infile)
    ; exit

    lat = infile->lat
    lon = infile->lon
    lev = infile->lev
    hyam = infile->hyam
    hybm = infile->hybm
    hyai = infile->hyai
    hybi = infile->hybi
    Po  = infile->P0
    Ps  = infile->PS(0,:,:)

    Z = infile->Z3(0,:,:,:)
    T = infile->T (0,:,:,:)
    Q = infile->Q (0,:,:,:)

    Tv = T*(1.+0.61*Q)

    P = pres_hybrid_ccm(Ps,Po,hyam,hybm)

    ; H = vinth2p(Z,hya,hyb,lev,Ps,1,Po,1,False)

    ; H = cz2ccm(Ps,Z,Tv,Po,hyam,hybm,hyai,hybi)

    P  = (/P /1e2/)
    Po = (/Po/1e2/)


    P!0 = "lev"
    P!1 = "lat"
    P!2 = "lon"
    P&lat = lat
    P&lon = lon


; print(avg( P))
; print(avg(Ps))
; print(avg(Po))
; exit
    
    H = P
    H@_FillValue = -999
    H = H@_FillValue

    nlat = dimsizes(lat)
    nlon = dimsizes(lon)
    nloc = dimsizes(xlat)
    nlev = dimsizes(lev)

    do n = 0,nloc-1
        j = xlat(n)
        i = xlon(n)

        tmp = vinth2p(Z(:,:,:),hyam,hybm,P(:,{j},{i}),Ps(:,:),2,Po,1,False)

        copy_VarCoords(P,tmp)

        H(:,{j},{i}) = tmp(:,{j},{i})

        delete(tmp)

    end do

    H!0 = "lev"
    H!1 = "lat"
    H!2 = "lon"
    H&lat = lat
    H&lon = lon

;========================================================================
;========================================================================
    

    cr = " "+inttochar(10) +" "

    fmt = "%8.1f"

    str = cr

    do k = 0,nlev-1
        str = str + sprinti("%2.2i",k+1)+"  ("+sprinti("%2.2i",nlev-k)+")"
        do n = 0,nloc-1
            j = xlat(n)
            i = xlon(n)

            if k.eq.nlev-1
                dzstr = "      "+"       "
                dpstr = "      "+"       "
            else
                dz = H(k,{j},{i}) - H(k+1,{j},{i})
                dp = P(k,{j},{i}) - P(k+1,{j},{i})

                dzstr = "     ("+sprintf("%6.1f",dz)+")"
                dpstr = "     ("+sprintf("%6.1f",dp)+")"
            end if
            
            str = str+"      "+sprintf(fmt, H(k,{j},{i}) )+dzstr
            str = str+"      "+sprintf(fmt, P(k,{j},{i}) )+dpstr


        end do
        str = str + cr
    end do

    print(str+"")

;========================================================================
;========================================================================
end
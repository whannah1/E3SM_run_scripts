;===============================================================================================================================================================
;    This script is used to automate subsetting of ACME output data
;    Jul, 2017  Walter Hannah       Lawrence Livermore National Lab
;===============================================================================================================================================================
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions.ncl"
begin
    
    ; scratch_dir = "/lustre/atlas1/cli115/scratch/hannah6/"      ; Titan
    scratch_dir = "/global/cscratch1/sd/whannah/"               ; NERSC

    case = "20161118.beta0.F20TRCOSP.ne30_ne30.edison"

    idir = "/global/cscratch1/sd/tang30/ACME_simulations/"+case+"/run/"

    odir = scratch_dir+case+"/"

    yr1 = 1997
    yr2 = 1999

    ; var = (/"time","lev","ncol","lat","lon","nbdate","TAUX","FSNS","FLNS","LHFLX","SHFLX"/)
    var = (/"lat","lon","date","nbdate","TS","PS","PSL","TAUX","FSNS","FLNS","LHFLX","SHFLX"/)


    overwrite = True
    ;---------------------------------------------------------------
    ;---------------------------------------------------------------
    year = ispan(yr1,yr2,1)

    num_y = dimsizes(year)
    num_v = dimsizes(var)
    
    files = systemfunc("ls -1 "+idir+"*cam.h0*")

    ; print(files)
    ; exit
    ;---------------------------------------------------------------
    ;---------------------------------------------------------------
    print("")
    do f = 0,dimsizes(files)-1
        do y = 0,num_y-1
            if isStrSubset(files(f),year(y)+"") then

                ifile = files(f)
                ofile = str_sub_str(ifile,idir,odir)

                if overwrite.and.fileexists(ofile) then system("rm "+ofile) end if
                
                infile = addfile(ifile,"r")
                outfile = addfile(ofile,"c")

                do v = 0,num_v-1
                    outfile->$var(v)$ = infile->$var(v)$
                end do

                print(""+ofile)

                ; exit

            end if
        end do
    end do
    print("")
    ;---------------------------------------------------------------
    ;---------------------------------------------------------------
end
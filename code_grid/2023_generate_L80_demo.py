import os, numpy as np, xarray as xr

p0 = 1000e2
ps = 1000e2

# flags for printing debugging/tuning info/lists
print_int_debug = False
print_mid_debug = False
print_L72_comparison = False

# nsmooth = 0

min_dz = 550 

# Set up terminal colors
class tcolor: ENDC,RED,GREEN,CYAN = '\033[0m','\033[31m','\033[32m','\033[36m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def main():

    refine          = True
    refine_method   = 'add'
    nsmooth         = 40

    stop_point = 4
    stop_point_iter = 5

    if stop_point==2:
        grid_name = f'L80_demo_{stop_point:02d}.{stop_point_iter:02d}'
    else:
        grid_name = f'L80_demo_{stop_point:02d}'

    #---------------------------------------------------------------------------
    # Load E3SM default L72 and convert to approx height 
    # to mimic main level generation script
    #---------------------------------------------------------------------------
    home = os.getenv('HOME')
    ds72 = xr.open_dataset(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc')
    am72, bm72 = ds72.hyam.values, ds72.hybm.values
    ai72, bi72 = ds72.hyai.values, ds72.hybi.values
    mlev72 = compute_pressure_from_hybrid_coef(am72,bm72)
    ilev72 = compute_pressure_from_hybrid_coef(ai72,bi72)

    ### rough estimate of height from pressure
    zlev = np.log(ilev72[::-1]/1e3) * -6740.
    
    ### define lower limit for smoothing
    limit_z_km = 10
    limit_k = (np.abs(zlev - limit_z_km*1e3)).argmin()

    dz = []
    for k in range(len(zlev)-1): dz.append(zlev[k+1]-zlev[k])
    # dz = np.array(dz)

    # for k in range(len(zlev)-1): print(f'k: {k:3d}   {zlev[k+1]}  {dz[k]}')
    # exit()
    
    ### old method to convert dk/dz list to dz/zlev
    # dk_list = [ 4, 4, 2,  4,  1,  2,  2,  2,  4,  6,  4, 14,  4,   2,   2,   6,   5,   4]
    # dz_list = [50,60,80,100,125,150,200,300,400,500,550,600,800,1000,1500,2000,2500,3000]
    # dz = []
    # if 'dz_list' in locals() and 'zlev' not in locals():
    #     zlev = np.zeros(np.sum(dk_list)+1)
    #     kk = 1
    #     for d,dk in enumerate(dk_list):
    #         for k in range(dk):
    #             zlev[kk] = zlev[kk-1] + dz_list[d]
    #             dz.append(dz_list[d])
    #             # print(f'{kk}  {zlev[kk]:10.1}  {dz_list[d]}')
    #             kk += 1

    #---------------------------------------------------------------------------
    # functions to help with refinement methods
    #---------------------------------------------------------------------------
    def is_monotonic(nz,dz):
        for k in range(nz-1):
            if dz[k+1]<dz[k] and np.absolute(dz[k+1]-dz[k])>1:
                return False
        return True
    def print_levs(zlev_new,zlev_old,dz_new,dz_old,refine_limit_k1,refine_limit_k2):
        print()
        for k in range(refine_limit_k1-2,len(zlev)-1): 
            msg1 = f'{zlev_old[k+1]:>8.2f}'
            msg2 = f'{zlev_new[k+1]:>8.2f}'
            if k<len(zlev):
                msg1 = msg1+f'{dz_old[k]:>10.2f}'
                msg2 = msg2+f'{dz_new[k]:>10.2f}'
            else:
                msg1 = msg1+' '*10
                msg2 = msg2+' '*10
            msg = f'k: {k:3d}      {msg1}       {msg2}'
            if k==refine_limit_k1: msg = msg + '  <<<<<<<<<<'
            if k==refine_limit_k2: msg = msg + '  <<<<<<<<<<'
            print(msg)
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    def refine_add(zlev_in,dz_in):
        zlev = zlev_in
        dz = dz_in
        #-----------------------------------------------------------------------
        if stop_point==0: return zlev
        #-----------------------------------------------------------------------
        ### only refine between specified limits
        refine_limit_z1,refine_limit_z2 = 10,45
        refine_limit_k1 = (np.abs(zlev - refine_limit_z1*1e3)).argmin()
        refine_limit_k2 = (np.abs(zlev - refine_limit_z2*1e3)).argmin()
        ### first pass - reset levels to min spacing
        for k in range(refine_limit_k1,refine_limit_k2): 
            # only refine if spacing is sufficiently large
            if dz[k] > min_dz:
                # put extra spacing into k+1 level to preserve grid height
                tmp_dz = dz[k] ; dz[k] = min_dz ; dz[k+1] = dz[k+1] + (tmp_dz-min_dz)
        #-----------------------------------------------------------------------
        if stop_point==1: 
            # recalculate zlev
            zlev = np.zeros(len(dz)+1)
            for k in range(1,len(dz)+1): zlev[k] = zlev[k-1]+dz[k-1]
            return zlev
        #-----------------------------------------------------------------------
        ### second pass - bisect levels until monotonic
        cnt = 0
        is_mono = is_monotonic(len(dz),dz)
        while not is_mono:
            # find level that violates monotonicity and bisect it
            for k in range(refine_limit_k1,refine_limit_k2+1): 
                if dz[k+1]<dz[k] and np.absolute(dz[k+1]-dz[k])>1:
                    dz_tmp = dz[k]/2
                    dz[k] = dz_tmp
                    dz.insert(k,dz_tmp)
            # recalculate zlev
            zlev = np.zeros(len(dz)+1)
            for k in range(1,len(dz)+1): zlev[k] = zlev[k-1]+dz[k-1]
            # redefine loop limits
            refine_limit_k1 = (np.abs(zlev - refine_limit_z1*1e3)).argmin()
            refine_limit_k2 = (np.abs(zlev - refine_limit_z2*1e3)).argmin()
            # recheck monotonicity
            is_mono = is_monotonic(len(dz),dz)
            cnt += 1
            print(f'  refine bisection count: {cnt}')
            if cnt>100: exit(f'exiting refinement due to iteration limit!  (cnt={cnt})')
            #-----------------------------------------------------------------------
            if stop_point==2: 
                if cnt==stop_point_iter: return zlev
            #-----------------------------------------------------------------------
        # print(f'len(dz): {len(dz)}')
        ### for L72 refinement make sure we have a round number
        if len(dz)==79:
            # find largest jump in dz and bisect it
            dzdz = np.zeros_like(dz)
            for k in range(1,len(dz)): dzdz[k] = np.absolute( dz[k] - dz[k-1])
            max_idx = np.where(dzdz == np.amax(dzdz))[0][0]
            print(f'max_idx: {max_idx}')
            dz_tmp = dz[max_idx]/2
            dz[max_idx] = dz_tmp
            dz.insert(max_idx,dz_tmp)
            # recalculate zlev
            zlev = np.zeros(len(dz)+1)
            for k in range(1,len(dz)+1): zlev[k] = zlev[k-1]+dz[k-1]
        #-----------------------------------------------------------------------
        if stop_point==3: return zlev
        #-----------------------------------------------------------------------
        ilev = np.exp( -1*zlev/(6740.) ) * 1000
        ilev = ilev[::-1]
        num_ilev = len(ilev)
        num_mlev = num_ilev-1
        dz_smoothed   = np.zeros(num_mlev)
        zlev_smoothed = np.copy(zlev)

        for s in range(nsmooth):
            zs_tmp = np.copy(zlev_smoothed)
            # for k in range(1,num_mlev): 
            for k in range(limit_k,num_mlev): # only smooth upper levels
            # for k in range(1,limit_k): # only smooth upper levels
                zlev_smoothed[k] = ( 0.25*zs_tmp[k-1] + 0.5*zs_tmp[k] + 0.25*zs_tmp[k+1] )
        
        for k in range(0,num_mlev): dz_smoothed[k] = zlev_smoothed[k+1] - zlev_smoothed[k]

        zlev = zlev_smoothed
        # dz = dz_smoothed
        #-----------------------------------------------------------------------
        return zlev
    #---------------------------------------------------------------------------
    # refinement method #1 - add levels
    #---------------------------------------------------------------------------
    zlev = refine_add(zlev,dz)

    # for k in range(len(zlev)-1): print(f'k: {k:3d}   {zlev[k+1]:6.2f}  {dz[k]:6.2f}')
    # exit()

    #---------------------------------------------------------------------------
    # use curve fit from climatology to get pressure from height
    #---------------------------------------------------------------------------
    ilev = np.exp( -1*zlev/(6740.) ) * 1000
    ilev = ilev[::-1]
    num_ilev = len(ilev)
    num_mlev = num_ilev-1

    #---------------------------------------------------------------------------
    # Generate hybrid vertical grid
    #---------------------------------------------------------------------------

    [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2)

    ### make sure bottom 3 levels are pure terrain following for L72
    if (num_ilev-1)==72:
        # for a,b in ai[-3:],bi[-3:]:
        for k in range(0,3):
            k2 = num_ilev-k-1
            if ai[k2]>0:
                bi[k2] = bi[k2] + ai[k2]
                ai[k2] = 0

    ### calculate mid-level hybrid coefficients
    am = np.empty(num_mlev)
    bm = np.empty(num_mlev)
    for k in range(num_mlev):
        am[k] = ( ai[k+1] + ai[k] )/2.
        bm[k] = ( bi[k+1] + bi[k] )/2.

    mlev = compute_pressure_from_hybrid_coef(am,bm)

    #---------------------------------------------------------------------------
    # Debug print statements
    #---------------------------------------------------------------------------

    ### print interface levels
    if print_int_debug:
        for k in range(num_ilev): 
            k2 = num_ilev-k-1
            # print(f'{k:3}  ({k2:3})    {ilev[k]:8.1f}    {ai[k]:5.3f}  {bi[k]:5.3f}')
            print(f'{k:02}  ({k2:02})    {ilev[k]:8.2f}    {zlev[k2]:8.1f}')


    ### print mid-level pressure and height
    if print_mid_debug:
        print(f'            pressure    height')
        for k in range(num_mlev): 
            k2 = num_mlev-k-1
            dz = zlev[k2+1] - zlev[k2] 
            zmid = ( zlev[k2+1] + zlev[k2] ) / 2.
            # dlev = mlev72[k] - mlev[k]
            # print(f'{k:3}  ({k2:3})    {mlev[k]:8.2f}    {am[k]:5.3f}  {bm[k]:5.3f}')
            print(f'{k:3}  ({k2:3})    {mlev[k]:8.2f}    {zmid:8.1f}     {dz:5.0f}')
            # print(f'{k:02}  ({k2:02})    {mlev[k]:8.2f}    {zmid:8.1f}    ')
        print()
    
    if print_int_debug or print_mid_debug:
        exit('Exiting before writing')

    #---------------------------------------------------------------------------
    ### compare with E3SM's L72
    #---------------------------------------------------------------------------
    # for k in range(num_mlev):
    #     k2 = num_mlev-k-1
    #     dz = zlev[k2+1] - zlev[k2] ; dlev = mlev72[k] - mlev[k]
    #     # print(f'{k:3}  ({k2:3})   {dz:8.1f}    {mlev[k]:8.2f}      {lev72[k]:8.2f}    {dlev:8.2f}')
    #     print(f'{k:3}  ({k2:3})     {am[k]:6.5f}  {am72[k]:6.5f}      {bm[k]:6.5f}  {bm72[k]:6.5f}')
    # print()
    if print_L72_comparison:
        for k in range(num_ilev): 
        # for k in range(20):
            k2 = num_ilev-k-1
            if k2<num_ilev-1:
                dz = zlev[k2+1] - zlev[k2] 
            else:
                dz = 0
            # dlev = ilev72[k] - ilev[k]
            # print(f'{k:3}  ({k2:3})   {dz:8.1f}    {ilev[k]:8.2f}      {ilev72[k]:8.2f}    {dlev:8.2f}')
            if k<num_ilev-1:
                dlev1 = ilev[k+1] - ilev[k]
                dlev2 = ilev72[k+1] - ilev72[k]
            else:
                dlev1,dlev2 = 0,0
            print(f'{k:3}      {ilev[k]:6.1f}  ({dlev1:4.1f})       {ilev72[k]:6.1f}  ({dlev2:4.1f})')
            # msg = f'{k:3}  ({k2:3})'
            # msg += f'         {ilev[k]:8.2f}  {ilev72[k]:8.2f}'
            # msg += f'         {ai[k]  :6.5f}  {ai72[k]  :6.5f}'
            # msg += f'         {bi[k]  :6.5f}  {bi72[k]  :6.5f}'
            # print(msg)
        # exit()
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    # ### print mid and interface levels
    # for k in range(num_mlev):
    #     k2 = num_mlev-k-1
    #     msg1 = f'{k:3}  ({k2:3})'
    #     msg2 = ' '*len(msg1)
    #     if k==0:
    #         ki = 0
    #         msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
    #         msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
    #         print(msg2)
    #     km = k
    #     ki = k+1
    #     msg1 = f'{k:3}  ({k2:3})'
    #     msg2 = ' '*len(msg1)
    #     msg1 = msg1 +' '*4+      f'{mlev[km]:8.2f}          {am[km]:8.5f}        {bm[km]:8.5f}'
    #     msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
    #     msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
    #     print(msg1)
    #     print(msg2)
    # # exit()

    #---------------------------------------------------------------------------
    # Write to file
    #---------------------------------------------------------------------------
    if 'grid_name' not in locals(): exit('grid_name not defined!')

    ofile = os.getenv('HOME')+f'/E3SM/vert_grid_files/{grid_name}.nc'
    
    mlev = xr.DataArray(mlev)
    ilev = xr.DataArray(ilev)

    ds = xr.Dataset()
    ds['lev']  = ('lev', mlev.data)
    ds['hyam'] = ('lev', am)
    ds['hybm'] = ('lev', bm)
    ds['ilev'] = ('ilev',ilev.data)
    ds['hyai'] = ('ilev',ai)
    ds['hybi'] = ('ilev',bi)
    ds['P0'] = p0

    ds['lev'].attrs['units']      = 'level'
    ds['lev'].attrs['positive']   = 'down'
    ds['ilev'].attrs['units']     = 'level'
    ds['ilev'].attrs['positive']  = 'down'
    ds['P0'].attrs['units']       = 'Pa'
    ds['P0'].attrs['long_name']   = 'reference pressure'
    ds['hyam'].attrs['long_name'] = 'hybrid A coefficient at layer midpoints'
    ds['hybm'].attrs['long_name'] = 'hybrid B coefficient at layer midpoints'
    ds['hyai'].attrs['long_name'] = 'hybrid A coefficient at layer interfaces'
    ds['hybi'].attrs['long_name'] = 'hybrid B coefficient at layer interfaces'
    
    print(f'\n{ofile}\n')

    ds.to_netcdf(ofile)

    print(f'\n{ofile}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def compute_hybrid_coef_from_pressure(plev):
    """ 
    compute hybrid coefficients from pressure levels 
    """
    pm = 18230.50  # level to switch from sigma to pressure? [pa]
    pt = 100.0     # top pressure? [pa]

    psize = len(plev)
    a = np.empty(psize)
    b = np.empty(psize)

    for i in range(psize) :
        # compute sigma
        if plev[i]<pm:
            sigma = ( plev[i] - pm ) / ( pm - pt )
        else:
            sigma = ( plev[i] - pm ) / ( ps - pm )
        # compute delta
        delta = 0.0 if sigma<0.0 else 1.0
        # compute A and B, pressure coefficients
        a[i] = ( pm*(1-sigma)*delta + (1-delta)*(pm*(1+sigma)-sigma*pt) ) / p0
        b[i] = np.abs( sigma*delta )

    return [a,b]
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def compute_pressure_from_hybrid_coef(a,b):
    """
    compute pressure from hybrid coefficients
    """
    lev = ( a*p0 + b*ps ) / 100.0
    return lev
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
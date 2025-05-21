import os, numpy as np, xarray as xr

p0 = 1000e2
ps = 1000e2

# Set up terminal colors
class tcolor: ENDC,RED,GREEN,CYAN = '\033[0m','\033[31m','\033[32m','\033[36m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def main():

    #---------------------------------------------------------------------------
    # simple recipe using a list of height thicknesses
    #---------------------------------------------------------------------------
    grid_name = 'L60'
    num_smooth = 20
    dk_list = [ 12,  8,  8,  8,  8,  8,  8]
    dz_list = [100,200,400,500,1000,2e3,4e3]

    #---------------------------------------------------------------------------
    # Turn dk_list and dz_list into arrays of dz and z
    #---------------------------------------------------------------------------
    dz,zlev = [],np.zeros(np.sum(dk_list)+1)
    kk = 1
    for d,dk in enumerate(dk_list):
        for k in range(dk):
            zlev[kk] = zlev[kk-1] + dz_list[d]
            dz.append(dz_list[d])
            kk += 1
    
    #---------------------------------------------------------------------------
    # use curve fit from climatology to get pressure from height
    #---------------------------------------------------------------------------
    ilev = np.exp( -1*zlev/(6740.) ) * 1000

    ilev = ilev[::-1]
    num_ilev = len(ilev)
    num_mlev = num_ilev-1

    #---------------------------------------------------------------------------
    # Smoothing
    #---------------------------------------------------------------------------
    dz_smoothed   = np.zeros(num_mlev)
    zlev_smoothed = np.copy(zlev)

    for s in range(num_smooth):
        zs_tmp = np.copy(zlev_smoothed)
        for k in range(1,num_mlev): 
            zlev_smoothed[k] = ( 0.25*zs_tmp[k-1] + 0.5*zs_tmp[k] + 0.25*zs_tmp[k+1] )
    
    for k in range(0,num_mlev): dz_smoothed[k] = zlev_smoothed[k+1] - zlev_smoothed[k]

    zlev = zlev_smoothed
    ilev = np.exp( -1*zlev/(6740.) ) * 1000
    ilev = ilev[::-1]

    #---------------------------------------------------------------------------
    # Generate hybrid vertical grid
    #---------------------------------------------------------------------------
    [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2)

    ### calculate mid-level hybrid coefficients
    am = np.empty(num_mlev)
    bm = np.empty(num_mlev)
    for k in range(num_mlev):
        am[k] = ( ai[k+1] + ai[k] )/2.
        bm[k] = ( bi[k+1] + bi[k] )/2.

    mlev = compute_pressure_from_hybrid_coef(am,bm)

    #---------------------------------------------------------------------------
    # useful print statements for debugging
    #---------------------------------------------------------------------------

    ### print interface levels
    # for k in range(num_ilev): 
    #     k2 = num_ilev-k-1
    #     # print(f'{k:3}  ({k2:3})    {ilev[k]:8.1f}    {ai[k]:5.3f}  {bi[k]:5.3f}')
    #     print(f'{k:02}  ({k2:02})    {ilev[k]:8.1f}    {zlev[k2]:8.1f}')
    # exit()

    ### print mid-level pressure and height
    print(f'            pressure    height')
    for k in range(num_mlev): 
        k2 = num_mlev-k-1
        dz = zlev[k2+1] - zlev[k2] 
        zmid = ( zlev[k2+1] + zlev[k2] ) / 2.
        print(f'{k:02}  ({k2:02})    {mlev[k]:8.1f}    {zmid:8.1f}    ')
    print()
    exit()

    ### print mid and interface levels
    for k in range(num_mlev):
        k2 = num_mlev-k-1
        msg1 = f'{k:3}  ({k2:3})'
        msg2 = ' '*len(msg1)
        if k==0:
            ki = 0
            msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
            msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
            print(msg2)
        km = k
        ki = k+1
        msg1 = f'{k:3}  ({k2:3})'
        msg2 = ' '*len(msg1)
        msg1 = msg1 +' '*4+      f'{mlev[km]:8.2f}          {am[km]:8.5f}        {bm[km]:8.5f}'
        msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
        msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
        print(msg1)
        print(msg2)
    # exit()

    #---------------------------------------------------------------------------
    # Write to file
    #---------------------------------------------------------------------------
    if 'grid_name' not in locals(): grid_name = f'L{num_mlev}'

    ofile = os.getenv('HOME')+f'/E3SM/vert_grid_files/{grid_name}.nc'

    mlev = xr.DataArray(mlev)
    ilev = xr.DataArray(ilev)

    ds = xr.Dataset()
    ds['lev']  = ('lev', mlev)
    ds['hyam'] = ('lev', am)
    ds['hybm'] = ('lev', bm)
    ds['ilev'] = ('ilev',ilev)
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

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def compute_hybrid_coef_from_pressure(plev):
    """ 
    compute hybrid coefficients from pressure levels 
    """
    pm = 18230.50  # level to switch from sigma to pressure? [pa]
    pt = 100.0     # top pressure? [pa]

    psize = len(plev)
    a,b = np.empty(psize),np.empty(psize)

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
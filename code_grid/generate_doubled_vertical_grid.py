import os, numpy as np, xarray as xr
home = os.getenv('HOME')
p0 = 1000e2
ps = 1000e2

# Set up terminal colors
class tcolor: ENDC,RED,GREEN,CYAN = '\033[0m','\033[31m','\033[32m','\033[36m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def main():

    ifile = f'{home}/E3SM/vert_grid_files/UP_L125.nc'
    ofile = f'{home}/E3SM/vert_grid_files/UP_L250.nc'

    #---------------------------------------------------------------------------
    # Load starting grid to be doubled
    #---------------------------------------------------------------------------
    ds_in = xr.open_dataset(ifile)
    am_in, bm_in = ds_in.hyam.values, ds_in.hybm.values
    ai_in, bi_in = ds_in.hyai.values, ds_in.hybi.values
    mlev_in = compute_pressure_from_hybrid_coef(am_in,bm_in)
    ilev_in = compute_pressure_from_hybrid_coef(ai_in,bi_in)
    
    num_ilev_in  = len(ai_in)

    #---------------------------------------------------------------------------
    # Generate new grid by inserting new interfaces at each mid level
    #---------------------------------------------------------------------------    
    num_ilev = num_ilev_in*2-1
    num_mlev = num_ilev-1

    ai, bi = np.zeros(num_ilev),np.ones(num_ilev)
    am, bm = np.zeros(num_mlev),np.ones(num_mlev)

    for k in range(num_ilev-1):
        if (k%2)==0: kk = int(k/2);     atmp, btmp = ai_in[kk], bi_in[kk]
        if (k%2)!=0: kk = int((k-1)/2); atmp, btmp = am_in[kk], bm_in[kk]
        if (k%2)!=0:
            kk = int((k-1)/2)
            atmp = ( ai_in[kk+1] + ai_in[kk] )/2.
            btmp = ( bi_in[kk+1] + bi_in[kk] )/2.
        # print(f' {k:3}  {kk:3}  {atmp:8.4f}  {btmp:8.4f}     {bi_in[kk]:8.4f}  {bm_in[kk]:8.4f}')
        ai[k], bi[k] = atmp, btmp
    
    # exit()
    
    ilev = compute_pressure_from_hybrid_coef(ai,bi)

    #---------------------------------------------------------------------------
    # calculate mid-level hybrid coefficients
    #---------------------------------------------------------------------------
    for k in range(num_mlev):
        am[k] = ( ai[k+1] + ai[k] )/2.
        bm[k] = ( bi[k+1] + bi[k] )/2.

    mlev = compute_pressure_from_hybrid_coef(am,bm)

    #---------------------------------------------------------------------------
    # print level pressures
    #---------------------------------------------------------------------------

    # # print mid-levels
    # for k in range(num_mlev): 
    #     k2 = num_mlev-k-1
    #     print(f'{k:3}  ({k2:3})    {mlev[k]:8.1f}    {am[k]:5.3f}  {bm[k]:5.3f}')

    # # print interface levels
    # for k in range(num_ilev): 
    #     k2 = num_ilev-k-1
    #     print(f'{k:3}  ({k2:3})    {ilev[k]:8.1f}    {ai[k]:5.3f}  {bi[k]:5.3f}')

    # exit()

    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

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

    print(f'\n{ofile}\n')

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
from time import perf_counter
timer_start = perf_counter()
import os, numpy as np, xarray as xr, cmocean
import cartopy.crs as ccrs, matplotlib.pyplot as plt, matplotlib.colors as mcolors
from scipy.spatial import cKDTree
import hapy
xr.set_options(use_new_combine_kwarg_defaults=True)
#-------------------------------------------------------------------------------
# plot variables from one or more E3SM domain files
#-------------------------------------------------------------------------------
file_list,file_name = [],[]
def add_file(file_in,n=None):
    file_list.append(file_in)
    file_name.append(os.path.basename(file_in).replace('.nc','') if n is None else n)
#-------------------------------------------------------------------------------
# tmp_path = '/lustre/orion/cli115/world-shared/e3sm/2026-INCITE-CONUS-RRM/files_domain'

# add_file(f'{tmp_path}/domain.lnd.conus-1024x2-pg2_RRSwISC6to18E3r5.20260721.mask-version.nc', n='20260721.mask-version')
# add_file(f'{tmp_path}/domain.lnd.conus-1024x2-pg2_RRSwISC6to18E3r5.20260618.nc',              n='20260618')

# add_file(f'{tmp_path}/domain.ocn.conus-1024x2-pg2_RRSwISC6to18E3r5.20260721.mask-version.nc', n='20260721.mask-version')
# add_file(f'{tmp_path}/domain.ocn.conus-1024x2-pg2_RRSwISC6to18E3r5.20260618.nc',              n='20260618')

DIN_LOC_ROOT = '/lustre/orion/cli115/world-shared/e3sm/inputdata'
DIN_LOC_ROOT = '/global/cfs/cdirs/e3sm/inputdata'
data_root = f'{DIN_LOC_ROOT}/share/domains'
add_file(f'{data_root}/domain.ocn.RRSwISC6to18E3r5.240328.nc',n='RRSwISC6to18E3r5 old')

# add_file(f'{data_root}/domain.ocn.oEC60to30v3.161222.nc',n='oEC60to30v3')

data_root = '/global/cfs/cdirs/e3sm/2026-INCITE-CONUS-RRM/files_domain'
add_file(f'{data_root}/domain.ocn.RRSwISC6to18E3r5.20260610.nc',n='RRSwISC6to18E3r5 new')

# tmp_path = '/lustre/orion/cli115/world-shared/e3sm/2026-INCITE-CONUS-RRM/files_domain'
# add_file(f'{tmp_path}/domain.ocn.RRSwISC6to18E3r5.20260618.nc',n='RRSwISC6to18E3r5')

#-------------------------------------------------------------------------------
fig_file = 'figs_grid/plot.domain.png'

#-------------------------------------------------------------------------------
var,var_str = [],[]
var_opts_list = []
def add_var(var_name,s=None,**kwargs):
    var.append(var_name)
    var_str.append(var_name if s is None else s)
    var_opts = {}
    for k, val in kwargs.items(): var_opts[k] = val
    var_opts_list.append(var_opts)
#-------------------------------------------------------------------------------
# available kwargs:  cmap / clev / vmin / vmax / scale
#-------------------------------------------------------------------------------

add_var('mask', s='domain mask',            cmap='viridis')
add_var('frac', s='active fraction',        cmap='viridis', vmin=0, vmax=1)
# add_var('area', s='cell area [km$^2$]',     cmap=cmocean.cm.thermal, scale=(6.37122e3)**2)

# add_var('xc', s='longitude [deg]')
# add_var('yc', s='latitude [deg]')

#-------------------------------------------------------------------------------
# layout - num_plot_col only applies when a single file is used,
#          otherwise var_x_file controls the panel arrangement
num_plot_col = 1
var_x_file   = False

print_stats  = True

# resolution of the rasterized image (>1 is finer but slower)
#   NOTE - this only affects the pixel lookup, which is a tiny part of the cost
#   for large grids, so turning it down does not make things much faster
pixel_ratio  = 1.0

# blank out pixels whose nearest column center is farther than this many degrees
# - only useful for a regional grid that does not cover the plotted region,
#   set to None for global grids (i.e. all normal domain files)
max_fill_dist = None

# map region - set to None for a global map
plot_extent = None
# plot_extent = [-130,-60,20,55]   # CONUS  [lon1,lon2,lat1,lat2]

#-------------------------------------------------------------------------------
# Set up plot resources
if file_list==[]: raise ValueError('ERROR - file list is empty!')
if var==[]      : raise ValueError('ERROR - var list is empty!')
num_var,num_file = len(var),len(file_list)

if num_file==1:
    num_plot_row = int(np.ceil(num_var/num_plot_col))
    num_plot_col_use = num_plot_col
else:
    (num_plot_row,num_plot_col_use) = (num_var,num_file) if var_x_file else (num_file,num_var)

def get_ax(v,f):
    """return the axes for a given var/file index based on the layout"""
    if num_file==1: return axs[v//num_plot_col_use, v%num_plot_col_use]
    return axs[v,f] if var_x_file else axs[f,v]

#-------------------------------------------------------------------------------
subplot_kwargs = {}
subplot_kwargs['projection'] = ccrs.PlateCarree()
# subplot_kwargs['projection'] = ccrs.PlateCarree(central_longitude=180)
# subplot_kwargs['projection'] = ccrs.Orthographic(central_latitude=-85)

fdx,fdy = 10,5
figsize = (fdx*num_plot_col_use,fdy*num_plot_row)
title_fontsize,lable_fontsize = 20,18

fig, axs = plt.subplots(num_plot_row, num_plot_col_use, subplot_kw=subplot_kwargs,
                        figsize=figsize, squeeze=False)

#-------------------------------------------------------------------------------
# load the domain files and reshape onto a single unstructured column dimension
#   NOTE - do not use ds.stack() here! for these grids nj=1 and ni=31.6M, so
#   stack() builds a 31.6M-entry MultiIndex and reindexes every variable
#   (including the 4x larger xv/yv vertices) before reset_index throws it away
#   - that costs ~8 sec and ~4 GB per file vs ~1 sec for isel below
ds_list = []
for f in range(num_file):
    hapy.print_line()
    print(' '*2+'file: '+hapy.tclr.GREEN+file_list[f]+hapy.tclr.END)

    ds = xr.open_dataset(file_list[f])

    # drop the cell vertices - only cell centers are needed for rasterizing
    ds = ds.drop_vars(['xv','yv'],errors='ignore')

    # domain files are (nj,ni) - collapse to a single ncol dimension
    if ds.sizes['nj']==1:
        ds = ds.isel(nj=0,drop=True).rename(ni='ncol')
    else:
        print(' '*2+f'{hapy.tclr.YELLOW}nj={ds.sizes["nj"]} - falling back to stack(){hapy.tclr.END}')
        ds = ds.stack(ncol=('nj','ni')).reset_index('ncol',drop=True)

    ds = ds.assign_coords(lat=ds['yc'].astype(np.float64),
                          lon=ds['xc'].astype(np.float64))
    ds_list.append(ds)

    print(' '*2+f'num columns: {len(ds["ncol"])}')

#-------------------------------------------------------------------------------
# restrict the columns used for rasterizing to the plotted region - the cost of
# rasterizing scales with the number of columns, not the number of pixels
subset_list = []
for f in range(num_file):
    if plot_extent is None:
        subset_list.append(None)
        continue
    lon1,lon2,lat1,lat2 = plot_extent
    tlat = ds_list[f]['lat'].values
    tlon = ds_list[f]['lon'].values
    tlon = np.where(tlon>180,tlon-360,tlon)  # normalize to [-180,180]
    pad = 2.0
    tmp_mask = ( (tlat>=lat1-pad) & (tlat<=lat2+pad) &
                 (tlon>=lon1-pad) & (tlon<=lon2+pad) )
    subset_list.append(np.where(tmp_mask)[0])
    print(' '*2+f'{file_name[f]}: using {len(subset_list[f])} of {len(tlat)} columns for the plotted region')

#-------------------------------------------------------------------------------
# rasterizing is expensive for large grids, so rasterize a map of column
# indices once per file and re-use it for every variable on that file
#   the nearest neighbor lookup is done here rather than with hapy.to_raster()
#   for two reasons: to_raster() spends most of its time estimating a grid
#   spacing in order to blank out distant pixels (which leaves speckled holes
#   wherever the grid is coarser than the sampled spacing), and its spherical
#   mode is prohibitively expensive for grids this large. searching unit sphere
#   vectors instead is exact everywhere - poles and dateline included - because
#   chord distance increases monotonically with great circle distance
index_map = [None]*num_file
def lonlat_to_xyz(lon,lat):
    """unit sphere vectors for lon/lat in degrees"""
    lon_rad,lat_rad = np.radians(lon),np.radians(lat)
    return np.column_stack([ np.cos(lat_rad)*np.cos(lon_rad),
                             np.cos(lat_rad)*np.sin(lon_rad),
                             np.sin(lat_rad) ])
def get_index_map(f,ax):
    """rasterized column index for file f, cached on the raster shape"""
    bbox = ax.get_window_extent()
    nx,ny = max(int(bbox.width*pixel_ratio),10), max(int(bbox.height*pixel_ratio),10)
    shape = (ny,nx)
    if index_map[f] is None or index_map[f][0]!=shape:
        print(' '*4+f'{hapy.tclr.CYAN}rasterizing column indices for {file_name[f]}{hapy.tclr.END}')
        sub = subset_list[f]
        tmp_lat = ds_list[f]['lat'].values
        tmp_lon = ds_list[f]['lon'].values
        if sub is not None: tmp_lat,tmp_lon = tmp_lat[sub],tmp_lon[sub]
        #-----------------------------------------------------------------------
        # pixel centers of the axes, converted from projection coords to lon/lat
        x1,x2 = ax.get_xlim(); y1,y2 = ax.get_ylim()
        xpix,ypix = np.meshgrid(np.linspace(x1,x2,nx),np.linspace(y1,y2,ny))
        pts = ccrs.PlateCarree().transform_points(ax.projection,xpix.ravel(),ypix.ravel())
        qlon,qlat = pts[:,0],pts[:,1]
        # pixels off the globe (i.e. back side of an Orthographic projection)
        valid = np.isfinite(qlon) & np.isfinite(qlat)
        #-----------------------------------------------------------------------
        tree = cKDTree(lonlat_to_xyz(tmp_lon,tmp_lat))
        dist,ind = tree.query(lonlat_to_xyz(qlon[valid],qlat[valid]),k=1)
        #-----------------------------------------------------------------------
        # optionally blank out pixels with no nearby column (regional grids)
        if max_fill_dist is not None:
            ang = np.degrees(2*np.arcsin(np.clip(dist/2,0,1)))  # chord > great circle
            ind = np.where(ang>max_fill_dist,-1,ind)
        #-----------------------------------------------------------------------
        rst = np.full(nx*ny,np.nan)
        rst[valid] = np.where(ind<0,np.nan,sub[ind] if sub is not None else ind)
        index_map[f] = (shape, rst.reshape(ny,nx))
    return index_map[f][1]

def raster_from_index(values,idx_rst):
    """map column values onto the rasterized index array"""
    valid = np.isfinite(idx_rst)
    rst = np.full(idx_rst.shape, np.nan)
    rst[valid] = values[idx_rst[valid].astype(np.int64)]
    return rst

#-------------------------------------------------------------------------------
for v in range(num_var):
    var_opts = var_opts_list[v]
    hapy.print_line()
    print(' '*2+'var: '+hapy.tclr.MAGENTA+var[v]+hapy.tclr.END)
    #---------------------------------------------------------------------------
    data_list = []
    for f in range(num_file):
        print(' '*4+'file: '+hapy.tclr.GREEN+file_name[f]+hapy.tclr.END)
        if var[v] not in ds_list[f]:
            raise ValueError(f'variable {var[v]} not found in {file_list[f]}')

        data = ds_list[f][var[v]].astype(np.float64)

        if 'scale' in var_opts: data = data*var_opts['scale']

        if print_stats: hapy.print_stat(data,name=var[v],stat='naxsh',indent=' '*6,compact=True)

        data_list.append(data)
    #---------------------------------------------------------------------------
    # common color limits across files for consistent comparison
    data_min = np.min([np.nanmin(d) for d in data_list])
    data_max = np.max([np.nanmax(d) for d in data_list])
    #---------------------------------------------------------------------------
    img_kwargs = {}
    img_kwargs['origin'] = 'lower'
    img_kwargs['cmap']   = var_opts['cmap'] if 'cmap' in var_opts else 'viridis'

    clev = var_opts['clev'] if 'clev' in var_opts else None
    if clev is not None:
        img_kwargs['norm'] = mcolors.BoundaryNorm(clev, ncolors=256)
    else:
        img_kwargs['vmin'] = var_opts['vmin'] if 'vmin' in var_opts else data_min
        img_kwargs['vmax'] = var_opts['vmax'] if 'vmax' in var_opts else data_max
    #---------------------------------------------------------------------------
    for f in range(num_file):
        ax = get_ax(v,f)

        if plot_extent is None:
            ax.set_global()
        else:
            ax.set_extent(plot_extent, crs=ccrs.PlateCarree())

        ax.coastlines(linewidth=0.5,edgecolor='black')
        ax.set_title(file_name[f],fontsize=title_fontsize, loc='left')
        ax.set_title(var_str[v],fontsize=title_fontsize, loc='right')

        rst = raster_from_index( data_list[f].values, get_index_map(f,ax) )

        img = ax.imshow(rst, extent=ax.get_xlim() + ax.get_ylim(), **img_kwargs)

        cbar = fig.colorbar(img, ax=ax, fraction=0.02, orientation='vertical')
        cbar.ax.tick_params(labelsize=lable_fontsize)

#-------------------------------------------------------------------------------
# turn off any unused panels
for p in range(num_var*num_file,num_plot_row*num_plot_col_use):
    axs[p//num_plot_col_use, p%num_plot_col_use].axis('off')

#-------------------------------------------------------------------------------
# Finalize plot
os.makedirs(os.path.dirname(fig_file), exist_ok=True)
fig.savefig(fig_file, dpi=100, bbox_inches='tight')
plt.close(fig)

print(f'\n{fig_file}')

#-------------------------------------------------------------------------------
etime = perf_counter()-timer_start
time_str = f'{etime:10.1f} sec'
if etime>60       : time_str += f' ({(etime/60):4.1f} min)'
if etime>(2*3600) : time_str += f' ({(etime/3600):.1f} hr)'
print(f'\n{hapy.tclr.YELLOW}elapsed time: {time_str} {hapy.tclr.END}')
print()
#-------------------------------------------------------------------------------

#!/usr/bin/env python3
"""
plot.grid.scrip.mask.py  —  Plot and compare the mask field of E3SM SCRIP grid
files with matplotlib + cartopy.

Each grid gets a panel shaded by its mask field (grid_imask by default), where
mask=0 is an inactive/masked cell and mask=1 is an active cell. When plot_diff
is enabled, an extra panel is added for each grid whose cell count matches the
first grid, showing (mask - mask of first grid) so differences between two
versions of a grid are easy to spot.

Edit the "User configuration" section below, then run:
    python plot.grid.scrip.mask.py
"""
# --------------------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------------------
import os, numpy as np, xarray as xr
import matplotlib.pyplot as plt
import matplotlib.collections as mcollections
import matplotlib.colors as mcolors
import cartopy.crs as ccrs, cartopy.feature as cfeature
# --------------------------------------------------------------------------------------------------
class tclr: END,RED,GRN,MGN,CYN,YLW = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m','\033[33m'
# --------------------------------------------------------------------------------------------------
# User configuration — edit this section
# --------------------------------------------------------------------------------------------------
grids = []
def add_grid(file, name, clat=0, clon=0, markers=None):
    """
    Register a SCRIP grid for plotting.
    ----------
    file       : str   — path to SCRIP .nc grid file
    name       : str   — label shown in the subplot title
    clat, clon : float — center of the zoomed view (ignored if global_view)
    markers    : list of (lat, lon) tuples to overlay as markers, or None
    """
    grids.append(dict(file=file, name=name, clat=clat, clon=clon,
                      markers=markers or []))
# ------------------------------------------------------------------------------
# Output path
fig_file = 'grid.mask.png'
# ------------------------------------------------------------------------------
# Add grids here
grid_root = '/global/cfs/cdirs/e3sm/whannah/files_grid'
#add_grid(f'{grid_root}/ne30pg2_scrip.nc', 'ne30pg2', clat=38, clon=-120)
#add_grid(f'{grid_root}/ne30pg2_scrip.nc', 'ne30pg2', clat=38, clon=-120)

root='/lustre/orion/cli115/world-shared/e3sm/inputdata/ocn/mpas-o/RRSwISC6to18E3r5'
add_grid(f'{root}/ocean.RRSwISC6to18E3r5.mask.scrip.20240327.nc', 'RRSwISC6to18E3r5.mask')
add_grid(f'{root}/ocean.RRSwISC6to18E3r5.nomask.scrip.20240327.nc', 'RRSwISC6to18E3r5.nomask')

# ------------------------------------------------------------------------------
# Name of the mask variable — 'grid_imask' is the SCRIP standard
mask_var = 'grid_imask'

# Add a difference panel for each grid relative to the first grid
#   — only done for grids with a matching cell count
plot_diff = False

# Draw cell outlines on top of the mask shading
draw_edges = False

# Global map instead of the zoomed view set by clat/clon and half_w/half_h
global_view = True

# Half-width/height of the zoomed view [degrees]
half_w = 50
half_h = 30

# Panel layout and figure size [inches per panel]
#   panel_h ~ panel_w/2 avoids a lot of white space for a global view
num_plot_col = 2
panel_w      = 5.5
panel_h      = 3.0

# ------------------------------------------------------------------------------
# Colors for mask = 0 (inactive) and mask = 1 (active)
MASK_COLORS = ['0.8', 'darkgreen']

# Colors for the difference panels — [ -1, 0, +1 ]
DIFF_COLORS = ['blue', '0.9', 'red']

# --------------------------------------------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------------------------------------------
RE = 6.37122e6   # radius of earth [m]

# ------------------------------------------------------------------------------
# Load SCRIP grid variables from a NetCDF file. SCRIP coordinates can be stored
# in degrees or radians, so convert to degrees when needed.
def load_scrip(path, mask_var):
    ds = xr.open_dataset(path)
    if mask_var not in ds:
        raise ValueError(f"No mask variable '{mask_var}' in {path}")
    clat = ds['grid_center_lat'].values.astype(np.float64)
    clon = ds['grid_center_lon'].values.astype(np.float64)
    vlat = ds['grid_corner_lat'].values.astype(np.float64)   # (ncells, nvertices)
    vlon = ds['grid_corner_lon'].values.astype(np.float64)
    units = ds['grid_center_lat'].attrs.get('units','degrees').lower()
    if units.startswith('rad') or np.max(np.abs(clat)) <= (np.pi/2 + 1e-3):
        clat,clon = np.degrees(clat),np.degrees(clon)
        vlat,vlon = np.degrees(vlat),np.degrees(vlon)
    mask = ds[mask_var].values.astype(np.float64).ravel()
    # grid_area is optional in the SCRIP format - fall back to a uniform area
    if 'grid_area' in ds:
        area = ds['grid_area'].values.ravel()      # steradians
    else:
        area = np.full(mask.size, 4*np.pi/mask.size)
    return dict(
        clat   = clat.reshape(mask.size),
        clon   = clon.reshape(mask.size),
        vlat   = vlat.reshape(mask.size,-1),
        vlon   = vlon.reshape(mask.size,-1),
        area   = area,
        mask   = mask,
        ncells = mask.size,
    )

# ------------------------------------------------------------------------------
# Compute approximate grid spacing [km] from SCRIP area [steradians]
def approx_dx(area):
    return np.sqrt(area) * RE / 1e3

# ------------------------------------------------------------------------------
# Normalize longitudes from 0..360 to -180..180
def norm_lon(lon):
    return np.where(lon > 180.0, lon - 360.0, lon)

# ------------------------------------------------------------------------------
# Project SCRIP corner vertices into the native coordinate system of `proj`.
# Returns x, y of shape (ncells, nvertices) and a boolean visibility mask
# (True = all corners project without NaN).
def transform_verts(vlat, vlon, proj, src_crs):
    ncells, nv = vlat.shape
    xyz = proj.transform_points(src_crs, vlon.ravel(), vlat.ravel())
    x = xyz[:, 0].reshape(ncells, nv)
    y = xyz[:, 1].reshape(ncells, nv)
    vis = ~np.any(np.isnan(x) | np.isnan(y), axis=1)
    return x, y, vis

# --------------------------------------------------------------------------------------------------
# Load the grids and print mask statistics
# --------------------------------------------------------------------------------------------------
if not grids: raise ValueError('ERROR - no grids were added!')

for g in grids:
    print(f'  {tclr.GRN}{g["name"]:20}{tclr.END}  {tclr.YLW}{g["file"]}{tclr.END}')
    sc = load_scrip(g['file'], mask_var)
    g['sc'] = sc
    mask    = sc['mask']
    num_off = int(np.sum(mask == 0))
    num_on  = int(np.sum(mask == 1))
    num_odd = mask.size - num_off - num_on
    print(f'    ncells : {sc["ncells"]}')
    print(f'    mask=0 : {num_off}   mask=1 : {num_on}'
          + (f'   {tclr.RED}other : {num_odd}{tclr.END}' if num_odd > 0 else ''))

# ------------------------------------------------------------------------------
# Compare masks against the first grid — only valid for matching cell counts
mask_ref = grids[0]['sc']['mask']
for g in grids[1:]:
    if g['sc']['ncells'] != grids[0]['sc']['ncells']:
        print(f'  {tclr.YLW}{g["name"]} vs {grids[0]["name"]} : cell count mismatch '
              f'({g["sc"]["ncells"]} vs {grids[0]["sc"]["ncells"]}) - no comparison{tclr.END}')
        continue
    num_diff = int(np.sum(g['sc']['mask'] != mask_ref))
    pct_diff = num_diff / mask_ref.size * 100
    print(f'  {tclr.MGN}{g["name"]} vs {grids[0]["name"]} : '
          f'{num_diff} cells differ ({pct_diff:.4f}%){tclr.END}')

# --------------------------------------------------------------------------------------------------
# Build the panel list — the mask for each grid, then the differences
# --------------------------------------------------------------------------------------------------
panels = [dict(grid=g, diff=False) for g in grids]
if plot_diff:
    for g in grids[1:]:
        if g['sc']['ncells'] != grids[0]['sc']['ncells']: continue
        panels.append(dict(grid=g, diff=True))

# --------------------------------------------------------------------------------------------------
# Discrete colormaps for the mask and the mask difference
# --------------------------------------------------------------------------------------------------
CMAP_MASK = mcolors.ListedColormap(MASK_COLORS)
NORM_MASK = mcolors.BoundaryNorm([-0.5, 0.5, 1.5], ncolors=CMAP_MASK.N)
CMAP_DIFF = mcolors.ListedColormap(DIFF_COLORS)
NORM_DIFF = mcolors.BoundaryNorm([-1.5, -0.5, 0.5, 1.5], ncolors=CMAP_DIFF.N)

# --------------------------------------------------------------------------------------------------
# Build figure
# --------------------------------------------------------------------------------------------------
num_panel = len(panels)
num_rows  = int(np.ceil(num_panel / num_plot_col))
src_crs   = ccrs.PlateCarree()

fig = plt.figure(figsize=(panel_w * num_plot_col, panel_h * num_rows))

for idx, p in enumerate(panels):

    g  = p['grid']
    sc = g['sc']

    # --------------------------------------------------------------------------
    # Fill data and color scale — mask or mask difference
    if p['diff']:
        fill_data  = sc['mask'] - mask_ref
        cmap,norm  = CMAP_DIFF,NORM_DIFF
        cbar_ticks = [-1, 0, 1]
        cbar_label = f'{mask_var} difference'
        title      = f'{g["name"]} - {grids[0]["name"]}'
    else:
        fill_data  = sc['mask']
        cmap,norm  = CMAP_MASK,NORM_MASK
        cbar_ticks = [0, 1]
        cbar_label = mask_var
        title      = g['name']

    print(f'  {tclr.CYN}{title:40}{tclr.END} {cbar_label}')

    # --------------------------------------------------------------------------
    proj = ccrs.PlateCarree()
    ax   = fig.add_subplot(num_rows, num_plot_col, idx + 1, projection=proj)

    clon, clat = g['clon'], g['clat']
    if global_view:
        ax.set_global()
    else:
        ax.set_extent(
            [clon - half_w, clon + half_w, clat - half_h, clat + half_h],
            crs=src_crs,
        )

    # --------------------------------------------------------------------------
    dx = approx_dx(sc['area'])

    # --------------------------------------------------------------------------
    # Normalize corner and center longitudes from 0..360 to -180..180.
    # E3SM SCRIP files store longitudes in 0..360; PlateCarree expects -180..180.
    vlon_norm = norm_lon(sc['vlon'])
    cclon     = norm_lon(sc['clon'])
    cclat     = sc['clat']

    # --------------------------------------------------------------------------
    # Transform normalized corner vertices to projected coordinates
    x, y, vis = transform_verts(sc['vlat'], vlon_norm, proj, src_crs)

    # --------------------------------------------------------------------------
    # Keep cells whose center falls within the zoomed view extent, padded by
    # one approximate cell-width so partially visible edge cells are included.
    # set_extent handles the visual clipping.
    if not global_view:
        dx_deg  = dx.max() / 111.0   # rough cell size in degrees (1 deg ~ 111 km)
        pad     = dx_deg * 1.5
        in_view = (
            (cclat >= clat - half_h - pad) & (cclat <= clat + half_h + pad) &
            (cclon >= clon - half_w - pad) & (cclon <= clon + half_w + pad)
        )
        vis = vis & in_view

    # --------------------------------------------------------------------------
    # Exclude cells that straddle the antimeridian (vertex lon range > 180 deg)
    vlon_range  = vlon_norm.max(axis=1) - vlon_norm.min(axis=1)
    not_wrapped = vlon_range < 180.0
    vis = vis & not_wrapped

    # --------------------------------------------------------------------------
    # Build PolyCollection from visible cells
    verts = np.stack([x[vis], y[vis]], axis=-1)   # (nvis, nvertices, 2)

    col = mcollections.PolyCollection(
        verts,
        array=fill_data[vis],
        cmap=cmap,
        norm=norm,
        linewidths=(0.1 if draw_edges else 0),
        edgecolors=('#444444' if draw_edges else 'none'),
        zorder=2,
    )
    ax.add_collection(col)

    # --------------------------------------------------------------------------
    # Coastlines and state borders
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='black', zorder=3)
    if not global_view:
        ax.add_feature(cfeature.STATES, linewidth=0.4, edgecolor='black', zorder=3)

    # --------------------------------------------------------------------------
    # Optional markers (list of (lat, lon) tuples)
    for (mlat, mlon) in g['markers']:
        ax.plot(mlon, mlat, 'r^', markersize=6, transform=src_crs, zorder=5)

    # --------------------------------------------------------------------------
    # Per-panel colorbar — discrete, one box per mask value
    cb = fig.colorbar(col, ax=ax, orientation='horizontal',
                      fraction=0.04, pad=0.02, shrink=0.85, ticks=cbar_ticks)
    cb.set_label(cbar_label, fontsize=8)
    cb.ax.tick_params(labelsize=7)

    # --------------------------------------------------------------------------
    # Subplot title
    if p['diff']:
        num_diff = int(np.sum(fill_data != 0))
        ax.set_title(f'{title}   ({num_diff:,} of {sc["ncells"]:,} cells differ)', fontsize=9)
    else:
        num_on = int(np.sum(fill_data == 1))
        ax.set_title(f'{title}   ({sc["ncells"]:,} cells,  {num_on:,} active)', fontsize=9)

# --------------------------------------------------------------------------------------------------
# Save figure
# --------------------------------------------------------------------------------------------------
os.makedirs(os.path.dirname(fig_file) or '.', exist_ok=True)
fig.tight_layout()
fig.savefig(fig_file, dpi=200, bbox_inches='tight')
print(f'\n{fig_file}\n')

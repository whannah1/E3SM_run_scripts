#!/usr/bin/env python3
"""
plot_domain_squares.py

Visualize square model domains of various sizes centered at a given lat/lon,
overlaid on a Cartopy map. Useful as a design aide for choosing E3SM/SCREAM
doubly-periodic or regional domain extents.

Usage:
    python plot_domain_squares.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# -------------------------------------------------------------------
# Configuration

CENTER_LON       = 75.0    # center longitude (degrees E)
CENTER_LAT       = 0.0     # center latitude  (degrees N)

DOMAIN_SIZES_KM  = [200, 400, 600, 1000]

OUTPUT_FILE      = "DP-domain-size.png"
DPI              = 150

# Extra padding beyond the largest domain (degrees)
MAP_PADDING_DEG  = 8.0

# Color cycle — outermost domain gets the first color
COLORS = [
    "#e63946",
    "#f4a261",
    "#2a9d8f",
    "#457b9d",
    "#6a4c93",
    "#1d3557",
]

# -------------------------------------------------------------------
# Helpers

def km_to_deg_lon(km, lat_deg):
    """Convert km to degrees longitude at a given latitude."""
    return km / (111.320 * np.cos(np.radians(lat_deg)))

def km_to_deg_lat(km):
    """Convert km to degrees latitude."""
    return km / 110.574

def domain_extent(center_lon, center_lat, side_km):
    """
    Return (lon_min, lon_max, lat_min, lat_max) for a square domain
    of side_km centered at (center_lon, center_lat).
    """
    half = side_km / 2.0
    dlon = km_to_deg_lon(half, center_lat)
    dlat = km_to_deg_lat(half)
    return (
        center_lon - dlon,
        center_lon + dlon,
        center_lat - dlat,
        center_lat + dlat,
    )

# -------------------------------------------------------------------
# Map extent — derived from the largest domain plus padding

lon_min, lon_max, lat_min, lat_max = domain_extent(
    CENTER_LON, CENTER_LAT, max(DOMAIN_SIZES_KM)
)
map_extent = [
    lon_min - MAP_PADDING_DEG,
    lon_max + MAP_PADDING_DEG,
    lat_min - MAP_PADDING_DEG,
    lat_max + MAP_PADDING_DEG,
]

# -------------------------------------------------------------------
# Figure

proj = ccrs.PlateCarree()

fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={"projection": proj})
ax.set_extent(map_extent, crs=proj)

# -------------------------------------------------------------------
# Background map features

ax.add_feature(cfeature.OCEAN.with_scale("50m"),     facecolor="#cde4f0", zorder=0)
ax.add_feature(cfeature.LAND.with_scale("50m"),      facecolor="#e8dfc8", zorder=1)
ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.6, edgecolor="#555", zorder=2)
ax.add_feature(cfeature.BORDERS.with_scale("50m"),   linewidth=0.3, edgecolor="#888", zorder=2)
ax.add_feature(cfeature.LAKES.with_scale("50m"),     facecolor="#cde4f0", zorder=2)
ax.add_feature(cfeature.RIVERS.with_scale("50m"),    linewidth=0.3, edgecolor="#7bb3cb", zorder=2)

# -------------------------------------------------------------------
# Gridlines

gl = ax.gridlines(
    crs=proj, draw_labels=True,
    linewidth=0.4, color="#aaa", linestyle="--", alpha=0.7,
    x_inline=False, y_inline=False,
)
gl.top_labels   = False
gl.right_labels = False
gl.xlabel_style = {"size": 8, "color": "#444"}
gl.ylabel_style = {"size": 8, "color": "#444"}

# -------------------------------------------------------------------
# Domain boxes — draw largest first so smallest sits on top

legend_handles = []

for i, size_km in enumerate(sorted(DOMAIN_SIZES_KM, reverse=True)):
    color = COLORS[i % len(COLORS)]
    lon0, lon1, lat0, lat1 = domain_extent(CENTER_LON, CENTER_LAT, size_km)

    rect = mpatches.Rectangle(
        xy=(lon0, lat0),
        width=lon1 - lon0,
        height=lat1 - lat0,
        linewidth=1.8,
        edgecolor=color,
        facecolor=color,
        alpha=0.08,
        transform=proj,
        zorder=3 + i,
    )
    ax.add_patch(rect)

    # -----------------------------------------------------------------
    # Label at top-right corner of each box

    ax.text(
        lon1, lat1 + 0.15,
        f"{size_km} km",
        transform=proj,
        fontsize=7.5, fontweight="bold",
        color=color, ha="right", va="bottom",
        zorder=10,
        path_effects=[pe.withStroke(linewidth=2, foreground="white")],
    )

    legend_handles.append(
        mpatches.Patch(
            facecolor=color, alpha=0.4, edgecolor=color, linewidth=1.5,
            label=f"{size_km} km x {size_km} km",
        )
    )

# -------------------------------------------------------------------
# Center marker

ax.plot(
    CENTER_LON, CENTER_LAT, "+",
    color="#cc0000", markersize=10, markeredgewidth=1.5,
    transform=proj, zorder=11,
)
ax.text(
    CENTER_LON + 0.3, CENTER_LAT + 0.3,
    f"({CENTER_LON:.1f}E, {CENTER_LAT:.1f}N)",
    transform=proj,
    fontsize=7.5, color="#cc0000",
    path_effects=[pe.withStroke(linewidth=2, foreground="white")],
    zorder=11,
)

# -------------------------------------------------------------------
# Legend and title

legend_handles.reverse()  # smallest first in legend
ax.legend(
    handles=legend_handles,
    title="Domain size", title_fontsize=8,
    fontsize=7.5, loc="lower left",
    framealpha=0.85, edgecolor="#ccc",
)

ax.set_title(
    f"Model domain size comparison  --  center: {CENTER_LON:.1f}E, {CENTER_LAT:.1f}N",
    fontsize=11, pad=8,
)

# -------------------------------------------------------------------
# Save

plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=DPI, bbox_inches="tight")
print(f"Saved: {OUTPUT_FILE}")
plt.show()
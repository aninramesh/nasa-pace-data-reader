from nasa_pace_data_reader import L1, L2, plot
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
import numpy as np
# cartopy related imports
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
# suppress warnings
import warnings
warnings.filterwarnings("ignore")


def concat_l1c_dicts(dict1, dict2):
    """Concatenate two L1C dicts along the along-track (row) axis.
    Spatial arrays (latitude, longitude, i, q, u, dolp, etc.) are concatenated;
    metadata (view_angles, wavelengths, F0, _units, date_time) are kept from dict1.
    """
    combined = {}
    # Keys that are spatial and should be concatenated along axis 0
    spatial_keys = [k for k in dict1.keys()
                    if k not in ('_units', 'date_time', 'view_angles',
                                 'intensity_wavelength', 'polarization_wavelength',
                                 'F0', 'polarization_f0')
                    and isinstance(dict1[k], np.ndarray)]
    for k in spatial_keys:
        combined[k] = np.concatenate([dict1[k], dict2[k]], axis=0)
    # Copy metadata from dict1
    for k in dict1:
        if k not in combined:
            combined[k] = dict1[k]
    return combined


def concat_l2_dicts(dict1, dict2):
    """Concatenate two L2 dicts along the along-track (row) axis.
    Spatial arrays are concatenated; metadata (wavelengths, _units, date_time) are kept from dict1.
    """
    combined = {}
    spatial_keys = [k for k in dict1.keys()
                    if k not in ('_units', 'date_time', 'wavelengths')
                    and isinstance(dict1[k], np.ndarray)]
    for k in spatial_keys:
        combined[k] = np.concatenate([dict1[k], dict2[k]], axis=0)
    for k in dict1:
        if k not in combined:
            combined[k] = dict1[k]
    return combined


def make_combined_fig(rgb_, rgb_extent_, dpi=300):
    """Create a figure with the combined RGB background."""
    fig = plt.figure(figsize=(3, 5), dpi=dpi)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_facecolor('black')
    ax.patch.set_facecolor('black')
    rgb_masked = np.ma.masked_where(rgb_ == 0, rgb_)
    ax.imshow(rgb_masked, origin='lower', extent=rgb_extent_, transform=ccrs.PlateCarree())
    fig.patch.set_facecolor('black')
    return fig, ax


def plot_var(l2_dict, var, fig, ax, chi2Mask, aod_mask=None,
             wavelength=None, saveFig=False, savePath=None,
             limitTriangle=[0,0], **kwargs):
    """Plot a variable from a combined L2 dict on the given axes."""
    # do not use aod_mask for AOT-type and chi2 variables
    if var in ['aot', 'aot_fine', 'aot_coarse', 'chi2']:
        aod_mask = None

    # resolve wavelength index
    wl = wavelength if wavelength is not None else 550
    idx = np.where(l2_dict['wavelengths'] == wl)[0][0]

    # scalar variables (no wavelength dimension)
    scalar_vars = ['chi2', 'n_iter', 'quality_flag', 'reff_coarse', 'reff_fine',
                   'vd', 'windspeed', 'angstrom', 'alh', 'spherFrac']

    # extract data
    data = l2_dict[var][:, :] if var in scalar_vars else l2_dict[var][:, :, idx]

    # apply masks
    if chi2Mask is not None:
        data = np.ma.masked_where(chi2Mask, data)
    if aod_mask is not None:
        data = np.ma.masked_where(aod_mask, data)

    lon, lat = l2_dict['longitude'], l2_dict['latitude']

    # strip non-matplotlib kwargs
    plot_kwargs = {k: v for k, v in kwargs.items()
                   if k not in ['saveFig', 'savePath', 'noAxisTicks',
                                'black_background', 'chi2Mask', 'aod_mask',
                                'dpi', 'limitTriangle']}

    im = ax.pcolormesh(lon, lat, data, transform=ccrs.PlateCarree(), **plot_kwargs)

    # styling
    fig.patch.set_facecolor('black')
    plt.rcParams['text.color'] = 'tan'
    plt.rcParams['axes.labelcolor'] = 'grey'
    plt.rcParams['xtick.color'] = 'tan'
    plt.rcParams['ytick.color'] = 'tan'
    plt.rcParams['axes.titlecolor'] = 'white'
    plt.rcParams['axes.edgecolor'] = 'tan'
    plt.rcParams['axes.facecolor'] = 'tan'

    # title
    ax.set_title(f'{var}' if var in scalar_vars else f'{var} at {wl} nm')
    ax.coastlines()
    ax.add_feature(cfeature.LAND, alpha=0.5)
    ax.add_feature(cfeature.OCEAN, alpha=0.5)

    # colorbar
    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)
    fig.add_axes(ax_cb)

    extend = 'neither'
    if limitTriangle[0] and limitTriangle[1]:
        extend = 'both'
    elif limitTriangle[0]:
        extend = 'min'
    elif limitTriangle[1]:
        extend = 'max'
    plt.colorbar(im, cax=ax_cb, extend=extend)

    # save
    if saveFig and savePath is not None:
        wl_str = f'_{wl}nm' if var not in scalar_vars and wavelength is not None else ''
        fig.savefig(f'{savePath}/{var}{wl_str}.png', dpi=kwargs.get('dpi', 300),
                    bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)


# %% Main code

# ---- Change the following parameters ---- #

# location of the L2 files (consecutive granules)
fileName = '/stor/z101/Data/PACE/HARP2/grasp/L2/v4-Beta/v01_a/PACE_HARP2.20240927T210427.L1C.V3.5km-v4-beta-01a.nc'
fileName2 = '/stor/z101/Data/PACE/HARP2/grasp/L2/v4-Beta/v01_a/PACE_HARP2.20240927T205927.L1C.V3.5km-v4-beta-01a.nc'

# l1c file locations
l1c_file = '/stor/z101/Data/PACE/HARP2/sds_test/V4/V01_c/L1C/PACE_HARP2.20240927T210427.L1C.V3.5km.nc'
l1c_file2 = '/stor/z101/Data/PACE/HARP2/sds_test/V4/V01_c/L1C/PACE_HARP2.20240927T205927.L1C.V3.5km.nc'

# save the plots in a folder
fileName_no_ext = os.path.splitext(os.path.basename(fileName))[0]
saveDir = f'/stor/z101/Data/PACE/HARP2/grasp/L2/v4-Beta/v01_c/figures/{fileName_no_ext}_combined/'

dpi = 300
cmap = 'Spectral_r'

# chi2 filtering
chiMax = 8
chiMin = 0.01

# filtering based on min AOD value
minAOD_550 = 0.05

# extents of the plot
AOD = [0, 0.3]
SSA = [0.85, 1]
Reff_coarse = [0.5, 3]
Reff_fine = [0.08, 0.35]
VD = [0, 0.5]
MR = [1.33, 1.7]
MI = [0, 0.1]
AE = [-0.2, 3]

# ---- Do not change anything below this line ---- #

if not os.path.exists(saveDir):
    os.makedirs(saveDir)

#%% Read and combine L1C data
l1c = L1.L1C()
l1c_dict1 = l1c.read(l1c_file)
l1c_dict2 = l1c.read(l1c_file2)
l1c_combined = concat_l1c_dicts(l1c_dict1, l1c_dict2)

# Create a Plot object with the combined data and project the RGB
plt_combined = plot.Plot(l1c_combined)
plt_combined.setBand('Blue')

# Zero out edge rows to prevent nearest-neighbor interpolation artifacts
# from meshgridRGB smearing edge pixels into streaks
n_edge = 3
n_rows_g1 = l1c_dict1['latitude'].shape[0]  # where granule 1 ends
for var in ['i', 'q', 'u', 'dolp']:
    if var in l1c_combined:
        l1c_combined[var][:n_edge, ...] = 0          # top edge
        l1c_combined[var][-n_edge:, ...] = 0         # bottom edge
        l1c_combined[var][n_rows_g1-1:n_rows_g1+1, ...] = 0  # granule seam
plt_combined.data = l1c_combined  # update the data reference
fig_rgb, ax_rgb, rgb_, rgb_extent_ = plt_combined.projectedRGB(
    normFactor=280, saveFig=False, dpi=dpi, figsize=(3, 5), returnRGB=True)
plt.close(fig_rgb)

# Save the combined RGB
fig_rgb, ax_rgb = make_combined_fig(rgb_, rgb_extent_, dpi)
fig_rgb.savefig(f'{saveDir}/RGB_combined.png', dpi=dpi, bbox_inches='tight',
                facecolor=fig_rgb.get_facecolor())
plt.close(fig_rgb)

#%% Read and combine L2 data
l2_1 = L2.L2()
l2_dict1 = l2_1.read(fileName)
l2_2 = L2.L2()
l2_dict2 = l2_2.read(fileName2)
l2_combined = concat_l2_dicts(l2_dict1, l2_dict2)

# Combined masks
chi2Mask = (l2_combined['chi2'] > chiMax) | (l2_combined['chi2'] < chiMin)
aod_mask = l2_combined['aot'][:,:,1] < minAOD_550

#%% Plot all variables

common = dict(cmap=cmap, dpi=dpi, saveFig=True, savePath=saveDir)

# AOT
fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'aot', fig_, ax_, chi2Mask, aod_mask,
         vmax=AOD[1], vmin=AOD[0], limitTriangle=[0,1], **common)

fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'aot_fine', fig_, ax_, chi2Mask, aod_mask,
         vmax=AOD[1], vmin=AOD[0], limitTriangle=[0,1], **common)

fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'aot_coarse', fig_, ax_, chi2Mask, aod_mask,
         vmax=AOD[1], vmin=AOD[0], limitTriangle=[0,1], **common)

# SSA at multiple wavelengths
for wl in [None, 670, 870, 440]:
    fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
    plot_var(l2_combined, 'ssa_total', fig_, ax_, chi2Mask, aod_mask,
             wavelength=wl, vmax=SSA[1], vmin=SSA[0], limitTriangle=[1,0], **common)

# Reff
fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'reff_coarse', fig_, ax_, chi2Mask, aod_mask,
         vmin=Reff_coarse[0], vmax=Reff_coarse[1], limitTriangle=[0,1], **common)

fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'reff_fine', fig_, ax_, chi2Mask, aod_mask,
         vmin=Reff_fine[0], vmax=Reff_fine[1], limitTriangle=[1,1], **common)

# Volume density
fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'vd', fig_, ax_, chi2Mask, aod_mask, **common)

# Refractive index
fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'mr', fig_, ax_, chi2Mask, aod_mask,
         wavelength=550, vmin=MR[0], vmax=MR[1], **common)

fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'mi', fig_, ax_, chi2Mask, aod_mask,
         vmin=MI[0], vmax=MI[1], **common)

# Angstrom exponent
fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'angstrom', fig_, ax_, chi2Mask, aod_mask,
         vmin=AE[0], vmax=AE[1], **common)

# Chi2
fig_, ax_ = make_combined_fig(rgb_, rgb_extent_, dpi)
plot_var(l2_combined, 'chi2', fig_, ax_, chi2Mask,
         vmax=chiMax, limitTriangle=[0,1], **common)

plt.close('all')
print(f'All combined plots saved to {saveDir}')
from nasa_pace_data_reader import L1, L2, plot
import copy
from matplotlib import pyplot as plt
import os
import numpy as np
# cartopy related imports
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Local function to project the variable and copy the figure and axis

def project_and_copy(l2, var, fig_base_, ax_base_, return_= False, **kwargs):
    # do not use aod_mask if var in ['aot', 'aot_fine', 'aot_coarse']
    if var in ['aot', 'aot_fine', 'aot_coarse', 'chi2']:
        kwargs['aod_mask'] = None
    # fig_, ax_ = copy.deepcopy((fig_base_, ax_base_))
    l2.projectVar(var, fig=fig_base_, ax=ax_base_, **kwargs)
    if not return_:
        del fig_base_, ax_base_
    else:
        return fig_base_, ax_base_

# %% Main code

# ---- Change the following parameters ---- #

# location of the L2 file
fileName = '/Users/aputhukkudy/Downloads/PACE/L2/2p6/PACE_HARP2.20241102T071117.L1C.V2.5km-v0.2.6.IDOLP_3px.nc'
# fileName2 = '/Users/aputhukkudy/Downloads/PACE/L2/2p4-Vanderlei/PACE_HARP2.20240907T172952.L1C.V2.5km-v0.2.4.IDOLP-test.nc'

# l1c file location
l1c_file = '/Users/aputhukkudy/Downloads/PACE_HARP2.20241102T071117.L1C.V2.5km.nc'

# save the plots in a folder
saveDir = '/Users/aputhukkudy/Downloads/PACE/L2/2p6/20241102T071117/'

dpi = 160
cmap = 'Spectral_r'

# chi2 filtering filter chi2 values greater than chiMax or chiMin
chiMax = 8
chiMin = 0.01
l2_chi2_mask = True # None to not use it, True to use it

# filtering the retrieved products based on the min AOD value
minAOD_550 = 0.25
AOD_mask = True     # None to not use it, True to use it

# extents of the plot
AOD = [0, 1]
SSA = [0.85, 1]
Reff_coarse = [0.5, 3]
Reff_fine = [0.08, 0.35]
VD = [0, 0.5]
MR = [1.33, 1.7]
MI = [0, 0.1]
AE = [-0.2, 3]

# ---- Do not change anything below this line ---- #

# make sure the saveDir exists
if not os.path.exists(saveDir):
    os.makedirs(saveDir)

# Read the L1C file
l1c = L1.L1C()
l1c_dict = l1c.read(l1c_file)

# project the L1C data
plt_ = plot.Plot(l1c_dict)
plt_.setBand('Blue')

fig_base, ax_base, rgb_, rgb_extent_ = plt_.projectedRGB(normFactor=280, saveFig=True,
                    dpi=dpi, figsize=(3,3), returnRGB=True)

# fig_base = plt.figure(figsize=(3,3), dpi=dpi)
# ax_base = plt.axes(projection=ccrs.PlateCarree())
# change the font color
fig_base.patch.set_facecolor('black')
# axis labels and ticks font color
fig_, ax_ = copy.deepcopy((fig_base, ax_base))
fig_.savefig(f'{saveDir}/RGB.png', dpi=dpi)

# Read the L2 file
l2 = L2.L2()
l2_dict = l2.read(fileName)
if l2_dict is not None:
    l2_chi2_mask = (l2_dict['chi2'] > chiMax) | (l2_dict['chi2'] < chiMin)

if AOD_mask is not None:
    AOD_mask = l2_dict['aot'][:,:,1] < minAOD_550

# create a mask based on min AOD value

# Define the common parameters
common_params = {'dpi': dpi, 'cmap': cmap, 'chi2Mask': l2_chi2_mask, 'saveFig': True, 'noAxisTicks': True,
                  'black_background': True, 'savePath': saveDir, 'aod_mask': AOD_mask}

#%% plot the retrieved variables

# Call the function for each variable
fig_, ax_ = copy.deepcopy((fig_base, ax_base))
fig_test, ax_test = project_and_copy(l2, 'aot', fig_, ax_, return_= True, vmax=AOD[1], vmin=AOD[0], limitTriangle=[0,1], **common_params)

fig_, ax_ = copy.deepcopy((fig_base, ax_base))
project_and_copy(l2, 'aot_fine', fig_, ax_, vmax=AOD[1], vmin=AOD[0], limitTriangle=[0,1], **common_params)

fig_, ax_ = copy.deepcopy((fig_base, ax_base))
project_and_copy(l2, 'aot_coarse', fig_, ax_, vmax=AOD[1], vmin=AOD[0], limitTriangle=[0,1], **common_params)

wavelengths = [None, 670, 870, 440]
for wavelength in wavelengths:
    fig_, ax_ = copy.deepcopy((fig_base, ax_base))
    if wavelength is None:
        project_and_copy(l2, 'ssa_total', fig_, ax_, vmax=SSA[1], vmin=SSA[0], limitTriangle=[1,0], **common_params)
    else:
        project_and_copy(l2, 'ssa_total', fig_, ax_, wavelength=wavelength, vmax=SSA[1], vmin=SSA[0], **common_params)

fig_, ax_ = copy.deepcopy((fig_base, ax_base))
project_and_copy(l2, 'reff_coarse', fig_, ax_, vmin=Reff_coarse[0], vmax=Reff_coarse[1], limitTriangle=[0,1], **common_params)

fig_, ax_ = copy.deepcopy((fig_base, ax_base))
fig_test, ax_test = project_and_copy(l2, 'reff_fine', fig_, ax_, return_= True, vmin=Reff_fine[0], vmax=Reff_fine[1], limitTriangle=[1,1], **common_params)

fig_, ax_ = copy.deepcopy((fig_base, ax_base))
project_and_copy(l2, 'vd', fig_, ax_, **common_params)

fig_, ax_ = copy.deepcopy((fig_base, ax_base))
project_and_copy(l2, 'mr', fig_, ax_, wavelength=550, vmin=MR[0], vmax=MR[1], **common_params)

fig_, ax_ = copy.deepcopy((fig_base, ax_base))
project_and_copy(l2, 'mi', fig_, ax_, vmin=MI[0], vmax=MI[1], **common_params)

fig_, ax_ = copy.deepcopy((fig_base, ax_base))
project_and_copy(l2, 'angstrom', fig_, ax_, vmin=AE[0], vmax=AE[1], **common_params)

fig_, ax_ = copy.deepcopy((fig_base, ax_base))
project_and_copy(l2, 'chi2', fig_, ax_, vmax=chiMax, limitTriangle=[0,1], **common_params)

'''
# Read the L2 file
l2 = L2.L2()
l2_dict = l2.read(fileName2)
if l2_dict is not None:
    l2_chi2_mask = (l2_dict['chi2'] > chiMax) | (l2_dict['chi2'] < chiMin)
    # additional filtering based on the aod values at 550 nmplt.c
    l2_chi2_mask = l2_chi2_mask | (l2_dict['aot'][:, :,1] < 0.25)

if AOD_mask is not None:
    AOD_mask = l2_dict['aot'][:,:,1] < minAOD_550
    
# Define the common parameters
common_params = {'dpi': dpi, 'cmap': cmap, 'chi2Mask': l2_chi2_mask, 'saveFig': True, 'noAxisTicks': True,
                  'black_background': True, 'savePath': saveDir, 'aod_mask': AOD_mask}

#%% plot the retrieved variables

# Call the function for each variable
# project_and_copy(l2, 'aot', fig_test, ax_test, vmax=1, vmin=0, limitTriangle=[0,1], **common_params)
# project_and_copy(l2, 'aot_fine', fig_base, ax_base, vmax=1, vmin=0, limitTriangle=[0,1], **common_params)
# project_and_copy(l2, 'aot_coarse', fig_base, ax_base, vmax=1, vmin=0, limitTriangle=[0,1], **common_params)
# project_and_copy(l2, 'ssa_total', fig_base, ax_base, vmax=1, vmin=0.85, limitTriangle=[1,0], **common_params)
# project_and_copy(l2, 'ssa_total', fig_base, ax_base, wavelength=670, vmax=1, vmin=0.85, **common_params)
# project_and_copy(l2, 'ssa_total', fig_base, ax_base, wavelength=870, vmax=1, vmin=0.85, limitTriangle=[1,0], **common_params)
# project_and_copy(l2, 'ssa_total', fig_base, ax_base, wavelength=440, vmax=1, vmin=0.85, **common_params)
# project_and_copy(l2, 'reff_coarse', fig_base, ax_base, vmin=0.5, vmax=3, limitTriangle=[0,1], **common_params)
# project_and_copy(l2, 'reff_fine', fig_test, ax_test, vmin=0.08, vmax=0.2, limitTriangle=[1,1], **common_params)
# project_and_copy(l2, 'vd', fig_base, ax_base, **common_params)
# project_and_copy(l2, 'mr', fig_base, ax_base, wavelength=550, vmin=1.33, vmax=1.7, **common_params)
# project_and_copy(l2, 'mi', fig_base, ax_base, **common_params)
# project_and_copy(l2, 'chi2', fig_base, ax_base, vmax=6, **common_params)

# close the figures
# plt.close('all')
'''
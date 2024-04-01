from nasa_pace_data_reader import L1, L2, plot
import copy
from matplotlib import pyplot as plt
# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# location of the L2 file
fileName = '/Users/aputhukkudy/Downloads/PACE/L2/2024-03-11T11_46_22_created_2024-03-27T08-30.nc'

# l1c file location
l1c_file = '/Users/aputhukkudy/Downloads/PACE/03-11/hipp382/PACE_HARP2.20240311T114622.L1C.nc'

# Read the L1C file
l1c = L1.L1C()
l1c_dict = l1c.read(l1c_file)

dpi = 160
cmap = 'Spectral_r'

# project the L1C data
plt_ = plot.Plot(l1c_dict)
plt_.setBand('Blue')
fig_1, ax_1, _, _ = plt_.projectedRGB(normFactor=280, saveFig=True,
                   dpi=dpi, figsize=(3,3), returnRGB=True)
# change the font color
fig_1.patch.set_facecolor('black')
# axis labels and ticks font color
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
fig_.savefig('RGB.png', dpi=dpi)
# Read the L2 file
l2 = L2.L2()
l2_dict = l2.read(fileName)

# chi2 filtering filter chi2 values greater than chiMax or chiMin
chiMax = 10
chiMin = 0.2
l2_chi2_mask = (l2_dict['chi2'] > chiMax) | (l2_dict['chi2'] < chiMin)

# plot the aot data
l2.projectVar('aot', dpi=dpi, vmax=2, vmin=0, cmap=cmap,
              chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True, horizontalColorbar=True, limitTriangle=[0,1])
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('aot_fine', dpi=dpi, vmax=2, vmin=0, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True, limitTriangle=[0,1])
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('aot_coarse', dpi=dpi, vmax=2, vmin=0, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True, limitTriangle=[0,1])
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('ssa_total', dpi=dpi, vmax=1, vmin=0.85, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True, limitTriangle=[1,0])
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('ssa_total', wavelength=670, dpi=dpi, vmax=1, vmin=0.85, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('ssa_total', wavelength=870, dpi=dpi, vmax=1, vmin=0.85, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('ssa_total', wavelength=440, dpi=dpi, vmax=1, vmin=0.85, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))

# plot the 'chi2' variable
l2.projectVar('reff_coarse', dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('reff_fine', dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True)
l2.projectVar('vd', dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('mr', wavelength=550, dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True)
l2.projectVar('chi2', dpi=dpi, vmax = chiMax, cmap=cmap)

from nasa_pace_data_reader import L1, L2, plot
import copy
# from matplotlib import pyplot as plt
# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# location of the L2 file
fileName = '/Users/aputhukkudy/Downloads/PACE/L2/v0p2p6/PACE_HARP2.20241110T082844.L1C.V2.5km-v0.2.6.IDOLP_3px.nc'

# l1c file location
l1c_file = '/Users/aputhukkudy/Downloads/PACE_HARP2.20241110T082844.L1C.V2.5km.nc'

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
chiMax = 20
chiMin = 0.01
l2_chi2_mask = None
if l2_dict is not None:
    l2_chi2_mask = (l2_dict['chi2'] > chiMax) | (l2_dict['chi2'] < chiMin)
    # additional filtering based on the aod values at 550 nmplt.c
    l2_chi2_mask = l2_chi2_mask | (l2_dict['aot'][:, :,1] < 0.25)

#%% plot the aot data
l2.projectVar('aot', dpi=dpi, vmax=5, vmin=0, cmap=cmap,
              chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True, limitTriangle=[0,1])
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('aot_fine', dpi=dpi, vmax=5, vmin=0, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True, limitTriangle=[0,1])
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('aot_coarse', dpi=dpi, vmax=1, vmin=0, cmap=cmap, chi2Mask=l2_chi2_mask,
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
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True, limitTriangle=[1,0],
              black_background=True)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('ssa_total', wavelength=440, dpi=dpi, vmax=1, vmin=0.85, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))

# plot the 'chi2' variable
l2.projectVar('reff_coarse', dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask, vmin=0.5, vmax=3,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True, limitTriangle=[0,1],
              black_background=True)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('reff_fine', dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask, vmin=0.08, vmax=0.2,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True, limitTriangle=[1,1],
              black_background=True, )
l2.projectVar('vd', dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('angstrom', dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask, fig=fig_, ax=ax_,
              black_background=True, saveFig=True, noAxisTicks=True, vmax=2, vmin=-0.2)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('alh', dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask, fig=fig_, ax=ax_,
              black_background=True, saveFig=True, noAxisTicks=True, vmax=7000, vmin=500)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('mr', wavelength=550, dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask, vmin=1.33, vmax=1.7,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True, 
              black_background=True,)
del fig_, ax_
fig_, ax_ = copy.deepcopy((fig_1, ax_1))
l2.projectVar('mi', wavelength=550, dpi=dpi, cmap=cmap, chi2Mask=l2_chi2_mask,
              saveFig=True, fig=fig_, ax=ax_, noAxisTicks=True,
              black_background=True,)
l2.projectVar('chi2', dpi=dpi, vmax = 6, cmap=cmap)

# Change Log Memory

## [2026-04-19] — Merge consecutive L2 granules into single combined plots

**Context:** The two L2 files are consecutive PACE granules. Instead of plotting them separately, we combine both onto a single figure per variable.

**Files Changed:**
- `Examples/L2-HARP2-GRASP-example.py` — complete rewrite: added `make_combined_fig()` (dual RGB background) and `plot_combined_var()` (overlays both L2 datasets on shared axes with single colorbar); removed dependency on `L2.projectVar` for combining

**Summary:** Script now reads both L1C files for RGB, both L2 files for data, computes combined extent automatically, and produces one merged plot per variable saved to a `_combined/` output directory.

**Special Notes:**
- `plot_combined_var` strips non-matplotlib kwargs (dpi, savePath, etc.) before passing to `pcolormesh`
- Figure size is (3, 5) to accommodate the taller combined extent
- Both `pcolormesh` calls share the same `vmin`/`vmax` so colors are consistent across granules

---



## [2026-04-19] — Fix deepcopy crash in L2-HARP2-GRASP-example.py

**Context:** The L2 example script was crashing because `copy.deepcopy` cannot handle cartopy `GeoAxes`/`CRS` objects. Additionally, the `projectVar` method in the installed package was missing `savePath`/`aod_mask` params, causing kwargs to leak into `pcolormesh`.

**Files Changed:**
- `Examples/L2-HARP2-GRASP-example.py` — replaced all `copy.deepcopy` calls with a new `make_base_fig()` helper that recreates fresh figure+axes with the RGB background; removed `import copy`; updated plot parameters (dpi, AOD range, minAOD, dynamic saveDir)
- `src/nasa_pace_data_reader/plot.py` — (staged by user, changes to projectedRGB/projectVar)

**Summary:** Fixed two runtime errors: (1) `copy.deepcopy` failing on cartopy CRS objects, and (2) `savePath` leaking through `**kwargs` to `pcolormesh`. The fix uses `make_base_fig()` to create fresh figures each time instead of deepcopying.

**Special Notes:**
- Cartopy CRS/GeoAxes objects are inherently non-picklable; always recreate rather than deepcopy
- The `make_base_fig` helper must match `projectedRGB`'s `imshow` call: `origin='lower'`, mask zeros, no `transform` kwarg for PlateCarree
- The installed package at `~/.venv/DL` was outdated vs the local source; user should `pip install -e .` to keep in sync

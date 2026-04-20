# Change Log Memory

## [2026-04-19] — Merge consecutive L2 granules into seamless combined plots

**Context:** The two L2 files are consecutive PACE granules. Instead of plotting them separately, we concatenate all data along the along-track axis and produce seamless combined plots.

**Files Changed:**
- `Examples/L2-HARP2-GRASP-example.py` — complete rewrite with data concatenation approach:
  - Added `concat_l1c_dicts()` / `concat_l2_dicts()` to merge spatial arrays along axis 0
  - Single `projectedRGB` call on combined L1C data → seamless RGB, no gap
  - Single `pcolormesh` per variable on combined L2 data
  - Added edge-zeroing (top/bottom/granule seam) to prevent `meshgridRGB` nearest-neighbor interpolation artifacts
  - Self-contained `plot_var()` function replaces dependency on `L2.projectVar`
- `CHANGE_LOG_MEMORY.md` — updated

**Summary:** Script concatenates both L1C and L2 data arrays along the along-track axis before any projection or plotting. This produces a seamless RGB background and unified data overlays with no inter-granule gap.

**Special Notes:**
- Concatenation keys are auto-detected: spatial numpy arrays are concatenated, metadata (wavelengths, view_angles, F0, _units, date_time) are kept from dict1
- Edge rows (top 3, bottom 3, seam 2) are zeroed before `projectedRGB` to prevent interpolation smearing
- `plot_var` strips non-matplotlib kwargs (dpi, savePath, etc.) before passing to `pcolormesh`
- Figure size is (3, 5) to accommodate the taller combined swath

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

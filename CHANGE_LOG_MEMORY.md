# Change Log Memory

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

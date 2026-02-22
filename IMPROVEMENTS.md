# NASA PACE Data Reader – Improvement Suggestions

Prioritized suggestions to improve maintainability, robustness, and usability. Some quick fixes have already been applied (see **Applied fixes** below).

---

## Applied fixes (this pass)

- **plot.py**: Fixed typo in error message: "shoulshould" → "should".
- **L2.py**: `read()` now raises `ValueError` when `checkFile()` fails instead of returning `None` (callers no longer get `None` without an exception).
- **L2.py**: In `read()`, the `except KeyError` block now re-raises after closing the file, so failures are explicit and the file is always closed.
- **__init__.py**: Removed `logging.basicConfig(level=logging.INFO)` so the library does not configure logging globally; applications can configure it themselves.

---

## High priority

### 1. **L2.read() – consistent error handling and return type**

- **Issue**: In the loop over `geophysical_names`, a `KeyError` is caught and only printed; execution continues and may leave some variables missing. The docstring says it returns a dict, but previously it could return `None` on wrong file type (now fixed).
- **Suggestion**: Either skip missing variables and log a warning, or raise on first missing variable. Document which variables are required vs optional. Ensure every code path either returns a dict or raises.

### 2. **Use logging instead of print in library code**

- **Where**: `L2.py` (e.g. "Reading ...", "Error: ...") and `plot.py` (e.g. band set, DPI, instrument, save location, errors).
- **Why**: Libraries should use `logging` so users can control level and destination. You already have `logger` in `L1.py` and `__init__.py`.
- **Action**: In `L2.py` and `plot.py`, add `logger = logging.getLogger(__name__)` and replace user-facing/error `print()` calls with `logger.info()`, `logger.warning()`, or `logger.error()` as appropriate.

### 3. **Unit tests**

- **Current**: No `test_*.py` files; only `.pytest_cache` present.
- **Suggestions**:
  - Add a `tests/` directory and `pytest` (and optionally `pytest-cov`) to dev dependencies in `pyproject.toml`.
  - Start with: (a) `L1C.read()` / `L1B.read()` with a minimal or mocked NetCDF file, (b) `L2.read()` with a minimal/mock L2 file, (c) `Plot` with a small fixture dict (e.g. `plotRGB`, `setBand`).
  - Cover edge cases: wrong file type, missing groups/variables, invalid band names.

---

## Medium priority

### 4. **README and examples**

- **README**: The example uses a bare `except:` when printing key shapes. Prefer `except Exception` and/or catch a specific exception (e.g. `AttributeError` for missing `.shape`).
- **Examples**: You have several very similar files (`L1B-RGB-example.py`, `L1B-RGB-example-fixed.py`, `L1B-RGB-example-fixed2.py`). Consider keeping one canonical L1B RGB example and linking to it from the README to reduce confusion and maintenance.

### 5. **Type hints**

- **L1.py**: Already uses typing (e.g. `Dict`, signatures). Good.
- **plot.py**: `Plot.__init__(self, data, instrument="HARP2")` and many methods have no type hints. Adding types for `data` (e.g. `Dict[str, Any]`), `instrument`, and return types would improve IDE support and catch misuse earlier.

### 6. **plot.py – assertions vs exceptions**

- **Where**: e.g. `setBand()` asserts band name; `setInstrument()` asserts instrument; `L2.projectVar()` asserts projection.
- **Suggestion**: For invalid user input (e.g. wrong band or projection), raise `ValueError` with a clear message instead of `AssertionError`, so callers can catch and handle invalid arguments in a standard way.

### 7. **L2.read() – file handle safety**

- **Issue**: If an exception occurs after `dataNC = Dataset(...)` but before `dataNC.close()` (e.g. in the geophysical loop), the file might not be closed.
- **Suggestion**: Use a context manager: `with Dataset(filename, "r") as dataNC:` so the file is always closed, then build and return `data` inside the block.

---

## Lower priority

### 8. **Pre-commit and linting**

- **Current**: Black is in `.pre-commit-config.yaml`; flake8 is commented out.
- **Suggestions**: Re-enable flake8 (or use ruff) with a sensible config (e.g. ignore E501 if line length is handled by Black). Add a `[tool.ruff]` or `[tool.flake8]` section in `pyproject.toml` if you want config in one place.

### 9. **Public API and __init__.py**

- **Current**: Usage is `from nasa_pace_data_reader import L1, L2, plot` (submodules). README uses `L1.L1C()`, `plot.Plot()`.
- **Optional**: For a friendlier API you could expose classes in `__init__.py`, e.g. `from .L1 import L1C, L1B` and `from . import plot`, so users can do `from nasa_pace_data_reader import L1C, L1B, plot` and `L1C()`, `plot.Plot()`. Not required if you prefer keeping submodules.

### 10. **Dependencies**

- **pyproject.toml**: You have `notebook` as a dependency; consider making it optional (e.g. `[optional-dependencies] notebook`) if the core reader/plotting does not require it, so CLI/headless users need fewer installs.

### 11. **Performance and large files**

- For very large granules, consider allowing lazy/virtual variables (e.g. netCDF4 variables without loading into memory until needed) or documenting recommended chunking. This is a larger change; the current approach is fine for typical use.

### 12. **Examples – avoid bare except**

- In `batch_pacepax_generator.py` and `batch_rgb_generator.py` there are `except:` clauses. Prefer `except Exception:` (and log or re-raise) so you don’t accidentally catch `KeyboardInterrupt`/`SystemExit`.

---

## Summary

- **Done**: Typo fix, L2 `read()` wrong-file and exception behavior, and logging config in `__init__.py`.
- **Next**: Add logging in L2 and plot, then add a small test suite and tighten L2 `read()` (optional vars vs required, context manager). After that, README/example cleanup, type hints, and replacing assertions with `ValueError` in plot will round out the improvements.

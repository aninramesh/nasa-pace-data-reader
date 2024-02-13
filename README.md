# NASA-PACE-Data-Reader

This repository contains a Python package for reading L1C files from NASA PACE instruments (HARP2, SPEXone, OCI). Development includes planned readers for L2 aerosol and surface products.

## How to build and upload:

Run `sh Install.sh`(make sure to specify correct version) or follow the steps

Build: Same as before (`python3 -m build`)

Upload: (`python3 -m twine upload --repository testpypi dist/*`)

Install: (`python3 -m pip install -i https://test.pypi.org/simple/ --no-deps nasa_pace_data_reader==0.0.3`)

Unistall: (`python3 -m pip uninstall nasa_pace_data_reader`)

---

Example usage:

```Python
from nasa_pace_data_reader import L1

calc = L1.L1C()
result = calc.add(5, 3)
print(result)  # Output: 8

```

Explanation of Changes:
---


Key Improvements
---

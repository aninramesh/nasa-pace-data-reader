# NASA-PACE-Data-Reader

This repository hosts a Python package designed to read L1C files from NASA PACE instruments, including HARP2, SPEXone, and OCI. Future development plans include the addition of readers for L2 aerosol and surface products.

## Building and Uploading the Package:

To build and upload the package, you can either run the `Install.sh` script (ensure to specify the correct version), or follow the steps outlined below:

**Build:** Use the same command as before, which is `python3 -m build`.

**Upload:** Use the command `python3 -m twine upload --repository testpypi dist/*`.

**Install:** Use the command `python3 -m pip install -i https://test.pypi.org/simple/ nasa-pace-data-reader`.

**Uninstall:** Use the command `python3 -m pip uninstall nasa_pace_data_reader`.

---

## Example Usage:

Here is a simple example of how to use the package:

```Python
from nasa_pace_data_reader import L1

calc = L1.L1C()
result = calc.add(5, 3)
print(result)  # This will output: 8
```

---

## Change Log:

---

## Key Improvements:


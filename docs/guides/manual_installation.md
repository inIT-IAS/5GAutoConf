(label-manual-installation)=
# Manual Installation

(label-manual-installation-prerequisites)=
## Prerequisites

The following prerequisites need to be installed first:

- Git
- Python 3
- Make

Make is not mandatory, but simplifies the installation and package management process. 
If Make is not available on your system, check the `Makefile` or the [Manual Package Installation](label-manual-installation-manual-package-installation) for manual installation and testing steps.

All other python-related dependencies are installed during the setup process.

### Ubuntu/Debian

Install `git`, `python3`, `python3-venv` and `python3-pip` using apt:

```bash
sudo apt update && sudo apt -y upgrade
sudo apt install -y git python3 python3-venv
```

Instead of the minimal `git` installation, using `git-all` during `apt install` will install all dependencies, including a GUI.
If your system does not have a GUI, do not install `git-all`.

Make is usually already part of Linux.
If not, you can install it using apt:

```bash
sudo apt install make 
```

### Windows

Install Git for Windows: [https://git-scm.com/install/windows](https://git-scm.com/install/windows).

Install Python3 from the website: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/). `pip` and `venv` are already part of the distribution.

Make is usually not part of Windows, but can be obtained using **MSYS2**:
1. Install MSYS2 from [https://www.msys2.org/](https://www.msys2.org/), follow their instructions for installation and package database update.
2. Open the MSYS2 UCRT64 terminal (or the terminal appropriate for your toolchain).
3. Install `make`: `pacman -S make`
4. Add the appropriate MSYS2 `bin` directory to your `PATH`, for example `C:\msys64\ucrt64\bin`, or if you are using the MSYS environment: `C:\msys64\usr\bin`.

(label-manual-installation-manual-package-installation)=
## Manual Package Installation

```{important}
Replace all `python` commands with `python3` when using Debian or Ubuntu!
```

Create a virtual environment, for example `.venv`.

```bash
python -m venv .venv
```

Activate the virtual environment.

Windows (Powershell):

```bash
.\.venv\Scripts\Activate.ps1
```

Linux:

```bash
source .venv/bin/activate
```

Install the 5GAutoConf package from the project's root directory:

```bash
pip install .[dev,dist]
```

Compile Python files:

```bash
python -m compileall .
```

Deactivate the virtual environment:

```bash
deactivate
```

## Run Unittests

The long unittests include the look-up tables and usually take a few minutes to complete.
The short unittests skip these tables and usually take a few seconds.

### Long Unittests

Activate the virtual environment (see above).
Then, from the project's root directory, run:

```bash
pytest test.py -v
```
Since these tests involve the look-up tables, they usually take a few minutes to complete.

### Short Unittests

Activate the virtual environment (see above).
Then, from the project's root directory, run:

```bash
pytest test.py -v -m "not slow"
```

## Update Code Coverage

Note: Ignores the `.venv` subdirectory.

From the projects root directory, run the long tests:

```bash
coverage run --omit '.venv/*' -m pytest test.py -v
```

Update Coverage badge in README.md:

```bash
readme-cov
```

Show report:

```bash
coverage report -m
```

Show report with HTMl formatting:

```bash
coverage html
```

## Reinstall docs

If `docs/` needs to be updated or fully rebuilt (e.g. after using `make clean`), the rst files can be fully regenerated from the project's root directory.

Activate the virtual environment, then run `sphinx-quickstart`:

```bash
sphinx-quickstart docs
```

During `sphinx-quickstart docs`, choose:

- `Separate source and build directories (y/n) [n]:` --> `n`
- `Project name:` --> `5GAutoConf`
- `Author name(s):` --> `Niels Hendrik Fliedner`
- `Project release []:` --> the most recent release version, e.g. `v0.3.3`
- `Project language [en]:` --> en

Edit `docs/conf.py`

```python
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.githubpages",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

napoleon_google_docstring = False
napoleon_numpy_docstring = True

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
]

html_theme = 'furo'
html_static_path = []
```

From the project's root directory, run:

sphinx-apidoc -f -o docs/api . docs site test.py
sphinx-build -b html docs docs/_build
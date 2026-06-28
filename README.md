# 5GAutoConf

[![Latest Release](https://img.shields.io/github/v/release/inIT-IAS/5GAutoConf?sort=semver)](https://github.com/inIT-IAS/5GAutoConf/releases)

A Rapid Data-Driven Autoconfiguration Tool for 5G Base Stations.

Currently, this tool works with OpenAirInterface5G as gNB and Open5GS as 5GC.
Any changes to the core need to be manually integrated into `static_settings.json`.

**Note: The distribution name is `gnbautoconf` to avoid import errors when using `pip install` and `import` from a distribution site.**

The API docs are available in `docs/`.

## Usage

This program uses static configuration derived from `static_settings.json` and dynamic configuration derived from user command line argument inputs.
Currently, **two modes** are supported: **Analysis** and **Synthesis**.

If the command line arguments are left at default, the program reproduces the OpenAirInterface5G configuration file [gnb.sa.band78.fr1.106PRB.usrpb210.conf](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf), but with an adapted filename and additional comments.

```bash
gnbautoconf [-h] [-f FREQUENCYBAND] [-b BANDWIDTH] [-r RASTER] [-d {TDD,FDD}] [-c CENTER] [-s {b200,b210,x300,x310,none}] [-l {debug,info,warning,error,critical}] [**kwargs]
```

### Options

The following options are mainly used for the **Analysis Mode**, while some are also used for **Synthesis Mode**.

| Short | Long | Choices | Default | Description | Used for Synthesis Mode? |
|-------|------|---------|---------|-------------| ------------------------ |
| `-h`| `--help`|  |  | Show the help message and exit. | No |
| `-f`| `--frequencyband`|  | `78` | The 5G NR frequency band. | Yes |
| `-b`| `--bandwidth`|  | `40` | The bandwidth in MHz of the channel to be configured. | Yes |
| `-r`| `--raster`|  | `30` | The ΔFRaster in kHz. This corresponds to the subcarrier spacing SCS. | No |
| `-d`| `--duplex`| `TDD`, `FDD` | `TDD` | **DEPRECATED** The Duplex mode. This serves no function anymore, since the frequency band already defines the duplex mode. | No |
| `-c`| `--center`|  | `3619.2` | The desired center frequency in MHz of the channel to be configured. | Yes |
| `-s`| `--sdr`| `b200`, `b210`, `x300`, `x310`, `none` | `b210` | The Software Defined Radio model being used. | Yes |
| `-l`| `--loglevel`| `debug`, `info`, `warning`, `error`, `critical` | `info` | The logging level for printing to the console. The logfile is always at level `debug`. | Yes |

#### Additional Synthesis Arguments (kwargs)

For synthesizing cell configuration parameters, 5GAutoConf automatically assumes a synthesis should be performed if any additional arguments (`kwargs`) are passed.
In that case, no analysis of input arguments is performed.

The following additional arguments are currently accepted.
If the argument is allowed to be omitted (see table below), then it will be ignored during parameter computation.
The example values result in `FR1`, `TDD`, and PRACH configuration index `161`.

| Argument | Example Values | Minimum Value | Maximum Value | Description | Omission allowed? |
| -------- | -------------- | ------------- | ------------- | ----------- | ----------------- |
| `n` | `1.000293` | anything `>0` | Technically none, but it will distort all other parameters. | Refractive index of the medium. | No |
| `r-cell` | `1900` | `0` | `14000` | Maximum gNB cell radius in meters. Maximum value defined by OAI5G due to missing implementation of 1250 kHz and 5000 kHz SCS for msg1. | No |
| `ue-speed` | `27.78` | `0` | ca. `7800` | Maximum UE speed in m/s. Maximum speed partially depends on the maximum delay spread. | No |
| `tau-d` | `15` | `0` | `66` | Maximum delay spread in microseconds. Maximum value defined by OAI5G due to missing implementation of 1250 kHz and 5000 kHz SCS for msg1. | No |
| `x` | `1` | `1` | `16` |  | Yes |
| `y` | `0` | `0` | `2` |  | Yes |
| `subframe-number` | `9` | `1` | `39` | For `FR2` and `TDD`, this is actually the slot number. | Yes |
| `starting-symbol` | `0` | `0` | `8` |  | Yes |
| `n-slot-ra` | `2` | `1` | `2` | Number of PRACH slots within a subframe / a 60 kHz slot | Yes |
| `n-t-ra-slot` | `1` | `1` | `7` |  | Yes |
| `n-dur-ra` | `12` | `0` | `12` |  | Yes |

Examples: 
- Full arguments: `gnbautoconf -f 78 -b 40 -c 3780 -s b210 -l info n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00 x=1 y=0 subframe-number=9 starting-symbol=0 n-slot-ra=2 n-t-ra-slot=1 n-dur-ra=12`
- Omitted arguments: `gnbautoconf -c 3780 n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00`

### Examples

#### Match OpenAirInterface5G Config

```bash
gnbautoconf
```

#### Match TH OWL Basestation in SmartFactoryOWL

Note: Verified and working with OAI5G UE, Amit 5G Modem, and Samsung S23.

```bash
gnbautoconf -f 78 -b 40 -r 30 -d TDD -c 3780 -s b210 -l info
```

Alternatively, use `make` to run this example:

```bash
make run
```

For running a synthesis example with the above arguments:

```bash
make synth
```

## Installation

### Prerequisites

Ubuntu/Debian: Install `python3`, `python3-venv` and `python3-pip` using apt:

```bash
sudo apt update && sudo apt -y upgrade
sudo apt install -y python3 python3-venv
```

**Note: Replace all `python` commands with `python3` when using Debian or Ubuntu!**

Windows: 

- Install Python3 from the website: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/). `pip` and `venv` are already part of the distribution.

### Using Make

Navigate to the package's root directory.

Run the installation using `make`:

```bash
make install
```

(Optional): Build wheel for distribution:

```bash
make build
```

The installation will create a `.venv` folder and compile Python files in `__pycache__` subdirectories.
Both can be removed using `make`:

```bash
make clean
```

If you are calling this from an IDE that uses the `.venv` Python version as intepreter, switch to a different interpreter first, then execute `make clean`.
Otherwise, the `.venv` folder will not be removed during `make clean`.

After the installation is complete, it is recommended to run the unittests using `make`:

```bash
make test
```

### Manual Package Installation

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

(Optional) compile Python files:

```bash
python -m compileall .
```

(Optional) deactivate the virtual environment:

```bash
deactivate
```

### Run Tests

From the projects root directory, run:

```bash
pytest test.py -v
```

### Update Code Coverage

Note: Should ignore the `.venv` subdirectory.

From the projects root directory, run:

```bash
coverage run --omit '.venv/*' -m pytest test.py -v
```

Update Coverage badge in README.md:

```bash
readme-cov
```

(Optional) show report:

```bash
coverage report -m
```

(Optional) show report with HTMl formatting:

```bash
coverage html
```

## Docs

Running `make docs` places a browsable html file in `docs/_build/index.html`.

If `docs/` needs to be updated or fully rebuilt (e.g. after using `make clean`), the rst files can be fully regenerated from the project's root directory:

```
sphinx-quickstart docs
```

During `sphinx-quickstart docs`, choose:

- `Separate source and build directories (y/n) [n]:` --> `n`
- `Project name:` --> `5GAutoConf`
- `Author name(s):` --> `Niels Hendrik Fliedner`
- `Project release []:` --> the most recent release version, e.g. `v0.3.0`
- `Project language [en]:` --> en

Edit `docs/conf.py`

```python
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "numpydoc",
]

html_theme = "sphinx_rtd_theme"
```

Edit `docs/index.rst`:

```rst
5GAutoConf documentation
========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/modules
```

From the project's root directory, run:

```
make docs
```

## Known Issues

### Incomplete PRACH settings result in no config synthesis

Since the synthesis of certain parameters has not been implemented yet, they need to be set manually in the source code.
The missing parameters consider capacity and coverage optimizations, so for now they are not computed automatically:

```python
x_sfn_stat = 1  # x for System frame number: SFN mod x = y
y_sfn_stat = 0  # y for System frame number: SFN mod x = y
subframe_number_stat = None
starting_symbol_stat = None

n_slot_ra_stat = None  # Number of PRACH slots within a subframe
n_t_ra_slot_stat = None  # Number of time-domain PRACH occasions within a PRACH slot
n_dur_ra_stat = None  # PRACH duration
```

The parameter values can be set to `None`, which results in them being ignored for making the PRACH configuration index choice.

The default values for `x_sfn_stat` and `y_sfn_stat` result in a PRACH occasion for every system frame number (SFN).

**Note: Any change requires to re-run `make clean` and then `make install`, if `gnbautoconf` shall be used instead of directly calling `run.py`.**

#### Temporary Solution 1: Ignore

If you don't need any more specific parameters for choosing the PRACH configuration, 5GAutoConf will pick the parameters of the first matching table entries, as described above.

#### Temporary Solution 2: Manual Parameter Setting

Check the commandline output for:
- Frequency range, e.g. `Frequency Range: FR1` --> Table choice
- Duplex mode, e.g. `Duplex Mode: TDD` --> Table choice
- PRACH preamble format, e.g. `PRACH Preamble Format: B4` -> PRACH configuration index choice

Open the respective 3GPP table and search for the PRACH preamble format:

- `FR1` and `FDD`: 3GPP TS 38.211 Table 6.3.3.2-2
- `FR1` and `TDD`: 3GPP TS 38.211 Table 6.3.3.2-3
- `FR2` and `TDD`: 3GPP TS 38.211 Table 6.3.3.2-4

For `FR1`, `TDD`, and `B4`, we use 3GPP TS 38.211 Table 6.3.3.2-3 and observe the range of PRACH configuration indices that cover `B4`: `198` - `218`

This results in the following table excerpt:

| PRACH Configuration Index | Preamble format | x | y | Subframe number | Starting symbol | Number of PRACH slots within a subframe | Number of time-domain PRACH occasions within a PRACH slot | PRACH duration |
|---|---|---|---|---|---|---|---|---|
| 145 | B4 | 16 | 1 | 9 | 0 | 2 | 1 | 12 |
| 146 | B4 | 8 | 1 | 9 | 0 | 2 | 1 | 12 |
| 147 | B4 | 4 | 1 | 9 | 2 | 1 | 1 | 12 |
| 148 | B4 | 2 | 1 | 9 | 0 | 1 | 1 | 12 |
| 149 | B4 | 2 | 1 | 9 | 2 | 1 | 1 | 12 |
| 150 | B4 | 2 | 1 | [7,9] | 2 | 1 | 1 | 12 |
| 151 | B4 | 2 | 1 | [4,9] | 2 | 1 | 1 | 12 |
| 152 | B4 | 2 | 1 | [4,9] | 0 | 2 | 1 | 12 |
| 153 | B4 | 2 | 1 | [8,9] | 0 | 2 | 1 | 12 |
| 154 | B4 | 2 | 1 | [2,3,4,7,8,9] | 0 | 1 | 1 | 12 |
| 155 | B4 | 1 | 0 | 1 | 0 | 1 | 1 | 12 |
| 156 | B4 | 1 | 0 | 2 | 0 | 1 | 1 | 12 |
| 157 | B4 | 1 | 0 | 4 | 0 | 1 | 1 | 12 |
| 158 | B4 | 1 | 0 | 7 | 0 | 1 | 1 | 12 |
| 159 | B4 | 1 | 0 | 9 | 0 | 1 | 1 | 12 |
| 160 | B4 | 1 | 0 | 9 | 2 | 1 | 1 | 12 |
| 161 | B4 | 1 | 0 | 9 | 0 | 2 | 1 | 12 |
| 162 | B4 | 1 | 0 | [4,9] | 2 | 1 | 1 | 12 |
| 163 | B4 | 1 | 0 | [7,9] | 2 | 1 | 1 | 12 |
| 164 | B4 | 1 | 0 | [8,9] | 0 | 2 | 1 | 12 |
| 165 | B4 | 1 | 0 | [3,4,8,9] | 2 | 1 | 1 | 12 |
| 166 | B4 | 1 | 0 | [1,3,5,7,9] | 2 | 1 | 1 | 12 |
| 167 | B4 | 1 | 0 | [0,1,2,3,4,5,6,7,8,9] | 0 | 2 | 1 | 12 |
| 168 | B4 | 1 | 0 | [0,1,2,3,4,5,6,7,8,9] | 2 | 1 | 1 | 12 |

Choose any of the rows and populate the source code with the remaining variables, for example (PRACH configuration index 161):

```python
x_sfn_stat = 1  # x for System frame number: SFN mod x = y
y_sfn_stat = 0  # y for System frame number: SFN mod x = y
subframe_number_stat = 9
starting_symbol_stat = 0

n_slot_ra_stat = 2  # Number of PRACH slots within a subframe
n_t_ra_slot_stat = 1  # Number of time-domain PRACH occasions within a PRACH slot
n_dur_ra_stat = 12  # PRACH duration
```

If you run 5GAutoConf again using `run.py` with your previously chosen parameters, it should result in a working configuration file.

### Slow test execution when using make test and make test-slow

Due to the computational overhead of `ts_dicts.py`, `make test` and `make test-slow` spend a long time in the `collecting` phase for `coverage`.

#### Temporary Solution: Run test commands directly without coverage

- Instead of `make test`, activate the `.venv` and run `python -m pytest test.py -v -m "not slow"`.
- Instead of `make test-slow`, activate the `.venv` and run `python -m pytest test.py -v`.

## License

5GAutoConf is licensed under the Mozilla Public License 2.0 (MPL-2.0).

Copyright (c) 2026 Niels Hendrik Fliedner

A copy of the license is available in the `LICENSE` file and online at:
https://mozilla.org/MPL/2.0/

## Citation

If you use 5GAutoConf in academic work, please cite both the software and the accompanying publication.

### Software

Niels Hendrik Fliedner. 5GAutoConf (Version 0.3.0) [Computer software]. Zenodo.

Concept DOI: https://doi.org/10.5281/zenodo.20796159

Version DOI: See the [release](https://github.com/inIT-IAS/5GAutoConf/releases) for the specific version you used.

BibTeX citation metadata is available via GitHub (`CITATION.cff`) and Zenodo.

### Accompanying paper

Niels Hendrik Fliedner, Florian Klingler, Henning Trsek. "5GAutoConf: A Rapid Data-Driven Autoconfiguration Tool for 5G Base Stations." In *2026 22nd International Conference on Distributed Computing in Smart Systems and the Internet of Things (DCOSS-IoT)*, 2026.

DOI: https://doi.org/CONFERENCE_PAPER_DOI (will be added after archival release)

The author's version can be downloaded at [https://www.th-owl.de/elsa/record/13829](https://www.th-owl.de/elsa/record/13829) or [https://fklingler.net/bib/fliedner2026autoconf/](https://fklingler.net/bib/fliedner2026autoconf/).

### Which citation should I use?

- Cite the conference paper when referring to the scientific method, algorithm, or research contribution.
- Cite the software DOI corresponding to the exact version used in your work.
- When appropriate, cite both.
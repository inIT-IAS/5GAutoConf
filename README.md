# 5GAutoConf

[![Latest Release](https://img.shields.io/github/v/release/inIT-IAS/5GAutoConf?sort=semver)](https://github.com/inIT-IAS/5GAutoConf/releases)

A Rapid Data-Driven Autoconfiguration Tool for 5G Base Stations.
Currently, this tool works with OpenAirInterface5G.

**Note: The distribution name is `gnbautoconf` to avoid import errors when using `pip install` and `import` from a distribution site.**

## Usage

This program uses static configuration derived from `static_settings.json` and dynamic configuration derived from user command line argument inputs.

If the command line arguments are left at default, the program reproduces the OpenAirInterface5G configuration file [gnb.sa.band78.fr1.106PRB.usrpb210.conf](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf), but with an adapted filename and additional comments.

```bash
gnbautoconf [-h] [-f FREQUENCYBAND] [-b BANDWIDTH] [-r RASTER] [-d {TDD,FDD}] [-c CENTER] [-s {b200,b210,x300,x310,none}] [-l {debug,info,warning,error,critical}]
```

### Options

| Short | Long | Choices | Default | Description |
|-------|------|---------|---------|-------------|
| `-h`| `--help`|  |  | Show the help message and exit. |
| `-f`| `--frequencyband`|  | `78` | The 5G NR frequency band. |
| `-b`| `--bandwidth`|  | `40` | The bandwidth in MHz of the channel to be configured. |
| `-r`| `--raster`|  | `30` | The ΔFRaster in kHz. This correspongs to the subcarrier spacing SCS. |
| `-d`| `--duplex`| `TDD`, `FDD` | `TDD` | The Duplex mode. |
| `-c`| `--center`|  | `3619.2` | The desired center frequency in MHz of the channel to be configured. |
| `-s`| `--sdr`| `b200`, `b210`, `x300`, `x310`, `none` | `b210` | The Software Defined Radio model being used. |
| `-l`| `--loglevel`| `debug`, `info`, `warning`, `error`, `critical` | `info` | The logging level for printing to the console. The logfile is always at level `debug`. |

#### Synthesis Arguments

For synthesizing cell configuration parameters, 5GAutoConf automatically assumes a synthesis should be performed if any additional arguments (`kwargs`) are passed.
In that case, no analysis of input arguments is performed.

The following additional arguments are currently accepted:

| Argument | Example Values | Description |
| -------- | -------------- | ----------- |
| `n` | `1.000293` | Refractive index of the medium |
| `r-cell` | `1900` | Maximum gNB cell radius in meters |
| `ue-speed` | `27.78` | Maximum UE speed in m/s |
| `tau-d` | `15` | Maximum delay spread in microseconds |

Example: `gnbautoconf -c 3780 n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00`

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

 ## License

5GAutoConf is licensed under the Mozilla Public License 2.0 (MPL-2.0).

Copyright (c) 2026 Niels Hendrik Fliedner

A copy of the license is available in the `LICENSE` file and online at:
https://mozilla.org/MPL/2.0/

## Citation

If you use 5GAutoConf in academic work, please cite both the software and the accompanying publication.

### Software

Niels Hendrik Fliedner. 5GAutoConf (Version 0.3.0) [Computer software]. Zenodo.

Concept DOI: https://doi.org/10.5281/zenodo.ZENODO_CONCEPT_DOI (will be added once linked)

Version DOI: https://doi.org/10.5281/zenodo.ZENODO_VERSION_DOI (will be added once linked)

BibTeX citation metadata is available via GitHub (`CITATION.cff`) and Zenodo.

### Accompanying paper

Niels Hendrik Fliedner, Florian Klingler, Henning Trsek. "5GAutoConf: A Rapid Data-Driven Autoconfiguration Tool for 5G Base Stations." In *2026 22nd International Conference on Distributed Computing in Smart Systems and the Internet of Things (DCOSS-IoT)*, 2026.

DOI: https://doi.org/CONFERENCE_PAPER_DOI (will be added after archival release)

### Which citation should I use?

- Cite the conference paper when referring to the scientific method, algorithm, or research contribution.
- Cite the software DOI corresponding to the exact version used in your work.
- When appropriate, cite both.
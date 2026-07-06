# 5GAutoConf

[![Latest Release](https://img.shields.io/github/v/release/inIT-IAS/5GAutoConf?sort=semver)](https://github.com/inIT-IAS/5GAutoConf/releases)

A Rapid Data-Driven Autoconfiguration Tool for 5G Base Stations.

Currently, this tool works with OpenAirInterface5G as gNB and Open5GS as 5GC.
Any changes to the core need to be manually integrated into `static_settings.json`.

**Note: The distribution name is `gnbautoconf` to avoid import errors when using `pip install` and `import` from a distribution site.**

The API docs, guides, and theory of work are all available in `docs/`.

## Setup

For a quick setup using `make`, see [Quickstart](docs/guides/quickstart.md).

For manual installation without `make`, see [Manual Installation](docs/guides/manual_installation.md).

## Usage

This program uses static configuration derived from `static_settings.json` and dynamic configuration derived from user command line argument inputs.
Currently, **two modes** are supported: **Analysis** and **Synthesis**.

```bash
gnbautoconf [-h] [-f FREQUENCYBAND] [-b BANDWIDTH] [-r RASTER] [-d {TDD,FDD}] [-c CENTER] [-s {b200,b210,x300,x310,none}] [-l {debug,info,warning,error,critical}] [**kwargs]
```

All CLI arguments have default values assigned.

For a quick start, see [Quickstart](docs/guides/quickstart.md).

### CLI Arguments

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

### `*kwargs` CLI Arguments

For synthesizing cell configuration parameters, 5GAutoConf automatically assumes a synthesis should be performed if any additional arguments (`kwargs`) are passed.
In that case, no analysis of input arguments is performed.

| Argument | Example Values | Minimum Value | Maximum Value | Description | Omission allowed? |
| -------- | -------------- | ------------- | ------------- | ----------- | ----------------- |
| `n` | `1.000293` | anything `>0` | Technically none, but it will distort all other parameters. | Refractive index of the medium. | No |
| `r-cell` | `1900` | `0` | `14000` | Maximum gNB cell radius in meters. Maximum value defined by OAI5G due to missing implementation of 1250 kHz and 5000 kHz SCS for msg1. | No |
| `ue-speed` | `27.78` | `0` | ca. `7800` | Maximum UE speed in m/s. Maximum speed partially depends on the maximum delay spread. | No |
| `tau-d` | `15` | `0` | `66` | Maximum delay spread in microseconds. Maximum value defined by OAI5G due to missing implementation of 1250 kHz and 5000 kHz SCS for msg1. | No |
| `x` | `1` | `1` | `16` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number | Yes |
| `y` | `0` | `0` | `2` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number | Yes |
| `subframe-number` | `9` | `1` | `39` | For `FR2` and `TDD`, this is actually the slot number. | Yes |
| `starting-symbol` | `0` | `0` | `8` | Starting symbol | Yes |
| `n-slot-ra` | `2` | `1` | `2` | Number of PRACH slots within a subframe / a 60 kHz slot | Yes |
| `n-t-ra-slot` | `1` | `1` | `7` | Number of time-domain PRACH occasions within a PRACH slot | Yes |
| `n-dur-ra` | `12` | `0` | `12` | PRACH occasion duration in symbols | Yes |

### Analysis Example

**Note: Verified and working with OAI5G UE, Amit 5G Modem, and Samsung S23.**

```bash
gnbautoconf -f 78 -b 40 -r 30 -d TDD -c 3780 -s b210 -l info
```

Alternatively, use `make` to run this example:

```bash
make run
```

For a detailed analysis tutorial, see [Waveform Parameter Analysis](docs/guides/waveform_parameter_analysis.md)

### Synthesis Example

Full arguments:

```bash
gnbautoconf -f 78 -b 40 -c 3780 -s b210 -l info n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00 x=1 y=0 subframe-number=9 starting-symbol=0 n-slot-ra=2 n-t-ra-slot=1 n-dur-ra=12
```

Alternatively, use `make` to run this example:

```bash
make synth
```

Omitted arguments with first-match-filling the remaining arguments:

```bash
gnbautoconf -c 3780 n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00
```

For a detailed synthesis tutorial, see [Waveform Parameter Synthesis](docs/guides/waveform_parameter_synthesis.md)

## Documentation

Running `make docs` places a browsable html file for the documentation in `docs/_build/index.html`.

## Known Issues

### Long test execution time when using make test and make test-slow

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

Niels Hendrik Fliedner. 5GAutoConf (Version 0.3.2) [Computer software]. Zenodo.

Concept DOI: https://doi.org/10.5281/zenodo.20796159

Version DOI: See the [release](https://github.com/inIT-IAS/5GAutoConf/releases) for the specific version you used.

BibTeX citation metadata is available via GitHub (`CITATION.cff`) and Zenodo.

### Accompanying paper

Niels Hendrik Fliedner, Florian Klingler, Henning Trsek. "5GAutoConf: A Rapid Data-Driven Autoconfiguration Tool for 5G Base Stations" in *2026 22nd International Conference on Distributed Computing in Smart Systems and the Internet of Things (DCOSS-IoT)*, 2026.

DOI: https://doi.org/CONFERENCE_PAPER_DOI (will be added after archival release)

The author's version can be downloaded at [https://www.th-owl.de/elsa/record/13829](https://www.th-owl.de/elsa/record/13829) or [https://fklingler.net/bib/fliedner2026autoconf/](https://fklingler.net/bib/fliedner2026autoconf/).

### Which citation should I use?

- Cite the conference paper when referring to the scientific method, algorithm, or research contribution.
- Cite the software DOI corresponding to the exact version used in your work.
- When appropriate, cite both.
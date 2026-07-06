(label-quickstart)=
# Quickstart

(label-quickstart-setup)=
## Setup

```{important}
This setup expects Git, Python, and Make to be already installed and set up!
If you don't have that yet, check [Manual Installation: Prerequisites](label-manual-installation-prerequisites).
```

1. Clone the package: `git clone https://github.com/inIT-IAS/5GAutoConf.git`
2. Navigate to the cloned directory (`5GAutoConf`)
3. Install the package from inside `5GAutoConf`: `make install`
4. (Optional) Build the docs locally to get browsable HTML files: `make docs`
    1. Open the local HTML docs from `docs/_build/index.html`
5. (Optional) Run the short tests with `make test` or the longer (complete) tests with `make test-slow` (since these tests involve the look-up tables, they usually take a few minutes to complete)
6. (Optional) Build the wheel for distribution: `make build`

You can uninstall the package and reset the root directory back to the cloned state: `make clean`.

```{important}
If you are calling `make clean` from an IDE or a commandline that uses the `.venv` Python version as intepreter, switch to a different interpreter first, then execute `make clean`.
Otherwise, the `.venv` folder will not be removed during `make clean`.
```

(label-quickstart-quick-analysis)=
## Quick Analysis

```{important}
**Analysis** refers to analyzing input waveform parameters regarding their cell parameter performances.
```

```{tip}
For a detailed manual analysis, check out [Waveform Parameter Analysis](label-waveform-parameter-analysis).
```

To get a default OpenAirInterface5G-compatible configuration file and its accompanying analysis, run this from `5GAutoConf` root directory:

```bash
make run
```

The manual execution would look like this:

```bash
gnbautoconf -f 78 -b 40 -r 30 -d TDD -c 3780 -s b210 -l info
```

(label-quickstart-quick-synthesis)=
## Quick Synthesis

```{important}
**Synthesis** refers to synthesizing cell parameters into waveform parameters.
```

```{tip}
For a detailed manual synthesis, check out [Waveform Parameter Synthesis](label-waveform-parameter-synthesis).
```

To get another default OpenAirInterface5G-compatible configuration file and its accompanying synthesis, run this from `5GAutoConf` root directory:

```bash
make synth
```

The manual execution would look like this:

```bash
gnbautoconf -f 78 -b 40 -c 3780 -s b210 -l info n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00 x=1 y=0 subframe-number=9 starting-symbol=0 n-slot-ra=2 n-t-ra-slot=1 n-dur-ra=12
```

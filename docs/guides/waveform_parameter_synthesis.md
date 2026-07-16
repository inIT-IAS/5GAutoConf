(label-waveform-parameter-synthesis)=
# Waveform Parameter Synthesis

```{important}
**Synthesis** refers to synthesizing cell parameters into waveform parameters.
```

```{important}
Synthesis mode is activated by providing at least one `*kwargs` parameter.
```

```{important}
Intermediate parameters need to be either defined in the source code or provided as `*kwargs` commandline (CLI) arguments.
```

```{important}
The configuration file with synthesized waveform parameters is written to `5GAutoConf_test01.conf`.
```

```{note}
These examples were presented during the "DCOSS-IoT 2026" paper presentation as part of the "6th International Workshop on Real-life Modeling in 5G/6G networks and beyond (REFRESH 2026)".
```

```{note}
Input cell parameters were originally used for analysis only. Thus, the split between input cell parameters and intermediate parameters is arbitrary.
```

```{hint}
Some of the parameters are computed based on optimization, such as SSB parameters and AbsoluteFrequencyPointA.
This also happens in analysis mode.
```

```{hint}
`5g_config.json` contains a JSON version of the synthesized configuration.
This can be used to convert the configuration file for other OSS stacks and platforms.
```

## CLI Arguments

The following options are mainly used for the **Analysis Mode**, while some are also used for **Synthesis Mode**.

| Short | Long | Choices | Default | Description | Used for Synthesis Mode? |
|-------|------|---------|---------|-------------| ------------------------ |
| `-h`| `--help`|  |  | Show the help message and exit. | No |
| `-f`| `--frequencyband`|  | `78` | The 5G NR frequency band. | Yes |
| `-b`| `--bandwidth`|  | `40` | The bandwidth in MHz of the channel to be configured. | Yes |
| `-r`| `--raster`|  | `30` | The ΔFRaster in kHz. This corresponds to the subcarrier spacing SCS. | No |
| `-d`| `--duplex`| `TDD`, `FDD` | `TDD` | **DEPRECATED** The Duplex mode. This serves no function anymore, since the frequency band already defines the duplex mode. It will be removed in a future release. | No |
| `-c`| `--center`|  | `3619.2` | The desired center frequency in MHz of the channel to be configured. | Yes |
| `-s`| `--sdr`| `b200`, `b210`, `x300`, `x310`, `none` | `b210` | The Software Defined Radio model being used. | Yes |
| `-l`| `--loglevel`| `debug`, `info`, `warning`, `error`, `critical` | `info` | The logging level for printing to the console. The logfile is always at level `debug`. | Yes |

### `*kwargs` CLI Arguments

For synthesizing cell configuration parameters, 5GAutoConf automatically assumes a synthesis should be performed if any additional arguments (`kwargs`) are passed.
In that case, no analysis of input arguments is performed.

The following additional arguments are currently accepted.
If the argument is allowed to be omitted (see table below), then it will be ignored during parameter computation and the first matching entry will be chosen.
The example values result in `FR1`, `TDD`, and PRACH configuration index `161`.

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

## Static Settings

```{important}
Static settings are not expected to need changes when configuring the same gNB.
```

Static settings are defined in `static_settings.json`.
These settings mostly refer to gNB and cell identification, PLMN, and network configurations.

## Synthesis Walkthrough

```{note}
5GAutoConf will always synthesize a working configuration, even if only some `*kwargs` are defined, by using the default choices and first matching combinations.
```

Since the synthesis mode is not fully implemented yet, certain parameters still need to be either defined in the source code or provided as `*kwargs` CLI arguments.
Alternatively, they can be left undefined and 5GAutoConf chooses the first matching variables.

If you don't already have all parameters defined to your liking, you can follow the steps described below.

**Step 1:** Run the `gnbautoconf` command only with the cell parameters you already know.

For example: 
- 5G band `n78`: `-f 78`
- channel bandwidth $40\,\text{MHz}$: `-b 40`
- center frequency $3.78\,\text{GHz}$: `-c 3780`
- maximum UE speed $27.78\,\text{m/s}~(=100\,\text{km/h})$ : `ue-speed=27.78`
- delay spread $15\,\text{µs}$: `tau-d=15.00`
- cell radius $1900\,\text{m}~(=1.9\,\text{km})$: `r-cell=1900`
- software-defined radio `B210`: `-s b210`

We also know that we will operate in regular air, so the refractive index should be $n=1.000293$: `n=1.000293`

Resulting command: `gnbautoconf -f 78 -b 40 -c 3780 -s b210 n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00`

**Step 2:** The remaining parameters will be chosen by 5GAutoConf based on the first match in their respective table (`x=1` and `y=0` are already defined per default): 

```bash
----------- SYNTHESIS MODE -----------
Maximum UE speed: 27.78 m/s
Maximum UE speed: 100.01 km/h
Refractive index of the medium: 1.000293
Minimum channel coherence time: 1427.05 µs
Maximum delay spread: 15.00 µs
Cell radius: 1900.00 m
Round-trip delay: 12.68 µs
Minimum guard time: 12.68 µs
Static PRACH Config Idx Parameters:
    Frequency Range: FR1
    Duplex Mode: TDD
Calculated PRACH Config Idx Parameters:
    PRACH Preamble Format: B4
    \Delta f_RA: 30000
PRACH Configuration Index calc: 155
PRACH Config Index Parameters:
    PRACH Preamble Format: B4
    x (SFN): 1
    y (SFN): 0
    Subframe number: 1
    Starting symbol: 0
    n_slot^RA: 1
    N_t^RA,slot: 1
    N_dur^RA: 12
```

If you are happy with that choice, you are done.
The synthesized configuration file `5GAutoConf_test01.conf` can be found in the root directory of 5GAutoConf.

**Step 3:** However, if you need changes and want to narrow down the valid options, open the respective table based on your chosen frequency range and duplex mode.
You can find these in the terminal output after executing `gnbautoconf`:

- `FR1` and `FDD`: 3GPP TS 38.211 Table 6.3.3.2-2
- `FR1` and `TDD`: 3GPP TS 38.211 Table 6.3.3.2-3
- `FR2` and `TDD`: 3GPP TS 38.211 Table 6.3.3.2-4

For our example, we received `FR1` and `TDD` from choosing `n78` and thus need to read 3GPP TS 38.211 Table 6.3.3.2-3.

**Step 4:** Find the PRACH configuration index chosen by `gnbautoconf` (here: `155`, which was the first matching table entry). 
Keep the preamble format fixed, since it was synthesized from you cell parameters (here: `B4`).
Also, keep all other parameters you already defined or you want to use as synthesized unchanged.
For example, for keeping PRACH occasions for every system frame, `x=0` and `y=0` shall remain unchanged.

This results in an excerpt of the table to remain valid:

| PRACH Configuration Index | Preamble format | $x$ | $y$ | Subframe number | Starting symbol | Number of PRACH slots within a subframe | $N_\text{t}^\text{RA,slot}$ | $N_\text{dur}^\text{RA}$ |
| --- | --- | --- | ---| --- | --- | --- | --- | --- |
| `155` | `B4` | `1` | `0` | `1` | `0` | `1` | `1` | `12` |
| `156` | `B4` | `1` | `0` | `2` | `0` | `1` | `1` | `12` |
| `157` | `B4` | `1` | `0` | `4` | `0` | `1` | `1` | `12` |
| `158` | `B4` | `1` | `0` | `7` | `0` | `1` | `1` | `12` |
| `159` | `B4` | `1` | `0` | `9` | `0` | `1` | `1` | `12` |
| `160` | `B4` | `1` | `0` | `9` | `2` | `1` | `1` | `12` |
| `161` | `B4` | `1` | `0` | `9` | `0` | `2` | `1` | `12` |
| `162` | `B4` | `1` | `0` | `4,9` | `2` | `1` | `1` | `12` |
| `163` | `B4` | `1` | `0` | `7,9` | `2` | `1` | `1` | `12` |
| `164` | `B4` | `1` | `0` | `8,9` | `0` | `2` | `1` | `12` |
| `165` | `B4` | `1` | `0` | `3,4,8,9` | `2` | `1` | `1` | `12` |
| `166` | `B4` | `1` | `0` | `1,3,5,7,9` | `2` | `1` | `1` | `12` |
| `167` | `B4` | `1` | `0` | `0,1,2,3,4,5,6,7,8,9` | `0` | `2` | `1` | `12` |
| `168` | `B4` | `1` | `0` | `0,1,2,3,4,5,6,7,8,9` | `2` | `1` | `1` | `12` |

**Step 5:** Let's say, after seeing our options, we now decide we want to move our PRACH occasion to the last subframe, which has the number `9`.
Looking at the table excerpt, we can see that there would be three valid options with PRACH configuration indices `159`, `160`, and `161`.

We also want to maximize the number of Number of PRACH slots within a subframe, which would result in `2` (with `1` and `2` being the only choices for `B4`).
We can now see, that only PRACH configuration index `161` could fulfil this requirement.

**Step 6:** Let's test this by plugging in the new parameters as `*kwargs` CLI arguments:

```bash
gnbautoconf -f 78 -b 40 -c 3780 -s b210 n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00 subframe-number=9 n-slot-ra=2
```

And indeed, the terminal output of 5GAutoConf gives us a new complete configuration that matches our updated requirements.
Our expectation of receiving the PRACH configuration index `161` was met as well.
Since we don't want any more changes, we are now done and can run OpenAirInterface5G with the synthesized configuration file `5GAutoConf_test01.conf`, which you can find in the root directory of 5GAutoConf.

**By the way, this is how the following `Example 01: Generic Cell` was synthesized!**

## Example 01: Generic Cell

High-level explanation:

> A generic 5G urban macro cell in the n78 band (TDD) with 40 MHz channel bandwidth, 3.78 GHz center frequency, a medium delay spread, a maximum radius of 1.9 km, and a maximum UE speed of 100 km/h, using an Ettus Research or NI USRP B210 software-defined radio.
> The latest possible subframe number and the maximum possible number of PRACH slots within a subframe shall be used.

See also:
- https://doi.org/10.1109/25.54229 for delay spread at 900 MHz

**Full input command:**

```bash
gnbautoconf -f 78 -b 40 -c 3780 -s b210 n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00 subframe-number=9 n-slot-ra=2
```

**Input Cell Parameters:**

| Parameter | Symbol | Value | CLI (`*kwargs`) Argument | Notes |
| --------- | ------ | ----- | ------------ | ----- |
| NR band |  | `n78` | `-f 78` | `n78` band is `TDD` only |
| Channel bandwidth | `CBW` | $40\,\text{MHz}$ | `-b 40` |  |
| Center frequency | $f_\text{c}$ | $3.78\,\text{GHz}$ | `-c 3780` |  |
| Refractive index | $n$ | $1.000293$ | `n=1.000293` | Refractive index in Air |
| Cell radius | $r_\text{cell}$ | $1.9\,\text{km}$ | `r-cell=1900` |  |
| Max. UE speed | $v_\text{UE,max}$ | $27.78\,\text{m/s} = 100\,\text{km/h}$ | `ue-speed=27.78` |  |
| Max. delay spread | $\tau_\text{d}$ | $15\,\text{µs}$ | `tau-d=15.00` |  |
| Subframe number |  | `9` | `subframe-number=9` |  |
| Number of PRACH slots within a subframe | $n_\text{slot}^\text{RA}$ | `2` | `n-slot-ra=2` |  |

**Intermediate parameters (automatically chosen):**

| Parameter | Symbol | Value | CLI `*kwargs` Argument | Notes |
| --------- | ------ | ----- | ---------------------- | ----- |
| x | $x$ | `1` | `x=1` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number |
| y | $y$ | `0` | `y=0` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number |
| Starting Symbol | $l_0$ | `0` | `starting-symbol=0` |  |
| Number of time-domain PRACH occasions within a PRACH slot | $N_\text{t}^\text{RA,slot}$ | `1` | `n-t-ra-slot=1` |  |
| PRACH occasion duration | $N_\text{dur}^\text{RA}$ | $12\,\text{symbols}$ | `n-dur-ra=12` |  |

**Output Waveform Config Parameters:**

| Parameter | Symbol | Value | Notes |
| --------- | ------ | ----- | ----- |
| Max. RBs | $n_\text{RB,max}$ | $106$ |  |
| Max. occupied Bandwidth | $B_\text{c,max}$ | $39.97\,\text{MHz}$ |  |
| Round-trip delay | $t_\text{RT}$ | $12.68\,\text{µs}$ |  |
| PRACH preamble format |  | $\text{B4}$ |  |
| PRACH subcarrier spacing | $\Delta f_\text{RA}$ | $30\,\text{kHz}$ |  |
| PRACH configuration index |  | `161` | `FR1` and `TDD`: TS 38.211 Table 6.3.3.2-3 |
| Resource Indication Value | `RIV` | $28875$ |  |

## Example 02: Rural Macro Cell (RMa)

High-level explanation:

> A 5G rural macro cell in the n28 band (FDD) with 10 MHz channel bandwidth, 700 MHz center frequency, a low delay spread, a maximum radius of 1.732 km, and a maximum UE speed of 120 km/h, using an Ettus Research or NI USRP B210 software-defined radio.
> The latest possible subframe number shall be used.

See also:
- 3GPP TR 38.901 v18.0.0 for use case
- https://doi.org/10.1109/25.54229 for delay spread at 900 MHz
- https://www.5g-anbieter.info/technik/5g-frequenzen.html for band usage by German telecom operators

**Full input command:**

```bash
gnbautoconf -f 28 -b 10 -c 700 -s b210 n=1.000293 r-cell=1732 ue-speed=33.33 tau-d=2.00 subframe-number=7
```

**Input Cell Parameters:**

| Parameter | Symbol | Value | CLI (`*kwargs`) Argument | Notes |
| --------- | ------ | ----- | ------------ | ----- |
| NR band |  | `n28` | `-f 28` | `n28` band is `FDD` only |
| Channel bandwidth | `CBW` | $10\,\text{MHz}$ | `-b 10` |  |
| Center frequency | $f_\text{c}$ | $700\,\text{MHz}$ | `-c 700` |  |
| Refractive index | $n$ | $1.000293$ | `n=1.000293` | Refractive index in Air |
| Cell radius | $r_\text{cell}$ | $1.732\,\text{km}$ | `r-cell=1732` |  |
| Max. UE speed | $v_\text{UE,max}$ | $33.33\,\text{m/s} = 120\,\text{km/h}$ | `ue-speed=33.33` |  |
| Max. delay spread | $\tau_\text{d}$ | $2\,\text{µs}$ | `tau-d=2.00` |  |
| Subframe number |  | `7` | `subframe-number=7` |  |

**Intermediate parameters (automatically chosen):**

| Parameter | Symbol | Value | CLI `*kwargs` Argument | Notes |
| --------- | ------ | ----- | ---------------------- | ----- |
| x | $x$ | `1` | `x=1` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number |
| y | $y$ | `0` | `y=0` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number |
| Starting Symbol | $l_0$ | `0` | `starting-symbol=0` |  |
| Number of PRACH slots within a subframe | $n_\text{slot}^\text{RA}$ | `2` | `n-slot-ra=2` |  |
| Number of time-domain PRACH occasions within a PRACH slot | $N_\text{t}^\text{RA,slot}$ | `2` | `n-t-ra-slot=2` |  |
| PRACH occasion duration | $N_\text{dur}^\text{RA}$ | $6\,\text{symbols}$ | `n-dur-ra=6` |  |

**Output Waveform Config Parameters:**

| Parameter | Symbol | Value | Notes |
| --------- | ------ | ----- | ----- |
| Max. RBs | $n_\text{RB,max}$ | $24$ |  |
| Max. occupied Bandwidth | $B_\text{c,max}$ | $9.97\,\text{MHz}$ |  |
| Round-trip delay | $t_\text{RT}$ | $11.56\,\text{µs}$ |  |
| PRACH preamble format |  | $\text{C2}$ |  |
| PRACH subcarrier spacing | $\Delta f_\text{RA}$ | $120\,\text{kHz}$ |  |
| PRACH configuration index |  | `250` | `FR1` and `FDD`: TS 38.211 Table 6.3.3.2-2 |
| Resource Indication Value | `RIV` | $6325$ |  |

## Example 03: SmartFactoryOWL (SFOWL)

High-level explanation:

> A 5G industrial micro cell in the n78 band (TDD) with 100 MHz channel bandwidth, 3.75 GHz center frequency, a high delay spread, a maximum radius of 51 m, and a maximum UE speed of 7.2 km/h, using an Ettus Research or NI USRP X300 software-defined radio.

See also:
- https://doi.org/10.1109/WFCS63373.2025.11077649 for SF OWL
- https://doi.org/10.1109/ETFA61755.2024.10710946 for SF OWL
- https://doi.org/10.1109/25.54229 for delay spread at 900 MHz


**Full input command:**

```bash
gnbautoconf -f 78 -b 100 -c 3750 -s x300 n=1.000293 r-cell=51 ue-speed=2 tau-d=20.00
```

**Input Cell Parameters:**

| Parameter | Symbol | Value | CLI (`*kwargs`) Argument | Notes |
| --------- | ------ | ----- | ------------ | ----- |
| NR band |  | `n78` | `-f 78` | `n78` band is `TDD` only |
| Channel bandwidth | `CBW` | $100\,\text{MHz}$ | `-b 100` |  |
| Center frequency | $f_\text{c}$ | $3.75\,\text{GHz}$ | `-c 3750` |  |
| Refractive index | $n$ | $1.000293$ | `n=1.000293` | Refractive index in Air |
| Cell radius | $r_\text{cell}$ | $51\,\text{m}$ | `r-cell=51` |  |
| Max. UE speed | $v_\text{UE,max}$ | $2\,\text{m/s} = 7.2\,\text{km/h}$ | `ue-speed=2` |  |
| Max. delay spread | $\tau_\text{d}$ | $20\,\text{µs}$ | `tau-d=20.00` |  |

**Intermediate parameters (automatically chosen):**

| Parameter | Symbol | Value | CLI `*kwargs` Argument | Notes |
| --------- | ------ | ----- | ---------------------- | ----- |
| x | $x$ | `1` | `x=1` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number |
| y | $y$ | `0` | `y=0` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number |
| Subframe number |  | `9` | `subframe-number=9` |  |
| Starting Symbol | $l_0$ | `2` | `starting-symbol=2` |  |
| Number of PRACH slots within a subframe | $n_\text{slot}^\text{RA}$ | `2` | `n-slot-ra=2` |  |
| Number of time-domain PRACH occasions within a PRACH slot | $N_\text{t}^\text{RA,slot}$ | `6` | `n-t-ra-slot=6` |  |
| PRACH occasion duration | $N_\text{dur}^\text{RA}$ | $2\,\text{symbols}$ | `n-dur-ra=2` |  |

**Output Waveform Config Parameters:**

| Parameter | Symbol | Value | Notes |
| --------- | ------ | ----- | ----- |
| Max. RBs | $n_\text{RB,max}$ | $273$ |  |
| Max. occupied Bandwidth | $B_\text{c,max}$ | $98.28\,\text{MHz}$ |  |
| Round-trip delay | $t_\text{RT}$ | $01.34\,\text{µs}$ |  |
| PRACH preamble format |  | $\text{C0}$ |  |
| PRACH subcarrier spacing | $\Delta f_\text{RA}$ | $30\,\text{kHz}$ |  |
| PRACH configuration index |  | `179` | `FR1` and `TDD`: TS 38.211 Table 6.3.3.2-3 |
| Resource Indication Value | `RIV` | $1099$ |  |

## Example 04: Wireless Backhaul

High-level explanation:

> A high-bandwidth 5G direct link between stationary towers in the n257 mmWave band (TDD) with 400 MHz channel bandwidth, 120 kHz PUSCH SCS, 28 GHz center frequency, a low delay spread, a maximum distance of 3000 m, and a maximum UE speed of 0 km/h, using an Ettus Research or NI USRP X310 software-defined radio.

```{important}
Since no other SDR models are supported yet, we assume the X310 was able to achieve 400 MHz bandwidth for illustrative purposes!
```

**Full input command:**

```bash
gnbautoconf -f 257 -b 400 -r 120 -c 28000 -s x310 n=1.000293 r-cell=3000 ue-speed=0 tau-d=1
```

**Input Cell Parameters:**

| Parameter | Symbol | Value | CLI (`*kwargs`) Argument | Notes |
| --------- | ------ | ----- | ------------ | ----- |
| NR band |  | `n257` | `-f 257` | `n257` band is `TDD` only |
| Channel bandwidth | `CBW` | $400\,\text{MHz}$ | `-b 400` |  |
| Center frequency | $f_\text{c}$ | $28\,\text{GHz}$ | `-c 28000` |  |
| Refractive index | $n$ | $1.000293$ | `n=1.000293` | Refractive index in Air |
| Cell radius | $r_\text{cell}$ | $3000\,\text{m}$ | `r-cell=3000` |  |
| Max. UE speed | $v_\text{UE,max}$ | $0\,\text{m/s} = 0\,\text{km/h}$ | `ue-speed=0` |  |
| Max. delay spread | $\tau_\text{d}$ | $1\,\text{µs}$ | `tau-d=1` |  |

**Intermediate parameters (automatically chosen)**

| Parameter | Symbol | Value | CLI `*kwargs` Argument | Notes |
| --------- | ------ | ----- | ---------------------- | ----- |
| x | $x$ | `1` | `x=1` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number |
| y | $y$ | `0` | `y=0` | Used for $n_\text{f} \mod x = y$, where $n_\text{f}$ is the system frame number |
| Slot number |  | `[19,39]` | `subframe-number=[19,39]` | CLI `*kwarg` is still `subframe-number` |
| Starting Symbol | $l_0$ | `2` | `starting-symbol=2` |  |
| Number of PRACH slots within a 60 kHz slot | $n_\text{slot}^\text{RA}$ | `1` | `n-slot-ra=1` |  |
| Number of time-domain PRACH occasions within a PRACH slot | $N_\text{t}^\text{RA,slot}$ | `2` | `n-t-ra-slot=2` |  |
| PRACH occasion duration | $N_\text{dur}^\text{RA}$ | $6\,\text{symbols}$ | `n-dur-ra=6` |  |

**Output Waveform Config Parameters:**

| Parameter | Symbol | Value | Notes |
| --------- | ------ | ----- | ----- |
| Max. RBs | $n_\text{RB,max}$ | $264$ |  |
| Max. occupied Bandwidth | $B_\text{c,max}$ | $399.88\,\text{MHz}$ |  |
| Round-trip delay | $t_\text{RT}$ | $20.02\,\text{µs}$ |  |
| PRACH preamble format |  | $\text{C2}$ |  |
| PRACH subcarrier spacing | $\Delta f_\text{RA}$ | $60\,\text{kHz}$ |  |
| PRACH configuration index |  | `185` | `FR2` and `TDD`: TS 38.211 Table 6.3.3.2-4 |
| Resource Indication Value | `RIV` | $3574$ |  |
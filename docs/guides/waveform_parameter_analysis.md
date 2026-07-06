(label-waveform-parameter-analysis)=
# Waveform Parameter Analysis

```{important}
**Analysis** refers to analyzing input waveform parameters regarding their cell parameter performances.
```

```{important}
Analysis mode is activated by providing only the CLI arguments listed below and no `*kwargs` parameter.
```

```{important}
Contrary to synthesis mode, all CLI arguments (parameters) need to be supplied for analysis mode.
```

```{hint}
Some of the parameters are computed based on optimization, such as SSB parameters and AbsoluteFrequencyPointA.
This also happens in synthesis mode.
```

```{hint}
`5g_config.json` contains a JSON version of the synthesized configuration.
This can be used to convert the configuration file for other OSS stacks and platforms.
```

## CLI Arguments

The following options are mainly used for the **Analysis Mode**, while some are also used for **Synthesis Mode**.

| Short | Long | Choices | Default | Description |
|-------|------|---------|---------|-------------|
| `-h`| `--help`|  |  | Show the help message and exit. |
| `-f`| `--frequencyband`|  | `78` | The 5G NR frequency band. |
| `-b`| `--bandwidth`|  | `40` | The bandwidth in MHz of the channel to be configured. |
| `-r`| `--raster`|  | `30` | The ΔFRaster in kHz. This corresponds to the subcarrier spacing SCS. |
| `-d`| `--duplex`| `TDD`, `FDD` | `TDD` | **DEPRECATED** The Duplex mode. This serves no function anymore, since the frequency band already defines the duplex mode. |
| `-c`| `--center`|  | `3619.2` | The desired center frequency in MHz of the channel to be configured. |
| `-s`| `--sdr`| `b200`, `b210`, `x300`, `x310`, `none` | `b210` | The Software Defined Radio model being used. |
| `-l`| `--loglevel`| `debug`, `info`, `warning`, `error`, `critical` | `info` | The logging level for printing to the console. The logfile is always at level `debug`. |

## Static Settings

```{important}
Static settings are not expected to need changes when configuring the same gNB.
```

Static settings are defined in `static_settings.json`.
These settings mostly refer to gNB and cell identification, PLMN, and network configurations.

## Analysis Walkthrough

```{note}
5GAutoConf will always analyze a working configuration, even if only some CLI arguments are defined, by using the default choices.
```

Since the analysis mode is not fully implemented yet, certain parameters still need to be either defined in the source code or provided as CLI arguments.

**Step 1:** Run the `gnbautoconf` command only with the cell parameters you already know.

For example: 
- 5G band `n78`: `-f 78`
- channel bandwidth $40\,\text{MHz}$: `-b 40`
- subcarrier spacing $30\,\text{kHz}$: `-r 30`
- center frequency $3.78\,\text{GHz}$: `-c 3780`

```bash
gnbautoconf -f 78 -b 40 -r 30 -c 3780 -s b210
```

**Step 2:** 5GAutoConf will derive the remaining cell configuration parameters and generate a configuration file in the root directory, named according to the parameters used (here: `gnb.sa.band78.fr1.106PRB.usrpb210.open5gs.generated.conf`).

The derived cell configuration parameters can be read from the terminal output:

```
----------- ANALYSIS MODE -----------
5G NR Frequency Band = n78 [CLI Argument]
5G NR Channel Bandwidth (CBW) = 40 MHz [CLI Argument]
5G NR Subcarrier Spacing (SCS) = 30 kHz [CLI Argument]
5G NR Numerology = 1
5G NR Cyclic Prefix = Normal
5G NR Support for Data = True
5G NR Support for Synch = True
5G NR Number of OFDM symbols per slot = 14
5G NR Number of slots per radio frame = 20
5G NR Number of slots per subframe = 2
5G NR Slot duration = 0.5 ms
5G NR OFDM Symbol duration = 35.71 us
5G NR Duplex Mode = TDD [CLI Argument]
5G NR Channel Center Frequency = 3780 MHz [CLI Argument]
5G NR Guard Bandwidth = 0.905 MHz
5G NR Band Lower Limit = 3760.0 MHz
5G NR Band Upper Limit = 3800.0 MHz
5G NR Frequency Range Designation = FR1
5G NR Corresponding Frequency Range = (410000000, 7125000000)
5G NR Bandwidth per Resource Block (RB) = 0.36 MHz
5G NR Maximum Number of Resource Blocks (RBs) = 106
5G NR Maximum Transmission Bandwidth = 38.16 MHz
5G NR Maximum Occupied Channel Bandwidth = 39.97 MHz
absoluteFrequencySSB (ARFCN) = 652032
absoluteFrequencySSB = 3780.48 MHz
absoluteFrequencyPointA (ARFCN) = 650728
absoluteFrequencyPointA (frequency) = 3760.92 MHz
absoluteFrequencyPointA k_SSB = 4
absoluteFrequencyPointA offsetToPointA = 44 RBs
NR Resource Indication Value (RIV) = 28875
5G NR Starting Resource Block (rb_start) = 0
```

**Step 3:** Analysis results are stored to a text file with the same naming scheme as the configuration file (here: `gnb.sa.band78.fr1.106PRB.usrpb210.open5gs.generated.results.txt`).

```
L_RA: 139
Delta f_RA: 30 kHz
Delta f: 30 kHz
RACH Occasion starting symbols: (0,)
Restricted set: 
Cyclic Prefix Extended: False
SSB Case: C
Downlink Symbols: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243)
Flexible Symbols: (104, 105, 106, 107, 244, 245, 246, 247)
Uplink Symbols: (108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279)
Number of P per NR Radio Frame: 2
Guard Period: 4.0 OFDM Symbols
              142.857 us
PRACH Occasion Symbols: (266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277)
PRACH Preamble Format:  A2
Message 1 FDM Index: 0
Number of PUSCH Resource Blocks occupied by PRACH: 12 Resource Blocks
                                                   360.0 kHz
Cyclic Prefix duration for PUSCH: 4.688 us
Cyclic Prefix duration for PRACH: 576 samples
                                  9.375 us
Maximum gNB cell radius (ignoring N_CS for now): 519.537 m
Short PRACH Guard Time: 0.149 us
Max. cell size with short GT: 0.022 km
No long PRACH Guard Time available
Max. Delay Spread: 4.688 us
Max. Round-Trip Delay: 4.836 us
Max. cell size according to RTD_max: 724.945 m
```

## Example 01: Generic Cell

High-level explanation:

> A 5G cell in the n78 band (TDD) with 40 MHz channel bandwidth, 30 kHz subcarrier spacing, and 3.78 GHz center frequency, using an Ettus Research or NI USRP B210 software-defined radio.

**Full input command:**

```bash
gnbautoconf -f 78 -b 40 -r 30 -c 3780 -s b210
```

**Input Waveform Parameters:**

| Parameter | Symbol | Value | CLI (`*kwargs`) Argument | Notes |
| --------- | ------ | ----- | ------------ | ----- |
| NR band |  | `n78` | `-f 78` | `n78` band is `TDD` only |
| Channel bandwidth | `CBW` | $40\,\text{MHz}$ | `-b 40` |  |
| Subcarrier spacing | `SCS` | $30\,\text{kHz}$ | `-r 30` |  |
| Center frequency | $f_\text{c}$ | $3.78\,\text{GHz}$ | `-c 3780` |  |
| Software-defined radio |  | `b210` | `-s b210` | Corresponds to Ettus Research USRP B210 |

**Output Cell Parameters:**

```
5G NR OFDM Symbol duration = 35.71 us
5G NR Guard Bandwidth = 0.905 MHz
5G NR Band Lower Limit = 3760.0 MHz
5G NR Band Upper Limit = 3800.0 MHz
5G NR Bandwidth per Resource Block (RB) = 0.36 MHz
5G NR Maximum Number of Resource Blocks (RBs) = 106
5G NR Maximum Transmission Bandwidth = 38.16 MHz
5G NR Maximum Occupied Channel Bandwidth = 39.97 MHz
absoluteFrequencySSB (ARFCN) = 652032
absoluteFrequencySSB = 3780.48 MHz
absoluteFrequencyPointA (ARFCN) = 650728
absoluteFrequencyPointA (frequency) = 3760.92 MHz
absoluteFrequencyPointA k_SSB = 4
absoluteFrequencyPointA offsetToPointA = 44 RBs
NR Resource Indication Value (RIV) = 28875
5G NR Starting Resource Block (rb_start) = 0
```

**Analysis Results:**

```
L_RA: 139
Delta f_RA: 30 kHz
Delta f: 30 kHz
RACH Occasion starting symbols: (0,)
Restricted set: 
Cyclic Prefix Extended: False
SSB Case: C
Downlink Symbols: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243)
Flexible Symbols: (104, 105, 106, 107, 244, 245, 246, 247)
Uplink Symbols: (108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279)
Number of P per NR Radio Frame: 2
Guard Period: 4.0 OFDM Symbols
              142.857 us
PRACH Occasion Symbols: (266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277)
PRACH Preamble Format:  A2
Message 1 FDM Index: 0
Number of PUSCH Resource Blocks occupied by PRACH: 12 Resource Blocks
                                                   360.0 kHz
Cyclic Prefix duration for PUSCH: 4.688 us
Cyclic Prefix duration for PRACH: 576 samples
                                  9.375 us
Maximum gNB cell radius (ignoring N_CS for now): 519.537 m
Short PRACH Guard Time: 0.149 us
Max. cell size with short GT: 0.022 km
No long PRACH Guard Time available
Max. Delay Spread: 4.688 us
Max. Round-Trip Delay: 4.836 us
Max. cell size according to RTD_max: 724.945 m
```
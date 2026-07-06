# Cell Configuration Parameter Computation


## Sources

- [\[0\] Fliedner, Niels Hendrik; Klingler, Florian; Trsek, Henning: "5GAutoConf: A Rapid Data-Driven Autoconfiguration Tool for 5G Base Stations," in *2026 22nd International Conference on Distributed Computing in Smart Systems and the Internet of Things (DCOSS-IoT)*, 2026.](https://www.th-owl.de/elsa/record/13829)
- [\[1\] Greenwood, D. and Hanzo, L.: "Characterisation of Mobile Radio Channels", in Steele, Raymond (Ed.) and Hanzo, Lajos (Ed.): "Mobile Radio Communications, 2nd Edition," Wiley, 1999](https://ieeexplore.ieee.org/document/5271272)
- [\[2\] Rappaport, Theodore S.: "Wireless Communications - Principles and Practice, 2nd Edition," Prentice Hall, 2002](https://openlibrary.org/books/OL3582348M/Wireless_communications)
- [\[3\] Cox,Christopher: "An Introduction To 5G : The New Radio, 5G Network, 5G Advanced and Beyond"](https://ebookcentral.proquest.com/lib/th-owl/detail.action?docID=32055379)
- [\[4\] Chakrapani, Arvind: "On the Design Details of SS/PBCH, Signal Generation and PRACH in 5G-NR", IEEE Access, 2020](https://ieeexplore.ieee.org/document/9144579)
- [\[5\] 3GPP TS 38.331 V19.1.0 (2026-02): "Radio Resource Control (RRC)"](https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/19.01.00_60/ts_138331v190100p.pdf)
- [\[6\] 3GPP TS 38.211 V18.2.0 (2024-05): "Physical channels and modulation"](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/18.02.00_60/ts_138211v180200p.pdf)

## Cell Parameter Computation

The following theory is based on the accompanying paper: Niels Hendrik Fliedner, Florian Klingler, Henning Trsek, "5GAutoConf: A Rapid Data-Driven
Autoconfiguration Tool for 5G Base Stations," in *2026 22nd International Conference on Distributed Computing in Smart Systems and the Internet of Things (DCOSS-IoT)*, 2026 [\[0\]](https://ias-git.init.th-owl.de/space_niels_fliedner/paper-dcoss-iot-2026).
If you are using the equations below in your published work, pleace cite the paper.

### Input Parameters

| Variable | Name | Unit | Description |
| -------- | ---- | ---- | ----------- |
| $t_\text{RT,max}$ | maximum round-trip delay | seconds |  |
| $r_\text{cell,max}$ | maximum physical cell radius | meters |  |
| $\tau_\text{d,max}$ | maximum delay spread |  |  |
| $T_\text{C,min}$ | minimum channel coherence time | seconds |  |
| $v_\text{max}$ | maximum speed in channel | meters per second | Either UE motion with maximum speed relative to the BS antenna (resulting in Doppler shift) in combination with multipath propagation, or reflective structures moving in the radio channel |

### Minimum Channel Coherence Time

Based on either UE motion with maximum speed relative to the BS antenna (resulting in maximum Doppler shift $D_\text{s,max}$) in combination with multipath propagation, or reflective structures moving in the radio channel.

```{math}
T_\text{C,min} = \frac{1}{D_\text{s,max}} = \frac{c_n}{2 \cdot v_\text{max} \cdot f_\text{c}} = \frac{c_0}{n \cdot 2 \cdot v_\text{max} \cdot f_\text{c}}~~~(1)
```

| Variable | Name | Unit | Description |
| -------- | ---- | ---- | ----------- |
| $D_\text{s,max}$ | maximum Doppler shift |  |  |
| $f_\text{c}$ | center frequency of the transmitter | hertz |  |
| $c_n$ | speed of light in a medium with refractive index $n$ | meters per second |  |
| $n$ | refractive index of a medium; $n=0$ for vacuum |  |  |

$(1)$ is based on the following estimation, that suggests a time duration during which a Rayleig fading signal may fluctuate wildly [\[2\]](https://openlibrary.org/books/OL3582348M/Wireless_communications):

```{math}
T_\text{C} \approx \frac{1}{D_\text{s}}~~~(1a)\\
D_\text{s} = 2 \cdot \frac{v_\text{max}}{c_n} \cdot f_\text{c} = 2 \cdot \frac{n \cdot v_\text{max}}{c_0} \cdot f_\text{c}~~~(1b)
```

A more conservative estimate was established in [\[1\]](https://ieeexplore.ieee.org/document/5271272), where $J_0()$ is the zero order Bessel function of the first kind and $D_\text{s} = \frac{v}{c}$ is assumed (which reads like a typo due to missing $f_\text{c}$):

```{math}
T_\text{C}(t) = \frac{J_0^2(2 \pi D_\text{s} \Delta t)}{2} \approx \frac{9}{16 \pi D_\text{s}}~~~(1c)
```

Using $(1b)$:

```{math}
T_\text{C}(t) \approx \frac{9 n}{16 \pi \cdot 2 \cdot v_\text{max} \cdot f_\text{c} \cdot c_0}~~~(1d)
```

A popular rule of thumb for modern digital communications is the geometric mean of $(1a)$ and $(1c)$ [\[2\]](https://openlibrary.org/books/OL3582348M/Wireless_communications):

```{math}
T_\text{C}(t) = \sqrt{\frac{9}{16 \pi D_\text{s} \cdot \frac{1}{D_\text{s}}}} = \sqrt{\frac{9}{16 \pi}} \cdot \frac{1}{D_\text{s}}~~~(1e)
```

Using $(1b)$:

```{math}
T_\text{C}(t) = \sqrt{\frac{9}{16 \pi}} \cdot \frac{c_0}{2 \cdot n \cdot v_\text{max} \cdot f_\text{c}}~~~(1f)
```

### PRACH Guard Times

#### PRACH Formats Other Than A1-A3

For all PRACH formats except A1-A3, a GT $T_\text{GT}$ occurs after the rearmost ZC sequence due to additional time resources within the assigned RO duration.
Here, the PRACH CP mainly constraints $\tau_\text{d,max}$ as well as other minor timing uncertainties.

```{math}
t_\text{RT,max} \leq T_\text{GT,min} = \left( N_\text{dur}^\text{RA} - (N_\text{CP}^\text{RA} + N_\text{u}) \right) \cdot \kappa \cdot T_\text{c}~~~(2)
```

**Variables:**

- [$\kappa$](label-glossary-kappa)
- [$N_\text{CP}^\text{RA}$](label-glossary-n-cp-ra)
- [$N_\text{dur}^\text{RA}$](label-glossary-n-dur-ra)
- [$N_\text{u}$](label-glossary-n-u)
- [$T_\text{c}$](label-glossary-t-c)

##### PRACH Formats 0-3

For PRACH formats 0-3 $N_\text{dur}^\text{RA} = 0$ applies, meaning that the specific PRACH resources to be reserved are not aligned to the overall time resource grid and thus not fully defined.
Here, an implicit GT duration can not be clearly assumed from the standard.
This creates a discrepancy between the standard, existing integrations, and scientific publications, some of which have published figures without disclosing the basics of their calculations.
Accordingly, we replace $N_\text{dur}^\text{RA}$ in $T_\text{GT,min}$ by the smallest number of subframes in the PRACH reference grid to exceed $N_\text{CP}^\text{RA} + N_\text{u}$, $n_\text{subframes}$, in agreement with Cox [\[3\]](https://ebookcentral.proquest.com/lib/th-owl/detail.action?docID=32055379). 
The resulting implicit GTs are thus roughly similar to values previously published in Chakrapani [\[4\]](https://ieeexplore.ieee.org/document/9144579).

```{math}
n_\text{subframes} = \min \lbrace n \in \mathbb{N}  \mid n \cdot 1\,\text{ms} \geq N_\text{CP}^\text{RA} + N_\text{u} \rbrace\\
t_\text{RT,max} \leq T_\text{GT,min} = \left( n_\text{subframes} - (N_\text{CP}^\text{RA} + N_\text{u}) \right) \cdot \kappa \cdot T_\text{c}
```

**Variables:**

- [$\kappa$](label-glossary-kappa)
- [$N_\text{CP}^\text{RA}$](label-glossary-n-cp-ra)
- [$N_\text{u}$](label-glossary-n-u)
- [$T_\text{c}$](label-glossary-t-c)

### PRACH Subcarrier Spacing

#### PRACH Formats A1-A3

For PRACH formats `A1-A3` no GT is implied in the specification and the PRACH preamble fully utilizes its slot duration.
Thus, the PRACH preamble's CP constraints both $t_\text{RT,max}$ and $\tau_\text{d,max}$, as well as other minor timing uncertainties.

The formats `A1-A3` are designed for very small $r_\text{cell,max}$, since any $t_\text{RT,max}$ longer than a few samples causes the PRACH sequence to leak into the subsequently scheduled data and control channels.
This is exacerbated if $\tau_\text{d,max}$ is at least as long as the CP of these subsequent channels, requiring CP adjustment.

As specified in the following equation, the upper bound for the PRACH SCS $\Delta f_\text{RA,max}$ depends on both $t_\text{RT,max}$ and $\tau_{d,max}$:

```{math}
\Delta f_\text{RA,max} = 15\,\text{kHz} \cdot 2^{\mu_\text{RA,max}} \\
\mu_\text{RA,max} = \lfloor -\log_2 \Bigl( \frac{\tau_\text{d,max} + t_\text{RT,max}}{N_\text{CP,pre}^\text{RA} \cdot \kappa \cdot T_\text{c} } \Bigr) \rfloor~~~(3)\\ 
N_\text{CP}^\text{RA} = N_\text{CP,pre}^\text{RA} \cdot \kappa \cdot 2^{-\mu_\text{RA}}~~~(4)
```

The lower bound for the PRACH SCS $\Delta f_\text{RA,min}$ depends on $T_\text{C,min}$ to preserve the ZC sequence's autocorrelation properties.
Deriving $\mu_\text{RA,min}$ from $T_\text{C,min}$ is specified in the following equation.

```{math}
\Delta f_\text{RA,min} = 15\,\text{kHz} \cdot 2^{\mu_\text{RA,min}}\\
\mu_\text{RA,min} = \lceil -\log_2 \Bigl( \frac{T_\text{C,min}}{N_\text{ZC}\cdot \kappa \cdot T_\text{c} } \Bigr) \rceil~~~(5)
```

**Variables:**

- [$\kappa$](label-glossary-kappa)
- [$N_\text{CP}^\text{RA}$](label-glossary-n-cp-ra)
- [$N_\text{CP,pre}^\text{RA}$](label-glossary-n-cp-pre-ra)
- [$N_\text{dur}^\text{RA}$](label-glossary-n-dur-ra)
- [$N_\text{u}$](label-glossary-n-u)
- [$T_\text{c}$](label-glossary-t-c)

#### All Other PRACH Formats

Since a GT occurs for all PRACH formats other than `A1-A3`, the equation for $\mu_\text{RA,max}$ is changed accordingly by omitting $t_\text{RT,max}$:

```{math}
\mu_\text{RA,max} = \lfloor -\log_2 \Bigl( \frac{\tau_\text{d,max}}{N_\text{CP,pre}^\text{RA} \cdot \kappa \cdot T_\text{c} } \Bigr) \rfloor\\ 
N_\text{CP}^\text{RA} = N_\text{CP,pre}^\text{RA} \cdot \kappa \cdot 2^{-\mu_\text{RA}}~~~(4)
```

To preserve the autocorrelation properties of a singular ZC sequence of length $N_\text{ZC}$, the lower bound for the PRACH SCS $\Delta f_\text{RA,min}$, via $\mu_\text{RA,min}$, depends on $T_\text{C,min}$ (see the following equation). 

```{math}
\Delta f_\text{RA,min} = 15\,\text{kHz} \cdot 2^{\mu_\text{RA,min}}\\
\mu_\text{RA,min} = \lceil -\log_2 \Bigl( \frac{T_\text{C,min}}{N_\text{ZC} \cdot \kappa \cdot T_\text{c} } \Bigr) \rceil~~~(5)
```

**Variables:**

- [$\kappa$](label-glossary-kappa)
- [$N_\text{CP}^\text{RA}$](label-glossary-n-cp-ra)
- [$N_\text{CP,pre}^\text{RA}$](label-glossary-n-cp-pre-ra)
- [$N_\text{u}$](label-glossary-n-u)
- [$T_\text{c}$](label-glossary-t-c)

### PRACH Sequence Length

A longer $N_\text{ZC}$ produces a higher correlation peak, which increases the required minimum detection threshold.
Then, the lower bound for the minimum ZC sequence length $N_\text{ZC,min}$ issued for PRACH is defined by the overall link budget $P_\text{rx}$ in dB, as shown in the following equation.

```{math}
N_\text{ZC,min} = \min \lbrace N\in \{139,571,839,1151\} \mid N \geq 10^\frac{P_\text{rx}}{20\,\text{dB}} \rbrace~~~(6)
```

Using $N_\text{ZC}=839$ is limited to PRACH formats $\{0, 1, 2, 3\}$ and $N_\text{ZC}=\{139, 571, 1151\}$ are limited to remaining PRACH formats.

$T_\text{C,min}$ defines the upper bound for the maximum ZC sequence length $N_\text{ZC,max}$, including $N_\text{CP}^\text{RA}$ to preserve its correlation properties, as described in the following equation.

```{math}
N_\text{ZC,max} + N_\text{CP}^\text{RA} \leq T_\text{C,min}~~~(7)
```

**Variables:**

- [$N_\text{CP}^\text{RA}$](label-glossary-n-cp-ra)
- [$N_\text{u}$](label-glossary-n-u)

### Overall Subcarrier Spacing

The choice of the SCS varies between PRACH and subsequent data and control channels, the latter of which are subjected to the TA command [\[5\]](https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/19.01.00_60/ts_138331v190100p.pdf).

Hence, the upper limit for a channel's SCS $\Delta f_\text{max}$ is defined by the CP duration $N_{\text{CP},l}^\mu$ being the upper bound for $\tau_{d,\text{max}}$.
This is analogous to $\Delta f_\text{RA,max}$ for all PRACH formats other than `A1-A3`.
The equation below describes the computation for the respective $\mu_\text{max}$.
Since $\Delta f_\text{max}$ is limited by shorter symbol durations, the relevant $N_{\text{CP},l}^\mu$ is computed for OFDM symbols $l\neq0$ und $l\neq7\cdot2^\mu$.
Following [\[6\]](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/18.02.00_60/ts_138211v180200p.pdf), the factor $144$ is replaced with $512$ for the extended CP option.

```{math}
\Delta f_\text{max} = 15\,\text{kHz} \cdot 2^{\mu_\text{max}}\\
\mu_\text{max} = \lfloor -\log_2 \Bigl( \frac{\tau_\text{d,max}}{144 \cdot \kappa \cdot T_\text{c} } \Bigr) \rfloor~~~(8)\\
\mu_\text{max} = \lfloor -\log_2 \Bigl( \frac{\tau_\text{d,max}}{512 \cdot \kappa \cdot T_\text{c} } \Bigr) \rfloor\text{~~~for extended CP}
```

Similarly to $\Delta f_\text{RA,min}$, the lower limit for a channel's SCS $\Delta f_\text{min}$ is defined by $T_\text{C,min}$ given in the equation for $T_\text{C,min}$.
To preserve the circular convolution properties and thus the orthogonality, $T_\text{C,min} \geq N_{\text{CP},l}^\mu + N_\text{u}^\mu$ needs to apply.
The equation below computes the respective $\mu_\text{min}$.

```{math}
\Delta f_\text{min} = 15\,\text{kHz} \cdot 2^{\mu_\text{min}}\\
\mu_\text{min} = \lceil -\log_2 \Bigl( \frac{T_\text{C,min}-16\cdot \kappa \cdot T_\text{c}}{2192 \cdot \kappa \cdot T_\text{c} } \Bigr) \rceil~~~(9)
```

The equations for $N_{\text{CP},l}^\mu$ and the OFDM symbol duration $N_\text{u}^\mu$ for all signals except PRACH and RIM-RS are given by the 5G TS in [\[6\]](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/18.02.00_60/ts_138211v180200p.pdf).
Computing separate SCSs for all channels subsequent to PRACH offers an optimization opportunity for the 5G BS's configuration by freeing up resources otherwise used to mitigate $t_\text{RT,max}$ in PRACH.

**Variables:**

- [$\kappa$](label-glossary-kappa)
- [$T_\text{c}$](label-glossary-t-c)
# Terms and Symbols

## Symbols

(label-glossary-beta)=
### $\beta$

Amplitude scaling for a physical channel/signal.
Source: [\[1\] TS 38.211, ch. 3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-beta-prach)=
### $\beta_\text{PRACH}$

Amplitude scaling factor in order to conform to the transmit power specified in [\[2\] TS 38.213](https://www.etsi.org/deliver/etsi_ts/138200_138299/138213/19.03.00_60/ts_138213v190300p.pdf).
Source: [\[2\] TS 38.213](https://www.etsi.org/deliver/etsi_ts/138200_138299/138213/19.03.00_60/ts_138213v190300p.pdf)

---

(label-glossary-c-v)=
### $C_v$

The cyclic shift.
Source: [\[1\] TS 38.211, ch. 6.3.3.1](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-delta-f)=
### $\Delta f$

The subcarrier spacing $\Delta f = 2^\mu \cdot 15\,\text{kHz}$.
Source: [\[1\] TS 38.211, ch. 3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-delta-f-ra)=
### $\Delta f_\text{RA}$

The subcarrier spacing used for the PRACH. The choice of subcarrier spacing affects the preamble's duration and the total bandwidth of the PRACH.

---

(label-glossary-i)=
### $i$

Zadoff-Chu sequence logical index.
Source: [\[1\] TS 38.211, Tables 6.3.3.1-3, 6.3.3.1-4, 6.3.3.1-4A, and 6.3.3.1-4B](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-bar-k)=
### $\bar{k}$

Defined in [\[1\] TS 38.211, ch. 6.3.3](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf).
Source: [\[1\] TS 38.211, ch. 5.3.2 and ch. 6.3.3](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-kappa)=
### $\kappa$

A constant, where $\kappa =$ [$T_\text{s}$](label-glossary-t-s) $/$ [$T_\text{c}$](label-glossary-t-c) $= 64$.
Source: [\[1\] TS 38.211, ch. 3.2, 4.1](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-l)=
### $l$

RACH Start symbol number(s) in 30 kHz (for FR1) or 120 kHz (for FR2) reference grid, given by $l =$ [$l_0$](label-glossary-l-0) $+$ [$n_\text{t}^\text{RA}$](label-glossary-n-t-ra) $\cdot$ [$N_\text{dur}^\text{RA}$](label-glossary-n-dur-ra) $+ 14 \cdot$ [$n_\text{slot}^\text{RA}$](label-glossary-n-slot-ra), used to compute $t_{\text{start,}l}^\mu$. The reference grid is assumed to always start at symbol 0 of "Subframe number" of TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-3 (15 kHz reference grid, which equals subframe grid, for [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) $\in \{1.25, 5, 15, 30\}\,\text{kHz}$) or "Slot number" of TS 38.211 Table 6.3.3.2-4 (60 kHz reference grid for [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) $\in \{60, 120, 480, 960\}\,\text{kHz}$).
Source: [\[1\] TS 38.211, ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-l-0)=
### $l_0$

The PRACH sequence starting symbol number within a PRACH slot of the chosen [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) grid **(or 30 kHz/120 kHz reference grid??)**, given by the parameter "starting symbol" in TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-4. $l_0 = 0$ refers to the first symbol in the chosen slot of the chosen [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) grid.
Source: [\[1\] TS 38.211, ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-l-max)=
### $L_\text{max}$

A maximum number of SS/PBCH block indexes in a cell, and the maximum number of transmitted SS/PBCH blocks within a half frame.
Source: [\[2\] TS 38.213, ch. 4.1](https://www.etsi.org/deliver/etsi_ts/138200_138299/138213/19.03.00_60/ts_138213v190300p.pdf)

---

(label-glossary-l-ra)=
### $L_\text{RA}$

The length of the Random Access Preamble sequence in the frequency domain, given in number of subcarriers used. A longer sequence requires more narrow SCS, which then leads to longer OFDM symbols. This allows for more extensive coverage and longer propagation delay.

---

(label-glossary-l-rbs)=
### $L_\text{RBs}$

The maximum number of Resource Blocks (RBs).

---

(label-glossary-mu)=
### $\mu$

The subcarrier spacing configuration (or: numerology).

---

(label-glossary-n-cp-ra)=
### $N_\text{CP}^\text{RA}$

Specifies the length of the cyclic prefix in terms of the number of samples for the PRACH preamble. Different PRACH formats will have different $N_\text{CP}^\text{RA}$ values based on the expected propagation environment and subcarrier spacing used.
Source: [\[1\] TS 38.211, Tables 6.3.3.1-1 to 6.3.3.1-2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-cp-l-ra)=
### $N_{\text{CP,}l}^\text{RA}$

$N_{\text{CP,}l}^\text{RA} =$ [$N_\text{CP}^\text{RA}$](label-glossary-n-cp-ra) $+$ $n \cdot 16$ [$\kappa$](label-glossary-kappa). For [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) $\in \{1.25,5\}\,\text{kHz}$: $n=0$. For [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) $\in \{15,30,60,120,480,960\}\,\text{kHz}$, $n$ is the number of times the interval $[$[$t_\text{start}^\text{RA}$](label-glossary-t-start-ra)$,$ [$t_\text{start}^\text{RA}$](label-glossary-t-start-ra)$+ (N_\text{u}^\text{RA} +$ [$N_\text{CP}^\text{RA}$](label-glossary-n-cp-ra)$) \cdot$ [$T_\text{c}$](label-glossary-t-c) $]$ overlaps with either time instance 0 or time instance $(\Delta f_\text{max} \cdot N_\text{f} / 2000) \cdot$ [$T_\text{c}$](label-glossary-t-c) $= 0.5\,\text{ms}$ in a subframe. In other words, every $0.5\,\text{m}$, a cyclic prefix with a longer duration is required to pad the number of OFDM symbols used for fitting into the subframe.
Source: [\[1\] TS 38.211, ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-cp-l-mu)=
### $N_{\text{CP,}l}^\mu$

The cyclic prefix duration for any physical channel or signal except PRACH.
Source: [\[1\] TS 38.211, ch. 5.3.1 and ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-cp-l-1-mu)=
### $N_{\text{CP,}l-1}^\mu$

Defined in [\[1\] TS 38.211, ch. 5.3.1 and ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf).
Source: [\[1\] TS 38.211, ch. 5.3.1 and ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-cp-pre-ra)=
### $N_\text{CP,pre}^\text{RA}$

The prefix of the [$N_\text{CP}^\text{RA}$](label-glossary-n-cp-ra) equations from [\[1\] TS 38.211, Tables 6.3.3.1-1 to 6.3.3.1-2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf).
Source: [\[1\] TS 38.211, Tables 6.3.3.1-1 to 6.3.3.1-2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-cs)=
### $N_\text{CS}$

Cyclic Shift Number, determines the size of the cyclic shift applied to the root sequence to generate multiple PRACH preamble sequences. Maximum possible value is $($[$L_\text{RA}$](label-glossary-l-ra)$-1)/2$.
Source: [\[1\] TS 38.211 Tables 6.3.3.1-5, 6.3.3.1-6, and 6.3.3.1-7](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-dur-ra)=
### $N_\text{dur}^\text{RA}$

PRACH occasion (RO) duration, given in number of symbols of the chosen [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) grid.
Source: [\[1\] TS 38.211, Tables 6.3.3.2-2 to 6.3.3.2-4](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-f)=
### $n_\text{f}$

System frame number (SFN) ([\[1\] TS 38.211 clause 3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)), integer in range `(0 ... 1023)` (TS 38.331).

In TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-4, it is part of a column header $n_\text{f} \mod x = y$, with subheaders $x$ and $y$.
It is assumed that this works as a normative definition, or rather a selection condition on the domain of applicability of the table entry.
Accordingly, this would be interpreted as:
**PRACH occasions are defined for radio frames satisfying $n_\text{f} \mod x = y$** ([\[29\]](https://www.techedgewireless.com/post/5g-nr-rach-procedure-in-detail))

**Available combinations**

| $x$ | $y$ | Applicable frames for PRACH |
| --- | --- | --------------------------- |
| 16 | 1 | \[1, 17, 33, 49, ..., 1009\] = ${n \cdot 16 + 1 \mid n \in {0,1,...,63}}$ |
| 16 | 1,2 | \[1, 2, 17, 18, ..., 1010\] = ${n \cdot 16 + 1 \mid n \in {0,1,...,63}} \cup {n \cdot 16 + 2 \mid n \in {0,1,...,63}}$ |
| 8 | 1 | \[1, 9, 17, 25, 33, ..., 1017\] = ${n \cdot 8 + 1 \mid n \in {0,1,...,127}}$ |
| 8 | 1,2 | \[1, 2, 9, 10 ..., 1018\] = ${n \cdot 8 + 1 \mid n \in {0,1,...,127}} \cup {n \cdot 8 + 1 \mid n \in {0,1,...,127}}$ |
| 4 | 1 | \[1, 5, 9, 13, 17, ..., 1021\] = ${n \cdot 4 + 1 \mid n \in {0,1,...,255}}$ |
| 4 | 1,2 | \[1, 2, 5, 6, ..., 1022\] = ${n \cdot 4 + 1 \mid n \in {0,1,...,255}} \cup {n \cdot 4 + 2 \mid n \in {0,1,...,255}}$ |
| 2 | 1 | \[1, 3, 5, 9, 11, ..., 1023\], every odd frame |
| 2 | 0 | \[0, 2, 4, 6, ... 1022\], every even frame |
| 1 | 0 | \[0, 1, 3, 4, ... 1023\], every frame |


**More definitions**

5.2.2.2.2 SI change indication and PWS notification --> SIB messaging (also SIB1)

> The modification period boundaries are defined by SFN values for which SFN mod m = 0, where m is the number of radio frames comprising the modification period. The modification period is configured by system information. If H-SFN is provided in _SIB1_, and UE is configured with eDRX, modification period boundaries are defined by SFN values for which (H-SFN * 1024 + SFN) mod _m_ = 0.

5.2.2.3.2 Acquisition of an SI message:

> ... the SI-window starts at the slot #_a_, where _a = x_ mod N, in the radio frame for which SFN mod _T_ = FLOOR(_x_/N), where _T_ is the _si-Periodicity_ of the concerned SI message and N is the number of slots in a radio frame as specified in TS 38.211

5.5.2.10 Reference signal measurement timing configuration:

> The UE shall setup the first SS/PBCH block measurement timing configuration (SMTC) in accordance with the received periodicityAndOffset parameter (providing Periodicity and Offset value for the following condition) in the SSB-MTC configuration. The first subframe of each SMTC occasion occurs at an SFN and subframe of the NR SpCell meeting the following condition:
> 
> SFN mod T = (FLOOR (Offset/10));

6.2.2 Message definitions

_MIB_ (pages 543-544)

> _*systemFrameNumber*_
> The 6 most significant bits (MSB) of the 10-bit System Frame Number (SFN). The 4 LSB of the SFN are conveyed in the PBCH transport block as part of channel coding (i.e. outside the MIB encoding), as defined in clause 7.1 in TS 38.212.

_UEAssistanceInformation_ (page 620)

> `ReferenceSFN-AndSlot-r18 ::= SEQUENCE {`
> `    referenceSFN-r18 INTEGER (0..1023),`
> `    referenceSlot-r18 INTEGER (0..639)`
> `}`

6.3.1 System information blocks

_deriveSSB-IndexFromCell_ (page 667)

> This field indicates whether the UE can utilize serving cell timing to derive the index of SS block transmitted by neighbour cell. If this field is set to true, the UE assumes SFN and frame boundary alignment across cells on the serving frequency as specified in TS 38.133

_EpochTime_ (page 891)

> The IE _EpochTime_ is used to indicate the epoch time for the NTN assistance information ...
> ...
> _*sfn*_
> For serving cell, it indicates the current SFN or the next upcoming SFN after the frame where the message indicating the _epochTime_ is received. For neighbour or target cell when explicit epoch time is present, it indicates the SFN nearest to the frame where the message indicating the _epochTime_ is received.

Sources:
- [\[1\] TS 38.211 clause 3.2, Tables 6.3.3.2-2 - 6.3.3.2-4](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)
- [\[3\] 3GPP TS 38.331 clauses 5.2.2.2.2, 5.2.2.3.2, 5.5.2.10, 6.2.2, 6.3.1](https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/19.01.00_60/ts_138331v190100p.pdf)

---

(label-glossary-n-gap)=
### $N_\text{gap}$
 
Source: [\[1\] TS 38.213, Table 8.1-2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-rb-ra)=
### $N_\text{RB}^\text{RA}$

The number of resource blocks occupied by RACH, given by the parameter allocation expressed in number of RBs for PUSCH in [\[1\] TS 38.211 Tables 6.3.3.2-1](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf).
Source: [\[1\] TS 38.211, ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-shift-seq)=
### $n_\text{shift}^\text{seq}$

The number of possible shifts per root sequence, where $n_\text{shift}^\text{seq} = \lfloor$ [$L_\text{RA}$](label-glossary-l-ra)$/$[$N_\text{CS}$](label-glossary-n-cs) $\rfloor$.
Source: [\[4\] ch. A.6.2](https://theses.hal.science/tel-03848017v1/file/120472_DE_JAVEL_2022_archivage.pdf)

---

(label-glossary-n-bwp-size)=
### $N_\text{BWP}^\text{size}$

The size if the active Bandwidth Part (BWP), counted in RBs.

---

(label-glossary-n-slot-ra)=
### $n_\text{slot}^\text{RA}$

PRACH slots (i.e., slots containing RACH occasion) in the 30 kHz (FR1) or 120 kHz (FR2) reference grid, beginning at symbol 0 of the 15 kHz (FR1) or 60 kHz (FR2) reference grid. Determines which slots of the 30 kHz (for FR1) or 120 kHz (for FR2) reference grid contain a RACH occasion, starting with the first symbol of the 30 kHz (for FR1) or 60 kHz (for FR2) reference grid of the slot chosen by "Subframe number" or "Slot number" in TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-2. $14 \cdot n_\text{slot}^\text{RA}$ when determining [$l$](label-glossary-l) results in a representation with regard to symbol.
Source: [\[1\] TS 38.211, ](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-t-ra)=
### $n_\text{t}^\text{RA}$

The PRACH transmission occasions within each PRACH slot [$n_\text{slot}^\text{RA}$](label-glossary-n-slot-ra), numbered in increasing order from 0 to $N_\text{t}^\text{RA,slot} - 1$ within a RACH slot where $N_\text{t}^\text{RA,slot}$ is given by TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-4 for [$L_\text{RA}$](label-glossary-l-ra) $\in \{139, 571, 1151\}$ and fixed to 1 for [$L_\text{RA}$](label-glossary-l-ra) $= 839$.
Source: [\[1\] TS 38.211, ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-u)=
### $N_\text{u}$

The length of the root Zadoff-Chu (ZC) sequence used to generate the PRACH preambles in number of symbols of the chosen [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) grid. The choice of $N_\text{u}$​ affects the number of available cyclic shifts, influencing the maximum number of simultaneous random access attempts that can be supported. A longer $N_\text{u}$​ provides more cyclic shift options, reducing the probability of preamble collisions and enhancing interference management. It usually depends on [$\kappa$](label-glossary-kappa) and (only Formats A, B, and C) $\mu_\text{RA}$.
Source: [\[1\] TS 38.211 Tables 6.3.3.1-1 and 6.3.3.1-2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-n-u-mu)=
### $N_\text{u}^\mu$

Defined in TS 38.211 ch. 5.3.1 and ch. 5.3.2.
Source: [\[1\] TS 38.211, ch. 5.3.1 and ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-rb-start)=
### $RB_\text{start}$

The RB index of a starting virtual resource block.

---

(label-glossary-t-c)=
### $T_\text{c}$

The basic time unit in 5G NR, defined as the smallest time interval used in the system. A constant, where $T_\text{c} = {1}/(\Delta f_\text{max} \cdot$ [$N_\text{f}$](label-glossary-n-f)$) = 0.5086\,\text{ns}$, with $\Delta f_\text{max} = 480 \cdot 10^3\,\text{Hz}$ and [$N_\text{f}$](label-glossary-n-f) $= 4096$.
Source: [\[1\] TS 38.211, ch. 4.1](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-t-s)=
### $T_\text{s}$

The basic time unit for LTE. Serves as the basis for defining time slots, subframe durations, and frame durations in the system. A constant, where $T_\text{s} = {1}/{\Delta f_\text{ref} \cdot N_\text{f,ref}} = 32.5521\,\text{ns}$, with $\Delta f_\text{ref} = 15 \cdot 10^3\,\text{Hz}$ and $N_\text{f,ref} = 2048$.
Source: [\[1\] TS 38.211, ch. 4.1](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-t-start-ra)=
### $t_\text{start}^\text{RA}$

The starting position of the PRACH preamble in a subframe (for [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) $\in \{1.25, 5, 15, 30\}\,\text{kHz}$) or in a 60 kHz slot (for [$\Delta f_\text{RA}$](label-glossary-delta-f-ra) $\in \{60, 120, 480, 960\}\,\text{kHz}$), given by $t_\text{start}^\text{RA} = t_{\text{start,}l}^\mu$, where $t_{\text{start,}l}^\mu = \begin{cases} 0 &\text{if } l = 0 \\  t_{\text{start,}l-1}^\mu + (N_\text{u}^\mu + N_{\text{CP,}l-1}^\mu) \cdot T_\text{c} &\text{otherwise }\end{cases}$. The subframe or 60 kHz slot is assumed to start at $t = 0$, which serves as starting point for counting the slots of all other reference grids used simultaneously.
Source: [\[1\] TS 38.211, ch. 5.3.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

---

(label-glossary-u)=
### $u$

Zadoff-Chu sequence number.
Source: [\[1\] TS 38.211, Tables 6.3.3.1-3, 6.3.3.1-4, 6.3.3.1-4A, and 6.3.3.1-4B](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)

## Terms

### Directions

- Downlink: gNB -> UE
- Uplink: UE -> gNB
- Sidelink: UE -> UE (no gNB involved)

---

### Channels

Signals are defined as reference signals, primary and secondary synchronization signals.

| Direction | Channel Abbrev. | Channel Name | Channel Description | Sources |
|-----------|-----------------|--------------|---------------------|---------|
| Downlink | PBCH | Physical Broadcast Channel | Provides a periodically transmitted broadcast signal, supporting the UEs' access to the NG-RAN. | [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf), [\[6\] ch. 7.1](https://www.degruyter.com/document/doi/10.1515/9783111186610/html)
| Downlink | PDCCH | Physical Downlink Control Channel | Transmits control information from the base station to the terminals and, among others, allocates the necessary resources for the PDSCH and PUSCH. | [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf), [\[6\] ch. 7.1](https://www.degruyter.com/document/doi/10.1515/9783111186610/html) |
| Downlink | PDSCH | Physical Downlink Shared Channel | Represents the actual transmission channel for data transfer from the gNB to the UE. Paging, the calling of a UE in the radio cell, also takes place via this channel. | [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf), [\[6\] ch. 7.1](https://www.degruyter.com/document/doi/10.1515/9783111186610/html) |
| Uplink | PRACH | Physical Random Access Channel | Enables the procedure for the random access of the UEs to the NG-RAN, e.g., in case of a handover. Also, the DL and UL transmit further required reference and synchronization signals. [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf), [\[6\] ch. 7.1](https://www.degruyter.com/document/doi/10.1515/9783111186610/html) |
| Uplink | PUCCH | Physical Uplink Control Channel | Responsible for the transmission of the control information, including the HARQ feedbacks (Hybrid Automatic Repeat Request). | [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf), [\[6\] ch. 7.1](https://www.degruyter.com/document/doi/10.1515/9783111186610/html) |
| Uplink | PUSCH | Physical Uplink Shared Channel | The data transfer from the UE to the gNB takes place here. | [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf), [\[6\] ch. 7.1](https://www.degruyter.com/document/doi/10.1515/9783111186610/html) |
| Sidelink | PSBCH | Physical Sidelink Broadcast Channel |  | [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf) |
| Sidelink | PSCCH | Physical Sidelink Control Channel |  | [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf) |
| Sidelink | PSFCH | Physical Sidelink Feedback Channel |  | [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf) |
| Sidelink | PSSCH | Physical Sidelink Shared Channel |  | [\[5\] TS 38.201, ch. 4.2.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf) |

---

### Absolute Frequency Point A
Represents the frequency location of `Point A`, which is the absolute frequency position of the reference resource block (Common RB 0), expressed as an ARFCN.
`Point A` serves as a common reference point for resource block grids.
It is also the lowest subcarrier of _Common Resource Block 0_ (`CRB0`) and a common reference point from which the relative position of a _BWP_ could be determined.
Absolute frequency position of the reference resource block (Common RB 0). Its lowest subcarrier is also known as Point A (see [[6] TS 38.211, clause 4.4.4.2](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/18.02.00_60/ts_138211v180200p.pdf)).
Note that the lower edge of the actual carrier is not defined by this field but rather in the _scs-SpecificCarrierList_.
Point A is found by applying `offsetToPointA` (unit: Resource Blocks) and `k_ssb` (unit: Subcarriers).
ASN.1 IE: `ARFCN-ValueNR`


#### Offset To Point A

*tbd*

---

### Absolute Frequency SSB (SSB_REF)
SSB Reference frequency on the GSCN raster.
Located at `RE0` of `RB10` inside `SSB`.
ASN.1 IE: `ARFCN-ValueNR OPTIONAL, -- Cond SpCellAdd`

---

### Absolute Radio Frequency Channel Number (NR-ARFCN)

*tbd*

---

### Bandwidth Part (BWP)



#### Initial Downlink BWP

> The dedicated (UE-specific) configuration for the initial downlink bandwidth-part. As described in 38.331, this is the dedicated (UE-specific) configuration for the initial downlink bandwidth-part (i.e. DL BWP#0). If any of the optional IEs are configured within this IE, the UE considers the BWP#0 to be an RRC configured BWP (from UE capability viewpoint). Otherwise, the UE does not consider the BWP#0 as an RRC configured BWP (from UE capability viewpoint). Network always configures the UE with a value for this field if no other BWPs are configured. Network always configures the UE with a value for this field if no other BWPs are configured. If the dedicated part of initial UL/DL BWP configuration is absent, the initial BWP can be used but with some limitations. For example, changing to another BWP requires RRCReconfiguration since DCI format 1_0 doesn't support DCI-based switching.

Source: ShareTechNote

#### Initial Uplink BWP

> If configured for an SpCell, this field contains the ID of the DL BWP to be activated upon performing the reconfiguration in which it is received. If the field is absent, the RRC reconfiguration does not impose a BWP switch (corresponds to L1 parameter 'active-BWP-UL-Pcell'). If configured for an SCell, this field contains the ID of the uplink bandwidth part to be used upon MAC-activation of an  SCell. The initial bandwidth part is referred to by BandiwdthPartId = 0

Source: ShareTechNote

#### Location And Bandwidth
> Frequency domain location and bandwidth of this bandwidth part. The value of the field shall be interpreted as resource indicator value (RIV). See [here](https://www.sharetechnote.com/html/5G/5G_CarrrierBandwidthPart.html#How_BWP_location_and_bandwidth_is_specified) for the details

Source: ShareTechNote

##### Resource Indication Value (RIV)

*tbd*

---

### Carrier Bandwidth
Bandwidth of the carrier in PRBs.
ASN.1 IE: `INTEGER (1..maxNrofPhysicalResourceBlocks)`

#### Offset To Carrier

*tbd*

---

### Control Resource Set Zero (CORESET#0)
Part of `PDCCH` `SIB1` config.


---

### Frequency Band

*tbd*

---

### gNodeB (gNB)

*tbd*

---

### Global Synchronization Channel Number (GSCN)

### Information Element (IE)
ASN.1-Format, defined in TS 38.331.


---

### Physical Cell ID

ASN.1 IE: `PhysCellId OPTIONAL, -- Cond HOAndServCellAdd`

---

### Resource Block (RB)

*tbd*

#### Physical Resource Block (PRB)

*tbd*

---

### Public Land Mobile Network (PLMN)


#### Mobile Country Code (MCC)
Mobile Country Code, part of `PLMN`.
Consists of 3 decimal digits of type `MCC-MNC-Digit` (0...9).
Examples: `262` (Germany), `001` (Test networks), `901` (world-wide, satellites etc.), `999` (internal use).
ASN.1 IE: `SEQUENCE (SIZE (3)) OF MCC-MNC-Digit` 

#### Mobile Network Code (MNC)
Consists of 2 or 3 decimal digits of type `MCC-MNC-Digit` (0...9).
Examples: `01`, `70`. Note MNC of `001` is not the same as MNC of `01`!  
ASN.1 IE: `SEQUENCE (SIZE (2..3)) OF MCC-MNC-Digit`

##### MNC Length
States the lenght of `MNC`, either `2` or `3`.

---

### Search Space Zero

*tbd*

---

### Single Network Slice Selection Assistance Information (S-NSSAI)
List of multiple `SST` and `SD` entries.
ASN.1 IE: `CHOICE {sst BIT STRING (SIZE (8)),sst-SD BIT STRING (SIZE (32))}`

#### Service Differentiator (SD)
Part of `SNSSAI`.
Can have multiple entries.
Hexadecimal bit string, for example: `0x010203`, `0x000001`, `0xFFFFFF` (reserved value "no SD value associated with the SST").
ASN.1 IE: `BIT STRING (SIZE (32))`

#### Slice/Service Type (SST)
part of `SNSSAI`. Can have multiple entries when written as a list. The `SST` field may have standardized and non standardized values. Values `0` to `127` belong to the standardized `SST`.
ASN.1 IE: `BIT STRING (SIZE (8))`

#### S-NSSAI List
List of multiple `S-NSSAI` entries.

---

### Signal Source Block (SSB)

*tbd*

---

### Tracking Area Code (TAC)
The IE TrackingAreaCode is used to identify a tracking area within the scope of a PLMN/SNPN.
`0x0000` and `0xfffe` are reserved values.
ASN.1 IE: `BIT STRING (SIZE (24))`

# Sources

- [\[1\] 3GPP TS 38.211 V19.3.0 (2026-04): "Physical channels and modulation"](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/19.03.00_60/ts_138211v190300p.pdf)
- [\[2\] 3GPP TS 38.213 V19.3.0 (2026-04): "Physical layer procedures for control"](https://www.etsi.org/deliver/etsi_ts/138200_138299/138213/19.03.00_60/ts_138213v190300p.pdf)
- [\[3\] 3GPP TS 38.331 V19.1.0 (2026-02): "Radio Resource Control (RRC)"](https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/19.01.00_60/ts_138331v190100p.pdf)
- [\[4\] de Javel, Aymeric: "5G RAN: physical layer implementation and network slicing", PHD Thesis, Institut Polytechnique de Paris, 2022](https://theses.hal.science/tel-03848017v1/file/120472_DE_JAVEL_2022_archivage.pdf)
- [\[5\] 3GPP TS 38.201 V19.0.0 (2026-01): "Physical layer; General description"](https://www.etsi.org/deliver/etsi_ts/138200_138299/138201/19.00.00_60/ts_138201v190000p.pdf)
- [\[6\] Trick, Ulrich: "5G - The 5th Generation Mobile Networks", De Gruyter Oldenbourg, 2023](https://www.degruyter.com/document/doi/10.1515/9783111186610/html)
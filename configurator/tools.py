#!/usr/bin/env python

# Copyright (c) 2026 Niels Hendrik Fliedner
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL
# was not distributed with this file, You can obtain one at
# https://mozilla.org/MPL/2.0/.

"""Tool functions for 5GAutoConf.

Raises
------
RuntimeError
    If this script is called directly or trying to access the main() function.

"""
import math
import pandas as pd
from itertools import groupby
from operator import itemgetter
import logging
import bisect

from types import MappingProxyType

from . import tables

logger = logging.getLogger(__name__)

# Speed of Light

C_M_PER_S = 299792458

# ΔF_Global values according to 3GPP TS 38.104 Table 5.4.2.1-1

DELTA_F_GLOBAL_HZ_LIST = [5 * 1000, 15 * 1000, 60 * 1000]

# F_REF_Offs values according to 3GPP TS 38.104 Table 5.4.2.1-1

F_REF_OFFS_HZ_LIST = [0.0 * 1000000, 3000.0 * 1000000, 24250.08 * 1000000]

# N_REF_Offs values according to 3GPP TS 38.104 Table 5.4.2.1-1

N_REF_OFFS_LIST = [0, 600000, 2016667]

# Frequency range values according to 3GPP TS 38.104 Tables 5.4.2.1-1 and 5.4.3.1-1

FREQ_RANGE_LOWER_LIMIT_HZ = F_REF_OFFS_HZ_LIST[0]
FREQ_RANGE_EDGE_HZ_1 = F_REF_OFFS_HZ_LIST[1]
FREQ_RANGE_EDGE_HZ_2 = math.floor(F_REF_OFFS_HZ_LIST[2])
FREQ_RANGE_UPPER_LIMIT_HZ = 100000 * 1000000

# NR-ARFCN range values according to 3GPP TS 38.104 Table 5.4.2.1-1

ARFCN_RANGE_LOWER_LIMIT_HZ = N_REF_OFFS_LIST[0]
ARFCN_RANGE_EDGE_HZ_1 = N_REF_OFFS_LIST[1]
ARFCN_RANGE_EDGE_HZ_2 = N_REF_OFFS_LIST[2]
ARFCN_RANGE_UPPER_LIMIT_HZ = 3279165


# T_c in seconds
# See 3GPP TS 38.211 ch. 4.1

T_C_S = 1 / (480 * 1000 * 4096)

# T_S in seconds, T_s = kappa * T_c
# See 3GPP TS 38.211 ch. 4.1

T_S_S = 1 / (15 * 1000 * 2048)

# kappa = T_s / T_c
# See 3GPP TS 38.211 ch. 4.1

KAPPA = 64

# Number of Resource Blocks (RBs) in a Synchronization Signal Block (SSB)

N_RBS_PER_SSB = 20

# Number of Subcarriers (SC) per Resource Block (RB)

N_SC_PER_RB = 12

# Number of Resource Blocks (RBs) in a Bandwidth Part (BWP)

N_RBS_PER_BWP = 275

# NR Radio Frame duration in ms

NR_RADIO_FRAME_DURATION_MS = 10

# Number of Subframes per NR Radio Frame

N_SUBFRAMES_PER_FRAME = 10

# NR Subframe duration in ms

NR_SUBFRAME_DURATION_MS = int(NR_RADIO_FRAME_DURATION_MS / N_SUBFRAMES_PER_FRAME)

# Frequency Range designation according to 3GPP TS 38.104 Table 5.1-1
# Note: The edge case between FR2-1 and FR2-2 has been manually set to FR2-2.
#       The standard has not resolved this yet.

freq_range_designation_dict = {
    "FR1": [410 * 1000000, 7125 * 1000000],
    "FR2": [24250 * 1000000, 71000 * 1000000],
    "FR2-1": [24250 * 1000000, 52600 * 1000000 - 1],
    "FR2-2": [52600 * 1000000, 71000 * 1000000],
}

# Δf_RA in different Frequency Ranges
# Note: This is interpreted from the structure in TS 38.211 Table 6.3.3.2-1, with context of TS 38.211 Tables 6.3.3.1-1 and 6.3.3.1-2 and ch. 5.3.2.
#   Currently, the author did not find a definitive statement, which Δf_RA are permitted in which Frequency Ranges.
#   It is unclear, whether Δf_RA = 60 kHz is permitted in FR1.
#   However, omission of 240 kHz is defined clearly.

freq_range_delta_f_ra_dict = {
    "FR1": [1250, 5000, 15 * 1000, 30 * 1000],
    "FR2": [60 * 1000, 120 * 1000, 480 * 1000, 960 * 1000],
    "FR2-1": [60 * 1000, 120 * 1000],
    "FR2-2": [120 * 1000, 480 * 1000, 960 * 1000],
}

DELTA_F_RA_HZ = [
    1250, 5000, 15 * 1000, 30 * 1000,
    60 * 1000, 120 * 1000, 480 * 1000, 960 * 1000
]

# Resource element index k

resource_element_index_k_dict = {
    0: 0,
    1: 6
}

# L_RA index
#
# prach_RootSequenceIndex_PR

prach_root_sequence_index_pr = {
    1: 839,
    2: 139
}

# PRACH subcarrier spacing reference raster for slot numbering in the tables
#
# This refers to 3GPP TS 38.211 ch. 6.3.3.2.

PRACH_SCS_HZ_REFERENCE_RASTER = {
    "FR1": 15 * 1000,
    "FR2": 60 * 1000,
    "FR2-1": 60 * 1000,
    "FR2-2": 60 * 1000
}

# Global Synchronization Channel Number (GSCN) Parameters
#
# SS block frequency positions SS_REF formulae
# Refers to 3GPP TS 38.104 Table 5.4.3.1-1
# The main keys are row indices
# Can use F_REF_OFFS_HZ_LIST for SS_REF offsets
# Row 0: 0...3000 MHz : SS_REF = 0 MHz + N * 1200 kHz + M * 50 kHz = F_REF_OFFS_HZ_LIST[0] + N * 1200 kHz + M * 50 kHz
# Note: The default value for operating bands which only support SCS spaced channel raster(s) is M=3.
# Row 1: 3000...24250 MHz : SS_REF = 3000 MHz + N * 1.44 MHz = F_REF_OFFS_HZ_LIST[1] + N * 1.44 MHz
# Row 2: 24250...100000 MHz : SS_REF = 24250.08 MHz + N * 17.28 MHz = F_REF_OFFS_HZ_LIST[2] + N * 17.28 MHz
#
# GSCN formulas
# Refers to 3GPP TS 38.104 Table 5.4.3.1-1
# The main keys are row indices
# Can use gscn_ranges_mhz_dict for GSCN offsets (Row 1 and 2 only!)
# Row 0: 0...3000 MHz : GSCN = 3 * N + (M-3)/2 = 3 * N + (M-3)/2
# Row 1: 3000...24250 MHz : GSCN = 7499 + N = gscn_ranges_mhz_dict[1][0] + 7499 + N
# Row 2: 24250...100000 MHz : GSCN = 22256 + N = gscn_ranges_mhz_dict[2][0] + 22256 + N

gscn_parameters_dict = {
    0: {
        "N": [1, 2499],
        "M": [1, 3, 5]
    },
    1: {
        "N": [0, 14756]
    },
    2: {
        "N": [0, 4383]
    }
}

gscn_ranges_mhz_dict = {
    0: [2, 7498],
    1: [7499, 22255],
    2: [22256, 26639]
}

# Number of OFDM Symbols per Slot

N_SYMB_PER_SLOT = 14
N_SYMB_PER_SLOT_EXTENDED_CYCLIC_PREFIX = 12

# SSB Cases, refers to 3GPP TS 38.213 ch. 4.1

SSB_CASES = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

SSB_CASES_SCS_HZ = {
    'A': 15000,
    'B': 30000,
    'C': 30000,
    'D': 120000,
    'E': 240000,
    'F': 480000,
    'G': 960000
}

# SSB Cases reverse, refers to 3GPP TS 38.213 ch. 4.1

SCS_HZ_TO_SSB_CASE = {
    15000: 'A',
    30000: ['B', 'C'],
    120000: 'D',
    240000: 'E',
    480000: 'F',
    960000: 'G'
}

# Numerology Reverse
# This refers to 3GPP TS 38.300 Table 5.1-1

SCS_HZ_TO_NUMEROLOGY = {
    15000: 0,
    30000: 1,
    60000: 2,
    120000: 3,
    240000: 4,
    480000: 5,
    960000: 6
}

# RACH-ConfigCommon IE

# ssb-perRACH-Occcasion (Number of SSBs per RACH occasion)
#
# 'oneEighth': 1 SSB is associated with 8 RACH occasions
# 'oneFourth': 1 SSB is associated with  4 RACH occasions
# 'oneHalf': 1 SSB is associated with 2 RACH occasions
# 'one': 1 SSB is associated with 1 RACH occasions
# 'two': 2 SSBs are associated with 1 RACH occasion
# 'four': 4 SSBs are associated with 1 RACH occasion
# 'eight': 8 SSBs are associated with 1 RACH occasion
# 'sixteen': 16 SSBs are associated with 1 RACH occasion

SSB_PER_RACH_OCCASION = {
    1: 'oneEighth',
    2: 'oneFourth',
    3: 'oneHalf',
    4: 'one',
    5: 'two',
    6: 'four',
    7: 'eight',
    8: 'sixteen'
}

SSB_PER_RACH_OCCASION_FLOAT = {
    1: 0.125,
    2: 0.25,
    3: 0.5,
    4: 1.0,
    5: 2.0,
    6: 4.0,
    7: 8.0,
    8: 16.0
}

# CB-PreamblesPerSSB (Number of Contention-Based preambles per SSB)
#
# The total number of CB preambles in a RACH occasion is given by CB-preambles-per-SSB * max(1, SSB-per-rach-occasion).
#
# n4 ... n64 (enumerated): n4 ... n64 contention-based preambles per SSB
#     Example: ssb-perRACH-OccasionAndCB-PreamblesPerSSB = 'oneFourth' and n64. Thus, 64 CB preambles are available per SSB and 1 SSB is associated with 4 RACH occasion
# 1 ... 16 (integer): Number of contention-based preambles shared by the SSBs in a RACH occasion.
#     Example: ssb-perRACH-OccasionAndCB-PreamblesPerSSB = 'four' and 16. Thus, 16 CB preambles are available per SSB and 4 SSBs share a given RACH occasion

CB_PREAMBLES_PER_SSB = {
    'oneEighth': ['n4', 'n8', 'n12', 'n16', 'n20', 'n24', 'n28', 'n32', 'n36', 'n40', 'n44', 'n48', 'n52', 'n56', 'n60', 'n64'],
    'oneFourth': ['n4', 'n8', 'n12', 'n16', 'n20', 'n24', 'n28', 'n32', 'n36', 'n40', 'n44', 'n48', 'n52', 'n56', 'n60', 'n64'],
    'oneHalf': ['n4', 'n8', 'n12', 'n16', 'n20', 'n24', 'n28', 'n32', 'n36', 'n40', 'n44', 'n48', 'n52', 'n56', 'n60', 'n64'],
    'one': ['n4', 'n8', 'n12', 'n16', 'n20', 'n24', 'n28', 'n32', 'n36', 'n40', 'n44', 'n48', 'n52', 'n56', 'n60', 'n64'],
    'two': ['n4', 'n8', 'n12', 'n16', 'n20', 'n24', 'n28', 'n32'],
    'four': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    'eight': [1, 2, 3, 4, 5, 6, 7, 8],
    'sixteen': [1, 2, 3, 4]
}

# ra-ContentionResolutionTimer
#
# The UE starts its Contention Resolution timer after the transmission of MSG3
# The timer stops when the contention is resolved, i.e. at the reception of MSG4 having 48 bits of MSG3 contents (in case of connected mode UE, PDCCH scrambled with C-RNTI is enough for the contention resolution).
# At the expiry of this timer, the RACH procedure is said to be failed, discard the Temp C-RNTI, contention resolution is said to be not successful, discard the successfully decoded MAC PDU, informed upper layers about the RACH failure.
# Source: https://www.linkedin.com/pulse/5g-mac-timers-manje-gowda-k-r-

RA_CONTENT_RESOLUTION_TIMER = {
    0: 'sf8',
    1: 'sf16',
    2: 'sf24',
    3: 'sf32',
    4: 'sf40',
    5: 'sf48',
    6: 'sf56',
    7: 'sf64'
}

# ssb_periodicityServingCell
#
# If the field is absent, the UE applies the value ms5 (see TS 38.213, clause 4.1).
# ENUMERATED { ms5, ms10, ms20, ms40, ms80, ms160, spare2, spare1 }

SSB_PERIODICITY_SERVING_CELL = {
    0: 'ms5',
    1: 'ms10',
    2: 'ms20',
    3: 'ms40',
    4: 'ms80',
    5: 'ms160',
    6: 'spare2',
    7: 'spare1'
}

# RACH-ConfigGeneric IE

# msg1-FDM
#
# The number of PRACH occasions frequency-division multiplexed in one time instance

MSG1_FDM = {
    0: 'one',
    1: 'two',
    2: 'four',
    3: 'eight'
}

MSG1_FDM_INT = {
    0: 1,
    1: 2,
    2: 4,
    3: 8
}

# powerRampingStep
#
# Power ramping steps for PRACH (see TS 38.321 [3],5.1.3).
# This field is set to the same value for different repetition numbers associated with a specific FeatureCombination.

POWER_RAMPING_STEP = {
    0: 'dB0',
    1: 'dB2',
    2: 'dB4',
    3: 'dB6'
}

# preambleTransMax
#
# Max number of RA preamble transmission performed before declaring a failure (see TS 38.321 [3], clauses 5.1.4, 5.1.5).
# The UE shall ignore this field in case rach-ConfigGeneric is included within an EarlyUL-SyncConfig IE.
# ENUMERATED {n3, n4, n5, n6, n7, n8, n10, n20, n50, n100, n200}

PREAMBLE_TRANS_MAX = {
    0: 3,
    1: 4,
    2: 5,
    3: 6,
    4: 7,
    5: 8,
    6: 10,
    7: 20,
    8: 50,
    9: 100,
    10: 200
}

# dl-UL-TransmissionPeriodicity
#
# Periodicity of the DL-UL pattern, see TS 38.213 [13], clause 11.1.
# If the dl-UL-TransmissionPeriodicity-v1530 is signalled, UE shall ignore the dl-UL-TransmissionPeriodicity (without suffix).
#
# This is the parameter from OAI5G configuration files.
# ENUMERATED {ms0p5, ms0p625, ms1, ms1p25, ms2, ms2p5, ms5, ms10}
# Valid periodicity values for a given Reference Subcarrier Spacing (OAI5G: referenceSubcarrierSpacing) are described in TS 38.213 ch. 11.1.
# The periodicity values of ms0p5, ms1, ms2, and ms5 are not described in TS 38.213 ch. 11.1.
# Configured choices for Reference Subcarrier Spacing in TS 38.213 ch. 11.1 are: µ_ref = {0,1,2,3,5,6}.

DL_UL_TRANSMISSION_PERIODICITY_MS = {
    0: 0.5,
    1: 0.625,
    2: 1.0,
    3: 1.25,
    4: 2.0,
    5: 2.5,
    6: 5.0,
    7: 10.0
}

# PRACH Preamble Formats

PRACH_PREAMBLE_FORMATS = ["0", "1", "2", "3", "A1", "A2", "A3", "B1", "B2", "B3", "B4", "C0", "C2", "A1/B1", "A2/B2", "A3/B3"]

# Ignore pattern for ts_dicts

IGNORE = (None, None)


def compute_nr_riv_from_rbs(rb_start: int, l_rbs: int):
    """Compute the NR Resource Indication Value (RIV) according to 3GPP TS 38.214 5.1.2.2.2.
    This computation is the Downlink resource allocation type 1.
    These equations compute an NR RIV for all cases except when DCI format 1_0 is decoded.

    The resource indication value is defined by:

    if (L_RBs - 1) <= floor(N_^size_BWP/2) then:
        RIV = N_^size_BWP * (L_RBs - 1) + RB_Start
    else:
        RIV = N_^size_BWP * (N_^size_BWP - L_RBs + 1) + (N_^size_BWP - 1 - RB_Start)

    Parameters
    ----------
    rb_start : int
        The starting virtual Resource Block RB_Start.

    l_rbs : int
        The length in terms of contiguously allocated resource blocks L_RBs.
        Usually, this equals the maximum number of resource blocks (RB_max).

    Returns
    -------
    nr_riv : int
        The NR Resource Indication Value (RIV).

    Raises
    ------
    TypeError
        If rb_start or l_rbs is not of type int.

    ValueError
        If l_rbs is < 1.

    ValueError
        If l_rbs > N_^size_BWP - RB_Start.

    """
    if isinstance(rb_start, int) and isinstance(l_rbs, int):
        if l_rbs >= 1:
            if l_rbs <= (N_RBS_PER_BWP - rb_start):
                if (l_rbs - 1) <= int(math.floor(N_RBS_PER_BWP / 2)):
                    nr_riv = N_RBS_PER_BWP * (l_rbs - 1) + rb_start
                else:
                    nr_riv = N_RBS_PER_BWP * (N_RBS_PER_BWP - l_rbs + 1) + (N_RBS_PER_BWP - 1 - rb_start)
                return nr_riv
            else:
                raise ValueError("l_rbs should not exceed N_^size_BWP - RB_Start (which is {0} - {1} = {2}), but is {3}!".format(N_RBS_PER_BWP, rb_start, N_RBS_PER_BWP - rb_start, l_rbs))
        else:
            raise ValueError("l_rbs should be >= 1, but is {0}!".format(l_rbs))
    else:
        raise TypeError("rb_start and l_rbs should both be of type int, but are {0}, and {1}!".format(type(rb_start), type(l_rbs)))


def verify_cbw_validity_from_freq_band(freq_band: int, cbw_hz: int):
    """Verify the validity of a CBW for the given Frequency Band.
    This refers to TS_38_101_1_TABLE_5_3_5_1 and TS_38_101_2_TABLE_5_3_5_1.
    Assumes Frequency Bands 1-256 for TS_38_101_1_TABLE_5_3_5_1 (FR1) and
        Frequency bands 257-512 for TS_38_101_2_TABLE_5_3_5_1 (FR2).

    Parameters
    ----------
    freq_band : int
        The Frequency Band.

    cbw_hz : int
        The Channel Bandwidth in Hz.
        This chooses a column from the dataframe.

    Returns
    -------
    valid_bool : bool
        True, if the CBW is part of the Frequency Band.

    Raises
    ------
    TypeError
        If freq_band is not of type int.
    TypeError
        If cbw_hz is not of type int.
    ValueError
        If freq_band is not a valid 5G NR Frequency Band.
    ValueError
        If cbw is not a valid CBW for either FR1 or FR2.

    """

    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if not isinstance(cbw_hz, int):
        raise TypeError("cbw_hz should be of type int, but is {0}!".format(type(cbw_hz)))

    cbw_mhz = int(cbw_hz / 1_000_000)

    if 0 < freq_band <= 256:
        if cbw_mhz not in tables.NR_FR1_CHANNEL_BW_MHZ_LIST:
            raise ValueError("{0} MHz is not a valid CBW in FR1!".format(cbw_mhz))
        freq_band_dict = tables.ts_38_101_1_table_5_3_5_1(freq_band=freq_band)

        if all(inner_dict.get(str(cbw_mhz)) == (None, None) for inner_dict in freq_band_dict.values()):
            valid_bool = False
        else:
            valid_bool = True
        return valid_bool

    elif 257 <= freq_band <= 512:
        if cbw_mhz not in tables.NR_FR2_CHANNEL_BW_MHZ_LIST:
            raise ValueError("{0} MHz is not a valid CBW in FR2!".format(cbw_mhz))
        freq_band_dict = tables.ts_38_101_2_table_5_3_5_1(freq_band=freq_band)

        if all(inner_dict.get(str(cbw_mhz)) == (None, None) for inner_dict in freq_band_dict.values()):
            valid_bool = False
        else:
            valid_bool = True
        return valid_bool

    else:
        raise ValueError("n{0} is not a valid Frequency Band!".format(freq_band))


def verify_scs_validity_from_freq_band(freq_band: int, scs_hz: int):
    """Verify the validity of an SCS from the Frequency Band.
    This refers to TS_38_101_1_TABLE_5_3_5_1 and TS_38_101_2_TABLE_5_3_5_1.

    Parameters
    ----------
    freq_band : int
        The frequency band.

    scs_hz : int
        The Subcarrier Spacing in Hz.

    Returns
    -------
    valid_bool : bool
        True, if the SCS is part of the Frequency Band.

    Raises
    ------
    TypeError
        If freq_band is not of type int.
    TypeError
        If scs_hz is not of type int.
    ValueError
        If freq_band is not a valid 5G NR Frequency Band.
    ValueError
        If scs_hz is not a valid SCS for the given Frequency Band.

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if not isinstance(scs_hz, int):
        raise TypeError("scs_hz should be of type int, but is {0}!".format(type(scs_hz)))

    scs_khz = int(scs_hz / 1_000)
    if scs_khz not in tables.NUMEROLOGY_FREQUENCY_RANGE_LIST:
        raise ValueError("{0} kHz is not a valid Subcarrier Spacing!".format(scs_khz))
    if 0 < freq_band <= 256:
        freq_band_dict = tables.ts_38_101_1_table_5_3_5_1(freq_band=freq_band)
        if (scs_khz, None) in freq_band_dict:
            valid_bool = True
        else:
            valid_bool = False
        return valid_bool
    elif 257 <= freq_band <= 512:
        freq_band_dict = tables.ts_38_101_2_table_5_3_5_1(freq_band=freq_band)
        if (scs_khz, None) in freq_band_dict:
            valid_bool = True
        else:
            valid_bool = False
        return valid_bool
    else:
        raise ValueError("n{0} is not a valid Frequency Band!".format(freq_band))


def find_closest_ss_ref(frequency_hz: int):
    """Find the closest SS Block reference frequency (SS_REF) on the GSCN raster to a given frequency according to 3GPP TS 38.104 Table 5.4.3.1-1.
    The GSCN parameters N and M computed are returned as well.

    NOTE: This function ignores closes SS_REF frequencies above the input frequency for table Row 0!

    Parameters
    ----------
    frequency_hz : int
        The input frequency in Hz.

    Returns
    -------
    ss_ref_hz : int
        The closest SS Block reference frequency (SS_REF) on the GSCN raster.

    N : int
        The GSCN parameter N.

    M : int
        The GSCN parameter M. Equals None if Row 1 or 2 is chosen.

    Raises
    ------
    IndexError
        If table_row is outside of [0, 1, 2].

    TypeError
        If frequency_hz is not of type int.

    ValueError
        If M or N is outside of the permitted range.

    """
    if isinstance(frequency_hz, int):
        table_row = get_table_row_from_frequency(frequency_hz)
        if table_row == 0:
            N = int(math.floor(frequency_hz / (1200 * 1000)))
            div = round(
                (
                    frequency_hz % (1200 * 1000)
                ) / (
                    50 * 1000
                )
            )
            M = min(gscn_parameters_dict[table_row]["M"], key=lambda x: abs(x - div))
            if gscn_parameters_dict[table_row]["N"][0] <= N <= gscn_parameters_dict[table_row]["N"][1] and M in gscn_parameters_dict[table_row]["M"]:
                ss_ref_hz = int(F_REF_OFFS_HZ_LIST[table_row] + N * 1200 * 1000 + M * 50 * 1000)
            else:
                raise ValueError("N = {0} or M = {1} is out of the allowed range!".format(N, M))  # Not reached by tests. Only targets code errors.
        elif table_row == 1:
            N = round(
                (frequency_hz - 3000 * 1000000) / (1.44 * 1000000)
            )
            M = None
            if gscn_parameters_dict[table_row]["N"][0] <= N <= gscn_parameters_dict[table_row]["N"][1]:
                ss_ref_hz = int(F_REF_OFFS_HZ_LIST[table_row] + N * 1.44 * 1000000)
            else:
                raise ValueError("N = {0} is out of the allowed range!".format(N))  # Not reached by tests. Only targets code errors.
        elif table_row == 2:
            N = round(
                (frequency_hz - 24250.08 * 1000000) / (17.28 * 1000000)
            )
            M = None
            if gscn_parameters_dict[table_row]["N"][0] <= N <= gscn_parameters_dict[table_row]["N"][1]:
                ss_ref_hz = int(F_REF_OFFS_HZ_LIST[table_row] + N * 17.28 * 1000000)
            else:
                raise ValueError("N = {0} is out of the allowed range!".format(N))  # Not reached by tests. Only targets code errors.
        else:
            raise IndexError("Row index {0} is outside of range!".format(table_row))  # Not reached by tests. Only targets code errors.
        return ss_ref_hz, N, M
    else:
        raise TypeError("frequency_hz should be of type int, but is {0}!".format(type(frequency_hz)))


def compute_gscn(frequency_hz: int, N: int, M=0):
    """Compute the Global Synchronization Channel Number (GSCN) according to 3GPP TS 38.104 Table 5.4.3.1-1.

    The computation formulas depend on the table row:

    Row 0: 0...3000 MHz : GSCN = 3 * N + (M-3)/2

    Row 1: 3000...24250 MHz : GSCN = 7499 + N

    Row 2: 24250...100000 MHz : GSCN = 22256 + N

    Parameters
    ----------
    frequency_hz : int
        The input frequency in Hz.

    N : int
        The GSCN parameter N.

    M : int
        The GSCN parameter M.

    Returns
    -------
    gscn : int
        The Global Synchronization Channel Number (GSCN).

    Raises
    ------
    IndexError
        If table_row is outside of [0, 1, 2].

    TypeError
        If frequency_hz, N or M is not of type int.

    ValueError
        If N or M is outside of the permitted range.

    ValueError
        If the GSCN is outside of the permitted range.

    """
    if isinstance(frequency_hz, int) and isinstance(N, int) and (isinstance(M, int) or M is None):
        table_row = get_table_row_from_frequency(frequency_hz)
        if table_row == 0:
            if gscn_parameters_dict[table_row]["N"][0] <= N <= gscn_parameters_dict[table_row]["N"][1] and M in gscn_parameters_dict[table_row]["M"]:
                gscn = int(
                    math.floor(
                        3 * N + (M - 3) / 2
                    )
                )
            else:
                raise ValueError("N or M is out of the allowed range!")
        elif table_row == 1:
            if gscn_parameters_dict[table_row]["N"][0] <= N <= gscn_parameters_dict[table_row]["N"][1]:
                gscn = int(
                    math.floor(
                        gscn_ranges_mhz_dict[table_row][0] + N
                    )
                )
            else:
                raise ValueError("N is out of the allowed range!")
        elif table_row == 2:
            if gscn_parameters_dict[table_row]["N"][0] <= N <= gscn_parameters_dict[table_row]["N"][1]:
                gscn = int(
                    math.floor(
                        gscn_ranges_mhz_dict[table_row][0] + N
                    )
                )
            else:
                raise ValueError("N is out of the allowed range!")
        else:
            raise IndexError("Row index {0} is outside of range!".format(table_row))  # Not reached by tests. Only targets code errors.
        if gscn_ranges_mhz_dict[table_row][0] <= gscn <= gscn_ranges_mhz_dict[table_row][1]:
            return gscn
        else:
            raise ValueError("GSCN = {0} is out of the allowed range [{1}, {2}]!".format(gscn, gscn_ranges_mhz_dict[table_row][0], gscn_ranges_mhz_dict[table_row][1]))  # Not reached by tests. Only targets code errors.
    else:
        raise TypeError("frequency_hz, N and M should all be of type int, but are {0}, {1} and {2}!".format(type(frequency_hz), type(N), type(M)))


def compute_ss_block_frequency_position(frequency_hz: int, N: int, M=0):
    """Compute the SS block frequency position (SS_REF) according to 3GPP TS 38.104 Table 5.4.3.1-1.

    The computation formulas depend on the table row:

    Row 0: 0...3000 MHz : SS_REF = 0 MHz + N * 1200 kHz + M * 50 kHz = F_REF_OFFS_HZ_LIST[0] + N * 1200 kHz + M * 50 kHz
    Note: The default value for operating bands which only support SCS spaced channel raster(s) is M=3.

    Row 1: 3000...24250 MHz : SS_REF = 3000 MHz + N * 1.44 MHz = F_REF_OFFS_HZ_LIST[1] + N * 1.44 MHz

    Row 2: 24250...100000 MHz : SS_REF = 24250.08 MHz + N * 17.28 MHz = F_REF_OFFS_HZ_LIST[2] + N * 17.28 MHz

    Parameters
    ----------
    frequency_hz : int
        The input frequency in Hz.
        This chooses the computation formula.

    N : int
        The GSCN parameter N.

    M : int
        The GSCN parameter M.

    Returns
    -------
    ss_ref_hz : int
        The SS block frequency position (SS_REF) in Hz.

    Raises
    ------
    IndexError
        If table_row is outside of [0, 1, 2].

    TypeError
        If N or M is not of type int.

    ValueError
        If N or M is outside of the permitted range.

    """
    if isinstance(frequency_hz, int) and isinstance(N, int) and (isinstance(M, int) or M is None):
        table_row = get_table_row_from_frequency(frequency_hz)
        if table_row == 0:
            if gscn_parameters_dict[table_row]["N"][0] <= N <= gscn_parameters_dict[table_row]["N"][1] and M in gscn_parameters_dict[table_row]["M"]:
                ss_ref_hz = int(
                    math.floor(
                        F_REF_OFFS_HZ_LIST[table_row] + N * 1200 * 1000 + M * 50 * 1000
                    )
                )
            else:
                raise ValueError("N or M is out of the allowed range!")  # Not reached by tests. Only targets code errors.
        elif table_row == 1:
            if gscn_parameters_dict[table_row]["N"][0] <= N <= gscn_parameters_dict[table_row]["N"][1]:
                ss_ref_hz = int(
                    math.floor(
                        F_REF_OFFS_HZ_LIST[table_row] + N * 1.44 * 1000000
                    )
                )
            else:
                raise ValueError("N is out of the allowed range!")  # Not reached by tests. Only targets code errors.
        elif table_row == 2:
            if gscn_parameters_dict[table_row]["N"][0] <= N <= gscn_parameters_dict[table_row]["N"][1]:
                ss_ref_hz = int(
                    math.floor(
                        F_REF_OFFS_HZ_LIST[table_row] + N * 17.28 * 1000000
                    )
                )
            else:
                raise ValueError("N is out of the allowed range!")  # Not reached by tests. Only targets code errors.
        else:
            raise IndexError("Row index {0} is outside of range!".format(table_row))  # Not reached by tests. Only targets code errors.
        return ss_ref_hz
    else:
        raise TypeError("frequency_hz, N and M should all be of type int, but are {0}, {1} and {2}!".format(type(frequency_hz), type(N), type(M)))


def get_table_row_from_frequency(frequency_hz: int):
    """Get the row in 3GPP TS 38.104 Table 5.4.2.1-1 based on the frequency.
    NOTE: The row numbering starts at 0.

    Parameters
    ----------
    frequency_hz : int
        The input frequency in Hz.

    Returns
    -------
    table_row : int
        The resulting table row.

    Raises
    ------
    TypeError
        If frequency_hz is not of type int.

    ValueError
        If frequency_hz is outside of range(0, 100000000000).

    """
    if not isinstance(frequency_hz, int):
        raise TypeError("frequency_hz should be of type int, but is {0}!".format(type(frequency_hz)))

    if frequency_hz >= FREQ_RANGE_LOWER_LIMIT_HZ and frequency_hz < FREQ_RANGE_EDGE_HZ_1:
        table_row = 0
    elif frequency_hz >= FREQ_RANGE_EDGE_HZ_1 and frequency_hz <= FREQ_RANGE_EDGE_HZ_2:
        table_row = 1
    elif frequency_hz > FREQ_RANGE_EDGE_HZ_2 and frequency_hz <= FREQ_RANGE_UPPER_LIMIT_HZ:
        table_row = 2
    else:
        raise ValueError("A frequency of {0} Hz is unsupported!".format(frequency_hz))

    return table_row


def get_table_row_from_arfcn(arfcn: int):
    """Get the row in 3GPP TS 38.104 Table 5.4.2.1-1 based on the NR-ARFCN.

    .. note::
        The row numbering starts at 0.

    Parameters
    ----------
    arfcn : int
        The input NR-ARFCN.

    Returns
    -------
    table_row : int
        The resulting table row.

    Raises
    ------
    TypeError
        If arfcn is not of type int.

    ValueError
        If arfcn is outside of range(0, 3279165).

    """
    if not isinstance(arfcn, int):
        raise TypeError("arfcn should be of type int, but is {0}!".format(type(arfcn)))

    if arfcn >= ARFCN_RANGE_LOWER_LIMIT_HZ and arfcn < ARFCN_RANGE_EDGE_HZ_1:
        table_row = 0
    elif arfcn >= ARFCN_RANGE_EDGE_HZ_1 and arfcn < ARFCN_RANGE_EDGE_HZ_2:
        table_row = 1
    elif arfcn >= ARFCN_RANGE_EDGE_HZ_2 and arfcn <= ARFCN_RANGE_UPPER_LIMIT_HZ:
        table_row = 2
    else:
        raise ValueError("An NR-ARFCN of {0} is unsupported!".format(arfcn))

    return table_row


def get_prach_configuration_index_from_parameters(freq_range: str, duplex_mode: str, preamble_format: str, x_sfn: int, y_sfn: int | list, subframe_number: int | list, starting_symbol: int, n_slot_ra: int | None, n_t_ra_slot: int | None, n_dur_ra: int):
    """Get the PRACH configuration index given by 3GPP TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-4 from matching the given parameters, used as column headers.
    The specific table is chosen by frequency range and duplex mode.

    The system frame number (SFN) choice mask `n_f mod x = y` indicates which frames have a RACH occasion.

    If more than one PRACH configuration index is matching the given parameters, the first matching entry is chosen arbitrarily.

    Notes
    -----
    - Tables 6.3.3.2-2 to 6.3.3.2-4 do not have separate `B2` and `B3` entries, so they are replaced by `A2/B2` and `A3/B3`, respectively.

    Parameters
    ----------
    freq_range : str
        The frequency range, either FR1 or FR2.

    duplex_mode : str
        The duplex mode, either FDD or TDD.

    preamble_format : str | None
        The PRACH preamble format.

    x_sfn : int | None
        The divisor for the SFN choice mask `n_f mod x = y`.

    y_sfn : int | list | None
        The remainder for the SFN choice mask `n_f mod x = y`.

    subframe_number : int | list | None
        The subframe number in a frame containing the RACH occasions.
        For FR2 and TDD, this is actually the slot number.

    starting_symbol : int | None
        The starting symbol in the given PRACH slot.

    n_slot_ra : int | None
        The number of PRACH slots n_slot^RA within a reference grid (FR1: 15 kHz, FR2: 60 kHz) slot.
        Entries are None, if not defined in the table.

    n_t_ra_slot : int | None
        The number of time-domain PRACH occasions within a PRACH slot.
        Entries are None, if not defined in the table.

    n_dur_ra : int | None
        The overall PRACH duration, given in number of symbols of the chosen Δf_RA grid.

    Returns
    -------
    list
        List of matching PRACH configuration indices from 3GPP TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-4.

    Raises
    ------
    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA for the given frequency range.

    """
    from . import ts_dicts

    if preamble_format == "B2":
        preamble_format = "A2/B2"
    if preamble_format == "B3":
        preamble_format = "A3/B3"

    if freq_range == "FR1" and duplex_mode == "FDD":
        prach_conf_dict = ts_dicts.TS_38_211_TABLE_6_3_3_2_2
        match_params = {
            "Preamble format": (preamble_format, None),
            "x": (x_sfn, None),
            "y": (y_sfn, None),
            "Subframe number": (subframe_number, None),
            "Starting symbol": (starting_symbol, None),
            "Number of PRACH slots within a subframe": (n_slot_ra, None),
            "Number of time-domain PRACH occasions within a PRACH slot": (n_t_ra_slot, None),
            "PRACH duration": (n_dur_ra, None),
        }
        logger.debug("Using 3GPP TS 38.211 Table 6.3.3.2-2")
    elif freq_range == "FR1" and duplex_mode == "TDD":
        prach_conf_dict = ts_dicts.TS_38_211_TABLE_6_3_3_2_3
        match_params = {
            "Preamble format": (preamble_format, None),
            "x": (x_sfn, None),
            "y": (y_sfn, None),
            "Subframe number": (subframe_number, None),
            "Starting symbol": (starting_symbol, None),
            "Number of PRACH slots within a subframe": (n_slot_ra, None),
            "Number of time-domain PRACH occasions within a PRACH slot": (n_t_ra_slot, None),
            "PRACH duration": (n_dur_ra, None),
        }
        logger.debug("Using 3GPP TS 38.211 Table 6.3.3.2-3")
    elif freq_range == "FR2" and duplex_mode == "TDD":
        prach_conf_dict = ts_dicts.TS_38_211_TABLE_6_3_3_2_4
        match_params = {
            "Preamble format": (preamble_format, None),
            "x": (x_sfn, None),
            "y": (y_sfn, None),
            "Slot number": (subframe_number, None),
            "Starting symbol": (starting_symbol, None),
            "Number of PRACH slots within a 60 kHz slot": (n_slot_ra, None),
            "Number of time-domain PRACH occasions within a PRACH slot": (n_t_ra_slot, None),
            "PRACH duration": (n_dur_ra, None),
        }
        logger.debug("Using 3GPP TS 38.211 Table 6.3.3.2-4")
    else:
        raise ValueError("The combination of freq_range {0} and duplex_mode {1} is not supported!".format(freq_range, duplex_mode))

    return find_keys(
        prach_conf_dict,
        **match_params
    )


def compute_n_slot_ra(n_prach_slots: int, delta_f_ra_hz: int):
    """Compute the number of PRACH slots n_slot^RA within a reference grid slot according to 3GPP TS 38.211 ch. 5.3.2.

    Parameters
    ----------
    n_prach_slots : int
        The number of PRACH slots within a subframe (Tables 6.3.3.2-2 to 6.3.3.2-3), or the number of PRACH slots within a 60 kHz slot (Table 6.3.3.2-4).

    delta_f_ra_hz : int
        The subcarrier spacing for the PRACH sequences; Δf_RA.
        Supported are 1.25, 5, 15, 30, 60, 120, 480, and 960 kHz.
        The OAI5G config sets this in msg1_SubcarrierSpacing.

    Returns
    -------
    n_slot_ra : tuple
        The number of PRACH slots n_slot^RA within a reference grid (FR1: 15 kHz, FR2: 60 kHz) slot.
        Variable type tuple chosen since the content shall remain immutable.

    Raises
    ------
    TypeError
        If n_prach_slots is not of type int.

    TypeError
        If delta_f_ra_hz is not of type int.

    ValueError
        If delta_f_ra_hz is not a support PRACH subcarrier spacing Δf_RA.

    """
    if not isinstance(n_prach_slots, int):
        raise TypeError("n_prach_slots should be of type int, but is {0}!".format(type(n_prach_slots)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))

    n_slot_ra = tuple()

    if delta_f_ra_hz in [1250, 5000, 15000, 60000]:
        # No influence of n_prach_slots
        n_slot_ra = (0,)    # Comma ensures tuple even with only one entry
    elif delta_f_ra_hz in [30000, 120000]:
        if n_prach_slots == 1:
            n_slot_ra = (1,)    # Comma ensures tuple even with only one entry
        else:
            n_slot_ra = (0, 1)
    elif delta_f_ra_hz in [480000, 960000]:
        if n_prach_slots == 1:
            if delta_f_ra_hz == 480000:
                n_slot_ra = (7,)    # Comma ensures tuple even with only one entry
            elif delta_f_ra_hz == 960000:
                n_slot_ra = (15,)    # Comma ensures tuple even with only one entry
        elif n_prach_slots == 2:
            if delta_f_ra_hz == 480000:
                n_slot_ra = (3, 7)
            elif delta_f_ra_hz == 960000:
                n_slot_ra = (7, 15)
        else:
            raise ValueError("A value for n_prach_slots of {0} is not supported in combination with delta_f_ra_hz = {1} hz!".format(n_prach_slots, delta_f_ra_hz))
    else:
        raise ValueError("A value for delta_f_ra_hz of {0} Hz is not supported!".format(delta_f_ra_hz))
    return n_slot_ra


def compute_n_t_ra_slot(prach_conf_idx: int, freq_range: str, duplex_mode: str, delta_f_ra_hz: int):
    """Compute the number of time-domain PRACH occasions within a PRACH slot N_t^RA,slot according to 3GPP TS 38.211 ch. 5.3.2.
    Use 3GPP TS 38.211 Tables 6.3.3.2-2 (FR1 FDD), 6.3.3.2-3 (FR1 TDD), and 6.3.3.2-4 (FR2).

    Parameters
    ----------
    prach_conf_idx : int
        PRACH configuration index from 3GPP TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-4.

    freq_range : str
        The frequency range, either FR1 or FR2.

    duplex_mode : str
        The duplex mode, either FDD or TDD.

    delta_f_ra_hz : int
        The subcarrier spacing for the PRACH sequences; Δf_RA.
        Supported are 1250, 5000, 15000, 30000, 60000, 120000, 480000, and 960000 Hz.

    Returns
    -------
    n_t_ra_slot : int
        The number of time-domain PRACH occasions within a PRACH slot, N_t^RA,slot.

    Raises
    ------
    TypeError
        If prach_conf_idx is not of type int.

    TypeError
        If freq_range is not of type str.

    TypeError
        If duplex_mode is not of type str.

    TypeError
        If delta_f_ra_hz is not of type int.

    ValueError
        If prach_conf_idx is not in range 0-262.

    ValueError
        If freq_range is not "FR1" or "FR2".

    ValueError
        If duplex_mode is not "FDD" or "TDD".

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA.

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA for the given frequency range.

    ValueError
        If duplex_mode is not valid for the given frequency range.

    """
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))
    if not isinstance(freq_range, str):
        raise TypeError("freq_range should be of type str, but is {0}!".format(type(freq_range)))
    if not isinstance(duplex_mode, str):
        raise TypeError("duplex_mode should be of type str, but is {0}!".format(type(duplex_mode)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))

    if prach_conf_idx < 0 or prach_conf_idx > 262:
        raise ValueError("A prach_conf_idx of {0} is not supported!".format(prach_conf_idx))
    if freq_range not in ["FR1", "FR2"]:
        raise ValueError("The freq_range {0} is not supported!".format(freq_range))
    if duplex_mode not in ["FDD", "TDD"]:
        raise ValueError("The duplex_mode {0} is not supported!".format(duplex_mode))
    if delta_f_ra_hz not in [*DELTA_F_RA_HZ]:
        raise ValueError("A value for delta_f_ra_hz of {0} Hz is not supported!".format(delta_f_ra_hz))
    if delta_f_ra_hz not in freq_range_delta_f_ra_dict[freq_range]:
        raise ValueError("A combination of delta_f_ra_hz {0} Hz and frequency range {1} is not supported!".format(delta_f_ra_hz, freq_range))

    if freq_range == "FR1" and duplex_mode == "FDD":
        row = tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=prach_conf_idx)
    elif freq_range == "FR1" and duplex_mode == "TDD":
        row = tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=prach_conf_idx)
    elif freq_range == "FR2" and duplex_mode == "TDD":
        row = tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=prach_conf_idx)
    else:
        raise ValueError("The combination of freq_range {0} and duplex_mode {1} is not supported!".format(freq_range, duplex_mode))

    if delta_f_ra_hz in [1250, 5000]:
        n_t_ra_slot = 1     # see 3GPP TS 38.211 ch. 5.3.2
    else:
        n_t_ra_slot = row["Number of time-domain PRACH occasions within a PRACH slot"][0]
        if n_t_ra_slot is None:
            # TS 38.211 5.3.2: N_t^RA,slot is given Tables 6.3.3.2-2 to 6.3.3.2-4 for L_RA in (138,571,1151)
            #     and fixed to 1 for L_RA = 839.
            # The Tables 6.3.3.2-2 to 6.3.3.2-4 contain no entry for N_t^RA,slot only for PRACH preamble formats 0, 1, 2, and 3,
            #     which are only permitted for L_RA = 839, and thus Δf_RA = 1.25 or 5 kHz.
            n_t_ra_slot = 1
    return n_t_ra_slot


def compute_rach_occasion_starting_symbols(prach_conf_idx: int, freq_range: str, duplex_mode: str, delta_f_ra_hz: int):
    """Compute a tuple of starting symbol numbers occupied with RACH occasions according to 3GPP TS 38.211 ch. 5.3.2.
    Use 3GPP TS 38.211 Tables 6.3.3.2-2 (FR1 FDD), 6.3.3.2-3 (FR1 TDD), and 6.3.3.2-4 (FR2).

    - rach_occasion_symbols = l (see 3GPP TS 38.211 ch. 5.3.2).
    - l = l_0 + n_t^RA*N_dur^RA + 14*n_slot^RA
    - l_0: Starting symbol in Δf_RA grid (Table)
    - n_t^RA: Consecutive PRACH occasion numbers, taken from n_t^RA,slot (Table): (0 … (N_t^RA,slot-1))
    - N_dur^RA: PRACH duration in PRACH OFDM symbols of ~~reference grid~~ (FR1: 30 kHz, FR2: 120 kHz) (Table).
        - NOTE: Prob. not based on reference grid, further reading needed!
    - n_slot^RA: Slots in the reference grid (FR1: 30 kHz, FR2: 120 kHz) containing PRACH slots, beginning with symbol 0 of the slot chosen by "Subframe number"; usually 1 or {0, 1}

    - For Δf_RA in {1.25, 5} kHz, µ=0 shall be assumed (3GPP TS 38.211 ch. 5.3.2).

    - Tables 6.3.3.2-2 and 6.3.3.2-3 have partially no entries for the following columns:
        - Number of PRACH slots within a subframe
        - Number of time-domain PRACH occasions within a PRACH slot
    - The missing entries occur for preamble formats 0, 1, 2, and 3 (which correspond to L_RA=839 and Δf_RA=1.25 or 5). Instead, the entries are assumed as follows:
        - For L_RA = 839, N_t^RA,slot=1 is fixed (3GPP TS 38.211 ch. 5.3.2). Code: `n_t_ra_slot`
        - For Δf_RA in {1.25, 5, 15, 60} kHz, n_slot_RA=0 is fixed 3GPP TS 38.211 ch. 5.3.2), so the column entry is not needed and set to 0 to distinguish it from 1 and 2, which are the only other possible column entries. Code: `n_slot_ra`

    :Example:
        * prach_conf_idx=98, freq_range="FR1", duplex_mode="TDD", delta_f_ra_hz=30000:
            * l_0:            0
            * n_t_ra_slot:    3
            * n_dur_ra:       4
            * n_prach_slots:  1
            * n_slot_ra:      (1,)
            * n_t_ra:         (0, 1, 2)
            * l:              (14, 18, 22)

    Parameters
    ----------
    prach_conf_idx : int
        PRACH configuration index from 3GPP TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-4.

    freq_range : str
        The frequency range, either FR1 or FR2.

    duplex_mode : str
        The duplex mode, either FDD or TDD.

    delta_f_ra_hz : int
        The subcarrier spacing for the PRACH sequences; Δf_RA.
        Supported are 1250, 5000, 15000, 30000, 60000, 120000, 480000, and 960000 Hz.

    Returns
    -------
    rach_occasion_symbols : tuple
        The PRACH OFDM symbol numbers occupied with RACH occasions (FR1: 30 kHz, FR2: 120 kHz).
        This equals the symbol positions l in 3GPP TS 38.211 ch. 5.3.2.

    Raises
    ------
    TypeError
        If prach_conf_idx is not of type int.

    TypeError
        If freq_range is not of type str.

    TypeError
        If duplex_mode is not of type str.

    TypeError
        If delta_f_ra_hz is not of type int.

    ValueError
        If prach_conf_idx is not in range 0-262.

    ValueError
        If freq_range is not "FR1" or "FR2".

    ValueError
        If duplex_mode is not "FDD" or "TDD".

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA.

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA for the given frequency range.

    ValueError
        If duplex_mode is not valid for the given frequency range.

    """
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))
    if not isinstance(freq_range, str):
        raise TypeError("freq_range should be of type str, but is {0}!".format(type(freq_range)))
    if not isinstance(duplex_mode, str):
        raise TypeError("duplex_mode should be of type str, but is {0}!".format(type(duplex_mode)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))

    if prach_conf_idx < 0 or prach_conf_idx > 262:
        raise ValueError("A prach_conf_idx of {0} is not supported!".format(prach_conf_idx))
    if freq_range not in ["FR1", "FR2"]:
        raise ValueError("The freq_range {0} is not supported!".format(freq_range))
    if duplex_mode not in ["FDD", "TDD"]:
        raise ValueError("The duplex_mode {0} is not supported!".format(duplex_mode))
    if delta_f_ra_hz not in [*DELTA_F_RA_HZ]:
        raise ValueError("A value for delta_f_ra_hz of {0} Hz is not supported!".format(delta_f_ra_hz))
    if delta_f_ra_hz not in freq_range_delta_f_ra_dict[freq_range]:
        raise ValueError("A combination of delta_f_ra_hz {0} Hz and frequency range {1} is not supported!".format(delta_f_ra_hz, freq_range))

    rach_occasion_symbols = tuple()
    if freq_range == "FR1" and duplex_mode == "FDD":
        row = tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=prach_conf_idx)
    elif freq_range == "FR1" and duplex_mode == "TDD":
        row = tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=prach_conf_idx)
    elif freq_range == "FR2" and duplex_mode == "TDD":
        row = tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=prach_conf_idx)
    else:
        raise ValueError("The combination of freq_range {0} and duplex_mode {1} is not supported!".format(freq_range, duplex_mode))

    # preamble_format = str(row["Preamble format"][0])
    l_0 = row["Starting symbol"][0]

    n_t_ra_slot = compute_n_t_ra_slot(
        prach_conf_idx=prach_conf_idx,
        freq_range=freq_range,
        duplex_mode=duplex_mode,
        delta_f_ra_hz=delta_f_ra_hz
    )

    n_dur_ra = row["PRACH duration"][0]
    if freq_range == "FR1":
        # Tables 6.3.3.2-2 to 6.3.3.2-4: Either 1 or 2 PRACH slots within a subframe or a 60 kHz slot.
        n_prach_slots = row["Number of PRACH slots within a subframe"][0]
        if n_prach_slots is None:
            # TS 38.211 5.3.2: If Δf_RA in (1.25, 5, 15, 60) kHz, then n_slot_RA = 0
            # Thus, any value of n_prach_slots can be chosen, since this is the only case where it does not
            #     influence the determination of n_slot^RA.
            # The Tables 6.3.3.2-2 to 6.3.3.2-4 contain no entry for n_prach_slots only for PRACH preamble formats 0, 1, 2, and 3,
            #     which are only permitted for L_RA = 839, and thus Δf_RA = 1.25 or 5 kHz.
            # Thus, the value of 0 is chosen for n_prach_slots to distinguish it from the other two options given by the
            #     Tables: 1 and 2.
            n_prach_slots = 0
    else:
        n_prach_slots = row["Number of PRACH slots within a 60 kHz slot"][0]
    n_slot_ra = compute_n_slot_ra(n_prach_slots=n_prach_slots, delta_f_ra_hz=delta_f_ra_hz)

    n_t_ra = tuple(range(0, n_t_ra_slot))
    for slot in n_slot_ra:
        for n in n_t_ra:
            l = l_0 + int(n) * n_dur_ra + N_SYMB_PER_SLOT * int(slot)
            rach_occasion_symbols = rach_occasion_symbols + (l,)

    return rach_occasion_symbols


def compute_all_t_cp_ra_dict():
    """Compute all PRACH cyclic prefix durations t_CP^RA in seconds based on 3GPP TS 38.211 Table 6.3.3.1-1 and 6.3.3.1-2.

    .. code-block::
        :caption: Output dictionary pattern:

        {
            t_cp_ra_s: {
                prach_preamble_format: {
                    "Delta f_RA": delta_f_ra_hz,
                    "N_CP,pre^RA": n_cp_pre_ra
                },
                prach_preamble_format: {
                    "Delta f_RA": delta_f_ra_hz,
                    "N_CP,pre^RA": n_cp_pre_ra
                }
            }
        }

    :Variables:
        * t_cp_ra_s: The PRACH cyclic prefix duration T_CP^RA in seconds
        * prach_preamble_format: The PRACH preamble format
        * delta_f_ra_hz: The PRACH subcarrier spacing Δf_RA in hertz
        * n_cp_pre_ra: The prefix N_CP,pre^RA of the cyclic prefix duration N_CP^RA

    Returns
    -------
    t_cp_ra_dict
        Dictionary of all PRACH cyclic prefix durations in seconds.
        The dictionary items include the PRACH preamble format, the PRACH subcarrier spacing, and the prefix of the PRACH cyclic prefix duration in symbols.

    """
    t_cp_ra_s = 0
    n_cp_pre_ra = 0
    t_cp_ra_dict = dict()

    for prach_preamble_format in filter(lambda x: x not in ("A1/B1", "A2/B2", "A3/B3"), PRACH_PREAMBLE_FORMATS):
        for delta_f_ra_hz in DELTA_F_RA_HZ:
            if delta_f_ra_hz in [1250, 5000]:
                mu_ra = 0
            else:
                mu_ra = SCS_HZ_TO_NUMEROLOGY[delta_f_ra_hz]

            # Test for valid combinations of PRACH Preamble Format and PRACH SCS
            if delta_f_ra_hz == 1250:
                delta_f_ra_khz = 1.25
            elif delta_f_ra_hz in [5000, 15000, 30000, 60000, 120000, 480000, 960000]:
                delta_f_ra_khz = int(delta_f_ra_hz / 1000)
            if prach_preamble_format in ['0', '1', '2', '3']:
                if delta_f_ra_khz != tables.ts_38_211_table_6_3_3_1_1(prach_preamble_format=prach_preamble_format)['Delta f_RA'][0]:
                    continue
            else:
                if delta_f_ra_khz % int(tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)['Delta f_RA'][0][0]) != 0:
                    continue

            n_cp_pre_ra = compute_prach_cyclic_prefix_duration(prach_preamble_format=prach_preamble_format)
            t_cp_ra_s = n_cp_pre_ra * KAPPA * T_C_S * math.pow(2, -1 * mu_ra)

            if t_cp_ra_s not in t_cp_ra_dict:
                t_cp_ra_dict[t_cp_ra_s] = {}

            if prach_preamble_format not in t_cp_ra_dict[t_cp_ra_s]:
                t_cp_ra_dict[t_cp_ra_s][prach_preamble_format] = {}

            t_cp_ra_dict[t_cp_ra_s][prach_preamble_format].update(
                {
                    "Delta f_RA": delta_f_ra_hz,
                    "N_CP,pre^RA": n_cp_pre_ra
                }
            )

    return t_cp_ra_dict


def compute_all_t_gt_ra_dict():
    """Compute all PRACH guard time durations T_GT^RA in seconds based on 3GPP TS 38.211 Tables 6.3.3.1-1, 6.3.3.1-2, 6.3.3.2-2, 6.3.3.2-3, and 6.3.3.2-4.

    .. code-block::
        :caption: Output dictionary pattern:

        {
            t_gt_ra: {
                prach_preamble_format: {
                    "Delta f_RA": delta_f_ra_hz,
                    "RACH occasion duration": t_dur_ra,
                    "PRACH preamble duration": t_n_cp_ra
                },
                prach_preamble_format: {
                    "Delta f_RA": delta_f_ra_hz,
                    "RACH occasion duration": t_dur_ra,
                    "PRACH preamble duration": t_n_cp_ra
                }
            }
        }

    :Variables:
        * t_gt_ra: The PRACH guard time duration T_GT^RA in seconds
        * prach_preamble_format: The PRACH preamble format
        * delta_f_ra_hz: The PRACH subcarrier spacing Δf_RA in hertz
        * t_dur_ra: The RACH occasion duration, based on 3GPP TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-4
        * t_n_cp_ra: The PRACH preamble duration N_u + N_CP^RA, based on 3GPP TS 38.211 Tables 6.3.3.1-1 to 6.3.3.1-2

    Returns
    -------
    t_gt_ra_dict
        Dictionary of all PRACH guard time durations in seconds.
        The dictionary items include the PRACH preamble format and the PRACH subcarrier spacing.

    """
    n_cp_pre_ra = 0
    t_gt_ra_dict = dict()

    for prach_preamble_format in filter(lambda x: x not in ("A1/B1", "A2/B2", "A3/B3"), PRACH_PREAMBLE_FORMATS):
        for delta_f_ra_hz in DELTA_F_RA_HZ:
            if delta_f_ra_hz in [1250, 5000]:
                mu_ra = 0
            else:
                mu_ra = SCS_HZ_TO_NUMEROLOGY[delta_f_ra_hz]

            # Test for valid combinations of PRACH Preamble Format and PRACH SCS
            if delta_f_ra_hz == 1250:
                delta_f_ra_khz = 1.25
            elif delta_f_ra_hz in [5000, 15000, 30000, 60000, 120000, 480000, 960000]:
                delta_f_ra_khz = int(delta_f_ra_hz / 1000)

            n_u = compute_prach_zc_sequences_duration(prach_preamble_format)

            if prach_preamble_format in ['0', '1', '2', '3']:
                row_dict = tables.ts_38_211_table_6_3_3_1_1(prach_preamble_format=prach_preamble_format)
                if delta_f_ra_khz != row_dict['Delta f_RA'][0]:
                    continue
                t_u = n_u * KAPPA * T_C_S * math.pow(2, -1 * mu_ra)
                n_cp_pre_ra = compute_prach_cyclic_prefix_duration(prach_preamble_format=prach_preamble_format)
                t_cp_ra_s = n_cp_pre_ra * KAPPA * T_C_S * math.pow(2, -1 * mu_ra)
                t_n_cp_ra = t_u + t_cp_ra_s
                t_dur_ra = math.ceil(1000000. * t_n_cp_ra / 1000.) / 1000
            else:
                if delta_f_ra_khz % tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)['Delta f_RA'][0][0] != 0:
                    continue
                t_symb_ra = 1000 * NR_RADIO_FRAME_DURATION_MS / (1000000 * N_SUBFRAMES_PER_FRAME * N_SYMB_PER_SLOT * math.pow(2, mu_ra))
                t_dur_ra = tables.N_RA_DUR[prach_preamble_format] * t_symb_ra
                t_u = n_u * KAPPA * T_C_S * math.pow(2, -1 * mu_ra)
                n_cp_pre_ra = compute_prach_cyclic_prefix_duration(prach_preamble_format=prach_preamble_format)
                t_cp_ra_s = n_cp_pre_ra * KAPPA * T_C_S * math.pow(2, -1 * mu_ra)
                t_n_cp_ra = t_u + t_cp_ra_s

            t_gt_ra = t_dur_ra - t_n_cp_ra

            if t_gt_ra not in t_gt_ra_dict:
                t_gt_ra_dict[t_gt_ra] = {}

            if prach_preamble_format not in t_gt_ra_dict[t_gt_ra]:
                t_gt_ra_dict[t_gt_ra][prach_preamble_format] = {}

            t_gt_ra_dict[t_gt_ra][prach_preamble_format].update(
                {
                    "Delta f_RA": delta_f_ra_hz,
                    "RACH occasion duration": t_dur_ra,
                    "PRACH preamble duration": t_n_cp_ra
                }
            )

    return t_gt_ra_dict


def compute_applicable_t_cp_ra_dict(t_c_min_s: float, tau_d_max_s: float):
    """Compute combinations of applicable PRACH cyclic prefix durations t_CP^RA.
    This results in a subset of compute_all_t_cp_ra_dict, containing all applicable t_CP^RA with their assigned PRACH preamble formats, Δf_RA, and N_CP,pre^RA.

    .. note::
        The lower boundary t_CP,min^RA is defined by the maximum delay spread tau_d,max:
            ``t_CP,min^RA >= tau_d,max``

        The upper boundary t_CP,max^RA is defined by the minimum channel coherence time T_C,min:
            ``t_CP,max^RA <= T_C,min``

    .. code-block::
        :caption: Output dictionary pattern:

        {
            t_cp_ra_s: {
                prach_preamble_format: {
                    "Delta f_RA": delta_f_ra_hz,
                    "N_CP,pre^RA": n_cp_pre_ra
                },
                prach_preamble_format: {
                    "Delta f_RA": delta_f_ra_hz,
                    "N_CP,pre^RA": n_cp_pre_ra
                }
            }
        }

    Parameters
    ----------
    t_c_min_s : float
        The minimum channel coherence time in seconds.
    tau_d_max_s : float
        The channel's maximum delay spread in seconds.

    Returns
    -------
    applicable_t_cp_ra_dict
        A dict of the applicable PRACH cyclic prefix durations, given in seconds, and PRACH preamble formats.

    """
    t_cp_ra_dict = compute_all_t_cp_ra_dict()
    t_cp_ra_s_lst_sorted = sorted(t_cp_ra_dict.keys())

    t_cp_ra_s_lst_sorted_bisect_right = bisect.bisect_right(t_cp_ra_s_lst_sorted, t_c_min_s)
    if t_cp_ra_s_lst_sorted_bisect_right > 0:
        t_cp_max_ra = t_cp_ra_s_lst_sorted[t_cp_ra_s_lst_sorted_bisect_right - 1]
    else:
        # no value for t_cp_max_ra <= t_c_min_s exists. This means, that no Cyclic Prefix duration shorter than the channel coherence time could be found
        raise ValueError("No cyclic prefix duration shorter than the minimum channel coherence time of {0} µs could be found!".format(t_c_min_s * 1_000_000))

    t_cp_ra_s_lst_sorted_bisect_left = bisect.bisect_left(t_cp_ra_s_lst_sorted, tau_d_max_s)
    if t_cp_ra_s_lst_sorted_bisect_left < len(t_cp_ra_s_lst_sorted):
        t_cp_min_ra = t_cp_ra_s_lst_sorted[t_cp_ra_s_lst_sorted_bisect_left]
    else:
        # no value for t_cp_min_ra >= tau_d_max_s exists. This means, that no Cyclic Prefix duration larger than the maximum delay spread could be found
        raise ValueError("No cyclic prefix duration larger than the maximum delay spread of {0} µs could be found!".format(tau_d_max_s * 1_000_000))

    t_cp_ra_s_lst_sorted_subset = [x for x in t_cp_ra_s_lst_sorted if t_cp_min_ra <= x <= t_cp_max_ra]

    applicable_t_cp_ra_dict = {k: t_cp_ra_dict[k] for k in t_cp_ra_s_lst_sorted_subset if k in t_cp_ra_dict}

    return applicable_t_cp_ra_dict


def compute_applicable_t_gt_ra_dict(t_rt_max_s: float):
    """Compute combinations of applicable PRACH guard time durations t_GT^RA.
    This results in a subset of compute_all_t_gt_ra_dict, containing all applicable t_CP^RA with their assigned PRACH preamble formats, Δf_RA, RACH occasion duration, and PRACH preamble duration.

    .. note::
        The lower boundary t_GT,min^RA is defined by the maximum round-trip time t_RT,max:
            ``t_GT,min^RA >= t_RT,max``

        Currently, no upper boundary is defined.

    .. code-block::
        :caption: Output dictionary pattern:

            {
                t_gt_ra: {
                    prach_preamble_format: {
                        "Delta f_RA": delta_f_ra_hz,
                        "RACH occasion duration": t_dur_ra,
                        "PRACH preamble duration": t_n_cp_ra
                    },
                    prach_preamble_format: {
                        "Delta f_RA": delta_f_ra_hz,
                        "RACH occasion duration": t_dur_ra,
                        "PRACH preamble duration": t_n_cp_ra
                    }
                }
            }

    Parameters
    ----------
    t_rt_max_s : float
        The maximum round-trip time in seconds due to cell radius r_cell.

    Raises
    ------
    ValueError
        If no guard time larger than the round-trip delay could be found.

    Returns
    -------
    applicable_t_gt_ra_dict
        A dict of the applicable PRACH guard time durations, given in seconds, and PRACH preamble formats.

    """
    t_gt_ra_dict = compute_all_t_gt_ra_dict()
    t_gt_ra_s_lst_sorted = sorted(t_gt_ra_dict.keys())

    t_gt_ra_s_lst_sorted_bisect_left = bisect.bisect_left(t_gt_ra_s_lst_sorted, t_rt_max_s)
    if t_gt_ra_s_lst_sorted_bisect_left < len(t_gt_ra_s_lst_sorted):
        t_gt_min_ra = t_gt_ra_s_lst_sorted[t_gt_ra_s_lst_sorted_bisect_left]
    else:
        # no value for t_gt_min_ra >= t_rt_max_s exists. This means, that no Guard Time larger than the round-trip delay could be found
        raise ValueError("No guard time longer larger the round-trip delay of {0} µs could be found!".format(t_rt_max_s * 1_000_000))

    t_gt_ra_s_lst_sorted_subset = [x for x in t_gt_ra_s_lst_sorted if x >= t_gt_min_ra]

    applicable_t_gt_ra_dict = {k: t_gt_ra_dict[k] for k in t_gt_ra_s_lst_sorted_subset if k in t_gt_ra_dict}

    return applicable_t_gt_ra_dict


def filter_prach_dict(input_dict: dict, match_set: set):
    """Filter a PRACH dictionary based on a matching set of second-level keys and third-level values.

    Parameters
    ----------
    input_dict : dict
        The input dictionary.
    match_set : set
        The dictionary to match.

    Returns
    -------
    filtered_dict : dict
        The filtered dictionary.
    """
    filtered_dict = {}

    for top_key, level2 in input_dict.items():
        filtered_level2 = {}

        for k2, level3 in level2.items():
            pair = (k2, level3.get("Delta f_RA"))

            if pair in match_set:
                filtered_level2[k2] = level3

        if filtered_level2:  # only keep non-empty entries
            filtered_dict[top_key] = filtered_level2

    return filtered_dict


def extract_ordered_pairs_prach_tuple(input_dict: dict):
    """Extract the second-level keys and third-level values from a nested dictionary, while preserving the order defined by their original top-level keys.

    Parameters
    ----------
    input_dict : dict
        The input dictionary.

    Returns
    -------
    ordered_pairs_prach_tuple: tuple
        The ordered pairs of matching values.
    """
    ordered_pairs_prach_tuple = tuple(
        (k2, level3["Delta f_RA"])
        for top_key in input_dict
        for k2, level3 in input_dict[top_key].items()
    )
    return ordered_pairs_prach_tuple


def balanced_min_max_rank(tuple1: tuple, tuple2: tuple):
    """Create ranked minimum and maximum entries matching between two tuples.
    Favors tuple1 for the maximum and tuple2 for the minimum, if the lowest or highest matching entries of both tuples are symmetrically cross-placed:
    * ``tuple1 = ((1,2),(3,4),(5,6),(7,8))``
    * ``tuple2 = ((3,4),(1,2),(7,8),(5,6))``
    * ``result = ((3,4),(7,8))``

    Parameters
    ----------
    tuple1 : tuple
        The first input tuple.
    tuple2 : tuple
        The second input tuple.

    Returns
    -------
    (min_item, max_item): tuple
        The minimum and maximum item in a tuple.
    """
    pos1 = {v: i for i, v in enumerate(tuple1)}
    pos2 = {v: i for i, v in enumerate(tuple2)}

    common_in_order = [x for x in tuple1 if x in pos2]

    # score = sum of positions
    min_item = min(common_in_order, key=lambda x: pos1[x] + pos2[x])
    max_item = max(common_in_order, key=lambda x: pos1[x] + pos2[x])

    return min_item, max_item


def verify_prach_occasion_validity(duplex_mode: str, freq_range: str, tdd_ul_dl_configuration_common_provided: bool, dl_symbols_tuple: tuple, ul_symbols_tuple: tuple, ss_pbch_symbols_tuple: tuple, prach_occasion_symbols_tuple: tuple, channel_access_mode: str, preamble_scs_hz: int, prach_conf_idx: int):
    """Verify that a PRACH occasion is valid according to TS 38.213 ch. 8.1 and Table 8.1-2.

    Parameters
    ----------
    duplex_mode: str
        The duplex mode, either FDD or TDD.

    freq_range: str
        The frequency range, either FR1 or FR2.

    tdd_ul_dl_configuration_common_provided: bool
        Indicates whether a tdd-UL-DL-ConfigurationCommon is provided.

    dl_symbols_tuple: tuple
        A tuple indicating all downlink symbols in a 5G NR frame. This is based on tdd-UL-DL-ConfigurationCommon.

    ul_symbols_tuple: tuple
        A tuple indicating all uplink symbols in a 5G NR frame. This is based on tdd-UL-DL-ConfigurationCommon.

    ss_pbch_symbols_tuple: tuple
        A tuple indicating the symbols occupied by SS/PBCH blocks. This is based on ssb-PositionsInBurst in SIB1 or in ServingCellConfigCommon, giving cases A-F.

    prach_occasion_symbols_tuple: tuple
        A tuple indicating the symbols occupied by PRACH occasions.

    channel_access_mode: str
        Indicates which channelAccessMode is provided. Choices are: static, semistatic, and dynamic (lower case only).

    preamble_scs_hz: int
        The subcarrier spacing of the RACH preamble.

    prach_conf_idx: int
        The PRACH configuration index.

    Returns
    -------
    prach_to_ssb_gap_validity: bool
        True, if the PRACH occasion is valid.

    Raises
    ------
    TypeError
        If duplex_mode is not of type str.

    TypeError
        If freq_range is not of type str.

    TypeError
        If tdd_ul_dl_configuration_common_provided is not of type bool.

    TypeError
        If dl_symbols_tuple is not of type tuple.

    TypeError
        If ul_symbols_tuple is not of type tuple.

    TypeError
        If ss_pbch_symbols_tuple is not of type tuple.

    TypeError
        If prach_occasion_symbols_tuple is not of type tuple.

    TypeError
        If channel_access_mode is not of type str.

    TypeError
        If preamble_scs_hz is not of type int.

    TypeError
        if prach_conf_idx is not of type int.

    ValueError
        If duplex_mode is not in [FDD, TDD].

    ValueError
        If freq_range is not FR1 or FR2.

    ValueError
        If channel_access_mode.lower() is not in [static, semistatic, dynamic].

    ValueError
        If preamble_scs_hz is not in [1250, 5000, 15000, 30000, 60000, 120000, 480000, 960000].

    ValueError
        If prach_conf_idx is not in range 0-262.

    ValueError
        IF the combination of nr_freq_range and nr_duplex_mode is not supported.

    ValueError
        If tdd_ul_dl_configuration_common_provided is False.
        This reflects the current support of OpenAirInterface5G.

    ValueError
        If channel_access_mode is semistatic or dynamic.
        This reflects the current support of OpenAirInterface5G.

    """
    if not isinstance(duplex_mode, str):
        raise TypeError("duplex_mode should be of type str, but is {0}!".format(type(duplex_mode)))
    if not isinstance(freq_range, str):
        raise TypeError("freq_range should be of type str, but is {0}!".format(type(freq_range)))
    if not isinstance(tdd_ul_dl_configuration_common_provided, bool):
        raise TypeError("tdd_ul_dl_configuration_common_provided should be of type bool, but is {0}!".format(type(tdd_ul_dl_configuration_common_provided)))
    if not isinstance(dl_symbols_tuple, tuple):
        raise TypeError("dl_symbols_tuple should be of type tuple, but is {0}!".format(type(dl_symbols_tuple)))
    if not isinstance(ul_symbols_tuple, tuple):
        raise TypeError("ul_symbols_tuple should be of type tuple, but is {0}!".format(type(ul_symbols_tuple)))
    if not isinstance(ss_pbch_symbols_tuple, tuple):
        raise TypeError("ss_pbch_symbols_tuple should be of type tuple, but is {0}!".format(type(ss_pbch_symbols_tuple)))
    if not isinstance(prach_occasion_symbols_tuple, tuple):
        raise TypeError("prach_occasion_symbols_tuple should be of type tuple, but is {0}!".format(type(prach_occasion_symbols_tuple)))
    if not isinstance(channel_access_mode, str):
        raise TypeError("channel_access_mode should be of type str, but is {0}!".format(type(channel_access_mode)))
    if not isinstance(preamble_scs_hz, int):
        raise TypeError("preamble_scs_hz should be of type int, but is {0}!".format(type(preamble_scs_hz)))
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))

    if duplex_mode not in ["FDD", "TDD"]:
        raise ValueError("The duplex_mode {0} is not supported!".format(duplex_mode))
    if freq_range not in ["FR1", "FR2"]:
        raise ValueError("An freq_range of {0} is not supported!".format(freq_range))
    if channel_access_mode.lower() not in ["static", "semistatic", "dynamic"]:
        raise ValueError("The channel_access_mode {0} is not supported!".format(channel_access_mode))
    if preamble_scs_hz not in [1250, 5000, 15000, 30000, 60000, 120000, 480000, 960000]:
        raise ValueError("A preamble_scs_hz of {0} Hz is not supported!".format(preamble_scs_hz))
    if prach_conf_idx < 0 or prach_conf_idx > 262:
        raise ValueError("A prach_conf_idx of {0} is not supported!".format(prach_conf_idx))

    if freq_range == "FR1" and duplex_mode == "FDD":
        prach_preamble_format = str(tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=prach_conf_idx)['Preamble format'][0])
    elif freq_range == "FR1" and duplex_mode == "TDD":
        prach_preamble_format = str(tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=prach_conf_idx)['Preamble format'][0])
    elif freq_range == "FR2" and duplex_mode == "TDD":
        prach_preamble_format = str(tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=prach_conf_idx)['Preamble format'][0])
    else:
        raise ValueError("The combination of {0} and {1} is not supported!".format(freq_range, duplex_mode))

    prach_to_ssb_gap_validity = False

    # OpenAirInterface5G: unsupported options (version check might apply!)
    if channel_access_mode.lower() in ["semistatic", "dynamic"]:
        raise ValueError("OpenAirInterface5G currently only supports static channel access mode!")
    if tdd_ul_dl_configuration_common_provided is False:
        raise ValueError("OpenAirInterface5G currently only supports providing a tdd-UL-DL-ConfigurationCommon!")

    # For paired spectrum or supplementary uplink band all PRACH occasions are valid.
    if duplex_mode == "FDD":
        prach_to_ssb_gap_validity = True

    # For unpaired spectrum
    else:
        # For preamble format B4 [TS 38.211], N_gap = 0.
        if prach_preamble_format == 'B4':
            n_gap = 0
        else:
            n_gap = tables.ts_38_213_table_8_1_2(preamble_scs_hz=preamble_scs_hz)

        if tdd_ul_dl_configuration_common_provided is True:

            if all(item in ul_symbols_tuple for item in prach_occasion_symbols_tuple):
                prach_to_ssb_gap_validity = True

            else:
                prach_occasion_slots_tuple = tuple(
                    set(
                        tuple(math.floor(x / N_SYMB_PER_SLOT) for x in prach_occasion_symbols_tuple)
                    )
                )

                # Test: PRACH occasion starts at least N_gap symbols after a last downlink symbol

                for k, g in groupby(enumerate(dl_symbols_tuple), lambda i_x: i_x[0] - i_x[1]):
                    dl_symbols_subgroup_tuple = tuple(map(itemgetter(1), g))
                    first_dl_symbol = min(dl_symbols_subgroup_tuple)
                    last_dl_symbol = max(dl_symbols_subgroup_tuple)

                    for prach_occ_symb in prach_occasion_symbols_tuple:

                        # Check if the PRACH symbol should be evaluated in this subgroup.
                        # If the PRACH symbol is associated with a later subgroup, it will be evaluated then again.
                        if prach_occ_symb >= first_dl_symbol:
                            prach_to_ssb_gap_validity = False

                            # Check if the PRACH symbol is at least n_gap symbols after the last DL symbol
                            if prach_occ_symb > last_dl_symbol + n_gap:
                                prach_to_ssb_gap_validity = True
                            else:
                                print("    PRACH occasion symbol {0} is NOT at least {1} symbols after Downlink symbol {2}".format(prach_occ_symb, n_gap, last_dl_symbol))
                                prach_to_ssb_gap_validity = False
                                return prach_to_ssb_gap_validity

                # Test: PRACH occasion does not precede an SS/PBCH block in the PRACH slot

                for ss_pbch_symb in ss_pbch_symbols_tuple:
                    ss_pbch_block_slot = math.floor(ss_pbch_symb / N_SYMB_PER_SLOT)

                    # SS/PBCH block in a PRACH slot
                    if ss_pbch_block_slot in prach_occasion_slots_tuple:

                        for prach_occ_symb in prach_occasion_symbols_tuple:

                            # PRACH occasion is in the the slot
                            if math.floor(prach_occ_symb / N_SYMB_PER_SLOT) == ss_pbch_block_slot:
                                prach_to_ssb_gap_validity = False
                                if ss_pbch_symb < prach_occ_symb:
                                    prach_to_ssb_gap_validity = True
                                else:
                                    print("    PRACH occasion symbol {0} precedes or overlaps with SS/PBCH block symbol {1}".format(prach_occ_symb, ss_pbch_symb))
                                    prach_to_ssb_gap_validity = False
                                    return prach_to_ssb_gap_validity

                # Test: PRACH occasion starts at least N_gap symbols after a last SS/PBCH block symbol

                last_ss_pbch_block_symb_tuple = ss_pbch_symbols_tuple[::4]

                for prach_occ_symb in prach_occasion_symbols_tuple:

                    for last_ss_pbch_symb in last_ss_pbch_block_symb_tuple:

                        prach_to_ssb_gap_validity = False
                        if last_ss_pbch_symb + n_gap < prach_occ_symb:
                            prach_to_ssb_gap_validity = True
                        else:
                            print("    PRACH occasion symbol {0} is NOT at least {1} symbols after the last symbol {2} in an SS/PBCH block".format(prach_occ_symb, n_gap, last_ss_pbch_symb))
                            prach_to_ssb_gap_validity = False
                            return prach_to_ssb_gap_validity

    return prach_to_ssb_gap_validity


def compute_ssb_time_domain_transmission_pattern(case: str, nr_channel_center_freq_hz: int, duplex_mode: str, shared_spectrum_channel_access: bool):
    """Compute the OFDM starting symbols of the candidate SSBs according to 3GPP TS 38.213 4.1.
    This is the time domain transmission pattern for the SSBs.

    :Cases:
        * Case A: 15 kHz, s = s_params + 14*n = {2, 8} + 14*n
        * Case B: 30 kHz, s = s_params + 14*n = {4, 8, 16, 20} + 28*n
        * Case C: 30 kHz, s = s_params + 14*n = {2, 8} + 14*n
        * Case D: 120 kHz, s = s_params + 14*n = {4, 8, 16, 20} + 28*n
        * Case E: 240 kHz, s = s_params + 14*n = {8, 12, 16, 20, 32, 36, 40, 44} + 56*n
        * Case F: 480 kHz, s = s_params + 14*n = {2, 9} + 14*n
        * Case G: 960 kHz, s = s_params + 14*n = {2, 9} + 14*n

    Parameters
    ----------
    case : str
        The time domain transmission pattern case.
        Choices: A, b, C, D, E, F, and G.

    nr_channel_center_freq_hz : int
        The 5G NR Channel Center Frequency in Hz.

    duplex_mode : str
        The duplex mode, either FDD or TDD.
        This is only relevant for Case C.

    shared_spectrum_channel_access : bool
        True, if operation with shared spectrum channel access applies, as described in 3GPP TS 37.213.

    Returns
    -------
    ssb_candidate_start_symbols : tuple
        The OFDM starting symbols of the candidate SSBs.
    l_max : int
        The maximum number of SS/PBCH block indexes in a cell, and the maximum number of transmitted SS/PBCH blocks within a half frame.

    Raises
    ------
    TypeError
        If case is not of type str.

    TypeError
        If nr_channel_center_freq_hz is not of type int.

    TypeError
        If duplex_mode is not of type str.

    TypeError
        If shared_spectrum_channel_access is not of type bool.

    ValueError
        If case is not in [A, B, C, D, E, F, G].

    ValueError
        If nr_channel_center_freq_hz is not in one of FR1 or FR2 frequencies.

    ValueError
        If duplex_mode is not in [FDD, TDD].

    ValueError
        If the parameter combination is supported.

    """
    if not isinstance(case, str):
        raise TypeError("case should be of type str, but is {0}!".format(type(case)))
    if not isinstance(nr_channel_center_freq_hz, int):
        raise TypeError("nr_channel_center_freq_hz should be of type int, but is {0}!".format(type(nr_channel_center_freq_hz)))
    if not isinstance(duplex_mode, str):
        raise TypeError("duplex_mode should be of type str, but is {0}!".format(type(duplex_mode)))
    if not isinstance(shared_spectrum_channel_access, bool):
        raise TypeError("shared_spectrum_channel_access should be of type bool, but is {0}!".format(type(shared_spectrum_channel_access)))

    if case not in SSB_CASES:
        raise ValueError("Case {0} is not supported!".format(case))
    if nr_channel_center_freq_hz not in range(freq_range_designation_dict["FR1"][0], freq_range_designation_dict["FR1"][1] + 1):
        if nr_channel_center_freq_hz not in range(freq_range_designation_dict["FR2"][0], freq_range_designation_dict["FR2"][1] + 1):
            raise ValueError("A nr_channel_center_freq_hz of {0} Hz is not supported!".format(nr_channel_center_freq_hz))
    if duplex_mode not in ["FDD", "TDD"]:
        raise ValueError("The duplex_mode {0} is not supported!".format(duplex_mode))

    ssb_candidate_start_symbols = tuple()
    n_params = tuple()
    s_params = tuple()
    s_candidate = 0
    l_max = 0

    # Case A
    if case == "A":
        s_params = (2, 8)
        n_factor = 14
        if shared_spectrum_channel_access is False:
            if nr_channel_center_freq_hz <= int(3000 * 1000000):
                n_params = (0, 1)
                l_max = 4
            elif nr_channel_center_freq_hz > int(3000 * 1000000) and nr_channel_center_freq_hz <= freq_range_designation_dict["FR1"][1]:
                n_params = (0, 1, 2, 3)
                l_max = 8
            else:
                raise ValueError("The parameter combination of case = {0}, nr_channel_center_freq_hz = {1}, duplex_mode = {2}, and shared_spectrum_channel_access = {3} is not supported!".format(case, nr_channel_center_freq_hz, duplex_mode, shared_spectrum_channel_access))
        else:
            n_params = (0, 1, 2, 3, 4)
            l_max = 0  # unknown
    # Case B
    elif case == "B":
        s_params = (4, 8, 16, 20)
        n_factor = 28
        if shared_spectrum_channel_access is False:
            if nr_channel_center_freq_hz <= int(3000 * 1000000):
                n_params = (0,)
                l_max = 4
            elif nr_channel_center_freq_hz > int(3000 * 1000000) and nr_channel_center_freq_hz <= int(6000 * 1000000):
                n_params = (0, 1)
                l_max = 8
            else:
                raise ValueError("The parameter combination of case = {0}, nr_channel_center_freq_hz = {1}, duplex_mode = {2}, and shared_spectrum_channel_access = {3} is not supported!".format(case, nr_channel_center_freq_hz, duplex_mode, shared_spectrum_channel_access))
        else:
            raise ValueError("The parameter combination of case = {0}, nr_channel_center_freq_hz = {1}, duplex_mode = {2}, and shared_spectrum_channel_access = {3} is not supported!".format(case, nr_channel_center_freq_hz, duplex_mode, shared_spectrum_channel_access))
    # Case C
    elif case == "C":
        s_params = (2, 8)
        n_factor = 14
        if shared_spectrum_channel_access is False:
            if duplex_mode == "FDD":
                if nr_channel_center_freq_hz <= int(3000 * 1000000):
                    n_params = (0, 1)
                    l_max = 4
                elif nr_channel_center_freq_hz > int(3000 * 1000000) and nr_channel_center_freq_hz <= freq_range_designation_dict["FR1"][1]:
                    n_params = (0, 1, 2, 3)
                    l_max = 8
                else:
                    raise ValueError("The parameter combination of case = {0}, nr_channel_center_freq_hz = {1}, duplex_mode = {2}, and shared_spectrum_channel_access = {3} is not supported!".format(case, nr_channel_center_freq_hz, duplex_mode, shared_spectrum_channel_access))
            elif duplex_mode == "TDD":
                if nr_channel_center_freq_hz < int(1880 * 1000000):
                    n_params = (0, 1)
                    l_max = 4
                elif nr_channel_center_freq_hz >= int(1880 * 1000000) and nr_channel_center_freq_hz <= int(3000 * 1000000):
                    n_params = (0, 1, 2, 3)
                    l_max = 8
                elif nr_channel_center_freq_hz > int(3000 * 1000000) and nr_channel_center_freq_hz <= freq_range_designation_dict["FR1"][1]:
                    n_params = (0, 1, 2, 3)
                    l_max = 8
                else:
                    raise ValueError("The parameter combination of case = {0}, nr_channel_center_freq_hz = {1}, duplex_mode = {2}, and shared_spectrum_channel_access = {3} is not supported!".format(case, nr_channel_center_freq_hz, duplex_mode, shared_spectrum_channel_access))
        else:
            n_params = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
            l_max = 0  # unknown
    # Case D
    elif case == "D":
        s_params = (4, 8, 16, 20)
        n_factor = 28
        if nr_channel_center_freq_hz >= freq_range_designation_dict["FR2"][0] and nr_channel_center_freq_hz <= freq_range_designation_dict["FR2"][1]:
            n_params = (0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18)
            l_max = 64
        else:
            raise ValueError("The parameter combination of case = {0}, nr_channel_center_freq_hz = {1}, duplex_mode = {2}, and shared_spectrum_channel_access = {3} is not supported!".format(case, nr_channel_center_freq_hz, duplex_mode, shared_spectrum_channel_access))
    # Case E
    elif case == "E":
        s_params = (8, 12, 16, 20, 32, 36, 40, 44)
        n_factor = 56
        if nr_channel_center_freq_hz >= freq_range_designation_dict["FR2-1"][0] and nr_channel_center_freq_hz <= freq_range_designation_dict["FR2-1"][1]:
            n_params = (0, 1, 2, 3, 5, 6, 7, 8)
            l_max = 64
        else:
            raise ValueError("The parameter combination of case = {0}, nr_channel_center_freq_hz = {1}, duplex_mode = {2}, and shared_spectrum_channel_access = {3} is not supported!".format(case, nr_channel_center_freq_hz, duplex_mode, shared_spectrum_channel_access))
    # Case F
    elif case == "F":
        s_params = (2, 9)
        n_factor = 14
        if nr_channel_center_freq_hz >= freq_range_designation_dict["FR2-2"][0] and nr_channel_center_freq_hz <= freq_range_designation_dict["FR2-2"][1]:
            n_params = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)
            l_max = 64
        else:
            raise ValueError("The parameter combination of case = {0}, nr_channel_center_freq_hz = {1}, duplex_mode = {2}, and shared_spectrum_channel_access = {3} is not supported!".format(case, nr_channel_center_freq_hz, duplex_mode, shared_spectrum_channel_access))
    # Case G
    elif case == "G":
        s_params = (2, 9)
        n_factor = 14
        if nr_channel_center_freq_hz >= freq_range_designation_dict["FR2-2"][0] and nr_channel_center_freq_hz <= freq_range_designation_dict["FR2-2"][1]:
            n_params = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)
            l_max = 64
        else:
            raise ValueError("The parameter combination of case = {0}, nr_channel_center_freq_hz = {1}, duplex_mode = {2}, and shared_spectrum_channel_access = {3} is not supported!".format(case, nr_channel_center_freq_hz, duplex_mode, shared_spectrum_channel_access))

    for n in n_params:
        for param in s_params:
            s_candidate = param + n_factor * n
            ssb_candidate_start_symbols = ssb_candidate_start_symbols + (s_candidate,)
    return tuple(sorted(ssb_candidate_start_symbols)), l_max


def get_ssb_case(freq_band: int, scs_hz: int):
    """Get the SSB burst pattern case from the Frequency Band and the Subcarrier Spacing.
    This refers to 3GPP TS 38.213 ch. 4.1 for all Subcarrier Spacing values except 30 kHz, which is linked to both Case B and C.
    In that case, this function refers to TS_38_104_TABLE_5_4_3_3_1.
    The other tables are not used, since they do not contain Case B or C.

    .. note::
        This function does *not* check if the given combination of Frequency Band, Subcarrier Spacing, and Channel Bandwidth is valid.

    Parameters
    ----------
    freq_band : int
        The frequency band.

    scs_hz : int
        The Subcarrier Spacing in Hz.

    Returns
    -------
    str
        The SSB burst pattern case.

    Raises
    ------
    TypeError
        If freq_band is not of type int.

    TypeError
        If scs_hz is not of type int.

    ValueError
        If freq_band is not a valid 5G NR Frequency Band.

    ValueError
        If scs_hz is not a valid Subcarrier Spacing.

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if not isinstance(scs_hz, int):
        raise TypeError("scs_hz should be of type int, but is {0}!".format(type(scs_hz)))
    if freq_band not in tables.NR_FR1_FREQ_BANDS_LIST and freq_band not in tables.NR_FR2_FREQ_BANDS_LIST:
        raise ValueError("n{0} is not a valid Frequency Band!".format(freq_band))
    if scs_hz not in list(SCS_HZ_TO_SSB_CASE.keys()):
        raise ValueError("{0} kHz is not a valid Subcarrier Spacing!".format(scs_hz))

    if isinstance(SCS_HZ_TO_SSB_CASE[scs_hz], list):
        return str(tables.ts_38_104_table_5_4_3_3_1(freq_band=freq_band)[(int(scs_hz / 1000), "kHz")]["SS Block pattern"][0].split(' ')[1])
    else:
        return SCS_HZ_TO_SSB_CASE[scs_hz]


def compute_ul_dl_symbols_per_frame(mu_ref: int, slot_configuration_period_ms: float, n_dl_slots: int, n_dl_symbols: int, n_ul_slots: int, n_ul_symbols: int):
    """Compute the Uplink, Downlink and Flexible symbols per NR Radio Frame.
    This is based on the slot configuration according to 3GPP TS 38.213 ch. 11.1, which is also known as pattern1.

    .. code-block::
        :caption: The configuration has the following pattern:

        | DL Slots | DL Symbols & Flexible Symbols | Flexible Slots | Flexible Symbols & Uplink Symbols | Uplink Slots |
        |<-------------------------------------- dl-UL-TransmissionPeriodicity --------------------------------------->|

    If dl-UL-TransmissionPeriodicity is not equal to 10 ms (the Frame duration), then the pattern is repeatet until 10 ms are reached.

    Parameters
    ----------
    mu_ref : int
        The Reference Subcarrier Spacing µ_ref

    slot_configuration_period_ms : float
        The Slot Configuration Period P.
        This is defined by the parameter dl-UL-TransmissionPeriodicity.

    n_dl_slots : int
        Number of Downlink Slots per Period.

    n_dl_symbols : int
        Number of Downlink Symbols per Period.

    n_ul_slots : int
        Number of Uplink Slots per Period.

    n_ul_symbols : int
        Number of Uplink Symbols per Period.

    Returns
    -------
    downlink_symbols_tuple : tuple
        The symbols configured as downlink in a NR Radio Frame.

    flexible_symbols_tuple : tuple
        The symbols configured as flexible in a NR Radio Frame.

    uplink_symbols_tuple : tuple
        The symbols configured as uplink in a NR Radio Frame.

    Raises
    ------
    TypeError
        If mu_ref: int.

    TypeError
        If slot_configuration_period_ms is not of type float.

    TypeError
        If n_dl_slots is not of type int.

    TypeError
        If n_dl_symbols is not of type int.

    TypeError
        If n_ul_slots is not of type int.

    TypeError
        If n_ul_symbols is not of type int.

    ValueError
        If mu_ref is not in [0,1,2,3,4,5,6].

    ValueError
        If slot_configuration_period_ms is not in [0.5,0.625,1.0,1.25,2.0,2.5,5.0,10.0].

    ValueError
        If too many or not enough OFDM symbols have been configured for a Slot Configuration Period P.

    ValueError
        If too many or not all OFDM symbols have been assigned to DL, Flex, and UL.

    """
    if not isinstance(mu_ref, int):
        raise TypeError("mu_ref should be of type int, but is {0}!".format(type(mu_ref)))
    if not isinstance(slot_configuration_period_ms, float):
        raise TypeError("slot_configuration_period_ms should be of type float, but is {0}!".format(type(slot_configuration_period_ms)))
    if not isinstance(n_dl_slots, int):
        raise TypeError("n_dl_slots should be of type int, but is {0}!".format(type(n_dl_slots)))
    if not isinstance(n_dl_symbols, int):
        raise TypeError("n_dl_symbols should be of type int, but is {0}!".format(type(n_dl_symbols)))
    if not isinstance(n_ul_slots, int):
        raise TypeError("n_ul_slots should be of type int, but is {0}!".format(type(n_ul_slots)))
    if not isinstance(n_ul_symbols, int):
        raise TypeError("n_ul_symbols should be of type int, but is {0}!".format(type(n_ul_symbols)))
    if mu_ref not in tables.NUMEROLOGY_RANGE_LIST:
        raise ValueError("A mu_ref of {0} is not supported!".format(mu_ref))
    if slot_configuration_period_ms not in [*DL_UL_TRANSMISSION_PERIODICITY_MS.values()]:
        raise ValueError("A slot_configuration_period_ms of {0} ms is not supported!".format(slot_configuration_period_ms))

    # Number of P per NR Radio Frame
    n_p_per_frame = int(
        math.floor(
            10.0 / slot_configuration_period_ms
        )
    )

    # Number of slots per P
    n_s_per_p = int(
        math.floor(
            slot_configuration_period_ms * math.pow(2, mu_ref)
        )
    )

    n_slots_per_frame = tables.ts_38_211_table_4_3_2_1(mu=mu_ref, col="N slots per frame")
    n_symbols_per_frame = N_SYMB_PER_SLOT * n_slots_per_frame
    n_symbols_per_p = N_SYMB_PER_SLOT * n_s_per_p
    n_dl_symbols_per_p = n_dl_slots * N_SYMB_PER_SLOT + n_dl_symbols
    n_ul_symbols_per_p = n_ul_slots * N_SYMB_PER_SLOT + n_ul_symbols
    n_flex_symbols_per_p = abs(n_symbols_per_p - (n_dl_symbols_per_p + n_ul_symbols_per_p))

    if (n_dl_symbols_per_p + n_ul_symbols_per_p + n_flex_symbols_per_p) != n_symbols_per_p:
        raise ValueError(
            "{0} OFDM symbols have been configured for a Slot Configuration Period P. However, only {1} OFDM Symbols are available per Slot Configuration Period P!".format(
                (n_dl_symbols_per_p + n_ul_symbols_per_p + n_flex_symbols_per_p),
                n_symbols_per_p
            )
        )

    downlink_symbols_tuple = tuple()
    flexible_symbols_tuple = tuple()
    uplink_symbols_tuple = tuple()

    for p in range(n_p_per_frame):
        downlink_symbols_tuple = downlink_symbols_tuple + tuple(p * n_symbols_per_p + x for x in range(n_dl_symbols_per_p))
        flexible_symbols_tuple = flexible_symbols_tuple + tuple(max(downlink_symbols_tuple) + 1 + x for x in range(n_flex_symbols_per_p))
        uplink_symbols_tuple = uplink_symbols_tuple + tuple(max(flexible_symbols_tuple) + 1 + x for x in range(n_ul_symbols_per_p))

    if tuple(range(n_symbols_per_frame)) != tuple(sorted(downlink_symbols_tuple + flexible_symbols_tuple + uplink_symbols_tuple)):
        raise ValueError("Either not all Symbols have been assigned to DL/Flex/UL, or too many Symbols have been assigned!")  # Not reached by tests. Only targets code errors.

    return downlink_symbols_tuple, flexible_symbols_tuple, uplink_symbols_tuple


def compute_pusch_rbs_occupied_by_prach(nr_freq_range: str, nr_duplex_mode: str, prach_conf_idx: int, l_ra: int, delta_f_ra_hz: int, nr_scs_hz: int, msg1_fdm_idx: int):
    """Compute the number of PUSCH Resource Blocks occupied by PRACH.
    For Δf_RA in {1.25, 5} kHz, µ=0 shall be assumed (3GPP TS 38.211 ch. 5.3.2).

    Parameters
    ----------
    nr_freq_range: str
        The frequency range, either FR1 or FR2.

    nr_duplex_mode: str
        The duplex mode, either FDD or TDD.

    prach_conf_idx: int
        The PRACH configuration index.

    l_ra: int
        The number of subcarriers in a PRACH preamble.
        Supported are 139, 839, 571, 1151.

    delta_f_ra_hz : int
        The subcarrier spacing for the PRACH sequences; Δf_RA.
        Supported are 1.25, 5, 15, 30, 60, 120, 480, and 960 kHz.
        The OAI5G config sets this in msg1_SubcarrierSpacing.

    nr_scs_hz: int
        The PUSCH subcarrier spacing in Hz.

    msg1_fdm_idx: int
        The index for msg1-FDM.
        Supported are 0, 1, 2, 3.

    Returns
    -------
    pusch_rbs_occupied_by_prach : int
        The number of PUSCH Resource Blocks (RBs) occupied by PRACH.

    Raises
    ------
    TypeError
        If nr_freq_range is not of type str.

    TypeError
        If nr_duplex_mode is not of type int.

    TypeError
        If prach_conf_idx is not of type int.

    TypeError
        If l_ra is not of type int.

    TypeError
        If delta_f_ra_hz is not of type int.

    TypeError
        If nr_scs_hz is not of type int.

    TypeError
        If msg1_fdm_idx is not of type int.

    ValueError
        If nr_freq_range is not FR1 or FR2.

    ValueError
        If nr_duplex_mode is not FDD or TDD.

    ValueError
        If prach_conf_idx is not in range 0-262.

    ValueError
        If l_ra is not 139, 839, 571, or 1151.

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA for the given frequency range.

    ValueError
        If nr_scs_hz is not a supported subcarrier spacing Δf.

    ValueError
        If msg1_fdm_idx is not 0, 1, 2, or 3.

    ValueError
        If l_ra is not compatible with the PRACH configuration.

    """
    if not isinstance(nr_freq_range, str):
        raise TypeError("nr_freq_range should be of type str, but is {0}!".format(type(nr_freq_range)))
    if not isinstance(nr_duplex_mode, str):
        raise TypeError("nr_duplex_mode should be of type str, but is {0}!".format(type(nr_duplex_mode)))
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))
    if not isinstance(l_ra, int):
        raise TypeError("l_ra should be of type int, but is {0}!".format(type(l_ra)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))
    if not isinstance(nr_scs_hz, int):
        raise TypeError("nr_scs_hz should be of type int, but is {0}!".format(type(nr_scs_hz)))
    if not isinstance(msg1_fdm_idx, int):
        raise TypeError("msg1_fdm_idx should be of type int, but is {0}!".format(type(msg1_fdm_idx)))
    if nr_freq_range not in ["FR1", "FR2"]:
        raise ValueError("An nr_freq_range of {0} is not supported!".format(nr_freq_range))
    if nr_duplex_mode not in ["TDD", "FDD"]:
        raise ValueError("An nr_duplex_mode of {0} is not supported!".format(nr_duplex_mode))
    if prach_conf_idx < 0 or prach_conf_idx > 262:
        raise ValueError("A prach_conf_idx of {0} is not supported!".format(prach_conf_idx))
    if l_ra not in [139, 839, 571, 1151]:
        raise ValueError("An l_ra of {0} is not supported!".format(l_ra))
    if delta_f_ra_hz not in freq_range_delta_f_ra_dict[nr_freq_range]:
        raise ValueError("A combination of delta_f_ra_hz {0} Hz and frequency range {1} is not supported!".format(delta_f_ra_hz, nr_freq_range))
    if nr_scs_hz not in [*SCS_HZ_TO_NUMEROLOGY]:
        raise ValueError("An nr_scs_hz of {0} is not supported!".format(nr_scs_hz))
    if msg1_fdm_idx not in [*MSG1_FDM]:
        raise ValueError("An msg1_fdm_idx of {0} is not supported!".format(msg1_fdm_idx))

    prach_preamble_format = compute_prach_preamble_format(nr_freq_range=nr_freq_range, nr_duplex_mode=nr_duplex_mode, prach_conf_idx=prach_conf_idx)

    if delta_f_ra_hz == 1250:
        delta_f_ra_khz = 1.25
        mu_msg1_numerology = 0
    elif delta_f_ra_hz in [5000, 15000, 30000, 60000, 120000, 480000, 960000]:
        delta_f_ra_khz = int(delta_f_ra_hz / 1000)
        if delta_f_ra_hz == 5000:
            mu_msg1_numerology = 0
        else:
            mu_msg1_numerology = SCS_HZ_TO_NUMEROLOGY[delta_f_ra_hz]

    l_ra_lst = []
    if prach_preamble_format in ['0', '1', '2', '3']:
        l_ra_lst.append(tables.ts_38_211_table_6_3_3_1_1(prach_preamble_format=prach_preamble_format)['L_RA'][0])
    else:
        if mu_msg1_numerology in [0, 1, 2, 3, 5, 6]:
            l_ra_lst.append(tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)["L_RA for mu in {0,1,2,3,5,6}"][0])
        if mu_msg1_numerology in [0, 3]:
            l_ra_lst.append(tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)["L_RA for mu in {0,3}"][0])
        if mu_msg1_numerology in [1, 3, 5]:
            l_ra_lst.append(tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)["L_RA for mu in {1,3,5}"][0])

    if l_ra not in l_ra_lst:
        raise ValueError("The L_RA choice is incompatibel with the PRACH configuration!")

    msg1_fdm_int = MSG1_FDM_INT[msg1_fdm_idx]

    pusch_rbs_occupied_by_prach = msg1_fdm_int * tables.ts_38_211_table_6_3_3_2_1(l_ra=l_ra, delta_f_ra_khz=float(delta_f_ra_khz), delta_f_khz=float(nr_scs_hz / 1000.))[0]

    return pusch_rbs_occupied_by_prach


def compute_pusch_ofdm_symbols_occupied_by_rach_occasions(nr_freq_range: str, nr_duplex_mode: str, prach_conf_idx: int, delta_f_ra_hz: int, delta_f_hz: int):
    """Compute the number PUSCH OFDM Symbols occupied by consecutive RACH occasion (RO).

    :Steps:
        1. Get PRACH SCS.
        2. Get PRACH Preamble Format using compute_prach_preamble_format().
        3. Get RO Configuration (Feed PRACH Preamble Format into tables.ts_38_211_table_6_3_3_1_1 - 2).
        4. Get PRACH Cyclic Prefix Duration (N_CP^RA * T_C) from Step 3.
        5. Get PRACH ZC Sequence Duration (N_u * T_C) from Step 3.
        6. Get N_dur^RA from PRACH configuration index and others into tables.ts_38_211_table_6_3_3_2_2 - 4.
        7. Get t_symb (OFDM symbol duration based on PRACH SCS).
        8. Get single RO Duration (N_dur^RA * t_symb).
        9. Get RO absolute Occasions using compute_rach_occasion_starting_symbols().
        10. Check overlap with PUSCH symbols (with separate PUSCH SCS) for each RO absolute Occasion.
        11. Create dictionary containing a tuple of occupied PUSCH OFDM symbols (values) for each RO (keys).

    Parameters
    ----------
    nr_freq_range : str
        The frequency range, either FR1 or FR2.
    nr_duplex_mode : str
        The duplex mode, either TDD or FDD.
    prach_conf_idx : int
        The PRACH configuration index.
    delta_f_ra_hz : int
        The PRACH subcarrier spacing in Hz.
    delta_f_hz : int
        The PUSCH subcarrier spacing in Hz.

    Returns
    -------
    pusch_ofdm_symbols_occupied_by_rach_occasions : float
        The number of PUSCH OFDM symbols occupied by RACH Occasions (RO).
        If this number contains decimal digits, a long Guard Time is expected to exist.

    Raises
    ------
    TypeError
        If nr_freq_range is not of type str.

    TypeError
        If nr_duplex_mode is not of type int.

    TypeError
        If prach_conf_idx is not of type int.

    TypeError
        If delta_f_ra_hz is not of type int.

    TypeError
        If delta_f_hz is not of type int.

    ValueError
        If nr_freq_range is not FR1 or FR2.

    ValueError
        If nr_duplex_mode is not FDD or TDD.

    ValueError
        If prach_conf_idx is not in range 0-262.

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA.

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA for the given frequency range.

    ValueError
        If delta_f_hz is not a supported subcarrier spacing Δf.

    ValueError
        If the given PRACH subcarrier spacing and PUSCH subcarrier spacing are not a valid combination.

    ValueError
        If the PRACH preamble format is not valid for the given PRACH subcarrier spacing.

    ValueError
        If duplex_mode is not valid for the given frequency range.

    """
    if not isinstance(nr_freq_range, str):
        raise TypeError("nr_freq_range should be of type str, but is {0}!".format(type(nr_freq_range)))
    if not isinstance(nr_duplex_mode, str):
        raise TypeError("nr_duplex_mode should be of type str, but is {0}!".format(type(nr_duplex_mode)))
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))
    if not isinstance(delta_f_hz, int):
        raise TypeError("delta_f_hz should be of type int, but is {0}!".format(type(delta_f_hz)))

    if nr_freq_range not in ["FR1", "FR2"]:
        raise ValueError("An nr_freq_range of {0} is not supported!".format(nr_freq_range))
    if nr_duplex_mode not in ["TDD", "FDD"]:
        raise ValueError("An nr_duplex_mode of {0} is not supported!".format(nr_duplex_mode))
    if prach_conf_idx < 0 or prach_conf_idx > 262:
        raise ValueError("A prach_conf_idx of {0} is not supported!".format(prach_conf_idx))
    if delta_f_ra_hz not in [*DELTA_F_RA_HZ]:
        raise ValueError("A value for delta_f_ra_hz of {0} Hz is not supported!".format(delta_f_ra_hz))
    if delta_f_ra_hz not in freq_range_delta_f_ra_dict[nr_freq_range]:
        raise ValueError("A combination of delta_f_ra_hz {0} Hz and frequency range {1} is not supported!".format(delta_f_ra_hz, nr_freq_range))
    if delta_f_hz not in [*SCS_HZ_TO_NUMEROLOGY]:
        raise ValueError("An delta_f_hz of {0} is not supported!".format(delta_f_hz))
    # 1
    # 2
    prach_preamble_format = compute_prach_preamble_format(nr_freq_range=nr_freq_range, nr_duplex_mode=nr_duplex_mode, prach_conf_idx=prach_conf_idx)

    if delta_f_ra_hz == 1250:
        delta_f_ra_khz = 1.25
        mu_msg1_numerology = 0
    elif delta_f_ra_hz in [5000, 15000, 30000, 60000, 120000, 480000, 960000]:
        delta_f_ra_khz = int(delta_f_ra_hz / 1000)
        if delta_f_ra_hz == 5000:
            mu_msg1_numerology = 0
        else:
            mu_msg1_numerology = SCS_HZ_TO_NUMEROLOGY[delta_f_ra_hz]

    # Check if combination of delta_f_ra_hz and delta_f_hz is permitted
    valid_rach_pusch_scs_counter = 0
    for l_ra in [139, 571, 839, 1151]:
        if tables.ts_38_211_table_6_3_3_2_1(l_ra=l_ra, delta_f_ra_khz=float(delta_f_ra_khz), delta_f_khz=float(delta_f_hz / 1000.)) is not None:
            valid_rach_pusch_scs_counter += 1
    if valid_rach_pusch_scs_counter == 0:
        raise ValueError("A combination of PRACH subcarrier spacing {0} kHz and PUSCH subcarrier spacing {1} kHz is not supported!".format(delta_f_ra_khz, int(delta_f_hz / 1000)))

    # Test for valid combinations of PRACH Preamble Format and PRACH SCS
    if prach_preamble_format in ['0', '1', '2', '3']:
        if delta_f_ra_khz != tables.ts_38_211_table_6_3_3_1_1(prach_preamble_format=prach_preamble_format)['Delta f_RA'][0]:
            raise ValueError("A combination of PRACH Preamble format {0} and PRACH subcarrier spacing {1} kHz is not supported!".format(prach_preamble_format, delta_f_ra_khz))
    else:
        if delta_f_ra_khz % int(tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)['Delta f_RA'][0][0]) != 0:
            raise ValueError("A combination of PRACH Preamble format {0} and PRACH subcarrier spacing {1} kHz is not supported!".format(prach_preamble_format, delta_f_ra_khz))

    # Compute actually occupied RACH resources (single RACH sequence with cyclic prefix)
    # 4: Compute N_CP^RA
    prach_cyclic_prefix_duration_samp = compute_prach_cyclic_prefix_duration(prach_preamble_format=prach_preamble_format)
    prach_cyclic_prefix_duration_s = prach_cyclic_prefix_duration_samp * KAPPA * T_C_S * math.pow(2, -1 * mu_msg1_numerology)
    # 5: Compute N_u
    prach_zc_sequences_duration_samp = compute_prach_zc_sequences_duration(prach_preamble_format=prach_preamble_format)
    prach_zc_sequences_duration_s = prach_zc_sequences_duration_samp * KAPPA * T_C_S * math.pow(2, -1 * mu_msg1_numerology)

    if nr_freq_range == "FR1" and nr_duplex_mode == "FDD":
        row = tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=prach_conf_idx)
    elif nr_freq_range == "FR1" and nr_duplex_mode == "TDD":
        row = tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=prach_conf_idx)
    elif nr_freq_range == "FR2" and nr_duplex_mode == "TDD":
        row = tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=prach_conf_idx)
    else:
        raise ValueError("The combination of {0} and {1} is not supported!".format(nr_freq_range, nr_duplex_mode))  # Not reached by tests. Only targets code errors.
    # Compute RACH occasion duration
    if prach_preamble_format in ['0', '1', '2', '3']:
        # The duration of this is not fully defined!
        # Assume PRACH occupying resources until the end of the last subframe.
        # 8: compute t_dur^RA in seconds
        t_dur_ra_s = math.ceil((prach_cyclic_prefix_duration_s + prach_zc_sequences_duration_s) / (1000 * 1e-6)) * (NR_RADIO_FRAME_DURATION_MS / (1000 * N_SUBFRAMES_PER_FRAME))
    else:
        # 6: Single Rach occasion duration as multiple of PRACH symbols
        n_dur_ra = row['PRACH duration'][0]
        # 7
        t_ra_symb_s = NR_RADIO_FRAME_DURATION_MS / (
            float(tables.ts_38_211_table_4_3_2_1(mu=mu_msg1_numerology, col="N symbols per slot")) * float(tables.ts_38_211_table_4_3_2_1(mu=mu_msg1_numerology, col="N slots per frame")) * 1000
        )
        # 8: compute t_dur^RA in seconds
        t_dur_ra_s = n_dur_ra * t_ra_symb_s  # Single RACH occasion duration in s

    # PUSCH OFDM symbol duration
    mu_pusch_numerology = SCS_HZ_TO_NUMEROLOGY[delta_f_hz]
    pusch_ofdm_symbol_duration_s = NR_RADIO_FRAME_DURATION_MS / (
        float(tables.ts_38_211_table_4_3_2_1(mu=mu_pusch_numerology, col="N symbols per slot")) * float(tables.ts_38_211_table_4_3_2_1(mu=mu_pusch_numerology, col="N slots per frame")) * 1000
    )

    max_rach_occasions_per_pusch_ofdm_symbol = pusch_ofdm_symbol_duration_s / t_dur_ra_s

    n_t_ra_slot = compute_n_t_ra_slot(
        prach_conf_idx=prach_conf_idx,
        freq_range=nr_freq_range,
        duplex_mode=nr_duplex_mode,
        delta_f_ra_hz=delta_f_ra_hz
    )

    pusch_ofdm_symbols_occupied_by_rach_occasions = n_t_ra_slot / max_rach_occasions_per_pusch_ofdm_symbol
    return pusch_ofdm_symbols_occupied_by_rach_occasions


def compute_prach_guard_times(nr_freq_range: str, nr_duplex_mode: str, prach_conf_idx: int, delta_f_ra_hz: int, delta_f_hz: int):
    """Compute the Guard Times for each RACH Occasion (RO).
    A GT is interpreted as the time between the end of the ZC sequence and the end of the last occupied PUSCH OFDM symbol.
    A short GT occurs when all occupied PUSCH OFDM symbols are fully covered by RACH ocasions.
    A long GT occurs when an occupied PUSCH OFDM symbol is not fully covered by RACH occasions, leaving a time gap until the end of the symbol.

    :Steps:
        1. Get dictionary containing a tuple of occupied PUSCH OFDM symbols for each RO using compute_pusch_ofdm_symbols_occupied_by_rach_occasions().
        2. Compute time span between end of ZC Sequence and end of last occupied PUSCH OFDM symbol; this is the Guard Time (GT)!
        3. Create tuple with all GTs for the given PRACH configuration; some GTs might vary if there is not perfect overlap between RO and PUSCH time grid.

    Parameters
    ----------
    nr_freq_range : str
        The frequency range, either FR1 or FR2.
    nr_duplex_mode : str
        The duplex mode, either TDD or FDD.
    prach_conf_idx : int
        The PRACH configuration index.
    delta_f_ra_hz : int
        The PRACH subcarrier spacing in Hz.
    delta_f_hz : int
        The PUSCH subcarrier spacing in Hz.

    Returns
    -------
    prach_guard_times_dict : dict
        The Guard Times for a given combination of PRACH configuration and PUSCH subcarrier spacing as a dict with keys:
        - "Short GT in s" (float): The short Guard Time in seconds. None, if no long GT exists.
        - "Long GT in s" (float): The long Guard Time in seconds. None, if no long GT exists.

    Raises
    ------
    TypeError
        If nr_freq_range is not of type str.

    TypeError
        If nr_duplex_mode is not of type int.

    TypeError
        If prach_conf_idx is not of type int.

    TypeError
        If delta_f_ra_hz is not of type int.

    TypeError
        If delta_f_hz is not of type int.

    ValueError
        If nr_freq_range is not FR1 or FR2.

    ValueError
        If nr_duplex_mode is not FDD or TDD.

    ValueError
        If prach_conf_idx is not in range 0-262.

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA.

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA for the given frequency range.

    ValueError
        If delta_f_hz is not a supported subcarrier spacing Δf.

    ValueError
        If the given PRACH subcarrier spacing and PUSCH subcarrier spacing are not a valid combination.

    ValueError
        If the PRACH preamble format is not valid for the given PRACH subcarrier spacing.

    ValueError
        If duplex_mode is not valid for the given frequency range.

    """
    if not isinstance(nr_freq_range, str):
        raise TypeError("nr_freq_range should be of type str, but is {0}!".format(type(nr_freq_range)))
    if not isinstance(nr_duplex_mode, str):
        raise TypeError("nr_duplex_mode should be of type str, but is {0}!".format(type(nr_duplex_mode)))
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))
    if not isinstance(delta_f_hz, int):
        raise TypeError("delta_f_hz should be of type int, but is {0}!".format(type(delta_f_hz)))

    if nr_freq_range not in ["FR1", "FR2"]:
        raise ValueError("An nr_freq_range of {0} is not supported!".format(nr_freq_range))
    if nr_duplex_mode not in ["TDD", "FDD"]:
        raise ValueError("An nr_duplex_mode of {0} is not supported!".format(nr_duplex_mode))
    if prach_conf_idx < 0 or prach_conf_idx > 262:
        raise ValueError("A prach_conf_idx of {0} is not supported!".format(prach_conf_idx))
    if delta_f_ra_hz not in [*DELTA_F_RA_HZ]:
        raise ValueError("A value for delta_f_ra_hz of {0} Hz is not supported!".format(delta_f_ra_hz))
    if delta_f_ra_hz not in freq_range_delta_f_ra_dict[nr_freq_range]:
        raise ValueError("A combination of delta_f_ra_hz {0} Hz and frequency range {1} is not supported!".format(delta_f_ra_hz, nr_freq_range))
    if delta_f_hz not in [*SCS_HZ_TO_NUMEROLOGY]:
        raise ValueError("An delta_f_hz of {0} is not supported!".format(delta_f_hz))

    prach_preamble_format = compute_prach_preamble_format(nr_freq_range=nr_freq_range, nr_duplex_mode=nr_duplex_mode, prach_conf_idx=prach_conf_idx)

    if delta_f_ra_hz == 1250:
        delta_f_ra_khz = 1.25
        mu_msg1_numerology = 0
    elif delta_f_ra_hz in [5000, 15000, 30000, 60000, 120000, 480000, 960000]:
        delta_f_ra_khz = int(delta_f_ra_hz / 1000)
        if delta_f_ra_hz == 5000:
            mu_msg1_numerology = 0
        else:
            mu_msg1_numerology = SCS_HZ_TO_NUMEROLOGY[delta_f_ra_hz]

    # Check if combination of delta_f_ra_hz and delta_f_hz is permitted
    valid_rach_pusch_scs_counter = 0
    for l_ra in [139, 571, 839, 1151]:
        if tables.ts_38_211_table_6_3_3_2_1(l_ra=l_ra, delta_f_ra_khz=float(delta_f_ra_khz), delta_f_khz=float(delta_f_hz / 1000.0)) is not None:
            valid_rach_pusch_scs_counter += 1
    if valid_rach_pusch_scs_counter == 0:
        raise ValueError("A combination of PRACH subcarrier spacing {0} kHz and PUSCH subcarrier spacing {1} kHz is not supported!".format(delta_f_ra_khz, int(delta_f_hz / 1000)))

    # Test for valid combinations of PRACH Preamble Format and PRACH SCS
    if prach_preamble_format in ['0', '1', '2', '3']:
        if delta_f_ra_khz != tables.ts_38_211_table_6_3_3_1_1(prach_preamble_format=prach_preamble_format)['Delta f_RA'][0]:
            raise ValueError("A combination of PRACH Preamble format {0} and PRACH subcarrier spacing {1} kHz is not supported!".format(prach_preamble_format, delta_f_ra_khz))
    else:
        if delta_f_ra_khz % int(tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)['Delta f_RA'][0][0]) != 0:
            raise ValueError("A combination of PRACH Preamble format {0} and PRACH subcarrier spacing {1} kHz is not supported!".format(prach_preamble_format, delta_f_ra_khz))
    # Compute actually occupied RACH resources (single RACH sequence with cyclic prefix)
    # 4: Compute N_CP^RA
    prach_cyclic_prefix_duration_samp = compute_prach_cyclic_prefix_duration(prach_preamble_format=prach_preamble_format)
    prach_cyclic_prefix_duration_s = prach_cyclic_prefix_duration_samp * KAPPA * T_C_S * math.pow(2, -1 * mu_msg1_numerology)
    # 5: Compute N_u
    prach_zc_sequences_duration_samp = compute_prach_zc_sequences_duration(prach_preamble_format=prach_preamble_format)
    prach_zc_sequences_duration_s = prach_zc_sequences_duration_samp * KAPPA * T_C_S * math.pow(2, -1 * mu_msg1_numerology)

    prach_occupied_resource_duration_single_s = prach_cyclic_prefix_duration_s + prach_zc_sequences_duration_s

    if nr_freq_range == "FR1" and nr_duplex_mode == "FDD":
        row = tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=prach_conf_idx)
    elif nr_freq_range == "FR1" and nr_duplex_mode == "TDD":
        row = tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=prach_conf_idx)
    elif nr_freq_range == "FR2" and nr_duplex_mode == "TDD":
        row = tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=prach_conf_idx)
    else:
        raise ValueError("The combination of {0} and {1} is not supported!".format(nr_freq_range, nr_duplex_mode))  # Not reached by tests. Only targets code errors.
    # Compute RACH occasion duration
    if prach_preamble_format in ['0', '1', '2', '3']:
        # The duration of this is not fully defined!
        # Assume PRACH occupying resources until the end of the last subframe.
        # 8: compute t_dur^RA in seconds
        t_dur_ra_s = math.ceil((prach_cyclic_prefix_duration_s + prach_zc_sequences_duration_s) / (1000 * 1e-6)) * (NR_RADIO_FRAME_DURATION_MS / (1000 * N_SUBFRAMES_PER_FRAME))
    else:
        # 6: Single Rach occasion duration as multiple of PRACH symbols
        n_dur_ra = row['PRACH duration'][0]
        # 7
        t_ra_symb_s = NR_RADIO_FRAME_DURATION_MS / (
            float(tables.ts_38_211_table_4_3_2_1(mu=mu_msg1_numerology, col="N symbols per slot")) * float(tables.ts_38_211_table_4_3_2_1(mu=mu_msg1_numerology, col="N slots per frame")) * 1000
        )
        # 8: compute t_dur^RA in seconds
        t_dur_ra_s = n_dur_ra * t_ra_symb_s  # Single RACH occasion duration in s

    short_gt_s = t_dur_ra_s - prach_occupied_resource_duration_single_s

    pusch_ofdm_symbols_occupied_by_rach_occasions = compute_pusch_ofdm_symbols_occupied_by_rach_occasions(nr_freq_range=nr_freq_range, nr_duplex_mode=nr_duplex_mode, prach_conf_idx=prach_conf_idx, delta_f_ra_hz=delta_f_ra_hz, delta_f_hz=delta_f_hz)
    eff_int_bool = math.isclose(
        pusch_ofdm_symbols_occupied_by_rach_occasions,
        round(pusch_ofdm_symbols_occupied_by_rach_occasions),
        rel_tol=1e-9,
        abs_tol=1e-12
    )

    long_gt_s = None
    if eff_int_bool is not True:
        mu_pusch_numerology = SCS_HZ_TO_NUMEROLOGY[delta_f_hz]
        pusch_ofdm_symbol_duration_s = NR_RADIO_FRAME_DURATION_MS / (
            float(tables.ts_38_211_table_4_3_2_1(mu=mu_pusch_numerology, col="N symbols per slot")) * float(tables.ts_38_211_table_4_3_2_1(mu=mu_pusch_numerology, col="N slots per frame")) * 1000
        )
        long_gt_s = short_gt_s + math.modf(pusch_ofdm_symbols_occupied_by_rach_occasions)[0] * pusch_ofdm_symbol_duration_s

    prach_guard_times_dict = {
        "Short GT in s": short_gt_s,
        "Long GT in s": long_gt_s
    }
    return prach_guard_times_dict


def compute_prach_preamble_format(nr_freq_range: str, nr_duplex_mode: str, prach_conf_idx: int):
    """Compute the PRACH Preamble Format.
    This uses 3GPP TS 38.211 Table 6.3.3.2-2 to 6.3.3.2-4.

    Parameters
    ----------
    nr_freq_range: str
        The frequency range, either FR1 or FR2.

    nr_duplex_mode: str
        The duplex mode, either FDD or TDD.

    prach_conf_idx : int
        The PRACH Configuration Index.

    Returns
    -------
    prach_preamble_format : str
        The PRACH Preamble Format.

    Raises
    ------
    TypeError
        If nr_freq_range is not of type str.

    TypeError
        If nr_duplex_mode is not of type str.

    TypeError
        if prach_conf_idx is not of type int.

    ValueError
        If nr_freq_range is not FR1 or FR2.

    ValueError
        If nr_duplex_mode is not FDD or TDD.

    ValueError
        If prach_conf_idx is not in [0, ..., 262].

    ValueError
        If the combination of nr_freq_range and nr_duplex_mode is not supported.

    """
    if not isinstance(nr_freq_range, str):
        raise TypeError("nr_freq_range should be of type str, but is {0}!".format(type(nr_freq_range)))
    if not isinstance(nr_duplex_mode, str):
        raise TypeError("nr_duplex_mode should be of type str, but is {0}!".format(type(nr_duplex_mode)))
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))
    if nr_freq_range not in ["FR1", "FR2"]:
        raise ValueError("An nr_freq_range of {0} is not supported!".format(nr_freq_range))
    if nr_duplex_mode not in ["TDD", "FDD"]:
        raise ValueError("An nr_duplex_mode of {0} is not supported!".format(nr_duplex_mode))
    if not 0 <= prach_conf_idx <= 262:
        raise ValueError("A PRACH Configuration Index of {0} is not supported! The permitted range is 0, ..., 262.".format(prach_conf_idx))

    if nr_freq_range == "FR1" and nr_duplex_mode == "FDD":
        prach_preamble_format = str(tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=prach_conf_idx)['Preamble format'][0])
    elif nr_freq_range == "FR1" and nr_duplex_mode == "TDD":
        prach_preamble_format = str(tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=prach_conf_idx)['Preamble format'][0])
    elif nr_freq_range == "FR2" and nr_duplex_mode == "TDD":
        prach_preamble_format = str(tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=prach_conf_idx)['Preamble format'][0])
    else:
        raise ValueError("The combination of {0} and {1} is not supported!".format(nr_freq_range, nr_duplex_mode))

    return prach_preamble_format


def compute_maximum_gnb_cell_radius(prach_preamble_format: str, l_ra: int, delta_f_ra_hz: int, restricted_set_str: str, cyclic_prefix_extended_bool: bool, channel_bw_hz: int, freq_range: str):
    """Compute the maximum gNB cell radius.
    This is experimental only, since the computational methods do not deliver proper results.

    :Sources:
        The computation below follows Section C.2 ("Cell Dimensioning) and Table 2 of
        A. Chakrapani, "On the Design Details of SS/PBCH, Signal Generation and PRACH in 5G-NR,"
        in IEEE Access, vol. 8, pp. 136617-136637, 2020, doi: 10.1109/ACCESS.2020.3010500

    ``r_cell <= ( N_CS / (Δf_RA * L_RA) - τ_d,PUSCH / 2^µ ) * c_0 / 2``

    Additionally, the cell radius formula given by https://5g.smarttelecomedu.com/prach-preamble-generation/
    is adapted:

    ``r_cell <= ( N_CS / (Δf_RA * L_RA) - τ_d,PUSCH ) * c_0 / 2``

    Lower bound for the cyclic shift N_CS in LTE according to S. Sesia, I. Toufik, M. Baker,
    "LTE The UMTS Long Term Evolution: From Theory to Practice":

    ``N_CS >= ceil( (20 / 3 * r_cell - τ_ds) * N_ZC / T_SEQ ) + n_g``

    where:

    * r_cell: cell size in km
    * τ_ds: maximum delay spread
    * N_ZC: PRACH sequence length (Zadoff-Chu-Sequence, here: 839)
    * T_SEQ: PRACH sequence duration in µs
    * n_g: number of additional guard samples due to the receiver pulse shaping filter

    .. note::
        The idea behind this seems to be, that multiple consecutive shifted ZC-sequences will behave as if those sequences are free to be interpreted as guard time.

    Parameters
    ----------
    prach_preamble_format : str
        The PRACH Preamble Format.

    l_ra : int
        The number of subcarriers in a PRACH preamble.
        Supported are 139, 839, 571, 1151.

    delta_f_ra_hz : int
        The subcarrier spacing for the PRACH sequences; Δf_RA.
        Supported are 1.25, 5, 15, 30, 60, 120, 480, and 960 kHz.
        The OAI5G config sets this in msg1_SubcarrierSpacing.

    restricted_set_str : str
        The restricted set type for long PRACH sequence formats 0 ... 3.
        Options: 'A', 'B', or '' (unrestricted sets or short PRACH sequence formats).

    cyclic_prefix_extended_bool : bool
        True, if the cyclic prefix has extended length.

    channel_bw_hz : int
        The channel bandwidth in Hz.

    freq_range : str
        The frequency range, either FR1 or FR2.

    Returns
    -------
    gnb_cell_radius_m
        The maximum gNB cell radius in meters.

    Raises
    ------
    TypeError
        prach_preamble_format is not of type str.

    TypeError
        If l_ra is not of type int.

    TypeError
        If delta_f_ra_hz is not of type int.

    TypeError
        If restricted_set_str is not of type str.

    TypeError
        If cyclic_prefix_extended_bool is not of type bool.

    TypeError
        If channel_bw_hz is not of type int.

    TypeError
        If freq_range is not of type str.

    ValueError
        If prach_preamble_format is not in ["0", "1", "2", "3", "A1", "A2", "A3", "B1", "B4", "C0", "C2", "A1/B1", "A2/B2", "A3/B3"].

    ValueError
        If l_ra is not 139, 839, 571, or 1151.

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA.

    ValueError
        If restricted_set_str is not 'A', 'B', or ''.

    ValueError
        If the combination of l_ra and delta_f_ra_hz is not supported.

    ValueError
        If freq_range is not "FR1" or "FR2".

    ValueError
        If delta_f_ra_hz is not a supported PRACH subcarrier spacing Δf_RA for the given frequency range.

    ValueError
        If channel_bw_hz is not a valid 5G NR FR1 or FR2 Channel Bandwidth.

    """
    if not isinstance(prach_preamble_format, str):
        raise TypeError("prach_preamble_format should be of type str, but is {0}!".format(type(prach_preamble_format)))
    if not isinstance(l_ra, int):
        raise TypeError("l_ra should be of type int, but is {0}!".format(type(l_ra)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))
    if not isinstance(restricted_set_str, str):
        raise TypeError("restricted_set_str should be of type str, but is {0}!".format(type(restricted_set_str)))
    if not isinstance(cyclic_prefix_extended_bool, bool):
        raise TypeError("cyclic_prefix_extended_bool should be of type bool, but is {0}!".format(type(cyclic_prefix_extended_bool)))
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))
    if not isinstance(freq_range, str):
        raise TypeError("freq_range should be of type str, but is {0}!".format(type(freq_range)))

    if prach_preamble_format not in PRACH_PREAMBLE_FORMATS:
        raise ValueError("A prach_preamble_format of {0} is not supported!".format(prach_preamble_format))
    if l_ra not in [139, 839, 571, 1151]:
        raise ValueError("An l_ra of {0} is not supported!".format(l_ra))
    if delta_f_ra_hz not in DELTA_F_RA_HZ:
        raise ValueError("A value for delta_f_ra_hz of {0} Hz is not supported!".format(delta_f_ra_hz))
    if restricted_set_str not in ['A', 'B', '']:
        raise ValueError("An restricted_set_str of {0} is not supported!".format(restricted_set_str))
    if freq_range not in ["FR1", "FR2"]:
        raise ValueError("An freq_range of {0} is not supported!".format(freq_range))
    if delta_f_ra_hz not in freq_range_delta_f_ra_dict[freq_range]:
        raise ValueError("A combination of delta_f_ra_hz {0} Hz and frequency range {1} is not supported!".format(delta_f_ra_hz, freq_range))
    if freq_range == "FR1":
        if not int(channel_bw_hz / 1000000) in tables.NR_FR1_CHANNEL_BW_MHZ_LIST:
            raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR1!".format(round(channel_bw_hz / 1000000)))
    else:
        if not int(channel_bw_hz / 1000000) in tables.NR_FR2_CHANNEL_BW_MHZ_LIST:
            raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(round(channel_bw_hz / 1000000)))

    if delta_f_ra_hz in [1250, 5000]:
        mu_ra = 0
    else:
        mu_ra = SCS_HZ_TO_NUMEROLOGY[delta_f_ra_hz]
    logger.info("PRACH Preamble Format: {0}".format(prach_preamble_format))

    # Determine N_CP^RA (PRACH Sequence Cyclic Prefix duration in samples)
    n_cp_ra = compute_prach_cyclic_prefix_duration(prach_preamble_format=prach_preamble_format)

    # Determine the maximum Radio Channel Delay Spread, which equals the PRACH Cyclic Prefix Size
    # NOTE: This seems to be incorrect. Instead, tau_d + RTD_max = CP_RACH
    # The tau_d should be defined using the PUSCH cyclic prefix as an upper bound.
    # The difference between CP_PUSCH and CP_PRACH will then be assigned to the RTD_max.
    tau_d_prach = T_C_S * KAPPA * n_cp_ra
    logger.info("Delay spread equal to PRACH CP size: tau_d = {0} µs".format(tau_d_prach * 1000000))
    logger.info("Delay spread equal to PRACH CP size: tau_d = {0} FFT samples".format(n_cp_ra))
    logger.info("Delay spread equal to PRACH CP size: tau_d = {0} T_C".format(tau_d_prach / T_C_S))

    # Compute N'_CS (Upper bound on N_CS)
    if prach_preamble_format in ['0', '1', '2']:
        n_prime_cs = l_ra * n_cp_ra / 24_576
    elif prach_preamble_format == '3':
        n_prime_cs = l_ra * n_cp_ra / 6_144
    else:
        n_prime_cs = l_ra * n_cp_ra / 2_048

    logger.info("N'_CS: {0} (Upper bound on N_CS)".format(n_prime_cs))

    # Compute the quantized value of N_CS based on N'_CS
    n_cs = 0
    if delta_f_ra_hz == 1250:
        if restricted_set_str == 'A':
            for zero_correlation_zone_config in range(0, 16):
                n_cs_candidate = tables.ts_38_211_table_6_3_3_1_5(zero_correlation_zone_config=zero_correlation_zone_config)["N_CS value for Restricted set type A"][0]
                # Table entry is NaN
                if pd.isna(n_cs_candidate):
                    break  # not testable yet
                # First loop step: Lowest entry is already larger than N'_CS (upper bound on N_CS) --> n_cs = 0, break
                # Other loop steps: Current entry is larger than N'_CS (upper bound on N_CS) --> n_cs = previous N_CS candidate, break
                # Last loop step: Current entry is still lower than N'_CS (upper bound on N_CS) --> n_cs = current N_CS candidate (column max.), loop ends
                elif n_cs_candidate > n_prime_cs:
                    break
                else:
                    n_cs = n_cs_candidate
        elif restricted_set_str == 'B':
            for zero_correlation_zone_config in range(0, 16):
                n_cs_candidate = tables.ts_38_211_table_6_3_3_1_5(zero_correlation_zone_config=zero_correlation_zone_config)["N_CS value for Restricted set type B"][0]
                # Table entry is NaN
                if pd.isna(n_cs_candidate):
                    break  # not testable yet
                # First loop step: Lowest entry is already larger than N'_CS (upper bound on N_CS) --> n_cs = 0, break
                # Other loop steps: Current entry is larger than N'_CS (upper bound on N_CS) --> n_cs = previous N_CS candidate, break
                # Last loop step: Current entry is still lower than N'_CS (upper bound on N_CS) --> n_cs = current N_CS candidate (column max.), loop ends
                elif n_cs_candidate > n_prime_cs:
                    break
                else:
                    n_cs = n_cs_candidate
        else:
            for zero_correlation_zone_config in range(0, 16):
                n_cs_candidate = tables.ts_38_211_table_6_3_3_1_5(zero_correlation_zone_config=zero_correlation_zone_config)["N_CS value for Unrestricted set"][0]
                # First loop step: Lowest entry is already larger than N'_CS (upper bound on N_CS) --> n_cs = 0, break
                # Other loop steps: Current entry is larger than N'_CS (upper bound on N_CS) --> n_cs = previous N_CS candidate, break
                # Last loop step: Current entry is still lower than N'_CS (upper bound on N_CS) --> n_cs = current N_CS candidate (column max.), loop ends
                if n_cs_candidate > n_prime_cs:
                    break
                else:
                    n_cs = n_cs_candidate
    elif delta_f_ra_hz == 5000:
        if restricted_set_str == 'A':
            for zero_correlation_zone_config in range(0, 16):
                n_cs_candidate = tables.ts_38_211_table_6_3_3_1_6(zero_correlation_zone_config=zero_correlation_zone_config)["N_CS value for Restricted set type A"][0]
                # First loop step: Lowest entry is already larger than N'_CS (upper bound on N_CS) --> n_cs = 0, break
                # Other loop steps: Current entry is larger than N'_CS (upper bound on N_CS) --> n_cs = previous N_CS candidate, break
                # Last loop step: Current entry is still lower than N'_CS (upper bound on N_CS) --> n_cs = current N_CS candidate (column max.), loop ends
                if n_cs_candidate > n_prime_cs:
                    break  # not testable yet
                else:
                    n_cs = n_cs_candidate
        elif restricted_set_str == 'B':
            for zero_correlation_zone_config in range(0, 16):
                n_cs_candidate = tables.ts_38_211_table_6_3_3_1_6(zero_correlation_zone_config=zero_correlation_zone_config)["N_CS value for Restricted set type B"][0]
                # Table entry is NaN
                if pd.isna(n_cs_candidate):
                    break
                # First loop step: Lowest entry is already larger than N'_CS (upper bound on N_CS) --> n_cs = 0, break
                # Other loop steps: Current entry is larger than N'_CS (upper bound on N_CS) --> n_cs = previous N_CS candidate, break
                # Last loop step: Current entry is still lower than N'_CS (upper bound on N_CS) --> n_cs = current N_CS candidate (column max.), loop ends
                elif n_cs_candidate > n_prime_cs:
                    break  # not testable yet
                else:
                    n_cs = n_cs_candidate
        else:
            for zero_correlation_zone_config in range(0, 16):
                n_cs_candidate = tables.ts_38_211_table_6_3_3_1_6(zero_correlation_zone_config=zero_correlation_zone_config)["N_CS value for Unrestricted set"][0]
                # First loop step: Lowest entry is already larger than N'_CS (upper bound on N_CS) --> n_cs = 0, break
                # Other loop steps: Current entry is larger than N'_CS (upper bound on N_CS) --> n_cs = previous N_CS candidate, break
                # Last loop step: Current entry is still lower than N'_CS (upper bound on N_CS) --> n_cs = current N_CS candidate (column max.), loop ends
                if n_cs_candidate > n_prime_cs:
                    break  # not testable yet
                else:
                    n_cs = n_cs_candidate
    else:
        if l_ra == 139:
            for zero_correlation_zone_config in range(0, 16):
                n_cs_candidate = tables.ts_38_211_table_6_3_3_1_7(zero_correlation_zone_config=zero_correlation_zone_config)["N_CS value for L_RA=139"][0]
                # First loop step: Lowest entry is already larger than N'_CS (upper bound on N_CS) --> n_cs = 0, break
                # Other loop steps: Current entry is larger than N'_CS (upper bound on N_CS) --> n_cs = previous N_CS candidate, break
                # Last loop step: Current entry is still lower than N'_CS (upper bound on N_CS) --> n_cs = current N_CS candidate (column max.), loop ends
                if n_cs_candidate > n_prime_cs:
                    break
                else:
                    n_cs = n_cs_candidate
        elif l_ra == 571:
            for zero_correlation_zone_config in range(0, 16):
                n_cs_candidate = tables.ts_38_211_table_6_3_3_1_7(zero_correlation_zone_config=zero_correlation_zone_config)["N_CS value for L_RA=571"][0]
                # First loop step: Lowest entry is already larger than N'_CS (upper bound on N_CS) --> n_cs = 0, break
                # Other loop steps: Current entry is larger than N'_CS (upper bound on N_CS) --> n_cs = previous N_CS candidate, break
                # Last loop step: Current entry is still lower than N'_CS (upper bound on N_CS) --> n_cs = current N_CS candidate (column max.), loop ends
                if n_cs_candidate > n_prime_cs:
                    break
                else:
                    n_cs = n_cs_candidate
        elif l_ra == 1151:
            for zero_correlation_zone_config in range(0, 16):
                n_cs_candidate = tables.ts_38_211_table_6_3_3_1_7(zero_correlation_zone_config=zero_correlation_zone_config)["N_CS value for L_RA=1151"][0]
                # First loop step: Lowest entry is already larger than N'_CS (upper bound on N_CS) --> n_cs = 0, break
                # Other loop steps: Current entry is larger than N'_CS (upper bound on N_CS) --> n_cs = previous N_CS candidate, break
                # Last loop step: Current entry is still lower than N'_CS (upper bound on N_CS) --> n_cs = current N_CS candidate (column max.), loop ends
                if n_cs_candidate > n_prime_cs:
                    break
                else:
                    n_cs = n_cs_candidate
        else:
            raise ValueError("The combination of L_RA = {0} and Δf_RA = {1} Hz is invalid!".format(l_ra, delta_f_ra_hz))  # not tested yet

    logger.info("N_CS: {0}".format(n_cs))

    # Compute required number of cyclic shifts
    c_v = math.floor(l_ra / n_cs)
    logger.info("C_v: {0} (Number of cyclic shifts)".format(c_v))

    # Compute required number of root sequences to generate 64 preambles
    # TODO: Determine if this is always 64, or if it is tied to the config parameter "number of contention-based preambles"
    n_root_seq_req = math.ceil(64 / c_v)
    logger.info("N_root-seq,req: {0} (Number of root sequences)".format(n_root_seq_req))

    # Determine the maximum Radio Channel Delay Spread, which equals the PUSCH Cyclic Prefix Size
    # Assume the same numerology as PRACH
    n_cp_l_mu = compute_pusch_cyclic_prefix_duration(mu=mu_ra, cyclic_prefix_extended_bool=cyclic_prefix_extended_bool, longer_symbol_duration_bool=False, channel_bw_hz=channel_bw_hz, freq_range=freq_range)
    tau_d_pusch = T_C_S * KAPPA * n_cp_l_mu
    logger.info("Delay spread equal to PUSCH CP size: tau_d = {0} µs".format(tau_d_pusch * 1_000_000))
    logger.info("Delay spread equal to PUSCH CP size: tau_d = {0} FFT samples".format(n_cp_l_mu))
    logger.info("Delay spread equal to PUSCH CP size: tau_d = {0} T_c".format(tau_d_pusch / T_C_S))

    # Compute the maximum gNB cell readius in meters
    gnb_cell_radius_m = (n_cs / (delta_f_ra_hz * l_ra) - tau_d_pusch) * C_M_PER_S / 2

    return gnb_cell_radius_m


def compute_prach_zc_sequences_duration(prach_preamble_format: str):
    """Compute the duration of (repeated) Zadoff-Chu sequences in FFT samples for the Physical Random Access Channel (PRACH), N_u.
    This is based on 3GPP TS 38.211 ch. 5.3.2, as well as TS 38.211 Tables 6.3.3.1-1 and 6.3.3.1-2.

    Parameters
    ----------
    prach_preamble_format : str
        The PRACH Preamble Format.

    Returns
    -------
    float
        The ZC sequence duration in FFT samples, N_u

    Raises
    ------
    TypeError
        prach_preamble_format is not of type str.
    ValueError
        If prach_preamble_format is not in ["0", "1", "2", "3", "A1", "A2", "A3", "B1", "B2", "B3", "B4", "C0", "C2", "A1/B1", "A2/B2", "A3/B3"].

    """
    if not isinstance(prach_preamble_format, str):
        raise TypeError("prach_preamble_format should be of type str, but is {0}!".format(type(prach_preamble_format)))

    if prach_preamble_format not in PRACH_PREAMBLE_FORMATS:
        raise ValueError("A prach_preamble_format of {0} is not supported!".format(prach_preamble_format))

    # Determine N_u
    if prach_preamble_format in ['0', '1', '2', '3']:
        # Ex.: "1 x 24576 x kappa", n_seq = 24576 (Factor 1 was added in the dictionary)
        # Ex.: "4 x 24576 x kappa", n_reps = 4, n_seq = 24576
        return int(
            tables.ts_38_211_table_6_3_3_1_1(prach_preamble_format=prach_preamble_format)['N_u'][0][0]
        ) * int(
            tables.ts_38_211_table_6_3_3_1_1(prach_preamble_format=prach_preamble_format)['N_u'][0][1]
        )
    else:
        # Ex.: "1 x 2048 x kappa x 2^-mu", n_seq = 2048 (Factor 1 was added in the dictionary)
        # Ex.: "4 x 2048 x kappa x 2^-mu", n_reps = 4, n_seq = 2048
        return int(
            tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)['N_u'][0][0]
        ) * int(
            tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)['N_u'][0][1]
        )


def compute_prach_cyclic_prefix_duration(prach_preamble_format: str):
    """Compute the cyclic prefix duration in FFT samples for the Physical Random Access Channel (PRACH), N_CP^RA.
    This is based on 3GPP TS 38.211 ch. 5.3.2, as well as TS 38.211 Tables 6.3.3.1-1 and 6.3.3.1-2
    This exists to offset some surplus OFDM symbols left after splitting a single OFDM symbol duration into cyclic prefixes for all symbols in a slot.

    Parameters
    ----------
    prach_preamble_format : str
        The PRACH Preamble Format.

    Returns
    -------
    float
        The cyclic prefix duration in FFT samples, N_CP^RA.

    Raises
    ------
    TypeError
        prach_preamble_format is not of type str.
    ValueError
        If prach_preamble_format is not in ["0", "1", "2", "3", "A1", "A2", "A3", "B1", "B2", "B3", "B4", "C0", "C2", "A1/B1", "A2/B2", "A3/B3"].

    """
    if not isinstance(prach_preamble_format, str):
        raise TypeError("prach_preamble_format should be of type str, but is {0}!".format(type(prach_preamble_format)))

    if prach_preamble_format not in PRACH_PREAMBLE_FORMATS:
        raise ValueError("A prach_preamble_format of {0} is not supported!".format(prach_preamble_format))

    # Determine N_CP^RA
    if prach_preamble_format in ['0', '1', '2', '3']:
        # Ex.: "3168 x kappa"
        return tables.ts_38_211_table_6_3_3_1_1(prach_preamble_format=prach_preamble_format)['N_CP^RA'][0][0]
    else:
        # Ex.: "288 x kappa x 2^-mu"
        return tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format=prach_preamble_format)["N_CP^RA"][0][0]


def compute_pusch_cyclic_prefix_duration(mu: int, cyclic_prefix_extended_bool: bool, longer_symbol_duration_bool: bool, channel_bw_hz: int, freq_range: str):
    """Compute the OFDM symbol cyclic prefix duration in FFT samples for the Physical Uplink Shared Channel (PUSCH), N_CP,l^mu.
    This is based on 3GPP TS 38.211 ch. 5.3.1, and takes into account 3GPP TS 38.104 Tables B.5.2-1 to B.5.2-4 and Tables C.5.2-1 to C.5.2-3.
    The numerology, channel bandwidth, and frequency range are taken into account.
    The longer symbol duration occurs for a predefined set of cyclic prefixes every 0.5 µs.
    This exists to offset some surplus OFDM symbols left after splitting a single OFDM symbol duration into cyclic prefixes for all symbols in a slot.

    According to 3GPP TS 38.211 ch. 5.3.1, the extended cyclic prefix does not occur together with a longer cyclic prefix every 0.5 ms!

    .. note::
        All the calculations in this function should actually be used for PRACH, not PUSCH!

    Correction: ch. 5.3.1 targets all channels except PRACH and RIM-RS

    | Numerology | SCS     | Symbols with longer duration |
    | ---------- | ------- | ---------------------------- |
    |          0 |  15 kHz |         [0, 7] for each slot |
    |          1 |  30 kHz |            [0] for each slot |
    |          2 |  60 kHz |            [0] for slots n*2 |
    |          3 | 120 kHz |            [0] for slots n*4 |
    |          4 | 240 kHz |            [0] for slots n*4 |
    |          5 | 480 kHz |            [0] for slots n*4 |
    |          6 | 960 kHz |            [0] for slots n*4 |

    :Example:
        * Parameters
            * Numerology: 0 (15 kHz SCS)
            * Channel bandwidth: 20 MHz
            * Frequency range: FR1
            * Longer symbol duration: False
        * Resulting
            * 14 OFDM symbols per slot
            * FFT size: 1024 samples
            * Cyclic prefix length for symbols 1-6 and 8-13: 144 FFT samples
            * Cyclic prefix length for symbols 0 and 7 (longer symbol duration = True)
        * Check for normal cyclic prefix with 14 OFDM symbols per slot:
            * The OFDM symbols with number 0 or (7 * 2^µ) in a slot have a cyclic prefix duration of 144 * 2^-µ + 16 FFT samples.
            * All other OFDM symbols have a cyclic prefix duration of 144 * 2^-µ FFT samples.

    For extended cyclic prefix with 12 OFDM symbols per slot:
    * All OFDM symbols have a cyclic prefix duration of 512 * 2^-µ FFT samples.

    Parameters
    ----------
    mu : int
        The numerology µ.

    cyclic_prefix_extended_bool : bool
        If True, the extended cyclic prefix is being computed.

    longer_symbol_duration : bool
        If True, the longer symbol duration is used for the normal cyclic prefix.
        This applies to symbol numbers 0 and 7 * 2^µ in a slot.

    channel_bw_hz : int
        The channel bandwidth in Hz.

    freq_range : str
        The frequency range, either FR1 or FR2.

    Returns
    -------
    n_cp_l_mu : float
        The cyclic prefix duration in FFT samples.

    Raises
    ------
    TypeError
        If mu is not of type int.

    TypeError
        If cyclic_prefix_extended_bool is not of type bool.

    TypeError
        If longer_symbol_duration_bool is not of type bool.

    TypeError
        If channel_bw_hz is not of type int.

    TypeError
        If freq_range is not of type str.

    ValueError
        If mu is not in  [0, 1, 2, 3, 4, 5, 6].

    ValueError
        If channel_bw_hz is not a valid 5G NR FR1 or FR2 Channel Bandwidth.

    ValueError
        If freq_range is not "FR1" or "FR2".

    """
    if not isinstance(mu, int):
        raise TypeError("mu should be of type int, but is {0}!".format(type(mu)))
    if not isinstance(cyclic_prefix_extended_bool, bool):
        raise TypeError("cyclic_prefix_extended_bool should be of type bool, but is {0}!".format(type(cyclic_prefix_extended_bool)))
    if not isinstance(longer_symbol_duration_bool, bool):
        raise TypeError("longer_symbol_duration_bool should be of type bool, but is {0}!".format(type(longer_symbol_duration_bool)))
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))
    if not isinstance(freq_range, str):
        raise TypeError("freq_range should be of type str, but is {0}!".format(type(freq_range)))

    if mu not in tables.NUMEROLOGY_RANGE_LIST:
        raise ValueError("Unknown numerology {0}!".format(mu))
    if freq_range not in ["FR1", "FR2"]:
        raise ValueError("An freq_range of {0} is not supported!".format(freq_range))
    if freq_range == "FR1":
        if not int(channel_bw_hz / 1000000) in tables.NR_FR1_CHANNEL_BW_MHZ_LIST:
            raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR1!".format(round(channel_bw_hz / 1000000)))
    else:
        if not int(channel_bw_hz / 1000000) in tables.NR_FR2_CHANNEL_BW_MHZ_LIST:
            raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(round(channel_bw_hz / 1000000)))

    # 3GPP TS 38.211 ch. 5.3.1
    if cyclic_prefix_extended_bool is True and longer_symbol_duration_bool is True:
        raise ValueError("cyclic_prefix_extended_bool and longer_symbol_duration_bool cannot both be true!")

    scs_hz = int(tables.ts_38_300_table_5_1_1(mu=mu, col="Delta f in kHz") * 1000)
    n_slots_per_frame = tables.ts_38_211_table_4_3_2_1(mu=mu, col="N slots per frame")
    # slot_duration_ms = NR_RADIO_FRAME_DURATION_MS / n_slots_per_frame
    n_add_cyclic_prefixes_per_slot = 10 / (n_slots_per_frame * 0.5)

    row_dict = get_table_row_from_channel_bw(channel_bw_hz=channel_bw_hz, freq_range=freq_range, scs_hz=scs_hz, cyclic_prefix_extended_bool=cyclic_prefix_extended_bool)
    ofdm_symbol_fft_size_samples = row_dict['FFT size'][0]
    cp_length_samples = next(
        value
        for key, value in row_dict.items()
        if "CP length" in key
    )[0]

    add_fft_size = 0

    # 3GPP TS 38.211 ch. 5.3.1
    if longer_symbol_duration_bool is True:
        # the additional cyclic prefix duration occurs every 0.5 ms. For mu = 0, this is 2 times per slot; for mu = 1, this is 1 time per slot, and so on.
        # in total, there will always be 20 cyclic prefixes with additional duration in a single frame.
        add_fft_size = n_slots_per_frame * (15 * ofdm_symbol_fft_size_samples - N_SYMB_PER_SLOT * (ofdm_symbol_fft_size_samples + cp_length_samples)) / 20
    n_cp_l_mu = cp_length_samples + add_fft_size

    logger.debug("Slot duration: {0} samples".format((ofdm_symbol_fft_size_samples + cp_length_samples) * 14 + add_fft_size * n_add_cyclic_prefixes_per_slot))
    logger.debug("Slot duration control: {0} samples".format(15 * ofdm_symbol_fft_size_samples))
    return n_cp_l_mu


def get_duplex_mode_from_freq_band(freq_band: int):
    """Get the duplex mode from the NR frequency band.
    This utilizes TS 38.101-1 Table 5.2-1 and TS 38.101-2 Table 5.2-1.
    The split between these tables is expected to happen after n256.

    Parameters
    ----------
    freq_band : int
        The 5G NR frequency band.

    Returns
    -------
    str
        The duplex mode.
        Currently supports FDD, TDD; SDL, and SUL.

    Raises
    ------
    TypeError
        If freq_band is not of type int.

    ValueError
        If freq_band is not a valid 5G NR frequency band.

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if 0 < freq_band <= 256:
        return tables.ts_38_101_1_table_5_2_1(freq_band=freq_band, col="Duplex Mode")
    elif 257 <= freq_band <= 512:
        return tables.ts_38_101_2_table_5_2_1(freq_band=freq_band, col="Duplex Mode")
    else:
        raise ValueError("n{0} is not a valid Frequency Band!".format(freq_band))


def get_freq_range_from_center_freq(nr_channel_center_freq_hz: int):
    """Get the frequency range from the channel center frequency.
    This follows a shortened version of TS 38.101-1 Table 5.1-1 and currently only returns FR1 or FR2.

    Parameters
    ----------
    nr_channel_center_freq_hz : int
        The channel center frequency.

    Returns
    -------
    str
        The frequency range, either FR1 or FR2.

    Raises
    ------
    TypeError
        If nr_channel_center_freq_hz is not of type int.

    ValueError
        If nr_channel_center_freq_hz is not a valid 5G NR FR1 or FR2 channel center frequency.

    """
    if not isinstance(nr_channel_center_freq_hz, int):
        raise TypeError("nr_channel_center_freq_hz should be of type int, but is {0}!".format(type(nr_channel_center_freq_hz)))

    for freq_range in [tables.FREQ_RANGE_LIST[0], tables.FREQ_RANGE_LIST[1]]:
        range_tuple = tables.ts_38_101_1_table_5_1_1(freq_range=freq_range)
        if nr_channel_center_freq_hz in range(range_tuple[0], range_tuple[1] + 1):
            return freq_range
        else:
            raise ValueError("{0} MHz is not a valid NR channel center frequency!".format(nr_channel_center_freq_hz / 1_000_000))


def get_table_row_from_channel_bw(channel_bw_hz: int, freq_range: str, scs_hz: int, cyclic_prefix_extended_bool: bool):
    """Get the table row based on the Channel Bandwidth.
    This refers to 3GPP TS 38.104 Tables B.5.2-1 to B.5.2-4 and Tables C.5.2-1 to C.5.2-3.

    :Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size: row_series['FFT size'].item()
        * 2 : CP length (various column headers): row_series.iloc[:, 2].item()
        * 3  :EVM window length W: row_series['EVM window length W'].item()
        * 4 : Ratio of W to total CP length (Note) (%) (various column headers): row_series.iloc[:, 4].item()

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    scs_hz : int
        The subcarrier spacing in Hz.

    freq_range : str
        The frequency range, either FR1 or FR2.

    cyclic_prefix_extended_bool : bool
        True, if the cyclic prefix has extended length.

    Returns
    -------
    row_dict : dict
        The table row.
        Empty, if no valid parameter combination is used.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.

    TypeError
        If freq_range is not of type str.

    TypeError
        If scs_hz is not of type int.

    TypeError
        If cyclic_prefix_extended_bool is not of type bool.

    ValueError
        If channel_bw_hz is not a valid 5G NR FR1 or FR2 Channel Bandwidth.

    ValueError
        If freq_range is not "FR1" or "FR2".

    ValueError
        If scs_hz is not in [1250, 5000, 15000, 30000, 60000, 120000, 480000, 960000].

    ValueError
        If the table does not contain the given channel bandwidth.

    ValueError
        If the combination of freq_range and scs_hz is not valid.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))
    if not isinstance(freq_range, str):
        raise TypeError("freq_range should be of type str, but is {0}!".format(type(freq_range)))
    if not isinstance(scs_hz, int):
        raise TypeError("scs_hz should be of type int, but is {0}!".format(type(scs_hz)))
    if not isinstance(cyclic_prefix_extended_bool, bool):
        raise TypeError("cyclic_prefix_extended_bool should be of type bool, but is {0}!".format(type(cyclic_prefix_extended_bool)))

    if freq_range not in ["FR1", "FR2"]:
        raise ValueError("An freq_range of {0} is not supported!".format(freq_range))

    channel_bw_mhz = int(channel_bw_hz / 1_000_000)

    if freq_range == "FR1":
        if channel_bw_mhz not in tables.NR_FR1_CHANNEL_BW_MHZ_LIST:
            raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR1!".format(channel_bw_mhz))
    else:
        if channel_bw_mhz not in tables.NR_FR2_CHANNEL_BW_MHZ_LIST:
            raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(channel_bw_mhz))
    if scs_hz not in [*SCS_HZ_TO_NUMEROLOGY]:
        raise ValueError("An scs_hz of {0} is not supported!".format(scs_hz))

    row_dict = dict()

    if freq_range == "FR1":
        if cyclic_prefix_extended_bool is False:
            if scs_hz == 15_000:
                row_dict = tables.ts_38_104_table_b_5_2_1(channel_bw_hz=channel_bw_hz)
            elif scs_hz == 30_000:
                row_dict = tables.ts_38_104_table_b_5_2_2(channel_bw_hz=channel_bw_hz)
            elif scs_hz == 60_000:
                row_dict = tables.ts_38_104_table_b_5_2_3(channel_bw_hz=channel_bw_hz)
            else:
                raise ValueError("A combination of channel_bw_hz = {0} and scs_hz = {1} is not valid for a normal cyclic prefix!".format(channel_bw_hz, scs_hz))
        else:
            if scs_hz == 60_000:
                row_dict = tables.ts_38_104_table_b_5_2_4(channel_bw_hz=channel_bw_hz)
            else:
                raise ValueError("A combination of channel_bw_hz = {0} and scs_hz = {1} is not valid for an extended cyclic prefix!".format(channel_bw_hz, scs_hz))
    else:
        if cyclic_prefix_extended_bool is False:
            if scs_hz == 60_000:
                row_dict = tables.ts_38_104_table_c_5_2_1(channel_bw_hz=channel_bw_hz)
            elif scs_hz == 120_000:
                row_dict = tables.ts_38_104_table_c_5_2_2(channel_bw_hz=channel_bw_hz)
            elif scs_hz == 480_000:
                row_dict = tables.ts_38_104_table_c_5_2_2a(channel_bw_hz=channel_bw_hz)
            elif scs_hz == 960_000:
                row_dict = tables.ts_38_104_table_c_5_2_2b(channel_bw_hz=channel_bw_hz)
            else:
                raise ValueError("A combination of channel_bw_hz = {0} and scs_hz = {1} is not valid for a normal cyclic prefix!".format(channel_bw_hz, scs_hz))
        else:
            if scs_hz == 60_000:
                row_dict = tables.ts_38_104_table_c_5_2_3(channel_bw_hz=channel_bw_hz)
            else:
                raise ValueError("A combination of channel_bw_hz = {0} and scs_hz = {1} is not valid for an extended cyclic prefix!".format(channel_bw_hz, scs_hz))

    return row_dict


def get_k_from_channel_raster(n_rb: int):
    """Get Resource element index k from the channel raster N_RB according to 3GPP TS 38.104 Table 5.4.2.2-1.

    Parameters
    ----------
    n_rb : int
        The number of Resource Blocks (N_RB).

    Returns
    -------
    k : int
        The resource element index k.

    Raises
    ------
    TypeError
        If n_rb is not of type int.

    ValueError
        If n_rb % 2 is not in [0, 1].

    """
    if isinstance(n_rb, int):
        try:
            k = resource_element_index_k_dict[n_rb % 2]
        except KeyError:
            raise ValueError("N_RB of {0} is unsupported!".format(n_rb))  # Not reached by tests. Only targets code errors.
        return k
    else:
        raise TypeError("n_rb should be of type int, but is {0}!".format(type(n_rb)))


def get_n_prb_from_channel_raster(n_rb: int):
    """Get Physical resource block number n_PRB from the channel raster N_RB according to 3GPP TS 38.104 Table 5.4.2.2-1.

    Parameters
    ----------
    n_rb : int
        The number of Resource Blocks (N_RB).

    Returns
    -------
    n_prb : int
        The Physical Resource Block number (n_PRB).

    Raises
    ------
    TypeError
        If n_rb is not of type int.

    ValueError
        If n_rb % 2 is not in [0, 1] and if n_rb < 0.

    """
    if isinstance(n_rb, int):
        if (n_rb % 2) in [0, 1] and n_rb >= 0:
            n_prb = math.floor(
                n_rb / 2
            )
        else:
            raise ValueError("N_RB of {0} is unsupported!".format(n_rb))
        return n_prb
    else:
        raise TypeError("n_rb should be of type int, but is {0}!".format(type(n_rb)))


def get_delta_f_global_from_frequency(frequency_hz: int):
    """Get ΔF_Global from a frequency according to 3GPP TS 38.104 chapter 5.4.2.1.

    Parameters
    ----------
    frequency_hz : int
        The input frequency in Hz.

    Returns
    -------
    delta_f_global_hz : int
        The resulting ΔF_Global.

    Raises
    ------
    TypeError
        If frequency_hz is not of type int.

    ValueError
        If frequency_hz is outside of range(0, 100000000000)

    """
    if isinstance(frequency_hz, int):
        if frequency_hz >= FREQ_RANGE_LOWER_LIMIT_HZ and frequency_hz < FREQ_RANGE_EDGE_HZ_1:
            delta_f_global_hz = DELTA_F_GLOBAL_HZ_LIST[0]
        elif frequency_hz >= FREQ_RANGE_EDGE_HZ_1 and frequency_hz <= FREQ_RANGE_EDGE_HZ_2:
            delta_f_global_hz = DELTA_F_GLOBAL_HZ_LIST[1]
        elif frequency_hz > FREQ_RANGE_EDGE_HZ_2 and frequency_hz <= FREQ_RANGE_UPPER_LIMIT_HZ:
            delta_f_global_hz = DELTA_F_GLOBAL_HZ_LIST[2]
        else:
            raise ValueError("A frequency of {0} Hz is unsupported!".format(frequency_hz))
        return delta_f_global_hz
    else:
        raise TypeError("frequency_hz should be of type int, but is {0}!".format(type(frequency_hz)))


def get_delta_f_global_from_arfcn(arfcn: int):
    """Get ΔF_Global from an NR-ARFCN according to 3GPP TS 38.104 chapter 5.4.2.1.

    Parameters
    ----------
    arfcn : int
        The input NR-ARFCN.

    Returns
    -------
    delta_f_global_hz : int
        The resulting ΔF_Global.

    Raises
    ------
    TypeError
        If arfcn is not of type int.

    ValueError
        If arfcn is outside of range(0, 3279165)

    """
    if isinstance(arfcn, int):
        if arfcn >= ARFCN_RANGE_LOWER_LIMIT_HZ and arfcn < ARFCN_RANGE_EDGE_HZ_1:
            delta_f_global_hz = DELTA_F_GLOBAL_HZ_LIST[0]
        elif arfcn >= ARFCN_RANGE_EDGE_HZ_1 and arfcn < ARFCN_RANGE_EDGE_HZ_2:
            delta_f_global_hz = DELTA_F_GLOBAL_HZ_LIST[1]
        elif arfcn >= ARFCN_RANGE_EDGE_HZ_2 and arfcn <= ARFCN_RANGE_UPPER_LIMIT_HZ:
            delta_f_global_hz = DELTA_F_GLOBAL_HZ_LIST[2]
        else:
            raise ValueError("An NR-ARFCN of {0} is unsupported!".format(arfcn))
        return delta_f_global_hz
    else:
        raise TypeError("arfcn should be of type int, but is {0}!".format(type(arfcn)))


def convert_frequency_to_arfcn(frequency_hz: int):
    """Convert a frequency to a NR-ARFCN according to 3GPP TS 38.104 chapter 5.4.2.1.

    The computation formula is:
        ``N_REF = (F_REF - F_REF-OFFS) / ΔF_Global + N_REF-Offs``

    Parameters
    ----------
    frequency_hz : int
        The input frequency in Hz.

    Returns
    -------
    arfcn : int
        The resulting NR-ARFCN.

    Raises
    ------
    TypeError
        If frequency_hz is not of type int.

    """
    if isinstance(frequency_hz, int):
        table_row = get_table_row_from_frequency(frequency_hz)
        arfcn = int(
            math.floor(
                (
                    ((frequency_hz - F_REF_OFFS_HZ_LIST[table_row]) / 1000000) / (DELTA_F_GLOBAL_HZ_LIST[table_row] / 1000000)
                ) + (
                    N_REF_OFFS_LIST[table_row]
                )
            )
        )
        return arfcn
    else:
        raise TypeError("frequency_hz should be of type int, but is {0}!".format(type(frequency_hz)))


def convert_arfcn_to_frequency(arfcn: int):
    """Convert a NR-ARFCN to a frequency according to 3GPP TS 38.104 chapter 5.4.2.1.

    The computation formula is:
        ``F_REF = F_REF-OFFS + ΔF_Global * (N_REF - N_REF-Offs)``

    Warning: All frequencies in the formula are expected to be in MHz by the standard!

    Parameters
    ----------
    arfcn : int
        The input NR-ARFCN.

    Returns
    -------
    frequency_hz : int
        The resulting frequency in Hz.

    Raises
    ------
    TypeError
        If arfcn is not of type int.

    """
    if isinstance(arfcn, int):
        table_row = get_table_row_from_arfcn(arfcn)
        frequency_hz = int(
            (F_REF_OFFS_HZ_LIST[table_row] / 1000000 + (DELTA_F_GLOBAL_HZ_LIST[table_row] / 1000000) * (arfcn - N_REF_OFFS_LIST[table_row])) * 1000000
        )
        return frequency_hz
    else:
        raise TypeError("arfcn should be of type int, but is {0}!".format(type(arfcn)))


def find_keys(data, **criteria):
    """Find a sub-dictionary of an input dictionary matching the given criteria.

    Parameters
    ----------
    data : dict | MappingProxyType
        The dictionary to be searched.

    criteria : dict
        A dictionary with a subset of parameters present in data, as keys and values.
        Values always are a tuple of the pattern (value, None)

    Raises
    ------
    TypeError
        If data is not of type dict.
    TypeError
        If criteria is not of type dict.

    """
    if not isinstance(data, dict) and not isinstance(data, MappingProxyType):
        raise TypeError("data should be of type dict, but is {0}".format(type(data)))
    if not isinstance(criteria, dict):
        raise TypeError("criteria should be of type dict, but is {0}".format(type(criteria)))

    criteria = {
        k: v
        for k, v in criteria.items()
        if v != IGNORE
    }

    return [
        k
        for k, v in data.items()
        if all(v.get(field) == value for field, value in criteria.items())
    ]


if __name__ == "__main__":
    raise RuntimeError("tools.py has no main function and is not meant to be executed directly.")  # Not reached by tests. Only targets code errors.

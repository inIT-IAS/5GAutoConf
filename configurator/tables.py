#!/usr/bin/env python

# Copyright (c) 2026 Niels Hendrik Fliedner
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL
# was not distributed with this file, You can obtain one at
# https://mozilla.org/MPL/2.0/.

"""Interface 3GPP tables for 5GAutoConf.

Raises
------
RuntimeError
    If this script is called directly or trying to access the main() function.

"""
from . import ts_dicts

FREQ_RANGE_LIST = ["FR1", "FR2", "FR2-1", "FR2-2"]

NUMEROLOGY_RANGE_LIST = [0, 1, 2, 3, 4, 5, 6]
NUMEROLOGY_FREQUENCY_RANGE_LIST = [15, 30, 60, 120, 240, 480, 960]
CHANNEL_BANDWIDTH_MHZ_RANGE_LIST = [
    3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100,
    200, 400, 800, 1600, 2000
]

NR_FR1_FREQ_BANDS_LIST = [
    1, 2, 3, 5, 7, 8, 12, 13, 14, 18, 20, 24, 25, 26, 28, 29, 30, 31, 34,
    35, 38, 39, 40, 41, 46, 47, 48, 50, 51, 53, 54, 65, 66, 67, 70, 71, 72,
    74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 89, 90, 91, 92, 93,
    94, 95, 96, 97, 98, 99, 100, 101, 102, 104, 105, 106, 109
]

NR_FR2_FREQ_BANDS_LIST = [
    257, 258, 259, 260, 261, 262, 263
]

#
# 3GPP TS 38.101-1 Table 5.3.2-1
#
NR_FR1_CHANNEL_SCS_KHZ_LIST = [
    15, 30, 60
]

#
# 3GPP TS 38.101-2 Table 5.3.2-1
#
NR_FR2_CHANNEL_SCS_KHZ_LIST = [
    60, 120, 480, 960
]

#
# 3GPP TS 38.101-1 Table 5.3.5-1
#
NR_FR1_CHANNEL_BW_MHZ_LIST = [
    3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100
]

#
# 3GPP TS 38.101-2 Table 5.3.5-1
#
NR_FR2_CHANNEL_BW_MHZ_LIST = [
    50, 100, 200, 400, 800, 1600, 2000
]

#
# 3GPP TS 38.211 Tables 6.3.3.2-2 to 6.3.3.2-4
# PRACH duration N_dur^RA for each PRACH configuration index in symbol durations of the current \Delta f_RA
#
N_RA_DUR = {
    "0": 0,
    "1": 0,
    "2": 0,
    "3": 0,
    "A1": 2,
    "A1/B1": 2,
    "A2": 4,
    "A2/B2": 4,
    "A3": 6,
    "A3/B3": 6,
    "B1": 2,
    "B2": 4,
    "B3": 6,
    "B4": 12,
    "C0": 2,
    "C2": 6,
}

#
# 3GPP TS 38.300
#


def ts_38_300_table_5_1_1(mu: int, col: str):
    """Look-up 3GPP TS 38.300 Table 5.1-1.
    Caption: Supported transmission numerologies.
    Refers to ts_dicts.TS_38_300_TABLE_5_1_1.

    :3GPP Table Columns:
        * 0 : Numerology µ
        * 1 : Δf = 2^mu * 15 [kHz]
        * 2 : Cyclic prefix ("Normal" or "Normal, Extended")
        * 3 : Support for Data (PDSCH, PUSCH, etc)
        * 4 : Support for Synch (PSS, SSS, PBCH)

    Parameters
    ----------
    mu : int
        The numerology µ.
    col : str
        The column to read and return.

    Returns
    -------
    int
        The subcarrier spacing in khz.
        If col = "Delta f in kHz".

    str
        The cyclic prefix type.
        If col = "CP".

    Bool
        True, if Data is supportet.
        If col = "Supported for data".

    Bool
        True, if Synch is supportet.
        If col = "Supported for synch".

    Raises
    ------
    TypeError
        If mu is not of type int.
    TypeError
        If col is not of type str.
    ValueError
        If mu is not in [0, 1, 2, 3, 4, 5, 6].
    KeyError
        If col is not in ["Delta f in kHz", "CP", "Supported for data", "Supported for synch"].

    """
    if not isinstance(mu, int):
        raise TypeError("mu should be of type int, but is {0}!".format(type(mu)))
    if not isinstance(col, str):
        raise TypeError("col should be of type str, but is {0}!".format(type(col)))
    if mu not in NUMEROLOGY_RANGE_LIST:
        raise ValueError("Unknown numerology {0}!".format(mu))

    try:
        return ts_dicts.TS_38_300_TABLE_5_1_1[mu][col][0]
    except KeyError:
        raise ValueError("A column header of {0} is not supported!".format(col))

#
# 3GPP TS 38.214
#


def ts_38_214_ch_5_1_2_2_2(rb_start: int, l_rbs: int):
    """Look-up NR RIV from table generated from the first equations in 3GPP TS 38.211 Ch. 5.1.2.2.2.
    Header: Downlink resource allocation type 1.
    Refers to TS_38_214_CH_5_1_2_2_2_EQ.
    These equations compute an NR RIV for all cases except when DCI format 1_0 is decoded.

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
    from . import tools

    if not isinstance(rb_start, int):
        raise TypeError("rb_start should be of type int, but is {0}!".format(type(rb_start)))
    if not isinstance(l_rbs, int):
        raise TypeError("l_rbs should be of type int, but is {0}!".format(type(l_rbs)))
    if l_rbs < 1:
        raise ValueError("l_rbs should be >= 1, but is {0}!".format(l_rbs))
    if l_rbs > (tools.N_RBS_PER_BWP - rb_start):
        raise ValueError("l_rbs should not exceed N_^size_BWP - RB_Start (which is {0} - {1} = {2}), but is {3}!".format(tools.N_RBS_PER_BWP, rb_start, tools.N_RBS_PER_BWP - rb_start, l_rbs))

    return ts_dicts.TS_38_214_CH_5_1_2_2_2_EQ[str(l_rbs)][str(rb_start)][0]


def ts_38_214_ch_5_1_2_2_2_reverse(nr_riv: int):
    """Look-up RB_Start and L_RBs from table generated from the first equations in 3GPP TS 38.211 Ch. 5.1.2.2.2.
    Header: Downlink resource allocation type 1.
    Refers to TS_38_214_CH_5_1_2_2_2_EQ.
    These equations compute an NR RIV for all cases except when DCI format 1_0 is decoded.

    Parameters
    ----------
    nr_riv : int
        The NR Resource Indication Value (RIV).

    Returns
    -------
    rb_start : int
        The starting virtual Resource Block RB_Start.
    l_rbs : int
        The length in terms of contiguously allocated resource blocks L_RBs.
        Usually, this equals the maximum number of resource blocks (RB_max).

    Raises
    ------
    TypeError
        If nr_riv is not of type int.
    ValueError
        If nr_riv is <0 or >37949.

    """
    if not isinstance(nr_riv, int):
        raise TypeError("nr_riv should be of type int, but is {0}!".format(type(nr_riv)))
    if nr_riv < 0 or nr_riv > 37949:
        raise ValueError("nr_riv should be >= 0 and <= 37949, but is {0}!".format(nr_riv))

    for l_rbs, inner_dict in ts_dicts.TS_38_214_CH_5_1_2_2_2_EQ.items():
        for rb_start, value in inner_dict.items():
            if value == (nr_riv, None):
                return int(rb_start), int(l_rbs)
                break

#
# 3GPP TS 38.213
#


def ts_38_213_table_8_1_2(preamble_scs_hz: int):
    """Look-up 3GPP TS 38.213 Table 8.2-1.
    Caption: N_gap values for different preamble SCS mu.
    Refers to TS_38_213_TABLE_8_1_2.

    :3GPP Table Columns:

    Parameters
    ----------
    preamble_scs_hz : int
        The subcarrier spacing of the PRACH.

    Returns
    -------
    n_gap : int
        The number of gap symbols after SS/PBCH block, N_gap.

    Raises
    ------
    TypeError
        If preamble_scs_hz is not of type int.
    ValueError
        If preamble_scs_hz is not in [1250, 5000, 15000, 30000, 60000, 120000, 480000, 960000].

    """
    if not isinstance(preamble_scs_hz, int):
        raise TypeError("preamble_scs_hz should be of type int, but is {0}!".format(type(preamble_scs_hz)))
    if preamble_scs_hz not in [1250, 5000, 15000, 30000, 60000, 120000, 480000, 960000]:
        raise ValueError("A preamble_scs_hz of {0} Hz is not supported!".format(preamble_scs_hz))

    return ts_dicts.TS_38_213_TABLE_8_1_2[str(preamble_scs_hz)]["N_gap"][0]


def ts_38_213_ch_11_1(slot_configuration_period_ms: float):
    """Look-up 3GPP TS 38.213 chapter 11.1 regarding applicable slot configuration periods.
    Header: Slot configuration.
    These are defined by dl-UL-TransmissionPeriodicity in pattern1 of tdd-UL-DL-ConfigurationCommon.
    TS 38.331 ch. 6.3.2 defines the options 0.5, 0.625, 1.0, 1.25, 2.0, 2.5, 5.0, and 10.0.
    However, only 0.625, 1.25, 2.5, and 10.0 are linked to µ_ref in 3GPP TS 38.213 chapter 11.1.
    Refers to TS_38_213_CH_11_1.

    Parameters
    ----------
    slot_configuration_period_ms : float
        The slot configuration period P.
        This is defined by the parameter dl-UL-TransmissionPeriodicity.

    Returns
    -------
    mu_ref : list
        A list of matching reference numerologies for the slot configuration period P.
        Is None if no matching mu_ref is found.

    Raises
    ------
    TypeError
        If slot_configuration_period_ms is not of type float.
    ValueError
        If slot_configuration_period_ms is not in [0.5,0.625,1.0,1.25,2.0,2.5,5.0,10.0].

    """
    from . import tools

    if not isinstance(slot_configuration_period_ms, float):
        raise TypeError("slot_configuration_period_ms should be of type float, but is {0}!".format(type(slot_configuration_period_ms)))
    if slot_configuration_period_ms not in [*tools.DL_UL_TRANSMISSION_PERIODICITY_MS.values()]:
        raise ValueError("A slot_configuration_period_ms of {0} ms is not supported!".format(slot_configuration_period_ms))

    return ts_dicts.TS_38_213_CH_11_1[str(slot_configuration_period_ms)]["mu_ref"][0]


def ts_38_213_ch_11_1_reverse(mu_ref: int):
    """Look-up 3GPP TS 38.213 chapter 11.1 regarding the Reference Subcarrier Spacing.
    Header: Slot configuration.
    Refers to TS_38_213_CH_11_1.

    Parameters
    ----------
    mu_ref : int
        The Reference Subcarrier Spacing µ_ref.

    Returns
    -------
    slot_configuration_period_ms_tuple : tuple
        The applicable slot configuration periods P.
        Empty tuple if no mu_ref is assigned to P.

    Raises
    ------
    TypeError
        If mu_ref is not of type int.
    ValueError
        If mu_ref is not in [0,1,2,3,4,5,6].

    """
    if not isinstance(mu_ref, int):
        raise TypeError("mu_ref should be of type int, but is {0}!".format(type(mu_ref)))
    if mu_ref not in NUMEROLOGY_RANGE_LIST:
        raise ValueError("A mu_ref of {0} is not supported!".format(mu_ref))

    return tuple(
        key
        for key, inner_dict in ts_dicts.TS_38_213_CH_11_1.items()
        if inner_dict.get("mu_ref") is not None and inner_dict["mu_ref"][0] is not None and mu_ref in inner_dict["mu_ref"][0]
    )

#
# 3GPP TS 38.211
#


def ts_38_211_table_6_3_3_1_1(prach_preamble_format: str):
    """Look-up 3GPP TS 38.211 Table 6.3.3.1-1.
    Caption: PRACH preamble formats for L_RA = 839 and Delta f_RA in {1.25, 5} kHz.
    Refers to TS_38_211_TABLE_6_3_3_1_1.

    :3GPP Table Columns:
        * 1 : Format
        * 2 : L_RA
        * 3 : Delta f_RA
        * 4 : N_u
        * 5 : N_CP^RA
        * 6 : Support for restricted sets

    Parameters
    ----------
    prach_preamble_format : str
        The PRACH preamble format.

    Returns
    -------
    row : dict
        The row of the PRACH preamble format.

    Raises
    ------
    TypeError
        if prach_preamble_format is not of type str.
    ValueError
        If prach_preamble_format is not in [0,1,2,3].

    """
    if not isinstance(prach_preamble_format, str):
        raise TypeError("prach_preamble_format should be of type str, but is {0}!".format(type(prach_preamble_format)))
    if prach_preamble_format not in ["0", "1", "2", "3"]:
        raise ValueError("A prach_preamble_format of {0} is not supported! The permitted formats are 0, 1, 2, 3.".format(prach_preamble_format))

    return ts_dicts.TS_38_211_TABLE_6_3_3_1_1[prach_preamble_format]


def ts_38_211_table_6_3_3_1_2(prach_preamble_format: str):
    """Look-up 3GPP TS 38.211 Table 6.3.3.1-2.
    Caption: Preamble formats for L_RA in {139,571,1151} and Delta f_RA = 15 x 2^mu kHz where mu in {0,1,2,3,5,6} kHz.
    Refers to TS_38_211_TABLE_6_3_3_1_2.

    :3GPP Table Columns:
        * 1 : Format
        * 2 : L_RA for mu in {0,1,2,3,5,6}
        * 3 : L_RA for mu in {0,3}
        * 4 : L_RA for mu in {1,3,5}
        * 5 : Delta f_RA
        * 6 : N_u
        * 7 : N_CP^RA
        * 8 : Support for restricted sets

    Parameters
    ----------
    prach_preamble_format : str
        The PRACH preamble format.

    Returns
    -------
    row : dict
        The row of the PRACH preamble format.

    Raises
    ------
    TypeError
        if prach_preamble_format is not of type str.
    ValueError
        If prach_preamble_format is not in ["A1","A2","A3","B1","B2","B3","B4","C0","C2"].

    """
    if not isinstance(prach_preamble_format, str):
        raise TypeError("prach_preamble_format should be of type str, but is {0}!".format(type(prach_preamble_format)))
    if prach_preamble_format not in ["A1", "A2", "A3", "B1", "B2", "B3", "B4", "C0", "C2"]:
        raise ValueError("A prach_preamble_format of {0} is not supported! The permitted formats are A1, A2, A3, B1, B2, B3, B4, C0, and C2.".format(prach_preamble_format))

    return ts_dicts.TS_38_211_TABLE_6_3_3_1_2[prach_preamble_format]


def ts_38_211_table_6_3_3_1_5(zero_correlation_zone_config: int):
    """Look-up 3GPP TS 38.211 Table 6.3.3.1-5.
    Caption: N_CS for preamble formats with Δf_RA = 1.25 kHz.
    Refers to TS_38_211_TABLE_6_3_3_1_5.

    :3GPP Table Columns:
        * 0 : zeroCorrelationZoneConfig,msgA-ZeroCorrelationZoneConfig
        * 1 : N_CS value for N_CS value for Unrestricted set
        * 2 : N_CS value for Restricted set type A
        * 3 : N_CS value for Restricted set type B

    Parameters
    ----------
    zero_correlation_zone_config : int
        The zeroCorrelationZoneConfig or msgA-ZeroCorrelationZoneConfig.

    Returns
    -------
    row : dict
        The row of the zeroCorrelationZoneConfig.

    Raises
    ------
    TypeError
        if zero_correlation_zone_config is not of type int.
    ValueError
        If zero_correlation_zone_config is not in [0, ..., 15].

    """
    if not isinstance(zero_correlation_zone_config, int):
        raise TypeError("zero_correlation_zone_config should be of type int, but is {0}!".format(type(zero_correlation_zone_config)))
    if not 0 <= zero_correlation_zone_config <= 15:
        raise ValueError("A zeroCorrelationZoneConfig of {0} is not supported! The permitted range is 0, ..., 15.".format(zero_correlation_zone_config))

    return ts_dicts.TS_38_211_TABLE_6_3_3_1_5[str(zero_correlation_zone_config)]


def ts_38_211_table_6_3_3_1_6(zero_correlation_zone_config: int):
    """Look-up 3GPP TS 38.211 Table 6.3.3.1-6.
    Caption: N_CS for preamble formats with Δf_RA = 5 kHz.
    Refers to TS_38_211_TABLE_6_3_3_1_6.

    :3GPP Table Columns:
        * 0 : zeroCorrelationZoneConfig,msgA-ZeroCorrelationZoneConfig
        * 1 : N_CS value for N_CS value for Unrestricted set
        * 2 : N_CS value for Restricted set type A
        * 3 : N_CS value for Restricted set type B

    Parameters
    ----------
    zero_correlation_zone_config : int
        The zeroCorrelationZoneConfig or msgA-ZeroCorrelationZoneConfig.

    Returns
    -------
    row : dict
        The row of the zeroCorrelationZoneConfig.

    Raises
    ------
    TypeError
        if zero_correlation_zone_config is not of type int.
    ValueError
        If zero_correlation_zone_config is not in [0, ..., 15].

    """
    if not isinstance(zero_correlation_zone_config, int):
        raise TypeError("zero_correlation_zone_config should be of type int, but is {0}!".format(type(zero_correlation_zone_config)))
    if not 0 <= zero_correlation_zone_config <= 15:
        raise ValueError("A zeroCorrelationZoneConfig of {0} is not supported! The permitted range is 0, ..., 15.".format(zero_correlation_zone_config))

    return ts_dicts.TS_38_211_TABLE_6_3_3_1_6[str(zero_correlation_zone_config)]


def ts_38_211_table_6_3_3_1_7(zero_correlation_zone_config: int):
    """Look-up 3GPP TS 38.211 Table 6.3.3.1-7.
    Caption: N_CS for preamble formats with L_RA in {139,571,1151}.
    Refers to TS_38_211_TABLE_6_3_3_1_7.

    :3GPP Table Columns:
        * 0 : zeroCorrelationZoneConfig,msgA-ZeroCorrelationZoneConfig
        * 1 : N_CS value for L_RA = 139
        * 2 : N_CS value for L_RA = 571
        * 3 : N_CS value for L_RA = 1151

    Parameters
    ----------
    zero_correlation_zone_config : int
        The zeroCorrelationZoneConfig or msgA-ZeroCorrelationZoneConfig.

    Returns
    -------
    row : dict
        The row of the zeroCorrelationZoneConfig.

    Raises
    ------
    TypeError
        if zero_correlation_zone_config is not of type int.
    ValueError
        If zero_correlation_zone_config is not in [0, ..., 15].

    """
    if not isinstance(zero_correlation_zone_config, int):
        raise TypeError("zero_correlation_zone_config should be of type int, but is {0}!".format(type(zero_correlation_zone_config)))
    if not 0 <= zero_correlation_zone_config <= 15:
        raise ValueError("A zeroCorrelationZoneConfig of {0} is not supported! The permitted range is 0, ..., 15.".format(zero_correlation_zone_config))

    return ts_dicts.TS_38_211_TABLE_6_3_3_1_7[str(zero_correlation_zone_config)]


def ts_38_211_table_6_3_3_2_4(prach_conf_idx: int):
    """Look-up 3GPP TS 38.211 Table 6.3.3.2-4.
    Caption: Random access configurations for FR2 and unpaired spectrum.
    Refers to TS_38_211_TABLE_6_3_3_2_4.

    .. note::
        "Unpaired" refers to TDD settings.

    :3GPP Table Columns:
        * 1 : PRACH Configuration Index
        * 2 : Preamble format, ["A1", "A2", "A3", "B1", "B4", "C0", "C2", "A1/B1", "A2/B2", "A3/B3"].
        * 3 : x (used in n_f mod x = y)
        * 4 : y (used in n_f mod x = y)
        * 5 : Slot number
        * 6 : Starting symbol
        * 7 : Number of PRACH slots within a 60 kHz slot
        * 8 : N_t^RA,slot, number of time-domain PRACH occasions within a PRACH slot
        * 9 : N_dur^RA, PRACH duration

    Parameters
    ----------
    prach_conf_idx : int
        The PRACH Configuration Index.

    Returns
    -------
    row : dict
        The row of the PRACH Configuration Index.

    Raises
    ------
    TypeError
        if prach_conf_idx is not of type int.
    ValueError
        If prach_conf_idx is not in [0, ..., 255].

    """
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))
    if not 0 <= prach_conf_idx <= 255:
        raise ValueError("A PRACH Configuration Index of {0} is not supported! The permitted range is 0, ..., 255.".format(prach_conf_idx))

    return ts_dicts.TS_38_211_TABLE_6_3_3_2_4[str(prach_conf_idx)]


def ts_38_211_table_6_3_3_2_3(prach_conf_idx: int):
    """Look-up 3GPP TS 38.211 Table 6.3.3.2-3.
    Caption: Random access configurations for FR1 and unpaired spectrum.
    Refers to TS_38_211_TABLE_6_3_3_2_3.

    .. note::
        "Unpaired" refers to TDD settings.

    :3GPP Table Columns:
        * 1 : PRACH Configuration Index
        * 2 : Preamble format, [0, 1, 2, 3, "A1", "A2", "A3", "B1", "B4", "C0", "C2", "A1/B1", "A2/B2", "A3/B3"].
        * 3 : x (used in n_f mod x = y)
        * 4 : y (used in n_f mod x = y)
        * 5 : Subframe number
        * 6 : Starting symbol
        * 7 : Number of PRACH slots within a subframe
        * 8 : N_t^RA,slot, number of time-domain PRACH occasions within a PRACH slot
        * 9 : N_dur^RA, PRACH duration

    Example Config
    --------------
        * PRACH Configuration Index : 98
        * Preamble format : A2
        * x (used in n_f mod x = y) : 2
        * y (used in n_f mod x = y) : 1
        * Subframe number : 9
        * Starting symbol : 0
        * Number of PRACH slots within a subframe : 1
        * N_t^RS,slot, number of time-domain PRACH occasions within a PRACH slot : 3
        * N_dur^RA, PRACH duration : 4

    Parameters
    ----------
    prach_conf_idx : int
        The PRACH Configuration Index.

    Returns
    -------
    row : dict
        The row of the PRACH Configuration Index.

    Raises
    ------
    TypeError
        if prach_conf_idx is not of type int.
    ValueError
        If prach_conf_idx is not in [0, ..., 262].

    """
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))
    if not 0 <= prach_conf_idx <= 262:
        raise ValueError("A PRACH Configuration Index of {0} is not supported! The permitted range is 0, ..., 262.".format(prach_conf_idx))

    return ts_dicts.TS_38_211_TABLE_6_3_3_2_3[str(prach_conf_idx)]


def ts_38_211_table_6_3_3_2_2(prach_conf_idx: int):
    """Look-up 3GPP TS 38.211 Table 6.3.3.2-2.
    Caption: Random access configurations for FR1 and paired spectrum/supplementary uplink.
    Refers to TS_38_211_TABLE_6_3_3_2_2.

    .. note::
        "Paired" refers to FDD settings, "supplementary uplink" refers to SUL.

    :3GPP Table Columns:
        * 1 : PRACH Configuration Index
        * 2 : Preamble format, [0, 1, 2, 3, "A1", "A1/B1", "A2", "A2/B2", "A3", "A3/B3", "B1", "B4", "C0", "C2"].
        * 3 : x (used in n_f mod x = y)
        * 4 : y (used in n_f mod x = y)
        * 5 : Subframe number
        * 6 : Starting symbol
        * 7 : Number of PRACH slots within a subframe
        * 8 : N_t^RA,slot, number of time-domain PRACH occasions within a PRACH slot
        * 9 : N_dur^RA, PRACH duration

    Parameters
    ----------
    prach_conf_idx : int
        The PRACH Configuration Index.

    Returns
    -------
    row : dict
        The row of the PRACH Configuration Index.

    Raises
    ------
    TypeError
        if prach_conf_idx is not of type int.
    ValueError
        If prach_conf_idx is not in [0, ..., 255].

    """
    if not isinstance(prach_conf_idx, int):
        raise TypeError("prach_conf_idx should be of type int, but is {0}!".format(type(prach_conf_idx)))
    if not 0 <= prach_conf_idx <= 255:
        raise ValueError("A PRACH Configuration Index of {0} is not supported! The permitted range is 0, ..., 255.".format(prach_conf_idx))

    return ts_dicts.TS_38_211_TABLE_6_3_3_2_2[str(prach_conf_idx)]


def ts_38_211_table_6_3_3_2_1(l_ra: int, delta_f_ra_khz: float, delta_f_khz: float):
    """Look-up 3GPP TS 38.211 Table 6.3.3.2-1.
    Caption: Supported combinations of Δf_RA and Δf, and the corresponding value of k.
    Refers to TS_38_211_TABLE_6_3_3_2_1.

    :3GPP Table Columns:
        * 1 : int : L_RA
        * 2 : float : Δf_RA for PRACH
        * 3 : float : Δf for PUSCH
        * 4 : int : N_RB^RA, allocation expressed in number of RBs for PUSCH
        * 5 : int : k

    Parameters
    ----------
    l_ra : int
        The length of the Random Access Preamble sequence in the frequency domain L_RA.

    delta_f_ra_khz : float
        The PRACH subcarrier spacing Δf_RA in kHz.

    delta_f_khz : int
        The PUSCH subcarrier spacing Δf in kHz.

    Returns
    -------
    allocation expressed in number of RBs for PUSCH, k : tuple
        For a supported combination of L_RA, Δf_RA, and Δf: allocation expressed in number of RBs for PUSCH and k.
        For an unsupported combination: None.

    Raises
    ------
    TypeError
        if l_ra is not of type int.
    TypeError
        if delta_f_ra_khz is not of type float.
    TypeError
        if delta_f_khz is not of type int.
    ValueError
        If l_ra is not in [139,571,839,1151].
    ValueError
        If delta_f_ra_khz is not in [1.25,5,15,30,60,120,480,960].
    ValueError
        If delta_f_khz is not in [15,30,60,120,480,960].

    """
    if not isinstance(l_ra, int):
        raise TypeError("l_ra should be of type int, but is {0}!".format(type(l_ra)))
    if not isinstance(delta_f_ra_khz, float):
        raise TypeError("delta_f_ra_khz should be of type float, but is {0}!".format(type(delta_f_ra_khz)))
    if not isinstance(delta_f_khz, float):
        raise TypeError("delta_f_khz should be of type float, but is {0}!".format(type(delta_f_khz)))
    if l_ra not in [139, 571, 839, 1151]:
        raise ValueError("L_RA of {0} is not supported! The permitted values are 139, 571, 839, and 1151.".format(l_ra))
    if delta_f_ra_khz not in [1.25, 5.0, 15.0, 30.0, 60.0, 120.0, 480.0, 960.0]:
        raise ValueError("Δf_RA of {0} is not supported! The permitted values are 1.25, 5, 15, 30, 60, 120, 480, and 960 kHz.".format(delta_f_ra_khz))
    if delta_f_khz not in [15.0, 30.0, 60.0, 120.0, 480.0, 960.0]:
        raise ValueError("Δf of {0} is not supported! The permitted values are 15, 30, 60, 120, 480, and 960 kHz.".format(delta_f_khz))  # This is derived from 38.211 Table 6.3.3.2-1

    try:
        return ts_dicts.TS_38_211_TABLE_6_3_3_2_1[(l_ra, delta_f_ra_khz, delta_f_khz)]
    except KeyError:
        return None


def ts_38_211_table_4_3_2_2(mu: int, col: str):
    """Look-up 3GPP TS 38.211 Table 4.3.2-2.
    Caption: Number of OFDM symbols per slot, slots per frame, and slots per subframe for extended cyclic prefix.
    Refers to TS_38_211_TABLE_4_3_2_2.

    :3GPP Table Columns:
        * 0 : Numerology µ
        * 1 : Number of OFDM symbols per slot = 14 (constant)
        * 2 : Number of slots per radio frame
        * 3 : Number of slots per subframe

    Parameters
    ----------
    mu : int
        The numerology µ.
    col : str
        The column to read and return.

    Returns
    -------
    int
        The number of OFDM symbols per slot = 14 (constant).
        If col = "N symbols per slot".
    int
        The number of slots per radio frame.
        If col = "N slots per frame".
    int
        The number of slots per subframe.
        If col = "N slots per subframe".

    Raises
    ------
    TypeError
        If mu is not of type int.
    TypeError
        If col is not of type str.
    ValueError
        If mu is not in [0, 1, 2, 3, 4, 5, 6].
    KeyError
        If col is not in ["N symbols per slot", "N slots per frame", "N slots per subframe"].

    """
    if not isinstance(mu, int):
        raise TypeError("mu should be of type int, but is {0}!".format(type(mu)))
    if not isinstance(col, str):
        raise TypeError("col should be of type str, but is {0}!".format(type(col)))
    if mu not in NUMEROLOGY_RANGE_LIST:
        raise ValueError("Unknown numerology {0}!".format(mu))

    try:
        return ts_dicts.TS_38_211_TABLE_4_3_2_2[str(mu)][col][0]
    except KeyError:
        raise ValueError("A column header of {0} is not supported!".format(col))


def ts_38_211_table_4_3_2_1(mu: int, col: str):
    """Look-up 3GPP TS 38.211 Table 4.3.2-1.
    Caption: Number of OFDM symbols per slot, slots per frame, and slots per subframe for normal cyclic prefix.
    Refers to TS_38_211_TABLE_4_3_2_1.

    :3GPP Table Columns:
        * 0 : Numerology µ
        * 1 : Number of OFDM symbols per slot = 14 (constant)
        * 2 : Number of slots per radio frame
        * 3 : Number of slots per subframe

    Parameters
    ----------
    mu : int
        The numerology µ.
    col : str
        The column to read and return.

    Returns
    -------
    int
        The number of OFDM symbols per slot = 14 (constant).
        If col = "N symbols per slot".
    int
        The number of slots per radio frame.
        If col = "N slots per frame".
    int
        The number of slots per subframe.
        If col = "N slots per subframe".

    Raises
    ------
    TypeError
        If mu is not of type int.
    TypeError
        If col is not of type str.
    ValueError
        If mu is not in [0, 1, 2, 3, 4, 5, 6].
    ValueError
        If col is not in ["N symbols per slot", "N slots per frame", "N slots per subframe"].

    """
    if not isinstance(mu, int):
        raise TypeError("mu should be of type int, but is {0}!".format(type(mu)))
    if not isinstance(col, str):
        raise TypeError("col should be of type str, but is {0}!".format(type(col)))
    if mu not in NUMEROLOGY_RANGE_LIST:
        raise ValueError("Unknown numerology {0}!".format(mu))

    try:
        return ts_dicts.TS_38_211_TABLE_4_3_2_1[str(mu)][col][0]
    except KeyError:
        raise ValueError("A column header of {0} is not supported!".format(col))


#
# 3GPP TS 38.104
#


def ts_38_104_table_5_4_3_3_1(freq_band: str):
    """Look-up 3GPP TS 38.104 Table 5.4.3.3-1.
    Caption: Applicable SS raster entries per operating band (FR1) for above 3 MHz channel bandwidth.
    Refers to TS_38_104_TABLE_5_4_3_3_1.

    :3GPP Table Columns:
        * 0 : NR operating band
        * 1 : SS Block SCS
        * 2 : SS Block pattern (Note 1)
        * 3 : Range of GSCN (First - <Step size> - Last)

    Parameters
    ----------
    freq_band : int
        The 5G NR Frequency Band.

    Returns
    -------
    dict
        A dictionary containing the SSB SCS, SS block pattern and GSCN range for the requested operating band.

    Raises
    ------
    TypeError
        If freg_band is not of type int.
    ValueError
        If freq_band is not a valid 5G NR FR1 Frequency Band.

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if freq_band not in NR_FR1_FREQ_BANDS_LIST:
        raise ValueError("n{0} is not a valid Frequency Band in FR1!".format(freq_band))

    return ts_dicts.TS_38_104_TABLE_5_4_3_3_1["n{0}".format(freq_band)]


def ts_38_104_table_5_4_3_3_2(freq_band: str):
    """Look-up 3GPP TS 38.104 Table 5.4.3.3-2.
    Caption: Applicable SS raster entries per operating band (FR2).
    Refers to TS_38_104_TABLE_5_4_3_3_2.

    Notes
    -----
    * SS Block pattern is defined in section 4.1 in TS 38.213.
        Applies to column "SS Block pattern".
    * SS Block SCS of 960 kHz is not used for initial access.
        Applies to n263 with SCS 960 kHz.

    :3GPP Table Columns:
        * 0 : NR operating band
        * 1 : SS Block SCS
        * 2 : SS Block pattern (Note 1)
        * 3 : Range of GSCN (First - <Step size> - Last)

    Parameters
    ----------
    freq_band : int
        The 5G NR Frequency Band.

    Returns
    -------
    dict
        A dictionary containing the SSB SCS, SS block pattern and GSCN range for the requested operating band.

    Raises
    ------
    TypeError
        If freg_band is not of type int.
    ValueError
        If freq_band is not a valid 5G NR FR2 Frequency Band.

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if freq_band not in NR_FR2_FREQ_BANDS_LIST:
        raise ValueError("n{0} is not a valid Frequency Band in FR2!".format(freq_band))

    return ts_dicts.TS_38_104_TABLE_5_4_3_3_2["n{0}".format(freq_band)]


def ts_38_104_table_5_4_3_3_3(scs_hz: int):
    """Look-up 3GPP TS 38.104 Table 5.4.3.3-3.
    Caption: Allowed GSCN for operation in band n263 for 120 kHz and 480 kHz
    Refers to TS_38_104_TABLE_5_4_3_3_3.

    :3GPP Table Columns:
        * 0 : SS Block SCS
        * 1 : Range of GSCN

    Parameters
    ----------
    scs_hz : int
        The subcarrier spacing in hz.

    Returns
    -------
    dict
        A dictionary containing GSCN formula parameters for the requested SSB subcarrier spacing.

    Raises
    ------
    TypeError
        If scs_hz is not of type int.
    ValueError
        If scs_hz is not in [120000, 480000].

    """
    if not isinstance(scs_hz, int):
        raise TypeError("scs_hz should be of type int, but is {0}!".format(type(scs_hz)))
    if scs_hz not in [120000, 480000]:
        raise ValueError("{0} kHz is not a valid subcarrier spacing for n263!".format(int(scs_hz / 1000)))

    return ts_dicts.TS_38_104_TABLE_5_4_3_3_3[(int(scs_hz / 1000), "kHz")]


def ts_38_104_table_5_4_3_3_4(freq_band: int):
    """Look-up 3GPP TS 38.104 Table 5.4.3.3-4.
    Caption: Applicable SS raster entries per operating band (FR1) for 3 MHz channel bandwidth
    Refers to TS_38_104_TABLE_5_4_3_3_4.

    .. note:: **Note 1**
        SS Block pattern is defined in clause 4.1 in TS 38.213.
        Applies to column "SS Block pattern".

    .. note:: **Note 2**
        Only applicable for 12 PRB transmission bandwidth configuration within 3 MHz channel with punctured PBCH defined in TS 38.211 clause 7.4.3.1.
        Applies to third GSCN setting for n100: 41637.

    :3GPP Table Columns:
        * 0 : NR operating band
        * 1 : SS Block SCS
        * 2 : SS Block pattern (Note 1)
        * 3 : Range of GSCN (First - <Step size> - Last)

    Parameters
    ----------
    freq_band : int
        The 5G NR Frequency Band.

    Returns
    -------
    dict
        A dictionary containing the SSB SCS, SS block pattern and GSCN range for the requested operating band.

    Raises
    ------
    TypeError
        If freg_band is not of type int.
    ValueError
        If freq_band is not a valid 5G NR FR1 Frequency Band.

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if freq_band not in NR_FR1_FREQ_BANDS_LIST:
        raise ValueError("n{0} is not a valid Frequency Band in FR1!".format(freq_band))

    return ts_dicts.TS_38_104_TABLE_5_4_3_3_4["n{0}".format(freq_band)]


def ts_38_104_table_b_5_2_1(channel_bw_hz: int):
    """Look-up 3GPP TS 38.104 Table B.5.2-1.
    Caption: EVM window length for normal CP, FR1, 15 kHz SCS
    Refers to TS_38_104_TABLE_B_5_2_1.

    .. note::
        These percentages are informative and apply to a slot's symbols 1 to 6 and 8 to 13. Symbols
        0 and 7 have a longer CP and therefore a lower percentage.

    :3GPP Table Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size
        * 2 : CP length for symbols 1-6 and 8-13 in FFT samples
        * 3 : EVM window length W
        * 4 : Ratio of W to total CP length for symbols 1-6 and 8-13 (Note) (%)

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    Returns
    -------
    dict
        A dictionary containing the requested Channel Bandwidth.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    ValueError
        If channel_bw_hz is not a valid 5G NR FR1 Channel Bandwidth.
    ValueError
        If channel_bw_hz is not part of this table.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1000000)

    if channel_bw_mhz not in NR_FR1_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR1!".format(channel_bw_mhz))

    try:
        return ts_dicts.TS_38_104_TABLE_B_5_2_1[str(channel_bw_mhz)]
    except KeyError:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for Table B.5.2-1!".format(channel_bw_mhz))


def ts_38_104_table_b_5_2_2(channel_bw_hz: int):
    """Look-up 3GPP TS 38.104 Table B.5.2-2.
    Caption: EVM window length for normal CP, FR1, 30 kHz SCS
    Refers to TS_38_104_TABLE_B_5_2_2.

    .. note::
        These percentages are informative and apply to a slot's symbols 1 through 13. Symbol 0 has
        a longer CP and therefore a lower percentage.

    :3GPP Table Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size
        * 2 : CP length for symbols 1-13 in FFT samples
        * 3 : EVM window length W
        * 4 : Ratio of W to total CP length for symbols 1-13 (Note) (%)

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    Returns
    -------
    dict
        A dictionary containing the requested Channel Bandwidth.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    ValueError
        If channel_bw_hz is not a valid 5G NR FR1 Channel Bandwidth.
    ValueError
        If channel_bw_hz is not part of this table.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1000000)

    if channel_bw_mhz not in NR_FR1_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR1!".format(channel_bw_mhz))

    try:
        return ts_dicts.TS_38_104_TABLE_B_5_2_2[str(channel_bw_mhz)]
    except KeyError:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for Table B.5.2-2!".format(channel_bw_mhz))


def ts_38_104_table_b_5_2_3(channel_bw_hz: int):
    """Look-up 3GPP TS 38.104 Table B.5.2-3.
    Caption: EVM window length for normal CP, FR1, 60 kHz SCS
    Refers to TS_38_104_TABLE_B_5_2_3.

    .. note::
        These percentages are informative and apply to all OFDM symbols within subframe except
        for symbol 0 of slot 0 and slot 2. Symbol 0 of slot 0 and slot 2 may have a longer CP and
        therefore a lower percentage.

    :3GPP Table Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size
        * 2 : CP length in FFT samples
        * 3 : EVM window length W
        * 4 : Ratio of W to total CP length (Note) (%)

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    Returns
    -------
    df_row : pandas.DataFrame
        A DataFrame containing the requested Channel Bandwidth.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    ValueError
        If channel_bw_hz is not a valid 5G NR FR1 Channel Bandwidth.
    ValueError
        If channel_bw_hz is not part of this table.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1000000)

    if channel_bw_mhz not in NR_FR1_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR1!".format(channel_bw_mhz))

    try:
        return ts_dicts.TS_38_104_TABLE_B_5_2_3[str(channel_bw_mhz)]
    except KeyError:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for Table B.5.2-3!".format(channel_bw_mhz))


def ts_38_104_table_b_5_2_4(channel_bw_hz: int):
    """Look-up 3GPP TS 38.104 Table B.5.2-4.
    Caption: EVM window length for extended CP, FR1, 60 kHz SCS
    Refers to TS_38_104_TABLE_B_5_2_4.

    .. note::
        These percentages are informative.
        The number of CP samples excluded from the EVM window is the same as for normal CP length.

    :3GPP Table Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size
        * 2 : CP length in FFT samples
        * 3 : EVM window length W
        * 4 : Ratio of W to total CP length (Note) (%)

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    Returns
    -------
    dict
        A dictionary containing the requested Channel Bandwidth.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    ValueError
        If channel_bw_hz is not a valid 5G NR FR1 Channel Bandwidth.
    ValueError
        If channel_bw_hz is not part of this table.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1000000)

    if channel_bw_mhz not in NR_FR1_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR1!".format(channel_bw_mhz))

    try:
        return ts_dicts.TS_38_104_TABLE_B_5_2_4[str(channel_bw_mhz)]
    except KeyError:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for Table B.5.2-4!".format(channel_bw_mhz))


def ts_38_104_table_c_5_2_1(channel_bw_hz: int):
    """Look-up 3GPP TS 38.104 Table C.5.2-1.
    Caption: EVM window length for normal CP, FR2, 60 kHz SCS
    Refers to TS_38_104_TABLE_C_5_2_1.

    .. note::
        These percentages are informative and apply to all OFDM symbols within subframe
        except for symbol 0 of slot 0 and slot 2. Symbol 0 of slot 0 and slot 2 may have a longer
        CP and therefore a lower percentage.

    :3GPP Table Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size
        * 2 : CP length in FFT samples
        * 3 : EVM window length W
        * 4 : Ratio of W to total CP length (Note) (%)

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    Returns
    -------
    dict
        A dictionary containing the requested Channel Bandwidth.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    ValueError
        If channel_bw_hz is not a valid 5G NR FR2 Channel Bandwidth.
    ValueError
        If channel_bw_hz is not part of this table.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1000000)

    # Condition based on 38.101-2 Table 5.3.5-1 Channel bandwidths for each NR band
    if channel_bw_mhz not in NR_FR2_CHANNEL_BW_MHZ_LIST[:NR_FR2_CHANNEL_BW_MHZ_LIST.index(200) + 1]:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(channel_bw_mhz))

    try:
        return ts_dicts.TS_38_104_TABLE_C_5_2_1[str(channel_bw_mhz)]
    except KeyError:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for Table C.5.2-1!".format(channel_bw_mhz))


def ts_38_104_table_c_5_2_2(channel_bw_hz: int):
    """Look-up 3GPP TS 38.104 Table C.5.2-2.
    Caption: EVM window length for normal CP, FR2, 120 kHz SCS
    Refers to TS_38_104_TABLE_C_5_2_2.

    .. note::
        These percentages are informative and apply to all OFDM symbols within subframe
        except for symbol 0 of slot 0 and slot 4. Symbol 0 of slot 0 and slot 4 may have a longer
        CP and therefore a lower percentage.

    :3GPP Table Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size
        * 2 : CP length in FFT samples
        * 3 : EVM window length W
        * 4 : Ratio of W to total CP length (Note) (%)

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    Returns
    -------
    dict
        A dictionary containing the requested Channel Bandwidth.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    ValueError
        If channel_bw_hz is not a valid 5G NR FR2 Channel Bandwidth.
    ValueError
        If channel_bw_hz is not part of this table.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1000000)

    if channel_bw_mhz not in NR_FR2_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(channel_bw_mhz))

    try:
        return ts_dicts.TS_38_104_TABLE_C_5_2_2[str(channel_bw_mhz)]
    except KeyError:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for Table C.5.2-2!".format(channel_bw_mhz))


def ts_38_104_table_c_5_2_2a(channel_bw_hz: int):
    """Look-up 3GPP TS 38.104 Table C.5.2-2a.
    Caption: EVM window length for normal CP, FR2-2, 480 kHz SCS
    Refers to TS_38_104_TABLE_C_5_2_2A.

    .. note::
        These percentages are informative and apply to all OFDM symbols within subframe
        except for symbol 0 of slot 0 and slot 4. Symbol 0 of slot 0 and slot 4 may have a longer
        CP and therefore a lower percentage.

    :3GPP Table Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size
        * 2 : CP length in FFT samples
        * 3 : EVM window length W
        * 4 : Ratio of W to total CP length (Note) (%)

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    Returns
    -------
    dict
        A dictionary containing the requested Channel Bandwidth.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    ValueError
        If channel_bw_hz is not a valid 5G NR FR2 Channel Bandwidth.
    ValueError
        If channel_bw_hz is not part of this table.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1000000)

    if channel_bw_mhz not in NR_FR2_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(channel_bw_mhz))

    try:
        return ts_dicts.TS_38_104_TABLE_C_5_2_2A[str(channel_bw_mhz)]
    except KeyError:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for Table C.5.2-2a!".format(channel_bw_mhz))


def ts_38_104_table_c_5_2_2b(channel_bw_hz: int):
    """Look-up 3GPP TS 38.104 Table C.5.2-2b.
    Caption: EVM window length for normal CP, FR2-2, 960 kHz SCS
    Refers to TS_38_104_TABLE_C_5_2_2B.

    .. note::
        These percentages are informative and apply to all OFDM symbols within subframe
        except for symbol 0 of slot 0 and slot 4. Symbol 0 of slot 0 and slot 4 may have a longer
        CP and therefore a lower percentage.

    :3GPP Table Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size
        * 2 : CP length in FFT samples
        * 3 : EVM window length W
        * 4 : Ratio of W to total CP length (Note) (%)

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    Returns
    -------
    dict
        A dictionary containing the requested Channel Bandwidth.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    ValueError
        If channel_bw_hz is not a valid 5G NR FR2 Channel Bandwidth.
    ValueError
        If channel_bw_hz is not part of this table.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1000000)

    if channel_bw_mhz not in NR_FR2_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(channel_bw_mhz))

    try:
        return ts_dicts.TS_38_104_TABLE_C_5_2_2B[str(channel_bw_mhz)]
    except KeyError:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for Table C.5.2-2b!".format(channel_bw_mhz))


def ts_38_104_table_c_5_2_3(channel_bw_hz: int):
    """Look-up 3GPP TS 38.104 Table C.5.2-3.
    Caption: EVM window length for extended CP, FR2, 60 kHz SCS
    Refers to TS_38_104_TABLE_C_5_2_3.

    .. note::
        These percentages are informative.

    :3GPP Table Columns:
        * 0 : Channel bandwidth (MHz)
        * 1 : FFT size
        * 2 : CP length in FFT samples
        * 3 : EVM window length W
        * 4 : Ratio of W to total CP length (Note) (%)

    Parameters
    ----------
    channel_bw_hz : int
        The channel bandwidth in Hz.

    Returns
    -------
    dict
        A dictionary containing the requested Channel Bandwidth.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    ValueError
        If channel_bw_hz is not a valid 5G NR FR2 Channel Bandwidth.
    ValueError
        If channel_bw_hz is not part of this table.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1000000)

    if channel_bw_mhz not in NR_FR2_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(channel_bw_mhz))

    try:
        return ts_dicts.TS_38_104_TABLE_C_5_2_3[str(channel_bw_mhz)]
    except KeyError:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for Table C.5.2-3!".format(channel_bw_mhz))

#
# 3GPP TS 38.101-1
#


def ts_38_101_1_table_5_1_1(freq_range: str):
    """Look-up 3GPP TS 38.101-1 Table 5.1-1.
    Caption: Definition of frequency ranges.
    Refers to TS_38_101_1_TABLE_5_1_1.

    :3GPP Table Columns:
        * 0 : Frequency range designation
        * 1 : Corresponding frequency range

    Parameters
    ----------
    freq_range : str
        The designated frequency range.
        Includes FR1, FR2, FR2-1, and FR2-2.

    Returns
    -------
    tuple
        The corresponding frequency range lower and upper limit in hz (FR_lower, FR_upper).
        Tuple contains only the integer values in Hz.

    Raises
    ------
    TypeError
        If freq_range is not of type str.
    ValueError
        If freq_range is not in ["FR1", "FR2", "FR2-1", "FR2-2"].

    """
    if not isinstance(freq_range, str):
        raise TypeError("freq_range should be of type str, but is {0}!".format(type(freq_range)))
    if freq_range not in FREQ_RANGE_LIST:
        raise ValueError("A frequency range of {0} is not supported!".format(freq_range))

    return tuple(x * 1_000_000 for x in ts_dicts.TS_38_101_1_TABLE_5_1_1[freq_range]["Corresponding frequency range"][0])


def ts_38_101_1_table_5_2_1(freq_band: int, col: str):
    """Look-up 3GPP TS 38.101-1 Table 5.2-1.
    Caption: NR operating bands in FR1.
    Refers to TS_38_101_1_TABLE_5_2_1.

    :3GPP Table Columns:
        * 0 : NR operating band
        * 1 : Uplink (UL) operating band BS receive / UE transmit F_UL_low - F_UL_high
        * 2 : Downlink (DL) operating band BS transmit / UE receive F_DL_low - F_DL_high
        * 3 : Duplex Mode

    Parameters
    ----------
    freq_band : int
        The NR operating band.
    col : str
        The column to read and return.

    Returns
    -------
    tuple
        The uplink NR operating Band (F_UL_low, F_UL_high) in MHz.
        If col = "Uplink (UL) operating band BS receive / UE transmit".
        None, if SDL.
    tuple
        The downlink NR operating Band (F_DL_low, F_DL_high) in MHz.
        If col = "Downlink (DL) operating band BS transmit / UE receive".
        None, if SUL.
    str
        The Duplex Mode.
        If col = "Duplex Mode".

    Raises
    ------
    TypeError
        If freq_band is not of type int.
    TypeError
        If col is not of type str.
    ValueError
        If freq_band is not a valid operating band in FR1.
    ValueError
        If col is not in ["Uplink (UL) operating band BS receive / UE transmit", "Downlink (DL) operating band BS transmit / UE receive", "Duplex Mode"].

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if not isinstance(col, str):
        raise TypeError("col should be of type str, but is {0}!".format(type(col)))
    if freq_band not in NR_FR1_FREQ_BANDS_LIST:
        raise ValueError("n{0} is not a valid Frequency Band in FR1!".format(freq_band))

    try:
        return ts_dicts.TS_38_101_1_TABLE_5_2_1["n{0}".format(freq_band)][col][0]
    except KeyError:
        raise ValueError("A column header of {0} is not supported!".format(col))


def ts_38_101_1_table_5_3_2_1(channel_bw_hz: int, scs_hz: int):
    """Look-up 3GPP TS 38.101-1 Table 5.3.2-1, which includes FR1 only.
    Caption: Maximum transmission bandwidth configuration N_RB.
    Refers to TS_38_101_1_TABLE_5_3_2_1.

    :3GPP Table Columns:
        * 0 : SCS (kHz)
        * 1 : 3 MHz (N_RB)
        * 2 : 5 MHz (N_RB)
        * 3 : 7 MHz (N_RB)
        * 4 : 10 MHz (N_RB)
        * 5 : 15 MHz (N_RB)
        * 6 : 20 MHz (N_RB)
        * 7 : 25 MHz (N_RB)
        * 8 : 30 MHz (N_RB)
        * 9 : 35 MHz (N_RB)
        * 10 : 40 MHz (N_RB)
        * 11 : 45 MHz (N_RB)
        * 12 : 50 MHz (N_RB)
        * 13 : 60 MHz (N_RB)
        * 14 : 70 MHz (N_RB)
        * 15 : 80 MHz (N_RB)
        * 16 : 90 MHz (N_RB)
        * 17 : 100 MHz (N_RB)

    Parameters
    ----------
    channel_bw_hz : int
        The UE channel bandwidth in Hz.
    scs_hz : int
        The UE subcarrier spacing in Hz.

    Returns
    -------
    int
        The maximum transmission bandwidth configuration in NRB.
        None, if table entry is NaN.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    TypeError
        If scs_hz is not of type int.
    ValueError
        If channel_bw_hz is not in [3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100].
    ValueError
        If scs_hz is not in [15, 30, 60].

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))
    if not isinstance(scs_hz, int):
        raise TypeError("scs_hz should be of type int, but is {0}!".format(type(scs_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1_000_000)
    scs_khz = int(scs_hz / 1_000)

    if channel_bw_mhz not in NR_FR1_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR1!".format(channel_bw_mhz))
    if scs_khz not in NR_FR1_CHANNEL_SCS_KHZ_LIST:
        raise ValueError("{0} kHz is not a valid Subcarrier Spacing in FR1!".format(scs_khz))

    return ts_dicts.TS_38_101_1_TABLE_5_3_2_1[str(scs_khz)]["{0} MHz".format(channel_bw_mhz)][0]


def ts_38_101_1_table_5_3_3_1(channel_bw_hz: int, scs_hz: int):
    """Look-up 3GPP TS 38.101-1 Table 5.3.3-1, which includes FR1 only.
    Caption: Minimum guardband for each UE channel bandwidth and SCS (kHz).
    Refers to TS_38_101_1_TABLE_5_3_3_1.

    :3GPP Table Columns:
        * 0 : SCS (kHz)
        * 1 : 3 MHz
        * 2 : 5 MHz
        * 3 : 7 MHz
        * 4 : 10 MHz
        * 5 : 15 MHz
        * 6 : 20 MHz
        * 7 : 25 MHz
        * 8 : 30 MHz
        * 9 : 35 MHz
        * 10 : 40 MHz
        * 11 : 45 MHz
        * 12 : 50 MHz
        * 13 : 60 MHz
        * 14 : 70 MHz
        * 15 : 80 MHz
        * 16 : 90 MHz
        * 17 : 100 MHz

    Parameters
    ----------
    channel_bw_hz : int
        The UE channel bandwidth in Hz.
    scs_hz : int
        The UE subcarrier spacing in Hz.

    Returns
    -------
    int
        The minimum guardband in kHz.
        None, if table entry is NaN.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    TypeError
        If scs_hz is not of type int.
    ValueError
        If channel_bw_hz / 1000000 is not in [3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100].
    ValueError
        If scs_hz / 1000 is not in [15, 30, 60].

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))
    if not isinstance(scs_hz, int):
        raise TypeError("scs_hz should be of type int, but is {0}!".format(type(scs_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1_000_000)
    scs_khz = int(scs_hz / 1_000)

    if channel_bw_mhz not in NR_FR1_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR1!".format(channel_bw_mhz))
    if scs_khz not in NR_FR1_CHANNEL_SCS_KHZ_LIST:
        raise ValueError("{0} kHz is not a valid Subcarrier Spacing in FR1!".format(scs_khz))

    return ts_dicts.TS_38_101_1_TABLE_5_3_3_1[str(scs_khz)]["{0} MHz".format(channel_bw_mhz)][0]


def ts_38_101_1_table_5_3_5_1(freq_band: int):
    """Look-up 3GPP TS 38.101-1 Table 5.3.5-1, which includes FR1 only.
    Caption: Channel bandwidths for each NR band.
    Refers to TS_38_101_1_TABLE_5_3_5_1.

    :3GPP Table Columns:
        * 0 : NR Band
        * 1 : SCS (kHz)
        * 2 : 3 (UE Channel bandwidth (MHz))
        * 3 : 5 (UE Channel bandwidth (MHz))
        * 4 : 7 (UE Channel bandwidth (MHz))
        * 5 : 10 (UE Channel bandwidth (MHz))
        * 6 : 15 (UE Channel bandwidth (MHz))
        * 7 : 20 (UE Channel bandwidth (MHz))
        * 8 : 25 (UE Channel bandwidth (MHz))
        * 9 : 30 (UE Channel bandwidth (MHz))
        * 10 : 35 (UE Channel bandwidth (MHz))
        * 11 : 40 (UE Channel bandwidth (MHz))
        * 12 : 45 (UE Channel bandwidth (MHz))
        * 13 : 50 (UE Channel bandwidth (MHz))
        * 14 : 60 (UE Channel bandwidth (MHz))
        * 15 : 70 (UE Channel bandwidth (MHz))
        * 16 : 80 (UE Channel bandwidth (MHz))
        * 17 : 90 (UE Channel bandwidth (MHz))
        * 18 : 100 (UE Channel bandwidth (MHz))

    Parameters
    ----------
    freq_band : int
        The 5G NR Frequency Band.

    Returns
    -------
    dict
        A dictionary containing the requested Frequency Band.

    Raises
    ------
    TypeError
        If freq_band is not of type int.
    ValueError
        If freq_band is not a valid 5G NR FR1 Frequency Band.

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if freq_band not in NR_FR1_FREQ_BANDS_LIST:
        raise ValueError("n{0} is not a valid Frequency Band in FR1!".format(freq_band))

    return ts_dicts.TS_38_101_1_TABLE_5_3_5_1["n{0}".format(freq_band)]

#
# 3GPP TS 38.101-2
#


def ts_38_101_2_table_5_2_1(freq_band: int, col: str):
    """Look-up 3GPP TS 38.101-2 Table 5.2-1.
    Caption: NR operating bands in FR2.
    Refers to TS_38_101_2_TABLE_5_2_1.

    :3GPP Table Columns:
        * 0 : Operating band
        * 1 : Uplink (UL) operating band BS receive / UE transmit F_UL_low - F_UL_high
        * 2 : Downlink (DL) operating band BS transmit / UE receive F_DL_low - F_DL_high
        * 3 : Duplex Mode

    Parameters
    ----------
    freq_band : int
        The NR operating band.
    col : str
        The column to read and return.

    Returns
    -------
    tuple
        The uplink NR operating Band (F_UL_low, F_UL_high) in MHz.
        If col = "Uplink (UL) operating band BS receive / UE transmit".
    tuple
        The downlink NR operating Band (F_DL_low, F_DL_high) in MHz.
        If col = "Downlink (DL) operating band BS transmit / UE receive".
    str
        The Duplex Mode.
        If col = "Duplex Mode".

    Raises
    ------
    TypeError
        If freq_band is not of type int.
    TypeError
        If col is not of type str.
    ValueError
        If freq_band is not a valid operating band in FR2.
    ValueError
        If col is not in ["Uplink (UL) operating band BS receive / UE transmit", "Downlink (DL) operating band BS transmit / UE receive", "Duplex Mode"].

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if not isinstance(col, str):
        raise TypeError("col should be of type str, but is {0}!".format(type(col)))
    if freq_band not in NR_FR2_FREQ_BANDS_LIST:
        raise ValueError("n{0} is not a valid Frequency Band in FR2!".format(freq_band))

    try:
        return ts_dicts.TS_38_101_2_TABLE_5_2_1["n{0}".format(freq_band)][col][0]
    except KeyError:
        raise ValueError("A column header of {0} is not supported!".format(col))


def ts_38_101_2_table_5_3_2_1(channel_bw_hz: int, scs_hz: int):
    """Look-up 3GPP TS 38.101-1 Table 5.3.2-2, which includes FR2 only.
    Caption: Maximum transmission bandwidth configuration N_RB.
    Refers to TS_38_101_2_TABLE_5_3_2_1.

    .. note::
        SCS 480 and 960 are optional in release 19.3.0 of the specification.

    :3GPP Table Columns:
        * 0 : SCS (kHz)
        * 1 : 50 MHz (N_RB)
        * 2 : 100 MHz (N_RB)
        * 3 : 200 MHz (N_RB)
        * 4 : 400 MHz (N_RB)
        * 5 : 800 MHz (N_RB)
        * 6 : 1600 MHz (N_RB)
        * 7 : 2000 MHz (N_RB)

    Parameters
    ----------
    channel_bw_hz : int
        The UE channel bandwidth in Hz.
    scs_hz : int
        The UE subcarrier spacing in Hz.

    Returns
    -------
    int
        The maximum transmission bandwidth configuration in NRB.
        None, if table entry is NaN.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    TypeError
        If scs_hz is not of type int.
    ValueError
        If channel_bw_hz is not in [50,100,200,400,800,1600,2000].
    ValueError
        If scs_hz is not in [60,120,480,960].

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))
    if not isinstance(scs_hz, int):
        raise TypeError("scs_hz should be of type int, but is {0}!".format(type(scs_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1_000_000)
    scs_khz = int(scs_hz / 1_000)

    if channel_bw_mhz not in NR_FR2_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(channel_bw_mhz))
    if scs_khz not in NR_FR2_CHANNEL_SCS_KHZ_LIST:
        raise ValueError("{0} kHz is not a valid Subcarrier Spacing in FR2!".format(scs_khz))

    return ts_dicts.TS_38_101_2_TABLE_5_3_2_1[str(scs_khz)]["{0} MHz".format(channel_bw_mhz)][0]


def ts_38_101_2_table_5_3_3_1(channel_bw_hz: int, scs_hz: int):
    """Look-up 3GPP TS 38.101-2 Table 5.3.3-1, which includes FR2 only.
    Caption: Minimum guardband for each UE channel bandwidth and SCS (kHz).
    Refers to TS_38_101_2_TABLE_5_3_3_1.

    .. note::
        The minimum guardbands have been calculated using the following equation:
        GB_Channel = (BW_Channel x 1000 (kHz) - N_RB x SCS x 12) / 2 - SCS/2,
        where N_RB are from Table 5.3.2-1 and GB_Channel expressed in kHz.

    :3GPP Table Columns:
        * 0 : SCS (kHz)
        * 1 : 50 MHz
        * 2 : 100 MHz
        * 3 : 200 MHz
        * 4 : 400 MHz
        * 5 : 800 MHz
        * 6 : 1600 MHz
        * 7 : 2000 MHz

    Parameters
    ----------
    channel_bw_hz : int
        The UE channel bandwidth in Hz.
    scs_hz : int
        The UE subcarrier spacing in Hz.

    Returns
    -------
    int
        The minimum guardband in kHz.
        None, if table entry is NaN.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    TypeError
        If scs_hz is not of type int.
    ValueError
        If channel_bw_hz / 1000000 is not in [50, 100, 200, 400, 800, 1600, 2000].
    ValueError
        If scs_hz / 1000 is not in [60, 120, 480, 960].

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))
    if not isinstance(scs_hz, int):
        raise TypeError("scs_hz should be of type int, but is {0}!".format(type(scs_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1_000_000)
    scs_khz = int(scs_hz / 1_000)

    if channel_bw_mhz not in NR_FR2_CHANNEL_BW_MHZ_LIST:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth in FR2!".format(channel_bw_mhz))
    if scs_khz not in NR_FR2_CHANNEL_SCS_KHZ_LIST:
        raise ValueError("{0} kHz is not a valid Subcarrier Spacing in FR2!".format(scs_khz))

    return ts_dicts.TS_38_101_2_TABLE_5_3_3_1[str(scs_khz)]["{0} MHz".format(channel_bw_mhz)][0]


def ts_38_101_2_table_5_3_3_2(channel_bw_hz: int, scs_hz: int):
    """Look-up 3GPP TS 38.101-2 Table 5.3.3-2, which includes FR2-1 only.
    Caption: Minimum guardband (kHz) of SCS 240 kHz SS/PBCH block in FR2-1.
    Refers to TS_38_101_2_TABLE_5_3_3_2.

    .. note::
        In FR2-1, the minimum guardband in Table 5.3.3-2 is applicable
        only when the SCS 240 kHz SS/PBCH block is received adjacent to
        the edge of the UE channel bandwidth which the SS/PBCH block is
        located.

    :3GPP Table Columns:
        * 0 : SCS (kHz)
        * 1 : 50 MHz
        * 2 : 100 MHz
        * 3 : 200 MHz
        * 4 : 400 MHz

    Parameters
    ----------
    channel_bw_hz : int
        The UE channel bandwidth in Hz.
    scs_hz : int
        The UE subcarrier spacing in Hz.

    Returns
    -------
    int
        The minimum guardband in kHz.
        None, if table entry is NaN.

    Raises
    ------
    TypeError
        If channel_bw_hz is not of type int.
    TypeError
        If scs_hz is not of type int.
    ValueError
        If channel_bw_hz / 1000000 is not in [100, 200, 400].
    ValueError
        If scs_hz / 1000 is not 240.

    """
    if not isinstance(channel_bw_hz, int):
        raise TypeError("channel_bw_hz should be of type int, but is {0}!".format(type(channel_bw_hz)))
    if not isinstance(scs_hz, int):
        raise TypeError("scs_hz should be of type int, but is {0}!".format(type(scs_hz)))

    channel_bw_mhz = int(channel_bw_hz / 1_000_000)
    scs_khz = int(scs_hz / 1_000)

    if channel_bw_mhz not in [100, 200, 400]:
        raise ValueError("{0} MHz is not a valid Channel Bandwidth for this table!".format(channel_bw_mhz))
    if scs_khz != 240:
        raise ValueError("{0} kHz is not a valid Subcarrier Spacing for this table!".format(scs_khz))

    return ts_dicts.TS_38_101_2_TABLE_5_3_3_2[str(scs_khz)]["{0} MHz".format(channel_bw_mhz)][0]


def ts_38_101_2_table_5_3_5_1(freq_band: int):
    """Look-up 3GPP TS 38.101-2 Table 5.3.5-1, which includes FR2 only.
    Caption: Channel bandwidths for each NR band.
    Refers to TS_38_101_2_TABLE_5_3_5_1.

    .. note:: 1
        This UE channel bandwidth is optional in this release of the specification.

    .. note:: 2
        This SCS is optional in this release of the specification.

    :3GPP Table Columns:
        * 0 : Operating Band
        * 1 : SCS (kHz)
        * 2 : 50 (UE Channel bandwidth (MHz))
        * 3 : 100 (UE Channel bandwidth (MHz))
        * 4 : 200 (UE Channel bandwidth (MHz))
        * 5 : 400 (UE Channel bandwidth (MHz))
        * 6 : 800 (UE Channel bandwidth (MHz))
        * 7 : 1600 (UE Channel bandwidth (MHz))
        * 8 : 2000 (UE Channel bandwidth (MHz))

    Parameters
    ----------
    freq_band : int
        The 5G NR Frequency Band.

    Returns
    -------
    dict
        A dictionary containing the requested Frequency Band.

    Raises
    ------
    TypeError
        If freq_band is not of type int.
    ValueError
        If freq_band is not a valid 5G NR FR2 Frequency Band.

    """
    if not isinstance(freq_band, int):
        raise TypeError("freq_band should be of type int, but is {0}!".format(type(freq_band)))
    if freq_band not in NR_FR2_FREQ_BANDS_LIST:
        raise ValueError("n{0} is not a valid Frequency Band in FR2!".format(freq_band))

    return ts_dicts.TS_38_101_2_TABLE_5_3_5_1["n{0}".format(freq_band)]


if __name__ == "__main__":
    raise RuntimeError("tables.py has no main function and is not meant to be executed directly.")  # Not reached by tests. Only targets code errors.

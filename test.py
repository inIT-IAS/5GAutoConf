#!/usr/bin/env python

# Copyright (c) 2026 Niels Hendrik Fliedner
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL
# was not distributed with this file, You can obtain one at
# https://mozilla.org/MPL/2.0/.

"""Unittests for 5GAutoConf.

"""
import unittest
import pytest
import pandas as pd
import pandas.testing as pd_testing
import math
import numpy as np
import os

from types import MappingProxyType

import configurator.generator as generator
import configurator.tables as tables
import configurator.tools as tools
import configurator.ts_dicts as ts_dicts

import scripts.build_long_guard_time_prach_pusch_combination_tables as build_long_guard_time_prach_pusch_combination_tables
import scripts.build_prach_ssb_collision_free_tables as build_prach_ssb_collision_free_tables
import scripts.build_tau_d_max_rtd_max_table as build_tau_d_max_rtd_max_table


class TestTables(unittest.TestCase):
    """Test the table look-up functions.

    """
    def assertDataframeEqual(self, a, b):
        try:
            pd_testing.assert_frame_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def assertSeriesEqual(self, a, b):
        try:
            pd_testing.assert_series_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def test_table_var_ranges(self):
        """Test the parameter value ranges for the following tables.

        3GPP TS 38.101-1 Table 5.1-1
        3GPP TS 38.101-1 Table 5.3.2-1
        3GPP TS 38.101-2 Table 5.3.2-1
        3GPP TS 38.101-1 Table 5.3.3-1
        3GPP TS 38.101-2 Table 5.3.3-1
        3GPP TS 38.101-1 Table 5.3.5-1
        3GPP TS 38.101-2 Table 5.3.5-1
        3GPP TS 38.104 Table 5.4.3.3-1
        3GPP TS 38.104 Table 5.4.3.3-2
        3GPP TS 38.104 Table 5.4.3.3-3
        3GPP TS 38.104 Table 5.4.3.3-4
        3GPP TS 38.104 Table B.5.2-1
        3GPP TS 38.104 Table B.5.2-2
        3GPP TS 38.104 Table B.5.2-3
        3GPP TS 38.104 Table B.5.2-4
        3GPP TS 38.104 Table C.5.2-1
        3GPP TS 38.104 Table C.5.2-2
        3GPP TS 38.104 Table C.5.2-2a
        3GPP TS 38.104 Table C.5.2-2b
        3GPP TS 38.104 Table C.5.2-3
        3GPP TS 38.211 Table 4.2-1
        3GPP TS 38.211 Table 4.2-1 Reverse
        3GPP TS 38.211 Table 4.3.2-1
        3GPP TS 38.211 Table 6.3.3.1-1
        3GPP TS 38.211 Table 6.3.3.1-2
        3GPP TS 38.211 Table 6.3.3.1-5
        3GPP TS 38.211 Table 6.3.3.1-6
        3GPP TS 38.211 Table 6.3.3.1-7
        3GPP TS 38.211 Table 6.3.3.2-1
        3GPP TS 38.211 Table 6.3.3.2-2
        3GPP TS 38.211 Table 6.3.3.2-3
        3GPP TS 38.211 Table 6.3.3.2-4
        3GPP TS 38.213 Table 8.1-2
        3GPP TS 38.213 Chapter 11.1
        3GPP TS 38.213 Chapter 11.1 Reverse
        3GPP TS 38.300 Table 5.1-1

        """
        self.test_bw_1_hz = 40_000_000
        self.test_scs_1_hz = 30_000
        self.test_bw_2_hz = 200_000_000
        self.test_bw_3_hz = 1_600_000_000
        self.test_bw_4_hz = 100_000_000
        self.test_bw_5_hz = 3_000_000
        self.test_scs_2_hz = 120_000
        self.test_scs_3_hz = 240_000
        self.test_scs_4_hz = 480_000
        self.test_numerology_mu = 99
        self.test_numerology_col = "wrong col"
        self.test_freq_band_1 = 78
        self.test_freq_band_2 = 257
        self.test_freq_band_3 = 513
        self.test_prach_conf_idx_1 = -1
        self.test_prach_conf_idx_2 = 256
        self.test_prach_conf_idx_3 = 263
        self.test_l_ra_1 = 100
        self.test_l_ra_2 = 839
        self.test_delta_f_ra_1 = 240
        self.test_delta_f_ra_2 = 30
        self.test_delta_f_1 = 240.0
        self.test_delta_f_2 = 30.0
        self.test_prach_preamble_format_1 = '4'
        self.test_prach_preamble_format_2 = 'XX'
        self.test_zero_correlation_zone_config = 16
        self.test_slot_configuration_period_ms_1 = 0.25
        self.test_slot_configuration_period_ms_2 = 20.0

        self.assertRaises(ValueError, tables.ts_38_101_1_table_5_1_1, "not FR1")

        self.assertRaises(ValueError, tables.ts_38_101_1_table_5_2_1, self.test_freq_band_2, "Duplex Mode")
        self.assertRaises(ValueError, tables.ts_38_101_1_table_5_2_1, self.test_freq_band_1, "wrong header")

        self.assertRaises(ValueError, tables.ts_38_101_2_table_5_2_1, self.test_freq_band_3, "Duplex Mode")
        self.assertRaises(ValueError, tables.ts_38_101_2_table_5_2_1, self.test_freq_band_2, "wrong header")

        self.assertRaises(ValueError, tables.ts_38_101_1_table_5_3_2_1, self.test_bw_1_hz, self.test_scs_2_hz)
        self.assertRaises(ValueError, tables.ts_38_101_1_table_5_3_2_1, self.test_bw_2_hz, self.test_scs_1_hz)

        self.assertRaises(ValueError, tables.ts_38_101_2_table_5_3_2_1, self.test_bw_1_hz, self.test_scs_2_hz)
        self.assertRaises(ValueError, tables.ts_38_101_2_table_5_3_2_1, self.test_bw_2_hz, self.test_scs_1_hz)

        self.assertRaises(ValueError, tables.ts_38_101_1_table_5_3_3_1, self.test_bw_1_hz, self.test_scs_2_hz)
        self.assertRaises(ValueError, tables.ts_38_101_1_table_5_3_3_1, self.test_bw_2_hz, self.test_scs_1_hz)

        self.assertRaises(ValueError, tables.ts_38_101_2_table_5_3_3_1, self.test_bw_2_hz, self.test_scs_1_hz)
        self.assertRaises(ValueError, tables.ts_38_101_2_table_5_3_3_1, self.test_bw_1_hz, self.test_scs_2_hz)

        self.assertRaises(ValueError, tables.ts_38_101_2_table_5_3_3_2, self.test_bw_2_hz, self.test_scs_1_hz)
        self.assertRaises(ValueError, tables.ts_38_101_2_table_5_3_3_2, self.test_bw_1_hz, self.test_scs_3_hz)

        self.assertRaises(ValueError, tables.ts_38_101_1_table_5_3_5_1, self.test_freq_band_2)

        self.assertRaises(ValueError, tables.ts_38_101_2_table_5_3_5_1, self.test_freq_band_1)

        self.assertRaises(ValueError, tables.ts_38_104_table_5_4_3_3_1, self.test_freq_band_2)

        self.assertRaises(ValueError, tables.ts_38_104_table_5_4_3_3_2, self.test_freq_band_3)

        self.assertRaises(ValueError, tables.ts_38_104_table_5_4_3_3_3, self.test_scs_1_hz)

        self.assertRaises(ValueError, tables.ts_38_104_table_5_4_3_3_4, self.test_freq_band_2)

        self.assertRaises(ValueError, tables.ts_38_104_table_b_5_2_1, self.test_bw_2_hz)
        self.assertRaises(ValueError, tables.ts_38_104_table_b_5_2_1, self.test_bw_4_hz)

        self.assertRaises(ValueError, tables.ts_38_104_table_b_5_2_2, self.test_bw_2_hz)
        self.assertRaises(ValueError, tables.ts_38_104_table_b_5_2_2, self.test_bw_5_hz)

        self.assertRaises(ValueError, tables.ts_38_104_table_b_5_2_3, self.test_bw_2_hz)
        self.assertRaises(ValueError, tables.ts_38_104_table_b_5_2_3, self.test_bw_5_hz)

        self.assertRaises(ValueError, tables.ts_38_104_table_b_5_2_4, self.test_bw_2_hz)
        self.assertRaises(ValueError, tables.ts_38_104_table_b_5_2_4, self.test_bw_5_hz)

        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_1, self.test_bw_1_hz)
        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_1, self.test_bw_3_hz)

        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_2, self.test_bw_1_hz)
        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_2, self.test_bw_3_hz)

        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_2a, self.test_bw_1_hz)
        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_2a, self.test_bw_2_hz)

        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_2b, self.test_bw_1_hz)
        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_2b, self.test_bw_2_hz)

        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_3, self.test_bw_1_hz)
        self.assertRaises(ValueError, tables.ts_38_104_table_c_5_2_3, self.test_bw_3_hz)

        self.assertRaises(ValueError, tables.ts_38_211_table_4_3_2_1, self.test_numerology_mu, "N symbols per slot")
        self.assertRaises(ValueError, tables.ts_38_211_table_4_3_2_1, 0, self.test_numerology_col)

        self.assertRaises(ValueError, tables.ts_38_211_table_4_3_2_2, self.test_numerology_mu, "N symbols per slot")
        self.assertRaises(ValueError, tables.ts_38_211_table_4_3_2_2, 2, self.test_numerology_col)

        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_1_1, self.test_prach_preamble_format_1)

        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_1_2, self.test_prach_preamble_format_2)

        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_1_5, self.test_zero_correlation_zone_config)

        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_1_6, self.test_zero_correlation_zone_config)

        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_1_7, self.test_zero_correlation_zone_config)

        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_2_1, self.test_l_ra_1, float(self.test_delta_f_ra_2), float(self.test_delta_f_2))
        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_2_1, self.test_l_ra_2, float(self.test_delta_f_ra_1), float(self.test_delta_f_2))
        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_2_1, self.test_l_ra_2, float(self.test_delta_f_ra_2), float(self.test_delta_f_1))

        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_2_2, self.test_prach_conf_idx_1)
        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_2_2, self.test_prach_conf_idx_2)

        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_2_3, self.test_prach_conf_idx_1)
        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_2_3, self.test_prach_conf_idx_3)

        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_2_4, self.test_prach_conf_idx_1)
        self.assertRaises(ValueError, tables.ts_38_211_table_6_3_3_2_4, self.test_prach_conf_idx_2)

        self.assertRaises(ValueError, tables.ts_38_213_table_8_1_2, self.test_scs_3_hz)

        self.assertRaises(ValueError, tables.ts_38_213_ch_11_1, self.test_slot_configuration_period_ms_1)
        self.assertRaises(ValueError, tables.ts_38_213_ch_11_1, self.test_slot_configuration_period_ms_2)

        self.assertRaises(ValueError, tables.ts_38_213_ch_11_1_reverse, self.test_numerology_mu)

        self.assertRaises(ValueError, tables.ts_38_300_table_5_1_1, self.test_numerology_mu, "Delta f in kHz")
        self.assertRaises(ValueError, tables.ts_38_300_table_5_1_1, 0, self.test_numerology_col)

    def test_table_var_types(self):
        """Test the parameter types for the following tables:

        3GPP TS 38.101-1 Table 5.1-1
        3GPP TS 38.101-1 Table 5.3.2-1
        3GPP TS 38.101-2 Table 5.3.2-1
        3GPP TS 38.101-1 Table 5.3.3-1
        3GPP TS 38.101-2 Table 5.3.3-1
        3GPP TS 38.101-1 Table 5.3.5-1
        3GPP TS 38.101-2 Table 5.3.5-1
        3GPP TS 38.104 Table 5.4.3.3-1
        3GPP TS 38.104 Table 5.4.3.3-2
        3GPP TS 38.104 Table 5.4.3.3-3
        3GPP TS 38.104 Table 5.4.3.3-4
        3GPP TS 38.104 Table B.5.2-1
        3GPP TS 38.104 Table B.5.2-2
        3GPP TS 38.104 Table B.5.2-3
        3GPP TS 38.104 Table B.5.2-4
        3GPP TS 38.104 Table C.5.2-1
        3GPP TS 38.104 Table C.5.2-2
        3GPP TS 38.104 Table C.5.2-2a
        3GPP TS 38.104 Table C.5.2-2b
        3GPP TS 38.104 Table C.5.2-3
        3GPP TS 38.211 Table 4.2-1
        3GPP TS 38.211 Table 4.2-1 Reverse
        3GPP TS 38.211 Table 4.3.2-1
        3GPP TS 38.211 Table 6.3.3.1-1
        3GPP TS 38.211 Table 6.3.3.1-2
        3GPP TS 38.211 Table 6.3.3.2-1
        3GPP TS 38.211 Table 6.3.3.2-2
        3GPP TS 38.211 Table 6.3.3.2-3
        3GPP TS 38.211 Table 6.3.3.2-4
        3GPP TS 38.213 Table 8.1-2
        3GPP TS 38.213 Chapter 11.1
        3GPP TS 38.213 Chapter 11.1 Reverse
        3GPP TS 38.300 Table 5.1-1

        """
        self.test_bw_1_hz = 40_000_000
        self.test_scs_1_hz = 30_000
        self.test_bw_2_hz = 200_000_000
        self.test_scs_2_hz = 120_000
        self.test_scs_3_hz = 240_000
        self.test_l_ra_1 = 839
        self.test_delta_f_ra_1 = 30.0
        self.test_delta_f_1 = 30.0

        self.assertRaises(TypeError, tables.ts_38_101_1_table_5_1_1, 0)

        self.assertRaises(TypeError, tables.ts_38_101_1_table_5_2_1, "not int", "Duplex Mode")
        self.assertRaises(TypeError, tables.ts_38_101_1_table_5_2_1, 78, 0)

        self.assertRaises(TypeError, tables.ts_38_101_2_table_5_2_1, "not int", "Duplex Mode")
        self.assertRaises(TypeError, tables.ts_38_101_2_table_5_2_1, 257, 0)

        self.assertRaises(TypeError, tables.ts_38_101_1_table_5_3_2_1, "not int", self.test_scs_1_hz)
        self.assertRaises(TypeError, tables.ts_38_101_1_table_5_3_2_1, self.test_bw_1_hz, "not int")

        self.assertRaises(TypeError, tables.ts_38_101_2_table_5_3_2_1, "not int", self.test_scs_2_hz)
        self.assertRaises(TypeError, tables.ts_38_101_2_table_5_3_2_1, self.test_bw_2_hz, "not int")

        self.assertRaises(TypeError, tables.ts_38_101_1_table_5_3_3_1, "not int", self.test_scs_1_hz)
        self.assertRaises(TypeError, tables.ts_38_101_1_table_5_3_3_1, self.test_bw_1_hz, "not int")

        self.assertRaises(TypeError, tables.ts_38_101_2_table_5_3_3_1, "not int", self.test_scs_2_hz)
        self.assertRaises(TypeError, tables.ts_38_101_2_table_5_3_3_1, self.test_bw_2_hz, "not int")

        self.assertRaises(TypeError, tables.ts_38_101_2_table_5_3_3_2, "not int", self.test_scs_3_hz)
        self.assertRaises(TypeError, tables.ts_38_101_2_table_5_3_3_2, self.test_bw_2_hz, "not int")

        self.assertRaises(TypeError, tables.ts_38_101_1_table_5_3_5_1, "not int")

        self.assertRaises(TypeError, tables.ts_38_101_2_table_5_3_5_1, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_5_4_3_3_1, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_5_4_3_3_2, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_5_4_3_3_3, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_5_4_3_3_4, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_b_5_2_1, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_b_5_2_2, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_b_5_2_3, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_b_5_2_4, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_c_5_2_1, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_c_5_2_2, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_c_5_2_2a, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_c_5_2_2b, "not int")

        self.assertRaises(TypeError, tables.ts_38_104_table_c_5_2_3, "not int")

        self.assertRaises(TypeError, tables.ts_38_211_table_4_3_2_1, "not int", "N symbols per slot")
        self.assertRaises(TypeError, tables.ts_38_211_table_4_3_2_1, 0, 0)

        self.assertRaises(TypeError, tables.ts_38_211_table_4_3_2_2, "not int", "N symbols per slot")
        self.assertRaises(TypeError, tables.ts_38_211_table_4_3_2_2, 2, 0)

        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_1_1, 0)

        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_1_2, 0)

        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_1_5, "not int")

        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_1_6, "not int")

        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_1_7, "not int")

        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_2_1, "not int", self.test_delta_f_ra_1, self.test_delta_f_1)
        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_2_1, self.test_l_ra_1, "not float", self.test_delta_f_1)
        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_2_1, self.test_l_ra_1, 60, self.test_delta_f_1)
        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_2_1, self.test_l_ra_1, self.test_delta_f_ra_1, "not float")
        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_2_1, self.test_l_ra_1, self.test_delta_f_ra_1, 60)

        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_2_2, "not int")

        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_2_3, "not int")

        self.assertRaises(TypeError, tables.ts_38_211_table_6_3_3_2_4, "not int")

        self.assertRaises(TypeError, tables.ts_38_213_table_8_1_2, "not int")

        self.assertRaises(TypeError, tables.ts_38_213_ch_11_1, "not float")

        self.assertRaises(TypeError, tables.ts_38_213_ch_11_1_reverse, "not int")

        self.assertRaises(TypeError, tables.ts_38_300_table_5_1_1, "not int", "Delta f in kHz")
        self.assertRaises(TypeError, tables.ts_38_300_table_5_1_1, 0, 0)

    def test_table_computation(self):
        """Test the computations from tables with known examples.

        3GPP TS 38.101-1 Table 5.1-1:

        | Frequency Range Designation | Corresponding Frequency Range |
        | --------------------------- | ----------------------------- |
        |                         FR1 |            410 MHz - 7125 MHz |

        3GPP TS 38.101-1 Table 5.2-1:

        | NR operating band | Uplink (UL) operating band | Downlink (DL) operating band | Duplex Mode |
        | ----------------- | -------------------------- | ---------------------------- | ----------- |
        | n26               |          814 MHz - 849 MHz |            859 MHz - 894 MHz |         FDD |
        | n67               |                        NaN |            738 MHz - 758 MHz |         SDL |
        | n78               |        3300 MHz - 3800 MHz |          3300 MHz - 3800 MHz |         TDD |
        | n80               |        1710 MHz - 1785 MHz |          NaN                 |         SUL |

        3GPP TS 38.101-2 Table 5.2-1:

        | NR operating band | Uplink (UL) operating band | Downlink (DL) operating band | Duplex Mode |
        | ----------------- | -------------------------- | ---------------------------- | ----------- |
        | n257              |      26500 MHz - 29500 MHz |        26500 MHz - 29500 MHz |         TDD |

        3GPP TS 38.101-1 and 3GPP TS 38.101-2 Table 5.3.3-1:

        | FR | CBW | SCS | Guardband |
        | -- | --- | --- | --------- |
        |  1 |  40 |  30 |       905 |
        |  2 | 200 | 120 |      4900 |

        3GPP TS 38.101-1 and 3GPP TS 38.101-2 Table 5.3.5-1:

        | Frequency Band | Dataframe |
        | -------------- | --------- |
        |            n78 |       yes |
        |           n257 |       yes |

        | FR | CBW | SCS | Guardband |
        | -- | --- | --- | --------- |
        |  1 |  40 |  30 |       905 |
        |  2 | 200 | 120 |      4900 |

        3GPP TS 38.104 Table 5.4.3.3-1:

        Dataframe: Yes

        | NR operating band | SS Block SCS | SS Block pattern | Range of GSCN (First-<Step size>-Last) |
        | ----------------- | ------------ | ---------------- | -------------------------------------- |
        | n34               | 15 kHz       | Case A           | [5032,5043,5054]                       |
        | n34               | 30 kHz       | Case C           | 5036-<1>-5050                          |
        | n78               | 30 kHz       | Case C           | 7711-<1>-8051                          |
        | n100              | 15 kHz       | Case A           | 2303-<1>-2307,41638                    |
        | n102              | 30 kHz       | Case C           | [9535,9548,9562,9576,9590,9603,9617,9631,9645,9659,9673,9687,9701,9714,9728,9742,9756,9770,9784,9798,9812,9826,9840,9853,9867] |

        3GPP TS 38.104 Table 5.4.3.3-2:

        Dataframe: Yes

        | NR operating band | SS Block SCS | SS Block pattern | Range of GSCN (First-<Step size>-Last) |
        | ----------------- | ------------ | ---------------- | -------------------------------------- |
        | n258              | 120 kHz      | Case D           | 22257-<1>-22443                        |
        | n258              | 240 kHz      | Case E           | 22258-<2>-22442                        |
        | n263              | 120 kHz      | Case D           | Table 5.4.3.3-3                        |
        | n263              | 480 kHz      | Case F           | Table 5.4.3.3-3                        |
        | n263              | 960 kHz      | Case G           | 24162-<6>-24954                        |

        3GPP TS 38.104 Table 5.4.3.3-3:

        | SS Block SCS | Range of GSCN                                 |
        | ------------ | --------------------------------------------- |
        | 120 kHz      | 24156 + 6 * N - 3 * floor((N+5)/18), N=0:137  |
        | 480 kHz      | 24162 + 24 * N - 12 * floor((N+4)/18), N=0:33 |

        3GPP TS 38.104 Table 5.4.3.3-4:

        Dataframe: Yes

        | NR operating band | SS Block SCS | SS Block pattern | Range of GSCN (First-<Step size>-Last) |
        | ----------------- | ------------ | ---------------- | -------------------------------------- |
        | n26               | 15 kHz       | Case A           | 30937-<1>-31100                        |
        | n100              | 15 kHz       | Case A           | 31240-<1>-31242                        |
        | n100              | 15 kHz       | Case A           | 31244-<1>-31253                        |
        | n100              | 15 kHz       | Case A           | 416372                                 |
        | n100              | 15 kHz       | Case A           | 31317-<1>-31329                        |

        3GPP TS 38.211 Table 4.2-1:

        |  µ | SCS | Cyclic Prefix |
        | -- | --- | ------------- |
        |  1 |  30 |        Normal |


        3GPP TS 38.211 Table 4.3.2-1:

        |  µ | N symbols per slot | N slots per frame | N slots per subframe |
        | -- | ------------------ | ----------------- | -------------------- |
        |  1 |                 14 |                20 |                    2 |


        3GPP TS 38.211 Table 6.3.3.1-1:

        Series: Yes

        | Format | L_RA | Δf_RA | N_u              | N_CP^RA      | Support for restricted sets |
        | ------ | ---- | ----- | ---------------- | ------------ | --------------------------- |
        | 3      | 839  | 5 kHz | 4 x 6144 x kappa | 3168 x kappa | Type A, Type B              |


        3GPP TS 38.211 Table 6.3.3.1-2:

        Series: Yes

        | Format | L_RA for mu in {0,1,2,3,5,6} | L_RA for mu in {0,3} | L_RA for mu in {1,3,5} | Delta f_RA    | N_u                      | N_CP^RA             | Support for restricted sets |
        | ------ | ---------------------------- | -------------------- | ---------------------- | ------------- | ------------------------ | ------------------- | --------------------------- |
        | A2     | 139                          | 1151                 | 571                    | 15 x 2^mu kHz | 4 x 2048 x kappa x 2^-mu | 576 x kappa x 2^-mu | NaN                         |


        3GPP TS 38.211 Table 6.3.3.1-5:

        Series: Yes

        | zeroCorrelationZoneConfig,msgA-ZeroCorrelationZoneConfig | N_CS value for Unrestricted set | N_CS value for Restricted set type A | N_CS value for Restricted set type B |
        | -------------------------------------------------------- | ------------------------------- | ------------------------------------ | ------------------------------------ |
        | 12                                                       | 119                             | 158                                  | 137                                  |
        | 15                                                       | 419                             | NaN                                  | NaN                                  |


        3GPP TS 38.211 Table 6.3.3.1-6:

        Series: Yes

        | zeroCorrelationZoneConfig,msgA-ZeroCorrelationZoneConfig | N_CS value for Unrestricted set | N_CS value for Restricted set type A | N_CS value for Restricted set type B |
        | -------------------------------------------------------- | ------------------------------- | ------------------------------------ | ------------------------------------ |
        | 12                                                       | 139                             | 173                                  | 122                                  |
        | 15                                                       | 419                             | 237                                  | NaN                                  |


        3GPP TS 38.211 Table 6.3.3.1-7:

        Series: Yes

        | zeroCorrelationZoneConfig,msgA-ZeroCorrelationZoneConfig | N_CS value for L_RA=139 | N_CS value for L_RA=571 | N_CS value for L_RA=1151 |
        | -------------------------------------------------------- | ----------------------- | ----------------------- | ------------------------ |
        | 12                                                       | 27                      | 81                      | 164                      |
        | 15                                                       | 69                      | 285                     | 575                      |


        3GPP TS 38.211 Table 6.3.3.2-1:

        Dataframe: Yes

        | L_RA | Δf_RA for PRACH | Δf for PUSCH | N_RB^RA, allocation expressed in number of RBs for PUSCH | k |
        | ---- | --------------- | ------------ | -------------------------------------------------------- | - |
        | 139  | 30              | 15           | 24                                                       | 2 |


        3GPP TS 38.211 Table 6.3.3.2-2:

        Dataframe: Yes

        | PRACH Configuration Index | Preamble format | x | y | Subframe number | Starting symbol | Number of PRACH slots within a subframe | Number of time-domain PRACH occasions within a PRACH slot | PRACH duration |
        | ------------------------- | --------------- | - | - | --------------- | --------------- | --------------------------------------- | --------------------------------------------------------- | -------------- |
        | 103                       | A1              | 1 | 0 | [2,7]           | 0               | 2                                       | 6                                                         | 2              |


        3GPP TS 38.211 Table 6.3.3.2-3:

        Dataframe: Yes

        | PRACH Configuration Index | Preamble format | x | y | Subframe number | Starting symbol | Number of PRACH slots within a subframe | Number of time-domain PRACH occasions within a PRACH slot | PRACH duration |
        | ------------------------- | --------------- | - | - | --------------- | --------------- | --------------------------------------- | --------------------------------------------------------- | -------------- |
        | 103                       | A2              | 1 | 0 | [8,9]           | 0               | 2                                       | 3                                                         | 4              |


        3GPP TS 38.211 Table 6.3.3.2-4:

        Dataframe: Yes

        | PRACH Configuration Index | Preamble format | x | y     | Slot number  | Starting symbol | Number of PRACH slots within a 60 kHz slot | Number of time-domain PRACH occasions within a PRACH slot | PRACH duration |
        | ------------------------- | --------------- | - | ----- | ------------ | --------------- | ------------------------------------------ | --------------------------------------------------------- | -------------- |
        | 148                       | C0              | 8 | [1,2] | [9,19,29,39] | 0               | 2                                          | 7                                                         | 2              |

        3GPP TS 38.213 Table 8.2-1:

        | Preamble SCS | N_gap |
        | ------------ | ----- |
        | 30 kHz       | 2     |

        3GPP TS 38.213 Chapter 11.1:

        | Applicable P in ms | mu_ref      |
        | ------------------ | ----------- |
        | 0.5                | [ ]         |
        | 5.0                | [ ]         |
        | 10.0               | [0,1,2,3,5] |

        3GPP TS 38.213 Chapter 11.1 Reverse:

        | mu_ref | Applicable P in ms |
        | ------ | ------------------ |
        | 0      | (10.0)             |
        | 4      | ()                 |
        | 6      | (0.625, 1.25, 2.5) |

        3GPP TS 38.300 Table 5.1-1:

        |  µ | SCS | Cyclic Prefix | Support for Data | Support for Synch |
        | -- | --- | ------------- | ---------------- | ----------------- |
        |  1 |  30 |        Normal |             True |              True |

        """
        self.test_bw_1_hz = 40_000_000
        self.test_scs_1_hz = 30_000
        self.test_bw_2_hz = 200_000_000
        self.test_scs_2_hz = 120_000
        self.test_scs_3_hz = 480_000
        self.test_scs_4_hz = 240_000
        self.test_numerology_mu_1 = 1
        self.test_numerology_mu_2 = 0
        self.test_numerology_mu_3 = 4
        self.test_numerology_mu_4 = 6
        self.test_numerology_mu_5 = 2
        self.test_freq_band_1 = 78
        self.test_freq_band_2 = 257
        self.test_freq_band_3 = 34
        self.test_freq_band_4 = 100
        self.test_freq_band_5 = 102
        self.test_freq_band_6 = 258
        self.test_freq_band_7 = 263
        self.test_freq_band_8 = 26
        self.test_freq_band_9 = 67
        self.test_freq_band_10 = 80
        self.test_prach_conf_idx_1 = 103
        self.test_prach_conf_idx_2 = 143
        self.test_l_ra_1 = 139
        self.test_l_ra_2 = 839
        self.test_delta_f_ra_1 = 30.0
        self.test_delta_f_ra_2 = 1.25
        self.test_delta_f_1 = 15.0
        self.test_delta_f_2 = 120.0
        self.test_delta_f_3 = 60.0
        self.test_slot_configuration_period_ms_1 = 0.5
        self.test_slot_configuration_period_ms_2 = 5.0
        self.test_slot_configuration_period_ms_3 = 10.0

        # n78
        self.test_ts_38_104_table_5_4_3_3_1_dict_1 = {
            (30, "kHz"): {
                "SS Block pattern": ("Case C", None),
                "Range of GSCN (First-<Step size>-Last)": ((7_711, 1, 8_051), None),
            },
        }

        # n34
        self.test_ts_38_104_table_5_4_3_3_1_dict_2 = {
            (15, "kHz"): {
                "SS Block pattern": ("Case A", None),
                "Range of GSCN (First-<Step size>-Last)": ([5_032, 5_043, 5_054], None),
            },
            (30, "kHz"): {
                "SS Block pattern": ("Case C", None),
                "Range of GSCN (First-<Step size>-Last)": ((5_036, 1, 5_050), None),
            },
        }

        # n100
        self.test_ts_38_104_table_5_4_3_3_1_dict_3 = {
            (15, "kHz"): {
                "SS Block pattern": ("Case A", None),
                "Range of GSCN (First-<Step size>-Last)": ((2_303, 1, 2_307), (41_638,), None),
            },
        }

        # n102
        self.test_ts_38_104_table_5_4_3_3_1_dict_4 = {
            (30, "kHz"): {
                "SS Block pattern": ("Case C", None),
                "Range of GSCN (First-<Step size>-Last)": ([9535, 9548, 9562, 9576, 9590, 9603, 9617, 9631, 9645, 9659, 9673, 9687, 9701, 9714, 9728, 9742, 9756, 9770, 9784, 9798, 9812, 9826, 9840, 9853, 9867], None),
            },
        }

        # n258
        self.test_ts_38_104_table_5_4_3_3_2_dict_1 = {
            (120, "kHz"): {
                "SS Block pattern": ("Case D", None),
                "Range of GSCN (First-<Step size>-Last)": ((22_257, 1, 22_443), None),
            },
            (240, "kHz"): {
                "SS Block pattern": ("Case E", None),
                "Range of GSCN (First-<Step size>-Last)": ((22_258, 2, 22_442), None),
            },
        }

        # n263
        self.test_ts_38_104_table_5_4_3_3_2_dict_2 = {
            (120, "kHz"): {
                "SS Block pattern": ("Case D", None),
                "Range of GSCN (First-<Step size>-Last)": ("Table 5.4.3.3-3", None),
            },
            (480, "kHz"): {
                "SS Block pattern": ("Case F", None),
                "Range of GSCN (First-<Step size>-Last)": ("Table 5.4.3.3-3", None),
            },
            (960, "kHz"): {
                "SS Block pattern": ("Case G", None),
                "Range of GSCN (First-<Step size>-Last)": ((24_162, 6, 24_954), None),
            },
        }

        # 120 kHz
        self.test_ts_38_104_table_5_4_3_3_3_dict_1 = {
            # "Range of GSCN": ("24156 + 6 * N - 3 * floor((N+5)/18), N=0:137", None),
            "Range of GSCN": ((24_156, 6, 3, 5, 18, 0, 137), None),
        }

        # 480 kHz
        self.test_ts_38_104_table_5_4_3_3_3_dict_2 = {
            # "Range of GSCN": ("24162 + 24 * N - 12 * floor((N+4)/18), N=0:33", None),
            "Range of GSCN": ((24_162, 24, 12, 4, 18, 0, 33), None),
        }

        # n26
        self.test_ts_38_104_table_5_4_3_3_4_dict_1 = {
            (15, "kHz"): {
                "SS Block pattern": ("Case A", None),
                "Range of GSCN (First-<Step size>-Last)": ((30_937, 1, 31_100), None),
            },
        }

        # n100
        self.test_ts_38_104_table_5_4_3_3_4_dict_2 = {
            (15, "kHz"): {
                "SS Block pattern": ("Case A", None),
                "Range of GSCN (First-<Step size>-Last)": ((31_240, 1, 31_242), (31_244, 1, 31_253), (41_637,), None),
            },
        }

        self.test_ts_38_104_table_b_5_2_1_dict_1 = {
            'FFT size': (1_024, None),
            'CP length for symbols 1-6 and 8-13 in FFT samples': (72, None),
            'EVM window length W': (28, None),
            'Ratio of W to total CP length for symbols 1-6 and 8-13 (Note) (%)': (40.0, None)
        }

        self.test_ts_38_104_table_b_5_2_2_dict_1 = {
            'FFT size': (512, None),
            'CP length for symbols 1-13 in FFT samples': (36, None),
            'EVM window length W': (14, None),
            'Ratio of W to total CP length for symbols 1-13 (Note) (%)': (40.0, None)
        }

        self.test_ts_38_104_table_b_5_2_3_dict_1 = {
            'FFT size': (256, None),
            'CP length in FFT samples': (18, None),
            'EVM window length W': (8, None),
            'Ratio of W to total CP length (Note) (%)': (40.0, None),
        }

        self.test_ts_38_104_table_b_5_2_4_dict_1 = {
            'FFT size': (256, None),
            'CP length in FFT samples': (64, None),
            'EVM window length W': (54, None),
            'Ratio of W to total CP length (Note) (%)': (84.0, None),
        }

        self.test_ts_38_104_table_c_5_2_1_dict_1 = {
            'FFT size': (1_024, None),
            'CP length in FFT samples': (72, None),
            'EVM window length W': (36, None),
            'Ratio of W to total CP length (Note) (%)': (50.0, None),
        }

        self.test_ts_38_104_table_c_5_2_2_dict_1 = {
            'FFT size': (512, None),
            'CP length in FFT samples': (36, None),
            'EVM window length W': (18, None),
            'Ratio of W to total CP length (Note) (%)': (50.0, None),
        }

        self.test_ts_38_104_table_c_5_2_2a_dict_1 = {
            'FFT size': (1_024, None),
            'CP length in FFT samples': (72, None),
            'EVM window length W': (36, None),
            'Ratio of W to total CP length (Note) (%)': (50.0, None),
        }

        self.test_ts_38_104_table_c_5_2_2b_dict_1 = {
            'FFT size': (512, None),
            'CP length in FFT samples': (36, None),
            'EVM window length W': (18, None),
            'Ratio of W to total CP length (Note) (%)': (50.0, None),
        }

        self.test_ts_38_104_table_c_5_2_3_dict_1 = {
            'FFT size': (1_024, None),
            'CP length in FFT samples': (256, None),
            'EVM window length W': (220, None),
            'Ratio of W to total CP length (Note) (%)': (85.9, None),
        }

        self.ts_38_211_table_6_3_3_1_1_dict = {
            "L_RA": (839, None),
            "Delta f_RA": (5, "kHz"),
            "N_u": ((4, 6_144, "Kappa"), None),
            "N_CP^RA": ((3_168, "Kappa"), None),
            "Support for restricted sets": (("Type A", "Type B"), None),
        }

        self.ts_38_211_table_6_3_3_1_2_dict = {
            "L_RA for mu in {0,1,2,3,5,6}": (139, None),
            "L_RA for mu in {0,3}": (1_151, None),
            "L_RA for mu in {1,3,5}": (571, None),
            "Delta f_RA": ((15, "2^mu"), "kHz"),
            "N_u": ((4, 2_048, "Kappa", "2^-mu"), None),
            "N_CP^RA": ((576, "Kappa", "2^-mu"), None),
            "Support for restricted sets": (None, None),
        }

        self.ts_38_211_table_6_3_3_1_5_dict_1 = {
            "N_CS value for Unrestricted set": (119, None),
            "N_CS value for Restricted set type A": (158, None),
            "N_CS value for Restricted set type B": (137, None),
        }

        self.ts_38_211_table_6_3_3_1_5_dict_2 = {
            "N_CS value for Unrestricted set": (419, None),
            "N_CS value for Restricted set type A": (None, None),
            "N_CS value for Restricted set type B": (None, None),
        }

        self.ts_38_211_table_6_3_3_1_6_dict_1 = {
            "N_CS value for Unrestricted set": (139, None),
            "N_CS value for Restricted set type A": (173, None),
            "N_CS value for Restricted set type B": (122, None),
        }

        self.ts_38_211_table_6_3_3_1_6_dict_2 = {
            "N_CS value for Unrestricted set": (419, None),
            "N_CS value for Restricted set type A": (237, None),
            "N_CS value for Restricted set type B": (None, None),
        }

        self.ts_38_211_table_6_3_3_1_7_dict_1 = {
            "N_CS value for L_RA=139": (27, None),
            "N_CS value for L_RA=571": (81, None),
            "N_CS value for L_RA=1151": (164, None),
        }

        self.ts_38_211_table_6_3_3_1_7_dict_2 = {
            "N_CS value for L_RA=139": (69, None),
            "N_CS value for L_RA=571": (285, None),
            "N_CS value for L_RA=1151": (575, None),
        }

        self.ts_38_211_table_6_3_3_2_1_tuple_1 = (24, 2)

        self.ts_38_211_table_6_3_3_2_1_tuple_2 = (2, 133)

        self.ts_38_211_table_6_3_3_2_2_dict = {
            "Preamble format": ("A1", None),
            "x": (1, None),
            "y": (0, None),
            "Subframe number": ([2, 7], None),
            "Starting symbol": (0, None),
            "Number of PRACH slots within a subframe": (2, None),
            "Number of time-domain PRACH occasions within a PRACH slot": (6, None),
            "PRACH duration": (2, None),
        }

        self.ts_38_211_table_6_3_3_2_3_dict = {
            "Preamble format": ("A2", None),
            "x": (1, None),
            "y": (0, None),
            "Subframe number": ([8, 9], None),
            "Starting symbol": (0, None),
            "Number of PRACH slots within a subframe": (2, None),
            "Number of time-domain PRACH occasions within a PRACH slot": (3, None),
            "PRACH duration": (4, None),
        }

        self.ts_38_211_table_6_3_3_2_4_dict = {
            "Preamble format": ("B4", None),
            "x": (1, None),
            "y": (0, None),
            "Slot number": (
                [
                    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                    16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                    30, 31, 32, 33, 34, 35, 36, 37, 38, 39
                ],
                None
            ),
            "Starting symbol": (2, None),
            "Number of PRACH slots within a 60 kHz slot": (1, None),
            "Number of time-domain PRACH occasions within a PRACH slot": (1, None),
            "PRACH duration": (12, None),
        }

        self.ts_38_213_ch_11_1_list_1 = None

        self.ts_38_213_ch_11_1_list_2 = None

        self.ts_38_213_ch_11_1_list_3 = [0, 1, 2, 3, 5]

        self.assertEqual(tables.ts_38_101_1_table_5_1_1(freq_range="FR1"), (410_000_000, 7_125_000_000))

        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_8, col="Uplink (UL) operating band BS receive / UE transmit"), (814, 849))
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_8, col="Downlink (DL) operating band BS transmit / UE receive"), (859, 894))
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_8, col="Duplex Mode"), "FDD")
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_9, col="Uplink (UL) operating band BS receive / UE transmit"), None)
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_9, col="Downlink (DL) operating band BS transmit / UE receive"), (738, 758))
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_9, col="Duplex Mode"), "SDL")
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_1, col="Uplink (UL) operating band BS receive / UE transmit"), (3_300, 3_800))
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_1, col="Downlink (DL) operating band BS transmit / UE receive"), (3_300, 3_800))
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_1, col="Duplex Mode"), "TDD")
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_10, col="Uplink (UL) operating band BS receive / UE transmit"), (1_710, 1_785))
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_10, col="Downlink (DL) operating band BS transmit / UE receive"), None)
        self.assertEqual(tables.ts_38_101_1_table_5_2_1(freq_band=self.test_freq_band_10, col="Duplex Mode"), "SUL")

        self.assertEqual(tables.ts_38_101_2_table_5_2_1(freq_band=self.test_freq_band_2, col="Uplink (UL) operating band BS receive / UE transmit"), (26_500, 29_500))
        self.assertEqual(tables.ts_38_101_2_table_5_2_1(freq_band=self.test_freq_band_2, col="Downlink (DL) operating band BS transmit / UE receive"), (26_500, 29_500))
        self.assertEqual(tables.ts_38_101_2_table_5_2_1(freq_band=self.test_freq_band_2, col="Duplex Mode"), "TDD")

        self.assertEqual(tables.ts_38_101_1_table_5_3_2_1(channel_bw_hz=self.test_bw_1_hz, scs_hz=self.test_scs_1_hz), 106)
        self.assertEqual(tables.ts_38_101_1_table_5_3_2_1(channel_bw_hz=3_000_000, scs_hz=self.test_scs_1_hz), None)

        self.assertEqual(tables.ts_38_101_2_table_5_3_2_1(channel_bw_hz=self.test_bw_2_hz, scs_hz=self.test_scs_2_hz), 132)
        self.assertEqual(tables.ts_38_101_2_table_5_3_2_1(channel_bw_hz=self.test_bw_2_hz, scs_hz=480_000), None)

        self.assertEqual(tables.ts_38_101_1_table_5_3_3_1(channel_bw_hz=self.test_bw_1_hz, scs_hz=self.test_scs_1_hz), 905)
        self.assertEqual(tables.ts_38_101_1_table_5_3_3_1(channel_bw_hz=3_000_000, scs_hz=self.test_scs_1_hz), None)

        self.assertEqual(tables.ts_38_101_2_table_5_3_3_1(channel_bw_hz=self.test_bw_2_hz, scs_hz=self.test_scs_2_hz), 4_900)
        self.assertEqual(tables.ts_38_101_2_table_5_3_3_1(channel_bw_hz=self.test_bw_2_hz, scs_hz=480_000), None)

        self.assertEqual(tables.ts_38_101_2_table_5_3_3_2(channel_bw_hz=self.test_bw_2_hz, scs_hz=self.test_scs_4_hz), 7_720)

        self.assertIsInstance(tables.ts_38_101_1_table_5_3_5_1(freq_band=self.test_freq_band_1), MappingProxyType)

        self.assertIsInstance(tables.ts_38_101_2_table_5_3_5_1(freq_band=self.test_freq_band_2), MappingProxyType)

        self.assertIsInstance(tables.ts_38_104_table_5_4_3_3_1(freq_band=self.test_freq_band_1), MappingProxyType)
        self.assertIsInstance(tables.ts_38_104_table_5_4_3_3_1(freq_band=self.test_freq_band_3), MappingProxyType)
        self.assertIsInstance(tables.ts_38_104_table_5_4_3_3_1(freq_band=self.test_freq_band_4), MappingProxyType)
        self.assertIsInstance(tables.ts_38_104_table_5_4_3_3_1(freq_band=self.test_freq_band_5), MappingProxyType)

        self.assertEqual(tables.ts_38_104_table_5_4_3_3_1(freq_band=self.test_freq_band_1), self.test_ts_38_104_table_5_4_3_3_1_dict_1)
        self.assertEqual(tables.ts_38_104_table_5_4_3_3_1(freq_band=self.test_freq_band_3), self.test_ts_38_104_table_5_4_3_3_1_dict_2)
        self.assertEqual(tables.ts_38_104_table_5_4_3_3_1(freq_band=self.test_freq_band_4), self.test_ts_38_104_table_5_4_3_3_1_dict_3)
        self.assertEqual(tables.ts_38_104_table_5_4_3_3_1(freq_band=self.test_freq_band_5), self.test_ts_38_104_table_5_4_3_3_1_dict_4)

        self.assertIsInstance(tables.ts_38_104_table_5_4_3_3_2(freq_band=self.test_freq_band_6), MappingProxyType)
        self.assertIsInstance(tables.ts_38_104_table_5_4_3_3_2(freq_band=self.test_freq_band_7), MappingProxyType)

        self.assertEqual(tables.ts_38_104_table_5_4_3_3_2(freq_band=self.test_freq_band_6), self.test_ts_38_104_table_5_4_3_3_2_dict_1)
        self.assertEqual(tables.ts_38_104_table_5_4_3_3_2(freq_band=self.test_freq_band_7), self.test_ts_38_104_table_5_4_3_3_2_dict_2)

        self.assertIsInstance(tables.ts_38_104_table_5_4_3_3_3(scs_hz=self.test_scs_2_hz), MappingProxyType)

        self.assertEqual(tables.ts_38_104_table_5_4_3_3_3(scs_hz=self.test_scs_2_hz), self.test_ts_38_104_table_5_4_3_3_3_dict_1)
        self.assertEqual(tables.ts_38_104_table_5_4_3_3_3(scs_hz=self.test_scs_3_hz), self.test_ts_38_104_table_5_4_3_3_3_dict_2)

        self.assertIsInstance(tables.ts_38_104_table_5_4_3_3_4(freq_band=self.test_freq_band_4), MappingProxyType)
        self.assertIsInstance(tables.ts_38_104_table_5_4_3_3_4(freq_band=self.test_freq_band_8), MappingProxyType)

        self.assertEqual(tables.ts_38_104_table_5_4_3_3_4(freq_band=self.test_freq_band_8), self.test_ts_38_104_table_5_4_3_3_4_dict_1)
        self.assertEqual(tables.ts_38_104_table_5_4_3_3_4(freq_band=self.test_freq_band_4), self.test_ts_38_104_table_5_4_3_3_4_dict_2)

        self.assertEqual(tables.ts_38_104_table_b_5_2_1(channel_bw_hz=10_000_000), self.test_ts_38_104_table_b_5_2_1_dict_1)

        self.assertEqual(tables.ts_38_104_table_b_5_2_2(channel_bw_hz=10_000_000), self.test_ts_38_104_table_b_5_2_2_dict_1)

        self.assertEqual(tables.ts_38_104_table_b_5_2_3(channel_bw_hz=10_000_000), self.test_ts_38_104_table_b_5_2_3_dict_1)

        self.assertEqual(tables.ts_38_104_table_b_5_2_4(channel_bw_hz=10_000_000), self.test_ts_38_104_table_b_5_2_4_dict_1)

        self.assertEqual(tables.ts_38_104_table_c_5_2_1(channel_bw_hz=50_000_000), self.test_ts_38_104_table_c_5_2_1_dict_1)

        self.assertEqual(tables.ts_38_104_table_c_5_2_2(channel_bw_hz=50_000_000), self.test_ts_38_104_table_c_5_2_2_dict_1)

        self.assertEqual(tables.ts_38_104_table_c_5_2_2a(channel_bw_hz=400_000_000), self.test_ts_38_104_table_c_5_2_2a_dict_1)

        self.assertEqual(tables.ts_38_104_table_c_5_2_2b(channel_bw_hz=400_000_000), self.test_ts_38_104_table_c_5_2_2b_dict_1)

        self.assertEqual(tables.ts_38_104_table_c_5_2_3(channel_bw_hz=50_000_000), self.test_ts_38_104_table_c_5_2_3_dict_1)

        self.assertEqual(tables.ts_38_211_table_4_3_2_1(mu=self.test_numerology_mu_1, col="N symbols per slot"), 14)
        self.assertEqual(tables.ts_38_211_table_4_3_2_1(mu=self.test_numerology_mu_1, col="N slots per frame"), 20)
        self.assertEqual(tables.ts_38_211_table_4_3_2_1(mu=self.test_numerology_mu_1, col="N slots per subframe"), 2)

        self.assertEqual(tables.ts_38_211_table_4_3_2_2(mu=self.test_numerology_mu_5, col="N symbols per slot"), 12)
        self.assertEqual(tables.ts_38_211_table_4_3_2_2(mu=self.test_numerology_mu_5, col="N slots per frame"), 40)
        self.assertEqual(tables.ts_38_211_table_4_3_2_2(mu=self.test_numerology_mu_5, col="N slots per subframe"), 4)

        self.assertEqual(tables.ts_38_211_table_6_3_3_2_1(l_ra=self.test_l_ra_1, delta_f_ra_khz=float(self.test_delta_f_ra_1), delta_f_khz=self.test_delta_f_1), self.ts_38_211_table_6_3_3_2_1_tuple_1)
        self.assertEqual(tables.ts_38_211_table_6_3_3_2_1(l_ra=self.test_l_ra_2, delta_f_ra_khz=float(self.test_delta_f_ra_2), delta_f_khz=self.test_delta_f_3), self.ts_38_211_table_6_3_3_2_1_tuple_2)
        self.assertEqual(tables.ts_38_211_table_6_3_3_2_1(l_ra=self.test_l_ra_1, delta_f_ra_khz=float(self.test_delta_f_ra_1), delta_f_khz=self.test_delta_f_2), None)

        self.assertEqual(tables.ts_38_211_table_6_3_3_1_1(prach_preamble_format='3'), self.ts_38_211_table_6_3_3_1_1_dict)

        self.assertEqual(tables.ts_38_211_table_6_3_3_1_2(prach_preamble_format='A2'), self.ts_38_211_table_6_3_3_1_2_dict)

        self.assertEqual(tables.ts_38_211_table_6_3_3_1_5(zero_correlation_zone_config=12), self.ts_38_211_table_6_3_3_1_5_dict_1)
        self.assertEqual(tables.ts_38_211_table_6_3_3_1_5(zero_correlation_zone_config=15), self.ts_38_211_table_6_3_3_1_5_dict_2)

        self.assertEqual(tables.ts_38_211_table_6_3_3_1_6(zero_correlation_zone_config=12), self.ts_38_211_table_6_3_3_1_6_dict_1)
        self.assertEqual(tables.ts_38_211_table_6_3_3_1_6(zero_correlation_zone_config=15), self.ts_38_211_table_6_3_3_1_6_dict_2)

        self.assertEqual(tables.ts_38_211_table_6_3_3_1_7(zero_correlation_zone_config=12), self.ts_38_211_table_6_3_3_1_7_dict_1)
        self.assertEqual(tables.ts_38_211_table_6_3_3_1_7(zero_correlation_zone_config=15), self.ts_38_211_table_6_3_3_1_7_dict_2)

        self.assertEqual(tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=self.test_prach_conf_idx_1), self.ts_38_211_table_6_3_3_2_2_dict)

        self.assertEqual(tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=self.test_prach_conf_idx_1), self.ts_38_211_table_6_3_3_2_3_dict)

        self.assertEqual(tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=self.test_prach_conf_idx_2), self.ts_38_211_table_6_3_3_2_4_dict)

        self.assertEqual(tables.ts_38_213_table_8_1_2(preamble_scs_hz=self.test_scs_1_hz), 2)

        self.assertEqual(tables.ts_38_213_ch_11_1(slot_configuration_period_ms=self.test_slot_configuration_period_ms_1), self.ts_38_213_ch_11_1_list_1)
        self.assertEqual(tables.ts_38_213_ch_11_1(slot_configuration_period_ms=self.test_slot_configuration_period_ms_2), self.ts_38_213_ch_11_1_list_2)
        self.assertEqual(tables.ts_38_213_ch_11_1(slot_configuration_period_ms=self.test_slot_configuration_period_ms_3), self.ts_38_213_ch_11_1_list_3)

        self.assertEqual(tables.ts_38_213_ch_11_1_reverse(mu_ref=self.test_numerology_mu_2), ("10.0",))
        self.assertEqual(tables.ts_38_213_ch_11_1_reverse(mu_ref=self.test_numerology_mu_3), tuple())
        self.assertEqual(tables.ts_38_213_ch_11_1_reverse(mu_ref=self.test_numerology_mu_4), ("0.625", "1.25", "2.5"))

        self.assertEqual(tables.ts_38_300_table_5_1_1(mu=self.test_numerology_mu_1, col="Delta f in kHz"), self.test_scs_1_hz / 1_000)
        self.assertEqual(tables.ts_38_300_table_5_1_1(mu=self.test_numerology_mu_1, col="CP"), "Normal")
        self.assertEqual(tables.ts_38_300_table_5_1_1(mu=self.test_numerology_mu_1, col="Supported for data"), True)
        self.assertEqual(tables.ts_38_300_table_5_1_1(mu=self.test_numerology_mu_1, col="Supported for synch"), True)


class TestGSCN(unittest.TestCase):
    """Test the GSCN functions.

    """

    def test_gscn_var_ranges(self):
        """Test the GSCN parameter value ranges.

        """
        self.test_freq_row_1_hz = 2_500_000_000
        self.test_freq_row_2_hz = 6_000_000_000
        self.test_freq_row_3_hz = 25_000_000_000

        self.assertRaises(ValueError, tools.compute_gscn, self.test_freq_row_1_hz, 0, 1)
        self.assertRaises(ValueError, tools.compute_gscn, self.test_freq_row_1_hz, 2_500, 1)
        self.assertRaises(ValueError, tools.compute_gscn, self.test_freq_row_1_hz, 1, 0)
        self.assertRaises(ValueError, tools.compute_gscn, self.test_freq_row_1_hz, 1, 2)
        self.assertRaises(ValueError, tools.compute_gscn, self.test_freq_row_1_hz, 1, 4)
        self.assertRaises(ValueError, tools.compute_gscn, self.test_freq_row_1_hz, 1, 6)
        self.assertRaises(ValueError, tools.compute_gscn, self.test_freq_row_2_hz, 14_757)
        self.assertRaises(ValueError, tools.compute_gscn, self.test_freq_row_3_hz, 4_384)

    def test_gscn_var_types(self):
        """Test the GSCN parameter types.

        """
        self.test_freq_row_1_hz = 2_500_000_000
        self.test_freq_row_2_hz = 6_000_000_000
        self.test_freq_row_3_hz = 25_000_000_000

        self.assertRaises(TypeError, tools.compute_gscn, "not int", 1, 1)
        self.assertRaises(TypeError, tools.compute_gscn, self.test_freq_row_1_hz, "not int", 1)
        self.assertRaises(TypeError, tools.compute_gscn, self.test_freq_row_1_hz, 1, "not int")
        self.assertIsInstance(tools.compute_gscn(frequency_hz=self.test_freq_row_1_hz, N=1, M=1), int)
        self.assertIsInstance(tools.compute_gscn(frequency_hz=self.test_freq_row_2_hz, N=1, M=None), int)

    def test_gscn_computation(self):
        """Test the GSCN computation with known examples.

        | Frequency Range | frequency_hz | N  | M  | GSCN | SS_REF |
        | --------------- | ------------ | -- | -- | ---- | ------ |
        | 0-3000 | 2500000000 | 2083 | 5 | 6250 | 2499850000 |
        | 3000-24250 | 6000000000 | 2083 | not used | 9582 | 5999520000 |
        | 24250-100000 | 25000000000 | 43 | not used | 22299 | 24993120000 |

        """
        self.test_freq_row_1_hz = 2_500_000_000
        self.test_freq_row_2_hz = 6_000_000_000
        self.test_freq_row_3_hz = 25_000_000_000

        self.assertEqual(tools.compute_gscn(frequency_hz=self.test_freq_row_1_hz, N=2_083, M=5), 6_250)
        self.assertEqual(tools.compute_gscn(frequency_hz=self.test_freq_row_2_hz, N=2_083), 9_582)
        self.assertEqual(tools.compute_gscn(frequency_hz=self.test_freq_row_3_hz, N=43), 22_299)


class TestSSREF(unittest.TestCase):
    """Test the SS_REF functions.

    """

    def test_ss_ref_var_types(self):
        """Test the SS_REF parameter types.

        """
        self.assertRaises(TypeError, tools.find_closest_ss_ref, "not int")

        self.assertRaises(TypeError, tools.compute_ss_block_frequency_position, "not int", 0, 0)
        self.assertRaises(TypeError, tools.compute_ss_block_frequency_position, 0, "not int", 0)
        self.assertRaises(TypeError, tools.compute_ss_block_frequency_position, 0, 0, "not int")

    def test_find_closest_ss_ref_computation(self):
        """Test the closest SS_REF computation with known examples.

        | Frequency Range | frequency_hz | N  | M  | GSCN | SS_REF |
        | --------------- | ------------ | -- | -- | ---- | ------ |
        | 0-3000 | 2500000000 | 2083 | 5 | 6250 | 2499850000 |
        | 3000-24250 | 6000000000 | 2083 | not used | 9582 | 5999520000 |
        | 24250-100000 | 25000000000 | 43 | not used | 22299 | 24993120000 |

        """
        self.test_freq_row_1_hz = 2_500_000_000
        self.test_freq_row_2_hz = 6_000_000_000
        self.test_freq_row_3_hz = 25_000_000_000

        self.assertEqual(tools.find_closest_ss_ref(frequency_hz=self.test_freq_row_1_hz), (2_499_850_000, 2_083, 5))
        self.assertEqual(tools.find_closest_ss_ref(frequency_hz=self.test_freq_row_2_hz), (5_999_520_000, 2_083, None))
        self.assertEqual(tools.find_closest_ss_ref(frequency_hz=self.test_freq_row_3_hz), (24_993_120_000, 43, None))

    def test_ss_block_frequency_computation(self):
        """Test the closest SS_REF computation with known examples.

        | Frequency Range | frequency_hz | N  | M  | GSCN | SS_REF |
        | --------------- | ------------ | -- | -- | ---- | ------ |
        | 0-3000 | 2500000000 | 2083 | 5 | 6250 | 2499850000 |
        | 3000-24250 | 6000000000 | 2083 | not used | 9582 | 5999520000 |
        | 24250-100000 | 25000000000 | 43 | not used | 22299 | 24993120000 |

        """
        self.test_freq_row_1_hz = 2_500_000_000
        self.test_freq_row_2_hz = 6_000_000_000
        self.test_freq_row_3_hz = 25_000_000_000

        self.assertEqual(tools.compute_ss_block_frequency_position(frequency_hz=self.test_freq_row_1_hz, N=2083, M=5), 2_499_850_000)
        self.assertEqual(tools.compute_ss_block_frequency_position(frequency_hz=self.test_freq_row_2_hz, N=2083, M=None), 5_999_520_000)
        self.assertEqual(tools.compute_ss_block_frequency_position(frequency_hz=self.test_freq_row_3_hz, N=43, M=None), 24_993_120_000)


class TestToolsLookupFunctions(unittest.TestCase):
    """Test the look up functions.

    """
    def assertDataframeEqual(self, a, b):
        try:
            pd_testing.assert_frame_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def assertSeriesEqual(self, a, b):
        try:
            pd_testing.assert_series_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        self.frequency_out_of_range = 100_000_000_000 + 1
        self.arfcn_out_of_range = 3_279_165 + 1
        self.n_rb_out_of_range = -1
        self.channel_bw_hz_1 = 40_000_000
        self.channel_bw_hz_2 = 400_000_000
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"
        self.freq_range_3 = "wrong FR"
        self.scs_hz_1 = 15_000
        self.scs_hz_2 = 0
        self.scs_hz_3 = 480_000
        self.cyclic_prefix_extended_bool_1 = False
        self.cyclic_prefix_extended_bool_2 = True

        self.assertRaises(ValueError, tools.get_table_row_from_frequency, self.frequency_out_of_range)

        self.assertRaises(ValueError, tools.get_table_row_from_arfcn, self.arfcn_out_of_range)

        self.assertRaises(ValueError, tools.get_n_prb_from_channel_raster, self.n_rb_out_of_range)

        self.assertRaises(ValueError, tools.get_delta_f_global_from_frequency, self.frequency_out_of_range)

        self.assertRaises(ValueError, tools.get_delta_f_global_from_arfcn, self.arfcn_out_of_range)

        self.assertRaises(ValueError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_2, self.freq_range_1, self.scs_hz_1, self.cyclic_prefix_extended_bool_1)
        self.assertRaises(ValueError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_1, self.freq_range_2, self.scs_hz_1, self.cyclic_prefix_extended_bool_1)
        self.assertRaises(ValueError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_1, self.freq_range_3, self.scs_hz_1, self.cyclic_prefix_extended_bool_1)
        self.assertRaises(ValueError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_1, self.freq_range_1, self.scs_hz_2, self.cyclic_prefix_extended_bool_1)

        self.assertRaises(ValueError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_1, self.freq_range_1, self.scs_hz_3, self.cyclic_prefix_extended_bool_1)
        self.assertRaises(ValueError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_1, self.freq_range_1, self.scs_hz_3, self.cyclic_prefix_extended_bool_2)
        self.assertRaises(ValueError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_2, self.freq_range_2, self.scs_hz_1, self.cyclic_prefix_extended_bool_1)
        self.assertRaises(ValueError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_2, self.freq_range_2, self.scs_hz_1, self.cyclic_prefix_extended_bool_2)

    def test_var_types(self):
        """Test the parameter types.

        """
        self.channel_bw_hz_1 = 40_000_000
        self.freq_range_1 = "FR1"
        self.scs_hz_1 = 15_000
        self.cyclic_prefix_extended_bool_1 = False

        self.assertRaises(TypeError, tools.get_table_row_from_frequency, "not int")

        self.assertRaises(TypeError, tools.get_table_row_from_arfcn, "not int")

        self.assertRaises(TypeError, tools.get_k_from_channel_raster, "not int")

        self.assertRaises(TypeError, tools.get_n_prb_from_channel_raster, "not int")

        self.assertRaises(TypeError, tools.get_delta_f_global_from_frequency, "not int")

        self.assertRaises(TypeError, tools.get_delta_f_global_from_arfcn, "not int")

        self.assertRaises(TypeError, tools.convert_frequency_to_arfcn, "not int")

        self.assertRaises(TypeError, tools.convert_arfcn_to_frequency, "not int")

        self.assertRaises(TypeError, tools.get_table_row_from_channel_bw, "not int", self.freq_range_1, self.scs_hz_1, self.cyclic_prefix_extended_bool_1)
        self.assertRaises(TypeError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_1, 0, self.scs_hz_1, self.cyclic_prefix_extended_bool_1)
        self.assertRaises(TypeError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_1, self.freq_range_1, "not int", self.cyclic_prefix_extended_bool_1)
        self.assertRaises(TypeError, tools.get_table_row_from_channel_bw, self.channel_bw_hz_1, self.freq_range_1, self.scs_hz_1, "not bool")

    def test_get_table_row_from_frequency_computation(self):
        """Test the closest SS_REF computation with known examples.

        | Frequency Range | frequency_hz | N  | M  | GSCN | SS_REF |
        | --------------- | ------------ | -- | -- | ---- | ------ |
        | 0-3000 | 2500000000 | 2083 | 5 | 6250 | 2499850000 |
        | 3000-24250 | 6000000000 | 2083 | not used | 9582 | 5999520000 |
        | 24250-100000 | 25000000000 | 43 | not used | 22299 | 24993120000 |

        """
        self.test_freq_row_1_hz = 2_500_000_000
        self.test_freq_row_2_hz = 6_000_000_000
        self.test_freq_row_3_hz = 25_000_000_000

        self.assertEqual(tools.get_table_row_from_frequency(frequency_hz=self.test_freq_row_1_hz), 0)
        self.assertEqual(tools.get_table_row_from_frequency(frequency_hz=self.test_freq_row_2_hz), 1)
        self.assertEqual(tools.get_table_row_from_frequency(frequency_hz=self.test_freq_row_3_hz), 2)

    def test_get_table_row_from_arfcn_computation(self):
        """Test the closest SS_REF computation with known examples.

        | Frequency Range | frequency_hz | N  | M  | GSCN | SS_REF |
        | --------------- | ------------ | -- | -- | ---- | ------ |
        | 0-3000 | 2500000000 | 2083 | 5 | 6250 | 2499850000 |
        | 3000-24250 | 6000000000 | 2083 | not used | 9582 | 5999520000 |
        | 24250-100000 | 25000000000 | 43 | not used | 22299 | 24993120000 |

        """
        self.test_arfcn_row_1 = 599_999
        self.test_arfcn_row_2 = 600_000
        self.test_arfcn_row_3 = 3_279_165

        self.assertEqual(tools.get_table_row_from_arfcn(arfcn=self.test_arfcn_row_1), 0)
        self.assertEqual(tools.get_table_row_from_arfcn(arfcn=self.test_arfcn_row_2), 1)
        self.assertEqual(tools.get_table_row_from_arfcn(arfcn=self.test_arfcn_row_3), 2)

    def test_get_k_from_channel_raster(self):
        """Test getting resource element index k from channel raster.
        This follows 3GPP TS 38.104 Table 5.4.4.2-1.

        |    | N_RB mod 2 = 0 | N_RB mod 2 = 1 |
        | -- | -------------- | -------------- |
        |  k |              0 |              6 |

        """
        n_rb_1 = 106
        n_rb_2 = 51

        self.assertEqual(tools.get_k_from_channel_raster(n_rb=n_rb_1), 0)
        self.assertEqual(tools.get_k_from_channel_raster(n_rb=n_rb_2), 6)

    def test_get_n_prb_from_channel_raster(self):
        """Test getting resource element index k from channel raster.
        This follows 3GPP TS 38.104 Table 5.4.4.2-1.

        |       | N_RB mod 2 = 0 | N_RB mod 2 = 1 |
        | ----- | -------------- | -------------- |
        | n_PRB |             53 |             25 |

        """
        n_rb_1 = 106
        n_rb_2 = 51

        self.assertEqual(tools.get_n_prb_from_channel_raster(n_rb=n_rb_1), 53)
        self.assertEqual(tools.get_n_prb_from_channel_raster(n_rb=n_rb_2), 25)

    def test_get_delta_f_global_from_frequency(self):
        """Test getting ΔF_Global from a frequency.

        | Range of frequencies | ΔF_Global | F_REF-Offs | N_REF-Offs |    Range of N_REF |
        | -------------------- | --------- | ---------- | ---------- | ----------------- |
        |             0 - 3000 |         5 |          0 |          0 |        0 - 599999 |
        |         3000 - 24250 |        15 |       3000 |     600000 |  600000 - 2016666 |
        |       24250 - 100000 |        60 |   24250.08 |    2016667 | 2016667 - 3279165 |

        """
        self.test_freq_row_1_hz = 2_500_000_000
        self.test_freq_row_2_hz = 6_000_000_000
        self.test_freq_row_3_hz = 25_000_000_000

        self.assertEqual(tools.get_delta_f_global_from_frequency(frequency_hz=self.test_freq_row_1_hz), int(5_000))
        self.assertEqual(tools.get_delta_f_global_from_frequency(frequency_hz=self.test_freq_row_2_hz), int(15_000))
        self.assertEqual(tools.get_delta_f_global_from_frequency(frequency_hz=self.test_freq_row_3_hz), int(60_000))

    def test_get_delta_f_global_from_arfcn(self):
        """Test getting ΔF_Global from an ARFCN.

        | Range of frequencies | ΔF_Global | F_REF-Offs | N_REF-Offs |    Range of N_REF |
        | -------------------- | --------- | ---------- | ---------- | ----------------- |
        |             0 - 3000 |         5 |          0 |          0 |        0 - 599999 |
        |         3000 - 24250 |        15 |       3000 |     600000 |  600000 - 2016666 |
        |       24250 - 100000 |        60 |   24250.08 |    2016667 | 2016667 - 3279165 |

        """
        self.test_arfcn_row_1 = 599_999
        self.test_arfcn_row_2 = 600_000
        self.test_arfcn_row_3 = 3_279_165

        self.assertEqual(tools.get_delta_f_global_from_arfcn(arfcn=self.test_arfcn_row_1), int(5_000))
        self.assertEqual(tools.get_delta_f_global_from_arfcn(arfcn=self.test_arfcn_row_2), int(15_000))
        self.assertEqual(tools.get_delta_f_global_from_arfcn(arfcn=self.test_arfcn_row_3), int(60_000))

    def test_convert_frequency_to_arfcn(self):
        """Test converting a frequency to an ARFCN.

        N_REF = (F_REF - F_REF-OFFS) / ΔF_Global + N_REF-Offs

        """
        self.test_freq_row_1_hz = 2_500_000_000

        self.assertEqual(tools.convert_frequency_to_arfcn(frequency_hz=self.test_freq_row_1_hz), 500_000)

    def test_convert_arfcn_to_frequency(self):
        """Test converting an ARFCN to a frequency.

        F_REF = F_REF-Offs + ΔF_Global(N_REF - N_REF-Offs)

        """
        self.test_arfcn_row_1 = 599_999

        self.assertEqual(tools.convert_arfcn_to_frequency(arfcn=self.test_arfcn_row_1), int(2_999_995_000))

    def test_get_table_row_from_channel_bw(self):
        """Test getting the table row based on the Channel Bandwidth.

        """
        self.channel_bw_hz_1 = 50_000_000
        self.channel_bw_hz_2 = 100_000_000
        self.channel_bw_hz_3 = 200_000_000
        self.channel_bw_hz_4 = 400_000_000
        self.channel_bw_hz_5 = 1_600_000_000
        self.channel_bw_hz_6 = 2_000_000_000
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"
        self.scs_hz_1 = 15_000
        self.scs_hz_2 = 30_000
        self.scs_hz_3 = 60_000
        self.scs_hz_4 = 120_000
        self.scs_hz_5 = 480_000
        self.scs_hz_6 = 960_000
        self.cyclic_prefix_extended_bool_1 = False
        self.cyclic_prefix_extended_bool_2 = True

        self.test_ts_38_104_table_b_5_2_1_dict_1 = {
            'FFT size': (4_096, None),
            'CP length for symbols 1-6 and 8-13 in FFT samples': (288, None),
            'EVM window length W': (144, None),
            'Ratio of W to total CP length for symbols 1-6 and 8-13 (Note) (%)': (50.0, None),
        }

        self.test_ts_38_104_table_b_5_2_2_dict_1 = {
            'FFT size': (4_096, None),
            'CP length for symbols 1-13 in FFT samples': (288, None),
            'EVM window length W': (172, None),
            'Ratio of W to total CP length for symbols 1-13 (Note) (%)': (60.0, None),
        }

        self.test_ts_38_104_table_b_5_2_3_dict_1 = {
            'FFT size': (2_048, None),
            'CP length in FFT samples': (144, None),
            'EVM window length W': (86, None),
            'Ratio of W to total CP length (Note) (%)': (60.0, None),
        }

        self.test_ts_38_104_table_b_5_2_4_dict_1 = {
            'FFT size': (2_048, None),
            'CP length in FFT samples': (512, None),
            'EVM window length W': (454, None),
            'Ratio of W to total CP length (Note) (%)': (88.7, None),
        }

        self.test_ts_38_104_table_c_5_2_1_dict_1 = {
            'FFT size': (4_096, None),
            'CP length in FFT samples': (288, None),
            'EVM window length W': (144, None),
            'Ratio of W to total CP length (Note) (%)': (50.0, None),
        }

        self.test_ts_38_104_table_c_5_2_2_dict_1 = {
            'FFT size': (4_096, None),
            'CP length in FFT samples': (288, None),
            'EVM window length W': (144, None),
            'Ratio of W to total CP length (Note) (%)': (50.0, None),
        }

        self.test_ts_38_104_table_c_5_2_2a_dict_1 = {
            'FFT size': (4_096, None),
            'CP length in FFT samples': (288, None),
            'EVM window length W': (144, None),
            'Ratio of W to total CP length (Note) (%)': (50.0, None),
        }

        self.test_ts_38_104_table_c_5_2_2b_dict_1 = {
            'FFT size': (2_048, None),
            'CP length in FFT samples': (144, None),
            'EVM window length W': (72, None),
            'Ratio of W to total CP length (Note) (%)': (50.0, None),
        }

        self.test_ts_38_104_table_c_5_2_3_dict_1 = {
            'FFT size': (4_096, None),
            'CP length in FFT samples': (1_024, None),
            'EVM window length W': (880, None),
            'Ratio of W to total CP length (Note) (%)': (85.9, None),
        }

        self.assertEqual(
            tools.get_table_row_from_channel_bw(
                channel_bw_hz=self.channel_bw_hz_1,
                freq_range=self.freq_range_1,
                scs_hz=self.scs_hz_1,
                cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1
            ),
            self.test_ts_38_104_table_b_5_2_1_dict_1)

        self.assertEqual(
            tools.get_table_row_from_channel_bw(
                channel_bw_hz=self.channel_bw_hz_2,
                freq_range=self.freq_range_1,
                scs_hz=self.scs_hz_2,
                cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1
            ),
            self.test_ts_38_104_table_b_5_2_2_dict_1)

        self.assertEqual(
            tools.get_table_row_from_channel_bw(
                channel_bw_hz=self.channel_bw_hz_2,
                freq_range=self.freq_range_1,
                scs_hz=self.scs_hz_3,
                cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1
            ),
            self.test_ts_38_104_table_b_5_2_3_dict_1)

        self.assertEqual(
            tools.get_table_row_from_channel_bw(
                channel_bw_hz=self.channel_bw_hz_2,
                freq_range=self.freq_range_1,
                scs_hz=self.scs_hz_3,
                cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_2
            ),
            self.test_ts_38_104_table_b_5_2_4_dict_1)

        self.assertEqual(
            tools.get_table_row_from_channel_bw(
                channel_bw_hz=self.channel_bw_hz_3,
                freq_range=self.freq_range_2,
                scs_hz=self.scs_hz_3,
                cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1
            ),
            self.test_ts_38_104_table_c_5_2_1_dict_1)

        self.assertEqual(
            tools.get_table_row_from_channel_bw(
                channel_bw_hz=self.channel_bw_hz_4,
                freq_range=self.freq_range_2,
                scs_hz=self.scs_hz_4,
                cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1
            ),
            self.test_ts_38_104_table_c_5_2_2_dict_1)

        self.assertEqual(
            tools.get_table_row_from_channel_bw(
                channel_bw_hz=self.channel_bw_hz_5,
                freq_range=self.freq_range_2,
                scs_hz=self.scs_hz_5,
                cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1
            ),
            self.test_ts_38_104_table_c_5_2_2a_dict_1)

        self.assertEqual(
            tools.get_table_row_from_channel_bw(
                channel_bw_hz=self.channel_bw_hz_6,
                freq_range=self.freq_range_2,
                scs_hz=self.scs_hz_6,
                cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1
            ),
            self.test_ts_38_104_table_c_5_2_2b_dict_1)

        self.assertEqual(
            tools.get_table_row_from_channel_bw(
                channel_bw_hz=self.channel_bw_hz_3,
                freq_range=self.freq_range_2,
                scs_hz=self.scs_hz_3,
                cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_2
            ),
            self.test_ts_38_104_table_c_5_2_3_dict_1)


class TestToolsVerificationFunctions(unittest.TestCase):
    """Test the verification functions.

    """

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        self.freq_band_1 = 0
        self.freq_band_2 = 78
        self.freq_band_3 = 257
        self.freq_band_4 = 1_024
        self.scs_hz_1 = 0
        self.scs_hz_2 = 30_000
        self.cbw_hz_1 = 400_000_000
        self.cbw_hz_2 = 40_000_000

        self.assertRaises(ValueError, tools.verify_scs_validity_from_freq_band, self.freq_band_1, self.scs_hz_2)
        self.assertRaises(ValueError, tools.verify_scs_validity_from_freq_band, self.freq_band_2, self.scs_hz_1)
        self.assertRaises(ValueError, tools.verify_scs_validity_from_freq_band, self.freq_band_3, self.scs_hz_1)

        self.assertRaises(ValueError, tools.verify_cbw_validity_from_freq_band, self.freq_band_1, self.cbw_hz_2)
        self.assertRaises(ValueError, tools.verify_cbw_validity_from_freq_band, self.freq_band_2, self.cbw_hz_1)
        self.assertRaises(ValueError, tools.verify_cbw_validity_from_freq_band, self.freq_band_3, self.cbw_hz_2)

    def test_var_types(self):
        """Test the parameter types.

        """
        self.freq_band = 78
        self.scs_hz = 30_000

        self.assertRaises(TypeError, tools.verify_scs_validity_from_freq_band, "not int", self.scs_hz)
        self.assertRaises(TypeError, tools.verify_scs_validity_from_freq_band, self.freq_band, "not int")

        self.assertRaises(TypeError, tools.verify_cbw_validity_from_freq_band, "not int", self.scs_hz)
        self.assertRaises(TypeError, tools.verify_cbw_validity_from_freq_band, self.freq_band, "not int")

    def test_verify_scs_validity_from_freq_band(self):
        """Test the verification of SCS validity.

        | Frequency Band |     SCS | Validity |
        | -------------- | ------- | -------- |
        |            n78 |  30 kHz |     True |
        |            n78 | 120 kHz |    False |
        |           n257 | 120 kHz |     True |
        |           n257 |  30 kHz |    False |

        """
        self.freq_band_1 = 78
        self.freq_band_2 = 257
        self.scs_hz_1 = 30_000
        self.scs_hz_2 = 120_000

        self.assertEqual(tools.verify_scs_validity_from_freq_band(freq_band=self.freq_band_1, scs_hz=self.scs_hz_1), True)
        self.assertEqual(tools.verify_scs_validity_from_freq_band(freq_band=self.freq_band_1, scs_hz=self.scs_hz_2), False)
        self.assertEqual(tools.verify_scs_validity_from_freq_band(freq_band=self.freq_band_2, scs_hz=self.scs_hz_2), True)
        self.assertEqual(tools.verify_scs_validity_from_freq_band(freq_band=self.freq_band_2, scs_hz=self.scs_hz_1), False)

    def test_verify_cbw_validity_from_freq_band(self):
        """Test the verification of CBW validity.

        | Frequency Band |     CBW | Validity |
        | -------------- | ------- | -------- |
        |            n78 |  40 MHz |     True |
        |            n78 |  45 MHz |    False |
        |           n257 | 100 MHz |     True |
        |           n257 | 800 MHz |    False |

        """
        self.freq_band_1 = 78
        self.freq_band_2 = 257
        self.cbw_hz_1 = 40_000_000
        self.cbw_hz_2 = 45_000_000
        self.cbw_hz_3 = 100_000_000
        self.cbw_hz_4 = 800_000_000

        self.assertEqual(tools.verify_cbw_validity_from_freq_band(freq_band=self.freq_band_1, cbw_hz=self.cbw_hz_1), True)
        self.assertEqual(tools.verify_cbw_validity_from_freq_band(freq_band=self.freq_band_1, cbw_hz=self.cbw_hz_2), False)
        self.assertEqual(tools.verify_cbw_validity_from_freq_band(freq_band=self.freq_band_2, cbw_hz=self.cbw_hz_3), True)
        self.assertEqual(tools.verify_cbw_validity_from_freq_band(freq_band=self.freq_band_2, cbw_hz=self.cbw_hz_4), False)


class TestToolsResourceAllocationFrequencyDomain(unittest.TestCase):
    """Test the computation functions for resource allocation in the frequency domain.

    """

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        self.rb_start = 0
        self.l_rbs = tools.N_RBS_PER_BWP - self.rb_start + 1
        self.nr_riv_1 = 0 - 1
        self.nr_riv_2 = 37949 + 1

        self.assertRaises(ValueError, tools.compute_nr_riv_from_rbs, self.rb_start, 0)
        self.assertRaises(ValueError, tools.compute_nr_riv_from_rbs, self.rb_start, self.l_rbs)

        self.assertRaises(ValueError, tables.ts_38_214_ch_5_1_2_2_2, self.rb_start, 0)
        self.assertRaises(ValueError, tables.ts_38_214_ch_5_1_2_2_2, self.rb_start, self.l_rbs)

        self.assertRaises(ValueError, tables.ts_38_214_ch_5_1_2_2_2_reverse, self.nr_riv_1)
        self.assertRaises(ValueError, tables.ts_38_214_ch_5_1_2_2_2_reverse, self.nr_riv_2)

    def test_var_types(self):
        """Test the parameter types.

        """
        self.rb_start = 0
        self.l_rbs = 106

        self.assertRaises(TypeError, tools.compute_nr_riv_from_rbs, "not int", self.l_rbs)
        self.assertRaises(TypeError, tools.compute_nr_riv_from_rbs, self.rb_start, "not int")

        self.assertRaises(TypeError, tables.ts_38_214_ch_5_1_2_2_2, "not int", self.l_rbs)
        self.assertRaises(TypeError, tables.ts_38_214_ch_5_1_2_2_2, self.rb_start, "not int")

        self.assertRaises(TypeError, tables.ts_38_214_ch_5_1_2_2_2_reverse, "not int")

    def test_compute_nr_riv_from_rbs(self):
        """Test the computation of NR RIV.

        Equations
        ---------

        if (L_RBs - 1) <= floor(N_^size_BWP/2) then:
            RIV = N_^size_BWP * (L_RBs - 1) + RB_Start
        else:
            RIV = N_^size_BWP * (N_^size_BWP - L_RBs + 1) + (N_^size_BWP - 1 - RB_Start)

        Tables
        ------
        TS_38_214_CH_5_1_2_2_2_EQ

        """
        self.rb_start_1 = 0
        self.rb_start_2 = 1
        self.l_rbs_1 = 106
        self.l_rbs_2 = int(math.floor(tools.N_RBS_PER_BWP / 2)) + 2
        self.nr_riv_1 = 28_875
        self.nr_riv_2 = 37_948

        self.assertEqual(tools.compute_nr_riv_from_rbs(rb_start=self.rb_start_1, l_rbs=self.l_rbs_1), self.nr_riv_1)
        self.assertEqual(tools.compute_nr_riv_from_rbs(rb_start=self.rb_start_2, l_rbs=self.l_rbs_2), self.nr_riv_2)

        self.assertEqual(tables.ts_38_214_ch_5_1_2_2_2(rb_start=self.rb_start_1, l_rbs=self.l_rbs_1), self.nr_riv_1)
        self.assertEqual(tables.ts_38_214_ch_5_1_2_2_2(rb_start=self.rb_start_2, l_rbs=self.l_rbs_2), self.nr_riv_2)

        self.assertEqual(tables.ts_38_214_ch_5_1_2_2_2_reverse(nr_riv=self.nr_riv_1), (self.rb_start_1, self.l_rbs_1))
        self.assertEqual(tables.ts_38_214_ch_5_1_2_2_2_reverse(nr_riv=self.nr_riv_2), (self.rb_start_2, self.l_rbs_2))

    def test_ts_38_214_ch_5_1_2_2_2(self):
        """Test the look-up table for NR RIV from RB_Start and L_RBs.
        This test should verify the integrity of the given table.

        """
        rb_start_list = [0, 275]
        l_rbs_list = [1, 274]

        for rb_start in range(rb_start_list[0], rb_start_list[1] + 1):
            for l_rbs in range(l_rbs_list[0], l_rbs_list[1] + 1):
                nr_riv = ts_dicts.TS_38_214_CH_5_1_2_2_2_EQ[str(l_rbs)][str(rb_start)][0]
                if nr_riv is not None:
                    self.assertEqual(tools.compute_nr_riv_from_rbs(rb_start=rb_start, l_rbs=l_rbs), nr_riv)
                else:
                    continue


class TestToolsResourceAllocationTimeDomain(unittest.TestCase):
    """Test the computation functions for resource allocation in the time domain.

    """

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        self.case_1 = "A"
        self.case_2 = "Z"
        self.case_3 = "B"
        self.case_4 = "C"
        self.case_5 = "D"
        self.case_6 = "E"
        self.case_7 = "F"
        self.case_8 = "G"
        self.nr_channel_center_freq_hz_1 = 3_750_000_000
        self.nr_channel_center_freq_hz_2 = 410_000_000 - 1
        self.nr_channel_center_freq_hz_3 = 7_125_000_000 + 1
        self.nr_channel_center_freq_hz_4 = 24_250_000_000 - 1
        self.nr_channel_center_freq_hz_5 = 71_000_000_000 + 1
        self.nr_channel_center_freq_hz_6 = 24_250_000_000
        self.nr_channel_center_freq_hz_7 = 52_600_000_000
        self.duplex_mode_1 = "TDD"
        self.duplex_mode_2 = "no DD"
        self.duplex_mode_3 = "FDD"
        self.shared_spectrum_channel_access_1 = False
        self.shared_spectrum_channel_access_2 = True
        self.freq_band_1 = 78
        self.freq_band_2 = 0
        self.freq_band_3 = -1
        self.freq_band_4 = 512 + 1
        self.scs_hz_1 = 30_000
        self.scs_hz_2 = 60_000

        # Duplex Mode
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_2, self.nr_channel_center_freq_hz_1, self.duplex_mode_1, self.shared_spectrum_channel_access_1)

        # NR Channel Center Frequencies
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_1, self.nr_channel_center_freq_hz_2, self.duplex_mode_1, self.shared_spectrum_channel_access_1)
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_1, self.nr_channel_center_freq_hz_3, self.duplex_mode_1, self.shared_spectrum_channel_access_1)
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_1, self.nr_channel_center_freq_hz_4, self.duplex_mode_1, self.shared_spectrum_channel_access_1)
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_1, self.nr_channel_center_freq_hz_5, self.duplex_mode_1, self.shared_spectrum_channel_access_1)
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_1, self.nr_channel_center_freq_hz_1, self.duplex_mode_2, self.shared_spectrum_channel_access_1)

        # Case A, FR1
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_1, self.nr_channel_center_freq_hz_6, self.duplex_mode_1, self.shared_spectrum_channel_access_1)

        # Case B, FR1
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_3, self.nr_channel_center_freq_hz_6, self.duplex_mode_1, self.shared_spectrum_channel_access_1)
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_3, self.nr_channel_center_freq_hz_1, self.duplex_mode_1, self.shared_spectrum_channel_access_2)

        # Case C, FR1
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_4, self.nr_channel_center_freq_hz_6, self.duplex_mode_3, self.shared_spectrum_channel_access_1)
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_4, self.nr_channel_center_freq_hz_6, self.duplex_mode_1, self.shared_spectrum_channel_access_1)

        # Case D, FR2
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_5, self.nr_channel_center_freq_hz_1, self.duplex_mode_1, self.shared_spectrum_channel_access_1)

        # Case E, FR2-1
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_6, self.nr_channel_center_freq_hz_1, self.duplex_mode_1, self.shared_spectrum_channel_access_1)
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_6, self.nr_channel_center_freq_hz_7, self.duplex_mode_1, self.shared_spectrum_channel_access_1)

        # Case F, FR2-2
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_7, self.nr_channel_center_freq_hz_1, self.duplex_mode_1, self.shared_spectrum_channel_access_1)
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_7, self.nr_channel_center_freq_hz_6, self.duplex_mode_1, self.shared_spectrum_channel_access_1)

        # Case G, FR2-2
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_8, self.nr_channel_center_freq_hz_1, self.duplex_mode_1, self.shared_spectrum_channel_access_1)
        self.assertRaises(ValueError, tools.compute_ssb_time_domain_transmission_pattern, self.case_8, self.nr_channel_center_freq_hz_6, self.duplex_mode_1, self.shared_spectrum_channel_access_1)

        self.assertRaises(ValueError, tools.get_ssb_case, self.freq_band_2, self.scs_hz_1)
        self.assertRaises(ValueError, tools.get_ssb_case, self.freq_band_3, self.scs_hz_1)
        self.assertRaises(ValueError, tools.get_ssb_case, self.freq_band_4, self.scs_hz_1)
        self.assertRaises(ValueError, tools.get_ssb_case, self.freq_band_1, self.scs_hz_2)

    def test_var_types(self):
        """Test the parameter types.

        """
        self.case = "A"
        self.nr_channel_center_freq_hz = 3_750_000_000
        self.duplex_mode = "TDD"
        self.shared_spectrum_channel_access = False
        self.freq_band_1 = 78
        self.scs_hz_1 = 30_000

        self.assertRaises(TypeError, tools.compute_ssb_time_domain_transmission_pattern, 0, self.nr_channel_center_freq_hz, self.duplex_mode, self.shared_spectrum_channel_access)
        self.assertRaises(TypeError, tools.compute_ssb_time_domain_transmission_pattern, self.case, "not int", self.duplex_mode, self.shared_spectrum_channel_access)
        self.assertRaises(TypeError, tools.compute_ssb_time_domain_transmission_pattern, self.case, self.nr_channel_center_freq_hz, 0, self.shared_spectrum_channel_access)
        self.assertRaises(TypeError, tools.compute_ssb_time_domain_transmission_pattern, self.case, self.nr_channel_center_freq_hz, self.duplex_mode, "not bool")

        self.assertRaises(TypeError, tools.get_ssb_case, "not int", self.scs_hz_1)
        self.assertRaises(TypeError, tools.get_ssb_case, self.freq_band_1, "not int")

    def test_compute_ssb_time_domain_transmission_pattern(self):
        """Test computing the OFDM starting symbols of the candidate SSBs according to 3GPP TS 38.213 4.1.

        - Case A: 15 kHz, s = s_params + 14*n = {2, 8} + 14*n
        - Case B: 30 kHz, s = s_params + 14*n = {4, 8, 16, 20} + 28*n
        - Case C: 30 kHz, s = s_params + 14*n = {2, 8} + 14*n
        - Case D: 120 kHz, s = s_params + 14*n = {4, 8, 16, 20} + 28*n
        - Case E: 240 kHz, s = s_params + 14*n = {8, 12, 16, 20, 32, 36, 40, 44} + 56*n
        - Case F: 480 kHz, s = s_params + 14*n = {2, 9} + 14*n
        - Case G: 960 kHz, s = s_params + 14*n = {2, 9} + 14*n

        """
        self.case_1 = "A"
        self.case_2 = "B"
        self.case_3 = "C"
        self.case_4 = "D"
        self.case_5 = "E"
        self.case_6 = "F"
        self.case_7 = "G"

        self.center_freq_1 = 410_000_000
        self.center_freq_2 = 2_400_000_000
        self.center_freq_3 = 3_750_000_000
        self.center_freq_4 = 24_250_000_000
        self.center_freq_5 = 52_600_000_000

        self.duplex_mode_1 = "FDD"
        self.duplex_mode_2 = "TDD"

        self.shared_spectrum_channel_access_1 = False
        self.shared_spectrum_channel_access_2 = True

        self.case_a_1 = ((2, 8, 16, 22), 4)
        self.case_a_2 = ((2, 8, 16, 22, 30, 36, 44, 50), 8)
        self.case_a_3 = ((2, 8, 16, 22, 30, 36, 44, 50, 58, 64), 0)
        self.case_b_1 = ((4, 8, 16, 20), 4)
        self.case_b_2 = ((4, 8, 16, 20, 32, 36, 44, 48), 8)
        self.case_c_1 = ((2, 8, 16, 22), 4)
        self.case_c_2 = ((2, 8, 16, 22, 30, 36, 44, 50), 8)
        self.case_c_3 = ((2, 8, 16, 22, 30, 36, 44, 50, 58, 64, 72, 78, 86, 92, 100, 106, 114, 120, 128, 134), 0)
        self.case_c_4 = ((2, 8, 16, 22), 4)
        self.case_c_5 = ((2, 8, 16, 22, 30, 36, 44, 50, 58, 64, 72, 78, 86, 92, 100, 106, 114, 120, 128, 134), 0)
        self.case_c_6 = ((2, 8, 16, 22, 30, 36, 44, 50), 8)
        self.case_c_7 = ((2, 8, 16, 22, 30, 36, 44, 50), 8)
        self.case_c_8 = ((2, 8, 16, 22, 30, 36, 44, 50, 58, 64, 72, 78, 86, 92, 100, 106, 114, 120, 128, 134), 0)
        self.case_d_1 = ((4, 8, 16, 20, 32, 36, 44, 48, 60, 64, 72, 76, 88, 92, 100, 104, 144, 148, 156, 160, 172, 176, 184, 188, 200, 204, 212, 216, 228, 232, 240, 244, 284, 288, 296, 300, 312, 316, 324, 328, 340, 344, 352, 356, 368, 372, 380, 384, 424, 428, 436, 440, 452, 456, 464, 468, 480, 484, 492, 496, 508, 512, 520, 524), 64)
        self.case_e_1 = ((8, 12, 16, 20, 32, 36, 40, 44, 64, 68, 72, 76, 88, 92, 96, 100, 120, 124, 128, 132, 144, 148, 152, 156, 176, 180, 184, 188, 200, 204, 208, 212, 288, 292, 296, 300, 312, 316, 320, 324, 344, 348, 352, 356, 368, 372, 376, 380, 400, 404, 408, 412, 424, 428, 432, 436, 456, 460, 464, 468, 480, 484, 488, 492), 64)
        self.case_f_1 = ((2, 9, 16, 23, 30, 37, 44, 51, 58, 65, 72, 79, 86, 93, 100, 107, 114, 121, 128, 135, 142, 149, 156, 163, 170, 177, 184, 191, 198, 205, 212, 219, 226, 233, 240, 247, 254, 261, 268, 275, 282, 289, 296, 303, 310, 317, 324, 331, 338, 345, 352, 359, 366, 373, 380, 387, 394, 401, 408, 415, 422, 429, 436, 443), 64)
        self.case_g_1 = ((2, 9, 16, 23, 30, 37, 44, 51, 58, 65, 72, 79, 86, 93, 100, 107, 114, 121, 128, 135, 142, 149, 156, 163, 170, 177, 184, 191, 198, 205, 212, 219, 226, 233, 240, 247, 254, 261, 268, 275, 282, 289, 296, 303, 310, 317, 324, 331, 338, 345, 352, 359, 366, 373, 380, 387, 394, 401, 408, 415, 422, 429, 436, 443), 64)

        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_1, nr_channel_center_freq_hz=self.center_freq_1, duplex_mode=self.duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_a_1)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_1, nr_channel_center_freq_hz=self.center_freq_3, duplex_mode=self.duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_a_2)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_1, nr_channel_center_freq_hz=self.center_freq_1, duplex_mode=self.duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_2), self.case_a_3)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_2, nr_channel_center_freq_hz=self.center_freq_1, duplex_mode=self.duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_b_1)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_2, nr_channel_center_freq_hz=self.center_freq_3, duplex_mode=self.duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_b_2)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_3, nr_channel_center_freq_hz=self.center_freq_1, duplex_mode=self.duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_c_1)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_3, nr_channel_center_freq_hz=self.center_freq_3, duplex_mode=self.duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_c_2)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_3, nr_channel_center_freq_hz=self.center_freq_1, duplex_mode=self.duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_2), self.case_c_3)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_3, nr_channel_center_freq_hz=self.center_freq_1, duplex_mode=self.duplex_mode_2, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_c_4)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_3, nr_channel_center_freq_hz=self.center_freq_1, duplex_mode=self.duplex_mode_2, shared_spectrum_channel_access=self.shared_spectrum_channel_access_2), self.case_c_5)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_3, nr_channel_center_freq_hz=self.center_freq_2, duplex_mode=self.duplex_mode_2, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_c_6)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_3, nr_channel_center_freq_hz=self.center_freq_3, duplex_mode=self.duplex_mode_2, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_c_7)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_3, nr_channel_center_freq_hz=self.center_freq_1, duplex_mode=self.duplex_mode_2, shared_spectrum_channel_access=self.shared_spectrum_channel_access_2), self.case_c_8)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_4, nr_channel_center_freq_hz=self.center_freq_4, duplex_mode=self.duplex_mode_2, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_d_1)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_5, nr_channel_center_freq_hz=self.center_freq_4, duplex_mode=self.duplex_mode_2, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_e_1)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_6, nr_channel_center_freq_hz=self.center_freq_5, duplex_mode=self.duplex_mode_2, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_f_1)
        self.assertEqual(tools.compute_ssb_time_domain_transmission_pattern(case=self.case_7, nr_channel_center_freq_hz=self.center_freq_5, duplex_mode=self.duplex_mode_2, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1), self.case_g_1)

    def test_get_ssb_case(self):
        """Test getting the SSB burst pattern case from the Frequency Band and the Subcarrier Spacing.
        This refers to 3GPP TS 38.213 ch. 4.1 for all Subcarrier Spacing values except 30 kHz, which is linked to both Case B and C.
        In that case, this function refers to TS_38_104_TABLE_5_4_3_3_1.

        SSB Cases
        ---------
        - 15000 : 'A', example band: n76
        - 30000 : ['B','C'], example bands: n66 and n78
        - 120000 : 'D', example band: n257
        - 240000 : 'E', example band: n257
        - 480000 : 'F', example band: n263
        - 960000 : 'G', example band: n263

        """
        self.freq_band_1 = 76
        self.freq_band_2 = 66
        self.freq_band_3 = 78
        self.freq_band_4 = 257
        self.freq_band_5 = 263

        self.scs_hz_1 = 15_000
        self.scs_hz_2 = 30_000
        self.scs_hz_3 = 120_000
        self.scs_hz_4 = 240_000
        self.scs_hz_5 = 480_000
        self.scs_hz_6 = 960_000

        self.case_1 = "A"
        self.case_2 = "B"
        self.case_3 = "C"
        self.case_4 = "D"
        self.case_5 = "E"
        self.case_6 = "F"
        self.case_7 = "G"

        self.assertEqual(tools.get_ssb_case(freq_band=self.freq_band_1, scs_hz=self.scs_hz_1), self.case_1)
        self.assertEqual(tools.get_ssb_case(freq_band=self.freq_band_2, scs_hz=self.scs_hz_2), self.case_2)
        self.assertEqual(tools.get_ssb_case(freq_band=self.freq_band_3, scs_hz=self.scs_hz_2), self.case_3)
        self.assertEqual(tools.get_ssb_case(freq_band=self.freq_band_4, scs_hz=self.scs_hz_3), self.case_4)
        self.assertEqual(tools.get_ssb_case(freq_band=self.freq_band_4, scs_hz=self.scs_hz_4), self.case_5)
        self.assertEqual(tools.get_ssb_case(freq_band=self.freq_band_5, scs_hz=self.scs_hz_5), self.case_6)
        self.assertEqual(tools.get_ssb_case(freq_band=self.freq_band_5, scs_hz=self.scs_hz_6), self.case_7)


class TestGeneratorFunctions(unittest.TestCase):
    """Test the configuration generator functions.

    """

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"
        self.freq_range_3 = "no FR"
        self.duplex_mode_1 = "FDD"
        self.duplex_mode_2 = "TDD"
        self.duplex_mode_3 = "no DD"
        self.delta_f_ra_hz_1 = 30_000
        self.delta_f_ra_hz_2 = 120_000
        self.delta_f_ra_hz_3 = 240_000

        self.assertRaises(KeyError, generator.create_prach_occasions_absolute_occupied_symbols, self.freq_range_3, self.duplex_mode_1, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, generator.create_prach_occasions_absolute_occupied_symbols, self.freq_range_1, self.duplex_mode_3, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, generator.create_prach_occasions_absolute_occupied_symbols, self.freq_range_1, self.duplex_mode_1, self.delta_f_ra_hz_3)

        self.assertRaises(ValueError, generator.create_prach_occasions_absolute_occupied_symbols, self.freq_range_2, self.duplex_mode_1, self.delta_f_ra_hz_2)

        self.assertRaises(ValueError, generator.create_prach_occasions_absolute_occupied_symbols, self.freq_range_2, self.duplex_mode_2, self.delta_f_ra_hz_1)

        self.assertRaises(ValueError, generator.create_ssb_time_domain_occupied_symbols, 'wrong SSB case', 3_750_000_000, 'TDD', False)
        self.assertRaises(ValueError, generator.create_ssb_time_domain_occupied_symbols, 'C', 1_000, 'TDD', False)
        self.assertRaises(ValueError, generator.create_ssb_time_domain_occupied_symbols, 'C', 3_750_000_000, 'wrong duplex mode', False)

    def test_var_types(self):
        """Test the parameter types.

        """
        self.test_dict = {"key": "value"}
        self.freq_range_1 = "FR1"
        self.duplex_mode_1 = "FDD"
        self.delta_f_ra_hz_1 = 30_000

        self.assertRaises(TypeError, generator.keys_exists, "not dict", "")
        self.assertRaises(AttributeError, generator.keys_exists, self.test_dict, )

        self.assertRaises(TypeError, generator.get_keys, "not dict")

        self.assertRaises(TypeError, generator.create_prach_occasions_absolute_occupied_symbols, 0, self.duplex_mode_1, self.delta_f_ra_hz_1)
        self.assertRaises(TypeError, generator.create_prach_occasions_absolute_occupied_symbols, self.freq_range_1, 0, self.delta_f_ra_hz_1)
        self.assertRaises(TypeError, generator.create_prach_occasions_absolute_occupied_symbols, self.freq_range_1, self.duplex_mode_1, "not int")

        self.assertRaises(TypeError, generator.create_ssb_time_domain_occupied_symbols, 0, 3_750_000_000, 'TDD', False)
        self.assertRaises(TypeError, generator.create_ssb_time_domain_occupied_symbols, 'C', 'not int', 'TDD', False)
        self.assertRaises(TypeError, generator.create_ssb_time_domain_occupied_symbols, 'C', 3_750_000_000, 0, False)
        self.assertRaises(TypeError, generator.create_ssb_time_domain_occupied_symbols, 'C', 3_750_000_000, 'TDD', 'not bool')

    def test_keys_exists(self):
        """Test the key checking function.

        """
        self.test_dict = {"key": "value"}

        self.assertEqual(generator.keys_exists(self.test_dict, "key"), True)
        self.assertEqual(generator.keys_exists(self.test_dict, "not key"), False)

    def test_get_keys(self):
        """Test the key retrieval function.

        """
        self.test_dict_1 = {"key": "value"}
        self.test_dict_2 = {
            "key1": {
                "key2": {
                    "key3": {
                        1: "value"
                    }
                }
            },
            "key4": 0,
            1: 0
        }

        self.assertEqual(generator.get_keys(self.test_dict_1), ["key"])
        self.assertEqual(generator.get_keys(self.test_dict_2), ["key1", "key1/key2", "key1/key2/key3", "key1/key2/key3/1", "key4", 1])

    @pytest.mark.slow
    def test_create_prach_occasions_absolute_occupied_symbols(self):
        """Test creating absolute starting symbols, PRACH duration, and absolute occupied symbols of the PRACH occasions.
        Use 3GPP TS 38.211 Tables 6.3.3.2-2 (FR1 FDD), 6.3.3.2-3 (FR1 TDD), and 6.3.3.2-4 (FR2).

        6.3.3.2-2 (FR1 FDD) case 1:
        ---------------------------
        prach_conf_idx=98, freq_range="FR1", duplex_mode="FDD", delta_f_ra_hz=30000:
            subframe/slot number:               4
            occasions absolute:                 (126, 128, 130, 132, 134, 136)
            n_dur_ra:                           2
            occasions all occupied symbols:     (126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137)

        6.3.3.2-2 (FR1 FDD) case 2:
        ---------------------------
        prach_conf_idx=2, freq_range="FR1", duplex_mode="FDD", delta_f_ra_hz=5000:
            subframe/slot number:               7
            occasions absolute:                 (98,)
            n_dur_ra:                           0
            occasions all occupied symbols:     (98,)

        6.3.3.2-3 (FR1 TDD) case 1:
        ---------------------------
        prach_conf_idx=98, freq_range="FR1", duplex_mode="TDD", delta_f_ra_hz=30000:
            subframe/slot number:               9
            occasions absolute:                 (266, 270, 274)
            n_dur_ra:                           4
            occasions all occupied symbols:     (266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277)

        6.3.3.2-3 (FR1 TDD) case 2:
        ---------------------------
        prach_conf_idx=2, freq_range="FR1", duplex_mode="TDD", delta_f_ra_hz=5000:
            subframe/slot number:               9
            occasions absolute:                 (126,)
            n_dur_ra:                           0
            occasions all occupied symbols:     (126,)

        6.3.3.2-4 (FR2 TDD) case 1:
        ---------------------------
        prach_conf_idx=98, freq_range="FR2", duplex_mode="TDD", delta_f_ra_hz=120000:
            subframe/slot number:               [9, 19, 29, 39]
            occasions absolute:                 (260, 262, 264, 274, 276, 278, 540, 542, 544, 554, 556, 558, 820, 822, 824, 834, 836, 838, 1100, 1102, 1104, 1114, 1116, 1118)
            n_dur_ra:                           2
            occasions all occupied symbols:     (260, 261, 262, 263, 264, 265, 274, 275, 276, 277, 278, 279, 540, 541, 542, 543, 544, 545, 554, 555, 556, 557, 558, 559, 820, 821, 822, 823, 824, 825, 834, 835, 836, 837, 838, 839, 1100, 1101, 1102, 1103, 1104, 1105, 1114, 1115, 1116, 1117, 1118, 1119)

        """
        self.prach_conf_idx_1 = 98
        self.prach_conf_idx_2 = 2
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"
        self.duplex_mode_1 = "FDD"
        self.duplex_mode_2 = "TDD"
        self.delta_f_ra_hz_1 = 30_000
        self.delta_f_ra_hz_2 = 5_000
        self.delta_f_ra_hz_3 = 120_000

        self.rach_occasion_starting_symbols_absolute_1 = (126, 128, 130, 132, 134, 136)
        self.rach_occasion_starting_symbols_absolute_2 = (98,)
        self.rach_occasion_starting_symbols_absolute_3 = (266, 270, 274)
        self.rach_occasion_starting_symbols_absolute_4 = (126,)
        self.rach_occasion_starting_symbols_absolute_5 = (260, 262, 264, 274, 276, 278, 540, 542, 544, 554, 556, 558, 820, 822, 824, 834, 836, 838, 1100, 1102, 1104, 1114, 1116, 1118)

        self.rach_occasion_all_occupied_symbols_absolute_1 = (126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137)
        self.rach_occasion_all_occupied_symbols_absolute_2 = (98,)
        self.rach_occasion_all_occupied_symbols_absolute_3 = (266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277)
        self.rach_occasion_all_occupied_symbols_absolute_4 = (126,)
        self.rach_occasion_all_occupied_symbols_absolute_5 = (260, 261, 262, 263, 264, 265, 274, 275, 276, 277, 278, 279, 540, 541, 542, 543, 544, 545, 554, 555, 556, 557, 558, 559, 820, 821, 822, 823, 824, 825, 834, 835, 836, 837, 838, 839, 1100, 1101, 1102, 1103, 1104, 1105, 1114, 1115, 1116, 1117, 1118, 1119)

        self.prach_occasion_occupied_symbols_df_1 = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=self.freq_range_1, duplex_mode=self.duplex_mode_1, delta_f_ra_hz=self.delta_f_ra_hz_1)
        self.prach_occasion_occupied_symbols_df_2 = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=self.freq_range_1, duplex_mode=self.duplex_mode_1, delta_f_ra_hz=self.delta_f_ra_hz_2)
        self.prach_occasion_occupied_symbols_df_3 = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=self.freq_range_1, duplex_mode=self.duplex_mode_2, delta_f_ra_hz=self.delta_f_ra_hz_1)
        self.prach_occasion_occupied_symbols_df_4 = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=self.freq_range_1, duplex_mode=self.duplex_mode_2, delta_f_ra_hz=self.delta_f_ra_hz_2)
        self.prach_occasion_occupied_symbols_df_5 = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=self.freq_range_2, duplex_mode=self.duplex_mode_2, delta_f_ra_hz=self.delta_f_ra_hz_3)

        self.assertEqual(self.prach_occasion_occupied_symbols_df_1['PRACH occasion starting symbols absolute'][self.prach_conf_idx_1], self.rach_occasion_starting_symbols_absolute_1)
        self.assertEqual(self.prach_occasion_occupied_symbols_df_2['PRACH occasion starting symbols absolute'][self.prach_conf_idx_2], self.rach_occasion_starting_symbols_absolute_2)
        self.assertEqual(self.prach_occasion_occupied_symbols_df_3['PRACH occasion starting symbols absolute'][self.prach_conf_idx_1], self.rach_occasion_starting_symbols_absolute_3)
        self.assertEqual(self.prach_occasion_occupied_symbols_df_4['PRACH occasion starting symbols absolute'][self.prach_conf_idx_2], self.rach_occasion_starting_symbols_absolute_4)
        self.assertEqual(self.prach_occasion_occupied_symbols_df_5['PRACH occasion starting symbols absolute'][self.prach_conf_idx_1], self.rach_occasion_starting_symbols_absolute_5)

        self.assertEqual(self.prach_occasion_occupied_symbols_df_1['PRACH occasions all occupied symbols'][self.prach_conf_idx_1], self.rach_occasion_all_occupied_symbols_absolute_1)
        self.assertEqual(self.prach_occasion_occupied_symbols_df_2['PRACH occasions all occupied symbols'][self.prach_conf_idx_2], self.rach_occasion_all_occupied_symbols_absolute_2)
        self.assertEqual(self.prach_occasion_occupied_symbols_df_3['PRACH occasions all occupied symbols'][self.prach_conf_idx_1], self.rach_occasion_all_occupied_symbols_absolute_3)
        self.assertEqual(self.prach_occasion_occupied_symbols_df_4['PRACH occasions all occupied symbols'][self.prach_conf_idx_2], self.rach_occasion_all_occupied_symbols_absolute_4)
        self.assertEqual(self.prach_occasion_occupied_symbols_df_5['PRACH occasions all occupied symbols'][self.prach_conf_idx_1], self.rach_occasion_all_occupied_symbols_absolute_5)


class TestCreateConfig(unittest.TestCase):
    """Test the configuration creation class.

    """
    def assertDataframeEqual(self, a, b):
        try:
            pd_testing.assert_frame_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def assertSeriesEqual(self, a, b):
        try:
            pd_testing.assert_series_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def setUp(self):

        self.nr_freq_band_1 = 78
        self.nr_cbw_hz_1 = int(40_000_000)
        self.nr_scs_hz_1 = int(30_000)
        self.nr_duplex_mode_1 = "TDD"
        self.nr_channel_center_freq_hz_1 = int(3_619_200_000)
        self.static_config_filename_1 = os.path.abspath(
            os.path.join(
                os.getcwd(), "testfiles", "test_static_conf_1.json"
            )
        )
        self.config_filename_1 = "TEST_5g_conf.json"

        self.nr_freq_band_2 = 0
        self.nr_cbw_hz_2 = 0
        self.nr_scs_hz_2 = 0
        self.nr_duplex_mode_2 = "not TDD"
        self.nr_channel_center_freq_hz_2 = int(3_619_200_000)
        self.static_config_filename_2 = os.path.abspath(
            os.path.join(
                os.getcwd(), "testfiles", "test_static_conf_1.json"
            )
        )
        self.config_filename_2 = "TEST_5g_conf.json"

        self.nr_freq_band_3 = 261
        self.nr_cbw_hz_3 = int(100_000_000)
        self.nr_scs_hz_3 = int(120_000)
        self.nr_duplex_mode_3 = "TDD"
        self.nr_channel_center_freq_hz_3 = int(27_524_520_000)
        self.static_config_filename_3 = os.path.abspath(
            os.path.join(
                os.getcwd(), "testfiles", "test_static_conf_1.json"
            )
        )
        self.config_filename_3 = "TEST_5g_conf.json"

        # Test for valid FR1 configuration with b210
        self.config_1 = generator.CreateConfig(
            nr_freq_band=self.nr_freq_band_1,
            nr_cbw_hz=self.nr_cbw_hz_1,
            nr_scs_hz=self.nr_scs_hz_1,
            nr_duplex_mode=self.nr_duplex_mode_1,
            nr_channel_center_freq_hz=self.nr_channel_center_freq_hz_1,
            static_config_filename=self.static_config_filename_1,
            config_filename=self.config_filename_1,
            sdr="b210"
        )

        # Test for valid FR1 configuration with x300
        self.config_2 = generator.CreateConfig(
            nr_freq_band=self.nr_freq_band_1,
            nr_cbw_hz=self.nr_cbw_hz_1,
            nr_scs_hz=self.nr_scs_hz_1,
            nr_duplex_mode=self.nr_duplex_mode_1,
            nr_channel_center_freq_hz=self.nr_channel_center_freq_hz_1,
            static_config_filename=self.static_config_filename_1,
            config_filename=self.config_filename_1,
            sdr="x300"
        )

        # Test for non-existent 5G NR frequency band
        self.config_3 = generator.CreateConfig(
            nr_freq_band=513,
            nr_cbw_hz=self.nr_cbw_hz_1,
            nr_scs_hz=self.nr_scs_hz_1,
            nr_duplex_mode=self.nr_duplex_mode_1,
            nr_channel_center_freq_hz=self.nr_channel_center_freq_hz_1,
            static_config_filename=self.static_config_filename_1,
            config_filename=self.config_filename_1,
            sdr="b210"
        )

        # Test for non-existent 5G NR channel bandwidth
        self.config_4 = generator.CreateConfig(
            nr_freq_band=self.nr_freq_band_1,
            nr_cbw_hz=0,
            nr_scs_hz=self.nr_scs_hz_1,
            nr_duplex_mode=self.nr_duplex_mode_1,
            nr_channel_center_freq_hz=self.nr_channel_center_freq_hz_1,
            static_config_filename=self.static_config_filename_1,
            config_filename=self.config_filename_1,
            sdr="b210"
        )

        # Test for non-existent 5G NR subcarrier spacing
        self.config_5 = generator.CreateConfig(
            nr_freq_band=self.nr_freq_band_1,
            nr_cbw_hz=self.nr_cbw_hz_1,
            nr_scs_hz=int(120_000),
            nr_duplex_mode=self.nr_duplex_mode_1,
            nr_channel_center_freq_hz=self.nr_channel_center_freq_hz_1,
            static_config_filename=self.static_config_filename_1,
            config_filename=self.config_filename_1,
            sdr="b210"
        )

        # Test for different valid FR1 configuration with varied channel center frequency
        self.config_7 = generator.CreateConfig(
            nr_freq_band=self.nr_freq_band_1,
            nr_cbw_hz=self.nr_cbw_hz_1,
            nr_scs_hz=self.nr_scs_hz_1,
            nr_duplex_mode=self.nr_duplex_mode_1,
            nr_channel_center_freq_hz=int(2_400_000_000),
            static_config_filename=self.static_config_filename_1,
            config_filename=self.config_filename_1,
            sdr="b210"
        )

        # Test for valid FR2 configuration
        self.config_8 = generator.CreateConfig(
            nr_freq_band=self.nr_freq_band_3,
            nr_cbw_hz=self.nr_cbw_hz_3,
            nr_scs_hz=self.nr_scs_hz_3,
            nr_duplex_mode=self.nr_duplex_mode_3,
            nr_channel_center_freq_hz=self.nr_channel_center_freq_hz_3,
            static_config_filename=self.static_config_filename_3,
            config_filename=self.config_filename_3,
            sdr="b210"
        )

    def tearDown(self):
        self.test_config_created_filename = os.path.abspath(
            os.path.join(
                os.getcwd(), "test_config_created"
            )
        )
        test_conf_filename_list = [
            self.config_filename_1,
            self.config_filename_2,
            self.config_filename_3,
            self.test_config_created_filename
        ]
        for filename in test_conf_filename_list:
            if os.path.exists(filename):
                os.remove(filename)

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        self.assertRaises(ValueError, self.config_3.create_dynamic_config)
        self.assertRaises(ValueError, self.config_4.create_dynamic_config)
        self.assertRaises(ValueError, self.config_5.create_dynamic_config)

    def test_var_types(self):
        """Test the parameter types.

        """
        self.assertRaises(TypeError, self.config_1.compute_absolute_frequency_ssb, "not int")

        self.assertRaises(TypeError, self.config_1.compute_absolute_frequency_point_a, "not int", 0, 0)
        self.assertRaises(TypeError, self.config_1.compute_absolute_frequency_point_a, 0, "not int", 0)
        self.assertRaises(TypeError, self.config_1.compute_absolute_frequency_point_a, 0, 0, "not int")

        self.assertRaises(TypeError, self.config_1.convert_dict_to_oai5g_config_string, "not dict")

        self.assertRaises(TypeError, self.config_1.create_openairinterface5g_config_file, "string", 0)
        self.assertRaises(TypeError, self.config_1.create_openairinterface5g_config_file, 0, "string")

        self.assertRaises(TypeError, self.config_1.map_ssb_and_valid_prach_occasions, "not pandas DataFrame", tuple())
        self.assertRaises(TypeError, self.config_1.map_ssb_and_valid_prach_occasions, pd.DataFrame(), "not tuple")

    def test_compute_absolute_frequency_ssb(self):
        """Test computing the absoluteFrequencySSB as ARFCN.

        """
        self.freq_hz = int(3_619_200_000)

        self.assertEqual(self.config_1.compute_absolute_frequency_ssb(frequency_hz=self.freq_hz), 641_280)

    def test_compute_absolute_frequency_point_a(self):
        """Test computing the absoluteFrequencyPointA as ARFCN and in Hz.
        Also tests computing k_SSB and offsetToPointA in RBs.

        """
        self.ssb_ref = int(3_619_200_000)
        self.scs_raster_hz = int(30_000)
        self.usable_band_lower_limit_hz = int((3_599.2 + 0.905) * 1_000_000)

        self.absolute_frequency_point_a_arfcn = 640_008
        self.absolute_frequency_point_a_hz = int(3_600_120_000)
        self.k_ssb = 0
        self.offset_to_point_a_n_rbs = 43

        self.freq_point_a_tuple = (
            self.absolute_frequency_point_a_arfcn, self.absolute_frequency_point_a_hz, self.k_ssb, self.offset_to_point_a_n_rbs
        )

        self.assertEqual(self.config_1.compute_absolute_frequency_point_a(ssb_ref_hz=self.ssb_ref, scs_raster_hz=self.scs_raster_hz, usable_band_lower_limit_hz=self.usable_band_lower_limit_hz), self.freq_point_a_tuple)

    def test_read_static_config(self):
        """Test reading the static configuration data.

        """
        self.assertEqual(self.config_1.read_static_config(), True)

    def test_create_dynamic_config(self):
        """Test creating the dynamic configuration data.

        """
        self.assertEqual(self.config_1.create_dynamic_config(), True)
        self.assertEqual(self.config_2.create_dynamic_config(), True)
        self.assertEqual(self.config_8.create_dynamic_config(), True)

    def test_read_dynamic_config(self):
        """Test reading the dynamic configuration from dict to general config dict.

        """
        self.config_1.read_static_config()
        self.config_1.create_dynamic_config()
        self.assertEqual(self.config_1.read_dynamic_config(), True)

    def test_convert_dict_to_oai5g_config_string(self):
        """Test converting a dict to an OpenAirInterface5G-compatible config string.

        """
        self.maxDiff = None

        # Test Config 1: B210

        self.config_1.read_static_config()
        self.config_1.create_dynamic_config()
        self.config_1.read_dynamic_config()
        self.config_1.correct_quotation_marks()
        self.conf_1_dict_str = self.config_1.convert_dict_to_oai5g_config_string(
            self.config_1.config_dict
        )
        self.test_config_1_str = ""

        # The test file derives from the following default configuration by OAI5G:
        # https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/2024.w30/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf
        # If an AssertionError occurs, add `self.maxDiff=None` before `self.assertEqual(self.conf_1_dict_str, self.test_config_1_str)` to receive a Diff output.
        self.test_config_1_file = os.path.abspath(
            os.path.join(
                os.getcwd(), "testfiles", "test_config_1"
            )
        )
        with open(self.test_config_1_file, 'r') as test_conf_file:
            self.test_config_1_str = test_conf_file.read()
        self.assertEqual(self.conf_1_dict_str, self.test_config_1_str)

        # Test Config 2: X300
        # This also checks for an alternative number contention-based preambles per SSB and RACH Occasion.

        self.config_2.read_static_config()
        self.config_2.create_dynamic_config()
        self.config_2.read_dynamic_config()
        self.config_2.correct_quotation_marks()
        self.config_2.config_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"] = 6
        self.config_2.config_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB"] = 15
        self.conf_2_dict_str = self.config_2.convert_dict_to_oai5g_config_string(
            self.config_2.config_dict
        )
        self.test_config_2_str = ""

        # The test file derives from the following default configuration by OAI5G:
        # https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/2024.w30/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf
        # The following lines are added:
        #     min_rxtxtime = 6;
        # If an AssertionError occurs, add `self.maxDiff=None` before `self.assertEqual(self.conf_2_dict_str, self.test_config_2_str)` to receive a Diff output.
        self.test_config_2_file = os.path.abspath(
            os.path.join(
                os.getcwd(), "testfiles", "test_config_2"
            )
        )
        with open(self.test_config_2_file, 'r') as test_conf_file:
            self.test_config_2_str = test_conf_file.read()
        self.assertEqual(self.conf_2_dict_str, self.test_config_2_str)

    def test_save_config_to_json(self):
        """Test saving the config to a JSON file.

        """
        self.assertEqual(self.config_1.save_config_to_json(), True)

    def test_create_openairinterface5g_config_file(self):
        """Test creating an OpenAirInterface5G config file.

        """
        self.config_1.read_static_config()
        self.config_1.create_dynamic_config()
        self.config_1.read_dynamic_config()
        self.config_1.correct_quotation_marks()
        self.conf_1_dict_str = self.config_1.convert_dict_to_oai5g_config_string(
            self.config_1.config_dict
        )
        self.test_filename = "test_config_created"

        self.assertEqual(self.config_1.create_openairinterface5g_config_file(conf_str=self.conf_1_dict_str, filename=self.test_filename), True)

    def test_map_ssb_and_valid_prach_occasions(self):
        """Test mapping SSB resources and valid PRACH occasions.

        DataFrames
        ----------

        - ssb_periodicityServingCell = 20 ms
        - n_tx_ssb_beams = 1
        - msg1_SubcarrierSpacing = 30 kHz
        - prach_ConfigurationIndex = 98
        - prach_msg1_FDM = 1

        | Index |  266 | 270 | 274 | 546 | 550 | 554 |
        | ----- | ---- | --- | --- | --- | --- | --- |
        | 0     | SSB0 | NaN | NaN | NaN | NaN | NaN |

        - ssb_periodicityServingCell = 20 ms
        - n_tx_ssb_beams = 8
        - msg1_SubcarrierSpacing = 30 kHz
        - prach_ConfigurationIndex = 98
        - prach_msg1_FDM = 2

        | Index |  266 |  270 | 274 |  546 |  550 | 554 |
        | ----- | ---- | ---- | --- | ---- | ---- | --- |
        | 0     | SSB0 | SSB2 | NaN | SSB4 | SSB6 | NaN |
        | 1     | SSB1 | SSB3 | NaN | SSB5 | SSB7 | NaN |

        - ssb_periodicityServingCell = 20 ms
        - n_tx_ssb_beams = 8
        - msg1_SubcarrierSpacing = 30 kHz
        - prach_ConfigurationIndex = 98
        - prach_msg1_FDM = 1

        None, since not enough PRACH occasions available.

        """
        self.delta_f_ra_hz_1 = 30_000
        self.shared_spectrum_channel_access_1 = False
        self.ssb_case_1 = 'C'
        self.columns_lst_1 = [266, 270, 274, 546, 550, 554]

        # Test dataframes

        self.ssb_beams_mapped_to_prach_resource_grid_df_1 = pd.DataFrame(
            np.nan, index=[0], columns=self.columns_lst_1
        ).astype(object)
        self.ssb_beams_mapped_to_prach_resource_grid_df_1.at[0, 266] = "SSB0"

        self.ssb_beams_mapped_to_prach_resource_grid_df_2 = pd.DataFrame(
            np.nan, index=[0], columns=self.columns_lst_1
        ).astype(object)
        self.ssb_beams_mapped_to_prach_resource_grid_df_2.at[0, 266] = "SSB0"
        self.ssb_beams_mapped_to_prach_resource_grid_df_2.at[1, 266] = "SSB1"
        self.ssb_beams_mapped_to_prach_resource_grid_df_2.at[0, 270] = "SSB2"
        self.ssb_beams_mapped_to_prach_resource_grid_df_2.at[1, 270] = "SSB3"
        self.ssb_beams_mapped_to_prach_resource_grid_df_2.at[0, 546] = "SSB4"
        self.ssb_beams_mapped_to_prach_resource_grid_df_2.at[1, 546] = "SSB5"
        self.ssb_beams_mapped_to_prach_resource_grid_df_2.at[0, 550] = "SSB6"
        self.ssb_beams_mapped_to_prach_resource_grid_df_2.at[1, 550] = "SSB7"

        # Case 1: 1 SSB Beam, msg1-FDM = 1 (config: 0)

        self.config_1.read_static_config()
        self.config_1.create_dynamic_config()
        self.config_1.read_dynamic_config()

        self.pss_symbol_pattern_tuple, self.sss_symbol_pattern_tuple, self.pbch_symbol_pattern_tuple, self.all_occupied_ssb_symbols = generator.create_ssb_time_domain_occupied_symbols(case=self.ssb_case_1, nr_channel_center_freq_hz=self.nr_channel_center_freq_hz_1, duplex_mode=self.nr_duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1)
        self.prach_occasion_occupied_symbols_df_1 = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=self.config_1.nr_freq_range, duplex_mode=self.nr_duplex_mode_1, delta_f_ra_hz=self.delta_f_ra_hz_1)

        self.assertDataframeEqual(
            self.config_1.map_ssb_and_valid_prach_occasions(prach_occasion_occupied_symbols_df=self.prach_occasion_occupied_symbols_df_1, all_occupied_ssb_symbols=self.all_occupied_ssb_symbols),
            self.ssb_beams_mapped_to_prach_resource_grid_df_1
        )

        # Case 2: 8 SSB Beams, msg1-FDM = 2 (config: 1)

        self.config_1.beam_forming_antenna_tx = True
        self.config_1.beam_forming_antenna_rx = True
        self.config_1.config_dict["gNBs"]["servingCellConfigCommon"]["prach_msg1_FDM"] = 1

        self.pss_symbol_pattern_tuple, self.sss_symbol_pattern_tuple, self.pbch_symbol_pattern_tuple, self.all_occupied_ssb_symbols = generator.create_ssb_time_domain_occupied_symbols(case=self.ssb_case_1, nr_channel_center_freq_hz=self.nr_channel_center_freq_hz_1, duplex_mode=self.nr_duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1)
        self.prach_occasion_occupied_symbols_df_2 = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=self.config_1.nr_freq_range, duplex_mode=self.nr_duplex_mode_1, delta_f_ra_hz=self.delta_f_ra_hz_1)

        self.assertDataframeEqual(
            self.config_1.map_ssb_and_valid_prach_occasions(prach_occasion_occupied_symbols_df=self.prach_occasion_occupied_symbols_df_2, all_occupied_ssb_symbols=self.all_occupied_ssb_symbols),
            self.ssb_beams_mapped_to_prach_resource_grid_df_2
        )

        # Case 3: 8 SSB Beams, msg1-FDM = 1 (config: 0)
        # This case should result in an empty DataFrame, since not enough PRACH occasions are available.

        self.config_1.beam_forming_antenna_tx = True
        self.config_1.beam_forming_antenna_rx = True
        self.config_1.config_dict["gNBs"]["servingCellConfigCommon"]["prach_msg1_FDM"] = 0

        self.pss_symbol_pattern_tuple, self.sss_symbol_pattern_tuple, self.pbch_symbol_pattern_tuple, self.all_occupied_ssb_symbols = generator.create_ssb_time_domain_occupied_symbols(case=self.ssb_case_1, nr_channel_center_freq_hz=self.nr_channel_center_freq_hz_1, duplex_mode=self.nr_duplex_mode_1, shared_spectrum_channel_access=self.shared_spectrum_channel_access_1)
        self.prach_occasion_occupied_symbols_df_3 = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=self.config_1.nr_freq_range, duplex_mode=self.nr_duplex_mode_1, delta_f_ra_hz=self.delta_f_ra_hz_1)

        self.assertEqual(
            self.config_1.map_ssb_and_valid_prach_occasions(prach_occasion_occupied_symbols_df=self.prach_occasion_occupied_symbols_df_3, all_occupied_ssb_symbols=self.all_occupied_ssb_symbols),
            None
        )


class TestToolsPRACH(unittest.TestCase):
    """Test the tool functions regarding PRACH.

    """

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        self.n_prach_slots_1 = 1
        self.n_prach_slots_2 = 10
        self.delta_f_ra_hz_1 = 480_000
        self.delta_f_ra_hz_2 = 240_000
        self.delta_f_ra_hz_3 = 30_000
        self.delta_f_ra_hz_4 = 5_000
        self.prach_conf_idx_1 = 98
        self.prach_conf_idx_2 = 262 + 1
        self.prach_conf_idx_3 = 0
        self.freq_range_1 = "wrong FR"
        self.freq_range_2 = "FR2"
        self.freq_range_3 = "FR1"
        self.duplex_mode_1 = "wrong DD"
        self.duplex_mode_2 = "TDD"
        self.duplex_mode_3 = "FDD"
        self.tdd_ul_dl_configuration_common_provided_1 = True
        self.tdd_ul_dl_configuration_common_provided_2 = False
        self.dl_symbols_tuple_1 = tuple()
        self.ul_symbols_tuple_1 = tuple()
        self.ss_pbch_symbols_tuple_1 = tuple()
        self.prach_occasion_symbols_tuple_1 = tuple()
        self.channel_access_mode_1 = "wrong channel access mode"
        self.channel_access_mode_2 = "static"
        self.channel_access_mode_3 = "semistatic"
        self.channel_access_mode_4 = "dynamic"
        self.l_ra_1 = 139
        self.l_ra_2 = 1
        self.l_ra_3 = 839
        self.scs_hz_1 = 30_000
        self.scs_hz_2 = 1
        self.scs_hz_3 = 120_000
        self.msg1_fdm_idx_1 = 0
        self.msg1_fdm_idx_2 = 4
        self.mu_ref_1 = 1
        self.mu_ref_2 = 7
        self.slot_configuration_period_ms_1 = 5.0
        self.slot_configuration_period_ms_2 = 20.0
        self.n_dl_slots_1 = 7
        self.n_dl_slots_2 = 9
        self.n_dl_symbols_1 = 6
        self.n_ul_slots_1 = 2
        self.n_ul_symbols_1 = 4
        self.prach_preamble_format_1 = "A2"
        self.prach_preamble_format_2 = "wrong prach preamble format"
        self.restricted_set_str_1 = ""
        self.restricted_set_str_2 = "wrong restricted set"
        self.cyclic_prefix_extended_bool_1 = False
        self.channel_bw_hz_1 = 40_000_000
        self.channel_bw_hz_2 = 400_000_000

        self.assertRaises(ValueError, tools.compute_n_slot_ra, self.n_prach_slots_2, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, tools.compute_n_slot_ra, self.n_prach_slots_1, self.delta_f_ra_hz_2)

        self.assertRaises(ValueError, tools.compute_n_t_ra_slot, self.prach_conf_idx_2, self.freq_range_2, self.duplex_mode_2, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, tools.compute_n_t_ra_slot, self.prach_conf_idx_1, self.freq_range_1, self.duplex_mode_2, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, tools.compute_n_t_ra_slot, self.prach_conf_idx_1, self.freq_range_2, self.duplex_mode_1, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, tools.compute_n_t_ra_slot, self.prach_conf_idx_1, self.freq_range_2, self.duplex_mode_2, self.delta_f_ra_hz_2)
        self.assertRaises(ValueError, tools.compute_n_t_ra_slot, self.prach_conf_idx_1, self.freq_range_2, self.duplex_mode_2, self.delta_f_ra_hz_3)
        self.assertRaises(ValueError, tools.compute_n_t_ra_slot, self.prach_conf_idx_1, self.freq_range_2, self.duplex_mode_3, self.delta_f_ra_hz_1)

        self.assertRaises(ValueError, tools.compute_rach_occasion_starting_symbols, self.prach_conf_idx_2, self.freq_range_2, self.duplex_mode_2, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, tools.compute_rach_occasion_starting_symbols, self.prach_conf_idx_1, self.freq_range_1, self.duplex_mode_2, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, tools.compute_rach_occasion_starting_symbols, self.prach_conf_idx_1, self.freq_range_2, self.duplex_mode_1, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, tools.compute_rach_occasion_starting_symbols, self.prach_conf_idx_1, self.freq_range_2, self.duplex_mode_2, self.delta_f_ra_hz_2)
        self.assertRaises(ValueError, tools.compute_rach_occasion_starting_symbols, self.prach_conf_idx_1, self.freq_range_3, self.duplex_mode_2, self.delta_f_ra_hz_1)
        self.assertRaises(ValueError, tools.compute_rach_occasion_starting_symbols, self.prach_conf_idx_1, self.freq_range_2, self.duplex_mode_3, self.delta_f_ra_hz_1)

        self.assertRaises(ValueError, tools.verify_prach_occasion_validity, self.duplex_mode_1, self.freq_range_2, self.tdd_ul_dl_configuration_common_provided_1, self.dl_symbols_tuple_1, self.ul_symbols_tuple_1, self.ss_pbch_symbols_tuple_1, self.prach_occasion_symbols_tuple_1, self.channel_access_mode_2, self.delta_f_ra_hz_1, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.verify_prach_occasion_validity, self.duplex_mode_2, self.freq_range_1, self.tdd_ul_dl_configuration_common_provided_1, self.dl_symbols_tuple_1, self.ul_symbols_tuple_1, self.ss_pbch_symbols_tuple_1, self.prach_occasion_symbols_tuple_1, self.channel_access_mode_2, self.delta_f_ra_hz_1, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.verify_prach_occasion_validity, self.duplex_mode_3, self.freq_range_2, self.tdd_ul_dl_configuration_common_provided_1, self.dl_symbols_tuple_1, self.ul_symbols_tuple_1, self.ss_pbch_symbols_tuple_1, self.prach_occasion_symbols_tuple_1, self.channel_access_mode_2, self.delta_f_ra_hz_1, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.verify_prach_occasion_validity, self.duplex_mode_2, self.freq_range_2, self.tdd_ul_dl_configuration_common_provided_2, self.dl_symbols_tuple_1, self.ul_symbols_tuple_1, self.ss_pbch_symbols_tuple_1, self.prach_occasion_symbols_tuple_1, self.channel_access_mode_2, self.delta_f_ra_hz_1, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.verify_prach_occasion_validity, self.duplex_mode_2, self.freq_range_2, self.tdd_ul_dl_configuration_common_provided_1, self.dl_symbols_tuple_1, self.ul_symbols_tuple_1, self.ss_pbch_symbols_tuple_1, self.prach_occasion_symbols_tuple_1, self.channel_access_mode_1, self.delta_f_ra_hz_1, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.verify_prach_occasion_validity, self.duplex_mode_2, self.freq_range_2, self.tdd_ul_dl_configuration_common_provided_1, self.dl_symbols_tuple_1, self.ul_symbols_tuple_1, self.ss_pbch_symbols_tuple_1, self.prach_occasion_symbols_tuple_1, self.channel_access_mode_3, self.delta_f_ra_hz_1, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.verify_prach_occasion_validity, self.duplex_mode_2, self.freq_range_2, self.tdd_ul_dl_configuration_common_provided_1, self.dl_symbols_tuple_1, self.ul_symbols_tuple_1, self.ss_pbch_symbols_tuple_1, self.prach_occasion_symbols_tuple_1, self.channel_access_mode_4, self.delta_f_ra_hz_1, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.verify_prach_occasion_validity, self.duplex_mode_2, self.freq_range_2, self.tdd_ul_dl_configuration_common_provided_1, self.dl_symbols_tuple_1, self.ul_symbols_tuple_1, self.ss_pbch_symbols_tuple_1, self.prach_occasion_symbols_tuple_1, self.channel_access_mode_2, self.delta_f_ra_hz_2, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.verify_prach_occasion_validity, self.duplex_mode_2, self.freq_range_2, self.tdd_ul_dl_configuration_common_provided_1, self.dl_symbols_tuple_1, self.ul_symbols_tuple_1, self.ss_pbch_symbols_tuple_1, self.prach_occasion_symbols_tuple_1, self.channel_access_mode_2, self.delta_f_ra_hz_1, self.prach_conf_idx_2)

        self.assertRaises(ValueError, tools.compute_ul_dl_symbols_per_frame, self.mu_ref_2, self.slot_configuration_period_ms_1, self.n_dl_slots_1, self.n_dl_symbols_1, self.n_ul_slots_1, self.n_ul_symbols_1)
        self.assertRaises(ValueError, tools.compute_ul_dl_symbols_per_frame, self.mu_ref_1, self.slot_configuration_period_ms_2, self.n_dl_slots_1, self.n_dl_symbols_1, self.n_ul_slots_1, self.n_ul_symbols_1)
        self.assertRaises(ValueError, tools.compute_ul_dl_symbols_per_frame, self.mu_ref_1, self.slot_configuration_period_ms_1, self.n_dl_slots_2, self.n_dl_symbols_1, self.n_ul_slots_1, self.n_ul_symbols_1)

        self.assertRaises(ValueError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range_1, self.duplex_mode_2, self.prach_conf_idx_1, self.l_ra_1, self.delta_f_ra_hz_1, self.scs_hz_1, self.msg1_fdm_idx_1)
        self.assertRaises(ValueError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range_2, self.duplex_mode_1, self.prach_conf_idx_1, self.l_ra_1, self.delta_f_ra_hz_1, self.scs_hz_1, self.msg1_fdm_idx_1)
        self.assertRaises(ValueError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range_2, self.duplex_mode_2, self.prach_conf_idx_2, self.l_ra_1, self.delta_f_ra_hz_1, self.scs_hz_1, self.msg1_fdm_idx_1)
        self.assertRaises(ValueError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range_2, self.duplex_mode_2, self.prach_conf_idx_1, self.l_ra_2, self.delta_f_ra_hz_1, self.scs_hz_1, self.msg1_fdm_idx_1)
        self.assertRaises(ValueError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range_2, self.duplex_mode_2, self.prach_conf_idx_1, self.l_ra_1, self.delta_f_ra_hz_2, self.scs_hz_1, self.msg1_fdm_idx_1)
        self.assertRaises(ValueError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range_2, self.duplex_mode_2, self.prach_conf_idx_1, self.l_ra_1, self.delta_f_ra_hz_1, self.scs_hz_2, self.msg1_fdm_idx_1)
        self.assertRaises(ValueError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range_2, self.duplex_mode_2, self.prach_conf_idx_1, self.l_ra_1, self.delta_f_ra_hz_1, self.scs_hz_1, self.msg1_fdm_idx_2)
        self.assertRaises(ValueError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range_2, self.duplex_mode_2, self.prach_conf_idx_1, self.l_ra_3, self.delta_f_ra_hz_1, self.scs_hz_1, self.msg1_fdm_idx_1)

        # FR
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_1, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_3, self.scs_hz_1)
        # Duplex Mode
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_3, self.duplex_mode_1, self.prach_conf_idx_1, self.delta_f_ra_hz_3, self.scs_hz_1)
        # PRACH cfg idx
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_3, self.duplex_mode_3, self.prach_conf_idx_2, self.delta_f_ra_hz_3, self.scs_hz_1)
        # delta_f_ra_hz
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_3, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_2, self.scs_hz_1)
        # delta_f_ra_hz & FR
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_3, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_1, self.scs_hz_1)
        # delta_f_hz
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_3, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_3, self.scs_hz_2)
        # PRACH SCS & PUSCH SCS
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_2, self.duplex_mode_2, self.prach_conf_idx_1, self.delta_f_ra_hz_1, self.scs_hz_1)
        # PRACH preamble & SCS 1
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_3, self.duplex_mode_2, self.prach_conf_idx_3, self.delta_f_ra_hz_3, self.scs_hz_1)
        # PRACH preamble & SCS 2
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_3, self.duplex_mode_2, self.prach_conf_idx_1, self.delta_f_ra_hz_4, self.scs_hz_1)
        # FR & Duplex mode
        self.assertRaises(ValueError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range_2, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_1, self.scs_hz_3)

        # FR
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_1, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_3, self.scs_hz_1)
        # Duplex Mode
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_3, self.duplex_mode_1, self.prach_conf_idx_1, self.delta_f_ra_hz_3, self.scs_hz_1)
        # PRACH cfg idx
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_3, self.duplex_mode_3, self.prach_conf_idx_2, self.delta_f_ra_hz_3, self.scs_hz_1)
        # delta_f_ra_hz
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_3, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_2, self.scs_hz_1)
        # delta_f_ra_hz & FR
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_3, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_1, self.scs_hz_1)
        # delta_f_hz
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_3, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_3, self.scs_hz_2)
        # PRACH SCS & PUSCH SCS
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_2, self.duplex_mode_2, self.prach_conf_idx_1, self.delta_f_ra_hz_1, self.scs_hz_1)
        # PRACH preamble & SCS 1
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_3, self.duplex_mode_2, self.prach_conf_idx_3, self.delta_f_ra_hz_3, self.scs_hz_1)
        # PRACH preamble & SCS 2
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_3, self.duplex_mode_2, self.prach_conf_idx_1, self.delta_f_ra_hz_4, self.scs_hz_1)
        # FR & Duplex mode
        self.assertRaises(ValueError, tools.compute_prach_guard_times, self.freq_range_2, self.duplex_mode_3, self.prach_conf_idx_1, self.delta_f_ra_hz_1, self.scs_hz_3)

        self.assertRaises(ValueError, tools.compute_prach_preamble_format, self.freq_range_1, self.duplex_mode_2, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.compute_prach_preamble_format, self.freq_range_2, self.duplex_mode_1, self.prach_conf_idx_1)
        self.assertRaises(ValueError, tools.compute_prach_preamble_format, self.freq_range_2, self.duplex_mode_2, self.prach_conf_idx_2)
        self.assertRaises(ValueError, tools.compute_prach_preamble_format, self.freq_range_2, self.duplex_mode_3, self.prach_conf_idx_1)

        self.assertRaises(ValueError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_2, self.l_ra_1, self.delta_f_ra_hz_3, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range_3)
        self.assertRaises(ValueError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra_2, self.delta_f_ra_hz_3, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range_3)
        self.assertRaises(ValueError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra_1, self.delta_f_ra_hz_2, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range_3)
        self.assertRaises(ValueError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra_1, self.delta_f_ra_hz_3, self.restricted_set_str_2, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range_3)
        self.assertRaises(ValueError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra_1, self.delta_f_ra_hz_3, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range_1)
        self.assertRaises(ValueError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra_1, self.delta_f_ra_hz_3, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range_2)
        self.assertRaises(ValueError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra_1, self.delta_f_ra_hz_3, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_2, self.freq_range_3)

        self.assertRaises(ValueError, tools.compute_prach_zc_sequences_duration, self.prach_preamble_format_2)

        self.assertRaises(ValueError, tools.compute_prach_cyclic_prefix_duration, self.prach_preamble_format_2)

    def test_var_types(self):
        """Test the parameter types.

        """
        self.n_prach_slots = 1
        self.delta_f_ra_hz = 30_000
        self.prach_conf_idx = 98
        self.freq_range = "FR1"
        self.duplex_mode = "TDD"
        self.tdd_ul_dl_configuration_common_provided = True
        self.dl_symbols_tuple = tuple()
        self.ul_symbols_tuple = tuple()
        self.ss_pbch_symbols_tuple = tuple()
        self.prach_occasion_symbols_tuple = tuple()
        self.channel_access_mode = "static"
        self.l_ra = 139
        self.scs_hz = 30_000
        self.msg1_fdm_idx = 0
        self.mu_ref_1 = 1
        self.slot_configuration_period_ms_1 = 5.0
        self.n_dl_slots_1 = 7
        self.n_dl_symbols_1 = 6
        self.n_ul_slots_1 = 2
        self.n_ul_symbols_1 = 4
        self.prach_preamble_format_1 = "A2"
        self.restricted_set_str_1 = ""
        self.cyclic_prefix_extended_bool_1 = False
        self.channel_bw_hz_1 = 40_000_000

        self.assertRaises(TypeError, tools.compute_n_slot_ra, "not int", self.delta_f_ra_hz)
        self.assertRaises(TypeError, tools.compute_n_slot_ra, self.n_prach_slots, "not int")

        self.assertRaises(TypeError, tools.compute_n_t_ra_slot, "not int", self.freq_range, self.duplex_mode, self.delta_f_ra_hz)
        self.assertRaises(TypeError, tools.compute_n_t_ra_slot, self.prach_conf_idx, 0, self.duplex_mode, self.delta_f_ra_hz)
        self.assertRaises(TypeError, tools.compute_n_t_ra_slot, self.prach_conf_idx, self.freq_range, 0, self.delta_f_ra_hz)
        self.assertRaises(TypeError, tools.compute_n_t_ra_slot, self.prach_conf_idx, self.freq_range, self.duplex_mode, "not int")

        self.assertRaises(TypeError, tools.compute_rach_occasion_starting_symbols, "not int", self.freq_range, self.duplex_mode, self.delta_f_ra_hz)
        self.assertRaises(TypeError, tools.compute_rach_occasion_starting_symbols, self.prach_conf_idx, 0, self.duplex_mode, self.delta_f_ra_hz)
        self.assertRaises(TypeError, tools.compute_rach_occasion_starting_symbols, self.prach_conf_idx, self.freq_range, 0, self.delta_f_ra_hz)
        self.assertRaises(TypeError, tools.compute_rach_occasion_starting_symbols, self.prach_conf_idx, self.freq_range, self.duplex_mode, "not int")

        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, 0, self.freq_range, self.tdd_ul_dl_configuration_common_provided, self.dl_symbols_tuple, self.ul_symbols_tuple, self.ss_pbch_symbols_tuple, self.prach_occasion_symbols_tuple, self.channel_access_mode, self.delta_f_ra_hz, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, self.duplex_mode, 0, self.tdd_ul_dl_configuration_common_provided, self.dl_symbols_tuple, self.ul_symbols_tuple, self.ss_pbch_symbols_tuple, self.prach_occasion_symbols_tuple, self.channel_access_mode, self.delta_f_ra_hz, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, self.duplex_mode, self.freq_range, "not bool", self.dl_symbols_tuple, self.ul_symbols_tuple, self.ss_pbch_symbols_tuple, self.prach_occasion_symbols_tuple, self.channel_access_mode, self.delta_f_ra_hz, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, self.duplex_mode, self.freq_range, self.tdd_ul_dl_configuration_common_provided, "not tuple", self.ul_symbols_tuple, self.ss_pbch_symbols_tuple, self.prach_occasion_symbols_tuple, self.channel_access_mode, self.delta_f_ra_hz, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, self.duplex_mode, self.freq_range, self.tdd_ul_dl_configuration_common_provided, self.dl_symbols_tuple, "not tuple", self.ss_pbch_symbols_tuple, self.prach_occasion_symbols_tuple, self.channel_access_mode, self.delta_f_ra_hz, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, self.duplex_mode, self.freq_range, self.tdd_ul_dl_configuration_common_provided, self.dl_symbols_tuple, self.ul_symbols_tuple, "not tuple", self.prach_occasion_symbols_tuple, self.channel_access_mode, self.delta_f_ra_hz, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, self.duplex_mode, self.freq_range, self.tdd_ul_dl_configuration_common_provided, self.dl_symbols_tuple, self.ul_symbols_tuple, self.ss_pbch_symbols_tuple, "not tuple", self.channel_access_mode, self.delta_f_ra_hz, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, self.duplex_mode, self.freq_range, self.tdd_ul_dl_configuration_common_provided, self.dl_symbols_tuple, self.ul_symbols_tuple, self.ss_pbch_symbols_tuple, self.prach_occasion_symbols_tuple, 0, self.delta_f_ra_hz, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, self.duplex_mode, self.freq_range, self.tdd_ul_dl_configuration_common_provided, self.dl_symbols_tuple, self.ul_symbols_tuple, self.ss_pbch_symbols_tuple, self.prach_occasion_symbols_tuple, self.channel_access_mode, "not int", self.prach_conf_idx)
        self.assertRaises(TypeError, tools.verify_prach_occasion_validity, self.duplex_mode, self.freq_range, self.tdd_ul_dl_configuration_common_provided, self.dl_symbols_tuple, self.ul_symbols_tuple, self.ss_pbch_symbols_tuple, self.prach_occasion_symbols_tuple, self.channel_access_mode, self.delta_f_ra_hz, "not int")

        self.assertRaises(TypeError, tools.compute_ul_dl_symbols_per_frame, "not int", self.slot_configuration_period_ms_1, self.n_dl_slots_1, self.n_dl_symbols_1, self.n_ul_slots_1, self.n_ul_symbols_1)
        self.assertRaises(TypeError, tools.compute_ul_dl_symbols_per_frame, self.mu_ref_1, "not float", self.n_dl_slots_1, self.n_dl_symbols_1, self.n_ul_slots_1, self.n_ul_symbols_1)
        self.assertRaises(TypeError, tools.compute_ul_dl_symbols_per_frame, self.mu_ref_1, self.slot_configuration_period_ms_1, "not int", self.n_dl_symbols_1, self.n_ul_slots_1, self.n_ul_symbols_1)
        self.assertRaises(TypeError, tools.compute_ul_dl_symbols_per_frame, self.mu_ref_1, self.slot_configuration_period_ms_1, self.n_dl_slots_1, "not int", self.n_ul_slots_1, self.n_ul_symbols_1)
        self.assertRaises(TypeError, tools.compute_ul_dl_symbols_per_frame, self.mu_ref_1, self.slot_configuration_period_ms_1, self.n_dl_slots_1, self.n_dl_symbols_1, "not int", self.n_ul_symbols_1)
        self.assertRaises(TypeError, tools.compute_ul_dl_symbols_per_frame, self.mu_ref_1, self.slot_configuration_period_ms_1, self.n_dl_slots_1, self.n_dl_symbols_1, self.n_ul_slots_1, "not int")

        self.assertRaises(TypeError, tools.compute_pusch_rbs_occupied_by_prach, 0, self.duplex_mode, self.prach_conf_idx, self.l_ra, self.delta_f_ra_hz, self.scs_hz, self.msg1_fdm_idx)
        self.assertRaises(TypeError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range, 0, self.prach_conf_idx, self.l_ra, self.delta_f_ra_hz, self.scs_hz, self.msg1_fdm_idx)
        self.assertRaises(TypeError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range, self.duplex_mode, "not int", self.l_ra, self.delta_f_ra_hz, self.scs_hz, self.msg1_fdm_idx)
        self.assertRaises(TypeError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range, self.duplex_mode, self.prach_conf_idx, "not int", self.delta_f_ra_hz, self.scs_hz, self.msg1_fdm_idx)
        self.assertRaises(TypeError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range, self.duplex_mode, self.prach_conf_idx, self.l_ra, "not int", self.scs_hz, self.msg1_fdm_idx)
        self.assertRaises(TypeError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range, self.duplex_mode, self.prach_conf_idx, self.l_ra, self.delta_f_ra_hz, "not int", self.msg1_fdm_idx)
        self.assertRaises(TypeError, tools.compute_pusch_rbs_occupied_by_prach, self.freq_range, self.duplex_mode, self.prach_conf_idx, self.l_ra, self.delta_f_ra_hz, self.scs_hz, "not int")

        self.assertRaises(TypeError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, 0, self.duplex_mode, self.prach_conf_idx, self.delta_f_ra_hz, self.scs_hz)
        self.assertRaises(TypeError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range, 0, self.prach_conf_idx, self.delta_f_ra_hz, self.scs_hz)
        self.assertRaises(TypeError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range, self.duplex_mode, "not int", self.delta_f_ra_hz, self.scs_hz)
        self.assertRaises(TypeError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range, self.duplex_mode, self.prach_conf_idx, "not int", self.scs_hz)
        self.assertRaises(TypeError, tools.compute_pusch_ofdm_symbols_occupied_by_rach_occasions, self.freq_range, self.duplex_mode, self.prach_conf_idx, self.delta_f_ra_hz, "not int")

        self.assertRaises(TypeError, tools.compute_prach_guard_times, 0, self.duplex_mode, self.prach_conf_idx, self.delta_f_ra_hz, self.scs_hz)
        self.assertRaises(TypeError, tools.compute_prach_guard_times, self.freq_range, 0, self.prach_conf_idx, self.delta_f_ra_hz, self.scs_hz)
        self.assertRaises(TypeError, tools.compute_prach_guard_times, self.freq_range, self.duplex_mode, "not int", self.delta_f_ra_hz, self.scs_hz)
        self.assertRaises(TypeError, tools.compute_prach_guard_times, self.freq_range, self.duplex_mode, self.prach_conf_idx, "not int", self.scs_hz)
        self.assertRaises(TypeError, tools.compute_prach_guard_times, self.freq_range, self.duplex_mode, self.prach_conf_idx, self.delta_f_ra_hz, "not int")

        self.assertRaises(TypeError, tools.compute_prach_preamble_format, 0, self.duplex_mode, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.compute_prach_preamble_format, self.freq_range, 0, self.prach_conf_idx)
        self.assertRaises(TypeError, tools.compute_prach_preamble_format, self.freq_range, self.duplex_mode, "not int")

        self.assertRaises(TypeError, tools.compute_maximum_gnb_cell_radius, 0, self.l_ra, self.delta_f_ra_hz, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range)
        self.assertRaises(TypeError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, "not int", self.delta_f_ra_hz, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range)
        self.assertRaises(TypeError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra, "not int", self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range)
        self.assertRaises(TypeError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra, self.delta_f_ra_hz, 0, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, self.freq_range)
        self.assertRaises(TypeError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra, self.delta_f_ra_hz, self.restricted_set_str_1, "not bool", self.channel_bw_hz_1, self.freq_range)
        self.assertRaises(TypeError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra, self.delta_f_ra_hz, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, "not int", self.freq_range)
        self.assertRaises(TypeError, tools.compute_maximum_gnb_cell_radius, self.prach_preamble_format_1, self.l_ra, self.delta_f_ra_hz, self.restricted_set_str_1, self.cyclic_prefix_extended_bool_1, self.channel_bw_hz_1, 0)

        self.assertRaises(TypeError, tools.compute_prach_zc_sequences_duration, 0)

        self.assertRaises(TypeError, tools.compute_prach_cyclic_prefix_duration, 0)

    def test_compute_n_slot_ra(self):
        """Test computing the number of PRACH slots n_slot^RA within a reference grid slot according to 3GPP TS 38.211 ch. 5.3.2.

        """
        self.n_prach_slots_1 = 1
        self.n_prach_slots_2 = 2
        self.delta_f_ra_hz_1_lst = [1_250, 5_000, 15_000, 60_000]
        self.delta_f_ra_hz_2_lst = [30_000, 120_000]
        self.delta_f_ra_hz_3 = 480_000
        self.delta_f_ra_hz_4 = 960_000

        for i in self.delta_f_ra_hz_1_lst:
            self.assertEqual(tools.compute_n_slot_ra(n_prach_slots=self.n_prach_slots_1, delta_f_ra_hz=i), (0,))
        for j in self.delta_f_ra_hz_2_lst:
            self.assertEqual(tools.compute_n_slot_ra(n_prach_slots=self.n_prach_slots_1, delta_f_ra_hz=j), (1,))
            self.assertEqual(tools.compute_n_slot_ra(n_prach_slots=self.n_prach_slots_2, delta_f_ra_hz=j), (0, 1))
        self.assertEqual(tools.compute_n_slot_ra(n_prach_slots=self.n_prach_slots_1, delta_f_ra_hz=self.delta_f_ra_hz_3), (7,))
        self.assertEqual(tools.compute_n_slot_ra(n_prach_slots=self.n_prach_slots_1, delta_f_ra_hz=self.delta_f_ra_hz_4), (15,))
        self.assertEqual(tools.compute_n_slot_ra(n_prach_slots=self.n_prach_slots_2, delta_f_ra_hz=self.delta_f_ra_hz_3), (3, 7))
        self.assertEqual(tools.compute_n_slot_ra(n_prach_slots=self.n_prach_slots_2, delta_f_ra_hz=self.delta_f_ra_hz_4), (7, 15))

    def test_compute_rach_occasion_starting_symbols(self):
        """Test computing a list of symbol numbers occupied with RACH occasions according to 3GPP TS 38.211 ch. 5.3.2.
        Use 3GPP TS 38.211 Tables 6.3.3.2-2 (FR1 FDD), 6.3.3.2-3 (FR1 TDD), and 6.3.3.2-4 (FR2).

        6.3.3.2-2 (FR1 FDD) case 1:
        ---------------------------
        prach_conf_idx=98, freq_range="FR1", duplex_mode="FDD", delta_f_ra_hz=30000:
            l_0:            0
            n_t_ra_slot:    6
            n_dur_ra:       2
            n_prach_slots:  1
            n_slot_ra:      (1,)
            n_t_ra:         (0, 1, 2, 3, 4, 5)
            l:              (14, 16, 18, 20, 22, 24)

        6.3.3.2-3 (FR1 TDD) case 1:
        ---------------------------
        prach_conf_idx=98, freq_range="FR1", duplex_mode="TDD", delta_f_ra_hz=30000:
            l_0:            0
            n_t_ra_slot:    3
            n_dur_ra:       4
            n_prach_slots:  1
            n_slot_ra:      (1,)
            n_t_ra:         (0, 1, 2)
            l:              (14, 18, 22)

        6.3.3.2-3 (FR1 TDD) case 2:
        ---------------------------
        prach_conf_idx=2, freq_range="FR1", duplex_mode="TDD", delta_f_ra_hz=5000:
            l_0:            0
            n_t_ra_slot:    3
            n_dur_ra:       0
            n_prach_slots:  1
            n_slot_ra:      (0,)
            n_t_ra:         (0,)
            l:              (0,)

        6.3.3.2-4 (FR2 TDD) case 1:
        ---------------------------
        prach_conf_idx=98, freq_range="FR2", duplex_mode="TDD", delta_f_ra_hz=120000:
            l_0:            8
            n_t_ra_slot:    3
            n_dur_ra:       2
            n_prach_slots:  2
            n_slot_ra:      (0, 1)
            n_t_ra:         (0, 1, 2)
            l:              (8, 10, 12, 22, 24, 26)

        """
        self.prach_conf_idx_1 = 98
        self.prach_conf_idx_2 = 2
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"
        self.duplex_mode_1 = "FDD"
        self.duplex_mode_2 = "TDD"
        self.delta_f_ra_hz_1 = 30_000
        self.delta_f_ra_hz_2 = 5_000
        self.delta_f_ra_hz_3 = 120_000

        self.rach_occasion_starting_symbols_1 = (14, 16, 18, 20, 22, 24)
        self.rach_occasion_starting_symbols_2 = (14, 18, 22)
        self.rach_occasion_starting_symbols_3 = (0,)
        self.rach_occasion_starting_symbols_4 = (8, 10, 12, 22, 24, 26)

        self.assertEqual(tools.compute_rach_occasion_starting_symbols(prach_conf_idx=self.prach_conf_idx_1, freq_range=self.freq_range_1, duplex_mode=self.duplex_mode_1, delta_f_ra_hz=self.delta_f_ra_hz_1), self.rach_occasion_starting_symbols_1)
        self.assertEqual(tools.compute_rach_occasion_starting_symbols(prach_conf_idx=self.prach_conf_idx_1, freq_range=self.freq_range_1, duplex_mode=self.duplex_mode_2, delta_f_ra_hz=self.delta_f_ra_hz_1), self.rach_occasion_starting_symbols_2)
        self.assertEqual(tools.compute_rach_occasion_starting_symbols(prach_conf_idx=self.prach_conf_idx_2, freq_range=self.freq_range_1, duplex_mode=self.duplex_mode_2, delta_f_ra_hz=self.delta_f_ra_hz_2), self.rach_occasion_starting_symbols_3)
        self.assertEqual(tools.compute_rach_occasion_starting_symbols(prach_conf_idx=self.prach_conf_idx_1, freq_range=self.freq_range_2, duplex_mode=self.duplex_mode_2, delta_f_ra_hz=self.delta_f_ra_hz_3), self.rach_occasion_starting_symbols_4)

    def test_verify_prach_occasion_validity(self):
        """Test verifying that a PRACH occasion is valid according to TS 38.213 ch. 8.1 and Table 8.1-2.

        TODO: Add valid and invalid PRACH occasion examples for all parameter combinations.

        """
        self.duplex_mode_1 = "FDD"
        self.duplex_mode_2 = "TDD"
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"
        self.tdd_ul_dl_configuration_common_provided_1 = False
        self.tdd_ul_dl_configuration_common_provided_1 = True
        self.dl_symbols_tuple_1 = tuple(
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
                33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
                48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62,
                63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77,
                78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92,
                93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 140, 141,
                142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153,
                154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165,
                166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177,
                178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189,
                190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201,
                202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213,
                214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225,
                226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237,
                238, 239, 240, 241, 242, 243]
        )
        self.ul_symbols_tuple_1 = tuple(
            [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
                120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131,
                132, 133, 134, 135, 136, 137, 138, 139, 248, 249, 250, 251,
                252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263,
                264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275,
                276, 277, 278, 279]
        )
        self.ss_pbch_symbols_tuple_1 = tuple(
            [2, 3, 4, 5, 8, 9, 10, 11, 16, 17, 18, 19, 22, 23, 24, 25, 30,
                31, 32, 33, 36, 37, 38, 39, 44, 45, 46, 47, 50, 51, 52, 53]
        )
        self.prach_occasion_symbols_tuple_1 = tuple(
            [266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277]
        )
        self.channel_access_mode_1 = "static"
        self.channel_access_mode_2 = "semistatic"
        self.channel_access_mode_3 = "dynamic"
        self.preamble_scs_hz_1 = 5_000
        self.preamble_scs_hz_2 = 30_000
        self.preamble_scs_hz_3 = 480_000
        self.preamble_scs_hz_4 = 960_000
        self.prach_conf_idx_1 = 98
        self.prach_conf_idx_2 = 145

        # Valid configuration 1:
        # FDD, which should always be valid

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_1,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=self.dl_symbols_tuple_1,
                ul_symbols_tuple=self.ul_symbols_tuple_1,
                ss_pbch_symbols_tuple=self.ss_pbch_symbols_tuple_1,
                prach_occasion_symbols_tuple=self.prach_occasion_symbols_tuple_1,
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_1,
                prach_conf_idx=self.prach_conf_idx_1
            ),
            True
        )

        # Valid configuration 2:
        # TDD

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_2,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=self.dl_symbols_tuple_1,
                ul_symbols_tuple=self.ul_symbols_tuple_1,
                ss_pbch_symbols_tuple=self.ss_pbch_symbols_tuple_1,
                prach_occasion_symbols_tuple=self.prach_occasion_symbols_tuple_1,
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_2,
                prach_conf_idx=self.prach_conf_idx_1
            ),
            True
        )

        # Valid configuration 3:
        # TDD, B4

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_2,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=self.dl_symbols_tuple_1,
                ul_symbols_tuple=self.ul_symbols_tuple_1,
                ss_pbch_symbols_tuple=self.ss_pbch_symbols_tuple_1,
                prach_occasion_symbols_tuple=self.prach_occasion_symbols_tuple_1,
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_2,
                prach_conf_idx=self.prach_conf_idx_2
            ),
            True
        )

        # Valid configuration 4:
        # TDD with some PRACH occasion symbols in Flex symbols (Uplink symbols modified)

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_2,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=self.dl_symbols_tuple_1,
                ul_symbols_tuple=self.ul_symbols_tuple_1[:-3],
                ss_pbch_symbols_tuple=self.ss_pbch_symbols_tuple_1,
                prach_occasion_symbols_tuple=self.prach_occasion_symbols_tuple_1,
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_2,
                prach_conf_idx=self.prach_conf_idx_1
            ),
            True
        )

        # Valid configuration 5:
        # TDD with some PRACH occasion symbols in Flex symbols (Uplink symbols modified)
        # and with SS/PBCH block in a PRACH slot (PRACH occasion symbols modified)

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_2,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=tuple(set(self.dl_symbols_tuple_1) - set(range(52, 56))),
                ul_symbols_tuple=tuple(sorted(self.ul_symbols_tuple_1[:-3] + tuple(range(54, 56)))),
                ss_pbch_symbols_tuple=self.ss_pbch_symbols_tuple_1,
                prach_occasion_symbols_tuple=tuple(sorted(self.prach_occasion_symbols_tuple_1 + tuple(range(54, 56)))),
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_2,
                prach_conf_idx=self.prach_conf_idx_1
            ),
            True
        )

        # - it does not precede a SS/PBCH block in the PRACH slot and starts at least N_gap symbols after a last
        #    downlink symbol and at least N_gap symbols after a last SS/PBCH block symbol, where N_gap is provided in
        #    Table 8.1-2,
        #  and if channelAccessMode = "semiStatic" is provided, does not overlap with a set of consecutive
        #    symbols before the start of a next channel occupancy time where there shall not be any transmissions, as
        #    described in [15, TS 37.213]
        #    - the candidate SS/PBCH block index of the SS/PBCH block corresponds to the SS/PBCH block index
        #        provided by ssb-PositionsInBurst in SIB1 or in ServingCellConfigCommon, as described in clause 4.1.

        # Invalid configuration 1: PRACH occasion symbols less than N_gap symbols after Downlink symbols
        # PRACH occasion symbols extended to neighbor with Downlink symbols (edge case)
        # Uplink symbols reduced by the last 3 elements, so not all PRACH occasion symbols are within Uplink symbols
        # PRACH Occasion symbols in Flex symbols (104 ... 139)

        # prach_occasion_symbols_tuple = tuple(sorted(prach_occasion_symbols_tuple + tuple(range(104,140))))
        # ul_symbols_tuple = ul_symbols_tuple[:-3]

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_2,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=self.dl_symbols_tuple_1,
                ul_symbols_tuple=self.ul_symbols_tuple_1,
                ss_pbch_symbols_tuple=self.ss_pbch_symbols_tuple_1,
                prach_occasion_symbols_tuple=tuple(sorted(self.prach_occasion_symbols_tuple_1 + tuple(range(104, 140)))),
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_2,
                prach_conf_idx=self.prach_conf_idx_1
            ),
            False
        )

        # Invalid configuration 2: PRACH occasion symbols less than N_gap symbols after Downlink symbols
        # Downlink symbols extended to neighbor with PRACH occasion symbols (edge case)
        # Uplink symbols reduced by the last 3 elements, so not all PRACH occasion symbols are within Uplink symbols

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_2,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=tuple(sorted(self.dl_symbols_tuple_1 + tuple(range(244, 266)))),
                ul_symbols_tuple=self.ul_symbols_tuple_1[:-3],
                ss_pbch_symbols_tuple=self.ss_pbch_symbols_tuple_1,
                prach_occasion_symbols_tuple=self.prach_occasion_symbols_tuple_1,
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_2,
                prach_conf_idx=self.prach_conf_idx_1
            ),
            False
        )

        # Invalid configuration 3: PRACH occasion precedes an SS/PBCH block in the PRACH slot
        # PRACH occasion symbols extended to precede SS/PBCH symbols (edge case)
        # Uplink symbols reduced by the last 3 elements, so not all PRACH occasion symbols are within Uplink symbols
        # Uplink symbols extended by symbols 0 and 1, so PRACH occasion symbols 0 and 1 in Uplink
        # Downlink symbols reduced by the first 2 elements, so PRACH occasion symbols are not in Downlink symbols

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_2,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=self.dl_symbols_tuple_1[2:],
                ul_symbols_tuple=tuple(sorted(self.ul_symbols_tuple_1[:-3] + tuple(range(0, 1)))),
                ss_pbch_symbols_tuple=self.ss_pbch_symbols_tuple_1,
                prach_occasion_symbols_tuple=tuple(sorted(self.prach_occasion_symbols_tuple_1 + tuple(range(0, 1)))),
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_2,
                prach_conf_idx=self.prach_conf_idx_1
            ),
            False
        )

        # Invalid configuration 4: PRACH occasion less than N_gap symbols after a last SS/PBCH block symbol
        # SS/PBCH symbols extended to neighbor with PRACH occasion (edge case)
        # Uplink symbols reduced by the last 3 elements, so not all PRACH occasion symbols are within Uplink symbols

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_2,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=self.dl_symbols_tuple_1,
                ul_symbols_tuple=self.ul_symbols_tuple_1[:-3],
                ss_pbch_symbols_tuple=tuple(sorted(self.ss_pbch_symbols_tuple_1 + tuple(range(244, 266)))),
                prach_occasion_symbols_tuple=self.prach_occasion_symbols_tuple_1,
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_2,
                prach_conf_idx=self.prach_conf_idx_1
            ),
            False
        )

        # Invalid configuration 5: PRACH occasion less than N_gap symbols after a last SS/PBCH block symbol
        # SS/PBCH symbols extended to overlap with PRACH occasion
        # Uplink symbols reduced by the last 3 elements, so not all PRACH occasion symbols are within Uplink symbols

        self.assertEqual(
            tools.verify_prach_occasion_validity(
                duplex_mode=self.duplex_mode_2,
                freq_range=self.freq_range_1,
                tdd_ul_dl_configuration_common_provided=self.tdd_ul_dl_configuration_common_provided_1,
                dl_symbols_tuple=self.dl_symbols_tuple_1,
                ul_symbols_tuple=self.ul_symbols_tuple_1[:-3],
                ss_pbch_symbols_tuple=tuple(sorted(self.ss_pbch_symbols_tuple_1 + tuple(range(244, 272)))),
                prach_occasion_symbols_tuple=self.prach_occasion_symbols_tuple_1,
                channel_access_mode=self.channel_access_mode_1,
                preamble_scs_hz=self.preamble_scs_hz_2,
                prach_conf_idx=self.prach_conf_idx_1
            ),
            False
        )

    def test_compute_ul_dl_symbols_per_frame(self):
        """Test the Uplink, Downlink and Flexible symbols per NR Radio Frame.
        This is based on the slot configuration according to 3GPP TS 38.213 ch. 11.1, which is also known as pattern1.

        NOTE: Slot 7 contains DL, Flex and UL symbols!

        | DL Slots | DL Symbols & Flexible Symbols | Flexible Slots | Flexible Symbols & Uplink Symbols | Uplink Slots |
        |        7 |          6 & 2                |              0 |                2 & 4              |            2 |
        |<---------------------------------- dl-UL-TransmissionPeriodicity = 5.0 ms ---------------------------------->|

        """
        self.mu_ref = 1
        self.slot_configuration_period_ms = 5.0
        self.n_dl_slots = 7
        self.n_dl_symbols = 6
        self.n_ul_slots = 2
        self.n_ul_symbols = 4
        self.downlink_symbols_tuple = (
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
            14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
            28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41,
            42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
            56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
            70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
            84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97,
            98, 99, 100, 101, 102, 103,
            140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153,
            154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167,
            168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181,
            182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195,
            196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209,
            210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223,
            224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237,
            238, 239, 240, 241, 242, 243
        )
        self.flexible_symbols_tuple = (
            104, 105, 106, 107,
            244, 245, 246, 247
        )
        self.uplink_symbols_tuple = (
            108, 109, 110, 111,
            112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
            126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139,
            248, 249, 250, 251,
            252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265,
            266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279
        )

        self.ul_flex_dl_symbols_tuple = (self.downlink_symbols_tuple, self.flexible_symbols_tuple, self.uplink_symbols_tuple)

        self.assertEqual(
            tools.compute_ul_dl_symbols_per_frame(
                mu_ref=self.mu_ref,
                slot_configuration_period_ms=self.slot_configuration_period_ms,
                n_dl_slots=self.n_dl_slots,
                n_dl_symbols=self.n_dl_symbols,
                n_ul_slots=self.n_ul_slots,
                n_ul_symbols=self.n_ul_symbols
            ),
            self.ul_flex_dl_symbols_tuple
        )

    def test_compute_pusch_rbs_occupied_by_prach(self):
        """Test computing the number of PUSCH Resource Blocks occupied by PRACH.

        The following combinations are tested:

        | Frequency Range | Duplex Mode | PRACH Config Index | L_RA | delta f_RA | Subcarrier Spacing | msg1-FDM Index | Occupied RBs |
        | --------------- | ----------- | ------------------ | ---- | ---------- | ------------------ | -------------- | ------------ |
        |             FR1 |         FDD |                 98 |  139 |     30 kHz |             30 kHz |              0 |           12 |
        |             FR1 |         FDD |                 98 |  571 |     30 kHz |             30 kHz |              0 |           48 |
        |             FR1 |         FDD |                 98 | 1151 |     15 kHz |             15 kHz |              0 |           96 |
        |             FR1 |         FDD |                 98 |  139 |     30 kHz |             30 kHz |              2 |           48 |
        |             FR1 |         FDD |                 98 |  571 |     30 kHz |             30 kHz |              3 |          384 |
        |             FR1 |         FDD |                 86 |  839 |      5 kHz |             30 kHz |              0 |           12 |
        |             FR1 |         TDD |                 98 |  139 |     30 kHz |             30 kHz |              0 |           12 |
        |             FR1 |         TDD |                 98 |  571 |     30 kHz |             30 kHz |              0 |           48 |
        |             FR1 |         TDD |                 98 | 1151 |     15 kHz |             15 kHz |              0 |           96 |
        |             FR1 |         TDD |                 98 |  139 |     30 kHz |             30 kHz |              2 |           48 |
        |             FR1 |         TDD |                 98 |  571 |     30 kHz |             30 kHz |              3 |          384 |
        |             FR1 |         TDD |                 66 |  839 |      5 kHz |             30 kHz |              0 |           12 |
        |             FR1 |         TDD |                 66 |  839 |   1.25 kHz |             30 kHz |              0 |            3 |
        |             FR2 |         TDD |                 98 |  139 |    120 kHz |            120 kHz |              0 |           12 |
        |             FR2 |         TDD |                 98 |  571 |    120 kHz |            120 kHz |              0 |           48 |
        |             FR2 |         TDD |                 98 | 1151 |    120 kHz |            120 kHz |              0 |           97 |
        |             FR2 |         TDD |                 98 |  139 |    120 kHz |            120 kHz |              2 |           48 |
        |             FR2 |         TDD |                 98 |  571 |    120 kHz |            960 kHz |              3 |           56 |

        """
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"
        self.duplex_mode_1 = "FDD"
        self.duplex_mode_2 = "TDD"
        self.prach_config_idx_1 = 98
        self.prach_config_idx_2 = 86
        self.prach_config_idx_3 = 66
        self.l_ra_1 = 139
        self.l_ra_2 = 571
        self.l_ra_3 = 1_151
        self.l_ra_4 = 839
        self.delta_f_ra_hz_1 = 30_000
        self.delta_f_ra_hz_2 = 15_000
        self.delta_f_ra_hz_3 = 5_000
        self.delta_f_ra_hz_4 = 120_000
        self.delta_f_ra_hz_5 = 1_250
        self.scs_hz_1 = 30_000
        self.scs_hz_2 = 15_000
        self.scs_hz_3 = 120_000
        self.scs_hz_4 = 960_000
        self.msg1_fdm_idx_1 = 0
        self.msg1_fdm_idx_2 = 2
        self.msg1_fdm_idx_3 = 3

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_1,
                delta_f_ra_hz=self.delta_f_ra_hz_1,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            12
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_2,
                delta_f_ra_hz=self.delta_f_ra_hz_1,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            48
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_3,
                delta_f_ra_hz=self.delta_f_ra_hz_2,
                nr_scs_hz=self.scs_hz_2,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            96
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_1,
                delta_f_ra_hz=self.delta_f_ra_hz_1,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_2
            ),
            48
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_2,
                delta_f_ra_hz=self.delta_f_ra_hz_1,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_3
            ),
            384
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=self.prach_config_idx_2,
                l_ra=self.l_ra_4,
                delta_f_ra_hz=self.delta_f_ra_hz_3,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            12
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_1,
                delta_f_ra_hz=self.delta_f_ra_hz_1,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            12
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_2,
                delta_f_ra_hz=self.delta_f_ra_hz_1,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            48
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_3,
                delta_f_ra_hz=self.delta_f_ra_hz_2,
                nr_scs_hz=self.scs_hz_2,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            96
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_1,
                delta_f_ra_hz=self.delta_f_ra_hz_1,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_2
            ),
            48
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_2,
                delta_f_ra_hz=self.delta_f_ra_hz_1,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_3
            ),
            384
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_3,
                l_ra=self.l_ra_4,
                delta_f_ra_hz=self.delta_f_ra_hz_3,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            12
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_3,
                l_ra=self.l_ra_4,
                delta_f_ra_hz=self.delta_f_ra_hz_5,
                nr_scs_hz=self.scs_hz_1,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            3
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_1,
                delta_f_ra_hz=self.delta_f_ra_hz_4,
                nr_scs_hz=self.scs_hz_3,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            12
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_2,
                delta_f_ra_hz=self.delta_f_ra_hz_4,
                nr_scs_hz=self.scs_hz_3,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            48
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_3,
                delta_f_ra_hz=self.delta_f_ra_hz_4,
                nr_scs_hz=self.scs_hz_3,
                msg1_fdm_idx=self.msg1_fdm_idx_1
            ),
            97
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_1,
                delta_f_ra_hz=self.delta_f_ra_hz_4,
                nr_scs_hz=self.scs_hz_3,
                msg1_fdm_idx=self.msg1_fdm_idx_2
            ),
            48
        )

        self.assertEqual(
            tools.compute_pusch_rbs_occupied_by_prach(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=self.prach_config_idx_1,
                l_ra=self.l_ra_2,
                delta_f_ra_hz=self.delta_f_ra_hz_4,
                nr_scs_hz=self.scs_hz_4,
                msg1_fdm_idx=self.msg1_fdm_idx_3
            ),
            56
        )

    def test_compute_prach_preamble_format(self):
        """Test computing the PRACH preamble format.

        The following combinations are tested:

        | Frequency Range | Duplex Mode | PRACH Config Index | PRACH Preamble Format |
        |-----------------|-------------|--------------------|-----------------------|
        | FR1             | FDD         | 0                  | 0                     |
        | FR1             | FDD         | 28                 | 1                     |
        | FR1             | FDD         | 53                 | 2                     |
        | FR1             | FDD         | 60                 | 3                     |
        | FR1             | FDD         | 87                 | A1                    |
        | FR1             | FDD         | 108                | A1/B1                 |
        | FR1             | FDD         | 117                | A2                    |
        | FR1             | FDD         | 137                | A2/B2                 |
        | FR1             | FDD         | 147                | A3                    |
        | FR1             | FDD         | 167                | A3/B3                 |
        | FR1             | FDD         | 177                | B1                    |
        | FR1             | FDD         | 198                | B4                    |
        | FR1             | FDD         | 219                | C0                    |
        | FR1             | FDD         | 255                | C2                    |
        | FR1             | TDD         | 0                  | 0                     |
        | FR1             | TDD         | 28                 | 1                     |
        | FR1             | TDD         | 34                 | 2                     |
        | FR1             | TDD         | 40                 | 3                     |
        | FR1             | TDD         | 67                 | A1                    |
        | FR1             | TDD         | 87                 | A2                    |
        | FR1             | TDD         | 110                | A3                    |
        | FR1             | TDD         | 133                | B1                    |
        | FR1             | TDD         | 145                | B4                    |
        | FR1             | TDD         | 169                | C0                    |
        | FR1             | TDD         | 189                | C2                    |
        | FR1             | TDD         | 211                | A1/B1                 |
        | FR1             | TDD         | 226                | A2/B2                 |
        | FR1             | TDD         | 241                | A3/B3                 |
        | FR2             | TDD         | 262                | 0                     |
        | FR2             | TDD         | 0                  | A1                    |
        | FR2             | TDD         | 29                 | A2                    |
        | FR2             | TDD         | 59                 | A3                    |
        | FR2             | TDD         | 89                 | B1                    |
        | FR2             | TDD         | 112                | B4                    |
        | FR2             | TDD         | 144                | C0                    |
        | FR2             | TDD         | 173                | C2                    |
        | FR2             | TDD         | 202                | A1/B1                 |
        | FR2             | TDD         | 220                | A2/B2                 |
        | FR2             | TDD         | 255                | A3/B3                 |

        """
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"
        self.duplex_mode_1 = "FDD"
        self.duplex_mode_2 = "TDD"

        # FR1, FDD

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=0
            ),
            '0'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=28
            ),
            '1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=53
            ),
            '2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=60
            ),
            '3'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=87
            ),
            'A1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=108
            ),
            'A1/B1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=117
            ),
            'A2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=137
            ),
            'A2/B2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=147
            ),
            'A3'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=167
            ),
            'A3/B3'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=177
            ),
            'B1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=198
            ),
            'B4'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=219
            ),
            'C0'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_1,
                prach_conf_idx=255
            ),
            'C2'
        )

        # FR1, TDD

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=0
            ),
            '0'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=28
            ),
            '1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=34
            ),
            '2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=40
            ),
            '3'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=67
            ),
            'A1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=87
            ),
            'A2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=110
            ),
            'A3'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=133
            ),
            'B1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=145
            ),
            'B4'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=169
            ),
            'C0'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=189
            ),
            'C2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=211
            ),
            'A1/B1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=226
            ),
            'A2/B2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=241
            ),
            'A3/B3'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_1,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=262
            ),
            '0'
        )

        # FR2, TDD

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=0
            ),
            'A1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=29
            ),
            'A2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=59
            ),
            'A3'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=89
            ),
            'B1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=112
            ),
            'B4'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=144
            ),
            'C0'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=173
            ),
            'C2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=202
            ),
            'A1/B1'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=220
            ),
            'A2/B2'
        )

        self.assertEqual(
            tools.compute_prach_preamble_format(
                nr_freq_range=self.freq_range_2,
                nr_duplex_mode=self.duplex_mode_2,
                prach_conf_idx=255
            ),
            'A3/B3'
        )

    def test_compute_maximum_gnb_cell_radius(self):
        """Test computing the maximum gNB cell radius.

        The following combinations are tested:

        | PRACH Preamble Format | L_RA | Δf_RA in Hz | Restricted Set Type | Extended Cyclic Prefix | Channel Bandwidth in Hz | Frequency Range | Maximum gNB Cell Radius |
        |-----------------------|------|-------------|---------------------|------------------------|-------------------------|-----------------|-------------------------|
        | 0                     | 839  | 1250        | ""                  | False                  | 40000000                | FR1             | 11887.07                |
        | 0                     | 839  | 1250        | "A"                 | False                  | 40000000                | FR1             | 12887.57                |
        | 0                     | 839  | 1250        | "B"                 | False                  | 40000000                | FR1             | 12887.57                |
        | 1                     | 839  | 1250        | ""                  | False                  | 40000000                | FR1             | 58481.75                |
        | 2                     | 839  | 1250        | ""                  | False                  | 40000000                | FR1             | 15603.21                |
        | 3                     | 839  | 5000        | ""                  | False                  | 40000000                | FR1             | 13566.48                |
        | 3                     | 839  | 5000        | "A"                 | False                  | 40000000                | FR1             | 7063.23                 |
        | 3                     | 839  | 5000        | "B"                 | False                  | 40000000                | FR1             | 3490.02                 |
        | A1                    | 139  | 15000       | ""                  | False                  | 40000000                | FR1             | -39.32                  |
        | A2                    | 139  | 30000       | ""                  | False                  | 40000000                | FR1             | 519.24                  |
        | A2                    | 571  | 30000       | ""                  | False                  | 40000000                | FR1             | 294.92                  |
        | A3                    | 139  | 60000       | ""                  | False                  | 40000000                | FR1             | 475.45                  |
        | B2                    | 1151 | 120000      | ""                  | False                  | 400000000               | FR2             | -1227.29                |

        """
        self.prach_preamble_format_1 = "0"
        self.prach_preamble_format_2 = "1"
        self.prach_preamble_format_3 = "2"
        self.prach_preamble_format_4 = "3"
        self.prach_preamble_format_5 = "A1"
        self.prach_preamble_format_6 = "A2"
        self.prach_preamble_format_7 = "A3"
        self.prach_preamble_format_8 = "B2"
        self.l_ra_1 = 839
        self.l_ra_2 = 139
        self.l_ra_3 = 571
        self.l_ra_4 = 1_151
        self.delta_f_ra_hz_1 = 1_250
        self.delta_f_ra_hz_2 = 5_000
        self.delta_f_ra_hz_3 = 15_000
        self.delta_f_ra_hz_4 = 30_000
        self.delta_f_ra_hz_5 = 60_000
        self.delta_f_ra_hz_6 = 120_000
        self.restricted_set_str_1 = ""
        self.restricted_set_str_2 = "A"
        self.restricted_set_str_3 = "B"
        self.cyclic_prefix_extended_bool_1 = False
        self.cyclic_prefix_extended_bool_2 = True
        self.channel_bw_hz_1 = 40_000_000
        self.channel_bw_hz_2 = 400_000_000
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_1,
                    l_ra=self.l_ra_1,
                    delta_f_ra_hz=self.delta_f_ra_hz_1,
                    restricted_set_str=self.restricted_set_str_1,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            11_887.07
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_1,
                    l_ra=self.l_ra_1,
                    delta_f_ra_hz=self.delta_f_ra_hz_1,
                    restricted_set_str=self.restricted_set_str_2,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            12_887.57
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_1,
                    l_ra=self.l_ra_1,
                    delta_f_ra_hz=self.delta_f_ra_hz_1,
                    restricted_set_str=self.restricted_set_str_3,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            12_887.57
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_2,
                    l_ra=self.l_ra_1,
                    delta_f_ra_hz=self.delta_f_ra_hz_1,
                    restricted_set_str=self.restricted_set_str_1,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            58_481.75
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_3,
                    l_ra=self.l_ra_1,
                    delta_f_ra_hz=self.delta_f_ra_hz_1,
                    restricted_set_str=self.restricted_set_str_1,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            15_603.21
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_4,
                    l_ra=self.l_ra_1,
                    delta_f_ra_hz=self.delta_f_ra_hz_2,
                    restricted_set_str=self.restricted_set_str_1,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            13_566.48
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_4,
                    l_ra=self.l_ra_1,
                    delta_f_ra_hz=self.delta_f_ra_hz_2,
                    restricted_set_str=self.restricted_set_str_2,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            7_063.23
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_4,
                    l_ra=self.l_ra_1,
                    delta_f_ra_hz=self.delta_f_ra_hz_2,
                    restricted_set_str=self.restricted_set_str_3,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            3_490.02
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_5,
                    l_ra=self.l_ra_2,
                    delta_f_ra_hz=self.delta_f_ra_hz_3,
                    restricted_set_str=self.restricted_set_str_1,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            -39.32
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_6,
                    l_ra=self.l_ra_2,
                    delta_f_ra_hz=self.delta_f_ra_hz_4,
                    restricted_set_str=self.restricted_set_str_1,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            519.54
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_6,
                    l_ra=self.l_ra_3,
                    delta_f_ra_hz=self.delta_f_ra_hz_4,
                    restricted_set_str=self.restricted_set_str_1,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_1,
                    freq_range=self.freq_range_1
                ),
                2
            ),
            294.92
        )

        self.assertEqual(
            np.round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=self.prach_preamble_format_8,
                    l_ra=self.l_ra_4,
                    delta_f_ra_hz=self.delta_f_ra_hz_6,
                    restricted_set_str=self.restricted_set_str_1,
                    cyclic_prefix_extended_bool=self.cyclic_prefix_extended_bool_1,
                    channel_bw_hz=self.channel_bw_hz_2,
                    freq_range=self.freq_range_2
                ),
                2
            ),
            -1_227.29
        )

    def test_compute_prach_cyclic_prefix_duration(self):
        """Test computing the OFDM symbol cyclic prefix duration in FFT samples for the Physical Random Access Channel (PRACH).

        | PRACH Preamble Format | Cyclic Prefix duration in FFT symbols |
        | --------------------- | ------------------------------------- |
        |                     0 |                                  3168 |
        |                     1 |                                 21024 |
        |                     2 |                                  4688 |
        |                     3 |                                  3168 |
        |                    A1 |                                   288 |
        |                    A2 |                                   576 |
        |                    A3 |                                   864 |
        |                    B2 |                                   360 |
        |                    C2 |                                  2048 |

        """
        self.prach_preamble_format_1 = "0"
        self.prach_preamble_format_2 = "1"
        self.prach_preamble_format_3 = "2"
        self.prach_preamble_format_4 = "3"
        self.prach_preamble_format_5 = "A1"
        self.prach_preamble_format_6 = "A2"
        self.prach_preamble_format_7 = "A3"
        self.prach_preamble_format_8 = "B2"
        self.prach_preamble_format_9 = "C2"

        self.assertEqual(
            tools.compute_prach_cyclic_prefix_duration(
                self.prach_preamble_format_1
            ),
            3_168
        )

        self.assertEqual(
            tools.compute_prach_cyclic_prefix_duration(
                self.prach_preamble_format_2
            ),
            21_024
        )

        self.assertEqual(
            tools.compute_prach_cyclic_prefix_duration(
                self.prach_preamble_format_3
            ),
            4_688
        )

        self.assertEqual(
            tools.compute_prach_cyclic_prefix_duration(
                self.prach_preamble_format_4
            ),
            3_168
        )

        self.assertEqual(
            tools.compute_prach_cyclic_prefix_duration(
                self.prach_preamble_format_5
            ),
            288
        )

        self.assertEqual(
            tools.compute_prach_cyclic_prefix_duration(
                self.prach_preamble_format_6
            ),
            576
        )

        self.assertEqual(
            tools.compute_prach_cyclic_prefix_duration(
                self.prach_preamble_format_7
            ),
            864
        )

        self.assertEqual(
            tools.compute_prach_cyclic_prefix_duration(
                self.prach_preamble_format_8
            ),
            360
        )

        self.assertEqual(
            tools.compute_prach_cyclic_prefix_duration(
                self.prach_preamble_format_9
            ),
            2_048
        )


class TestToolsPUSCH(unittest.TestCase):
    """Test the tool functions regarding PUSCH.

    """

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        self.mu_1 = 1
        self.mu_2 = 7
        self.cyclic_prefix_extended_bool_1 = False
        self.cyclic_prefix_extended_bool_2 = True
        self.longer_symbol_duration_bool_1 = False
        self.longer_symbol_duration_bool_2 = True
        self.channel_bw_hz_1 = 40_000_000
        self.channel_bw_hz_2 = 400_000_000
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"
        self.freq_range_3 = "wrong FR"

        self.assertRaises(ValueError, tools.compute_pusch_cyclic_prefix_duration, self.mu_2, self.cyclic_prefix_extended_bool_1, self.longer_symbol_duration_bool_1, self.channel_bw_hz_1, self.freq_range_1)
        self.assertRaises(ValueError, tools.compute_pusch_cyclic_prefix_duration, self.mu_1, self.cyclic_prefix_extended_bool_1, self.longer_symbol_duration_bool_1, self.channel_bw_hz_1, self.freq_range_3)
        self.assertRaises(ValueError, tools.compute_pusch_cyclic_prefix_duration, self.mu_1, self.cyclic_prefix_extended_bool_1, self.longer_symbol_duration_bool_1, self.channel_bw_hz_1, self.freq_range_2)
        self.assertRaises(ValueError, tools.compute_pusch_cyclic_prefix_duration, self.mu_1, self.cyclic_prefix_extended_bool_1, self.longer_symbol_duration_bool_1, self.channel_bw_hz_2, self.freq_range_1)
        self.assertRaises(ValueError, tools.compute_pusch_cyclic_prefix_duration, self.mu_1, self.cyclic_prefix_extended_bool_2, self.longer_symbol_duration_bool_2, self.channel_bw_hz_1, self.freq_range_1)

    def test_var_types(self):
        """Test the parameter types.

        """
        self.mu_1 = 1
        self.cyclic_prefix_extended_bool_1 = False
        self.longer_symbol_duration_bool_1 = False
        self.channel_bw_hz_1 = 40_000_000
        self.freq_range_1 = "FR1"

        self.assertRaises(TypeError, tools.compute_pusch_cyclic_prefix_duration, "not int", self.cyclic_prefix_extended_bool_1, self.longer_symbol_duration_bool_1, self.channel_bw_hz_1, self.freq_range_1)
        self.assertRaises(TypeError, tools.compute_pusch_cyclic_prefix_duration, self.mu_1, "not bool", self.longer_symbol_duration_bool_1, self.channel_bw_hz_1, self.freq_range_1)
        self.assertRaises(TypeError, tools.compute_pusch_cyclic_prefix_duration, self.mu_1, self.cyclic_prefix_extended_bool_1, "not bool", self.channel_bw_hz_1, self.freq_range_1)
        self.assertRaises(TypeError, tools.compute_pusch_cyclic_prefix_duration, self.mu_1, self.cyclic_prefix_extended_bool_1, self.longer_symbol_duration_bool_1, "not int", self.freq_range_1)
        self.assertRaises(TypeError, tools.compute_pusch_cyclic_prefix_duration, self.mu_1, self.cyclic_prefix_extended_bool_1, self.longer_symbol_duration_bool_1, self.channel_bw_hz_1, 0)

    def test_compute_pusch_cyclic_prefix_duration(self):
        """Test computing the OFDM symbol cyclic prefix duration in FFT samples for the Physical Uplink Shared Channel (PUSCH).

        mu: int, cyclic_prefix_extended_bool: bool, longer_symbol_duration_bool: bool, channel_bw_hz: int, freq_range: str
        n_cp_l_mu

        |  µ  | Cyclic Prefix Extended | Longer Symbol Duration | Channel Bandwidth | Frequency Range | N_CP,l^µ |
        | --- | ---------------------- | ---------------------- | ----------------- | --------------- | -------- |
        |   0 |                  False |                  False |            40 MHz |             FR1 |      288 |
        |   0 |                  False |                   True |            40 MHz |             FR1 |      320 |
        |   1 |                  False |                  False |            40 MHz |             FR1 |      144 |
        |   1 |                  False |                   True |            40 MHz |             FR1 |      176 |
        |   2 |                  False |                  False |            40 MHz |             FR1 |       72 |
        |   2 |                  False |                   True |            40 MHz |             FR1 |      104 |
        |   2 |                   True |                  False |            40 MHz |             FR1 |      328 |
        |   2 |                   True |                   True |            40 MHz |             FR1 |      360 |
        |   2 |                  False |                  False |           200 MHz |             FR2 |      288 |
        |   2 |                  False |                   True |           200 MHz |             FR2 |      416 |
        |   2 |                   True |                  False |           200 MHz |             FR2 |     1312 |
        |   2 |                   True |                   True |           200 MHz |             FR2 |     1440 |
        |   3 |                  False |                  False |           400 MHz |             FR2 |      288 |
        |   3 |                  False |                   True |           400 MHz |             FR2 |      544 |
        |   5 |                  False |                  False |           400 MHz |             FR2 |       72 |
        |   5 |                  False |                   True |           400 MHz |             FR2 |      328 |
        |   6 |                  False |                  False |           400 MHz |             FR2 |       36 |
        |   6 |                  False |                   True |           400 MHz |             FR2 |      292 |

        """
        self.mu_1 = 0
        self.mu_2 = 1
        self.mu_3 = 2
        self.mu_4 = 3
        self.mu_5 = 5
        self.mu_6 = 6
        self.cyclic_prefix_extended_bool_1 = False
        self.cyclic_prefix_extended_bool_2 = True
        self.longer_symbol_duration_bool_1 = False
        self.longer_symbol_duration_bool_2 = True
        self.channel_bw_hz_1 = 40_000_000
        self.channel_bw_hz_2 = 200_000_000
        self.channel_bw_hz_3 = 400_000_000
        self.freq_range_1 = "FR1"
        self.freq_range_2 = "FR2"

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_1,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_1,
                self.channel_bw_hz_1,
                self.freq_range_1
            ),
            288
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_1,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_2,
                self.channel_bw_hz_1,
                self.freq_range_1
            ),
            320
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_2,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_1,
                self.channel_bw_hz_1,
                self.freq_range_1
            ),
            144
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_2,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_2,
                self.channel_bw_hz_1,
                self.freq_range_1
            ),
            176
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_3,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_1,
                self.channel_bw_hz_1,
                self.freq_range_1
            ),
            72
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_3,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_2,
                self.channel_bw_hz_1,
                self.freq_range_1
            ),
            104
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_3,
                self.cyclic_prefix_extended_bool_2,
                self.longer_symbol_duration_bool_1,
                self.channel_bw_hz_1,
                self.freq_range_1
            ),
            256
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_3,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_1,
                self.channel_bw_hz_2,
                self.freq_range_2
            ),
            288
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_3,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_2,
                self.channel_bw_hz_2,
                self.freq_range_2
            ),
            416
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_3,
                self.cyclic_prefix_extended_bool_2,
                self.longer_symbol_duration_bool_1,
                self.channel_bw_hz_2,
                self.freq_range_2
            ),
            1024
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_4,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_1,
                self.channel_bw_hz_3,
                self.freq_range_2
            ),
            288
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_4,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_2,
                self.channel_bw_hz_3,
                self.freq_range_2
            ),
            544
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_5,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_1,
                self.channel_bw_hz_3,
                self.freq_range_2
            ),
            72
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_5,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_2,
                self.channel_bw_hz_3,
                self.freq_range_2
            ),
            328
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_6,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_1,
                self.channel_bw_hz_3,
                self.freq_range_2
            ),
            36
        )

        self.assertEqual(
            tools.compute_pusch_cyclic_prefix_duration(
                self.mu_6,
                self.cyclic_prefix_extended_bool_1,
                self.longer_symbol_duration_bool_2,
                self.channel_bw_hz_3,
                self.freq_range_2
            ),
            292
        )


@pytest.mark.slow
class TestBuildPRACHSSBCollisionFreeTables(unittest.TestCase):
    """Test creating collision-free combinations between PRACH Occasions and SSB time-domain pattern.

    """
    def assertDataframeEqual(self, a, b):
        try:
            pd_testing.assert_frame_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def assertSeriesEqual(self, a, b):
        try:
            pd_testing.assert_series_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        duplex_mode_1 = "FDD"
        duplex_mode_2 = "wrong DD"
        delta_f_ra_hz_1 = 30_000
        delta_f_ra_hz_2 = 240_000
        delta_f_ra_hz_3 = 60_000
        delta_f_ra_hz_4 = 120_000
        delta_f_ra_hz_5 = 480_000
        delta_f_ra_hz_6 = 960_000

        self.assertRaises(ValueError, build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations, duplex_mode_2, delta_f_ra_hz_1)
        self.assertRaises(ValueError, build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations, duplex_mode_1, delta_f_ra_hz_2)

        self.assertRaises(ValueError, build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations, duplex_mode_1, delta_f_ra_hz_3)
        self.assertRaises(ValueError, build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations, duplex_mode_1, delta_f_ra_hz_4)
        self.assertRaises(ValueError, build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations, duplex_mode_1, delta_f_ra_hz_5)
        self.assertRaises(ValueError, build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations, duplex_mode_1, delta_f_ra_hz_6)

    def test_var_types(self):
        """Test the parameter types.

        """
        duplex_mode = "FDD"
        delta_f_ra_hz = 30_000
        all_rach_occasions = set()
        prach_occasions_absolute_occupied_symbols_df = pd.DataFrame()
        symbols_per_frame = 14 * 10
        freq_range = "FR1"

        self.assertRaises(TypeError, build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations, 0, delta_f_ra_hz)
        self.assertRaises(TypeError, build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations, duplex_mode, "not int")

        self.assertRaises(TypeError, build_prach_ssb_collision_free_tables.plot_prach_occasions, "not set", prach_occasions_absolute_occupied_symbols_df, symbols_per_frame, freq_range, duplex_mode, delta_f_ra_hz)
        self.assertRaises(TypeError, build_prach_ssb_collision_free_tables.plot_prach_occasions, all_rach_occasions, "not pandas DataFrame", symbols_per_frame, freq_range, duplex_mode, delta_f_ra_hz)
        self.assertRaises(TypeError, build_prach_ssb_collision_free_tables.plot_prach_occasions, all_rach_occasions, prach_occasions_absolute_occupied_symbols_df, "not int", freq_range, duplex_mode, delta_f_ra_hz)
        self.assertRaises(TypeError, build_prach_ssb_collision_free_tables.plot_prach_occasions, all_rach_occasions, prach_occasions_absolute_occupied_symbols_df, symbols_per_frame, 0, duplex_mode, delta_f_ra_hz)
        self.assertRaises(TypeError, build_prach_ssb_collision_free_tables.plot_prach_occasions, all_rach_occasions, prach_occasions_absolute_occupied_symbols_df, symbols_per_frame, freq_range, 0, delta_f_ra_hz)
        self.assertRaises(TypeError, build_prach_ssb_collision_free_tables.plot_prach_occasions, all_rach_occasions, prach_occasions_absolute_occupied_symbols_df, symbols_per_frame, freq_range, duplex_mode, "not int")

    def test_create_collision_free_prach_ssb_combinations(self):
        """Test creating CSV tables of all collision-free combinations between PRACH Occasions and SSB time-domain pattern.

        """
        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='FDD',
                delta_f_ra_hz=1250
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='FDD',
                delta_f_ra_hz=5_000
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='FDD',
                delta_f_ra_hz=15_000
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='FDD',
                delta_f_ra_hz=30_000
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='TDD',
                delta_f_ra_hz=1250
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='TDD',
                delta_f_ra_hz=5_000
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='TDD',
                delta_f_ra_hz=15_000
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='TDD',
                delta_f_ra_hz=30_000
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='TDD',
                delta_f_ra_hz=60_000
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='TDD',
                delta_f_ra_hz=120_000
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='TDD',
                delta_f_ra_hz=480_000
            ),
            True
        )

        self.assertEqual(
            build_prach_ssb_collision_free_tables.create_collision_free_prach_ssb_combinations(
                duplex_mode='TDD',
                delta_f_ra_hz=960_000
            ),
            True
        )


@pytest.mark.slow
class TestBuildLongGuardTimePRACHPUSCHCombinationTables(unittest.TestCase):
    """Test creating combinations of PRACH configuration and PUSCH subcarrier spacing with long Guard Times.

    """
    def assertDataframeEqual(self, a, b):
        try:
            pd_testing.assert_frame_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def assertSeriesEqual(self, a, b):
        try:
            pd_testing.assert_series_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        nr_freq_ranges_lst_1 = ['FR1', 'FR2']
        nr_freq_ranges_lst_2 = ['FR1', 'wrong FR']
        nr_duplex_modes_lst_1 = ['FDD', 'TDD']
        nr_duplex_modes_lst_2 = ['FDD', 'wrong DD']
        max_prach_conf_idx_1 = 262
        max_prach_conf_idx_2 = 263
        max_prach_conf_idx_3 = -1

        self.assertRaises(ValueError, build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables, nr_freq_ranges_lst_2, nr_duplex_modes_lst_1, max_prach_conf_idx_1)
        self.assertRaises(ValueError, build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables, nr_freq_ranges_lst_1, nr_duplex_modes_lst_2, max_prach_conf_idx_1)
        self.assertRaises(ValueError, build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables, nr_freq_ranges_lst_1, nr_duplex_modes_lst_1, max_prach_conf_idx_2)
        self.assertRaises(ValueError, build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables, nr_freq_ranges_lst_1, nr_duplex_modes_lst_1, max_prach_conf_idx_3)

    def test_var_types(self):
        """Test the parameter types.

        """
        nr_freq_ranges_lst = ['FR1', 'FR2']
        nr_duplex_modes_lst = ['FDD', 'TDD']
        max_prach_conf_idx = 262

        self.assertRaises(TypeError, build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables, "not list", nr_duplex_modes_lst, max_prach_conf_idx)
        self.assertRaises(TypeError, build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables, 0, nr_duplex_modes_lst, max_prach_conf_idx)
        self.assertRaises(TypeError, build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables, nr_freq_ranges_lst, "not list", max_prach_conf_idx)
        self.assertRaises(TypeError, build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables, nr_freq_ranges_lst, 0, max_prach_conf_idx)
        self.assertRaises(TypeError, build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables, nr_freq_ranges_lst, nr_duplex_modes_lst, "not int")

    def test_build_long_gt_prach_pusch_combi_tables(self):
        """Test building combination tables of PRACH and PUSCH configurations that lead to long Guard Times.

        """
        nr_freq_ranges_lst = ['FR1', 'FR2']
        nr_duplex_modes_lst = ['FDD', 'TDD']
        max_prach_conf_idx = 262

        self.assertEqual(
            build_long_guard_time_prach_pusch_combination_tables.build_long_gt_prach_pusch_combi_tables(
                nr_freq_ranges_lst=nr_freq_ranges_lst,
                nr_duplex_modes_lst=nr_duplex_modes_lst,
                max_prach_conf_idx=max_prach_conf_idx
            ),
            True
        )


@pytest.mark.slow
class TestBuildTaudDMaxRTDMaxTable(unittest.TestCase):
    """Test creating maximum delay spread and maximum round-trip delay from PRACH configuration and PUSCH subcarrier spacing combinations.

    """
    def assertDataframeEqual(self, a, b):
        try:
            pd_testing.assert_frame_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def assertSeriesEqual(self, a, b):
        try:
            pd_testing.assert_series_equal(left=a, right=b, check_names=False)
        except AssertionError as e:
            raise self.failureException() from e

    def test_var_ranges(self):
        """Test the parameter value ranges.

        """
        nr_freq_ranges_lst_1 = ['FR1', 'FR2']
        nr_freq_ranges_lst_2 = ['FR1', 'wrong FR']
        nr_duplex_modes_lst_1 = ['FDD', 'TDD']
        nr_duplex_modes_lst_2 = ['FDD', 'wrong DD']
        max_prach_conf_idx_1 = 262
        max_prach_conf_idx_2 = 263
        max_prach_conf_idx_3 = -1

        self.assertRaises(ValueError, build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table, nr_freq_ranges_lst_2, nr_duplex_modes_lst_1, max_prach_conf_idx_1)
        self.assertRaises(ValueError, build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table, nr_freq_ranges_lst_1, nr_duplex_modes_lst_2, max_prach_conf_idx_1)
        self.assertRaises(ValueError, build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table, nr_freq_ranges_lst_1, nr_duplex_modes_lst_1, max_prach_conf_idx_2)
        self.assertRaises(ValueError, build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table, nr_freq_ranges_lst_1, nr_duplex_modes_lst_1, max_prach_conf_idx_3)

    def test_var_types(self):
        """Test the parameter types.

        """
        nr_freq_ranges_lst = ['FR1', 'FR2']
        nr_duplex_modes_lst = ['FDD', 'TDD']
        max_prach_conf_idx = 262

        self.assertRaises(TypeError, build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table, "not list", nr_duplex_modes_lst, max_prach_conf_idx)
        self.assertRaises(TypeError, build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table, 0, nr_duplex_modes_lst, max_prach_conf_idx)
        self.assertRaises(TypeError, build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table, nr_freq_ranges_lst, "not list", max_prach_conf_idx)
        self.assertRaises(TypeError, build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table, nr_freq_ranges_lst, 0, max_prach_conf_idx)
        self.assertRaises(TypeError, build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table, nr_freq_ranges_lst, nr_duplex_modes_lst, "not int")

    def test_build_tau_d_max_rtd_max_table(self):
        """Test building combination table for maximum delay spread and maximum round-trip delay from PRACH configurations and PUSCH subcarrier spacing configurations.

        """
        nr_freq_ranges_lst = ['FR1', 'FR2']
        nr_duplex_modes_lst = ['FDD', 'TDD']
        max_prach_conf_idx = 262

        self.assertEqual(
            build_tau_d_max_rtd_max_table.build_tau_d_max_rtd_max_table(
                nr_freq_ranges_lst=nr_freq_ranges_lst,
                nr_duplex_modes_lst=nr_duplex_modes_lst,
                max_prach_conf_idx=max_prach_conf_idx
            ),
            True
        )


if __name__ == "__main__":
    unittest.main()  # Not reached by tests. Only targets code errors.

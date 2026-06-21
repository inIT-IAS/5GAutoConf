#!/usr/bin/env python

# Copyright (c) 2026 Niels Hendrik Fliedner
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL
# was not distributed with this file, You can obtain one at
# https://mozilla.org/MPL/2.0/.

"""Create maximum delay spread and maximum round-trip delay from PRACH configuration and PUSCH subcarrier spacing combinations.

Usage: build_tau_d_max_rtd_max_table.py

"""
import logging
import os
import pandas as pd
import math

from configurator import tools
from configurator import tables

logger = logging.getLogger(__name__)


def build_tau_d_max_rtd_max_table(nr_freq_ranges_lst: list, nr_duplex_modes_lst: list, max_prach_conf_idx: int):
    """Build combination table for maximum delay spread and maximum round-trip delay from PRACH configurations and PUSCH subcarrier spacing configurations.

    """
    if not isinstance(nr_freq_ranges_lst, list):
        raise TypeError("nr_freq_ranges_lst should be of type list, but is {0}!".format(type(nr_freq_ranges_lst)))
    if not isinstance(nr_duplex_modes_lst, list):
        raise TypeError("nr_duplex_modes_lst should be of type list, but is {0}!".format(type(nr_duplex_modes_lst)))
    if not isinstance(max_prach_conf_idx, int):
        raise TypeError("max_prach_conf_idx should be of type int, but is {0}!".format(type(max_prach_conf_idx)))

    if not set(nr_freq_ranges_lst).issubset(["FR1", "FR2"]):
        raise ValueError("An nr_freq_ranges_lst of {0} is not supported!".format(nr_freq_ranges_lst))
    if not set(nr_duplex_modes_lst).issubset(["TDD", "FDD"]):
        raise ValueError("An nr_duplex_modes_lst of {0} is not supported!".format(nr_duplex_modes_lst))
    if max_prach_conf_idx < 0 or max_prach_conf_idx > 262:
        raise ValueError("A max_prach_conf_idx of {0} is not supported!".format(max_prach_conf_idx))

    build_table_success = False
    counter = 0
    value_error_counter = 0
    columns = [
        "Frequency Range",
        "Duplex Mode",
        "PRACH Config. Index",
        "PRACH Format",
        "Δf_RA in Hz (PRACH)",
        "PRACH CP in µs",
        "PRACH GT in µs",
        "PRACH GT is long GT",
        "Δf in HZ (PUSCH)",
        "PUSCH CP in µs",
        "Max delay spread in µs",
        "Max round-trip delay in µs",
        "Max gNB cell radius in m"
    ]
    rows = []
    for nr_freq_range in nr_freq_ranges_lst:
        for nr_duplex_mode in nr_duplex_modes_lst:
            for prach_conf_idx in range(0, max_prach_conf_idx + 1):
                for delta_f_ra_hz in [*tools.DELTA_F_RA_HZ]:
                    for nr_scs_hz in [*tools.SCS_HZ_TO_NUMEROLOGY]:
                        for cyclic_prefix_extended_bool in [False, True]:
                            for longer_symbol_duration_bool in [False, True]:
                                if nr_freq_range == "FR1":
                                    nr_cbw_hz = 40 * 1000 * 1000
                                elif nr_freq_range == "FR2":
                                    nr_cbw_hz = 400 * 1000 * 1000

                                try:
                                    # PRACH
                                    prach_guard_times_dict = tools.compute_prach_guard_times(
                                        nr_freq_range=nr_freq_range,
                                        nr_duplex_mode=nr_duplex_mode,
                                        prach_conf_idx=prach_conf_idx,
                                        delta_f_ra_hz=delta_f_ra_hz,
                                        delta_f_hz=nr_scs_hz
                                    )
                                    for key, value in prach_guard_times_dict.items():
                                        if key == "Short GT in s":
                                            prach_guard_time_s = value
                                            prach_long_gt_bool = False
                                        elif key == "Long GT in s":
                                            if value is not None:
                                                prach_guard_time_s = value
                                                prach_long_gt_bool = True
                                            else:
                                                continue
                                        prach_preamble_format = tools.compute_prach_preamble_format(
                                            nr_freq_range=nr_freq_range,
                                            nr_duplex_mode=nr_duplex_mode,
                                            prach_conf_idx=prach_conf_idx
                                        )

                                        prach_cyclic_prefix_duration = tools.compute_prach_cyclic_prefix_duration(
                                            prach_preamble_format=prach_preamble_format
                                        )
                                        if delta_f_ra_hz in [1250, 5000]:
                                            prach_cyclic_prefix_duration_s = prach_cyclic_prefix_duration * tools.T_C_S * tools.KAPPA
                                        else:
                                            mu_ra = tools.SCS_HZ_TO_NUMEROLOGY[delta_f_ra_hz]
                                            prach_cyclic_prefix_duration_s = prach_cyclic_prefix_duration * tools.T_C_S * tools.KAPPA * math.pow(2., -1. * mu_ra)

                                        # PUSCH
                                        pusch_cyclic_prefix_duration_s = tools.compute_pusch_cyclic_prefix_duration(
                                            mu=tools.SCS_HZ_TO_NUMEROLOGY[nr_scs_hz],
                                            cyclic_prefix_extended_bool=cyclic_prefix_extended_bool,
                                            longer_symbol_duration_bool=longer_symbol_duration_bool,
                                            channel_bw_hz=nr_cbw_hz,
                                            freq_range=nr_freq_range
                                        ) * tools.T_C_S * tools.KAPPA

                                        # Compare
                                        max_rtd_s = prach_cyclic_prefix_duration_s + prach_guard_time_s - pusch_cyclic_prefix_duration_s
                                        max_gnb_cell_radius_m = max_rtd_s * tools.C_M_PER_S / 2
                                        if nr_freq_range == "FR1" and nr_duplex_mode == "FDD":
                                            row = tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=prach_conf_idx)
                                        elif nr_freq_range == "FR1" and nr_duplex_mode == "TDD":
                                            row = tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=prach_conf_idx)
                                        elif nr_freq_range == "FR2" and nr_duplex_mode == "TDD":
                                            row = tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=prach_conf_idx)
                                        counter += 1
                                        df_row = {
                                            "Frequency Range": nr_freq_range,
                                            "Duplex Mode": nr_duplex_mode,
                                            "PRACH Config. Index": prach_conf_idx,
                                            "PRACH Format": str(row["Preamble format"][0]),
                                            "Δf_RA in Hz (PRACH)": delta_f_ra_hz,
                                            "PRACH CP in µs": prach_cyclic_prefix_duration_s * 1000000.,
                                            "PRACH GT in µs": prach_guard_time_s * 1000000.,
                                            "PRACH GT is long GT": prach_long_gt_bool,
                                            "Δf in HZ (PUSCH)": nr_scs_hz,
                                            "PUSCH CP in µs": pusch_cyclic_prefix_duration_s * 1000000.,
                                            "Max delay spread in µs": pusch_cyclic_prefix_duration_s * 1000000.,
                                            "Max round-trip delay in µs": max_rtd_s * 1000000.,
                                            "Max gNB cell radius in m": max_gnb_cell_radius_m
                                        }
                                        rows.append(df_row)
                                        logger.debug(df_row)
                                except ValueError as ve:
                                    value_error_counter += 1
                                    logger.debug(ve)
                                    logger.debug("continuing...")
                                    continue
    logger.debug("{0} round-trip delay configurations calculated".format(counter))
    logger.debug("Skipped {0} Value Errors".format(value_error_counter))
    df = pd.DataFrame(rows, columns=columns)
    if df.shape[0] != 0:
        build_table_success = True
    csv_filepath = os.path.abspath(
        os.path.join(
            "tables",
            "tau_d_max_RTD_max_Configs.csv"
        )
    )
    os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
    df.to_csv(csv_filepath, index=False, encoding="utf-8")
    logger.info("Wrote {0} entries with tau_d,max and RTD_max to {1}". format(counter, csv_filepath))

    return build_table_success


def main():
    """The main function of build_prach_ssb_collision_free_tables.py.
    This only runs when calling the script directly.

    """
    # Not reached by tests.
    logger.info("Creating delay spread and maximum round-trip delay from PRACH configuration and PUSCH subcarrier spacing combinations.\nThis might take a while...")
    build_tau_d_max_rtd_max_table(
        nr_freq_ranges_lst=['FR1', 'FR2'],
        nr_duplex_modes_lst=['FDD', 'TDD'],
        max_prach_conf_idx=262
    )


if __name__ == '__main__':
    main()  # Not reached by tests.

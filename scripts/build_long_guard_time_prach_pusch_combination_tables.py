#!/usr/bin/env python

# Copyright (c) 2026 Niels Hendrik Fliedner
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL
# was not distributed with this file, You can obtain one at
# https://mozilla.org/MPL/2.0/.

"""Create combinations of PRACH configuration and PUSCH subcarrier spacing with long Guard Times.

Usage: build_long_guard_time_prach_pusch_combination_tables.py

"""
import logging
import os
import pandas as pd

from configurator import tools
from configurator import tables

logger = logging.getLogger(__name__)


def build_long_gt_prach_pusch_combi_tables(nr_freq_ranges_lst: list, nr_duplex_modes_lst: list, max_prach_conf_idx: int):
    """Build combination tables of PRACH and PUSCH configurations that lead to long Guard Times.

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

    build_tables_success = False
    columns = [
        "Frequency Range",
        "Duplex Mode",
        "PRACH Config. Index",
        "PRACH Format",
        "Δf_RA in Hz (PRACH)",
        "Δf in HZ (PUSCH)",
        "Short GT in µs",
        "Round-trip distance for short GT in m",
        "Long GT in µs",
        "Round-trip distance for long GT in m"
    ]
    rows = []
    counter = 0
    for nr_freq_range in nr_freq_ranges_lst:
        for nr_duplex_mode in nr_duplex_modes_lst:
            for prach_conf_idx in range(0, max_prach_conf_idx + 1):
                for delta_f_ra_hz in tools.DELTA_F_RA_HZ:
                    for delta_f_hz in [*tools.SCS_HZ_TO_NUMEROLOGY]:
                        try:
                            prach_guard_times_dict = tools.compute_prach_guard_times(
                                nr_freq_range=nr_freq_range,
                                nr_duplex_mode=nr_duplex_mode,
                                prach_conf_idx=prach_conf_idx,
                                delta_f_ra_hz=delta_f_ra_hz,
                                delta_f_hz=delta_f_hz
                            )
                            if prach_guard_times_dict["Long GT in s"] is not None:
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
                                    "Δf in HZ (PUSCH)": delta_f_hz,
                                    "Short GT in µs": prach_guard_times_dict["Short GT in s"] * 1000000,
                                    "Round-trip distance for short GT in m": tools.C_M_PER_S * prach_guard_times_dict["Short GT in s"] / 2,
                                    "Long GT in µs": prach_guard_times_dict["Long GT in s"] * 1000000,
                                    "Round-trip distance for long GT in m": tools.C_M_PER_S * prach_guard_times_dict["Long GT in s"] / 2
                                }
                                rows.append(df_row)
                                logger.debug(df_row)
                        except ValueError as ve:
                            logger.debug(ve)
                            logger.debug("continuing...")
    long_gt_prach_pusch_combi_df = pd.DataFrame(rows, columns=columns)
    if long_gt_prach_pusch_combi_df.shape[0] != 0:
        build_tables_success = True
    csv_filepath = os.path.abspath(
        os.path.join(
            "tables",
            "Long_GT_PRACH_PUSCH_Configs.csv"
        )
    )
    os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
    long_gt_prach_pusch_combi_df.to_csv(csv_filepath, index=False, encoding="utf-8")
    logger.info("Wrote {0} PRACH-PUSCH configurations with long GT to {1}". format(counter, csv_filepath))

    return build_tables_success


def main():
    """The main function of build_prach_ssb_collision_free_tables.py.
    This only runs when calling the script directly.

    """
    # Not reached by tests.
    logger.info("Creating combinations of PRACH configuration and PUSCH subcarrier spacing with long Guard Times.\nThis might take a while...")
    build_long_gt_prach_pusch_combi_tables(
        nr_freq_ranges_lst=['FR1', 'FR2'],
        nr_duplex_modes_lst=['FDD', 'TDD'],
        max_prach_conf_idx=262
    )


if __name__ == '__main__':
    main()  # Not reached by tests.

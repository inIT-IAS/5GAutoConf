#!/usr/bin/env python

# Copyright (c) 2026 Niels Hendrik Fliedner
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL
# was not distributed with this file, You can obtain one at
# https://mozilla.org/MPL/2.0/.

"""Create collision-free combinations between PRACH Occasions and SSB time-domain pattern.

Usage: build_prach_ssb_collision_free_tables.py

"""
import logging
import os
import pathlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def plot_prach_occasions(all_rach_occasions: set, prach_occasions_absolute_occupied_symbols_df: pd.DataFrame, symbols_per_frame: int, freq_range: str, duplex_mode: str, delta_f_ra_hz: int):
    """Plot the RACH occasions.

    Parameters
    ----------
    all_rach_occasions : set
        All RACH occasions.

    prach_occasions_absolute_occupied_symbols_df : pandas.DataFramepandas.DataFrame
        The DataFrame with absolute starting symbols of the PRACH occasions.
        Columns: 'PRACH configuration index', 'Subframe/slot number', 'PRACH occasions starting symbols absolute', 'PRACH duration', 'PRACH occasions all occupied symbols', 'Number of all occupied symbols', 'Number of symbols per Frame'.

    symbols_per_frame : int
        The number of OFDM symbols per frame.

    freq_range : str
        The designated frequency range.
        Includes FR1, FR2, FR2-1, and FR2-2.

    duplex_mode : str
        The duplex mode, either FDD or TDD.

    delta_f_ra_hz : int
        The subcarrier spacing of RACH Δf_RA.

    Returns
    -------
    prach_occasion_plot_success : bool
        True, if all steps of plotting finish without exception.

    Raises
    ------
    TypeError
        If all_rach_occasions is not of type set.
    TypeError
        If prach_occasions_absolute_occupied_symbols_df is not of type pandas.DataFrame.
    TypeError
        If symbols_per_frame is not of type int.
    TypeError
        If freq_range is not of type str.
    TypeError
        If duplex_mode is not of type str.
    TypeError
        If delta_f_ra_hz is not of type int.

    """
    if not isinstance(all_rach_occasions, set):
        raise TypeError("all_rach_occasions should be of type set, but is {0}!".format(type(all_rach_occasions)))
    if not isinstance(prach_occasions_absolute_occupied_symbols_df, pd.DataFrame):
        raise TypeError("prach_occasions_absolute_occupied_symbols_df should be of type pd.DataFrame, but is {0}!".format(type(prach_occasions_absolute_occupied_symbols_df)))
    if not isinstance(symbols_per_frame, int):
        raise TypeError("symbols_per_frame should be of type int, but is {0}!".format(type(symbols_per_frame)))
    if not isinstance(freq_range, str):
        raise TypeError("freq_range should be of type str, but is {0}!".format(type(freq_range)))
    if not isinstance(duplex_mode, str):
        raise TypeError("duplex_mode should be of type str, but is {0}!".format(type(duplex_mode)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))

    prach_occasion_plot_success = False
    try:
        logger.debug("Plotting RACH Occasions")

        sorted_rach_occasions = sorted(all_rach_occasions)
        index_to_pos = {index: pos for pos, index in enumerate(sorted_rach_occasions)}

        plot_data = np.zeros((len(prach_occasions_absolute_occupied_symbols_df), len(sorted_rach_occasions)))

        for row_idx, t in enumerate(prach_occasions_absolute_occupied_symbols_df['PRACH occasions all occupied symbols']):
            for idx in t:
                col_idx = index_to_pos[idx]
                plot_data[row_idx, col_idx] = 1  # Set to 1 to fill the box

        # Prevent Spyder from displaying the figure
        plt.switch_backend('Agg')

        plt.figure(figsize=(30, 15))
        plt.imshow(plot_data, aspect='auto', cmap='Greens', origin='lower')

        # Set axis labels and ticks
        plt.xlabel('PRACH Occasions')
        plt.ylabel('PRACH Configuration Index')

        # Set x-ticks to integer values
        plt.xticks(range(len(sorted_rach_occasions)), sorted_rach_occasions, rotation=90)

        # Set y-ticks to DataFrame indices
        plt.yticks(range(len(prach_occasions_absolute_occupied_symbols_df)), prach_occasions_absolute_occupied_symbols_df.index)

        # Display the plot
        plt.tight_layout()
        png_filepath = os.path.abspath(
            os.path.join(
                "plots", "PRACH_Occasions_{0}_{1}_{2}.png".format(freq_range, duplex_mode, delta_f_ra_hz)
            )

        )
        pdf_filepath = os.path.abspath(
            os.path.join(
                "plots", "PRACH_Occasions_{0}_{1}_{2}.pdf".format(freq_range, duplex_mode, delta_f_ra_hz)
            )
        )

        path = pathlib.Path("plots")
        path.mkdir(parents=True, exist_ok=True)
        plt.savefig(png_filepath, bbox_inches='tight')
        plt.savefig(pdf_filepath, bbox_inches='tight')
        plt.close()

        prach_occasion_plot_success = True
    except Exception as e:
        logger.error(e)  # Not reached by tests. Only targets code errors.
        prach_occasion_plot_success = False  # Not reached by tests. Only targets code errors.
    return prach_occasion_plot_success


def create_collision_free_prach_ssb_combinations(duplex_mode: str, delta_f_ra_hz: int):
    """Create CSV table files of all collision-free combinations between PRACH Occasions and SSB time-domain pattern.
    File names are separated into Duplex Mode, Frequency Range (FR1, FR2, FR2-1, FR2-2) and Delta f_RA.

    - TODO: Determine Raster for SSB when using different PRACH Occasions.
    - TODO: Repeat SSB blocks to allow overlay checks with longer PRACH occasions in, for example, FR2 at higher Subcarrier Spacings.
    - TODO: Add plots of prach_occasion_time_domain_occupied_symbols for testing purposes. Use tables.ts_38_211_table_4_3_2_1 to determine x-Axis scale

    Columns
    -------
    - 'SSB Case': Case A ... Case G
    - 'Carrier Frequency Range in Hz': Applicable frequency range. FR1: Split at 3 GHz (Case A, B, and C FDD) or 1.88 GHz (Case C TDD). FR2: Split into FR2-1 and FR2-2 if applicable.
    - 'Shared Spectrum Channel Access': Yes or No. Only relevant for Case C.
    - 'Delta f_RA in Hz': The Subcarrier Spacing for the RACH signal in Hz. FR1: {1250, 5000, 15000, 30000} Hz. FR2: {60000, 120000, 480000, 960000} Hz.
    - 'PRACH Configuration Indices': Tuple of PRACH Configuration Indices without collisions regarding SSB signaling. Subset of first column in 38.211 Tables 6.3.3.2-2 (FR1 FDD), 6.3.3.2-3 (FR1 TDD), and 6.3.3.2-4 (FR2).

    Parameters
    ----------
    delta_f_ra_hz : int
        The subcarrier spacing of RACH Δf_RA.

    duplex_mode : str
        The duplex mode, either FDD or TDD.

    Returns
    -------
    table_creation_success : bool
        True, if all steps of creating the tables finish without exception.

    Raises
    ------
    TypeError
        If duplex_mode is not of type str.
    TypeError
        If delta_f_ra_hz is not of type int.
    ValueError
        If duplex_mode is not in [FDD, TDD].
    ValueError
        If delta_f_ra_hz is not in [1250, 5000, 15000, 30000, 60000, 120000, 480000, 960000].

    """
    import configurator.generator as generator
    import configurator.tools as tools
    import configurator.tables as tables

    if not isinstance(duplex_mode, str):
        raise TypeError("duplex_mode should be of type str, but is {0}!".format(type(duplex_mode)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))

    if duplex_mode not in ["FDD", "TDD"]:
        raise ValueError("The duplex_mode {0} is not supported!".format(duplex_mode))
    if delta_f_ra_hz not in [1250, 5000, 15000, 30000, 60000, 120000, 480000, 960000]:
        raise ValueError("delta_f_ra_hz = {0} Hz is not supported!".format(delta_f_ra_hz))

    logger.info("Creating collision-free PRACH and SSB combinations with duplex mode {0} and Delta f_RA {1} Hz".format(duplex_mode, delta_f_ra_hz))

    table_creation_success = False

    if duplex_mode == "TDD":

        for freq_range in generator.get_keys(tools.freq_range_designation_dict):

            if delta_f_ra_hz not in tools.freq_range_delta_f_ra_dict[freq_range]:
                logger.debug("delta_f_ra_hz = {0} Hz is not supported in {1}!".format(delta_f_ra_hz, freq_range))
            else:
                if freq_range == 'FR1':
                    freq_range_main = 'FR1'
                elif freq_range in ['FR2', 'FR2-1', 'FR2-2']:
                    freq_range_main = 'FR2'
                prach_occasions_absolute_occupied_symbols_df = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=freq_range_main, duplex_mode=duplex_mode, delta_f_ra_hz=delta_f_ra_hz)
                collision_free_prach_ssb_combinations_df = pd.DataFrame(
                    columns=[
                        'SSB Case', 'Carrier Frequency Range in Hz', 'Shared Spectrum Channel Access', 'Delta f_RA in Hz', 'PRACH Configuration Indices'
                    ]
                )
                collision_free_prach_config_idx_tuple = tuple()

                # FR1

                for case in ['A', 'B', 'C']:

                    ssb_scs_hz = tools.SSB_CASES_SCS_HZ[case]
                    mu = tools.SCS_HZ_TO_NUMEROLOGY[ssb_scs_hz]
                    symbols_per_frame = tables.ts_38_211_table_4_3_2_1(mu=mu, col="N symbols per slot") * tables.ts_38_211_table_4_3_2_1(mu=mu, col="N slots per frame")

                    for shared_spectrum_channel_access in [False, True]:
                        if (case == 'B') and (shared_spectrum_channel_access is True):
                            logger.debug("SSB cell search case {0} does not support Shared Spectrum Channel Access!".format(case))
                        else:
                            if case in ['A', 'B', 'C'] and freq_range != 'FR1':
                                logger.debug("SSB cell search case {0} is not supported in {1}!".format(case, freq_range))
                                break

                            freq_range_repr_center_freq_hz_lower = 1000 * 1000000
                            freq_range_repr_center_freq_hz_upper = 4000 * 1000000

                            if case in ['A', 'B']:
                                freq_range_split_hz = 3000 * 1000000        # Lower: less or equal 3 GHz. Upper: larger than 3 GHz
                            elif case == 'C':
                                freq_range_split_hz = 1880 * 1000000 - 1    # Lower: less 1.88 GHz. Upper: equal or larger 1.88 GHz

                            for freq_range_repr_center_freq_hz in [freq_range_repr_center_freq_hz_lower, freq_range_repr_center_freq_hz_upper]:

                                ssb_time_domain_occupied_symbols = generator.create_ssb_time_domain_occupied_symbols(case=case, nr_channel_center_freq_hz=freq_range_repr_center_freq_hz, duplex_mode=duplex_mode, shared_spectrum_channel_access=shared_spectrum_channel_access)[3]

                                all_rach_occasions = set()

                                # Iterate through table with PRACH Configuration Indices
                                for index, value in prach_occasions_absolute_occupied_symbols_df['PRACH occasions all occupied symbols'].items():

                                    table_creation_success = False

                                    prach_occasion_time_domain_occupied_symbols = prach_occasions_absolute_occupied_symbols_df['PRACH occasions all occupied symbols'][index]
                                    common_elements = tuple(
                                        set(
                                            ssb_time_domain_occupied_symbols
                                        ) & set(
                                            prach_occasion_time_domain_occupied_symbols
                                        )
                                    )

                                    if len(common_elements) == 0:
                                        # TODO: Test for validity here! Use tools.verify_prach_occasion_validity
                                        collision_free_prach_config_idx_tuple = collision_free_prach_config_idx_tuple + (prach_occasions_absolute_occupied_symbols_df['PRACH configuration index'][index],)
                                    else:
                                        logger.debug("Overlapping SSB and PRACH occasion symbols: {0}".format(len(common_elements)))

                                    common_elements = tuple()

                                    all_rach_occasions.update(value)

                                    table_creation_success = True

                                if freq_range_repr_center_freq_hz == freq_range_repr_center_freq_hz_lower:
                                    carrier_freq_range_hz = (tools.freq_range_designation_dict[freq_range][0], freq_range_split_hz)
                                elif freq_range_repr_center_freq_hz == freq_range_repr_center_freq_hz_upper:
                                    carrier_freq_range_hz = (freq_range_split_hz + 1, tools.freq_range_designation_dict[freq_range][1])

                                collision_free_prach_config_idx_tuple = tuple(int(x) for x in collision_free_prach_config_idx_tuple)

                                row_dict = {
                                    'SSB Case': case,
                                    'Carrier Frequency Range in Hz': carrier_freq_range_hz,
                                    'Shared Spectrum Channel Access': shared_spectrum_channel_access,
                                    'Delta f_RA in Hz': delta_f_ra_hz,
                                    'PRACH Configuration Indices': collision_free_prach_config_idx_tuple
                                }
                                collision_free_prach_ssb_combinations_df = pd.concat(
                                    [
                                        collision_free_prach_ssb_combinations_df, pd.Series(row_dict).to_frame().T
                                    ], ignore_index=True
                                )

                                logger.debug(row_dict)

                                collision_free_prach_config_idx_tuple = tuple()

                # FR2

                for case in ['D', 'E', 'F', 'G']:

                    ssb_scs_hz = tools.SSB_CASES_SCS_HZ[case]
                    mu = tools.SCS_HZ_TO_NUMEROLOGY[ssb_scs_hz]
                    symbols_per_frame = tables.ts_38_211_table_4_3_2_1(mu=mu, col="N symbols per slot") * tables.ts_38_211_table_4_3_2_1(mu=mu, col="N slots per frame")

                    for shared_spectrum_channel_access in [False, True]:
                        if case == 'D' and freq_range not in ['FR2', 'FR2-1', 'FR2-2']:
                            logger.debug("SSB cell search case {0} is not supported in {1}!".format(case, freq_range))
                            break
                        if case == 'E' and freq_range not in ['FR2', 'FR2-1']:
                            logger.debug("SSB cell search case {0} is not supported in {1}!".format(case, freq_range))
                            break
                        if case in ['F', 'G'] and freq_range not in ['FR2', 'FR2-2']:
                            logger.debug("SSB cell search case {0} is not supported in {1}!".format(case, freq_range))
                            break

                        if case == 'D':
                            freq_range_repr_center_freq_hz = 25000 * 1000000
                        elif case == 'E':
                            freq_range_repr_center_freq_hz = 25000 * 1000000
                        elif case == 'F':
                            freq_range_repr_center_freq_hz = 60000 * 1000000
                        elif case == 'G':
                            freq_range_repr_center_freq_hz = 60000 * 1000000

                        carrier_freq_range_hz = (tools.freq_range_designation_dict[freq_range][0], tools.freq_range_designation_dict[freq_range][1])

                        ssb_time_domain_occupied_symbols = generator.create_ssb_time_domain_occupied_symbols(case=case, nr_channel_center_freq_hz=freq_range_repr_center_freq_hz, duplex_mode=duplex_mode, shared_spectrum_channel_access=shared_spectrum_channel_access)[3]

                        all_rach_occasions = set()

                        # Iterate through table with PRACH Configuration Indices
                        for index, value in prach_occasions_absolute_occupied_symbols_df['PRACH occasions all occupied symbols'].items():

                            table_creation_success = False

                            prach_occasion_time_domain_occupied_symbols = prach_occasions_absolute_occupied_symbols_df['PRACH occasions all occupied symbols'][index]
                            common_elements = tuple(
                                set(
                                    ssb_time_domain_occupied_symbols
                                ) & set(
                                    prach_occasion_time_domain_occupied_symbols
                                )
                            )

                            if len(common_elements) == 0:
                                # TODO: Test for validity here! Use tools.verify_prach_occasion_validity
                                collision_free_prach_config_idx_tuple = collision_free_prach_config_idx_tuple + (prach_occasions_absolute_occupied_symbols_df['PRACH configuration index'][index],)
                            else:
                                logger.debug("Overlapping SSB and PRACH occasion symbols: {0}".format(len(common_elements)))

                            common_elements = tuple()

                            all_rach_occasions.update(value)

                            table_creation_success = True

                        collision_free_prach_config_idx_tuple = tuple(int(x) for x in collision_free_prach_config_idx_tuple)

                        row_dict = {
                            'SSB Case': case,
                            'Carrier Frequency Range in Hz': carrier_freq_range_hz,
                            'Shared Spectrum Channel Access': shared_spectrum_channel_access,
                            'Delta f_RA in Hz': delta_f_ra_hz,
                            'PRACH Configuration Indices': collision_free_prach_config_idx_tuple
                        }
                        collision_free_prach_ssb_combinations_df = pd.concat(
                            [
                                collision_free_prach_ssb_combinations_df, pd.Series(row_dict).to_frame().T
                            ], ignore_index=True
                        )

                        logger.debug(row_dict)

                        collision_free_prach_config_idx_tuple = tuple()

                #
                # Plot PRACH occasions here!
                #

                plot_success = plot_prach_occasions(
                    all_rach_occasions=all_rach_occasions,
                    prach_occasions_absolute_occupied_symbols_df=prach_occasions_absolute_occupied_symbols_df,
                    symbols_per_frame=symbols_per_frame,
                    freq_range=freq_range,
                    duplex_mode=duplex_mode,
                    delta_f_ra_hz=delta_f_ra_hz
                )
                if plot_success is True:
                    logger.debug("Successfully plotted all RACH occasions")

                #
                # export to CSV here!
                #

                path = pathlib.Path("tables")
                path.mkdir(parents=True, exist_ok=True)

                csv_filepath = os.path.abspath(
                    os.path.join(
                        "tables",
                        "PRACH_SSB_{0}_{1}_{2}_Hz_no_collision_settings.csv".format(freq_range, duplex_mode, delta_f_ra_hz)
                    )
                )
                os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
                collision_free_prach_ssb_combinations_df.to_csv(path_or_buf=csv_filepath, index=False)

                prach_occasions_absolute_occupied_symbols_df.drop(prach_occasions_absolute_occupied_symbols_df.index, inplace=True)
                collision_free_prach_ssb_combinations_df.drop(collision_free_prach_ssb_combinations_df.index, inplace=True)

    elif duplex_mode == "FDD":

        # FR1

        freq_range = 'FR1'

        prach_occasions_absolute_occupied_symbols_df = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=freq_range, duplex_mode=duplex_mode, delta_f_ra_hz=delta_f_ra_hz)
        collision_free_prach_ssb_combinations_df = pd.DataFrame(
            columns=[
                'SSB Case', 'Carrier Frequency Range in Hz', 'Shared Spectrum Channel Access', 'Delta f_RA in Hz', 'PRACH Configuration Indices'
            ]
        )
        collision_free_prach_config_idx_tuple = tuple()

        if delta_f_ra_hz not in tools.freq_range_delta_f_ra_dict[freq_range]:
            logger.debug("delta_f_ra_hz = {0} Hz is not supported in {1}!".format(delta_f_ra_hz, freq_range))  # Not reached by tests. Only targets code errors.
        else:
            for case in ['A', 'B', 'C']:

                ssb_scs_hz = tools.SSB_CASES_SCS_HZ[case]
                mu = tools.SCS_HZ_TO_NUMEROLOGY[ssb_scs_hz]
                symbols_per_frame = tables.ts_38_211_table_4_3_2_1(mu=mu, col="N symbols per slot") * tables.ts_38_211_table_4_3_2_1(mu=mu, col="N slots per frame")

                for shared_spectrum_channel_access in [False, True]:
                    # Impossible due to hard-coded settings?
                    # if case in ['A', 'B', 'C'] and freq_range != 'FR1':
                    #    logger.debug("SSB cell search case {0} is not supported in {1}!".format(case, freq_range))
                    #    break

                    # TODO: Check if this combination is actually not allowed! Otherwise, keep both versions.
                    # if case == 'B' and shared_spectrum_channel_access == True:
                    #    break

                    freq_range_repr_center_freq_hz_lower = 1000 * 1000000
                    freq_range_repr_center_freq_hz_upper = 4000 * 1000000
                    freq_range_split_hz = 3000 * 1000000        # Lower: less or equal 3 GHz. Upper: larger than 3 GHz

                    for freq_range_repr_center_freq_hz in [freq_range_repr_center_freq_hz_lower, freq_range_repr_center_freq_hz_upper]:

                        try:
                            ssb_time_domain_occupied_symbols = generator.create_ssb_time_domain_occupied_symbols(case=case, nr_channel_center_freq_hz=freq_range_repr_center_freq_hz, duplex_mode=duplex_mode, shared_spectrum_channel_access=shared_spectrum_channel_access)[3]

                            all_rach_occasions = set()

                            # Iterate through table with PRACH Configuration Indices
                            for index, value in prach_occasions_absolute_occupied_symbols_df['PRACH occasions all occupied symbols'].items():
                                # No check for overlapping elements, since time-domain overlap is irrelevant in FDD for PRACH (Uplink) and SSB (Downlink)

                                table_creation_success = False

                                collision_free_prach_config_idx_tuple = collision_free_prach_config_idx_tuple + (prach_occasions_absolute_occupied_symbols_df['PRACH configuration index'][index],)

                                all_rach_occasions.update(value)

                                table_creation_success = True

                            if freq_range_repr_center_freq_hz == freq_range_repr_center_freq_hz_lower:
                                carrier_freq_range_hz = (tools.freq_range_designation_dict[freq_range][0], freq_range_split_hz)
                            elif freq_range_repr_center_freq_hz == freq_range_repr_center_freq_hz_upper:
                                carrier_freq_range_hz = (freq_range_split_hz + 1, tools.freq_range_designation_dict[freq_range][1])

                            collision_free_prach_config_idx_tuple = tuple(int(x) for x in collision_free_prach_config_idx_tuple)

                            row_dict = {
                                'SSB Case': case,
                                'Carrier Frequency Range in Hz': carrier_freq_range_hz,
                                'Shared Spectrum Channel Access': shared_spectrum_channel_access,
                                'Delta f_RA in Hz': delta_f_ra_hz,
                                'PRACH Configuration Indices': collision_free_prach_config_idx_tuple
                            }
                            collision_free_prach_ssb_combinations_df = pd.concat(
                                [
                                    collision_free_prach_ssb_combinations_df, pd.Series(row_dict).to_frame().T
                                ], ignore_index=True
                            )

                            logger.debug(row_dict)

                            collision_free_prach_config_idx_tuple = tuple()
                        except ValueError as e:
                            logger.debug(e)

            #
            # Plot PRACH occasions here!
            #

            plot_success = plot_prach_occasions(
                all_rach_occasions=all_rach_occasions,
                prach_occasions_absolute_occupied_symbols_df=prach_occasions_absolute_occupied_symbols_df,
                symbols_per_frame=symbols_per_frame,
                freq_range=freq_range,
                duplex_mode=duplex_mode,
                delta_f_ra_hz=delta_f_ra_hz
            )
            if plot_success is True:
                logger.debug("Successfully plotted all RACH occasions")

            #
            # export to CSV here!
            #

            logger.debug(collision_free_prach_ssb_combinations_df)

            path = pathlib.Path("tables")
            path.mkdir(parents=True, exist_ok=True)

            csv_filepath = os.path.abspath(
                os.path.join(
                    "tables",
                    "PRACH_SSB_{0}_{1}_{2}_Hz_no_collision_settings.csv".format(freq_range, duplex_mode, delta_f_ra_hz)
                )
            )
            os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
            collision_free_prach_ssb_combinations_df.to_csv(path_or_buf=csv_filepath, index=False)

            prach_occasions_absolute_occupied_symbols_df.drop(prach_occasions_absolute_occupied_symbols_df.index, inplace=True)
            collision_free_prach_ssb_combinations_df.drop(collision_free_prach_ssb_combinations_df.index, inplace=True)

    return table_creation_success


def main():
    """The main function of build_prach_ssb_collision_free_tables.py.
    This only runs when calling the script directly.

    """
    # Not reached by tests.
    logger.info("Creating collision-free combinations of SSB and PRACH occasions.\nThis might take a while...")
    for duplex_mode in ['TDD', 'FDD']:
        for delta_f_ra_hz in [1250, 5000, 15000, 30000, 60000, 120000, 480000, 960000]:
            try:
                create_collision_free_prach_ssb_combinations(duplex_mode=duplex_mode, delta_f_ra_hz=delta_f_ra_hz)
            except Exception as e:
                logger.debug(e)


if __name__ == '__main__':
    main()  # Not reached by tests.

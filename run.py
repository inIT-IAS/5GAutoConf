#!/usr/bin/env python

# Copyright (c) 2026 Niels Hendrik Fliedner
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL
# was not distributed with this file, You can obtain one at
# https://mozilla.org/MPL/2.0/.

"""Create a 5G-NR-compatible configuration.

For synthesizing cell configuration parameters, 5GAutoConf automatically assumes a synthesis should be performed if any additional arguments (kwargs) are passed.
In that case, no analysis of input arguments is performed.
Consequently, if no kwargs are passed, 5GAutoConf only performs an analysis.

:Usage:
    >>> run.py [-h] [-f FREQUENCYBAND] [-b BANDWIDTH] [-r RASTER] [-d {TDD,FDD}] [-c CENTER] [-s {b200,b210,x300,x310,none}] [-l {debug,info,warning,error,critical}] [**kwargs]

:Options:
    * ``-h``, ``--help``: Show the help message and exit.
    * ``-f``, ``--frequencyband``: The 5G NR frequency band.
    * ``-b``, ``--bandwidth``: The bandwidth in MHz of the channel to be configured.
    * ``-r``, ``--raster``: The Δf-raster in kHz. This corresponds to the subcarrier spacing SCS.
    * ``-d``, ``--duplex``: DEPRECATED The Duplex mode. This serves no function anymore, since the frequency band already defines the duplex mode..
    * ``-c``, ``--center``: The desired center frequency in MHz of the channel to be configured.
    * ``-s``, ``--sdr``: The Software Defined Radio model being used.
    * ``-l``, ``--loglevel``: The logging level for printing to the console. The logfile is always at level debug.

:Synthesis Arguments (kwargs):
    * ``n=<value>``                 Refractive index of the medium
    * ``r-cell=<value>``            Maximum gNB cell radius in meters
    * ``ue-speed=<value>``          Maximum UE speed in m/s
    * ``tau-d=<value>``             Maximum delay spread in microseconds
    * ``x=<value>``                 [PRACH] x for SFN, so that SFN mod x = y (can be omitted)
    * ``y=<value>``                 [PRACH] y for SFN, so that SFN mod x = y (can be omitted)
    * ``subframe-number=<value>``   [PRACH] Subframe number (can be omitted)
    * ``starting-symbol=<value>``   [PRACH] Starting symbol (can be omitted)
    * ``n-slot-ra=<value>``         [PRACH] Number of PRACH slots within a subframe / 60 kHz slot (can be omitted)
    * ``n-t-ra-slot=<value>``       [PRACH] Number of time-domain PRACH occasions within a PRACH slot (can be omitted)
    * ``n-dur-ra=<value>``          [PRACH] PRACH occasion duration (can be omitted)


:Examples:
    >>> python run.py -f 78 -b 40 -c 3780 -s b210 -l info n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00 x=1 y=0 subframe-number=9 starting-symbol=0 n-slot-ra=2 n-t-ra-slot=1 n-dur-ra=12
    >>> gnbautoconf -c 3780 n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00

"""
import argparse
import logging
import sys
import math
import json
from ast import literal_eval

from importlib.metadata import version
from logging_config import setup_logging
from configurator import tables
from configurator import tools
from configurator import generator


def main():
    """The main function of run.py.
    This only runs when calling the script directly.

    """
    parser = argparse.ArgumentParser(
        description=("Create a 5G-NR-compatible configuration."),
        epilog="""
synthesis arguments:
  n=<value>                 Refractive index of the medium
  r-cell=<value>            Maximum gNB cell radius in meters
  ue-speed=<value>          Maximum UE speed in m/s
  tau-d=<value>             Maximum delay spread in microseconds
  x=<value>                 [PRACH] x for SFN, so that SFN mod x = y (can be omitted)
  y=<value>                 [PRACH] y for SFN, so that SFN mod x = y (can be omitted)
  subframe-number=<value>   [PRACH] Subframe number (can be omitted)
  starting-symbol=<value>   [PRACH] Starting symbol (can be omitted)
  n-slot-ra=<value>         [PRACH] Number of PRACH slots within a subframe / 60 kHz slot (can be omitted)
  n-t-ra-slot=<value>       [PRACH] Number of time-domain PRACH occasions within a PRACH slot (can be omitted)
  n-dur-ra=<value>          [PRACH] PRACH occasion duration (can be omitted)

Examples:
  python run.py -f 78 -b 40 -c 3780 -s b210 -l info n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00 x=1 y=0 subframe-number=9 starting-symbol=0 n-slot-ra=2 n-t-ra-slot=1 n-dur-ra=12
  gnbautoconf -c 3780 n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('-f', '--frequencyband', type=int, default=78, help="The 5G NR frequency band.")
    parser.add_argument('-b', '--bandwidth', type=int, default=40, help="The bandwidth in MHz of the channel to be configured.")
    parser.add_argument('-r', '--raster', type=int, default=30, help="The ΔFRaster in kHz. This corresponds to the subcarrier spacing SCS.")
    parser.add_argument('-d', '--duplex', type=str, default="TDD", choices=["TDD", "FDD"], help="DEPRECATED The Duplex mode. This serves no function anymore, since the frequency band already defines the duplex mode.")
    parser.add_argument('-c', '--center', type=float, default=3619.2, help="The desired center frequency in MHz of the channel to be configured.")
    parser.add_argument('-s', '--sdr', type=str, default="b210", choices=["b200", "b210", "x300", "x310", "none"], help="The Software Defined Radio model being used.")
    parser.add_argument('-l', '--loglevel', type=str, default="info", choices=["debug", "info", "warning", "error", "critical"], help="The logging level for printing to the console. The logfile is always at level debug.")

    args, synth_args = parser.parse_known_args()

    kwargs = {}
    for arg in synth_args:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v

    numeric_loglevel = getattr(logging, args.loglevel.upper())

    logfile = "5GAutoConf.log"
    setup_logging(loglevel=numeric_loglevel, logfile=logfile)

    logger = logging.getLogger(__name__)

    # Read 5GAutoConf version
    __version__ = version("gnbautoconf")

    with open(logfile, 'a') as f:
        f.write("---------------------------------------\n")
    logger.info("5GAutoConf Version v{0}".format(__version__))
    logger.info("Starting logs.")

    nr_freq_band = args.frequencyband
    nr_cbw_hz = int(args.bandwidth * 1_000_000)
    nr_scs_hz = int(args.raster * 1_000)
    # nr_duplex_mode = args.duplex
    nr_channel_center_freq_hz = int(args.center * 1_000_000)
    sdr = args.sdr.lower()

    nr_duplex_mode = tools.get_duplex_mode_from_freq_band(freq_band=nr_freq_band)

    # --------------------------------------------------------------------------- #
    # If kwargs are empty, 5GAutoConf assumes only an analysis shall be performed #
    # --------------------------------------------------------------------------- #
    if not kwargs:

        logger.info("----------- ANALYSIS MODE -----------")

        # Create instance of CreateConfig
        config = generator.CreateConfig(
            nr_freq_band=nr_freq_band,
            nr_cbw_hz=nr_cbw_hz,
            nr_scs_hz=nr_scs_hz,
            nr_duplex_mode=nr_duplex_mode,
            nr_channel_center_freq_hz=nr_channel_center_freq_hz,
            static_config_filename="static_settings.json",
            config_filename="5g_config.json",
            sdr=sdr
        )

        # Manually set Shared Spectrum Channel Access to False
        # TODO: Add configuration parameters and function to determine this dynamically
        shared_spectrum_channel_access = False

        if nr_duplex_mode == 'TDD':
            # Manually set TDD UL DL Configuration Common Provided to True
            # This is the default for OpenAirInterface5G: Slot configuration using RRC (tdd-UL-DL-ConfigurationCommon)
            tdd_ul_dl_configuration_common_provided = True
        else:
            tdd_ul_dl_configuration_common_provided = False

        # Manually set Channel Access Mode to static
        # This is the default for OpenAirInterface5G
        channel_access_mode = 'static'

        # Manually set Restricted Set to '', since no long PRACH preamble format is used
        restricted_set_str = ''

        # Manually set extended cyclic prefic to false
        cyclic_prefix_extended_bool = False

        # Read static configuration from JSON to dict

        if config.read_static_config() is False:
            sys.exit()

        if config.create_dynamic_config() is False:
            sys.exit()

        if config.read_dynamic_config() is False:
            sys.exit()

        # Correct quotation marks and continue only if the function returns True

        if config.correct_quotation_marks() is False:
            sys.exit()

        if config.save_config_to_json() is False:
            sys.exit()

        config_string = config.convert_dict_to_oai5g_config_string(
            config.config_dict
        )

        # Append parameters
        config_string += "\n# Input parameters:\n"
        config_string += "    # -f Frequency band: {{n}}{0}\n".format(args.frequencyband)
        config_string += "    # -b Channel bandwidth: {0} {{MHz}}\n".format(args.bandwidth)
        config_string += "    # -r Raster (subcarrier spacing): {0} {{kHz}}\n".format(args.raster)
        config_string += "    # -d Duplex mode: {0}\n".format(args.duplex)
        config_string += "    # -c Center frequency: {0} {{MHz}}\n".format(args.center)
        config_string += "    # -s Software-defined radio choice: {0}\n".format(args.sdr)
        config_string += "    # -l Log level: {0}\n".format(args.loglevel)

        # Append copyright notice
        config_string += "\n### Generated using 5GAutoConf v{0} by Niels Hendrik Fliedner, Copyright 2026\n".format(__version__)

        logger.debug("5GAutoConf Config String:\n%s", config_string)

        if sdr in ["b200", "b210", "x300", "x310"]:
            sdr_str = ".usrp{0}".format(sdr)
        else:
            sdr_str = ""

        oai5g_conf_filename_analysis = "gnb.sa.band{0}.{1}.{2}PRB{3}.open5gs.generated.conf".format(
            nr_freq_band,
            config.nr_freq_range.lower(),
            config.max_nrb,
            sdr_str
        )

        if config.create_openairinterface5g_config_file(
            conf_str=config_string,
            filename=oai5g_conf_filename_analysis
        ) is False:
            logger.error("Writing configuration to %s failed!", oai5g_conf_filename_analysis)
            sys.exit()

        logger.info("Wrote configuration to %s", oai5g_conf_filename_analysis)

        analysis_string = (
            "     _    _   _    _    _  __   ______ ___ ____\n"
            "    / \\  | \\ | |  / \\  | | \\ \\ / / ___|_ _/ ___|\n"
            "   / _ \\ |  \\| | / _ \\ | |  \\ V /\\___ \\| |\\___ \\\n"
            "  / ___ \\| |\\  |/ ___ \\| |___| |  ___) | | ___) |\n"
            " /_/   \\_\\_| \\_/_/   \\_\\_____|_| |____/___|____/\n"
        )

        logger.info("----------- ANALYSIS -----------")

        # Analysis results in a string
        analysis_string += "\n5GAutoConf Version v{0}\n".format(__version__)
        analysis_string += "---------------------------------------\n"
        analysis_string += "\nInput parameters:\n"
        analysis_string += "-----------------\n\n"
        analysis_string += "-f Frequency band: {{n}}{0}\n".format(args.frequencyband)
        analysis_string += "-b Channel bandwidth: {0} {{MHz}}\n".format(args.bandwidth)
        analysis_string += "-r Raster (subcarrier spacing): {0} {{kHz}}\n".format(args.raster)
        analysis_string += "-d Duplex mode: {0}\n".format(args.duplex)
        analysis_string += "-c Center frequency: {0} {{MHz}}\n".format(args.center)
        analysis_string += "-s Software-defined radio choice: {0}\n".format(args.sdr)
        analysis_string += "-l Log level: {0}\n".format(args.loglevel)
        analysis_string += "\nResults:\n"
        analysis_string += "--------\n\n"

        #########
        # Create SSB and PRACH occasions
        #########

        # TODO generator.create_prach_occasions_absolute_occupied_symbols should be programmed to generate look-up tables with no-collision settings during setup.
        #       create_prach_occasions_absolute_occupied_symbols: 3.181268329999875 s average for 10 executions
        # TODO Same for generator.create_ssb_time_domain_occupied_symbols?
        #       create_ssb_time_domain_occupied_symbols: 9.899999713525177e-06 s average for 10 executions

        l_ra = tools.prach_root_sequence_index_pr[config.config_dict["gNBs"]["servingCellConfigCommon"]["prach_RootSequenceIndex_PR"]]
        mu_msg1_subcarrier_spacing = config.config_dict["gNBs"]["servingCellConfigCommon"]["msg1_SubcarrierSpacing"]
        delta_f_ra_hz = tables.ts_38_300_table_5_1_1(mu=mu_msg1_subcarrier_spacing, col="Delta f in kHz") * 1000

        logger.info("Delta f_RA: %s kHz", delta_f_ra_hz / 1e3)

        if delta_f_ra_hz == 1_250:
            delta_f_ra_khz = 1.25
        elif delta_f_ra_hz in [5_000, 15_000, 30_000, 60_000, 120_000, 480_000, 960_000]:
            delta_f_ra_khz = int(delta_f_ra_hz / 1_000)
        else:
            raise ValueError("Δf_RA = {0} Hz is not supported!".format(delta_f_ra_hz))

        delta_f_khz = int(nr_scs_hz / 1_000)

        if tables.ts_38_211_table_6_3_3_2_1(l_ra=l_ra, delta_f_ra_khz=float(delta_f_ra_khz), delta_f_khz=float(delta_f_khz)) is None:
            raise ValueError("A combination of L_RA = {0}, Δf_RA = {1} Hz, and Δf = {2} Hz is not supported!".format(l_ra, delta_f_ra_hz, nr_scs_hz))

        analysis_string += "L_RA: {0}\n".format(l_ra)
        analysis_string += "Delta f_RA: {0} kHz\n".format(delta_f_ra_khz)
        analysis_string += "Delta f: {0} kHz\n".format(delta_f_khz)
        analysis_string += "RACH Occasion starting symbols: {0}\n".format(tools.compute_rach_occasion_starting_symbols(prach_conf_idx=2, freq_range="FR1", duplex_mode="TDD", delta_f_ra_hz=5_000))

        analysis_string += "Restricted set: {0}\n".format(restricted_set_str)
        analysis_string += "Cyclic Prefix Extended: {0}\n".format(cyclic_prefix_extended_bool)

        case = tools.get_ssb_case(freq_band=nr_freq_band, scs_hz=nr_scs_hz)

        logger.info("SSB Case: %s", case)

        analysis_string += "SSB Case: {0}\n".format(case)

        pss_symbol_pattern_tuple, sss_symbol_pattern_tuple, pbch_symbol_pattern_tuple, all_occupied_ssb_symbols = generator.create_ssb_time_domain_occupied_symbols(case=case, nr_channel_center_freq_hz=nr_channel_center_freq_hz, duplex_mode=nr_duplex_mode, shared_spectrum_channel_access=shared_spectrum_channel_access)
        prach_occasion_occupied_symbols_df = generator.create_prach_occasions_absolute_occupied_symbols(freq_range=config.nr_freq_range, duplex_mode=nr_duplex_mode, delta_f_ra_hz=delta_f_ra_hz)

        prach_conf_idx = config.config_dict["gNBs"]["servingCellConfigCommon"]["prach_ConfigurationIndex"]

        mu_ref = config.config_dict["gNBs"]["servingCellConfigCommon"]["referenceSubcarrierSpacing"]
        slot_configuration_period_ms = tools.DL_UL_TRANSMISSION_PERIODICITY_MS[config.config_dict["gNBs"]["servingCellConfigCommon"]["dl_UL_TransmissionPeriodicity"]]
        n_dl_slots = config.config_dict["gNBs"]["servingCellConfigCommon"]["nrofDownlinkSlots"]
        n_dl_symbols = config.config_dict["gNBs"]["servingCellConfigCommon"]["nrofDownlinkSymbols"]
        n_ul_slots = config.config_dict["gNBs"]["servingCellConfigCommon"]["nrofUplinkSlots"]
        n_ul_symbols = config.config_dict["gNBs"]["servingCellConfigCommon"]["nrofUplinkSymbols"]

        downlink_symbols_tuple, flexible_symbols_tuple, uplink_symbols_tuple = tools.compute_ul_dl_symbols_per_frame(
            mu_ref=mu_ref,
            slot_configuration_period_ms=slot_configuration_period_ms,
            n_dl_slots=n_dl_slots,
            n_dl_symbols=n_dl_symbols,
            n_ul_slots=n_ul_slots,
            n_ul_symbols=n_ul_symbols
        )

        analysis_string += "Downlink Symbols: {0}\n".format(downlink_symbols_tuple)
        analysis_string += "Flexible Symbols: {0}\n".format(flexible_symbols_tuple)
        analysis_string += "Uplink Symbols: {0}\n".format(uplink_symbols_tuple)

        # Number of P per NR Radio Frame
        n_p_per_frame = int(
            math.floor(
                10.0 / slot_configuration_period_ms
            )
        )

        analysis_string += "Number of P per NR Radio Frame: {0}\n".format(n_p_per_frame)

        n_flex_symbols_guard_period = len(flexible_symbols_tuple) / n_p_per_frame

        logger.info("Guard Period: %s OFDM Symbols", n_flex_symbols_guard_period)
        logger.info("Guard Period: %.2f µs", n_flex_symbols_guard_period * config.nr_ofdm_symbol_duration_s * 1_000_000)

        analysis_string += "Guard Period: {0} OFDM Symbols\n".format(n_flex_symbols_guard_period)
        analysis_string += "              {0} us\n".format(round(n_flex_symbols_guard_period * config.nr_ofdm_symbol_duration_s * 1_000_000, 3))

        prach_occasion_symbols_tuple = tuple(prach_occasion_occupied_symbols_df.iloc[prach_conf_idx]['PRACH occasions all occupied symbols'])

        prach_preamble_format = tools.compute_prach_preamble_format(nr_freq_range=config.nr_freq_range, nr_duplex_mode=nr_duplex_mode, prach_conf_idx=prach_conf_idx)

        logger.info("PRACH Preamble Format: %s", prach_preamble_format)

        # Verifying PRACH occasion validity

        if tools.verify_prach_occasion_validity(
            duplex_mode=nr_duplex_mode,
            freq_range=config.nr_freq_range,
            tdd_ul_dl_configuration_common_provided=tdd_ul_dl_configuration_common_provided,
            dl_symbols_tuple=downlink_symbols_tuple,
            ul_symbols_tuple=uplink_symbols_tuple,
            ss_pbch_symbols_tuple=all_occupied_ssb_symbols,
            prach_occasion_symbols_tuple=prach_occasion_symbols_tuple,
            channel_access_mode=channel_access_mode,
            preamble_scs_hz=delta_f_ra_hz,
            prach_conf_idx=prach_conf_idx
        ) is True:
            logger.info("The chosen PRACH occasion configuration is valid!")
        else:
            logger.error("The configured PRACH occasion is invalid!")
            raise Exception("The configured PRACH occasion is invalid!")

        analysis_string += "PRACH Occasion Symbols: {0}\n".format(prach_occasion_symbols_tuple)
        analysis_string += "PRACH Preamble Format:  {0}\n".format(prach_preamble_format)

        ssb_beams_mapped_to_prach_resource_grid_df = config.map_ssb_and_valid_prach_occasions(prach_occasion_occupied_symbols_df=prach_occasion_occupied_symbols_df, all_occupied_ssb_symbols=all_occupied_ssb_symbols)

        logger.debug("SSB Beams mapped to the PRACH resource grid:\n%s", ssb_beams_mapped_to_prach_resource_grid_df)
        msg1_fdm_idx = config.config_dict["gNBs"]["servingCellConfigCommon"]["prach_msg1_FDM"]

        analysis_string += "Message 1 FDM Index: {0}\n".format(msg1_fdm_idx)

        pusch_rbs_occupied_by_prach = tools.compute_pusch_rbs_occupied_by_prach(
            nr_freq_range=config.nr_freq_range, nr_duplex_mode=nr_duplex_mode, prach_conf_idx=prach_conf_idx, l_ra=l_ra, delta_f_ra_hz=delta_f_ra_hz, nr_scs_hz=nr_scs_hz, msg1_fdm_idx=msg1_fdm_idx
        )

        prach_occupied_pusch_resource_blocks_frequency_hz = nr_scs_hz * pusch_rbs_occupied_by_prach
        logger.info(
            "Number of PUSCH Resource Blocks occupied by PRACH (RBs): %s",
            pusch_rbs_occupied_by_prach
        )
        logger.info(
            "Number of PUSCH Resource Blocks occupied by PRACH (frequency): %s kHz",
            prach_occupied_pusch_resource_blocks_frequency_hz / 1e3
        )

        analysis_string += "Number of PUSCH Resource Blocks occupied by PRACH: {0} Resource Blocks\n".format(pusch_rbs_occupied_by_prach)
        analysis_string += "                                                   {0} kHz\n".format(prach_occupied_pusch_resource_blocks_frequency_hz / 1e3)

        pusch_cyclic_prefix_duration_s = tools.compute_pusch_cyclic_prefix_duration(
            mu=tools.SCS_HZ_TO_NUMEROLOGY[nr_scs_hz],
            cyclic_prefix_extended_bool=False,
            longer_symbol_duration_bool=False,
            channel_bw_hz=nr_cbw_hz,
            freq_range=config.nr_freq_range
        ) * tools.T_C_S * tools.KAPPA

        logger.info(
            "Cyclic Prefix duration for PUSCH: %s µs",
            pusch_cyclic_prefix_duration_s * 1_000_000
        )

        prach_cyclic_prefix_duration = tools.compute_prach_cyclic_prefix_duration(
            prach_preamble_format=prach_preamble_format
        )
        logger.info(
            "Cyclic Prefix duration for PRACH: %s samples",
            prach_cyclic_prefix_duration
        )
        if delta_f_ra_hz in ["1250", "5000"]:
            prach_cyclic_prefix_duration_s = prach_cyclic_prefix_duration * tools.T_C_S * tools.KAPPA
        else:
            prach_cyclic_prefix_duration_s = prach_cyclic_prefix_duration * tools.T_C_S * tools.KAPPA * math.pow(2., -1. * mu_msg1_subcarrier_spacing)
        logger.info(
            "Cyclic Prefix duration for PRACH: %s µs",
            prach_cyclic_prefix_duration_s * 1_000_000
        )

        analysis_string += "Cyclic Prefix duration for PUSCH: {0} us\n".format(round(pusch_cyclic_prefix_duration_s * 1_000_000, 3))
        analysis_string += "Cyclic Prefix duration for PRACH: {0} samples\n".format(prach_cyclic_prefix_duration)
        analysis_string += "                                  {0} us\n".format(round(prach_cyclic_prefix_duration_s * 1_000_000, 3))

        analysis_string += "Maximum gNB cell radius (ignoring N_CS for now): {0} m\n".format(
            round(
                tools.compute_maximum_gnb_cell_radius(
                    prach_preamble_format=prach_preamble_format,
                    l_ra=l_ra,
                    delta_f_ra_hz=delta_f_ra_hz,
                    restricted_set_str=restricted_set_str,
                    cyclic_prefix_extended_bool=cyclic_prefix_extended_bool,
                    channel_bw_hz=nr_cbw_hz,
                    freq_range=config.nr_freq_range
                ), 3
            )
        )

        prach_guard_times_dict = tools.compute_prach_guard_times(
            nr_freq_range=config.nr_freq_range,
            nr_duplex_mode=nr_duplex_mode,
            prach_conf_idx=prach_conf_idx,
            delta_f_ra_hz=delta_f_ra_hz,
            delta_f_hz=nr_scs_hz
        )
        short_prach_gt_s = prach_guard_times_dict["Short GT in s"]
        long_prach_gt_s = prach_guard_times_dict["Long GT in s"]
        logger.info(
            "Short PRACH Guard Time = %.2f µs",
            short_prach_gt_s * 1_000_000
        )
        logger.info(
            "Max. cell size with short GT = %.2f m",
            short_prach_gt_s * tools.C_M_PER_S / 2
        )

        analysis_string += "Short PRACH Guard Time: {0} us\n".format(round(short_prach_gt_s * 1_000_000, 3))
        analysis_string += "Max. cell size with short GT: {0} km\n".format(round(short_prach_gt_s * tools.C_M_PER_S / (2 * 1_000), 3))

        if long_prach_gt_s is not None:
            logger.info(
                "Long PRACH Guard Time = %.2f µs",
                long_prach_gt_s * 1_000_000
            )
            logger.info(
                "Max. cell size with long GT = %.2f m",
                long_prach_gt_s * tools.C_M_PER_S / 2
            )

            analysis_string += "Long PRACH Guard Time: {0} us\n".format(round(long_prach_gt_s * 1_000_000, 3))
            analysis_string += "Max. cell size with long GT: {0} km\n".format(round(long_prach_gt_s * tools.C_M_PER_S / (2 * 1_000), 3))

        else:
            logger.info(
                "No long PRACH Guard Time available"
            )

            analysis_string += "No long PRACH Guard Time available\n"

        # The ceiling for the maximum delay spread tau_d,max is the PUSCH cyclic prefix.
        max_delay_spread_s = pusch_cyclic_prefix_duration_s
        logger.info(
            "Max. Delay Spread: %.2f µs",
            max_delay_spread_s * 1_000_000
        )

        analysis_string += "Max. Delay Spread: {0} us\n".format(round(max_delay_spread_s * 1_000_000, 3))

        # The ceiling for the combined duration of the maximum delay spread tau_d,max and the maximum round-trip delay RTD_max
        # is the PRACH cyclic prefix plus PRACH guard time.
        # Accordingly, the maximum round-trip delay RTD_max is the difference between PRACH cyclic prefix plus PRACH guard time
        # and the maximum delay spread tau_d,max.
        max_round_trip_delay = prach_cyclic_prefix_duration_s + short_prach_gt_s - max_delay_spread_s
        logger.info(
            "Max. Round-Trip Delay: %.2f µs",
            max_round_trip_delay * 1_000_000
        )
        logger.info(
            "Max. cell size according to RTD_max = %.2f m",
            max_round_trip_delay * tools.C_M_PER_S / 2
        )

        analysis_string += "Max. Round-Trip Delay: {0} us\n".format(round(max_round_trip_delay * 1_000_000, 3))
        analysis_string += "Max. cell size according to RTD_max: {0} m\n".format(round(max_round_trip_delay * tools.C_M_PER_S / 2, 3))

        analysis_filename = "gnb.sa.band{0}.{1}.{2}PRB{3}.open5gs.generated.results.txt".format(
            nr_freq_band,
            config.nr_freq_range.lower(),
            config.max_nrb,
            sdr_str
        )

        with open(analysis_filename, 'w') as f:
            f.write(analysis_string)

    # ------------------------------------------------------------------------------- #
    # If kwargs are not empty, 5GAutoConf assumes only a synthesis shall be performed #
    # ------------------------------------------------------------------------------- #
    else:

        logger.info("----------- SYNTHESIS MODE -----------")

        # Commandline arguments

        freq_band_synth = int(args.frequencyband)
        cbw_hz_synth = int(args.bandwidth * 1_000_000)
        scs_hz_synth = int(args.raster * 1_000)
        channel_center_freq_hz_synth = int(args.center * 1_000_000)
        sdr = args.sdr.lower()

        # Static parameters, replace with computations later

        freq_range = tools.get_freq_range_from_center_freq(nr_channel_center_freq_hz=nr_channel_center_freq_hz)

        logger.info("Static PRACH Config Idx Parameters:")
        logger.info("    Frequency Range: {0}".format(freq_range))
        logger.info("    Duplex Mode: {0}".format(nr_duplex_mode))

        # COHERENCE TIMES AND DELAY SPREADS

        ue_speed_max_m_s = float(kwargs["ue-speed"])
        logger.info("Maximum UE speed: %.2f m/s", ue_speed_max_m_s)
        ue_speed_max_km_h = ue_speed_max_m_s * 3.6
        logger.info("Maximum UE speed: %.2f km/h", ue_speed_max_km_h)

        n_ref_ind = float(kwargs["n"])
        logger.info("Refractive index of the medium: {0}".format(n_ref_ind))

        try:
            t_c_min_s = tools.C_M_PER_S / (n_ref_ind * 2 * ue_speed_max_m_s * nr_channel_center_freq_hz)
        except ZeroDivisionError:
            logger.warning("Tried to divide by zero for a stationary UE. Assuming a channel coherence time of 1 s from here on.")
            t_c_min_s = 1.
        logger.info("Minimum channel coherence time: %.2f µs", t_c_min_s * 1_000_000)

        # Maximum channel delay spread
        # tau_d_max_s = 3.0e-6  # https://doi.org/10.1109/25.54229, Urban areas: 2-3 µs at 900 MHz
        # tau_d_max_s = 7.0e-6  # https://doi.org/10.1109/25.54229, Hilly residential and open areas: 5-7 µs at 900 MHz
        # tau_d_max_s = 20.0e-6  # https://doi.org/10.1109/25.54229, City skylines and mountains: >20 µs at 900 MHz
        # tau_d_max_s = 100.0e-6  # https://doi.org/10.1109/25.54229, Worst case: >100 µs at 900 MHz
        # tau_d_max_s = 15.00e-6  # Manual setting to enforce choice of Cyclic Prefix duration
        tau_d_max_us = float(kwargs["tau-d"])
        tau_d_max_s = tau_d_max_us / 1_000_000.
        logger.info("Maximum delay spread: %.2f µs", tau_d_max_us)

        try:
            applicable_t_cp_ra_dict = tools.compute_applicable_t_cp_ra_dict(
                t_c_min_s=t_c_min_s,
                tau_d_max_s=tau_d_max_s
            )
        except ValueError as e:
            logger.error(e)
            logger.error("Generating synthesized configuration failed!")
            sys.exit()

        logger.debug("Applicable t_CP^RA:")
        logger.debug(json.dumps(applicable_t_cp_ra_dict, indent=4))

        # Drop applicable_t_cp_ra_dict entries with SCS that is not permitted for the given frequency band freq_band_synth
        # Use TS 38.101-1 Table 5.3.5-1 for FR1 and TS 38.101-2 Table 5.3.5-1 for FR2

        if freq_range == "FR1":
            nr_band_dict = tables.ts_38_101_1_table_5_3_5_1(freq_band=freq_band_synth)
        else:
            nr_band_dict = tables.ts_38_101_2_table_5_3_5_1(freq_band=freq_band_synth)

        permitted_scs_khz_tuples_list = list(nr_band_dict.keys())

        logging.debug("Permitted SCS kHz tuples list for NR operating band n{0}: {1}".format(freq_band_synth, permitted_scs_khz_tuples_list))

        filtered_applicable_t_cp_ra_dict = {
            key: outer
            for key, outer in applicable_t_cp_ra_dict.items()
            if any((v["Delta f_RA"] / 1_000, None) in permitted_scs_khz_tuples_list for v in outer.values())
        }

        logger.debug("Filtered applicable t_CP^RA:")
        logger.debug(json.dumps(filtered_applicable_t_cp_ra_dict, indent=4))

        # FOR TESTING ONLY: Set SSB SCS to match PRACH SCS
        # TODO: Determine SSB SCS based on the same parameters as PRACH SCS

        ssb_scs_hz = scs_hz_synth

        # Compute applicable SSB SCS
        # Use TS 38.104 Table 5.4.3.3-1 for FR1 and Table 5.4.3.3-2 for FR2

        if freq_range == "FR1":
            ssb_scs_dict = tables.ts_38_104_table_5_4_3_3_1(freq_band=freq_band_synth)
        else:
            ssb_scs_dict = tables.ts_38_104_table_5_4_3_3_2(freq_band=freq_band_synth)

        if (ssb_scs_hz / 1_000, "kHz") not in ssb_scs_dict.keys():
            raise ValueError("An SSB subcarrier spacing of {0} kHz is not permitted for NR operating band n{1}!".format(ssb_scs_hz / 1_000, freq_band_synth))

        r_cell_max_m = float(kwargs["r-cell"])
        logger.info("Cell radius: %.2f m", r_cell_max_m)
        t_rt_max_s = 2. * n_ref_ind * r_cell_max_m / tools.C_M_PER_S
        logger.info("Round-trip delay: %.2f µs", t_rt_max_s * 1e6)
        t_gt_min = t_rt_max_s  # Minimum guard time
        logger.info("Minimum guard time: %.2f µs", t_gt_min * 1e6)

        try:
            applicable_t_gt_ra_dict = tools.compute_applicable_t_gt_ra_dict(
                t_rt_max_s=t_rt_max_s
            )
        except ValueError:
            logger.error("It seems a cell radius of {0} m is too large and no guard time higher than the round-trip delay of {1} µs could be found!".format(r_cell_max_m, t_rt_max_s * 1_000_000))
            logger.error("Generating synthesized configuration failed!")
            sys.exit()

        logger.debug("Applicable T_GT^RA:")
        logger.debug(json.dumps(dict(sorted(applicable_t_gt_ra_dict.items())), indent=4))

        # COMBINE PRACH PREAMBLE FORMATS AND SCS

        t_cp_ra_pairs = set()
        for top_key, level2 in filtered_applicable_t_cp_ra_dict.items():
            for k2, level3 in level2.items():
                value = level3.get("Delta f_RA")
                t_cp_ra_pairs.add((k2, value))

        t_gt_ra_pairs = set()
        for top_key, level2 in applicable_t_gt_ra_dict.items():
            for k2, level3 in level2.items():
                value = level3.get("Delta f_RA")
                t_gt_ra_pairs.add((k2, value))

        logger.debug("T_CP^RA pairs: {0}".format(t_cp_ra_pairs))
        logger.debug("T_GT^RA pairs: {0}".format(t_gt_ra_pairs))

        t_cp_ra_t_gt_ra_matches = t_cp_ra_pairs & t_gt_ra_pairs

        logger.debug("Matching pairs of PRACH preamble formats and SCS in T_CP^RA and T_GT^RA ({0}):".format(type(t_cp_ra_t_gt_ra_matches)))
        logger.debug(t_cp_ra_t_gt_ra_matches)

        # T_CP^RA

        matched_t_cp_ra_dict = tools.filter_prach_dict(
            input_dict=filtered_applicable_t_cp_ra_dict,
            match_set=t_cp_ra_t_gt_ra_matches
        )

        logger.debug("Matched PRACH cyclic prefix durations T_CP^RA:")
        logger.debug(json.dumps(matched_t_cp_ra_dict, indent=4))

        # T_GT^RA

        matched_t_gt_ra_dict = tools.filter_prach_dict(
            input_dict=applicable_t_gt_ra_dict,
            match_set=t_cp_ra_t_gt_ra_matches
        )

        logger.debug("Matched PRACH guard time durations T_GT^RA:")
        logger.debug(json.dumps(matched_t_gt_ra_dict, indent=4))

        # Ordered tuples of the PRACH preamble formats and SCS

        ordered_pairs_prach_tuple_t_cp_ra = tools.extract_ordered_pairs_prach_tuple(
            input_dict=matched_t_cp_ra_dict
        )

        logger.debug("Ordered Pairs of PRACH tuples T_CP^RA:")
        logger.debug(ordered_pairs_prach_tuple_t_cp_ra)

        ordered_pairs_prach_tuple_t_gt_ra = tools.extract_ordered_pairs_prach_tuple(
            input_dict=matched_t_gt_ra_dict
        )

        logger.debug("Ordered Pairs of PRACH tuples T_GT^RA:")
        logger.debug(ordered_pairs_prach_tuple_t_gt_ra)

        # Rank aggregation

        try:
            min_max_matched_tuple = tools.balanced_min_max_rank(
                ordered_pairs_prach_tuple_t_cp_ra,
                ordered_pairs_prach_tuple_t_gt_ra
            )
        except ValueError:
            logger.error("It seems a UE speed of {0} m/s is too high for a delay spread of {1} µs!".format(ue_speed_max_m_s, tau_d_max_us))
            logger.error("Generating synthesized configuration failed!")
            sys.exit()

        logger.debug("Tuples with balanced matches of minimum and maximum:")
        logger.debug(min_max_matched_tuple)

        min_set = {min_max_matched_tuple[0]}
        max_set = {min_max_matched_tuple[1]}

        # Min and Max T_CP^RA and T_GT^RA

        min_t_cp_ra_dict = tools.filter_prach_dict(
            input_dict=matched_t_cp_ra_dict,
            match_set=min_set
        )

        max_t_cp_ra_dict = tools.filter_prach_dict(
            input_dict=matched_t_cp_ra_dict,
            match_set=max_set
        )

        try:
            new_ue_max_speed_m_s = tools.C_M_PER_S / (n_ref_ind * 2 * next(iter(min_t_cp_ra_dict)) * nr_channel_center_freq_hz)
        except ZeroDivisionError:
            logger.error("A refractive index of {0} is not permitted!".format(n_ref_ind))
            logger.error("Generating synthesized configuration failed!")
            sys.exit()

        min_t_gt_ra_dict = tools.filter_prach_dict(
            input_dict=matched_t_gt_ra_dict,
            match_set=min_set
        )

        max_t_gt_ra_dict = tools.filter_prach_dict(
            input_dict=matched_t_gt_ra_dict,
            match_set=max_set
        )

        new_max_cell_radius_m = next(iter(max_t_gt_ra_dict)) * tools.C_M_PER_S / n_ref_ind

        logger.debug("Lower limit of applicable PRACH parameters")
        logger.debug("    t_CP^RA (cyclic prefix): %.2f µs", next(iter(min_t_cp_ra_dict)) * 1e6)
        logger.debug("        --> Highest resource efficiency and highest robustness towards a future channel coherence time decrease, e.g. due to UE speed increase up to {0} m/s or {1} km/h.".format(new_ue_max_speed_m_s, new_ue_max_speed_m_s * 3.6))

        logger.debug("    t_GT^RA (guard time): %.2f µs", next(iter(min_t_gt_ra_dict)) * 1e6)
        logger.debug("        --> Highest resource efficiency.")

        second_key, level3 = next(iter(next(iter(min_t_cp_ra_dict.values())).items()))
        third_items = tuple(level3.items())
        logger.debug("    PRACH preamble format: {0}".format(second_key))
        for k, v in third_items:
            logger.debug("    {0}: {1}".format(k, v))

        second_key, level3 = next(iter(next(iter(min_t_gt_ra_dict.values())).items()))
        third_items = tuple(level3.items())
        for k, v in third_items:
            if k == "Delta f_RA":
                continue
            logger.debug("    {0}: {1:.2f} µs".format(k, v * 1e6))

        logger.debug("Upper limit of applicable PRACH parameters")
        logger.debug("    t_CP^RA (cyclic prefix): %.2f µs", next(iter(max_t_cp_ra_dict)) * 1e6)
        logger.debug("        --> Highest robustness towards a future channel delay spread increase.")
        logger.debug("    t_GT^RA (guard time): %.2f µs", next(iter(max_t_gt_ra_dict)) * 1e6)
        logger.debug("        --> Highest robustness towards a future cell radius increase up to {0} km.".format(new_max_cell_radius_m / 1e3))

        second_key, level3 = next(iter(next(iter(max_t_cp_ra_dict.values())).items()))
        third_items = tuple(level3.items())
        logger.debug("    PRACH preamble format: {0}".format(second_key))
        for k, v in third_items:
            logger.debug("    {0}: {1}".format(k, v))

        second_key, level3 = next(iter(next(iter(max_t_gt_ra_dict.values())).items()))
        third_items = tuple(level3.items())
        for k, v in third_items:
            if k == "Delta f_RA":
                continue
            logger.debug("    {0}: {1:.2f} µs".format(k, v * 1e6))

        # COMPUTE PRACH CONFIG INDEX

        # Choose any of these manually if desired
        # x_sfn_stat = 1 and y_sfn_stat = 0 result in a PRACH occasion for every system frame number (SFN)

        try:
            x_sfn_stat = int(kwargs["x"])
            logger.info("    x (SFN): {0}".format(x_sfn_stat))
        except KeyError:
            x_sfn_stat = 1

        try:
            y_sfn_stat = literal_eval(kwargs["y"])
            logger.info("    y (SFN): {0}".format(y_sfn_stat))
        except KeyError:
            y_sfn_stat = 0

        try:
            subframe_number_stat = literal_eval(kwargs["subframe-number"])  # For `FR2` and `TDD`, this is actually the slot number.
            logger.info("    Subframe number: {0}".format(subframe_number_stat))
        except KeyError:
            subframe_number_stat = None

        try:
            starting_symbol_stat = int(kwargs["starting-symbol"])
            logger.info("    Starting Symbol: {0}".format(starting_symbol_stat))
        except KeyError:
            starting_symbol_stat = None

        # Number of PRACH slots within a subframe / 60 kHz slot
        try:
            n_slot_ra_stat = int(kwargs["n-slot-ra"])
            logger.info("    n_slot^RA: {0}".format(n_slot_ra_stat))
        except KeyError:
            n_slot_ra_stat = None

        # Number of time-domain PRACH occasions within a PRACH slot
        try:
            n_t_ra_slot_stat = int(kwargs["n-t-ra-slot"])
            logger.info("    N_t^RA,slot: {0}".format(n_t_ra_slot_stat))
        except KeyError:
            n_t_ra_slot_stat = None

        # PRACH occasion duration
        try:
            n_dur_ra_stat = int(kwargs["n-dur-ra"])
            logger.info("    N_dur^RA: {0}".format(n_dur_ra_stat))
        except KeyError:
            n_dur_ra_stat = None

        n_slot_ra = n_slot_ra_stat
        n_t_ra_slot = n_t_ra_slot_stat
        n_dur_ra = n_dur_ra_stat

        # Calculated parameters
        second_key, level3 = next(iter(next(iter(min_t_cp_ra_dict.values())).items()))
        prach_preamble_format_calc = second_key
        third_items = tuple(level3.items())
        delta_f_ra_calc = third_items[0][1]
        try:
            scs_ra_calc = tools.SCS_HZ_TO_NUMEROLOGY[delta_f_ra_calc]
        except KeyError:
            logger.error("OpenAirInterface5G currently only allows msg1 Subcarrier Spacing of 15 kHz or higher, but the input parameters suggest {0} kHz instead!".format(delta_f_ra_calc / 1_000))
            logger.error("Generating synthesized configuration failed!")
            sys.exit()

        logger.info("Calculated PRACH Config Idx Parameters:")
        logger.info("    PRACH Preamble Format: {0}".format(prach_preamble_format_calc))
        logger.info("    \\Delta f_RA: {0}".format(delta_f_ra_calc))

        if prach_preamble_format_calc in ['0', '1', '2', '3']:
            n_slot_ra_calc = None  # Number of PRACH slots within a subframe / 60 kHz slot
            n_t_ra_slot_calc = None  # Number of time-domain PRACH occasions within a PRACH slot
            n_dur_ra_calc = 0  # PRACH occasion duration

            n_slot_ra = n_slot_ra_calc
            n_t_ra_slot = n_t_ra_slot_calc
            n_dur_ra = n_dur_ra_calc

            logger.info("    n_slot^RA: {0}".format(n_slot_ra))
            logger.info("    N_t^RA,slot: {0}".format(n_t_ra_slot))
            logger.info("    N_dur^RA: {0}".format(n_dur_ra))

        # PRACH Configuration Index

        prach_config_idx_calc_lst = tools.get_prach_configuration_index_from_parameters(
            freq_range=freq_range,  # Frequency Range
            duplex_mode=nr_duplex_mode,  # Duplex Mode
            preamble_format=prach_preamble_format_calc,  # PRACH Preamble Format
            x_sfn=x_sfn_stat,  # x for SFN
            y_sfn=y_sfn_stat,  # y for SFN
            subframe_number=subframe_number_stat,  # Subframe number, For `FR2` and `TDD`, this is actually the slot number.
            starting_symbol=starting_symbol_stat,  # Starting symbol
            n_slot_ra=n_slot_ra,  # Number of PRACH slots within a subframe / 60 kHz slot
            n_t_ra_slot=n_t_ra_slot,  # Number of time-domain PRACH occasions within a PRACH slot
            n_dur_ra=n_dur_ra  # PRACH occasion duration
        )

        logger.debug("PRACH configuration index list: {0}".format(prach_config_idx_calc_lst))

        try:
            prach_config_idx_calc = int(prach_config_idx_calc_lst[0])  # Arbitrarily choose first entry, cast form string to int
            logger.info("PRACH Configuration Index calc: {0}".format(prach_config_idx_calc))  # Pick first entry regardless of length
        except IndexError:
            logger.error("No PRACH configuration Index could be calculated!")
            sys.exit()

        if freq_range == "FR1" and nr_duplex_mode == "FDD":
            prach_conf_dict = tables.ts_38_211_table_6_3_3_2_2(prach_config_idx_calc)
        elif freq_range == "FR1" and nr_duplex_mode == "TDD":
            prach_conf_dict = tables.ts_38_211_table_6_3_3_2_3(prach_config_idx_calc)
        elif freq_range == "FR2" and nr_duplex_mode == "TDD":
            prach_conf_dict = tables.ts_38_211_table_6_3_3_2_4(prach_config_idx_calc)

        logger.info("PRACH Config Index Parameters:")
        logger.info("    PRACH Preamble Format: {0}".format(prach_conf_dict["Preamble format"][0]))
        logger.info("    x (SFN): {0}".format(prach_conf_dict["x"][0]))
        logger.info("    y (SFN): {0}".format(prach_conf_dict["y"][0]))
        try:
            logger.info("    Subframe number: {0}".format(prach_conf_dict["Subframe number"][0]))
        except KeyError:
            try:
                logger.info("    Slot number: {0}".format(prach_conf_dict["Slot number"][0]))  # For `FR2` and `TDD`, this is actually the slot number.
            except KeyError:
                logger.error("No PRACH configuration Index could be calculated!")
        logger.info("    Starting symbol: {0}".format(prach_conf_dict["Starting symbol"][0]))
        try:
            logger.info("    n_slot^RA: {0}".format(prach_conf_dict["Number of PRACH slots within a subframe"][0]))
        except KeyError:
            try:
                logger.info("    n_slot^RA: {0}".format(prach_conf_dict["Number of PRACH slots within a 60 kHz slot"][0]))
            except KeyError:
                logger.error("No PRACH configuration Index could be calculated!")
                sys.exit()
        logger.info("    N_t^RA,slot: {0}".format(prach_conf_dict["Number of time-domain PRACH occasions within a PRACH slot"][0]))
        logger.info("    N_dur^RA: {0}".format(prach_conf_dict["PRACH duration"][0]))

        # W R I T I N G   C O N F I G

        # Create instance of CreateConfig
        config_synth = generator.CreateConfig(
            nr_freq_band=freq_band_synth,
            nr_cbw_hz=cbw_hz_synth,
            nr_scs_hz=scs_hz_synth,
            nr_duplex_mode=nr_duplex_mode,
            nr_channel_center_freq_hz=channel_center_freq_hz_synth,
            static_config_filename="static_settings.json",
            config_filename="5g_config.json",
            sdr=sdr
        )

        # Manually set Shared Spectrum Channel Access to False
        # TODO: Add configuration parameters and function to determine this dynamically
        shared_spectrum_channel_access = False

        if nr_duplex_mode == 'TDD':
            # Manually set TDD UL DL Configuration Common Provided to True
            # This is the default for OpenAirInterface5G: Slot configuration using RRC (tdd-UL-DL-ConfigurationCommon)
            tdd_ul_dl_configuration_common_provided = True
        else:
            tdd_ul_dl_configuration_common_provided = False

        # Manually set Channel Access Mode to static
        # This is the default for OpenAirInterface5G
        channel_access_mode = 'static'

        # Read static configuration from JSON to dict

        if config_synth.read_static_config() is False:
            sys.exit()

        if config_synth.create_dynamic_config() is False:
            sys.exit()

        # INJECT SYNTHESIZED PARAMETERS

        config_synth.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["prach_ConfigurationIndex"] = prach_config_idx_calc
        config_synth.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["msg1_SubcarrierSpacing"] = scs_ra_calc

        # INJECT FIXES

        config_synth.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ra_ResponseWindow"] = 5

        if config_synth.read_dynamic_config() is False:
            sys.exit()

        # Correct quotation marks and continue only if the function returns True

        if config_synth.correct_quotation_marks() is False:
            sys.exit()

        if config_synth.save_config_to_json() is False:
            sys.exit()

        config_string = config_synth.convert_dict_to_oai5g_config_string(
            config_synth.config_dict
        )

        # Append parameters
        config_string += "\n# Input parameters:\n"
        config_string += "    # -f Frequency band: {{n}}{0}\n".format(args.frequencyband)
        config_string += "    # -b Channel bandwidth: {0} {{MHz}}\n".format(args.bandwidth)
        config_string += "    # -r Raster (subcarrier spacing): {0} {{kHz}}\n".format(args.raster)
        config_string += "    # -d Duplex mode: {0}\n".format(args.duplex)
        config_string += "    # -c Center frequency: {0} {{MHz}}\n".format(args.center)
        config_string += "    # -s Software-defined radio choice: {0}\n".format(args.sdr)
        config_string += "    # -l Log level: {0}\n".format(args.loglevel)

        # Append copyright notice
        config_string += "\n### Generated using 5GAutoConf v{0} by Niels Hendrik Fliedner, Copyright 2026\n".format(__version__)

        oai5g_conf_filename_synth = "5GAutoConf_test01.conf"

        if config_synth.create_openairinterface5g_config_file(
            conf_str=config_string,
            filename=oai5g_conf_filename_synth
        ) is False:
            logger.error("Writing synthesized configuration to %s failed!", oai5g_conf_filename_synth)
            sys.exit()

        logger.info("Wrote synthesized configuration to %s", oai5g_conf_filename_synth)

    # LOGS FINISHED
    logger.info("Logs finished.")


if __name__ == '__main__':
    main()

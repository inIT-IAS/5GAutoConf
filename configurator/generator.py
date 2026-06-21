#!/usr/bin/env python

# Copyright (c) 2026 Niels Hendrik Fliedner
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL
# was not distributed with this file, You can obtain one at
# https://mozilla.org/MPL/2.0/.

"""Generate Configs for 5G Base Stations.

Raises
------
RuntimeError
    If this script is called directly or trying to access the main() function.

"""
import json
import logging
import math
import pandas as pd
import os
import pathlib
import numpy as np

from . import tools
from . import tables

logger = logging.getLogger(__name__)


class CreateConfig:
    """Create OAI5G-compatible configuration files.

    """

    def __init__(self, nr_freq_band: int, nr_cbw_hz: int, nr_scs_hz: int, nr_duplex_mode: str, nr_channel_center_freq_hz: int, static_config_filename: str, config_filename: str, sdr: str):
        """The initialization function.

        Parameters
        ----------
        nr_freq_band : int
            The 5G NR frequency band.
        nr_cbw_hz : int
            The 5G NR Channel Bandwidth in Hz.
        nr_scs_hz : int
            The 5G NR Subcarrier Spacing in Hz.
        nr_duplex_mode : str
            The 5G NR Duplex Mode, either "TDD" or "FDD".
        nr_channel_center_freq_hz : int
            The 5G NR Channel Center Frequency in Hz.
        static_config_filename : str
            The filename for the static configuration JSON file.
            The data within is static for each 5G Basestation.
        config_filename : str
            The filename for the resulting configuration JSON file.
        sdr : str
            The software-defined radio model.

        """
        self.nr_freq_band = nr_freq_band
        self.nr_cbw_hz = nr_cbw_hz
        self.nr_scs_hz = nr_scs_hz
        self.nr_duplex_mode = nr_duplex_mode
        self.nr_channel_center_freq_hz = nr_channel_center_freq_hz
        self.config_filename = config_filename
        self.static_config_filename = static_config_filename
        self.sdr = sdr

        self.dynamic_config_data = {}
        self.static_config_data = {}
        self.config_string = ""
        self.config_dict = {}
        self.config_dict["Active_gNBs"] = '(\"gNB-OAI\")'
        self.config_dict["Asn1_verbosity"] = '\"none\"'
        self.config_dict["usrp-tx-thread-config"] = 1
        self.shared_spectrum_channel_access = False
        self.beam_forming_antenna_tx = False
        self.beam_forming_antenna_rx = False

        self.nr_freq_range = ""
        self.nr_numerology = 0
        self.nr_cyclic_prefix = ""
        self.nr_support_for_data = False
        self.nr_support_for_synch = False
        self.nr_n_symb_per_slot = 0
        self.nr_n_slots_per_frame = 0
        self.nr_n_slots_per_subframe = 0
        self.nr_slot_duration_s = 0
        self.nr_ofdm_symbol_duration_s = 0
        self.nr_guard_band_hz = 0
        self.nr_band_lower_hz = 0
        self.nr_band_upper_hz = 0
        self.nr_corresp_freq_range = []
        self.bw_per_rb_hz = 0
        self.max_nrb = 0
        self.max_transmission_bw_hz = 0
        self.max_cbw_occupied_hz = 0
        self.absolute_frequency_ssb_arfcn = 0
        self.ssb_ref_hz = 0
        self.k_ssb = 0
        self.offset_to_point_a_n_rbs = 0
        self.absolute_frequency_point_a_arfcn = 0
        self.absolute_frequency_point_a_hz = 0
        self.freq_band_dict = dict()
        self.nr_riv = 0
        self.rb_start = 0

    def compute_absolute_frequency_ssb(self, frequency_hz: int):
        """Compute the Signal Source Block (SSB) Reference frequency SSB_REF.
        In the OAI5G configs, this is referred to as absoluteFrequencySSB.
        The SSB_REF equals the position of the Resource Element 0 (RE0) of Resource Block 0 (RB10) of the Synchronization Signal Block (SSB).
        SSB_REF needs to sit on the GSCN raster.

        Parameters
        ----------
        frequency_hz : int
            The input frequency in Hz.

        Returns
        -------
        absolute_frequency_ssb_arfcn : int
            The SSB_REF frequency on the GSCN raster as ARFCN.

        Raises
        ------
        TypeError
            If frequency_hz is not of type int.

        """
        if not isinstance(frequency_hz, int):
            raise TypeError("frequency_hz should be of type int, but is {0}!".format(type(frequency_hz)))
        ss_ref_hz, N, M = tools.find_closest_ss_ref(frequency_hz=frequency_hz)
        absolute_frequency_ssb_arfcn = tools.convert_frequency_to_arfcn(frequency_hz=ss_ref_hz)
        return absolute_frequency_ssb_arfcn

    def compute_absolute_frequency_point_a(self, ssb_ref_hz: int, scs_raster_hz: int, usable_band_lower_limit_hz: int):
        """Compute the absoluteFrequencyPointA close to the lower limit of the usable channel.
        The usable channel is the part of a full channel with guard bands removed from both sides.

        Parameters
        ----------
        ssb_ref_hz : int
            The input SSB_REF frequency in Hz.
        scs_raster_hz : int
            The SCS raster in Hz.
        usable_band_lower_limit_hz : int
            The lower limit of the usable channel in Hz.

        Returns
        -------
        absolute_frequency_point_a_arfcn : int
            The absoluteFrequencyPointA as ARFCN.
        absolute_frequency_point_a_hz : int
            The absoluteFrequencyPointA in Hz.
        k_ssb : int
            k_SSB.
        offset_to_point_a_n_rbs : int
            offsetToPointA in N_RBs.

        Raises
        ------
        TypeError
            If ssb_ref_hz, scs_raster_hz or usable_band_lower_limit_hz is not of type int.

        """
        if not isinstance(ssb_ref_hz, int) or not isinstance(scs_raster_hz, int) or not isinstance(usable_band_lower_limit_hz, int):
            raise TypeError("self.ssb_ref_hz, scs_raster_hz and usable_band_lower_limit_hz should all be of type int, but are {0}, {1} and {2}!".format(type(ssb_ref_hz), type(scs_raster_hz), type(usable_band_lower_limit_hz)))
        point_a_temp_hz_1 = int(ssb_ref_hz - (tools.N_RBS_PER_SSB * scs_raster_hz * tools.N_SC_PER_RB) / 2)

        # OffsetToPointA Estimation

        k_ssb = 0

        offset_to_point_a_n_rbs = int(
            max(
                math.floor(
                    (point_a_temp_hz_1 - (usable_band_lower_limit_hz)) / (tools.N_SC_PER_RB * scs_raster_hz)
                ),
                0.0
            )
        )

        point_a_temp_hz_2 = point_a_temp_hz_1 - (k_ssb * scs_raster_hz) - (offset_to_point_a_n_rbs * tools.N_SC_PER_RB * scs_raster_hz)

        # k_SSB Estimation

        k_ssb = int(
            max(
                math.floor(
                    (point_a_temp_hz_2 - (usable_band_lower_limit_hz)) / (scs_raster_hz)
                ),
                0.0
            )
        )

        absolute_frequency_point_a_hz = point_a_temp_hz_1 - (k_ssb * scs_raster_hz) - (offset_to_point_a_n_rbs * tools.N_SC_PER_RB * scs_raster_hz)
        absolute_frequency_point_a_arfcn = tools.convert_frequency_to_arfcn(frequency_hz=absolute_frequency_point_a_hz)

        return absolute_frequency_point_a_arfcn, absolute_frequency_point_a_hz, k_ssb, offset_to_point_a_n_rbs

    def read_static_config(self):
        """Read static configuration from JSON file.

        Returns
        -------
        Boolean
            True, if no error occured.

        """
        with open(self.static_config_filename, "r") as read_file:
            self.static_config_data = json.load(read_file)
            for key in self.static_config_data:
                self.config_dict[key] = self.static_config_data[key]
        return True

    def create_dynamic_config(self):
        """Create dynamic configuration dictionary.

        Returns
        -------
        Boolean
            True, if no error occured.

        Raises
        ------
        ValueError
            If nr_freq_band is < 0 or > 512.
        ValueError
            If nr_cbw_hz is not available for the chosen frequency band.
        ValueError
            If nr_scs_hz is not available for the chosen frequency band.
        ValueError
            If nr_freq_range is not one of "FR1", "FR2", "FR2-1", or "FR2-2".

        """
        self.dynamic_config_data = json.loads('{ "gNBs":{ "servingCellConfigCommon":{ "physCellId":0 } } }')
        logger.info("5G NR Frequency Band = n{0} [CLI Argument]".format(self.nr_freq_band))
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["dl_frequencyBand"] = self.nr_freq_band
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ul_frequencyBand"] = self.nr_freq_band

        if 0 < self.nr_freq_band <= 256:
            self.nr_freq_range = "FR1"
        elif 257 <= self.nr_freq_band <= 512:
            self.nr_freq_range = "FR2"
        else:
            raise ValueError("The Band n{0} is not supported!".format(self.nr_freq_band))

        if tools.verify_cbw_validity_from_freq_band(freq_band=self.nr_freq_band, cbw_hz=self.nr_cbw_hz) is True:
            logger.info("5G NR Channel Bandwidth (CBW) = {0} MHz [CLI Argument]".format(int(self.nr_cbw_hz / 1000000)))
        else:
            raise ValueError("A Channel Bandwidth (CBW) of {0} MHz is not permitted for Band n{1}!".format(int(self.nr_cbw_hz / 1000000), self.nr_freq_band))  # Not reached by tests. Only targets code errors.

        if tools.verify_scs_validity_from_freq_band(freq_band=self.nr_freq_band, scs_hz=self.nr_scs_hz) is True:
            logger.info("5G NR Subcarrier Spacing (SCS) = {0} kHz [CLI Argument]".format(int(self.nr_scs_hz / 1000)))
        else:
            raise ValueError("A Subcarrier Spacing (SCS) of {0} kHz is not permitted for Band n{1}!".format(int(self.nr_scs_hz / 1000), self.nr_freq_band))

        self.nr_numerology = tools.SCS_HZ_TO_NUMEROLOGY[self.nr_scs_hz]
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["dl_subcarrierSpacing"] = self.nr_numerology
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["initialDLBWPsubcarrierSpacing"] = self.nr_numerology
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ul_subcarrierSpacing"] = self.nr_numerology
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["initialULBWPsubcarrierSpacing"] = self.nr_numerology
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["msg1_SubcarrierSpacing"] = self.nr_numerology
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["subcarrierSpacing"] = self.nr_numerology
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["referenceSubcarrierSpacing"] = self.nr_numerology
        logger.info("5G NR Numerology = {0}".format(self.nr_numerology))

        self.nr_cyclic_prefix = tables.ts_38_300_table_5_1_1(mu=self.nr_numerology, col="CP")
        logger.info("5G NR Cyclic Prefix = {0}".format(self.nr_cyclic_prefix))
        self.nr_support_for_data = tables.ts_38_300_table_5_1_1(mu=self.nr_numerology, col="Supported for data")
        logger.info("5G NR Support for Data = {0}".format(self.nr_support_for_data))
        self.nr_support_for_synch = tables.ts_38_300_table_5_1_1(mu=self.nr_numerology, col="Supported for synch")
        logger.info("5G NR Support for Synch = {0}".format(self.nr_support_for_synch))

        self.nr_n_symb_per_slot = tables.ts_38_211_table_4_3_2_1(mu=self.nr_numerology, col="N symbols per slot")
        logger.info("5G NR Number of OFDM symbols per slot = {0}".format(self.nr_n_symb_per_slot))
        self.nr_n_slots_per_frame = tables.ts_38_211_table_4_3_2_1(mu=self.nr_numerology, col="N slots per frame")
        logger.info("5G NR Number of slots per radio frame = {0}".format(self.nr_n_slots_per_frame))
        self.nr_n_slots_per_subframe = tables.ts_38_211_table_4_3_2_1(mu=self.nr_numerology, col="N slots per subframe")
        logger.info("5G NR Number of slots per subframe = {0}".format(self.nr_n_slots_per_subframe))

        """Detailed Numerology computations.

        3GPP TS 38.211 Table 4.3.2-1:
        Radio Frame Duration = 10 ms
        Numer of Subframes per Frame = 10
        Subframe Duration = 1 ms
        OFDM Symbols in a Slot = 14
        Number of Subcarriers per PRB = 12

        Computations
        ------------
        - Slot duration = 1 ms / N_slots_per_subframe
        - OFDM Symbol Duration = Slot duration / 14
        - PRB Bandwidth = 12 * SCS

        """

        self.nr_slot_duration_s = (1. / 1000.) / self.nr_n_slots_per_subframe
        logger.info("5G NR Slot duration = {0} ms".format(self.nr_slot_duration_s * 1000.))
        self.nr_ofdm_symbol_duration_s = self.nr_slot_duration_s / tools.N_SYMB_PER_SLOT
        logger.info("5G NR OFDM Symbol duration = {:.2f} us".format(self.nr_ofdm_symbol_duration_s * 1000000.))

        logger.info("5G NR Duplex Mode = {0} [CLI Argument]".format(self.nr_duplex_mode))
        # TODO: Add test for valid center frequency
        logger.info("5G NR Channel Center Frequency = {0} MHz [CLI Argument]".format(int(self.nr_channel_center_freq_hz / 1000000)))

        if self.nr_freq_range == "FR1":
            self.nr_guard_band_hz = tables.ts_38_101_1_table_5_3_3_1(channel_bw_hz=self.nr_cbw_hz, scs_hz=self.nr_scs_hz) * 1_000
        elif self.nr_freq_range in ["FR2", "FR2-1", "FR2-2"]:
            self.nr_guard_band_hz = tables.ts_38_101_2_table_5_3_3_1(channel_bw_hz=self.nr_cbw_hz, scs_hz=self.nr_scs_hz) * 1_000
        else:
            raise ValueError("The frequency range {0} is not supported!".format(self.nr_freq_range))  # Not reached by tests. Only targets code errors.

        logger.info("5G NR Guard Bandwidth = {0} MHz".format(self.nr_guard_band_hz / 1000000))
        self.nr_band_lower_hz = int(self.nr_channel_center_freq_hz - self.nr_cbw_hz / 2)
        logger.info("5G NR Band Lower Limit = {0} MHz".format(self.nr_band_lower_hz / 1000000))
        self.nr_band_upper_hz = int(self.nr_channel_center_freq_hz + self.nr_cbw_hz / 2)
        logger.info("5G NR Band Upper Limit = {0} MHz".format(self.nr_band_upper_hz / 1000000))
        # TODO: Add test for valid occupied frequency ranges within the chosen band

        logger.info("5G NR Frequency Range Designation = {0}".format(self.nr_freq_range))
        self.nr_corresp_freq_range = tables.ts_38_101_1_table_5_1_1(self.nr_freq_range)
        logger.info("5G NR Corresponding Frequency Range = {0}".format(self.nr_corresp_freq_range))

        self.bw_per_rb_hz = tools.N_SC_PER_RB * self.nr_scs_hz
        logger.info("5G NR Bandwidth per Resource Block (RB) = {0} MHz".format(self.bw_per_rb_hz / 1000000))

        self.max_nrb = int(
            math.floor(
                (self.nr_cbw_hz - 2 * self.nr_guard_band_hz) / self.bw_per_rb_hz
            )
        )
        # TODO: Check if max_nrb needs to be calculated each time, or if using the tables below is better.
        if self.nr_freq_range == "FR1":
            if self.max_nrb != tables.ts_38_101_1_table_5_3_2_1(channel_bw_hz=self.nr_cbw_hz, scs_hz=self.nr_scs_hz):
                raise Exception(
                    "An error occured when computing self.max_nrb. The computed result was {0}, but should be {1} according to 3GPP TS 38.101-1 Table 5.3.2-1!".format(
                        self.max_nrb, tables.ts_38_101_1_table_5_3_2_1(channel_bw_hz=self.nr_cbw_hz, scs_hz=self.nr_scs_hz)
                    )
                )  # Not reached by tests. Only targets code errors.
        elif self.nr_freq_range in ["FR2", "FR2-1", "FR2-2"]:
            if self.max_nrb != tables.ts_38_101_2_table_5_3_2_1(channel_bw_hz=self.nr_cbw_hz, scs_hz=self.nr_scs_hz):
                raise Exception(
                    "An error occured when computing self.max_nrb. The computed result was {0}, but should be {1} according to 3GPP TS 38.101-2 Table 5.3.2-1!".format(
                        self.max_nrb, tables.ts_38_101_2_table_5_3_2_1(channel_bw_hz=self.nr_cbw_hz, scs_hz=self.nr_scs_hz)
                    )
                )  # Not reached by tests. Only targets code errors.

        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["dl_carrierBandwidth"] = self.max_nrb
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ul_carrierBandwidth"] = self.max_nrb
        logger.info("5G NR Maximum Number of Resource Blocks (RBs) = {0}".format(self.max_nrb))

        self.max_transmission_bw_hz = tools.N_SC_PER_RB * self.nr_scs_hz * self.max_nrb
        logger.info("5G NR Maximum Transmission Bandwidth = {0} MHz".format(self.max_transmission_bw_hz / 1000000))

        self.max_cbw_occupied_hz = self.max_transmission_bw_hz + 2 * self.nr_guard_band_hz
        logger.info("5G NR Maximum Occupied Channel Bandwidth = {0} MHz".format(self.max_cbw_occupied_hz / 1000000))

        # Absolute Frequency SSB = SS_REF on GSCN raster, given as ARFCN

        logger.debug("Starting to compute absoluteFrequencySSB.")
        self.absolute_frequency_ssb_arfcn = self.compute_absolute_frequency_ssb(self.nr_channel_center_freq_hz)
        logger.debug("Computing absoluteFrequencySSB finished.")
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["absoluteFrequencySSB"] = self.absolute_frequency_ssb_arfcn
        logger.info("absoluteFrequencySSB (ARFCN) = {0}".format(self.absolute_frequency_ssb_arfcn))

        # AbsoluteFrequencyPointA = Common RB0 = CRB0

        self.ssb_ref_hz = tools.convert_arfcn_to_frequency(arfcn=self.absolute_frequency_ssb_arfcn)
        logger.info("absoluteFrequencySSB = {0} MHz".format(self.ssb_ref_hz / 1000000))

        logger.debug("Starting to compute absoluteFrequencyPointA.")
        self.absolute_frequency_point_a_arfcn, self.absolute_frequency_point_a_hz, self.k_ssb, self.offset_to_point_a_n_rbs = self.compute_absolute_frequency_point_a(ssb_ref_hz=self.ssb_ref_hz, scs_raster_hz=self.nr_scs_hz, usable_band_lower_limit_hz=self.nr_band_lower_hz + self.nr_guard_band_hz)
        logger.debug("Computing absoluteFrequencyPointA finished.")
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["dl_absoluteFrequencyPointA"] = self.absolute_frequency_point_a_arfcn
        logger.info("absoluteFrequencyPointA (ARFCN) = {0}".format(self.absolute_frequency_point_a_arfcn))
        logger.info("absoluteFrequencyPointA (frequency) = {0} MHz".format(self.absolute_frequency_point_a_hz / 1000000))
        logger.info("absoluteFrequencyPointA k_SSB = {0}".format(self.k_ssb))
        logger.info("absoluteFrequencyPointA offsetToPointA = {0} RBs".format(self.offset_to_point_a_n_rbs))

        # Frequency Band Tables

        if self.nr_freq_range == "FR1":
            self.freq_band_dict = tables.ts_38_101_1_table_5_3_5_1(freq_band=self.nr_freq_band)
        elif self.nr_freq_range in ["FR2", "FR2-1", "FR2-2"]:
            self.freq_band_dict = tables.ts_38_101_2_table_5_3_5_1(freq_band=self.nr_freq_band)
        else:
            raise ValueError("{0} is not a valid Frequency Range!".format(self.nr_freq_range))  # Not reached by tests. Only targets code errors.

        # Location and Bandwidth: NR RIV

        logger.debug("Starting to compute the NR Resource Indication Value (RIV).")
        self.nr_riv = tools.compute_nr_riv_from_rbs(rb_start=self.rb_start, l_rbs=self.max_nrb)
        logger.debug("Computing the NR Resource Indication Value (RIV) finished.")
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["initialDLBWPlocationAndBandwidth"] = self.nr_riv
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["initialULBWPlocationAndBandwidth"] = self.nr_riv
        logger.info("NR Resource Indication Value (RIV) = {0}".format(self.nr_riv))

        logger.debug("Starting to compute rb_start.")
        self.rb_start = tables.ts_38_214_ch_5_1_2_2_2_reverse(self.nr_riv)[0]
        logger.debug("Computing rb_start finished.")
        logger.info("5G NR Starting Resource Block (rb_start) = {0}".format(self.rb_start))

        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["dl_offstToCarrier"] = 0
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["initialDLBWPcontrolResourceSetZero"] = 12
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["initialDLBWPsearchSpaceZero"] = 0
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ul_offstToCarrier"] = 0
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["pMax"] = 20
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["prach_ConfigurationIndex"] = 98
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["prach_msg1_FDM"] = 0
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["prach_msg1_FrequencyStart"] = 0
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["zeroCorrelationZoneConfig"] = 13
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["preambleReceivedTargetPower"] = -96
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["preambleTransMax"] = 6
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["powerRampingStep"] = 1
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ra_ResponseWindow"] = 4
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"] = 4
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB"] = 14
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ra_ContentionResolutionTimer"] = 7
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["rsrp_ThresholdSSB"] = 19
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["prach_RootSequenceIndex_PR"] = 2
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["prach_RootSequenceIndex"] = 1
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["restrictedSetConfig"] = 0
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["msg3_DeltaPreamble"] = 1
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["p0_NominalWithGrant"] = -90
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["pucchGroupHopping"] = 0
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["hoppingId"] = 40
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["p0_nominal"] = -90
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ssb_PositionsInBurst_PR"] = 2
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ssb_PositionsInBurst_Bitmap"] = 1
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ssb_periodicityServingCell"] = 2
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["dmrs_TypeA_Position"] = 0
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["dl_UL_TransmissionPeriodicity"] = 6
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["nrofDownlinkSlots"] = 7
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["nrofDownlinkSymbols"] = 6
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["nrofUplinkSlots"] = 2
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["nrofUplinkSymbols"] = 4
        self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]["ssPBCH_BlockPower"] = -25

        # Radio Units

        self.dynamic_config_data["RUs"] = {}
        self.dynamic_config_data["RUs"]["local_rf"] = "yes"
        self.dynamic_config_data["RUs"]["nb_tx"] = 1
        self.dynamic_config_data["RUs"]["nb_rx"] = 1
        if self.sdr in ["b200", "b210"]:
            self.dynamic_config_data["RUs"]["att_tx"] = 12
            self.dynamic_config_data["RUs"]["att_rx"] = 12
            self.dynamic_config_data["RUs"]["max_rxgain"] = 114
            self.dynamic_config_data["RUs"]["bf_weights"] = ["0x00007fff", "0x0000", "0x0000", "0x0000"]    # 1x2 matrix: ["0x00007fff", "0x0000"]; 1x4 matrix (1 layer x 4 antennas): [0x00007fff, 0x0000,0x0000, 0x0000]; 2x2 matrix: [0x00007fff, 0x00000000, 0x00000000, 0x00007fff]; 4x4 matrix: [0x00007fff, 0x0000, 0x0000, 0x0000, 0x00000000, 0x00007fff, 0x0000, 0x0000, 0x0000, 0x0000, 0x00007fff, 0x0000, 0x0000, 0x0000, 0x0000, 0x00007fff]
            self.dynamic_config_data["RUs"]["clock_src"] = "internal"       # Valid choices are: "internal", "external", and "gpsdo".
            self.dynamic_config_data["RUs"]["time_src"] = "internal"        # Valid choices are: "internal", "external", and "gpsdo".
            self.dynamic_config_data["RUs"]["sdr_addrs"] = "type=b200"      # Valid choices are the USRP device identification string: https://files.ettus.com/manual/page_identification.html.
        if self.sdr in ["x300", "x310"]:
            self.dynamic_config_data["RUs"]["att_tx"] = 0
            self.dynamic_config_data["RUs"]["att_rx"] = 0
            self.dynamic_config_data["RUs"]["max_rxgain"] = 114
            self.dynamic_config_data["RUs"]["bf_weights"] = ["0x00007fff", "0x0000"]    # 1x2 matrix: ["0x00007fff", "0x0000"]; 1x4 matrix (1 layer x 4 antennas): [0x00007fff, 0x0000,0x0000, 0x0000]; 2x2 matrix: [0x00007fff, 0x00000000, 0x00000000, 0x00007fff]; 4x4 matrix: [0x00007fff, 0x0000, 0x0000, 0x0000, 0x00000000, 0x00007fff, 0x0000, 0x0000, 0x0000, 0x0000, 0x00007fff, 0x0000, 0x0000, 0x0000, 0x0000, 0x00007fff]
            self.dynamic_config_data["RUs"]["clock_src"] = "internal"           # Valid choices are: "internal", "external", and "gpsdo".
            self.dynamic_config_data["RUs"]["time_src"] = "internal"            # Valid choices are: "internal", "external", and "gpsdo".
            self.dynamic_config_data["RUs"]["sdr_addrs"] = "addr=192.168.40.2"  # Valid choices are the USRP device identification string: https://files.ettus.com/manual/page_identification.html. For using 2 10Gb Ethernet interfaces on a N3x0 or X3x0 or X4x0 (requires that you flashed the FPGA wth the XG image): sdr_addrs = "addr=192.168.10.2,second_addr=192.168.20.2"
        self.dynamic_config_data["RUs"]["bands"] = [78]
        self.dynamic_config_data["RUs"]["max_pdschReferenceSignalPower"] = -27
        self.dynamic_config_data["RUs"]["eNB_instances"] = [0]

        return True

    def read_dynamic_config(self):
        """Read dynamic configuration from dictionary.

        Returns
        -------
        Boolean
            True, if no error occured.

        """
        self.config_dict["gNBs"]["servingCellConfigCommon"] = self.dynamic_config_data["gNBs"]["servingCellConfigCommon"]
        self.config_dict["RUs"] = self.dynamic_config_data["RUs"]
        return True

    def convert_dict_to_oai5g_config_string(self, data_dict: dict):
        """Convert a dict to OAI5G-compatible config string.
        Maximum dictionary depth is 3.

        Parameters
        ----------
        data_dict : dict
            The input dictionary.

        Returns
        -------
        config_str : str
            The formatted OAI5G-compatible config string.

        Raises
        ------
        TypeError
            If data_dict is not a dict.

        """
        if not isinstance(data_dict, dict):
            raise TypeError("data_dict should be of type dict, but is {0}!".format(type(data_dict)))
        config_string = ""
        config_string += "Active_gNBs = {0};\n".format(data_dict["Active_gNBs"])
        config_string += "Asn1_verbosity = {0};\n".format(data_dict["Asn1_verbosity"])
        if self.sdr in ["x300", "x310"]:
            config_string += "usrp-tx-thread-config = {0};\n".format(data_dict["usrp-tx-thread-config"])

        config_string += "gNBs = (\n"
        config_string += "{\n"

        config_string += "    ////////// Identification parameters:\n"
        config_string += "    gNB_ID             = {0};\n".format(data_dict["gNBs"]["gNB_ID"])
        config_string += "    gNB_name           = {0};\n".format(data_dict["gNBs"]["gNB_name"])
        config_string += "    tracking_area_code = {0};\n".format(data_dict["gNBs"]["tracking_area_code"])
        config_string += "    plmn_list          = (\n"
        config_string += "    {\n"
        config_string += "        mcc        = {0};\n".format(data_dict["gNBs"]["plmn_list"]["mcc"])
        config_string += "        mnc        = {0};\n".format(data_dict["gNBs"]["plmn_list"]["mnc"])
        config_string += "        mnc_length = {0};\n".format(data_dict["gNBs"]["plmn_list"]["mnc_length"])
        config_string += "        snssaiList = (\n"
        config_string += "        {\n"
        config_string += "            sst = {0};\n".format(data_dict["gNBs"]["plmn_list"]["snssaiList"]["sst"])
        config_string += "        });\n"
        config_string += "    });\n"
        config_string += "    nr_cellid    = {0};\n\n".format(data_dict["gNBs"]["nr_cellid"])
        config_string += "    ////////// Physical parameters:\n\n"
        config_string += "    do_CSIRS     = {0};\n".format(1)
        config_string += "    do_SRS       = {0};\n".format(1)
        config_string += "    min_rxtxtime = {0};\n".format(6)

        config_string += "    servingCellConfigCommon = (\n"
        config_string += "    {\n"
        config_string += "    # spCellConfigCommon\n"
        config_string += "        physCellId                                   = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["physCellId"])
        config_string += "    # downlinkConfigCommon\n"
        config_string += "        # this is {0} MHz\n".format(round(tools.convert_arfcn_to_frequency(arfcn=self.absolute_frequency_ssb_arfcn) / 1000000., 3))
        config_string += "        absoluteFrequencySSB                         = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["absoluteFrequencySSB"])
        config_string += "        dl_frequencyBand                             = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["dl_frequencyBand"])
        config_string += "        # this is {0} MHz\n".format(round(tools.convert_arfcn_to_frequency(arfcn=self.absolute_frequency_point_a_arfcn) / 1000000., 3))
        config_string += "        dl_absoluteFrequencyPointA                   = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["dl_absoluteFrequencyPointA"])
        config_string += "        dl_offstToCarrier                            = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["dl_offstToCarrier"])
        config_string += "      # Downlink Subcarrier Spacing\n"
        config_string += "        # 0=kHz15, 1=kHz30, 2=kHz60, 3=kHz120, 4=kHz240, 5=kHz480, 6=kHz960\n"
        config_string += "        # this is {0} kHz\n".format(float(tables.ts_38_300_table_5_1_1(mu=data_dict["gNBs"]["servingCellConfigCommon"]["dl_subcarrierSpacing"], col="Delta f in kHz")))
        config_string += "        dl_subcarrierSpacing                         = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["dl_subcarrierSpacing"])
        config_string += "      # Downlink Carrier Bandwidth in Physical Resource Blocks\n"
        config_string += "        dl_carrierBandwidth                          = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["dl_carrierBandwidth"])
        config_string += "      # Initial Downlink Bandwidthpart\n"
        config_string += "        # Initial Downlink Bandwidthpart Location and Bandwidth\n"
        config_string += "        # this is (275*(L-1))+RBstart, with RBstart = {0} and L = {1}\n".format(self.rb_start, self.max_nrb)
        config_string += "        initialDLBWPlocationAndBandwidth             = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["initialDLBWPlocationAndBandwidth"])
        config_string += "      # Initial Downlink Bandwidth-Product Subcarrier Spacing\n"
        config_string += "        # 0=kHz15, 1=kHz30, 2=kHz60, 3=kHz120, 4=kHz240, 5=kHz480, 6=kHz960\n"
        config_string += "        # this is {0} kHz\n".format(float(tables.ts_38_300_table_5_1_1(mu=data_dict["gNBs"]["servingCellConfigCommon"]["initialULBWPsubcarrierSpacing"], col="Delta f in kHz")))
        config_string += "        initialDLBWPsubcarrierSpacing                = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["initialDLBWPsubcarrierSpacing"])
        config_string += "        initialDLBWPcontrolResourceSetZero           = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["initialDLBWPcontrolResourceSetZero"])
        config_string += "        initialDLBWPsearchSpaceZero                  = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["initialDLBWPsearchSpaceZero"])
        config_string += "    # uplinkConfigCommon\n"
        config_string += "        ul_frequencyBand                             = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ul_frequencyBand"])
        config_string += "        ul_offstToCarrier                            = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ul_offstToCarrier"])
        config_string += "      # Uplink Subcarrier Spacing\n"
        config_string += "        # 0=kHz15, 1=kHz30, 2=kHz60, 3=kHz120, 4=kHz240, 5=kHz480, 6=kHz960\n"
        config_string += "        # this is {0} kHz\n".format(float(tables.ts_38_300_table_5_1_1(mu=data_dict["gNBs"]["servingCellConfigCommon"]["ul_subcarrierSpacing"], col="Delta f in kHz")))
        config_string += "        ul_subcarrierSpacing                         = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ul_subcarrierSpacing"])
        config_string += "      # Uplink Carrier Bandwidth in Physical Resource Blocks\n"
        config_string += "        ul_carrierBandwidth                          = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ul_carrierBandwidth"])
        config_string += "        pMax                                         = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["pMax"])
        config_string += "      # Initial Uplink Bandwidthpart\n"
        config_string += "        # Initial Uplink Bandwidthpart Location and Bandwidth\n"
        config_string += "        # this is (275*(L-1))+RBstart, with RBstart = {0} and L = {1}\n".format(self.rb_start, self.max_nrb)
        config_string += "        initialULBWPlocationAndBandwidth             = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["initialULBWPlocationAndBandwidth"])
        config_string += "      # Initial Uplink Bandwidth-Product Subcarrier Spacing\n"
        config_string += "        # 0=kHz15, 1=kHz30, 2=kHz60, 3=kHz120, 4=kHz240, 5=kHz480, 6=kHz960\n"
        config_string += "        # this is {0} kHz\n".format(float(tables.ts_38_300_table_5_1_1(mu=data_dict["gNBs"]["servingCellConfigCommon"]["initialULBWPsubcarrierSpacing"], col="Delta f in kHz")))
        config_string += "        initialULBWPsubcarrierSpacing                = {0};\n".format(int(data_dict["gNBs"]["servingCellConfigCommon"]["initialULBWPsubcarrierSpacing"]))
        config_string += "    # rach-ConfigCommon\n"
        config_string += "      # prach-ConfigurationIndex\n"
        config_string += "        prach_ConfigurationIndex                     = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["prach_ConfigurationIndex"])
        config_string += "      # msg1-FDM\n"
        config_string += "        # 0=one, 1=two, 2=four, 3=eight\n"
        config_string += "        # this is {0} PRACH occasions frequency-division multiplexed in one time instance\n".format(tools.MSG1_FDM[data_dict["gNBs"]["servingCellConfigCommon"]["prach_msg1_FDM"]])
        config_string += "        prach_msg1_FDM                               = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["prach_msg1_FDM"])
        config_string += "      # msg1-FrequencyStart\n"
        config_string += "        # Offset of lowest PRACH transmission occasion in frequency domain with respective to PRB 0.\n"
        config_string += "        # INTEGER (0..maxNrofPhysicalResourceBlocks-1)\n"
        config_string += "        prach_msg1_FrequencyStart                    = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["prach_msg1_FrequencyStart"])
        config_string += "      # zeroCorrelationZoneConfig\n"
        config_string += "        # N_CS configuration for preamble formats with L_RA in {139,571,1151}.\n"
        if data_dict["gNBs"]["servingCellConfigCommon"]["prach_RootSequenceIndex_PR"] == 2:
            config_string += "        # here: L_RA = 139 and N_CS = {0}\n".format(tables.ts_38_211_table_6_3_3_1_7(zero_correlation_zone_config=data_dict["gNBs"]["servingCellConfigCommon"]["zeroCorrelationZoneConfig"])['N_CS value for L_RA=139'][0])
        config_string += "        zeroCorrelationZoneConfig                    = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["zeroCorrelationZoneConfig"])
        config_string += "      # preambleReceivedTargetPower\n"
        config_string += "        # The target power level at the network receiver side.\n"
        config_string += "        # Only multiples of 2 dBm may be chosen (e.g. -202, -200, -198, ...).\n"
        config_string += "        preambleReceivedTargetPower                  = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["preambleReceivedTargetPower"])
        config_string += "        \n"
        config_string += "      # preambleTransMax\n"
        config_string += "        # Max number of RA preamble transmission performed before declaring a failure\n"
        config_string += "        # (0...10) = (3,4,5,6,7,8,10,20,50,100,200)\n"
        config_string += "        preambleTransMax                             = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["preambleTransMax"])
        config_string += "      # powerRampingStep\n"
        config_string += "        # 0=dB0,1=dB2,2=dB4,3=dB6\n"
        config_string += "        # this is {0}, which equals {1} dB per step\n".format(
            tools.POWER_RAMPING_STEP[data_dict["gNBs"]["servingCellConfigCommon"]["powerRampingStep"]],
            tools.POWER_RAMPING_STEP[data_dict["gNBs"]["servingCellConfigCommon"]["powerRampingStep"]].split('dB')[1]
        )
        config_string += "        powerRampingStep                             = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["powerRampingStep"])
        config_string += "      # ra_ReponseWindow\n"
        config_string += "        # Msg2 (RAR) window length in enumerated number of slots. \n"
        config_string += "        # The network configures a value lower than or equal to 10 ms when Msg2 is transmitted in licensed spectrum and a value lower than or equal to 40 ms when Msg2 is transmitted with shared spectrum channel access.\n"
        config_string += "        # ENUM    | 0 | 1 | 2 | 3 |  4 |  5 |  6 |  7 |\n"
        config_string += "        # n_slots | 1 | 2 | 4 | 8 | 10 | 20 | 40 | 80 |\n"
        config_string += "        ra_ResponseWindow                            = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ra_ResponseWindow"])
        config_string += "    # ssb-perRACH-OccasionAndCB-PreamblesPerSSB\n"
        config_string += "      # SSBs per RACH Occasion\n"
        config_string += "        # 1=oneEighth, 2=oneFourth, 3=oneHalf, 4=one, 5=two, 6=four, 7=eight, 8=sixteen\n"
        config_string += "        # here: one RACH occasion is associated with {0} SSB(s)\n".format(tools.SSB_PER_RACH_OCCASION[data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"]])
        config_string += "        ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"])
        config_string += "      # CB-PreamblesPerSSB\n"
        config_string += "        # for {0} SSB(s) per RACH occasion: {1}\n".format(
            tools.SSB_PER_RACH_OCCASION[data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"]],
            tools.CB_PREAMBLES_PER_SSB[tools.SSB_PER_RACH_OCCASION[data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"]]]
        )
        if tools.SSB_PER_RACH_OCCASION[data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"]] in ['oneEighth', 'oneFourth', 'oneHalf', 'one', 'two']:
            config_string += "        # here: {0} contention-based preambles per SSB\n".format(
                tools.CB_PREAMBLES_PER_SSB[
                    tools.SSB_PER_RACH_OCCASION[data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"]]
                ][data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB"]].split('n')[1]
            )
        else:
            config_string += "        # here: {0} contention-based preambles shared by {1} SSB(s) in a RACH occasion\n".format(
                tools.CB_PREAMBLES_PER_SSB[
                    tools.SSB_PER_RACH_OCCASION[data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"]]
                ][data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB"]],
                tools.MSG1_FDM_INT[data_dict["gNBs"]["servingCellConfigCommon"]["prach_msg1_FDM"]]
            )
            config_string += "        # this is {0} contention-based preambles per SSB\n".format(
                int(
                    int(tools.CB_PREAMBLES_PER_SSB[
                        tools.SSB_PER_RACH_OCCASION[data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB_PR"]]
                    ][data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB"]]) / tools.MSG1_FDM_INT[data_dict["gNBs"]["servingCellConfigCommon"]["prach_msg1_FDM"]]
                )
            )

        config_string += "        ssb_perRACH_OccasionAndCB_PreamblesPerSSB    = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ssb_perRACH_OccasionAndCB_PreamblesPerSSB"])
        config_string += "      # ra_ContentionResolutionTimer\n"
        config_string += "        # (0...7) = 8,16,24,32,40,48,56,64 subframes\n"
        config_string += "        # this is {0}, which equals {1} subframes\n".format(
            tools.RA_CONTENT_RESOLUTION_TIMER[data_dict["gNBs"]["servingCellConfigCommon"]["ra_ContentionResolutionTimer"]],
            tools.RA_CONTENT_RESOLUTION_TIMER[data_dict["gNBs"]["servingCellConfigCommon"]["ra_ContentionResolutionTimer"]].split('sf')[1]
        )
        config_string += "        ra_ContentionResolutionTimer                 = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ra_ContentionResolutionTimer"])
        config_string += "        rsrp_ThresholdSSB                            = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["rsrp_ThresholdSSB"])
        config_string += "      # prach-RootSequenceIndex_PR\n"
        config_string += "        # 1 = 839, 2 = 139\n"
        config_string += "        prach_RootSequenceIndex_PR                   = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["prach_RootSequenceIndex_PR"])
        config_string += "        prach_RootSequenceIndex                      = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["prach_RootSequenceIndex"])
        config_string += "      # Message1 Subcarrier Spacing\n"
        config_string += "        # can only be 15 for 30 kHz < 6 GHz, takes precendence over the one derived from prach-ConfigIndex\n"
        config_string += "        # 0=kHz15, 1=kHz30, 2=kHz60, 3=kHz120\n"
        config_string += "        # this is {0} kHz\n".format(float(tables.ts_38_300_table_5_1_1(mu=data_dict["gNBs"]["servingCellConfigCommon"]["msg1_SubcarrierSpacing"], col="Delta f in kHz")))
        config_string += "        msg1_SubcarrierSpacing                       = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["msg1_SubcarrierSpacing"])
        config_string += "      # restrictedSetConfig\n"
        config_string += "        # 0=unrestricted, 1=restricted type A, 2=restricted type B\n"
        config_string += "        restrictedSetConfig                          = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["restrictedSetConfig"])
        config_string += "      # Message3 Power\n"
        config_string += "        # Message3 DeltaPreamble = INTEGER (-1..6)\n"
        config_string += "        msg3_DeltaPreamble                           = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["msg3_DeltaPreamble"])
        config_string += "        # msg3 Power = preambleReceivedTargetPower + (2 x msg3-DeltaPreamble) = {0}\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["preambleReceivedTargetPower"] + 2 * data_dict["gNBs"]["servingCellConfigCommon"]["msg3_DeltaPreamble"])
        config_string += "       # P0\n"
        config_string += "        # p0-NominalWithGrant = INTEGER (-202..24)\n"
        config_string += "        p0_NominalWithGrant                          = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["p0_NominalWithGrant"])
        config_string += "        \n"
        config_string += "    # pucch-ConfigCommon setup\n"
        config_string += "      # pucchGroupHopping\n"
        config_string += "        # 0=neither, 1=group hopping, 2=sequence hopping\n"
        config_string += "        pucchGroupHopping                            = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["pucchGroupHopping"])
        config_string += "        hoppingId                                    = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["hoppingId"])
        config_string += "        p0_nominal                                   = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["p0_nominal"])
        config_string += "        ssb_PositionsInBurst_PR                      = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ssb_PositionsInBurst_PR"])
        config_string += "        ssb_PositionsInBurst_Bitmap                  = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ssb_PositionsInBurst_Bitmap"])
        config_string += "      # ssb_periodicityServingCell\n"
        config_string += "        # 0=ms5, 1=ms10, 2=ms20, 3=ms40, 4=ms80, 5=ms160, 6=spare2, 7=spare1\n"
        config_string += "        ssb_periodicityServingCell                   = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ssb_periodicityServingCell"])
        config_string += "      # dmrs_TypeA_position\n"
        config_string += "        # 0=pos2, 1=pos3\n"
        config_string += "        dmrs_TypeA_Position                          = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["dmrs_TypeA_Position"])
        config_string += "      # Subcarrier Spacing\n"
        config_string += "        # 0=kHz15, 1=kHz30, 2=kHz60, 3=kHz120, 4=kHz240, 5=kHz480, 6=kHz960\n"
        config_string += "        # Subcarrier Spacing: {0} kHz\n".format(float(tables.ts_38_300_table_5_1_1(mu=data_dict["gNBs"]["servingCellConfigCommon"]["subcarrierSpacing"], col="Delta f in kHz")))
        config_string += "        subcarrierSpacing                            = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["subcarrierSpacing"])
        config_string += "      # Subcarrier Spacing\n"
        config_string += "        # 0=kHz15, 1=kHz30, 2=kHz60, 3=kHz120, 4=kHz240, 5=kHz480, 6=kHz960\n"
        config_string += "        \n"
        config_string += "    # tdd-UL-DL-ConfigurationCommon\n"
        config_string += "      # Reference Subcarrier Spacing\n"
        config_string += "        # 0=kHz15, 1=kHz30, 2=kHz60, 3=kHz120\n"
        config_string += "        # Reference Subcarrier Spacing: {0} kHz\n".format(float(tables.ts_38_300_table_5_1_1(mu=data_dict["gNBs"]["servingCellConfigCommon"]["referenceSubcarrierSpacing"], col="Delta f in kHz")))
        config_string += "        referenceSubcarrierSpacing                   = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["referenceSubcarrierSpacing"])
        config_string += "      # pattern1\n"
        config_string += "        # dl_UL_TransmissionPeriodicity\n"
        config_string += "        # 0=ms0p5, 1=ms0p625, 2=ms1, 3=ms1p25, 4=ms2, 5=ms2p5, 6=ms5, 7=ms10\n"
        config_string += "        dl_UL_TransmissionPeriodicity                = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["dl_UL_TransmissionPeriodicity"])
        config_string += "        nrofDownlinkSlots                            = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["nrofDownlinkSlots"])
        config_string += "        nrofDownlinkSymbols                          = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["nrofDownlinkSymbols"])
        config_string += "        nrofUplinkSlots                              = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["nrofUplinkSlots"])
        config_string += "        nrofUplinkSymbols                            = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["nrofUplinkSymbols"])
        config_string += "        ssPBCH_BlockPower                            = {0};\n".format(data_dict["gNBs"]["servingCellConfigCommon"]["ssPBCH_BlockPower"])
        config_string += "    });\n\n"

        config_string += "    # ------- SCTP definitions\n"
        config_string += "    SCTP : \n"
        config_string += "    {\n"
        config_string += "        # Number of streams to use in input/output\n"
        config_string += "        SCTP_INSTREAMS  = {0};\n".format(data_dict["gNBs"]["SCTP"]["SCTP_INSTREAMS"])
        config_string += "        SCTP_OUTSTREAMS = {0};\n".format(data_dict["gNBs"]["SCTP"]["SCTP_OUTSTREAMS"])
        config_string += "    };\n\n"

        config_string += "    ////////// AMF parameters:\n"
        config_string += "     amf_ip_address = (\n"
        config_string += "    {\n"
        config_string += "        ipv4 = {0};\n".format(data_dict["gNBs"]["amf_ip_address"]["ipv4"])
        config_string += "    });\n\n"

        config_string += "    NETWORK_INTERFACES :\n"
        config_string += "    {\n"
        config_string += "        GNB_IPV4_ADDRESS_FOR_NG_AMF = {0};\n".format(data_dict["gNBs"]["NETWORK_INTERFACES"]["GNB_IPV4_ADDRESS_FOR_NG_AMF"])
        config_string += "        GNB_IPV4_ADDRESS_FOR_NGU    = {0};\n".format(data_dict["gNBs"]["NETWORK_INTERFACES"]["GNB_IPV4_ADDRESS_FOR_NGU"])
        config_string += "        GNB_PORT_FOR_S1U            = {0};\n".format(data_dict["gNBs"]["NETWORK_INTERFACES"]["GNB_PORT_FOR_S1U"])
        config_string += "    };\n"

        config_string += "});\n\n"

        config_string += "MACRLCs = (\n"
        config_string += "{\n"
        config_string += "    num_cc               = {0};\n".format(data_dict["MACRLCs"]["num_cc"])
        config_string += "    tr_s_preference      = {0};\n".format(data_dict["MACRLCs"]["tr_s_preference"])
        config_string += "    tr_n_preference      = {0};\n".format(data_dict["MACRLCs"]["tr_n_preference"])
        config_string += "    pusch_TargetSNRx10   = {0};\n".format(data_dict["MACRLCs"]["pusch_TargetSNRx10"])
        config_string += "    pucch_TargetSNRx10   = {0};\n".format(data_dict["MACRLCs"]["pucch_TargetSNRx10"])
        config_string += "});\n\n"

        config_string += "L1s = (\n"
        config_string += "{\n"
        config_string += "    num_cc               = {0};\n".format(data_dict["L1s"]["num_cc"])
        config_string += "    tr_n_preference      = {0};\n".format(data_dict["L1s"]["tr_n_preference"])
        config_string += "    prach_dtx_threshold  = {0};\n".format(data_dict["L1s"]["prach_dtx_threshold"])
        config_string += "    pucch0_dtx_threshold = {0};\n".format(data_dict["L1s"]["pucch0_dtx_threshold"])
        config_string += "    ofdm_offset_divisor  = {0};\n".format(data_dict["L1s"]["ofdm_offset_divisor"])
        config_string += "});\n\n"

        config_string += "RUs = (\n"
        config_string += "{\n"
        config_string += "    local_rf                      = {0};\n".format(data_dict["RUs"]["local_rf"])
        config_string += "    nb_tx                         = {0};\n".format(data_dict["RUs"]["nb_tx"])
        config_string += "    nb_rx                         = {0};\n".format(data_dict["RUs"]["nb_rx"])
        config_string += "    att_tx                        = {0};\n".format(data_dict["RUs"]["att_tx"])
        config_string += "    att_rx                        = {0};\n".format(data_dict["RUs"]["att_rx"])

        bands_str = "["
        for n in data_dict["RUs"]["bands"]:
            bands_str += "{0}, ".format(n)
        bands_str = bands_str[:-2]
        bands_str += "]"

        config_string += "    bands                         = {0};\n".format(bands_str)
        config_string += "    max_pdschReferenceSignalPower = {0};\n".format(data_dict["RUs"]["max_pdschReferenceSignalPower"])
        config_string += "    max_rxgain                    = {0};\n".format(data_dict["RUs"]["max_rxgain"])

        enb_instances_str = "["
        for n in data_dict["RUs"]["eNB_instances"]:
            enb_instances_str += "{0}, ".format(n)
        enb_instances_str = enb_instances_str[:-2]
        enb_instances_str += "]"

        config_string += "    eNB_instances                 = {0};\n".format(enb_instances_str)

        bf_weights_str = "["
        for n in data_dict["RUs"]["bf_weights"]:
            bf_weights_str += "{0}, ".format(n)
        bf_weights_str = bf_weights_str[:-2]
        bf_weights_str += "]"

        config_string += "    bf_weights                    = {0};\n".format(bf_weights_str)
        config_string += "    clock_src                     = {0};\n".format(data_dict["RUs"]["clock_src"])
        config_string += "    time_src                      = \"{0}\";\n".format(data_dict["RUs"]["time_src"])
        config_string += "    sdr_addrs                     = \"{0}\";\n".format(data_dict["RUs"]["sdr_addrs"])
        config_string += "});\n\n"

        config_string += "THREAD_STRUCT = (\n"
        config_string += "{\n"
        config_string += "    #three config for level of parallelism \"PARALLEL_SINGLE_THREAD\", \"PARALLEL_RU_L1_SPLIT\", or \"PARALLEL_RU_L1_TRX_SPLIT\"\n"
        config_string += "    parallel_config      = {0};\n".format(data_dict["THREAD_STRUCT"]["parallel_config"])
        config_string += "    #two option for worker \"WORKER_DISABLE\" or \"WORKER_ENABLE\"\n"
        config_string += "    worker_config        = {0};\n".format(data_dict["THREAD_STRUCT"]["worker_config"])
        config_string += "});\n\n"

        config_string += "rfsimulator :\n"
        config_string += "{\n"
        config_string += "    serveraddr = {0};\n".format(data_dict["rfsimulator"]["serveraddr"])
        config_string += "    serverport = {0};\n".format(data_dict["rfsimulator"]["serverport"])
        config_string += "    options    = (); #(\"saviq\"); or/and \"chanmod\"\n"
        config_string += "    modelname  = {0};\n".format(data_dict["rfsimulator"]["modelname"])
        config_string += "    IQfile     = {0};\n".format(data_dict["rfsimulator"]["IQfile"])
        config_string += "};\n\n"

        config_string += "security = {\n"
        config_string += "    # preferred ciphering algorithms\n"
        config_string += "    # the first one of the list that an UE supports in chosen\n"
        config_string += "    # valid values: nea0, nea1, nea2, nea3\n"
        config_string += "    ciphering_algorithms = {0};\n".format(data_dict["security"]["ciphering_algorithms"])
        config_string += "    \n"
        config_string += "    # preferred integrity algorithms\n"
        config_string += "    # the first one of the list that an UE supports in chosen\n"
        config_string += "    # valid values: nia0, nia1, nia2, nia3\n"
        config_string += "    integrity_algorithms = {0};\n".format(data_dict["security"]["integrity_algorithms"])
        config_string += "    \n"
        config_string += "    # setting 'drb_ciphering' to \"no\" disables ciphering for DRBs, no matter\n"
        config_string += "    # what 'ciphering_algorithms' configures; same thing for 'drb_integrity'\n"
        config_string += "    drb_ciphering = {0};\n".format(data_dict["security"]["drb_ciphering"])
        config_string += "    drb_integrity = {0};\n".format(data_dict["security"]["drb_integrity"])
        config_string += "};\n\n"

        config_string += "log_config :\n"
        config_string += "{\n"
        config_string += "    global_log_level = {0};\n".format(data_dict["log_config"]["global_log_level"])
        config_string += "    hw_log_level = {0};\n".format(data_dict["log_config"]["hw_log_level"])
        config_string += "    phy_log_level = {0};\n".format(data_dict["log_config"]["phy_log_level"])
        config_string += "    mac_log_level = {0};\n".format(data_dict["log_config"]["mac_log_level"])
        config_string += "    rlc_log_level = {0};\n".format(data_dict["log_config"]["rlc_log_level"])
        config_string += "    pdcp_log_level = {0};\n".format(data_dict["log_config"]["pdcp_log_level"])
        config_string += "    rrc_log_level = {0};\n".format(data_dict["log_config"]["rrc_log_level"])
        config_string += "    ngap_log_level = {0};\n".format(data_dict["log_config"]["ngap_log_level"])
        config_string += "    f1ap_log_level = {0};\n".format(data_dict["log_config"]["f1ap_log_level"])
        config_string += "};\n\n"

        config_string += "e2_agent = {\n"
        config_string += "    near_ric_ip_addr = {0};\n".format(data_dict["e2_agent"]["near_ric_ip_addr"])
        config_string += "    #sm_dir = \"/path/where/the/SMs/are/located/\"\n"
        config_string += "    sm_dir = {0};\n".format(data_dict["e2_agent"]["sm_dir"])
        config_string += "};\n"

        return config_string

    def save_config_to_json(self):
        """Save the configuration to a JSON file.

        Returns
        -------
        Boolean
            True, if no error occured.

        """
        with open(self.config_filename, "w") as write_file:
            json.dump(self.config_dict, write_file, ensure_ascii=False, indent=4)
        return True

    def correct_quotation_marks(self):
        """Correct string formats, which need extra quotation marks: "...".

        Returns
        -------
        Boolean
            True, if no error occured.

        """
        self.config_dict["gNBs"]["gNB_name"] = '\"{0}\"'.format(self.config_dict["gNBs"]["gNB_name"])
        self.config_dict["gNBs"]["amf_ip_address"]["ipv4"] = '\"{0}\"'.format(self.config_dict["gNBs"]["amf_ip_address"]["ipv4"])
        self.config_dict["gNBs"]["NETWORK_INTERFACES"]["GNB_IPV4_ADDRESS_FOR_NG_AMF"] = '\"{0}\"'.format(self.config_dict["gNBs"]["NETWORK_INTERFACES"]["GNB_IPV4_ADDRESS_FOR_NG_AMF"])
        self.config_dict["gNBs"]["NETWORK_INTERFACES"]["GNB_IPV4_ADDRESS_FOR_NGU"] = '\"{0}\"'.format(self.config_dict["gNBs"]["NETWORK_INTERFACES"]["GNB_IPV4_ADDRESS_FOR_NGU"])

        self.config_dict["MACRLCs"]["tr_s_preference"] = '\"{0}\"'.format(self.config_dict["MACRLCs"]["tr_s_preference"])
        self.config_dict["MACRLCs"]["tr_n_preference"] = '\"{0}\"'.format(self.config_dict["MACRLCs"]["tr_n_preference"])

        self.config_dict["L1s"]["tr_n_preference"] = '\"{0}\"'.format(self.config_dict["L1s"]["tr_n_preference"])

        self.config_dict["RUs"]["local_rf"] = '\"{0}\"'.format(self.config_dict["RUs"]["local_rf"])
        self.config_dict["RUs"]["clock_src"] = '\"{0}\"'.format(self.config_dict["RUs"]["clock_src"])

        self.config_dict["THREAD_STRUCT"]["parallel_config"] = '\"{0}\"'.format(self.config_dict["THREAD_STRUCT"]["parallel_config"])
        self.config_dict["THREAD_STRUCT"]["worker_config"] = '\"{0}\"'.format(self.config_dict["THREAD_STRUCT"]["worker_config"])

        self.config_dict["rfsimulator"]["serveraddr"] = '\"{0}\"'.format(self.config_dict["rfsimulator"]["serveraddr"])
        self.config_dict["rfsimulator"]["modelname"] = '\"{0}\"'.format(self.config_dict["rfsimulator"]["modelname"])
        self.config_dict["rfsimulator"]["IQfile"] = '\"{0}\"'.format(self.config_dict["rfsimulator"]["IQfile"])

        self.config_dict["security"]["ciphering_algorithms"] = '(\"{0}\")'.format(self.config_dict["security"]["ciphering_algorithms"][0])
        self.config_dict["security"]["integrity_algorithms"] = '(\"{0}\", \"{1}\")'.format(self.config_dict["security"]["integrity_algorithms"][0], self.config_dict["security"]["integrity_algorithms"][1])
        self.config_dict["security"]["drb_ciphering"] = '\"{0}\"'.format(self.config_dict["security"]["drb_ciphering"])
        self.config_dict["security"]["drb_integrity"] = '\"{0}\"'.format(self.config_dict["security"]["drb_integrity"])

        self.config_dict["log_config"]["global_log_level"] = '\"{0}\"'.format(self.config_dict["log_config"]["global_log_level"])
        self.config_dict["log_config"]["hw_log_level"] = '\"{0}\"'.format(self.config_dict["log_config"]["hw_log_level"])
        self.config_dict["log_config"]["phy_log_level"] = '\"{0}\"'.format(self.config_dict["log_config"]["phy_log_level"])
        self.config_dict["log_config"]["mac_log_level"] = '\"{0}\"'.format(self.config_dict["log_config"]["mac_log_level"])
        self.config_dict["log_config"]["rlc_log_level"] = '\"{0}\"'.format(self.config_dict["log_config"]["rlc_log_level"])
        self.config_dict["log_config"]["pdcp_log_level"] = '\"{0}\"'.format(self.config_dict["log_config"]["pdcp_log_level"])
        self.config_dict["log_config"]["rrc_log_level"] = '\"{0}\"'.format(self.config_dict["log_config"]["rrc_log_level"])
        self.config_dict["log_config"]["ngap_log_level"] = '\"{0}\"'.format(self.config_dict["log_config"]["ngap_log_level"])
        self.config_dict["log_config"]["f1ap_log_level"] = '\"{0}\"'.format(self.config_dict["log_config"]["f1ap_log_level"])

        self.config_dict["e2_agent"]["near_ric_ip_addr"] = '\"{0}\"'.format(self.config_dict["e2_agent"]["near_ric_ip_addr"])
        self.config_dict["e2_agent"]["sm_dir"] = '\"{0}\"'.format(self.config_dict["e2_agent"]["sm_dir"])

        return True

    def create_openairinterface5g_config_file(self, conf_str: str, filename: str):
        """Create OpenAirInterface5G Config File.

        Returns
        -------
        Boolean
            True, if no error occured.

        Raises
        ------
        TypeError
            If conf_str is not a str.
        TypeError
            If filename is not a str.

        """
        if not isinstance(conf_str, str):
            raise TypeError("conf_str should be of type str, but is {0}!".format(type(conf_str)))
        if not isinstance(filename, str):
            raise TypeError("filename should be of type str, but is {0}!".format(type(filename)))
        logger.debug("Starting to create OpenAirInterface5G Config File.")
        with open(filename, "w") as write_file:
            write_file.write(conf_str)
        logger.debug("Creating OpenAirInterface5G Config File finished.")
        return True

    def map_ssb_and_valid_prach_occasions(self, prach_occasion_occupied_symbols_df: pd.DataFrame, all_occupied_ssb_symbols: tuple):
        """Map SSB resources and valid PRACH occasions.

        Parameters
        ----------
        prach_occasion_occupied_symbols_df : pd.DataFrame
            The DataFrame with absolute starting symbols of the PRACH occasions.

        all_occupied_ssb_symbols : tuple
            The tuple with all occupied symbols of the SSB time domain pattern.

        Returns
        -------
        ssb_beams_mapped_to_prach_resource_grid_df : pd.DataFrame
            The SSB beams mapped to the PRACH resource grid as a DataFrame.
            The columns are named after the RACH occasion starting_symbols.

        Raises
        ------
        TypeError
            If prach_occasion_occupied_symbols_df is not of type pandas.DataFrame.
        TypeError
            If all_occupied_ssb_symbols is not of type tuple.

        """
        if not isinstance(prach_occasion_occupied_symbols_df, pd.DataFrame):
            raise TypeError("prach_occasion_occupied_symbols_df should be of type pd.DataFrame, but is {0}!".format(type(prach_occasion_occupied_symbols_df)))
        if not isinstance(all_occupied_ssb_symbols, tuple):
            raise TypeError("all_occupied_ssb_symbols should be of type tuple, but is {0}!".format(type(all_occupied_ssb_symbols)))

        # SSB Time Pattern

        case = tools.get_ssb_case(freq_band=self.nr_freq_band, scs_hz=self.nr_scs_hz)
        ssb_candidate_start_symbols, l_max = tools.compute_ssb_time_domain_transmission_pattern(case=case, nr_channel_center_freq_hz=self.nr_channel_center_freq_hz, duplex_mode=self.nr_duplex_mode, shared_spectrum_channel_access=self.shared_spectrum_channel_access)
        ssb_configuration_period_ms = int(
            tools.SSB_PERIODICITY_SERVING_CELL[
                self.config_dict["gNBs"]["servingCellConfigCommon"]["ssb_periodicityServingCell"]
            ].split('ms')[1]
        )

        if self.beam_forming_antenna_tx is False or self.beam_forming_antenna_rx is False:
            n_tx_ssb_beams = 1
        else:
            n_tx_ssb_beams = l_max

        # PRACH Occasion Time Pattern

        mu_msg1_subcarrier_spacing = self.config_dict["gNBs"]["servingCellConfigCommon"]["msg1_SubcarrierSpacing"]

        prach_occasion_starting_symbols_absolute_tuple = prach_occasion_occupied_symbols_df.iloc[self.config_dict["gNBs"]["servingCellConfigCommon"]["prach_ConfigurationIndex"]].loc["PRACH occasion starting symbols absolute"]

        prach_occasion_all_occupied_symbols_tuple = prach_occasion_occupied_symbols_df.iloc[self.config_dict["gNBs"]["servingCellConfigCommon"]["prach_ConfigurationIndex"]].loc["PRACH occasions all occupied symbols"]

        slots_per_frame = tables.ts_38_211_table_4_3_2_1(mu=mu_msg1_subcarrier_spacing, col="N slots per frame")
        symbols_per_frame = tools.N_SYMB_PER_SLOT * slots_per_frame

        prach_configuration_period_ms = tools.NR_RADIO_FRAME_DURATION_MS * math.ceil(max(prach_occasion_all_occupied_symbols_tuple) / symbols_per_frame)

        association_period = math.ceil(ssb_configuration_period_ms / prach_configuration_period_ms)

        msg1_fdm_int = tools.MSG1_FDM_INT[self.config_dict["gNBs"]["servingCellConfigCommon"]["prach_msg1_FDM"]]

        prach_occasions_per_frame = msg1_fdm_int * len(prach_occasion_starting_symbols_absolute_tuple) * tools.NR_RADIO_FRAME_DURATION_MS / prach_configuration_period_ms

        prach_occasions_per_ssb_periodicity = prach_occasions_per_frame * ssb_configuration_period_ms / tools.NR_RADIO_FRAME_DURATION_MS

        if (prach_occasions_per_ssb_periodicity / n_tx_ssb_beams) < 1.0:
            logger.warning("There are not enough PRACH occasions available to map all SSB beams! Returning None instead of DataFrame!")
            return None

        # Generate PRACH resource grid
        df_columns = prach_occasion_starting_symbols_absolute_tuple + tuple(x + symbols_per_frame for x in prach_occasion_starting_symbols_absolute_tuple)
        ssb_beams_mapped_to_prach_resource_grid_df = pd.DataFrame(np.nan, index=range(msg1_fdm_int), columns=df_columns).astype(object)

        # Map SSB beams to PRACH resource grid

        logger.debug("Number of SSB beams: {0}".format(n_tx_ssb_beams))
        logger.debug("Association Period: {0}".format(association_period))

        ssb_beams_per_frame = int(n_tx_ssb_beams / association_period)
        ssb_beam_index = 0

        if n_tx_ssb_beams == 1:
            ssb_beams_mapped_to_prach_resource_grid_df.at[0, prach_occasion_starting_symbols_absolute_tuple[0]] = "SSB{0}".format(ssb_beam_index)
            ssb_beam_index = n_tx_ssb_beams - 1
        else:
            for n_association_period in range(0, association_period):
                ssb_counter = 0
                for n_rach_time_occasion_window in prach_occasion_starting_symbols_absolute_tuple:
                    for n_msg1_fdm in range(0, msg1_fdm_int):
                        if ssb_beam_index < n_tx_ssb_beams:
                            if ssb_counter < ssb_beams_per_frame:
                                ssb_beams_mapped_to_prach_resource_grid_df.at[n_msg1_fdm, n_rach_time_occasion_window + n_association_period * symbols_per_frame] = "SSB{0}".format(ssb_beam_index)
                                ssb_counter += 1
                                ssb_beam_index += 1
        empty_rach_occasions = ssb_beams_mapped_to_prach_resource_grid_df.isna().sum().sum()

        logger.info("Empty RACH Occasions: {0}".format(empty_rach_occasions))

        return ssb_beams_mapped_to_prach_resource_grid_df


def create_prach_occasions_absolute_occupied_symbols(freq_range: str, duplex_mode: str, delta_f_ra_hz: int):
    """Create absolute starting symbols, PRACH duration, and absolute occupied symbols of the PRACH occasions.
    The absolute starting symbols are offset with regards to column "subframe number", interpreted from 15 kHz raster.

    TS 38.211 ch. 5.3.2.:
    - For Δf_RA in {1.25, 5} kHz, µ=0 shall be assumed (3GPP TS 38.211 ch. 5.3.2).

    Parameters
    ----------
    freq_range : str
        The frequency range, either FR1 or FR2.

    duplex_mode : str
        The duplex mode, either FDD or TDD.

    delta_f_ra_hz : int
        The subcarrier spacing of RACH Δf_RA.

    Returns
    -------
    prach_occasion_occupied_symbols_df : pandas.DataFrame
        The DataFrame with absolute starting symbols of the PRACH occasions.
        Columns: 'PRACH configuration index', 'Subframe/slot number', 'PRACH occasions starting symbols absolute', 'PRACH duration', 'PRACH occasions all occupied symbols', 'Number of all occupied symbols', 'Number of symbols per Frame'.

    Raises
    ------
    TypeError
        If freq_range is not a str.
    TypeError
        If duplex_mode is not a str.
    TypeError
        If delta_f_ra_hz is not a int.
    ValueError
        If delta_f_ra_hz is not associated with freq_range according to tools.freq_range_delta_f_ra_dict.

    """
    if not isinstance(freq_range, str):
        raise TypeError("freq_range should be of type str, but is {0}!".format(type(freq_range)))
    if not isinstance(duplex_mode, str):
        raise TypeError("duplex_mode should be of type str, but is {0}!".format(type(duplex_mode)))
    if not isinstance(delta_f_ra_hz, int):
        raise TypeError("delta_f_ra_hz should be of type int, but is {0}!".format(type(delta_f_ra_hz)))

    if delta_f_ra_hz not in tools.freq_range_delta_f_ra_dict[freq_range]:
        raise ValueError("delta_f_ra_hz = {0} Hz is not supported in {1}!".format(delta_f_ra_hz, freq_range))

    logger.debug("Starting to compute the absolute starting symbols of the PRACH occasions.")
    logger.debug("Parameters: freq_range={0}, duplex_mode={1}, Delta f_RA = {2} kHz.".format(freq_range, duplex_mode, delta_f_ra_hz / 1000.))
    prach_occasion_occupied_symbols_df = pd.DataFrame(columns=['PRACH configuration index', 'Subframe/slot number', 'PRACH occasion starting symbols absolute', 'PRACH duration', 'PRACH occasions all occupied symbols', 'Number of all occupied symbols', 'Number of symbols per Frame'])
    occasions_abs_lst = list()
    occupied_symbols_tuple = tuple()

    if delta_f_ra_hz in [1250, 5000]:
        mu = 0
    else:
        mu = tools.SCS_HZ_TO_NUMEROLOGY[delta_f_ra_hz]
    slots_per_frame = tables.ts_38_211_table_4_3_2_1(mu=mu, col="N slots per frame")
    symbols_per_frame = tools.N_SYMB_PER_SLOT * slots_per_frame

    for prach_conf_idx in range(0, 263):
        if freq_range == "FR1" and duplex_mode == "FDD":
            if prach_conf_idx == 256:
                break
            subframe_number = tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=prach_conf_idx)['Subframe number'][0]
            prach_duration = tables.ts_38_211_table_6_3_3_2_2(prach_conf_idx=prach_conf_idx)['PRACH duration'][0]
            reference_grid_hz = 15000
            if delta_f_ra_hz in [1250, 5000]:
                symbols_per_subframe = (int(15000 / reference_grid_hz)) * tools.N_SYMB_PER_SLOT
            else:
                symbols_per_subframe = (int(delta_f_ra_hz / reference_grid_hz)) * tools.N_SYMB_PER_SLOT
        elif freq_range == "FR1" and duplex_mode == "TDD":
            subframe_number = tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=prach_conf_idx)['Subframe number'][0]
            prach_duration = tables.ts_38_211_table_6_3_3_2_3(prach_conf_idx=prach_conf_idx)['PRACH duration'][0]
            reference_grid_hz = 15000
            if delta_f_ra_hz in [1250, 5000]:
                symbols_per_subframe = (int(15000 / reference_grid_hz)) * tools.N_SYMB_PER_SLOT
            else:
                symbols_per_subframe = (int(delta_f_ra_hz / reference_grid_hz)) * tools.N_SYMB_PER_SLOT
        elif freq_range == "FR2" and duplex_mode == "TDD":
            if prach_conf_idx == 256:
                break
            subframe_number = tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=prach_conf_idx)['Slot number'][0]
            prach_duration = tables.ts_38_211_table_6_3_3_2_4(prach_conf_idx=prach_conf_idx)['PRACH duration'][0]
            reference_grid_hz = 60000
            symbols_per_subframe = (int(delta_f_ra_hz / reference_grid_hz)) * tools.N_SYMB_PER_SLOT
        else:
            raise ValueError("The combination of {0} and {1} is not supported!".format(freq_range, duplex_mode))
        if isinstance(subframe_number, list):
            for j in subframe_number:
                offset_symbols = j * symbols_per_subframe
                occasions_list = list(tools.compute_rach_occasion_starting_symbols(prach_conf_idx=prach_conf_idx, freq_range=freq_range, duplex_mode=duplex_mode, delta_f_ra_hz=delta_f_ra_hz))
                occasions = [x + offset_symbols for x in occasions_list]
                occasions_abs_lst = occasions_abs_lst + occasions
        else:
            offset_symbols = subframe_number * symbols_per_subframe
            occasions_list = list(tools.compute_rach_occasion_starting_symbols(prach_conf_idx=prach_conf_idx, freq_range=freq_range, duplex_mode=duplex_mode, delta_f_ra_hz=delta_f_ra_hz))
            occasions_abs_lst = [x + offset_symbols for x in occasions_list]
        occasions_abs_tuple = tuple(
            sorted(
                occasions_abs_lst
            )
        )
        occ_symb_n = tuple()
        for n in occasions_abs_tuple:
            if prach_duration == 0:
                occ_symb_n = (n + int(prach_duration),)
            else:
                for x in range(0, prach_duration):
                    occ_symb_n = occ_symb_n + (n + x,)
            occupied_symbols_tuple = occupied_symbols_tuple + occ_symb_n
            occ_symb_n = tuple()
        prach_occasion_occupied_symbols_df.loc[prach_conf_idx] = [prach_conf_idx, subframe_number, occasions_abs_tuple, prach_duration, occupied_symbols_tuple, len(occupied_symbols_tuple), symbols_per_frame]

        occasions_abs_lst = []
        occasions_abs_tuple = tuple()
        occupied_symbols_tuple = tuple()

    path = pathlib.Path("tables")
    path.mkdir(parents=True, exist_ok=True)

    csv_filepath = os.path.abspath(
        os.path.join(
            "tables",
            "PRACH_Config_Idx_Occupied_Symbols_{0}_{1}_{2}_Hz.csv".format(freq_range, duplex_mode, delta_f_ra_hz)
        )
    )
    prach_occasion_occupied_symbols_df.to_csv(path_or_buf=csv_filepath, index=False)
    logger.debug("Computing the absolute starting symbols of the PRACH occasions finished.")
    return prach_occasion_occupied_symbols_df


def create_ssb_time_domain_occupied_symbols(case: str, nr_channel_center_freq_hz: int, duplex_mode: str, shared_spectrum_channel_access: bool):
    """Create tuples of all occupied symbols of SSB time domain pattern. Creates a separate tuple for PSS, SSS and PBCH.
    The choice of time domain transmission pattern case depends on 3GPP TS 38.104 Table 5.4.3.3-1.

    Parameters
    ----------
    case : str
        The time domain transmission pattern case.
        Choices: A, B, C, D, E, F, and G.

    nr_channel_center_freq_hz : int
        The 5G NR Channel Center Frequency in Hz.

    duplex_mode : str
        The duplex mode, either FDD or TDD.
        This is only relevant for Case C.

    shared_spectrum_channel_access : bool
        True, if operation with shared spectrum channel access applies, as described in 3GPP TS 37.213.

    Returns
    -------
    pss_symbol_pattern_tuple : tuple
        The tuple with all occupied PSS symbols of the SSB time domain pattern.

    sss_symbol_pattern_tuple : tuple
        The tuple with all occupied SSS symbols of the SSB time domain pattern.

    pbch_symbol_pattern_tuple : tuple
        The tuple with all occupied PBCH symbols of the SSB time domain pattern.

    all_occupied_ssb_symbols : tuple
        The tuple with all occupied symbols of the SSB time domain pattern.

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

    """
    if not isinstance(case, str):
        raise TypeError("case should be of type str, but is {0}!".format(type(case)))
    if not isinstance(nr_channel_center_freq_hz, int):
        raise TypeError("nr_channel_center_freq_hz should be of type int, but is {0}!".format(type(nr_channel_center_freq_hz)))
    if not isinstance(duplex_mode, str):
        raise TypeError("duplex_mode should be of type str, but is {0}!".format(type(duplex_mode)))
    if not isinstance(shared_spectrum_channel_access, bool):
        raise TypeError("shared_spectrum_channel_access should be of type bool, but is {0}!".format(type(shared_spectrum_channel_access)))

    if case not in tools.SSB_CASES:
        raise ValueError("Case {0} is not supported!".format(case))
    if nr_channel_center_freq_hz not in range(tools.freq_range_designation_dict["FR1"][0], tools.freq_range_designation_dict["FR1"][1] + 1):
        if nr_channel_center_freq_hz not in range(tools.freq_range_designation_dict["FR2"][0], tools.freq_range_designation_dict["FR2"][1] + 1):
            raise ValueError("A nr_channel_center_freq_hz of {0} Hz is not supported!".format(nr_channel_center_freq_hz))
    if duplex_mode not in ["FDD", "TDD"]:
        raise ValueError("The duplex_mode {0} is not supported!".format(duplex_mode))

    pss_symbol_pattern_tuple = tools.compute_ssb_time_domain_transmission_pattern(case=case, nr_channel_center_freq_hz=nr_channel_center_freq_hz, duplex_mode=duplex_mode, shared_spectrum_channel_access=shared_spectrum_channel_access)[0]
    sss_symbol_pattern_tuple = tuple()
    pbch_symbol_pattern_tuple = tuple()
    all_occupied_ssb_symbols = tuple()

    for n in pss_symbol_pattern_tuple:
        sss_symbol_pattern_tuple = sss_symbol_pattern_tuple + (n + 2,)
        pbch_symbol_pattern_tuple = pbch_symbol_pattern_tuple + (n + 1,) + (n + 2,) + (n + 3,)
        all_occupied_ssb_symbols = all_occupied_ssb_symbols + (n,) + (n + 1,) + (n + 2,) + (n + 3,)
    return pss_symbol_pattern_tuple, sss_symbol_pattern_tuple, pbch_symbol_pattern_tuple, all_occupied_ssb_symbols


def keys_exists(element: dict, *keys):
    """Check if *keys (nested) exists in `element` (dict).

    Parameters
    ----------
    element : dict
        The dict to be searched.
    *keys
        Keys of any type to be found in element.
        Can be appended with comma separation.

    Returns
    -------
    bool
        True, if all keys exist in the given dict.

    Raises
    ------
    AttributeError
        If element is not a dict.
    AttributeError
        If no keys are given.

    """
    if not isinstance(element, dict):
        raise TypeError('keys_exists() expects dict as first argument, but got {0} instead.'.format(type(element)))
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True


def get_keys(dictionary: dict):
    """Get all keys from a dict.

    TODO: Move to tools.

    Parameters
    ----------
    dictionary : dict
        The input dictionary.

    Returns
    -------
    result : list
        A list of all keys in the dict.
        Nested keys are reformatted as strings and returned step-wise and with "/"-separation.
        Example: ["key1", "key1/key2", "key1/key2/key3", "key1/key2/key3/key4"]

    """
    if not isinstance(dictionary, dict):
        raise TypeError('get_keys() expects dict as first argument, but got {0} instead.'.format(type(dictionary)))
    result = []
    for key, value in dictionary.items():
        if type(value) is dict:
            new_keys = get_keys(value)
            result.append(key)
            for innerkey in new_keys:
                result.append(f'{key}/{innerkey}')
        else:
            result.append(key)
    return result


if __name__ == "__main__":
    raise RuntimeError("generator.py has no main function and is not meant to be executed directly.")  # Not reached by tests. Only targets code errors.

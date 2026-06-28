#!/usr/bin/env python

# Copyright (c) 2026 Niels Hendrik Fliedner
#
# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL
# was not distributed with this file, You can obtain one at
# https://mozilla.org/MPL/2.0/.

"""Set up the logger.

.. code-block::
    :caption: Usage:

        import logging
        logger = logging.getLogger(__name__)

Raises
------
RuntimeError
    If this script is called directly or trying to access the main() function.

"""
import logging


def setup_logging(loglevel=logging.INFO, logfile="5GAutoConf.log"):
    """Set up the logging configuration with a global loglevel and logfile.

    Parameters
    ----------
    loglevel : int
        The loglevel.
    logfile : str
        The logfile.

    """
    logging.basicConfig(
        level=logging.DEBUG,  # always log DEBUG to file
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=logfile,
        filemode='a',
        encoding='utf-8'
    )

    console = logging.StreamHandler()
    console.setLevel(loglevel)

    formatter = logging.Formatter(
        '%(name)-12s: %(levelname)-8s %(message)s'
    )
    console.setFormatter(formatter)

    logging.getLogger('').addHandler(console)


if __name__ == "__main__":
    raise RuntimeError("logging_config.py has no main function and is not meant to be executed directly.")  # Not reached by tests. Only targets code errors.

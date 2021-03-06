#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <slemaguer@coli.uni-saarland.de>

DESCRIPTION

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 10 October 2016
"""

import os
import sys
import traceback
import argparse as ap

import time
import subprocess       # Shell command calling
import re
import logging
from rendering.utils.ema import *

from multiprocessing import Process, Queue, JoinableQueue
from shutil import copyfile # For copying files

import numpy as np

###############################################################################
# Functions
###############################################################################
class EMARenderer:
    def __init__(self, conf, out_handle, logger, nb_proc, preserve):
        self.conf = conf
        self.logger = logger
        self.out_handle = out_handle
        self.nb_proc = nb_proc
        self.preserve = preserve

    def EMA2JSON(self, out_path, gen_labfile_base_lst):
        """
        Convert parameter to STRAIGHT params
        """

        # Convert duration to labels
        q = JoinableQueue()
        processs = []
        for base in range(self.nb_proc):
            t = EMAToJSON(self.conf, out_path, self.logger, q)
            t.start()
            processs.append(t)

        for base in gen_labfile_base_lst:
            base = base.strip()
            base = os.path.splitext(os.path.basename(base))[0]
            q.put(base)

        # stop workers
        for i in range(len(processs)):
            q.put(None)

        for t in processs:
            t.join()

    def debug_part(self, out_path, gen_labfile_base_lst):
        """
        Generate PLY debug information
        """
        list_processs = []
        for base in gen_labfile_base_lst:
            process = JSONtoPLY(self.conf, out_path, base, self.logger)
            process.start()

            if not self.nb_proc:
                process.join()
            else:
                list_processs.append(process)

        if self.nb_proc:
            for process in list_processs:
                process.join()


    def render(self, out_path, gen_labfile_base_lst):

        self.logger.info("EMA binary to JSON")
        self.EMA2JSON(out_path, gen_labfile_base_lst)


        # self.logger.info("PLY rendering")
        # self.debug_part(out_path, gen_labfile_base_lst)

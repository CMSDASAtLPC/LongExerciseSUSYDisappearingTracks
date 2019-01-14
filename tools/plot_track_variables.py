#!/bin/env python
from __future__ import division
import glob
from ROOT import *
from CfgUtils import readSamplesConfig
import treeplotter
import numpy as np
import multiprocessing

plot_config = {
    "pt": {"binw": 25, "xmin": 0, "xmax": 1000, "xlabel": "p_{T} (GeV)", "ylabel": "number of tracks / 25 GeV", "logx": False, "logy": True},
    "dxyVtx": {"binw": 0.001, "xmin": 0, "xmax": 0.03, "xlabel": "dxy (cm)", "ylabel": "number of tracks / 0.001", "logx": False, "logy": True},
    "nValidPixelHits": {"binw": 1, "xmin": 0, "xmax": 12, "xlabel": "valid pixel hits", "ylabel": "number of tracks", "logx": False, "logy": True},
    "nValidTrackerHits": {"binw": 1, "xmin": 0, "xmax": 12, "xlabel": "valid tracker hits", "ylabel": "number of tracks", "logx": False, "logy": True},
              }

my_cuts = ""

# plot short tracks (pixel-only)
treeplotter.loop_over_files("/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/tracks-pixelonly", "samples.cfg", plot_config, tree_folder_name="PreSelection", cutstring = my_cuts, suffix="_short", ignore_samples="g1800_chi1400", folder="./plots")

# plot long tracks (pixel+strips)
treeplotter.loop_over_files("/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/tracks-pixelstrips", "samples.cfg", plot_config, tree_folder_name="PreSelection", cutstring = my_cuts, suffix="_long", ignore_samples="g1800_chi1400", folder="./plots")




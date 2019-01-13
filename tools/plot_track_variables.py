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
    "dzVtx": {"binw": 0.005, "xmin": 0, "xmax": 0.1, "xlabel": "dz (cm)", "ylabel": "number of tracks / 0.005", "logx": False, "logy": True},
    "nValidPixelHits": {"binw": 1, "xmin": 0, "xmax": 12, "xlabel": "valid pixel hits", "ylabel": "number of tracks", "logx": False, "logy": True},
    "nValidTrackerHits": {"binw": 1, "xmin": 0, "xmax": 12, "xlabel": "valid tracker hits", "ylabel": "number of tracks", "logx": False, "logy": True},
    "nMissingOuterHits": {"binw": 1, "xmin": 0, "xmax": 15, "xlabel": "missing outer hits", "ylabel": "number of tracks", "logx": False, "logy": True},
    "matchedCaloEnergy": {"binw": 2, "xmin": 0, "xmax": 50, "xlabel": "E_{dep} (GeV)", "ylabel": "number of tracks / 2", "logx": False, "logy": True},
    "trkRelIso": {"binw": 0.01, "xmin": 0, "xmax": 0.2, "xlabel": "relative isolation", "ylabel": "number of tracks / 0.01", "logx": False, "logy": True},
    "ptErrOverPt2": {"binw": 0.01, "xmin": 0, "xmax": 0.5, "xlabel": "#Delta p_{T} / p_{T}^{2}", "ylabel": "number of tracks / 0.01", "logx": False, "logy": True},
              }

my_cuts = ""

treeplotter.loop_over_files("/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/tracking/track-tag/tracks-short", "samples.cfg", plot_config, tree_folder_name="PreSelection", cutstring = my_cuts, suffix="_short", ignore_samples="g1800_chi1400")

plot_config["ptErrOverPt2"]["binw"] = 0.002
plot_config["ptErrOverPt2"]["xmax"] = 0.1
plot_config["ptErrOverPt2"]["ylabel"] = "number of tracks / 0.002"

treeplotter.loop_over_files("/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/tracking/track-tag/tracks-long", "samples.cfg", plot_config, tree_folder_name="PreSelection", cutstring = my_cuts, suffix="_long", ignore_samples="g1800_chi1400")




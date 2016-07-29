# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 06:52:02 2016

@author: Axel
"""

import mne
data_path = 'C:/Anaconda2/Lib/site-packages/examples/BCICIV_1_asc/'
mrkfilePath = data_path + 'BCICIV_calib_ds1a_mrk.txt'


pts = mne.io.kit.read_mrk(fname=mrkfilePath)
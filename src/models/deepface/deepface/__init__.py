# -*- coding: utf-8 -*-
"""deepface
"""

from . import confs
from . import detectors
from . import recognizers
from . import utils

from .shortcuts import \
    get_detector, \
    get_recognizer, \
    save_features

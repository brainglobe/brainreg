import os

import numpy as np
from numpy.testing import assert_array_equal, assert_raises
import tifffile

from brainreg.utils.preprocess import pre_process_fmost


def test_background_removal():
    test_img_path = os.path.join(  # the middle layer (raw)
        os.getcwd(),
        "tests",
        "data",
        "input",
        "pre_processing",
        "191797_red_mm_SLA_layer280.tif"
    )
    test_out_path = os.path.join(  # the middle layer (pre-processed)
        os.getcwd(),
        "tests",
        "data",
        "input",
        "pre_processing",
        "191797_red_mm_SLA_layer280_clean_no_bg.tif"
    )
    test_img = tifffile.imread(test_img_path)
    test_out = tifffile.imread(test_out_path)
    pre_processed_test_img = pre_process_fmost(test_img)
    assert_array_equal(pre_processed_test_img.astype(np.uint16), test_out)

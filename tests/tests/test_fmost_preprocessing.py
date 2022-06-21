import os

import numpy as np
from numpy.testing import assert_array_equal, assert_raises
import tifffile

from brainreg.utils.preprocess import subtract_background


def test_background_removal():
    test_img_path = os.path.join(  # the middle layer
        os.getcwd(),
        "tests",
        "data",
        "brain data",
        "image_0134.tif"
    )
    test_img = tifffile.imread(test_img_path)
    mask = subtract_background(test_img)
    assert_raises(AssertionError, assert_array_equal, mask, np.zeros_like(test_img))  # mask shouldn't be all 0s
    assert_raises(AssertionError, assert_array_equal, mask, np.ones_like(test_img))  # mask shouldn't be all 1s

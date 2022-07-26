import os

import numpy as np
import pandas as pd
from imio.load import load_any

relative_tolerance = 0.01
absolute_tolerance = 10
check_less_precise_pd = 1


def check_volumes_equal(output_directory, test_output_directory):
    pd.testing.assert_frame_equal(
        pd.read_csv(os.path.join(output_directory, "volumes.csv")),
        pd.read_csv(os.path.join(test_output_directory, "volumes.csv")),
    )


def check_images_same(image_name, output_directory, test_output_directory):
    image = load_any(
        os.path.join(output_directory, image_name),
    )
    test_image = load_any(
        os.path.join(test_output_directory, image_name),
    )
    np.testing.assert_allclose(
        image, test_image, rtol=relative_tolerance, atol=absolute_tolerance
    )

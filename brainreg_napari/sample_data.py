from typing import List

import numpy as np
import pooch
from napari.types import LayerData
from skimage.io import imread

base_url = "https://raw.githubusercontent.com/brainglobe/brainreg/master/tests/data/brain%20data"


def load_sample() -> List[LayerData]:
    """
    Load some sample data.
    """
    data = []
    for i in range(270):
        url = f"{base_url}/image_{str(i).zfill(4)}.tif"
        file = pooch.retrieve(url=url, known_hash=None)
        data.append(imread(file))

    data = np.stack(data, axis=0)
    return [(data, {"name": 'Sample brain'}), ]

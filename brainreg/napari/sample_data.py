import zipfile
from typing import List

import numpy as np
import pooch
from napari.types import LayerData
from skimage.io import imread

# git SHA for version of sample data to download
data_commit_sha = "3bb18dd5ae2a85d10cafe1bfb3154b9f744a0fb3"

POOCH_REGISTRY = pooch.create(
    path=pooch.os_cache("brainreg_napari"),
    base_url=(
        "https://gin.swc.ucl.ac.uk/brainglobe/test-data/"
        f"raw/{data_commit_sha}/brainreg/"
    ),
    registry={
        "test_brain.zip": "7bcfbc45bb40358cd8811e5264ca0a2367976db90bcefdcd67adf533e0162b5f"  # noqa: E501
    },
)


def load_test_brain() -> List[LayerData]:
    """
    Load test brain data.
    """
    data = []

    try:
        brain_zip = POOCH_REGISTRY.fetch("test_brain.zip")
    except OSError:
        pooch_url = POOCH_REGISTRY.base_url
        POOCH_REGISTRY.base_url = pooch_url.replace("https://", "http://")

        try:
            brain_zip = POOCH_REGISTRY.fetch("test_brain.zip")
        finally:
            POOCH_REGISTRY.base_url = pooch_url

    with zipfile.ZipFile(brain_zip, mode="r") as archive:
        for i in range(270):
            with archive.open(
                f"test_brain/image_{str(i).zfill(4)}.tif"
            ) as tif:
                data.append(imread(tif))

    data = np.stack(data, axis=0)
    meta = {"voxel_size": [50, 40, 40], "data_orientation": "psl"}
    return [
        (data, {"name": "Sample brain", "metadata": meta}, "image"),
    ]

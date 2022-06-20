import zipfile
from typing import List

import numpy as np
import pooch
from napari.types import LayerData
from skimage.io import imread

# git SHA for version of sample data to download
data_commit_sha = "72b73c52f19cee2173467ecdca60747a60e5fb95"

POOCH_REGISTRY = pooch.create(
    path=pooch.os_cache("brainreg_napari"),
    base_url=(
        "https://gin.g-node.org/cellfinder/data/"
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
    brain_zip = POOCH_REGISTRY.fetch("test_brain.zip")

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

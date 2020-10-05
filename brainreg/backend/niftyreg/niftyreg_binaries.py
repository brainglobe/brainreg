import os
import platform
from pkg_resources import resource_filename


__os_folder_names = {"Linux": "linux_x64", "Darwin": "osX", "Windows": "win64"}

try:
    os_folder_name = __os_folder_names[platform.system()]
except KeyError:
    raise ValueError(
        "Platform {} is not recognised as a valid platform. "
        "Valid platforms are : {}".format(
            platform.system(), __os_folder_names.keys()
        )
    )


def get_binary(binaries_folder, program_name):
    path = os.path.join(binaries_folder, os_folder_name, program_name)
    return path


def get_niftyreg_binaries():
    return resource_filename("brainreg", "bin/nifty_reg")

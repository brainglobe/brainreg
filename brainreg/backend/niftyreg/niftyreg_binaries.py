import os
from pkg_resources import resource_filename


def get_binary(binaries_folder, program_name):
    path = os.path.join(binaries_folder, program_name)
    return path


def get_niftyreg_binaries():
    return resource_filename("brainreg", "nifty_reg/bin")

import os
from pkg_resources import resource_filename
from brainreg import _nifty_reg_bin_dir


def get_binary(binaries_folder, program_name):
    path = os.path.join(binaries_folder, program_name)
    return path


def get_niftyreg_binaries():
    return _nifty_reg_bin_dir

# Dependencies that are extremely verbose at DEBUG level.
#
# `fancylog.start_logging` configures the root logger (unless `logger_name` is
# given, which brainreg cannot use because it logs via the root logger) and
# pins it to `file_log_level`, which defaults to "DEBUG". Every dependency
# logger would otherwise inherit that level, so brainreg's log file and
# console would fill with thousands of unrelated messages.
#
# Pass these to `fancylog.start_logging(third_party_loggers=...)`, which pins
# them to `third_party_log_level` ("WARNING" by default). brainreg's own log
# detail is unchanged, including when running with `--debug`.
NOISY_DEPENDENCY_LOGGERS = (
    "aiobotocore",
    "boto3",
    "botocore",
    "fsspec",
    "s3fs",
    "urllib3",
    "zarr",
)

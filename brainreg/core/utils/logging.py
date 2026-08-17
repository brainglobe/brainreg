import logging

# Dependencies that are extremely verbose at DEBUG level.
#
# `fancylog.start_logging` configures the root logger (unless `logger_name` is
# given, which brainreg cannot use because it logs via the root logger) and
# pins it to `file_log_level`, which defaults to "DEBUG". Every dependency
# logger inherits that level, so brainreg's log file and console fill with
# thousands of unrelated messages.
#
# This is worse than noise: a dependency emitting a badly formatted record
# breaks the code that logged it, because `rich.logging.RichHandler.emit` and
# `_pytest.logging.LogCaptureHandler.handleError` both let the resulting
# TypeError escape `Logger.handle`.
NOISY_DEPENDENCY_LOGGERS = (
    "aiobotocore",
    "boto3",
    "botocore",
    "fsspec",
    "s3fs",
    "urllib3",
    "zarr",
)


def quieten_dependency_logging(level=logging.WARNING):
    """
    Stop verbose dependencies from logging at the root logger's level.

    Call this after `fancylog.start_logging`. Only the loggers in
    `NOISY_DEPENDENCY_LOGGERS` are affected, so brainreg's own log detail is
    unchanged, including when running with `--debug`.

    Parameters
    ----------
    level
        Level to set the dependency loggers to. Default: `logging.WARNING`.

    """
    for logger_name in NOISY_DEPENDENCY_LOGGERS:
        logging.getLogger(logger_name).setLevel(level)

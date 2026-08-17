import logging

import pytest
from fancylog import fancylog

import brainreg as package_for_log
from brainreg.core.utils.logging import (
    NOISY_DEPENDENCY_LOGGERS,
    quieten_dependency_logging,
)


@pytest.fixture
def restore_logging():
    """
    fancylog mutates global logging state, so save and restore it.
    """
    root = logging.getLogger()
    old_level, old_handlers = root.level, root.handlers[:]
    old_dependency_levels = {
        name: logging.getLogger(name).level
        for name in NOISY_DEPENDENCY_LOGGERS
    }

    yield

    root.setLevel(old_level)
    root.handlers = old_handlers
    for name, level in old_dependency_levels.items():
        logging.getLogger(name).setLevel(level)


@pytest.fixture
def started_logging(tmp_path, restore_logging):
    fancylog.start_logging(
        str(tmp_path),
        package=package_for_log,
        verbose=False,
        log_header="TEST LOG",
        multiprocessing_aware=False,
    )


def test_fancylog_puts_root_logger_at_debug(started_logging):
    """
    Documents the fancylog behaviour this module exists to compensate for:
    `verbose` only sets the console handler level, while the root logger is
    always pinned to `file_log_level` (default "DEBUG").
    """
    assert logging.getLogger().level == logging.DEBUG


def test_dependencies_are_quietened(started_logging):
    quieten_dependency_logging()

    for name in NOISY_DEPENDENCY_LOGGERS:
        assert logging.getLogger(name).getEffectiveLevel() == logging.WARNING


def test_brainreg_logging_is_untouched(started_logging):
    """
    Quietening dependencies must not reduce brainreg's own log detail.
    """
    quieten_dependency_logging()

    assert logging.getLogger().level == logging.DEBUG
    assert logging.getLogger("brainreg").getEffectiveLevel() == logging.DEBUG


@pytest.mark.parametrize("name", NOISY_DEPENDENCY_LOGGERS)
def test_malformed_dependency_debug_record_does_not_reach_handlers(
    name, started_logging
):
    """
    Regression test for the failure that broke the whole test suite.

    With the root logger at DEBUG, a dependency emitting a badly formatted
    DEBUG record (as aiobotocore does in `regions.construct_endpoint`) raises
    TypeError out of `Logger.handle` under pytest, because
    `_pytest.logging.LogCaptureHandler.handleError` re-raises. That aborted
    unrelated dependency code, e.g. `BrainGlobeAtlas.check_latest_version`.

    Once the dependency logger is quietened the record is never emitted, so
    it cannot break the caller.
    """
    quieten_dependency_logging()

    # One placeholder, two arguments: formatting this raises TypeError.
    logging.getLogger(name).debug("only one %s", "a", "b")

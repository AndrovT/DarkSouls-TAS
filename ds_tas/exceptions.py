"""
Module for all DSTAS exceptions
"""


class DSTASException(Exception):
    """
    Base exception class

    """


class GameNotRunningError(DSTASException):
    """
    Run if there is an error that indicates
    Dark Souls is not running.
    """

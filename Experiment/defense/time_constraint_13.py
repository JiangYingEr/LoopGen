from loopgen_countermeasure_base import LoopGenCountermeasureBase


class TimeConstraint13(LoopGenCountermeasureBase):
    """Minimum inter-update window from the paper's Section 6."""

    APP_NAME = "time_constraint_13"
    ENABLE_LOOP_DETECTION = False
    MIN_UPDATE_INTERVAL_SEC = 0.05

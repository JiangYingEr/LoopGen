from loopgen_countermeasure_base import LoopGenCountermeasureBase


class LoopDetect13(LoopGenCountermeasureBase):
    """Controller-side loop detection from the paper's Section 6."""

    APP_NAME = "loop_detect_13"
    ENABLE_LOOP_DETECTION = True
    MIN_UPDATE_INTERVAL_SEC = None

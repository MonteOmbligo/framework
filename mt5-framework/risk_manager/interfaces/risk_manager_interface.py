from events.events import SizingEvent

from typing import Protocol

class IRiskManager(Protocol):

    def assess_order(self, sizing_event: SizingEvent) -> float | None:
        ...
        


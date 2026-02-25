from datetime import datetime

class Request:
    def __init__(self, plate: str, destination: str):
        self._plate = plate
        self._timestamp = datetime.now()
        self._destination = destination

    @property
    def plate(self) -> str:
        return self._plate

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def destination(self) -> str:
        return self._destination

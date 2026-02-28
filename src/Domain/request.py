from datetime import datetime
import uuid

class Request:
    def __init__(self, plate: str, destination: str):
        self._uuid = str(uuid.uuid4())
        self._plate = plate
        self._timestamp = datetime.now()
        self._destination = destination

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def plate(self) -> str:
        return self._plate

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def destination(self) -> str:
        return self._destination

    def to_dict(self):
        return {
            "uuid": self._uuid,
            "plate": self._plate,
            "timestamp": self._timestamp.isoformat(),
            "destination": self._destination
        }
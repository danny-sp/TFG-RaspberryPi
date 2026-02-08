from src.Domain.charger_type import ChargerType

class Charger:
    def __init__(self, id: int, type: ChargerType, busy: bool, active: bool):
        self._id = id
        self._type = type
        self._busy = busy
        self._active = active

    def insert(self):
        self._chargerDAO.insert(self)

    def update(self):
        self._chargerDAO.update(self)

    def delete(self):
        self._chargerDAO.delete(self)

    ##############
    # PROPERTIES #
    ##############
    @property
    def id(self) -> int:
        return self._id

    @property
    def type(self) -> ChargerType:
        return self._type

    @property
    def speed_kw(self) -> float:
        return self._type.kw_speed

    @property
    def busy(self) -> bool:
        return self._busy

    @property
    def active(self) -> bool:
        return self._active

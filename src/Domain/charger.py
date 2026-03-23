"""
Represents a charger in a charging station.
"""


class Charger:
    """
    Represents a charger in a charging station.

    Attributes:
        id (int): The unique identifier of the charger.
        power_kw (float): The power rating of the charger in kilowatts.
        busy (bool): Indicates whether the charger is currently in use.
    """

    def __init__(self, id: int, power_kw: float, busy: bool):
        self._id = id
        self._power_kw = power_kw
        self._busy = busy

    ##############
    # PROPERTIES #
    ##############
    @property
    def id(self) -> int:
        """
        The unique identifier of the charger.
        """
        return self._id

    @property
    def power_kw(self) -> float:
        """
        The power rating of the charger in kilowatts.
        """
        return self._power_kw

    @property
    def busy(self) -> bool:
        """
        Indicates whether the charger is currently in use.
        """
        return self._busy

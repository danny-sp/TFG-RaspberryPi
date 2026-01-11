class chargingStation:
    def __init__(self, id, latitude, longitude, power_kw):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.power_kw = power_kw

    def get_location(self):
        return (self.latitude, self.longitude)
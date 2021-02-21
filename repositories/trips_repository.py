class TripsRepository:
    def __init__(self, mongo_client):
        self.mongo = mongo_client

    def save_trip(self, trip):
        self.mongo.carpoolearg.trips.insert_one({"trip": trip})

    def get_all_trips(self):
        trips = self.mongo.carpoolearg.trips.find({})
        return [trip["trip"] for trip in trips]

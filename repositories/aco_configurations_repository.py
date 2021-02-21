class AcoConfigurationsRepository:
    def __init__(self, mongo_client):
        self.mongo = mongo_client

    def save_configurations(self, iter, evaporation_rate, debug):
        config = self.mongo.carpoolearg.aco_configurations.find_one()
        if config is None:
            self.mongo.carpoolearg.aco_configurations.insert_one(
                {"iter": iter, "evaporation_rate": evaporation_rate, "debug": debug}
            )
        else:
            self.mongo.carpoolearg.aco_configurations.replace_one(
                {"_id": config["_id"]},
                {"iter": iter, "evaporation_rate": evaporation_rate, "debug": debug}
            )

    def get_configurations(self):
        return self.mongo.carpoolearg.aco_configurations.find_one()

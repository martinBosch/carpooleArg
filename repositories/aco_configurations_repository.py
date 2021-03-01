class AcoConfigurationsRepository:
    def __init__(self, mongo_client):
        self.mongo = mongo_client

    def save_configurations(self, iter, evaporation_rate, debug, aco_algorithm, weight_best_tour_so_far, ants_per_iteration, number_ants_to_rank):
        config = self.mongo.carpoolearg.aco_configurations.find_one()
        document = {
            "iter": iter,
            "evaporation_rate": evaporation_rate,
            "debug": debug,
            "aco_algorithm": aco_algorithm,
            "weight_best_tour_so_far": weight_best_tour_so_far,
            "ants_per_iteration": ants_per_iteration,
            "number_ants_to_rank": number_ants_to_rank
        }

        if config is None:
            self.mongo.carpoolearg.aco_configurations.insert_one(document)
        else:
            self.mongo.carpoolearg.aco_configurations.replace_one(
                {"_id": config["_id"]},
                document
            )

    def get_configurations(self):
        return self.mongo.carpoolearg.aco_configurations.find_one()

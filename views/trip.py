from flask import Blueprint, request, render_template, url_for, redirect, flash
from aco.aco import ant_system, elitist_ant_system, rank_ant_system
from config import trips_repository, aco_configurations_repository

bp = Blueprint("trip", __name__, url_prefix="/trip")


nodes = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
         "M", "N", "O", "P"]


@bp.route("/publish", methods=['GET', 'POST'])
def publish_trip():
    if request.method == "POST":
        trip = list(request.form.to_dict().values())
        for node in trip:
            if node not in nodes:
                flash(f"El nodo \"{node}\" ingresado es invalido")
                return redirect(url_for("trip.publish_trip"))

        trips_repository.save_trip(trip)
        flash("Tu viaje a sido publicado!", "success")
        return redirect(url_for("trip.search_trip"))

    return render_template("trip/publish_trip.html")


@bp.route("/search", methods=['GET', 'POST'])
def search_trip():
    data = [
        {"from": "A", "to": "E"},
        {"from": "A", "to": "F"},
        {"from": "A", "to": "B"},
        {"from": "B", "to": "F"},
        {"from": "B", "to": "C"},
        {"from": "B", "to": "G"},
        {"from": "C", "to": "G"},
        {"from": "C", "to": "D"},
        {"from": "C", "to": "H"},
        {"from": "D", "to": "H"},
        {"from": "E", "to": "F"},
        {"from": "E", "to": "I"},
        {"from": "E", "to": "J"},
        {"from": "F", "to": "J"},
        {"from": "F", "to": "G"},
        {"from": "F", "to": "K"},
        {"from": "G", "to": "K"},
        {"from": "G", "to": "H"},
        {"from": "G", "to": "L"},
        {"from": "H", "to": "L"},
        {"from": "I", "to": "J"},
        {"from": "I", "to": "M"},
        {"from": "I", "to": "N"},
        {"from": "J", "to": "K"},
        {"from": "J", "to": "N"},
        {"from": "J", "to": "O"},
        {"from": "K", "to": "L"},
        {"from": "K", "to": "O"},
        {"from": "K", "to": "P"},
        {"from": "L", "to": "P"},
        {"from": "M", "to": "N"},
        {"from": "N", "to": "O"},
        {"from": "O", "to": "P"},
    ]

    trips = trips_repository.get_all_trips()

    if request.method == "POST":
        node_from = request.form["from"]
        if node_from not in nodes:
            return {"error": f"El nodo origen \"{node_from}\" ingresado es invalido"}

        node_to = request.form["to"]
        if node_to not in nodes:
            return {"error": f"El nodo destino \"{node_to}\" ingresado es invalido"}

        if not trips:
            return {"best_trip": []}

        aco_configurations = aco_configurations_repository.get_configurations()
        if aco_configurations is None:
            aco_configurations = {
                "iter": 50,
                "evaporation_rate": 0.1,
                "aco_algorithm": "ant_system",
                "weight_best_tour_so_far": 16,
                "ants_per_iteration": 10,
                "number_ants_to_rank": 6
            }
        iter = aco_configurations["iter"]
        evaporation_rate = aco_configurations["evaporation_rate"]
        aco_algorithm = aco_configurations["aco_algorithm"]

        if aco_algorithm == "ant_system":
            best_trip = ant_system(node_from, node_to, trips, iter, evaporation_rate)
        elif aco_algorithm == "elitist_ant_system":
            weight_best_tour_so_far = aco_configurations["weight_best_tour_so_far"]
            best_trip = elitist_ant_system(node_from, node_to, trips, iter, evaporation_rate, weight_best_tour_so_far)
        elif aco_algorithm == "rank_ant_system":
            ants_per_iteration = aco_configurations["ants_per_iteration"]
            number_ants_to_rank = aco_configurations["number_ants_to_rank"]
            best_trip = rank_ant_system(node_from, node_to, trips, iter, ants_per_iteration, number_ants_to_rank, evaporation_rate)
        else:
            best_trip = ant_system(node_from, node_to, trips, iter, evaporation_rate)

        return {"best_trip": best_trip}

    return render_template("trip/search_trip.html",
                           data=data,
                           trips=to_trips_output(trips))


def to_trips_output(trips):
    trips_output = []
    for trip in trips:
        for i in range(len(trip) - 1):
            nodo = trip[i]
            nodo_sig = trip[i + 1]
            trips_output.append({"from": nodo, "to": nodo_sig})

    return trips_output

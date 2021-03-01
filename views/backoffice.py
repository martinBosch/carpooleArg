from flask import Blueprint, render_template, url_for, redirect, request
from flask_socketio import emit

from aco.aco_backoffice import ant_system, elitist_ant_system, rank_ant_system
from config import socketIO, trips_repository, aco_configurations_repository
from views.trip import nodes


bp = Blueprint("backoffice", __name__, url_prefix="/backoffice")


@bp.route("/")
def home():
    return render_template("backoffice/index.html")


@bp.route("/trip/search")
def search_trip():
    data = [
        {"from": "A", "to": "E", "feromone": 1},
        {"from": "A", "to": "F", "feromone": 1},
        {"from": "A", "to": "B", "feromone": 1},
        {"from": "B", "to": "F", "feromone": 1},
        {"from": "B", "to": "C", "feromone": 1},
        {"from": "B", "to": "G", "feromone": 1},
        {"from": "C", "to": "G", "feromone": 1},
        {"from": "C", "to": "D", "feromone": 1},
        {"from": "C", "to": "H", "feromone": 1},
        {"from": "D", "to": "H", "feromone": 1},
        {"from": "E", "to": "F", "feromone": 1},
        {"from": "E", "to": "I", "feromone": 1},
        {"from": "E", "to": "J", "feromone": 1},
        {"from": "F", "to": "J", "feromone": 1},
        {"from": "F", "to": "G", "feromone": 1},
        {"from": "F", "to": "K", "feromone": 1},
        {"from": "G", "to": "K", "feromone": 1},
        {"from": "G", "to": "H", "feromone": 1},
        {"from": "G", "to": "L", "feromone": 1},
        {"from": "H", "to": "L", "feromone": 1},
        {"from": "I", "to": "J", "feromone": 1},
        {"from": "I", "to": "M", "feromone": 1},
        {"from": "I", "to": "N", "feromone": 1},
        {"from": "J", "to": "K", "feromone": 1},
        {"from": "J", "to": "N", "feromone": 1},
        {"from": "J", "to": "O", "feromone": 1},
        {"from": "K", "to": "L", "feromone": 1},
        {"from": "K", "to": "O", "feromone": 1},
        {"from": "K", "to": "P", "feromone": 1},
        {"from": "L", "to": "P", "feromone": 1},
        {"from": "M", "to": "N", "feromone": 1},
        {"from": "N", "to": "O", "feromone": 1},
        {"from": "O", "to": "P", "feromone": 1},
    ]
    trips = trips_repository.get_all_trips()

    return render_template("backoffice/search_trip.html",
                           data=data,
                           trips=to_trips_output(trips))


@socketIO.on("search_trip")
def handle_search_trip(data):
    node_from = data["from"]
    if node_from not in nodes:
        emit('search_trip_finish', {"error": f"El nodo origen \"{node_from}\" ingresado es invalido"})
        return
    node_to = data["to"]
    if node_to not in nodes:
        emit('search_trip_finish', {"error": f"El nodo destino \"{node_to}\" ingresado es invalido"})
        return

    trips = trips_repository.get_all_trips()
    if not trips:
        emit('search_trip_finish', {"best_trip": []})
        return

    aco_configurations = aco_configurations_repository.get_configurations()
    iter_input = aco_configurations["iter"]
    debug = aco_configurations["debug"]
    evaporation_rate = aco_configurations["evaporation_rate"]
    aco_algorithm = aco_configurations["aco_algorithm"]

    if aco_algorithm == "ant_system":
        best_trip = ant_system(node_from, node_to, trips, iter_input, evaporation_rate, debug)
    elif aco_algorithm == "elitist_ant_system":
        weight_best_tour_so_far = aco_configurations["weight_best_tour_so_far"]
        best_trip = elitist_ant_system(node_from, node_to, trips, iter_input, evaporation_rate, weight_best_tour_so_far, debug)
    elif aco_algorithm == "rank_ant_system":
        ants_per_iteration = aco_configurations["ants_per_iteration"]
        number_ants_to_rank = aco_configurations["number_ants_to_rank"]
        best_trip = rank_ant_system(node_from, node_to, trips, iter_input, ants_per_iteration, number_ants_to_rank, evaporation_rate, debug)
    else:
        best_trip = ant_system(node_from, node_to, trips, iter_input, evaporation_rate, debug)

    emit('search_trip_finish', {"best_trip": best_trip})


@bp.route("/trip/search/configs", methods=['POST'])
def save_search_trip_configs():
    iter_input = int(request.form["iter_input"])
    evaporation_rate = float(request.form["evaporation_rate"])
    debug = request.form["debug"] == "true"
    aco_algorithm = request.form["aco_algorithm"]
    weight_best_tour_so_far = int(request.form["weight_best_tour_so_far"])
    ants_per_iteration = int(request.form["ants_per_iteration"])
    number_ants_to_rank = int(request.form["number_ants_to_rank"])

    aco_configurations_repository.save_configurations(
        iter=iter_input,
        evaporation_rate=evaporation_rate,
        debug=debug,
        aco_algorithm=aco_algorithm,
        weight_best_tour_so_far=weight_best_tour_so_far,
        ants_per_iteration=ants_per_iteration,
        number_ants_to_rank=number_ants_to_rank
    )

    return {}


@bp.route("/trip/delete", methods=['POST'])
def delete_all_trips():
    trips_repository.delete_all_trips()
    return redirect(url_for("backoffice.search_trip"))


def to_trips_output(trips):
    trips_output = []
    for trip in trips:
        for i in range(len(trip) - 1):
            nodo = trip[i]
            nodo_sig = trip[i + 1]
            trips_output.append({"from": nodo, "to": nodo_sig})

    return trips_output

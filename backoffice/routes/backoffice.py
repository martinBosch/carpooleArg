from flask import Blueprint, session, render_template, url_for, redirect, request
from flask_socketio import emit

from backoffice.aco.aco import ant_system
from config import socketIO, trips_repository
from routes.trip import nodes


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

    iter_input = 25 if not data["iter_input"] else int(data["iter_input"])
    debug = data["debug"]
    evaporation_rate = 0.0 if not data["evaporation_rate"] else float(data["evaporation_rate"])
    session["iter"] = iter_input
    print("iter:", session["iter"])
    session["evaporation_rate"] = evaporation_rate
    print("evaporation rate:", session["evaporation_rate"])

    trips = trips_repository.get_all_trips()
    if not trips:
        emit('search_trip_finish', {"best_trip": []})
        return

    best_trip = ant_system(node_from, node_to, trips, iter_input, evaporation_rate, debug)
    emit('search_trip_finish', {"best_trip": best_trip})


@bp.route("/trip/search/configs", methods=['POST'])
def save_search_trip_configs():
    iter_input = 25 if not request.form["iter_input"] else int(request.form["iter_input"])
    evaporation_rate = 0.0 if not request.form["evaporation_rate"] else float(request.form["evaporation_rate"])
    session["iter"] = iter_input
    session["evaporation_rate"] = evaporation_rate
    return {}


@bp.route("/trip/delete", methods=['POST'])
def delete_all_trips():
    session["trips"] = {}
    return redirect(url_for("backoffice.search_trip"))


def to_trips_output(trips):
    trips_output = []
    for trip in trips:
        for i in range(len(trip) - 1):
            nodo = trip[i]
            nodo_sig = trip[i + 1]
            trips_output.append({"from": nodo, "to": nodo_sig})

    return trips_output

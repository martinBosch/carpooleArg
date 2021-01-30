from flask import Blueprint, session, render_template
from backoffice.aco import ant_system
from extensions import socketIO


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
    trips = session.get("trips", {})

    return render_template("backoffice/search_trip.html",
                           data=data,
                           trips=to_trips_output(trips))


@socketIO.on("search_trip")
def handle_search_trip(data):
    iter_input = 25 if not data["iter_input"] else int(data["iter_input"])
    debug = data["debug"]
    evaporation_rate = 0.0 if not data["evaporation_rate"] else float(data["evaporation_rate"])

    trips = session.get("trips", {})
    ant_system(trips, iter_input, evaporation_rate, debug)


def to_trips_output(trips):
    trips_output = []
    nodos = trips.keys()
    for nodo in nodos:
        nodos_sig = trips[nodo].keys()
        for nodo_sig in nodos_sig:
            trips_output.append({"from": nodo, "to": nodo_sig})

    return trips_output

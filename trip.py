from flask import Blueprint, request, render_template, session, url_for, redirect

from aco import Grafo, ant_system

bp = Blueprint("trip", __name__, url_prefix="/trip")


@bp.route("/publish", methods=['GET', 'POST'])
def publish_trip():
    if request.method == "POST":
        trip = list(request.form.to_dict().values())
        add_trip(trip)
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

    trips = session.get("trips", {})
    if request.method == "POST":
        iter = 50
        evaporation_rate = 0.1

        grafo = Grafo(grafo=trips)
        best_trip = ant_system(grafo, iter, evaporation_rate)
        return {"best_trip": best_trip}

    return render_template("trip/search_trip.html",
                           data=data,
                           trips=to_trips_output(trips))


def to_trips_output(trips):
    trips_output = []
    nodos = trips.keys()
    for nodo in nodos:
        nodos_sig = trips[nodo].keys()
        for nodo_sig in nodos_sig:
            trips_output.append({"from": nodo, "to": nodo_sig})

    return trips_output


def add_trip(trip):
    trips = session.get("trips", {})

    for i in range(len(trip) - 1):
        nodo = trip[i]
        nodo_sig = trip[i + 1]
        if nodo not in trips:
            trips[nodo] = {}
        trips[nodo][nodo_sig] = [1, 1]

    session["trips"] = trips

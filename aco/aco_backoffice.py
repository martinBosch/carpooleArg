from random import random
from time import sleep

from flask_socketio import emit


def choose_nodo_siguiente(probabilidades_a_nodos_sig, nodos_sig):
    p = [0, probabilidades_a_nodos_sig[0]]
    for i in range(1, len(probabilidades_a_nodos_sig)):
        p.append(p[-1] + probabilidades_a_nodos_sig[i])

    x = random()

    i = 0
    for j in range(len(p) - 1):
        if p[j] <= x < p[j + 1]:
            return nodos_sig[i]
        i += 1


def actualizar_feromonas(grafo, camino, distancia_camino, evaporation_rate, debug):
    grafo.evaporar_feromona(evaporation_rate)

    for i, j in zip(camino[0::1], camino[1::1]):
        feromona = 1 / distancia_camino
        grafo.actualizar_feromona(i, j, feromona)

    if debug:
        grafo.emit_feromona()
        sleep(0.5)


def elitist_actualizar_feromonas(grafo, camino, distancia_camino, best_tour_so_far, best_tour_so_far_distance, evaporation_rate, weight_best_tour_so_far, debug):
    grafo.evaporar_feromona(evaporation_rate)

    for i, j in zip(camino[0::1], camino[1::1]):
        feromona = 1 / distancia_camino
        grafo.actualizar_feromona(i, j, feromona)

    e = weight_best_tour_so_far
    for i, j in zip(best_tour_so_far[0::1], best_tour_so_far[1::1]):
        feromona = e / best_tour_so_far_distance
        grafo.actualizar_feromona(i, j, feromona)

    if debug:
        grafo.emit_feromona()
        sleep(0.5)


def rank_actualizar_feromonas(grafo, iteration_tours, number_ants_to_rank, best_tour_so_far, best_tour_so_far_distance, evaporation_rate, debug):
    grafo.evaporar_feromona(evaporation_rate)

    ranked_iteration_tours = sorted(iteration_tours, key=lambda x: x["distancia_camino"])
    w = number_ants_to_rank
    r = 1
    for ranked_tour in ranked_iteration_tours:
        camino = ranked_tour["camino"]
        distancia_camino = ranked_tour["distancia_camino"]
        for i, j in zip(camino[0::1], camino[1::1]):
            feromona = (w - r) / distancia_camino
            grafo.actualizar_feromona(i, j, feromona)

    for i, j in zip(best_tour_so_far[0::1], best_tour_so_far[1::1]):
        feromona = w / best_tour_so_far_distance
        grafo.actualizar_feromona(i, j, feromona)

    if debug:
        grafo.emit_feromona()
        sleep(0.5)


def probabilidades_a_nodos_siguentes(grafo, nodo):
    p = [grafo.feromona(nodo, vecino) * (1 / grafo.distancia(nodo, vecino)) for vecino in grafo.vecinos(nodo)]
    total = sum(p)
    return [e / total for e in p]


def elegir_siguiente_nodo(grafo, nodo):
    nodos_sig = grafo.vecinos(nodo)
    if len(nodos_sig) == 1:
        nodo_sig = nodos_sig[0]
    else:
        probabilidades_a_nodos_sig = probabilidades_a_nodos_siguentes(grafo, nodo)
        nodo_sig = choose_nodo_siguiente(probabilidades_a_nodos_sig, nodos_sig)

    return nodo_sig


def lanzar_hormiga(grafo, node_from, node_to, debug):
    nodo = node_from
    camino = [node_from]
    distancia_camino = 0

    while nodo != node_to and not grafo.es_nodo_final(nodo):
        nodo_sig = elegir_siguiente_nodo(grafo, nodo)
        if debug:
            emit("avanzar_hormiga", {"from": nodo, "to": nodo_sig})

        camino += [nodo_sig]
        distancia_camino += grafo.distancia(nodo, nodo_sig)
        nodo = nodo_sig
        if debug:
            sleep(0.1)

    return camino, distancia_camino


def ant_system(node_from, node_to, trips, iterations, evaporation_rate, debug):
    grafo = Grafo(trips)

    for iter_num in range(iterations):
        camino, distancia_camino = lanzar_hormiga(grafo, node_from, node_to, debug)
        if camino[0] == node_from and camino[-1] == node_to:
            actualizar_feromonas(grafo, camino, distancia_camino, evaporation_rate, debug)

        if debug:
            emit('hormiga_finish', iter_num + 1)
            sleep(0.5)
        else:
            emit('inc_iter', iter_num + 1)

    if not debug:
        grafo.emit_feromona()
        sleep(0.5)

    best_trip = grafo.mejor_camino(node_from, node_to)
    return best_trip


def elitist_ant_system(node_from, node_to, trips, iterations, evaporation_rate, weight_best_tour_so_far, debug):
    grafo = Grafo(trips)

    best_tour_so_far = None
    best_tour_so_far_distance = 0
    for iter_num in range(iterations):
        camino, distancia_camino = lanzar_hormiga(grafo, node_from, node_to, debug)
        if camino[0] == node_from and camino[-1] == node_to:
            if distancia_camino < best_tour_so_far_distance or best_tour_so_far is None:
                best_tour_so_far = camino
                best_tour_so_far_distance = distancia_camino

            elitist_actualizar_feromonas(grafo, camino, distancia_camino, best_tour_so_far, best_tour_so_far_distance, evaporation_rate, weight_best_tour_so_far, debug)

        if debug:
            emit('hormiga_finish', iter_num + 1)
            sleep(0.5)
        else:
            emit('inc_iter', iter_num + 1)

    if not debug:
        grafo.emit_feromona()
        sleep(0.5)

    best_trip = grafo.mejor_camino(node_from, node_to)
    return best_trip


def rank_ant_system(node_from, node_to, trips, iterations, ants_per_iteration, number_ants_to_rank, evaporation_rate, debug):
    grafo = Grafo(trips)

    best_tour_so_far = None
    best_tour_so_far_distance = 0
    for iter_num in range(iterations):
        iteration_tours = []
        for _ in range(ants_per_iteration):
            camino, distancia_camino = lanzar_hormiga(grafo, node_from, node_to, debug)
            if camino[0] == node_from and camino[-1] == node_to:
                if distancia_camino < best_tour_so_far_distance or best_tour_so_far is None:
                    best_tour_so_far = camino
                    best_tour_so_far_distance = distancia_camino

                iteration_tours.append({"camino": camino, "distancia_camino": distancia_camino})
            if debug:
                emit('hormiga_finish', iter_num)
                sleep(0.5)

        rank_actualizar_feromonas(grafo, iteration_tours, number_ants_to_rank, best_tour_so_far, best_tour_so_far_distance, evaporation_rate, debug)
        if debug:
            emit('hormiga_finish', iter_num + 1)
            sleep(0.5)
        else:
            emit('inc_iter', iter_num + 1)

    if not debug:
        grafo.emit_feromona()
        sleep(0.5)

    best_trip = grafo.mejor_camino(node_from, node_to)
    return best_trip


class Grafo:

    DISTANCIA = 0
    FEROMONA = 1

    def __init__(self, trips):
        self.grafo = self._init_grafo(trips)

    def es_nodo_final(self, nodo):
        return nodo not in self.grafo

    def vecinos(self, nodo):
        return [*self.grafo[nodo].keys()]

    def distancia(self, nodo_origen, nodo_destino):
        return self.grafo[nodo_origen][nodo_destino][self.DISTANCIA]

    def feromona(self, nodo_origen, nodo_destino):
        try:
            feromona = self.grafo[nodo_origen][nodo_destino][self.FEROMONA]
        except KeyError:
            feromona = 1.0
        return feromona

    def feromona_rounded(self, nodo_origen, nodo_destino):
        return round(self.feromona(nodo_origen, nodo_destino), 2)

    def actualizar_feromona(self, nodo_origen, nodo_destino, new_feromona):
        self.grafo[nodo_origen][nodo_destino][self.FEROMONA] += new_feromona

    def evaporar_feromona(self, evaporation_rate):
        for nodo_origen in self.grafo:
            for nodo_destino in self.grafo[nodo_origen]:
                self.grafo[nodo_origen][nodo_destino][self.FEROMONA] *= 1 - evaporation_rate

    def emit_feromona(self):
        for nodo_origen in self.grafo:
            for nodo_destino in self.grafo[nodo_origen]:
                emit('actualizar_feromona', {"from": nodo_origen, "to": nodo_destino, "feromone": self.feromona_rounded(nodo_origen, nodo_destino)})

    def mejor_camino(self, node_from, node_to):
        mejor_camino = [node_from]

        nodo = node_from
        while nodo != node_to and not self.es_nodo_final(nodo):
            vecinos = self.vecinos(nodo)
            nodo_sig = vecinos[0]
            max_feromona = self.feromona(nodo, vecinos[0])
            for vecino in vecinos:
                if self.feromona(nodo, vecino) > max_feromona:
                    nodo_sig = vecino
            mejor_camino.append(nodo_sig)
            nodo = nodo_sig

        if mejor_camino[0] == node_from and mejor_camino[-1] == node_to:
            return mejor_camino
        else:
            return []

    def _init_grafo(self, trips):
        grafo = {}
        for trip in trips:
            for i in range(len(trip) - 1):
                nodo = trip[i]
                nodo_sig = trip[i + 1]
                if nodo not in grafo:
                    grafo[nodo] = {}
                grafo[nodo][nodo_sig] = [1, 1]

        return grafo

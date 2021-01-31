from random import random


def choose_nodo_siguiente(probabilidades_a_nodos_sig, nodos_sig):
    p = [0, probabilidades_a_nodos_sig[0]]
    for i in range(1, len(probabilidades_a_nodos_sig)):
        p.append(p[-1] + probabilidades_a_nodos_sig[i])

    x = random()

    i = 0
    for j in range(len(p)-1):
        if p[j] <= x < p[j+1]:
            return nodos_sig[i]
        i += 1


def actualizar_feromonas(grafo, camino, distancia_camino, evaporation_rate, node_from, node_to):
    grafo.evaporar_feromona(evaporation_rate)

    if camino[0] != node_from or camino[-1] != node_to:
        return

    for i, j in zip(camino[0::1], camino[1::1]):
        feromona = 1 / distancia_camino
        grafo.actualizar_feromona(i, j, feromona)


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


def lanzar_hormiga(grafo, node_from, node_to):
    nodo = node_from
    camino = [node_from]
    distancia_camino = 0

    while nodo != node_to and not grafo.es_nodo_final(nodo):
        nodo_sig = elegir_siguiente_nodo(grafo, nodo)
        camino += [nodo_sig]
        distancia_camino += grafo.distancia(nodo, nodo_sig)
        nodo = nodo_sig

    return camino, distancia_camino


def ant_system(node_from, node_to, trips, iterations, evaporation_rate):
    grafo = Grafo(trips=trips)

    for iter_num in range(iterations):
        camino, distancia_camino = lanzar_hormiga(grafo, node_from, node_to)
        print("camino:", camino)
        actualizar_feromonas(grafo, camino, distancia_camino, evaporation_rate, node_from, node_to)

    mejor_camino = grafo.mejor_camino(node_from, node_to)
    print("mejor_camino:", mejor_camino)
    print("grafo:", grafo.grafo)
    return mejor_camino


class Grafo:

    DISTANCIA = 0
    FEROMONA = 1

    def __init__(self, trips):
        self.grafo = trips
        self._reset_feromone()

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
            feromona = 1
        return round(feromona, 2)

    def actualizar_feromona(self, nodo_origen, nodo_destino, new_feromona):
        self.grafo[nodo_origen][nodo_destino][self.FEROMONA] += new_feromona

    def evaporar_feromona(self, evaporation_rate):
        for nodo_origen in self.grafo:
            for nodo_destino in self.grafo[nodo_origen]:
                self.grafo[nodo_origen][nodo_destino][self.FEROMONA] *= 1 - evaporation_rate

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

    def _reset_feromone(self):
        for nodo_origen in self.grafo:
            for nodo_destino in self.grafo[nodo_origen]:
                self.grafo[nodo_origen][nodo_destino][self.FEROMONA] = 1

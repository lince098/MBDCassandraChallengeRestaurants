import json
import matplotlib.path as mplPath
import numpy as np


class Vecindario:

    def __init__(self, id, tipo, puntos):
        """
        @param puntos puede ser un poligono obj["geometry"]["coordinates"]               [0][indice de puntos]
        @param puntos puede ser un array de poligonos obj["geometry"]["coordinates"]     [index poligono][0][indicepunto]]
        """
        self.id = id
        self.polygons = []
        if tipo == 'Polygon':
            self.addPolygon(list(map(lambda x: list(reversed(x)), puntos[0])))
        else:
            for i in range(len(puntos)):
                self.addPolygon(
                    list(map(lambda x: list(reversed(x)), puntos[i][0])))

    def addPolygon(self, puntos):
        self.polygons.append(mplPath.Path(np.array(puntos)))

    def estaDentro(self, restaurante):
        for index, poly in enumerate(self.polygons):
            if poly.contains_point(restaurante.location):
                return (self.id, index, restaurante.id)
        return None


class Restaurante:
    def __init__(self, id, location):
        self.id = id
        self.location = location
        self.location.reverse()


def dumpPolygon(neighborhood, dumpFile):
    for i in range(len(neighborhood["geometry"]["coordinates"][0])):
        neighborhood["geometry"]["coordinates"][0][i].reverse()
        dumpLine = "{0},0,{1},{2},{3},\"{4}\"\n".format(neighborhood["_id"]["$oid"],
                                                        i, neighborhood['name'],
                                                        neighborhood["geometry"]["type"],
                                                        neighborhood["geometry"]["coordinates"][0][i])
        dumpFile.write(dumpLine)


def dumpMultiPolygon(neighborhood, dumpFile):
    for i in range(len(neighborhood["geometry"]["coordinates"])):
        for j in range(len(neighborhood["geometry"]["coordinates"][i][0])):
            neighborhood["geometry"]["coordinates"][i][0][j].reverse()
            dumpLine = "{0},{1},{2},{3},{4},\"{5}\"\n".format(neighborhood["_id"]["$oid"],
                                                              i, j, neighborhood['name'],
                                                              neighborhood["geometry"]["type"],
                                                              neighborhood["geometry"]["coordinates"][i][0][j])
            dumpFile.write(dumpLine)


def dumpNeighborhood(neighborhood, dumpFile):
    if neighborhood['geometry']['type'] == 'MultiPolygon':
        dumpMultiPolygon(neighborhood, dumpFile)
    else:
        dumpPolygon(neighborhood, dumpFile)
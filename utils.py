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
            self.addPolygon(puntos[0])
        else:
            for i in range(len(puntos)):
                self.addPolygon(puntos[i][0])

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


def dumpPolygon(neighborhood, dumpFile):
    for i in range(len(neighborhood["geometry"]["coordinates"][0])):
        dumpLine = "{0},0,{1},{2},{3},{4}\n".format(neighborhood["_id"]["$oid"],
                                                    i, neighborhood['name'],
                                                    neighborhood["geometry"]["type"],
                                                    neighborhood["geometry"]["coordinates"][0][i])
        dumpFile.write(dumpLine)


def dumpMultiPolygon(neighborhood, dumpFile):
    for i in range(len(neighborhood["geometry"]["coordinates"])):
        for j in range(len(neighborhood["geometry"]["coordinates"][i][0])):
            dumpLine = "{0},{1},{2},{3},{4},{5}\n".format(neighborhood["_id"]["$oid"],
                                                          i, j, neighborhood['name'],
                                                          neighborhood["geometry"]["type"],
                                                          neighborhood["geometry"]["coordinates"][i][0][j])
            dumpFile.write(dumpLine)


def dumpNeighborhood(neighborhood, dumpFile):
    if neighborhood['geometry']['type'] == 'MultiPolygon':
        dumpMultiPolygon(neighborhood, dumpFile)
    else:
        dumpPolygon(neighborhood, dumpFile)


##############################################

# Funciones de mierda que hacen la conexión con
# cassandra e insertan uno a uno en vez de hacer
# un puto csv con los datos y pasarlos al container
# F por mi tiempo

###############################################


def insertRestaurantLine(line, session):
    restaurant = json.loads(line)
    stmt = session.prepare(
        'INSERT INTO restaurants (id, location, name, type) values(?, ?, ?, ?)')
    args = [restaurant["_id"]["$oid"], restaurant["location"]
            ["coordinates"], restaurant["name"], restaurant["location"]["type"]]
    session.execute(stmt, args)


def insertPoligon(obj, session):
    i = 0
    for _ in obj["geometry"]["coordinates"][0]:
        stmt = session.prepare('INSERT INTO neighborhoods (id, "polygonNumber", "pointNumber",name, type, point) \
                               values(?, ?, ?, ?, ?, ?)')
        args = [obj["_id"]["$oid"], 0, i, obj['name'], obj["geometry"]
                ["type"], obj["geometry"]["coordinates"][0][i]]
        session.execute(stmt, args)
        i += 1


def insertMultiPoligon(obj, session):
    i = 0
    for _ in obj["geometry"]["coordinates"]:
        j = 0
        for _ in obj["geometry"]["coordinates"][i][0]:

            stmt = session.prepare('INSERT INTO neighborhoods (id, "polygonNumber", "pointNumber",name, type, point) \
                                   values(?, ?, ?, ?, ?, ?)')
            args = [obj["_id"]["$oid"], i, j, obj['name'], obj["geometry"]
                    ["type"], obj["geometry"]["coordinates"][i][0][j]]
            session.execute(stmt, args)
            j += 1
        i += 1


def insertNeighborhood(line, session):
    obj = json.loads(line)
    if obj['geometry']['type'] == 'MultiPolygon':
        insertMultiPoligon(obj, session)
    else:
        insertPoligon(obj, session)

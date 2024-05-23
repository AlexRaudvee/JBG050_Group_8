# Imports
import geopandas

import numpy as np

from typing import List
from shapely.ops import split
from shapely.geometry import MultiPolygon, Polygon, LineString


def rhombus(square: Polygon):
    """
    Naively transform the square into a Rhombus at a 45 degree angle
    """
    coords = square.boundary.coords.xy
    xx = list(coords[0])
    yy = list(coords[1])
    radians = 1
    points = list(zip(xx, yy))
    Rhombus = Polygon(
        [
            points[0],
            points[1],
            points[3],
            ((2 * points[3][0]) - points[2][0], (2 * points[3][1]) - points[2][1]),
            points[4],
        ]
    )
    return Rhombus


def get_squares_from_rect(RectangularPolygon: Polygon, side_length: float = 0.0025):
    """
    Divide a Rectangle (Shapely Polygon) into squares of equal area.

    `side_length` : required side of square

    """
    rect_coords = np.array(RectangularPolygon.boundary.coords.xy)
    y_list = rect_coords[1]
    x_list = rect_coords[0]
    y1 = min(y_list)
    y2 = max(y_list)
    x1 = min(x_list)
    x2 = max(x_list)
    width = x2 - x1
    height = y2 - y1

    xcells = int(np.round(width / side_length))
    ycells = int(np.round(height / side_length))

    yindices = np.linspace(y1, y2, ycells + 1)
    xindices = np.linspace(x1, x2, xcells + 1)
    horizontal_splitters = [
        LineString([(x, yindices[0]), (x, yindices[-1])]) for x in xindices
    ]
    vertical_splitters = [
        LineString([(xindices[0], y), (xindices[-1], y)]) for y in yindices
    ]
    result = RectangularPolygon
    for splitter in vertical_splitters:
        result = MultiPolygon(split(result, splitter))
    for splitter in horizontal_splitters:
        result = MultiPolygon(split(result, splitter))
    square_polygons = list(result.geoms)

    return square_polygons


def split_polygon(G: Polygon, side_length: float = 0.025, shape: str = "square", thresh: float = 0.9) -> List:
    """
    Using a rectangular envelope around `G`, creates a mesh of squares of required length.
    
    Removes non-intersecting polygons. 
            

    Args:
    
    - `thresh` : Range - [0,1]

        This controls - the number of smaller polygons at the boundaries.
        
        A thresh == 1 will only create (or retain) smaller polygons that are 
        completely enclosed (area of intersection=area of smaller polygon) 
        by the original Geometry - `G`.
        
        A thresh == 0 will create (or retain) smaller polygons that 
        have a non-zero intersection (area of intersection>0) with the
        original geometry - `G` 

    - `side_length` : Range - (0,infinity)
        side_length must be such that the resultant geometries are smaller 
        than the original geometry - `G`, for a useful result.

        side_length should be >0 (non-zero positive)

    - `shape` : {square/rhombus}
        Desired shape of subset geometries. 


    """
    assert side_length>0, "side_length must be a float>0"
    Rectangle    = G.envelope
    squares      = get_squares_from_rect(Rectangle, side_length=side_length)
    SquareGeoDF  = geopandas.GeoDataFrame(squares).rename(columns={0: "geometry"}).set_geometry('geometry')
    print(SquareGeoDF.set_geometry('geometry'))
    Geoms        = SquareGeoDF[SquareGeoDF.intersects(G)].geometry.values
    if shape == "rhombus":
        Geoms = [rhombus(g) for g in Geoms]
        geoms_ = [g for g in Geoms if ((g.intersection(G)).area / g.area) >= thresh]
    elif shape == "square":
        geoms_ = [g for g in Geoms if ((g.intersection(G)).area / g.area) >= thresh]

    geoms = []
    for polygon in geoms_:
        geoms.append(list(polygon.exterior.coords))
    return geoms
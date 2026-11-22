import numpy.typing as npt
import numpy as np
import shapely
import pyogrio

LAND_FGB_PATH = 'data/land_polygons_indexed.fgb'
INLAND_WATER_FGB_PATH = 'data/inland_water_indexed.fgb'

#lat, lon
def points_are_water(points: npt.NDArray):

    min_coords = points.min(axis=0)
    max_coords = points.max(axis=0)
    bbox = (min_coords[1], min_coords[0], max_coords[1], max_coords[0])
    point_geoms = shapely.points(points[:, 1], points[:, 0])

    is_inland = check_points_intersect(point_geoms, bbox, LAND_FGB_PATH)
    is_inland_water = check_points_intersect(point_geoms, bbox, INLAND_WATER_FGB_PATH)

    return ~is_inland | is_inland_water

def check_points_intersect(point_geoms, bbox, fgb_path):

    intersects = np.zeros(len(point_geoms), dtype=bool)

    _, table = pyogrio.read_arrow(fgb_path, bbox=bbox)
    wkb_array = table["wkb_geometry"].to_numpy()

    valid_mask = np.array([len(b) > 0 for b in wkb_array], dtype=bool)
    if not np.any(valid_mask):
        return intersects
    
    geometries = shapely.from_wkb(wkb_array)

    tree = shapely.STRtree(geometries)
    point_indices = tree.query(point_geoms, predicate='intersects')[0]
    intersects[point_indices] = True

    return intersects

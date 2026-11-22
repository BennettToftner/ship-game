import numpy as np
import numpy.typing as npt
import splines

A = 6378137
F = 1/298.257223563
B = A * (1 - F)
E_2 = 2*F - F*F
E_2_PRIME = E_2 / ((1 - F) * (1 - F))

NUM_SAMPLES = 500

def wgs84_to_cartesian(coords: npt.NDArray):

    lat_rad = np.deg2rad(coords[:, 0])
    lon_rad = np.deg2rad(coords[:, 1])
    h = coords[:, 2]
    cos_lat = np.cos(lat_rad)
    sin_lat = np.sin(lat_rad)
    cos_lon = np.cos(lon_rad)
    sin_lon = np.sin(lon_rad)
    v = A / np.sqrt(1 - E_2 * sin_lat * sin_lat)
    x = (v + h) * cos_lat * cos_lon
    y = (v + h) * cos_lat * sin_lon
    z = ((1 - E_2) * v + h) * sin_lat
    return np.column_stack((x, y, z))

def cartesian_to_wgs84(coords: npt.NDArray):
    
    x = coords[:, 0]
    y = coords[:, 1]
    z = coords[:, 2]
    lon = np.arctan2(y, x)
    p = np.sqrt(x * x + y * y)
    theta = np.arctan2(z * A, p * B)
    lat = np.arctan2(z + E_2_PRIME * B * np.power(np.sin(theta), 3), p - E_2 * A * np.power(np.cos(theta), 3))
    n = A / np.sqrt(1 - E_2 * np.power(np.sin(lat), 2))
    h = (p / np.cos(lat)) - n
    return np.column_stack((np.rad2deg(lat), np.rad2deg(lon), h))

def project_to_ellipsoid(points: npt.NDArray):
    wgs84 = cartesian_to_wgs84(points)
    wgs84[:, 2] = np.zeros((np.size(wgs84, axis=0)))
    return wgs84_to_cartesian(wgs84)

# possibly look at subdividing points along the earth's surface if they are too far apart
# which will reduce effect of splines cutting too far below earth's surface which may result in artifacts
def build_arc_length_table(points: npt.NDArray):
    cartesian_coords = wgs84_to_cartesian(points)
    spline = splines.CatmullRom(cartesian_coords, alpha=0.5)
    final_t = spline.grid[-1]
    t_values = np.linspace(0, final_t, NUM_SAMPLES)
    spline_points = spline.evaluate(t_values)
    surface_points = project_to_ellipsoid(spline_points)
    deltas = np.diff(surface_points, axis=0)
    segment_lengths = np.linalg.norm(deltas, axis=1)

    arc_lengths = np.empty(len(surface_points))
    arc_lengths[0] = 0.0
    arc_lengths[1:] = np.cumsum(segment_lengths)

    return np.column_stack((arc_lengths, surface_points))


def get_coordinate_from_table(arc_length_table: npt.NDArray, arc_length):
    # linearly interpolate between the two arc lengths on either side of the desired arc length

    if arc_length < arc_length_table[0, 0] or arc_length > arc_length_table[len(arc_length_table) - 1, 0]:
        return None
    idx_1 = np.searchsorted(arc_length_table[:, 0], arc_length)

    # should only happen when supplied arc_length is 0
    if idx_1 == 0:
        return arc_length_table[0, 1:]

    idx_0 = idx_1 - 1

    lower_length = arc_length_table[idx_0, 0]
    upper_length = arc_length_table[idx_1, 0]

    lower_coordinate = arc_length_table[idx_0, 1:]
    upper_coordinate = arc_length_table[idx_1, 1:]

    t = (arc_length - lower_length) / (upper_length - lower_length)

    return (1 - t) * lower_coordinate + t * upper_coordinate
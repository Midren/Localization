import numpy as np
from itertools import chain
from collections import defaultdict

@np.vectorize
def rssi_from_distance(d):
    return -20*np.log10(d)

def get_bins_according_to_accuracy(rssi, accuracy):
    bins = np.arange(rssi.min(), rssi.max())
    group_size = int(accuracy*2 + 1)

    split_indeces = list(range(group_size, bins.shape[0], group_size))
    if split_indeces[-1] != bins.shape[0] - 1:
        split_indeces.append(bins.shape[0]-1)

    bins = np.split(bins, split_indeces)
    bins=np.fromiter(map(np.mean, bins), dtype=float)

    return [bins[abs(bins - rssi[i]).argmin()] for i in range(rssi.shape[0])]

def get_intervals_with_same_rssi(rssi_bins, dist_bins):
    rssi_to_dist_map = defaultdict(list)
    for rssi, dist in zip(rssi_bins, dist_bins):
        rssi_to_dist_map[rssi].append(dist)
    return np.array([(min(distances), max(distances)) for distances in rssi_to_dist_map.values()])

def get_radiuses_for_distance_contour_lines_from_intevals(intervals):
    return np.array([end for st, end in intervals])

def get_radiuses_for_distance_contour_lines(rssi_accuracy, max_distance=10):
    distances = np.arange(0.01, max_distance, 0.01)
    rssi = rssi_from_distance(distances)
    rssi_bins = get_bins_according_to_accuracy(rssi, rssi_accuracy)
    return get_radiuses_for_distance_contour_lines_from_intevals(get_intervals_with_same_rssi(rssi_bins, distances))

def cartesian_cross_product(x,y):
    cross_product = np.transpose([np.tile(x, len(y)),np.repeat(y,len(x))])
    return cross_product

def distance(p1, p2):
    def helper(p1, p2):
        return (((p1[:,0] - p2[0])**2 + (p1[:,1] - p2[1])**2)**0.5)
    vectorized_distance = np.vectorize(helper, signature='(n,m),(m)->(n)')

    return np.apply_along_axis(lambda x: vectorized_distance(p1, x), 1, p2)

distance = np.vectorize(distance, signature='(n,m),(k,m)->(k,n)')

def find_interval_num(dist, radiuses):
    @np.vectorize
    def helper(dist):
        return (dist > radiuses).argmin() - 1
    return helper(dist)

def find_point_flag(p, beacons_location, radiuses):
    return find_interval_num(distance(p, beacons_location).T, radiuses)

find_point_flag = np.vectorize(find_point_flag, signature='(n,m),(i,m),(j)->(n,i)')

def drop_small_radiuses_groups(points_grouped, radiuses, minimum_radius=0.1):
    min_group = np.asscalar(find_interval_num(minimum_radius, radiuses))

    return dict(filter(lambda x: all(map(lambda x: x >= min_group, x[0])), points_grouped.items()))

def accuracy_by_box(points):
    x_boundary = np.array([min(points, key=lambda x: x[0])[0], max(points, key=lambda x: x[0])[0]])
    y_boundary = np.array([min(points, key=lambda x: x[1])[1], max(points, key=lambda x: x[1])[1]])

    minima, maxima = np.concatenate([x_boundary.reshape(1, -1), y_boundary.reshape(1, -1)]).T
    return np.asscalar(distance(minima.reshape(1,-1), maxima.reshape(1,-1)))/2

def accuracy_by_mean_dist(points):
    return np.mean(distance(points, points))

def calculate_per_region_accuracy(points_grouped, calculate_accuracy):
    return {region: calculate_accuracy(points) for region, points in points_grouped.items()}

def mean_accuracy(region_accuracy):
    return np.mean(np.fromiter(chain(region_accuracy.values()),dtype=float))

def group_points_by_region(points, point_flags):
    points_grouped_list = defaultdict(list)

    for i in range(point_flags.shape[0]):
         points_grouped_list[tuple(point_flags[i])].append(points[i])

    return {group: np.array(points_grouped_list[group]) for group in points_grouped_list.keys()}

def calculate_mean_accuracy(x_len, y_len, beacons_location, radiuses, delta=0.01):
    points = cartesian_cross_product(np.arange(0, x_len, delta), np.arange(0, y_len, delta))
    point_flags = find_point_flag(points, beacons_location, radiuses)

    points_grouped = drop_small_radiuses_groups(group_points_by_region(points, point_flags), radiuses)

    return mean_accuracy(calculate_per_region_accuracy(points_grouped, accuracy_by_box))

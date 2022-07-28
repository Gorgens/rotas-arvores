import grass.script as gscript
import itertools

def trail(elevation, friction, walk_coeff, lambda_, slope_factor, point_from, points_to, vect_paths):
    """Computes least cost path to multiple locations based on walking time"""
    gscript.run_command('r.walk', flags='k', elevation=elevation, friction=friction, lambda_=lambda_, walk_coeff=walk_coeff, slope_factor=slope_factor, start_coordinates=point_from, stop_coordinates=points_to, output='tmp_walk', outdir='tmp_walk_dir')
    for i in range(len(points_to)):
        gscript.run_command('r.drain', flags='d', input='tmp_walk', direction='tmp_walk_dir', output='tmp_drain', drain=vect_paths[i], start_coordinates=points_to[i], overwrite=True)
    gscript.run_command('g.remove', type=['raster', 'vector'], name=['tmp_walk', 'tmp_walk_dir', 'tmp_drain'], flags='f')


def trails_combinations(elevation, friction, walk_coeff, lambda_, slope_factor, points, vector_routes):
    coordinates = gscript.read_command('v.out.ascii', input=points, format='point', separator=',').strip()
    coords_list = []
    for coords in coordinates.split():
        coords_list.append(coords.split(',')[:2])
    combinations = itertools.combinations(coords_list, 2)
    combinations = [list(group) for k, group in itertools.groupby(combinations, key=lambda x: x[0])]
    i = k = 0
    vector_routes_list = []
    for points in combinations:
        i += 1
        point_from = ','.join(points[0][0])
        points_to = [','.join(pair[1]) for pair in points]
        vector_routes_list_drain = []
        for each in points_to:
            vector_routes_list_drain.append('route_path_' + str(k))
            k += 1
        vector_routes_list.extend(vector_routes_list_drain)
        trail(elevation, friction, walk_coeff, lambda_, slope_factor, point_from, points_to, vector_routes_list_drain)
    gscript.run_command('v.patch', input=vector_routes_list, output=vector_routes)


def trails_salesman(trails, points, output):
    gscript.run_command('v.net', input=trails, points=points, output='tmp_net', operation='connect', threshold=10)
    cats = gscript.read_command('v.category', input='tmp_net', layer=2, option='print').strip().split()
    gscript.run_command('v.net.salesman', input='tmp_net', output=output, center_cats=','.join(cats), arc_layer=1, node_layer=2)
    # remove temporary map
    gscript.run_command('g.remove', type='vector', name='tmp_net', flags='f')

if __name__ == '__main__':
    trails_combinations('campus_jk_nodata', friction='slope', walk_coeff=[0.72, 6, 0, 6], lambda_=0.5, slope_factor=0, points='markers', vector_routes='route_net')
    trails_salesman(trails='route_net', points='markers', output='route_salesman')
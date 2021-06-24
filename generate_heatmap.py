import click
import fitparse
import glob
import os.path
import collections
import timeit
import json
import datetime

folder_root = ''

API_KEY = os.environ['GOOGLE_MAPS_API_KEY']

# Garmin stores degrees as a 32-bit integer rather than a float. Divide by this
# to get a float of the degrees.
BIT_DEGREES_32 = 2**32 / 360

# copy-paste into debugger to look at the messages and try and reverse-engineer
def helpme(fitfile):
    i = 0
    print(i); fitfile.messages[i]; i+=1

@click.command()
@click.option(
    "--folder-root",
    help="Specify an input folder."
)
@click.option(
    "--initial-latitude",
    default=47.658941857516766
)
@click.option(
    "--initial-longitude",
    default=-122.31575896963477
)
@click.option(
    "--initial-zoom",
    default=13
)
@click.option(
    "--filter-sport",
    default="cycling"
)
def main(folder_root, initial_latitude, initial_longitude, initial_zoom, filter_sport):
    files = glob.glob(os.path.join(folder_root, '*.fit'))
    fitobjects = {}
    fitobjects_by_sport = collections.defaultdict(dict)
    sports = collections.Counter()
    
    all_points = []
    init_time = timeit.default_timer()
    for filename in files:
        start_time = timeit.default_timer()
        now = datetime.datetime.now().isoformat()
        print(f'{now} started parsing {filename}')
        objname = os.path.basename(filename)

        fitfile = fitparse.FitFile(filename)

        sport = fitfile.messages[17].get_value('sport')
        if sport is None:
            for message in fitfile.messages:
                sport = message.get_value('sport')
                if sport:
                    break
        if sport is None:
            raise(f'Could not find sport for {filename}')

        for message in fitfile.messages:
            latitude = message.get_value('position_lat')
            longitude = message.get_value('position_long')
            if (filter_sport == sport) and latitude is not None and longitude is not None:
                all_points.append([float(latitude / BIT_DEGREES_32), float(longitude / BIT_DEGREES_32)])

        sports[sport] += 1
        print(f'{filename} is {sport}')

        fitobjects[objname] = fitfile
        fitobjects_by_sport[sport][objname] = fitfile

        elapsed = timeit.default_timer() - start_time
        print(all_points[-1])
        all_points_len = len(all_points)
        print(f'parsed {filename} in {elapsed}. total points: {all_points_len}')

    total_elapsed = timeit.default_timer() - init_time

    print(f'total time elapsed: {total_elapsed} seconds')
    print(json.dumps(sports, indent=4, sort_keys=True))


    with open('output/cycling_objects.json', 'w') as cycs:
        cycs.write(
            json.dumps(
                list(fitobjects_by_sport['cycling'].keys()),
                indent=4,
                sort_keys=True
            )
        )

    with open(f'output/{filter_sport}_points.json', 'w') as f:
        f.write(
            json.dumps(
                list(all_points),
                indent=4,
                sort_keys=True
            )
        )

    generate_html(all_points, 'output.html',  folder_root, initial_latitude, initial_longitude, initial_zoom)

def get_outline():
    """Reads in the html outline file"""
    with open('map-outline.txt', 'r') as file:
        outline = file.read()
    return outline
    
def generate_html(points, file_out, folder_root, initial_latitude, initial_longitude, initial_zoom):
    """Generates a new html file with points"""
    if not os.path.exists('output'):
        os.mkdir('output')
    f = open(f"output/{file_out}.html", "w")
    outline = get_outline()
    google_points = ",\n".join([f"new google.maps.LatLng({point[0]}, {point[1]})" for point in points])
    updated_content = outline.replace("LIST_OF_POINTS", google_points).replace("API_KEY", API_KEY).replace("INIT_LATITUDE", str(initial_latitude)).replace("INIT_LONGITUDE", str(initial_longitude)).replace("INIT_ZOOM", str(initial_zoom))
    f.write(updated_content)
    f.close()

if __name__ == '__main__':
    main()

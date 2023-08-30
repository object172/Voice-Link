# -*- coding: utf-8 -*-

import os
import json
from PIL import Image, ImageDraw
import base64
from io import BytesIO

JSON = 'data.json'


def load():
    if not os.path.exists(JSON):
        print('file does not exist')
    else:
        with open(JSON) as fp:
            print('file is founded')
            return json.load(fp)


def get_color(color: int):
    if color in [0, 1, 2]:
        return 'green'
    elif color in [3, 4, 5, 6]:
        return 'yellow'
    elif color in [7, 8, 9]:
        return 'red'
    elif color == 10:
        return 'purple'
    else:
        return 'darkgrey'


def get_point(value, minimum, scale, shift=0) -> int:
    return int(float((value-minimum) * scale)) + shift


def get_circle_coord(x, y, r: int) -> list[tuple, tuple]:
    return [(x-r, y-r), (x+r, y+r)]


def get_picture(node_data: dict, link_data: dict,
                image_width: int, image_height: int) -> bytes:
    node_radius = 5

    max_lat = max([d['lat'] for d in node_data.values()])
    min_lat = min([d['lat'] for d in node_data.values()])

    diff_lat = max_lat - min_lat
    lat_scale = (image_height - (node_radius * 2))/diff_lat

    max_lng = max([d['lng'] for d in node_data.values()])
    min_lng = min([d['lng'] for d in node_data.values()])

    diff_lng = max_lng - min_lng
    lng_scale = (image_width - (node_radius * 2))/diff_lng

    im = Image.new('RGB', (image_width, image_height), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    for values in link_data.values():

        from_x = get_point(node_data[values['fromNodeId']]['lng'],
                           min_lng, lng_scale, node_radius)

        from_y = get_point(node_data[values['fromNodeId']]['lat'],
                           min_lat, lat_scale, node_radius)

        to_x = get_point(node_data[values['toNodeId']]['lng'],
                         min_lng, lng_scale, node_radius)

        to_y = get_point(node_data[values['toNodeId']]['lat'],
                         min_lat, lat_scale, node_radius)

        draw.line((from_x, from_y, to_x, to_y), width=4,
                  fill=get_color(values['load']))

    for node_data_value in node_data.values():

        x = get_point(node_data_value['lng'], min_lng, lng_scale, node_radius)
        y = get_point(node_data_value['lat'], min_lat, lat_scale, node_radius)

        draw.ellipse(get_circle_coord(x, y, node_radius),
                     fill='brown',
                     outline=(0, 0, 0))

    buffered = BytesIO()
    im.save(buffered, format="PNG")
    im.show()
    return base64.b64encode(buffered.getvalue())


if __name__ == '__main__':
    data = load()
    node_data = {}
    for item in data['graph']['nodes']:
        node_data[item['id']] = {'lng': item['location']['lng'],
                                 'lat': item['location']['lat']}

    link_data = {}
    for item in data['graph']['links']:
        link_data[item['id']] = {'fromNodeId': item['fromNodeId'],
                                 'toNodeId': item['toNodeId'],
                                 'load': None}

    for item in data['loads']:
        link_data[item['link_id']]['load'] = item['load']

    image_width = data['image']['width']
    image_height = data['image']['height']

    picture = get_picture(node_data, link_data, image_width, image_height)
    # print(picture)

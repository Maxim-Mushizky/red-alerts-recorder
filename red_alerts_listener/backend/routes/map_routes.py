from flask import Blueprint, render_template, jsonify
import os

from red_alerts_listener.backend.services.detection_service import get_detected_points

template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_dir = os.path.join(template_dir, 'frontend')
static_folder = os.path.join(template_dir, 'static')
template_dir = os.path.join(template_dir, 'templates')

map_blueprint = Blueprint('map_blueprint', __name__,
                          template_folder=template_dir,
                          static_folder=static_folder)


@map_blueprint.route('/map')
def show_map():
    # Replace with your dynamic data from the database
    detected_points = [
        {'lat': 31.7683, 'lon': 35.2137, 'name': 'Jerusalem'},
        {'lat': 32.0853, 'lon': 34.7818, 'name': 'Tel Aviv'}
    ]

    # Pass the points to the template
    return render_template('map.html', points=detected_points)


@map_blueprint.route('/test')
def test_page():
    return "<h1>This is a test page!</h1>"


@map_blueprint.route('/api/detected_points')
def get_points():
    points = get_detected_points()
    return jsonify(points)

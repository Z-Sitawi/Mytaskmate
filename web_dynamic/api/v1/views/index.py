from flask import jsonify
from models import storage
from web_dynamic.api.v1.views import app_views


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status():
    """ Status of API """
    return jsonify({"status": "OK"})


@app_views.route('/stats', methods=['GET'], strict_slashes=False)
def stats():
    """ Status of API """
    return jsonify({"users": storage.count('User'),
                    "missions": storage.count('Mission'),
                    "tasks": storage.count('Task')
                    })

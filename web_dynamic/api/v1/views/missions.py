from flask import jsonify, session, redirect, url_for
from models import storage
from web_dynamic.api.v1.views import app_views
from models.mission import Mission


@app_views.route('/missions/<m_id>', methods=['GET'], strict_slashes=False)
@app_views.route('/missions', methods=['GET'], strict_slashes=False)
def get_missions(m_id=None):
    """ Retrieves the list of all Mission objects if Mission id is none
        or a single Task based on the id
    """
    if m_id:
        return jsonify(storage.get('Mission', m_id).to_dict())

    missions_list = []
    for m in storage.all("Mission").values():
        missions_list.append(m.to_dict())
    return jsonify(missions_list)


@app_views.route('/missions', methods=['DELETE'], strict_slashes=False)
def del_mission():
    """ Deletes a mission and all its tasks based on its id """
    if 'user' in session:
        user_id = session['user']
        # Retrieve user details based on the user ID
        user = storage.get('User', user_id)
        if user:
            storage.delete_active_mission(user_id)
            return "Mission deleted"
        else:
            # Handle case where user details cannot be retrieved
            return "User details not found", 404
    else:
        # Redirect to login page if user is not logged in
        return redirect(url_for('app_views.login'))


@app_views.route('/missions', methods=['POST'], strict_slashes=False)
def create_mission():
    """ Creates a Mission object """
    if 'user' in session:
        user_id = session['user']
        # Retrieve user details based on the user ID
        user = storage.get('User', user_id)
        if user:
            m_obj = Mission(user_id=user_id)
            storage.new(m_obj)
            storage.save()
            return "Mission created"
        else:
            # Handle case where user details cannot be retrieved
            return "User details not found", 404
    else:
        # Redirect to login page if user is not logged in
        return redirect(url_for('app_views.login'))


@app_views.route('/active', methods=['GET'])
def active():
    if 'user' in session:
        user_id = session['user']
        active_mission = storage.get_active_mission(user_id)
        if active_mission:
            # Check if the active_mission's user_id matches the user_id from the session
            if active_mission.user_id == user_id:
                return jsonify(active_mission.to_dict())
            else:
                return "Unauthorized", 401  # Return 401 Unauthorized if the user_id doesn't match
        else:
            return jsonify({"active": False,
                            "completed_tasks": None,
                            "created_at": None,
                            "id": None,
                            "total_tasks": None,
                            "updated_at": None,
                            "user_id": None
                            })
    else:
        return "Unauthorized", 401


@app_views.route('/deactivate/<m_id>', methods=['PUT'])
def deactivate_mission(m_id):
    print('in deactivate mission')
    if 'user' in session:
        print("Logged in")
        user_id = session['user']
        storage.deactivate_mission(m_id, user_id)
        return jsonify({})
    else:
        print("Not Logged in")
        return "Unauthorized", 401

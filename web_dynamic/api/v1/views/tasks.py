from flask import jsonify, session, redirect, url_for
from models import storage
from web_dynamic.api.v1.views import app_views
from models.task import Task


@app_views.route('/tasks', methods=['GET'], strict_slashes=False)
def get_tasks():
    """ Retrieves the list of all Task objects """
    tasks_list = [task.to_dict() for task in storage.all("Task").values()]
    return jsonify(tasks_list)


# @app_views.route('/tasks/<t_id>', methods=['GET'], strict_slashes=False)
# def get_task(t_id):
#     """ Retrieves a single Task object based on its id """
#     task = storage.get('Task', t_id)
#     if task:
#         return jsonify(task.to_dict())
#     else:
#         return "Task not found", 404


@app_views.route('/tasks/<t_id>', methods=['DELETE'], strict_slashes=False)
def delete_task(t_id):
    """ Deletes a task based on its id """
    if 'user' not in session:
        return "Not Authorized", 403

    user_id = session['user']
    user = storage.get('User', user_id)
    task = storage.get('Task', t_id)

    if not user or not task:
        return "User or Task not found", 404

    if task.completed:
        storage.update("Mission", task.mission_id, new_value=False, att=2)
    storage.update("Mission", task.mission_id, new_value=False, att=1)
    storage.delete('Task', t_id)
    return "Task deleted Successfully"


@app_views.route('/tasks/<m_id>/<title>', methods=['POST'], strict_slashes=False)
def create_task(m_id, title=None):
    """ Creates a Task object for a given mission ID """
    print("In create task API")
    if 'user' in session:
        user_id = session['user']
        # Retrieve user details based on the user ID
        user = storage.get('User', user_id)
        if user and m_id and title:
            if not title.endswith('.'):
                title += '.'
            print(f"User Id: {user_id}, M_ID: {m_id}, Title: {title}")
            task = Task(title=title.capitalize(), mission_id=m_id)
            print("Task object created")
            storage.new(task)
            print("Task object added to session")
            storage.save()
            print("Task object saved")
            storage.update("Mission", m_id, new_value=True, att=1)
            print("Mission object updated")
            return "A New Task Has Been Created Successfully"
        else:
            # Handle case where user details cannot be retrieved
            print("User details not found in create task API")
            return "User details not found", 404
    else:
        # Redirect to login page if user is not logged in
        print("Not logged in")
        return redirect(url_for('app_views.login'))


@app_views.route('/tasks/<m_id>', methods=['GET'], strict_slashes=False)
def retrieve_tasks(m_id):
    """ Retrieves all active tasks for a given mission ID """
    if 'user' not in session:
        return "Not Authorized", 403

    if not m_id:
        return "Mission ID not provided", 400

    return jsonify(storage.get_tasks(m_id))


@app_views.route('/tasks/<t_id>/<action>', methods=['PUT'], strict_slashes=False)
def update_task(t_id, action):
    """ Updates the status of a task (done/undone) """
    if 'user' not in session:
        return "Not Authorized", 403

    if action not in ('done', 'undone'):
        return "Invalid action", 400

    user_id = session['user']
    user = storage.get('User', user_id)
    task = storage.get('Task', t_id)

    if not (user and task):
        return "User or Task not found", 404

    completed = (action == 'done')
    storage.update("Task", t_id, completed)
    storage.update("Mission", task.mission_id, new_value=completed, att=2)

    return f"Task {action.capitalize()} Successfully"

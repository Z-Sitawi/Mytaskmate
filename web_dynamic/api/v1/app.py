import secrets

from flask import Flask, make_response, render_template, session, url_for, redirect
from models import storage
from web_dynamic.api.v1.views import app_views
app = Flask(__name__, template_folder='/root/Mytaskmate/web_dynamic/templates/',
            static_folder='/root/Mytaskmate/web_dynamic/static')

app.register_blueprint(app_views)
app.secret_key = secrets.token_hex(16)


@app.teardown_appcontext
def close_db(error):
    """ Close Storage """
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """ 404 Error
    ---
    responses:
      404:
        description: a resource was not found
    """
    return make_response('<h1 style="text-align: center">Page Not Found</h1>', 404)


@app.route('/', methods=['GET'])
def main():
    if 'user' in session:
        return redirect(url_for('home'))
    else:
        return render_template('main.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user' in session:
        user_id = session['user']
        # Retrieve user details based on the user ID
        user = storage.get('User', user_id)
        if user:
            # Pass user's ID and username to the home page template
            storage.deactivate_mission(user_id)
            dashboard_info = storage.get_dashboard_info(user_id)
            return render_template('dashboard.html', info=dashboard_info)
        else:
            # Handle case where user details cannot be retrieved
            return "User details not found", 404
    else:
        # Redirect to login page if user is not logged in
        return redirect(url_for('app_views.login'))


@app.route('/home', methods=['GET'])
def home():
    # Check if user ID is stored in the session
    if 'user' in session:
        user_id = session['user']
        # Retrieve user details based on the user ID
        user = storage.get('User', user_id)
        if user:
            # Pass user's ID and username to the home page template
            storage.deactivate_mission(user_id)
            tasks = storage.get_active_tasks(user_id)
            return render_template('home.html', user_id=user.id, tasks=tasks)
        else:
            # Handle case where user details cannot be retrieved
            return "User details not found", 404
    else:
        # Redirect to login page if user is not logged in
        return redirect(url_for('app_views.login'))


@app.route('/history', methods=['GET'])
def history():
    if 'user' in session:
        user_id = session['user']
        # Retrieve user details based on the user ID
        user = storage.get('User', user_id)
        if user:
            # Pass user's ID and username to the home page template
            storage.deactivate_mission(user_id)
            return render_template('history.html', missions=storage.get_inactive_missions(user_id))
        else:
            # Handle case where user details cannot be retrieved
            return "User details not found", 404
    else:
        # Redirect to login page if user is not logged in
        return redirect(url_for('app_views.login'))


@app.route('/settings', methods=['GET'])
def settings():
    if 'user' in session:
        user_id = session['user']
        # Retrieve user details based on the user ID
        user = storage.get('User', user_id)
        if user:
            # Pass user's ID and username to the home page template
            storage.deactivate_mission(user_id)
            return render_template('settings.html')
        else:
            # Handle case where user details cannot be retrieved
            return "User details not found", 404
    else:
        # Redirect to login page if user is not logged in
        return redirect(url_for('app_views.login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)


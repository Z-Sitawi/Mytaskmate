from flask import jsonify, request, render_template, redirect, url_for, session
from models import storage
from web_dynamic.api.v1.views import app_views


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
@app_views.route('/users', methods=['GET'], strict_slashes=False)
def get_users(user_id=None):
    """ Retrieves the list of all User objects if User id is none
        or a single Task based on the id
    """
    if user_id:
        return jsonify(storage.get('User', user_id).to_dict())

    users_list = []
    for user in storage.all("User").values():
        users_list.append(user.to_dict())
    return jsonify(users_list)


@app_views.route('/users/<user_id>', methods=['DELETE'], strict_slashes=False)
def del_user(user_id):
    """ Deletes a User and all its missions based on its id """
    storage.delete('User', user_id)

    return jsonify({})


@app_views.route('/signup', methods=['POST'], strict_slashes=False)
def sign_up():
    """ Creates a User object """
    from models.user import User
    username = request.form.get('username')
    email = request.form.get('email')
    pwd = request.form.get('pwd')
    pwd2 = request.form.get('pwd2')
    errors = []

    message = "Your account has been created successfully"

    if pwd != pwd2:
        errors.append("Passwords do not match")
    elif username in pwd:
        errors.append("Passwords can't contain your username")
    elif email in pwd:
        errors.append("Passwords can't contain your email")
    else:
        u_obj = User(username=username, email=email, password=pwd)
        storage.new(u_obj)
        err = storage.save()
        if err is not None:
            errors.append(f"{err.capitalize()} Already Exists.")

    if errors:
        return render_template(template_name_or_list='main.html', errors=errors, up=True), 400
    else:
        return render_template(template_name_or_list='main.html', message=message, up=True), 201


@app_views.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    """Logs in to a User account if it exists"""
    if request.method == 'POST':
        account_holder = request.form['loginUser']
        pwd = request.form['loginPwd']
        user = storage.get_user(account_holder)
        error = ""
        if user is None:
            error = 'Account Does Not Exist'
        else:
            if pwd != user.password:
                error = 'Invalid Password'
            else:  # log in succeed
                session['user'] = user.id
                return redirect(url_for('home'))
        return render_template('main.html', loginError=error, In=True)
    else:
        return render_template('main.html', In=True)


@app_views.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)  # Clear user ID from the session
    return redirect('/')

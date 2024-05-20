from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from models.base import Base
from models.user import User
from models.mission import Mission
from models.task import Task
from os import getenv

# Dictionary mapping class names to corresponding model classes
classes = {'User': User, 'Mission': Mission, 'Task': Task}


def current_date():
    from datetime import datetime
    now = datetime.now()
    return {"day": now.day, "month": now.month, "year": now.year}


def check_24h_passed(mission_date_time):
    """ Checks creation date and time of mission entered.
    If it passed 24h returns True, otherwise False.
    """
    from datetime import datetime, timedelta

    # Calculate the current date and time
    current_date_time = datetime.now()

    # Calculate the difference between the current date and time and the given date and time
    time_difference = current_date_time - mission_date_time

    # Check if 24 hours have passed
    if time_difference >= timedelta(hours=24):
        return True
    else:
        return False


class DBStorage:
    """
    Represents a database storage engine.
    """

    def __init__(self):
        """ Initializes a new DB storage """
        user = getenv('MTM_USER')
        passwd = getenv('MTM_PWD')
        host = getenv('MTM_HOST')
        db = getenv('MTM_DB')
        connection_url = f"mysql+mysqldb://{user}:{passwd}@{host}/{db}"

        # Create the SQLAlchemy engine
        self.__engine = create_engine(connection_url, pool_pre_ping=True, pool_size=20, pool_timeout=60)
        session_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(session_factory)()
        Base.metadata.create_all(self.__engine)

    def new(self, obj):
        """Add obj to the current database session."""
        self.__session.add(obj)

    def save(self):
        """Commit all changes to the current database session."""
        try:
            self.__session.commit()
        except IntegrityError as e:
            # Handle integrity constraint violations
            err = str(e.__dict__['orig']).split(maxsplit=6)[6].removesuffix("'\")").removeprefix("'users.")
            return err

    def delete(self, cls=None, obj_id=""):
        """Delete obj from the current database session."""
        if cls is None:
            return None

        obj_to_del = self.__session.query(classes[cls]).filter_by(id=obj_id).first()
        if obj_to_del:
            # Delete the row
            m_id = completed = None
            if cls == 'Task':
                m_id = obj_to_del.mission_id
                completed = obj_to_del.completed
            self.__session.delete(obj_to_del)

            # Commit the changes to the database
            self.save()
            print(f"The {cls} with ID: {obj_id} was deleted successfully.")
            return {"mission_id": m_id, "completed": completed}
        else:
            print("** No instance found **")
            return None

    def reload(self):
        print("in reload")
        """Create all tables in the database and initialize a new session."""
        session_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Base.metadata.create_all(self.__engine)
        return scoped_session(session_factory)()

    def all(self, cls_name=None):
        """Query objects from the current database session."""
        new_dict = {}
        for cls in classes:
            if cls_name is None or cls_name == cls:
                objs = self.__session.query(classes[cls]).all()
                for obj in objs:
                    key = f"{obj.__class__.__name__}.{obj.id}"
                    new_dict[key] = obj
        return new_dict

    def close(self):
        """ Close the session """
        if self.__session is not None:
            self.__session.close()

    def update(self, cls=None, obj_id="", new_value=True, att=0):
        """Updates a column of an obj from the current database session."""
        import datetime
        obj_to_up = self.__session.query(classes[cls]).filter_by(id=obj_id).first()

        if not obj_to_up:
            print("** No instance found **")
            return None

        if cls == "Task":
            if obj_to_up.completed == new_value:
                print("** This action is already set **")
                return None
            obj_to_up.completed = new_value
            print(f"The {cls} with ID: {obj_id} was updated successfully.")
        elif cls == "Mission":
            if att == 1 and new_value:
                obj_to_up.total_tasks += 1
            elif att == 1 and not new_value:
                obj_to_up.total_tasks -= 1
            elif att == 2 and new_value:
                obj_to_up.completed_tasks += 1
            elif att == 2 and not new_value:
                obj_to_up.completed_tasks -= 1

        obj_to_up.updated_at = datetime.datetime.utcnow()
        # Commit the changes to the database
        self.save()
        return True

    def get(self, cls, obj_id):
        """Returns the object based on the class and its ID, or None if not found"""
        if cls not in classes:
            return None
        obj = self.__session.query(classes[cls]).filter_by(id=obj_id).first()
        return obj

    def count(self, cls=None):
        """Count the number of objects in storage"""
        if cls is None:
            # Count all objects
            return sum(self.__session.query(cls).count() for cls in classes.values())
        else:
            # Count objects of a specific class
            return self.__session.query(classes[cls]).count()

    def get_user(self, login):
        """ Takes a username or email and returns a user object
            if no user found returns None.
        """
        if '@' in login:
            obj = self.__session.query(User).filter_by(email=login).first()
            return obj
        obj = self.__session.query(User).filter_by(username=login).first()
        return obj

    def delete_active_mission(self, user_id):
        """ Delete the active mission """
        try:
            mission = self.__session.query(Mission).filter_by(active=True, user_id=user_id).first()
            if mission:
                self.__session.delete(mission)
                self.__session.commit()
                print("The active mission has been deleted successfully.")
            else:
                print("No active mission found.")
        except Exception as e:
            print("Error occurred:", str(e))
            self.__session.rollback()

    def get_active_mission(self, user_id):
        """ Takes a user id and looks for an Active mission """
        with self.__session:
            mission = self.__session.query(Mission).filter_by(active=True, user_id=user_id).first()
        if mission:
            return mission
        else:
            return None

    def get_tasks(self, m_id):
        """ Takes a Mission id and looks for all its tasks """
        with self.__session as session:
            tasks = session.query(Task).filter_by(mission_id=m_id).all()
        if tasks:
            unsorted_missions = [task.to_dict() for task in tasks]
            sorted_missions = sorted(unsorted_missions, key=lambda x: x['created_at'])
            return sorted_missions
        else:
            return []

    def get_active_tasks(self, u_id):
        """ Retrieves active tasks based on user id """
        active_mission = self.get_active_mission(user_id=u_id)
        if active_mission:
            return self.get_tasks(active_mission.id)
        else:
            return []

    def deactivate_mission(self, user_id):
        """ Deactivates a Mission based on its mission id """
        with self.__session as session:
            active_mission = session.query(Mission).filter_by(user_id=user_id, active=True).first()
            if active_mission:
                if check_24h_passed(active_mission.created_at):
                    active_mission.active = False
                    session.commit()
                    print("Mission Deactivated Successfully")
                    return
            else:
                pass

    def get_inactive_missions(self, u_id):
        """ Takes a User id and returns all its inactive missions """
        with self.__session as session:
            missions = session.query(Mission).filter_by(user_id=u_id, active=False).all()
        if missions:
            unsorted_missions = [m.to_dict() for m in missions]
            sorted_missions = sorted(unsorted_missions, key=lambda x: x['created_at'], reverse=True)
            return sorted_missions
        else:
            return []

    def get_dashboard_info(self, u_id):
        """Retrieves dashboard information for a user."""
        info = {
            "today": {"total_tasks": 0, "completed": 0, "uncompleted": 0},
            "month": {"missions": 0, "total_tasks": 0, "completed": 0, "uncompleted": 0},
            "all": {"missions": 0, "total_tasks": 0, "completed": 0, "uncompleted": 0}
        }

        with self.__session as session:
            missions = session.query(Mission).filter_by(user_id=u_id).all()

        if missions:
            now = current_date()
            info["all"]['missions'] = len(missions)

            for m in missions:
                # Updating today's tasks
                if m.active:
                    info['today']['total_tasks'] += m.total_tasks
                    info['today']['completed'] += m.completed_tasks
                    info['today']['uncompleted'] = info['today']['total_tasks'] - info['today']['completed']

                # Updating this month's tasks
                if m.created_at.month == now['month'] and m.created_at.year == now['year']:
                    info['month']['missions'] += 1
                    info['month']['total_tasks'] += m.total_tasks
                    info['month']['completed'] += m.completed_tasks
                    info['month']['uncompleted'] = info['month']['total_tasks'] - info['month']['completed']

                # Updating all-time tasks
                info['all']['total_tasks'] += m.total_tasks
                info['all']['completed'] += m.completed_tasks
                info['all']['uncompleted'] = info['all']['total_tasks'] - info['all']['completed']

        return info


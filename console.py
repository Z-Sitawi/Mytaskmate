import cmd
from models import storage
from models.engine.db_storage import classes

storage.reload()


def good_print(a_dict, cls=None):
    if a_dict == {}:
        cls = "" if cls is None else cls
        print(f"** No {cls} Objects Yet **")
    counter = 0
    for k, v in a_dict.items():
        counter += 1
        print(f"Object {counter} => {k}: {v.to_dict()}")
        print("")


def check(arg_list):
    arg_list = arg_list.split(" ", maxsplit=1)
    if arg_list[0] == "":
        print("** Class Name Missing **")
        return None
    elif len(arg_list) >= 1:
        if arg_list[0] not in classes:
            print("** Class Does Not Exist **")
            return None
        else:
            return arg_list[0]


def get_object_info(cls):
    if cls is None:
        return None
    info = {}
    if cls == 'User':
        info = {'username': "", "email": "", "password": ""}
        for k, v in info.items():
            info[k] = input(f'{k.capitalize()}: ').lower()
    elif cls == 'Mission':
        user_id = input('User ID: ')
        for k in storage.all('User').keys():
            if 'User.'+user_id == k:
                info = {'user_id': user_id}
                break
        else:
            print("** No Instance Found **")
            return None
    elif cls == 'Task':
        m_id = input('Mission ID: ')
        for k in storage.all('Mission').keys():
            if 'Mission.' + m_id == k:
                info = {'title': input("Title: "), "mission_id": m_id}
                break
        else:
            print("** No Instance Found **")
            return None
    return info


class MyTaskMate(cmd.Cmd):

    prompt = "====> "

    def do_clear(self, arg):
        """Clears the command prompt"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_x(self, args):
        """Exits the command line"""
        return True

    def precmd(self, line):
        return line

    def do_create(self, arg):
        """Creates an instance of a class, saves it, and prints its id"""
        cls = check(arg)
        info = get_object_info(cls)
        if info is not None:
            obj = classes[cls](**info)
            if cls == 'Task':
                storage.update("Mission", obj.mission_id, new_value=True, att=1)
            storage.new(obj)
            err = storage.save()
            if err:
                print(f"** {err.capitalize()} Already Exists Chose A Different One.")
                storage.close()
                return
            print(obj.id)

    def do_see(self, arg):
        """
        * Prints all existing objects if no argument passed.
        * Prints all existing objects of one type if a valid cls name is given.
        * Prints a single object if a valid cls name & id were given.
        Usage: see / see <cls_name> / see <cls_name> <id>
        """
        args = arg.split(maxsplit=3)
        if len(args) == 0:
            good_print(storage.all())
        elif len(args) >= 1:
            if args[0] not in classes:
                print("** Class Does Not Exist **")
            else:
                if len(args) > 1:
                    try:
                        key = f'{args[0]}.{args[1]}'
                        print(storage.all(args[0])[key])
                    except KeyError:
                        print("** No Instance Found **")
                else:
                    good_print(storage.all(args[0]), args[0])

    def do_delete(self, arg):
        """Deletes an instance of a class based on its id
            Usage : delete <class name>
        """
        cls = check(arg)
        if cls is not None:
            obj_id = input(f'{cls} ID: ')
            t_info = storage.delete(cls, obj_id)
            if cls == 'Task' and t_info["mission_id"]:
                storage.update("Mission", t_info["mission_id"], new_value=False, att=1)
                if t_info['completed']:
                    storage.update("Mission", t_info["mission_id"], new_value=False, att=2)

    def do_list(self, args):
        """Lists all tasks of a mission based on its id."""
        m_id = input("Mission Id: ")
        all_missions = storage.all("Mission")
        tasks = []
        if "Mission."+m_id in all_missions.keys():
            all_tasks = storage.all("Task")
            for val in all_tasks.values():
                if val.mission_id == m_id:
                    if val.completed:
                        tasks.append((val.title, "Completed"))
                    else:
                        tasks.append((val.title, "Uncompleted"))
        else:
            print("** Mission Does Not Exist **")
            return

        if len(tasks) == 0:
            print("** No Tasks Yet **")
        else:
            count = 0
            for task in tasks:
                count += 1
                output = f"Task {count}: {task[0]}"
                while len(output) < 130:
                    output += "_"
                print(f"Task {count}: {output}[{task[1]}]")

    def do_done(self, arg):
        """ Marks a task as completed.
         Usage: done <task_id>"""
        args = arg.split(maxsplit=1)
        if len(args) == 0:
            print('** Task Id missing Usage: done <task id> **')
        else:
            status = storage.update("Task", args[0])
            if status is not None:
                task = storage.all('Task')["Task." + args[0]]
                if task is not None:
                    storage.update("Mission", task.mission_id, new_value=True, att=2)

    def do_undone(self, arg):
        """ Marks a task as uncompleted.
         Usage: done <task_id>"""
        args = arg.split(maxsplit=1)
        if len(args) == 0:
            print('** Task Id missing Usage: done <task id> **')
        else:
            status = storage.update("Task", args[0], False)
            if status is not None:
                task = storage.all('Task')["Task."+args[0]]
                if task is not None:
                    storage.update("Mission", task.mission_id, new_value=False, att=2)

    def do_count(self, arg=None):
        if not arg:
            print("Total Objects:", storage.count())
        else:
            if arg not in classes:
                print("** Class Does Not Exist **")
                return
            print(f"Total Objects of {arg}:", storage.count(arg))

    def do_mdown(self, arg):
        if not arg:
            print("Mission Id missing")
        else:
            storage.deactivate_mission(arg)

    def emptyline(self):
        """Shows the prompt again when Enter is pressed without typing anything."""
        pass


if __name__ == '__main__':
    MyTaskMate().cmdloop()

# -*- coding:utf-8 -*-
from flask_script import Manager, Shell
from app import create_app, db
from app.models import Role, User, Post
from flask_migrate import Migrate, MigrateCommand

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()


@manager.command
def deploy():
    from flask_migrate import upgrade
    from app.models import Role

    upgrade()

    Role.insert_roles()

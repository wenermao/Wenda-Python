#coding:utf-8
#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User,Role,Question,Follow
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
def make_shell_context():
    return dict(app=app, db=db,User=User,Role=Role,Question=Question)
manager.add_command("shell",Shell(make_context=make_shell_context))

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
#启动服务器
if __name__ == '__main__':
    app.run(debug=True)
    # manager.run()
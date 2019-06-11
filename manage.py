# -*- coding: utf-8 -*-
# @Author: wangchao
# @Time: 19-6-4 下午5:01
import os
from app import create_app, db
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app('default')

# 管理配置
manager = Manager(app)
# 数据库迁移配置
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

manager.add_command("shell", Shell(make_context=make_shell_context))
# 将db加入shell命令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

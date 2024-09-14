from flask_script import Manager

from myapp import app

manager = Manager(app)

def crazy_call():
    print("crazy_call")

@manager.command
def runserver():
    app.run()
    crazy_call()

if __name__ == "__main__":
    manager.run()

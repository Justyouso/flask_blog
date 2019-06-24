from app import create_app


# @app.route('/')
# def hello_world():
#     return 'Hello World!'
app = create_app("default")

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
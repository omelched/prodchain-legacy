from app import application


@application.route('/')
def root():
    return 'Hello, world', 200

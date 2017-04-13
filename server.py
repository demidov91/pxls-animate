from flask import Flask, request
app = Flask(__name__)


@app.route('im')
def get_image():
    pass


@app.route('gif')
def get_gif():
    pass

if __name__ == '__main__':
    app.run()

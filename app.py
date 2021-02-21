from flask import Flask, render_template
from config import socketIO
from backoffice.routes.backoffice import bp as backoffice_bp
from routes.trip import bp as trip_bp

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socketIO.init_app(app)

app.register_blueprint(backoffice_bp)
app.register_blueprint(trip_bp)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == '__main__':
    socketIO.run(app)

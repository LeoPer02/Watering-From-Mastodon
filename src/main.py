import datetime
import ipaddress

from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import aux
from flask_paranoid import Paranoid
from dotenv import load_dotenv
import os
import json
import mqtt as mqtt
from mastodon import Mastodon

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")



login_manager = LoginManager()
login_manager.init_app(app)

paranoid = Paranoid(app)
paranoid.redirect_view = '/'

db = SQLAlchemy()


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)


class Control_agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip = db.Column(db.String(32), nullable=False)
    port = db.Column(db.Integer, nullable=False)


class Commands(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issuer = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ca = db.Column(db.Integer, db.ForeignKey('control_agent.id'), nullable=False)
    command = db.Column(db.String(32), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Pools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ca = db.Column(db.Integer, db.ForeignKey('control_agent.id'), nullable=False)
    light_value = db.Column(db.Integer, nullable=False)


db.init_app(app)

with app.app_context():
    db.create_all()


mqtt_client = mqtt.connect_mqtt()
mqtt_client.loop_start()

def mastodon_message(message):
    mastodon_instance_url = 'https://mastodon.social'

    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')

    # Authenticate with the Mastodon API
    mastodon = Mastodon(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        api_base_url=mastodon_instance_url
    )

    # Post a message
    def post_to_mastodon(message):
        try:
            mastodon.status_post(message)
            print("Message posted successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

    post_to_mastodon(message)
    #post_to_mastodon("Plant 1 status:\n Water:XXX \n Light:XXX")

def subscribe(client, topic):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        with app.app_context():
            res = json.loads(msg.payload.decode())
            pool = Pools(ca=res["id"], light_value=res["light_value"])
            db.session.add(pool)
            db.session.commit()
        mastodon_message(msg.payload.decode())


    client.subscribe(topic)
    client.on_message = on_message
subscribe(mqtt_client, "arduino/pool")

@login_manager.user_loader
def loader_user(user_id):
    return db.session.get(Users, user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_check = aux.check_user(username)
        if user_check is not None:
            return user_check, 201

        pass_check = aux.check_pass(password)
        if pass_check is not None:
            return pass_check, 201

        # Check if Username is being used
        user = Users.query.filter_by(
            username=username).first()
        if user is not None:
            res = {
                "error": "Username already in use"
            }
            return res, 201

        password = generate_password_hash(password)
        user = Users(username=username,
                     password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        session['username'] = username
        session['user_id'] = user.id
        return redirect(url_for("home"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_check = aux.check_user(username)
        if user_check is not None:
            return user_check, 201

        pass_check = aux.check_pass(password)
        if pass_check is not None:
            return pass_check, 201

        user = Users.query.filter_by(
            username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['username'] = username
            session['user_id'] = user.id
            return redirect(url_for("home"))
        else:
            res = {
                "error": "Login failed, please check the username and password"
            }
            return res, 201
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/control_agents", methods=['GET'])
@login_required
def list_control_agents():
    user_id = session["user_id"]
    ControlAgents = Control_agent.query.filter_by(
        owner=user_id
    ).all()
    control_agent_list: list = []
    for i in ControlAgents:
        temp = {
            "id": i.id,
            "ip": i.ip,
            "port": i.port
        }
        control_agent_list.append(temp)
    return jsonify(control_agent_list), 200


@app.route("/add_ca", methods=['GET', 'POST'])
@login_required
def add_control_agent():
    username = session["username"]
    user_id = session["user_id"]
    if request.method == "POST":
        ca_ip = request.form["control_agent_ip"]
        ca_port = request.form["control_agent_port"]
        try:
            # If this failed it will throw an error meaning the ip is invalid
            ipaddress.ip_address(ca_ip)
            if (not ca_port.isdigit()) or int(ca_port) <= 0 or 65535 < int(ca_port):
                res = {
                    "error": "Invalid Port"
                }
                return res, 400

            user_lookup = Users.query.filter_by(id=user_id, username=username).first()
            if not user_lookup:
                res = {
                    "error": "User provided is different from user detected"
                }
                return res, 401
            check_ca_existince = Control_agent.query.filter_by(ip=ca_ip, port=ca_port).first()
            if check_ca_existince:
                res = {
                    "error": "The Ip port combination provided is already in use"
                }
                return res, 400
            control_agent = Control_agent(ip=ca_ip, port=ca_port, owner=user_id)
            db.session.add(control_agent)
            db.session.commit()
            return jsonify(""), 200
        except ValueError:
            # Not legal
            res = {
                "error": "Invalid IP address"
            }
            return res, 400
    else:
        return render_template("add_ca.html", username=username)


@app.route("/remove_ca", methods=['GET', 'POST'])
@login_required
def remove_control_agent():
    username = session["username"]
    user_id = session["user_id"]
    if request.method == 'POST':
        ca_ip = request.form["control_agent_ip"]
        ca_port = request.form["control_agent_port"]
        try:
            # If this failed it will throw an error meaning the ip is invalid
            ipaddress.ip_address(ca_ip)
            if (not ca_port.isdigit()) or int(ca_port) <= 0 or 65535 < int(ca_port):
                res = {
                    "error": "Invalid Port"
                }
                return res, 400

            user_lookup = Users.query.filter_by(id=user_id, username=username).first()
            if not user_lookup:
                res = {
                    "error": "User provided is different from user detected"
                }
                return res, 401
            check_ca_existince = Control_agent.query.filter_by(ip=ca_ip, port=ca_port, owner=user_id).first()
            if not check_ca_existince:
                res = {
                    "error": F"No control agent found with {ca_ip}:{ca_port} for user {username}"
                }
                return res, 400
            Control_agent.query.filter_by(ip=ca_ip, port=ca_port, owner=user_id).delete()
            db.session.commit()
            return jsonify(""), 200
        except ValueError:
            # Not legal
            res = {
                "error": "Invalid IP address"
            }
            return res, 400
    else:
        controlagents = Control_agent.query.filter_by(owner=user_id).all()
        return render_template("remove_ca.html", username=username, ControlAgents=controlagents)


ALLOWED_COMMANDS = ['water', 'heat', 'light']


def insert_command(command, ca_id):
    db.session.add(command)
    row_count = Commands.query.filter_by(ca=ca_id).count()
    # Allow only a maximum of 20 commands per Control Agent to be stored in the database
    if row_count > 20:
        first_person = Commands.query.order_by(Commands.created_date.asc()).first()
        db.session.delete(first_person)
    db.session.commit()


@app.route("/action/<int:ca_id>/<string:command>", methods=['GET'])
@login_required
def perform_command_user(ca_id, command):
    user_id = session["user_id"]
    ca = Control_agent.query.filter_by(owner=user_id, id=ca_id).first()
    if not ca:
        res = {
            "error": "Command issuer does not own the Control Agent"
        }
        return res, 401
    if command not in ALLOWED_COMMANDS:
        res = {
            "error": "Command provided is not within the commands allowed",
            "commands_allowed": ALLOWED_COMMANDS
        }
        return res, 201
    command_event = Commands(issuer=ca_id, ca=ca.id, command=command)
    insert_command(command_event, ca_id)
    commands = Commands.query.filter_by(ca=ca_id).order_by(Commands.id).all()
    commands.reverse()
    event = {
        "id": str(ca_id),
        "command": str(command)
    }
    event_data = json.dumps(event)
    mqtt.publish(mqtt_client, event_data, "arduino/action") # Test of the mqtt
    return jsonify(""), 200


@app.route("/commands/<int:ca_id>", methods=['GET'])
@login_required
def list_commands(ca_id):
    user_id = session["user_id"]
    ca = Control_agent.query.filter_by(owner=user_id, id=ca_id).first()
    if not ca:
        res = {
            "error": "Issuer does not own the Control Agent"
        }
        return res, 401
    commands = Commands.query.filter_by(issuer=user_id, ca=ca_id).all()
    new_commands: list = []
    for i in commands:
        temp = {
                "id": i.id,
                "issuer": i.issuer,
                "ca": i.ca,
                "command": i.command,
                "created_date": str(i.created_date)
        }
        new_commands.append(temp)
    return jsonify(new_commands), 200

@app.route("/test/pool")
@login_required
def test_pool():
    pools = Pools.query.all()
    new_pools: list = []
    for i in pools:
        temp = {
            "id": i.id,
            "ca": i.ca,
            "light_value": i.light_value
        }
        new_pools.append(temp)
    return jsonify(new_pools), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

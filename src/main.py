import datetime
import ipaddress
import logging
import random

from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import aux
from flask_paranoid import Paranoid
from dotenv import load_dotenv
import os
import json
from mastodon import Mastodon
import paho.mqtt.client as mqtt
# Load environment variables from .env file
load_dotenv()

# MQTT broker details
BROKER = 'mosquitto'  # Replace with your MQTT broker address
PORT = 1883                          # Replace with your MQTT broker port (default is 1883)
TOPIC = 'pool'

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
    light_value = db.Column(db.Integer, nullable=True)
    humidity_value = db.Column(db.Integer, nullable=True)
    temperature_value = db.Column(db.Integer, nullable=True)
    moisture_value = db.Column(db.Integer, nullable=True)



db.init_app(app)

with app.app_context():
    db.create_all()


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

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_message(client, userdata, msg):
    print(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")
    logging.log(logging.ERROR, f"Mensagem aqui {msg.topic}")
    try:
        mastodon_message(msg.payload.decode())
        with app.app_context():
            res = json.loads(msg.payload.decode())
            light_value = None
            humidity_value = None
            temperature_value = None
            moisture_value = None
            if 'light_value' in res:
                light_value = res["light_value"]
            if 'humidity_value' in res:
                humidity_value  = res["humidity_value"]
            if 'temperature_value' in res:
                temperature_value = res["temperature_value"]
            if 'moisture_value' in res:
                moisture_value = res["moisture_value"]
            pool = Pools(ca=res["id"], light_value=light_value, humidity_value=humidity_value, temperature_value=temperature_value, moisture_value=moisture_value)
            db.session.add(pool)
            db.session.commit()
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe(TOPIC)
    else:
        print("Connection failed with code", rc)



def subscribe(client):

    # Assign the callback functions
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Connect to the broker
    client.connect(BROKER, PORT, 60)

    # Blocking loop to process network traffic, dispatch callbacks, and handle reconnecting.
    client.loop_start()


mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
subscribe(mqtt_client)

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
        logging.log(logging.ERROR, f"For CA {i.id} Issuer: {user_id}")
        commands = Commands.query.filter_by(issuer=user_id, ca=i.id).all()
        logging.log(logging.ERROR, f"Size of commands: {len(commands)}")
        new_commands: list = []
        for j in commands:
            temp_commands = {
                "id": j.id,
                "issuer": j.issuer,
                "ca": j.ca,
                "command": j.command,
                "created_date": str(j.created_date)
            }
            new_commands.append(temp_commands)
        logging.log(logging.ERROR, f"Commands: {new_commands}")
        temp = {
            "id": i.id,
            "ip": i.ip,
            "port": i.port,
            "commands": new_commands
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
    logging.log(logging.ERROR, f"Adding: {command} for {ca_id}")
    db.session.add(command)
    row_count = Commands.query.filter_by(ca=ca_id).count()
    # Allow only a maximum of 20 commands per Control Agent to be stored in the database
    if row_count > 20:
        first_command = Commands.query.order_by(Commands.created_date.asc()).first()
        db.session.delete(first_command)
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
    command_event = Commands(issuer=user_id, ca=ca_id, command=command)
    insert_command(command_event, ca_id)
    commands = Commands.query.filter_by(ca=ca_id).order_by(Commands.id).all()
    commands.reverse()
    event = {
        "id": str(ca_id),
        "command": str(command)
    }
    event_data = json.dumps(event)
    mqtt_client.publish("action", event_data) # Test of the mqtt
    return jsonify(""), 200

@app.route("/pool", methods=["GET"])
@login_required
def test_pool():
    user_id = session["user_id"]
    if not user_id:
        return "Bad request", 401
    control_agents = Control_agent.query.filter_by(owner=user_id).all()
    control_agent_list = []
    for i in control_agents:
        pools = Pools.query.filter_by(ca=i.id).all()
        new_pools = []
        for j in pools:
            temp = {
                "id": j.id,
                "ca": j.ca,
                "light_value": j.light_value,
                "humidity_value": j.humidity_value,
                "temperature_value": j.temperature_value,
                "moisture_value": j.moisture_value
            }
            dup = {
                "id": j.id - 1,
                "ca": j.ca,
                "light_value": j.light_value,
                "humidity_value": j.humidity_value,
                "temperature_value": j.temperature_value,
                "moisture_value": j.moisture_value
            }
            if dup not in new_pools:
                new_pools.append(temp)
        temp = {
            "id": i.id,
            "ip": i.ip,
            "port": i.port,
            "pool": new_pools
        }
        control_agent_list.append(temp)
    return jsonify(control_agent_list), 200


###################################### Test Section #############################################

@app.route("/test/commands")
def test_commands():
    commands = Commands.query.all()
    new_commands: list = []
    for j in commands:
        temp_commands = {
            "id": j.id,
            "issuer": j.issuer,
            "ca": j.ca,
            "command": j.command,
            "created_date": str(j.created_date)
        }
        new_commands.append(temp_commands)
    return jsonify(new_commands), 200



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

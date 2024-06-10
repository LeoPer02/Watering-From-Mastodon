import datetime
import ipaddress
import logging
import random

from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from auxi import process_values, check_user, check_pass, too_much_light, too_much_humidity, too_much_water, too_much_heat, too_little_humidity, funny_plant_names
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
TOPIC1 = 'pool'
TOPIC2 = 'actions'

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
    name = db.Column(db.String(32), nullable=False)
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
    humidity_value = db.Column(db.Integer, nullable=False)
    temperature_value = db.Column(db.Integer, nullable=False)
    moisture_value = db.Column(db.Integer, nullable=False)

class Threshold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ca = db.Column(db.Integer, db.ForeignKey('control_agent.id'), nullable=False)
    light_value_high = db.Column(db.Integer, nullable=False)
    light_value_low = db.Column(db.Integer, nullable=False)
    humidity_value_high = db.Column(db.Integer, nullable=False)
    humidity_value_low = db.Column(db.Integer, nullable=False)
    temperature_value_low = db.Column(db.Integer, nullable=False)
    temperature_value_high = db.Column(db.Integer, nullable=False)
    moisture_value_high = db.Column(db.Integer, nullable=False)
    moisture_value_low = db.Column(db.Integer, nullable=False)



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
    logging.log(logging.ERROR, f"Message received on topic: {msg.topic}")
    if msg.topic == "pool":
        try:
            with app.app_context():
                logging.log(logging.ERROR, f"Message: {msg.payload} on topic: {msg.topic}")
                if msg.payload == "":
                    return
                id, light_value, moisture_value, temperature_value, humidity_value = process_values(msg.payload.decode())
                if not id:
                    return
                if not light_value:
                    light_value = db.session.query(func.avg(Pools.light_value)).scalar()
                if not moisture_value:
                    moisture_value = db.session.query(func.avg(Pools.moisture_value)).scalar()
                if not temperature_value:
                    temperature_value = db.session.query(func.avg(Pools.temperature_value)).scalar()
                if not humidity_value:
                    humidity_value = db.session.query(func.avg(Pools.humidity_value)).scalar()
                pool = Pools(ca=id, light_value=light_value, humidity_value=humidity_value, temperature_value=temperature_value, moisture_value=moisture_value)
                db.session.add(pool)
                db.session.commit()

                # =============== CHECK THRESHOLDS ===============
                Ca_object = Control_agent.query.filter_by(id=id).first()
                if Ca_object is None:
                    return
                name = Ca_object.name
                threshold = Threshold.query.filter_by(ca=id).first()
                if light_value > threshold.light_value_high:
                    random_index = random.randrange(len(too_much_light))
                    mastodon_message(f"{name}: {too_much_light[random_index]}")
                if temperature_value > threshold.temperature_value_high:
                    random_index = random.randrange(len(too_much_heat))
                    mastodon_message(f"{name}: {too_much_heat[random_index]}")
                if moisture_value > threshold.moisture_value_high:
                    random_index = random.randrange(len(too_much_water))
                    mastodon_message(f"{name}: {too_much_water[random_index]}")
                if humidity_value > threshold.humidity_value_high:
                    random_index = random.randrange(len(too_much_humidity))
                    mastodon_message(f"{name}: {too_much_humidity[random_index]}")
                if humidity_value < threshold.humidity_value_low:
                    random_index = random.randrange(len(too_little_humidity))
                    mastodon_message(f"{name}: {too_little_humidity[random_index]}")

        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
    if msg.topic == "actions":
        logging.log(logging.ERROR, f"Just received an action from the arduino: {msg.payload}")
        content = msg.payload.decode()
        logging.log(logging.ERROR, f"Content: {content}")
        parts = content.strip().split()

        # Check if there are exactly two parts
        if len(parts) != 2:
            return

        # Extract id and command
        id_str, command = parts

        # Validate id as integer
        try:
            id = int(id_str)
        except ValueError:
            return

        # Validate command
        if command not in ['water', 'heat', 'light']:
            return None, None
        with app.app_context():
            if Control_agent.query.filter_by(id=id).first() is None:
                return

            new_command = Commands(issuer=-1, ca=id, command=command)
            insert_command(new_command, id)


    else:
        pass
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe(TOPIC1)
        client.subscribe(TOPIC2)
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

        user_check = check_user(username)
        if user_check is not None:
            return user_check, 201

        pass_check = check_pass(password)
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
        user_check = check_user(username)
        if user_check is not None:
            return user_check, 201

        pass_check = check_pass(password)
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
        commands_automatic = Commands.query.filter_by(issuer=-1, ca=i.id).all()
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
        for j in commands_automatic:
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
        if "control_agent_ip" not in request.form or "control_agent_port" not in request.form:
            error = {
                "error": "Invalid Parameters. Make sure you're sending a valid IP and Port"
            }
            return jsonify(error), 400
        ca_ip = request.form["control_agent_ip"]
        ca_port = request.form["control_agent_port"]
        name = None
        if "control_agent_name" not in request.form:
            index = random.randrange(len(funny_plant_names))
            name = funny_plant_names[index]
            funny_plant_names.pop(index)
        else:
            name = request.form["control_agent_name"]
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
            control_agent = Control_agent(ip=ca_ip, port=ca_port, owner=user_id, name=name)
            db.session.add(control_agent)
            db.session.commit()
            insert_threshold(None, None, None, None, None, None, None, None, control_agent.id)
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
    event = f"{ca_id} {command}"
    mqtt_client.publish("commands", event) # Test of the mqtt
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

def insert_threshold(light_value_low, light_value_high, moisture_value_low, moisture_value_high, temperature_value_low,
                     temperature_value_high, humidity_value_low, humidity_value_high, ca_id):
    if not ca_id:
        return
    threshold = Threshold.query.filter_by(ca=ca_id).first()
    if threshold is None:
        logging.log(logging.ERROR, f"No threshold for ca {ca_id}")

        # ====================== DEFAULT VALUES FOR THRESHOLD =============================

        if not light_value_low:
            light_value_low = 100
        if not light_value_high:
            light_value_high = 200
        if not moisture_value_low:
            moisture_value_low = 0
        if not moisture_value_high:
            moisture_value_high = 100
        if not temperature_value_low:
            temperature_value_low = 0
        if not temperature_value_high:
            temperature_value_high = 40
        if not humidity_value_low:
            humidity_value_low = 0
        if not humidity_value_high:
            humidity_value_high = 25

        # ================== END OF DEFAULT VALUES FOR THRESHOLD ==========================
        threshold = Threshold(ca=ca_id, light_value_low=light_value_low, light_value_high=light_value_high, moisture_value_low=moisture_value_low,
        moisture_value_high=moisture_value_high, temperature_value_low=temperature_value_low, temperature_value_high=temperature_value_high,
                              humidity_value_low=humidity_value_low, humidity_value_high=humidity_value_high)
        db.session.add(threshold)
        db.session.commit()
        return
    if light_value_low:
        threshold.light_value_low = light_value_low
    if light_value_high:
        threshold.light_value_high = light_value_high
    if moisture_value_low:
        threshold.moisture_value_low = moisture_value_low
    if moisture_value_high:
        threshold.moisture_value_high = moisture_value_high
    if humidity_value_low:
        threshold.humidity_value_low = humidity_value_low
    if humidity_value_high:
        threshold.humidity_value_high = humidity_value_high
    if temperature_value_low:
        threshold.temperature_value_low = temperature_value_low
    if temperature_value_high:
        threshold.temperature_value_low = temperature_value_high
    db.session.commit()

@app.route("/set_thresholds", methods=['POST'])
@login_required
def set_threshold():
    username = session["username"]
    user_id = session["user_id"]
    if request.method == 'POST':
        try:
            ca = int(request.form["control_agent"]) if "control_agent" in request.form else None
            light_value_high = float(request.form["light_value_high"]) if "light_value_high" in request.form else None
            light_value_low = float(request.form["light_value_low"]) if "light_value_low" in request.form else None
            moisture_value_high = float(request.form["moisture_value_high"]) if "moisture_value_high" in request.form else None
            moisture_value_low = float(request.form["moisture_value_low"]) if "moisture_value_low" in request.form else None
            temperature_value_high = float(request.form["temperature_value_high"]) if "temperature_value_high" in request.form else None
            temperature_value_low = float(request.form["temperature_value_low"]) if "temperature_value_low" in request.form else None
            humidity_value_high = float(request.form["humidity_value_high"]) if "humidity_value_high" in request.form else None
            humidity_value_low = float(request.form["humidity_value_low"]) if "humidity_value_low" in request.form else None
        except (TypeError, ValueError):
            error = {
                "error": "You provided an invalid value for one of the thresholds"
            }
            return jsonify(error), 400
        logging.log(logging.ERROR, f"control_agent: {ca}, light_value: ({light_value_low} <-> {light_value_high}), moisture_value: ({moisture_value_low} <-> {moisture_value_high}), temperature_value: ({temperature_value_low} <-> {temperature_value_high}), humidity_value: ({humidity_value_low} <-> {humidity_value_high})")
        if not Control_agent.query.filter_by(id=ca, owner=user_id).first():
            return "", 403
        if not ca:
            return "", 401
        insert_threshold(light_value_low=light_value_low, light_value_high=light_value_high, moisture_value_low=moisture_value_low,
                         moisture_value_high=moisture_value_high, temperature_value_high=temperature_value_high,
                         temperature_value_low=temperature_value_low, humidity_value_low=humidity_value_low,
                         humidity_value_high=humidity_value_high, ca_id=ca)
        with app.app_context():
            t = Threshold.query.filter_by(ca=ca).first()
            event = f"{ca} {t.light_value_low} {t.light_value_high} {t.moisture_value_low} {t.moisture_value_high} {t.humidity_value_low} {t.humidity_value_high} {t.temperature_value_low} {t.temperature_value_high}"
            mqtt_client.publish("thresholds", event)
        return "", 200

@app.route("/thresholds/<int:id>", methods=["GET"])
@login_required
def thresholds(id):
    user_id = session["user_id"]
    if not user_id:
        return "Bad request", 401
    control_agents = Control_agent.query.filter_by(owner=user_id, id=id).all()
    control_agent_list = []
    for i in control_agents:
        threshold = Threshold.query.filter_by(ca=i.id).first()
        if not threshold:
            temp = {
                "id": i.id,
                "ip": i.ip,
                "port": i.port,
                "threshold": None
            }
        else:
            temp = {
                "id": i.id,
                "ip": i.ip,
                "port": i.port,
                "threshold": {
                    "light_value_low": threshold.light_value_low,
                    "light_value_high": threshold.light_value_high,
                    "humidity_value_low": threshold.humidity_value_low,
                    "humidity_value_high": threshold.humidity_value_high,
                    "temperature_value_low": threshold.temperature_value_low,
                    "temperature_value_high": threshold.temperature_value_high,
                    "moisture_value_low": threshold.moisture_value_low,
                    "moisture_value_high": threshold.moisture_value_high
                }
            }
        control_agent_list.append(temp)
    return jsonify(control_agent_list), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

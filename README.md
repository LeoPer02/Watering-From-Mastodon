# Watering from Mastodon

## Overview

**Watering from Mastodon** is an embedded systems project designed to monitor and manage the health of plants by tracking environmental parameters and acting upon predefined thresholds. The system utilizes Arduinos as control agents and a Raspberry Pi as a central broker, with a server implemented in Python using Flask to facilitate communication with an Android application.

## Components

### Arduino Control Agents

The Arduino units are equipped with various sensors to monitor:
- Light levels
- Air humidity
- Temperature
- Soil moisture

These sensors collect data and send it to the Raspberry Pi broker. When sensor readings exceed predefined thresholds, the Arduinos can autonomously activate actuators to adjust conditions (e.g., water the plants, increase light).

### Raspberry Pi Broker

The Raspberry Pi acts as the central hub, receiving data from the Arduino control agents via MQTT (using Mosquitto). It hosts a server, implemented in Python using Flask, to manage and relay information to an Android application. The broker coordinates the overall system, ensuring timely responses to sensor data.

In addition to serving the Android application, the broker also monitors sensor values received from the Arduinos every second. If any threshold is breached, the broker will publish a post on Mastodon with a passive-aggressive message. The message will identify the plant by its user-given name or a generated name if none is provided.

### Android Application

The Android application provides an interface for users to:
- Add new plants
- Monitor the status of each plant (view sensor values)
- Define and adjust thresholds for sensor readings
- Manually activate actuators (e.g., water plants, increase light)

## System Architecture

### Communication

The communication between Arduinos and the Raspberry Pi is managed through a publisher/subscriber model using MQTT (Mosquitto). This ensures efficient and reliable data transmission across the system.

### Server

The server running on the Raspberry Pi is developed in Python using Flask. It handles requests from the Android application, processes data from the Arduino units, and facilitates interaction between components.

## Getting Started

### Prerequisites

- **Arduino**: Set up with the necessary sensors and actuators.
- **Raspberry Pi**: Installed with Python, Flask, and Mosquitto MQTT broker.
- **Android Device**: Running the application.
- **Mastodon Account**: For the Raspberry Pi broker to post updates. Add the API tokens/secrets to the .env file

More information on how to deploy each component can be found on it's corresponding wiki

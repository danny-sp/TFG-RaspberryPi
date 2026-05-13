"""
Module for handling MQTT communication with the broker, including publishing requests and receiving responses.
"""

import os
import threading

import paho.mqtt.client as mqtt

from src.Utils.logger import setup_logger


class MqttService:
    """
    Service class to handle MQTT communication for publishing requests and receiving responses.
    """

    _server = os.getenv("MQTT_BROKER_HOST", "server")
    _port = int(os.getenv("MQTT_BROKER_PORT", "1883"))

    _client = mqtt.Client()
    _client.connect(_server, _port)

    _requests_topic = os.getenv("MQTT_REQUESTS_TOPIC", "vehicles/requests")
    _plate = os.getenv("VEHICLE_PLATE", "1234 BCD")

    _logger = setup_logger("MqttService")

    _received_message = None
    _message_event = threading.Event()

    @classmethod
    def publish_request(cls, request_json: str):
        """
        Publish a request message to the MQTT broker on the specified topic.

        Args:
            request_json (str): The JSON string representation of the request to be published.
        """

        cls._logger.debug(f"Broker host: {cls._server}, port: {cls._port}")
        cls._logger.info(
            f"Publishing request to topic '{cls._requests_topic}': {request_json}"
        )
        cls._client.publish(cls._requests_topic, request_json, qos=1)

    @classmethod
    def get_response(cls, timeout=30) -> str | None:
        """
        Wait for a response message on the topic 'response/{plate}' and return its payload.

        Args:
            timeout (int): The maximum time to wait for a response in seconds.

        Returns:
            str | None: The payload of the received message as a string, or None if no message was received within the timeout period.
        """
        cls._received_message = None
        cls._message_event.clear()
        cls._logger.info(
            f"Waiting for response on topic 'response/{cls._plate}' with timeout of {timeout} seconds..."
        )
        cls._client.subscribe(f"response/{cls._plate}", qos=1)
        cls._client.on_message = cls.on_message
        cls._client.loop_start()

        if cls._message_event.wait(timeout):
            cls._logger.info("Message received successfully")
            return cls._received_message
        else:
            cls._logger.warning(f"Timeout waiting for response after {timeout} seconds")
            return None

    @classmethod
    def on_message(cls, client, userdata, msg):
        """
        Callback function to handle incoming MQTT messages.
        """
        cls._logger.info(f"Received response from topic '{msg.topic}'")
        cls._received_message = msg.payload.decode()
        cls._message_event.set()

    @classmethod
    def setup_message_callback(cls):
        """
        Set up the MQTT client to listen for responses on the appropriate topic and handle incoming messages.
        """
        cls._client.on_message = cls.on_message
        cls._client.loop_start()

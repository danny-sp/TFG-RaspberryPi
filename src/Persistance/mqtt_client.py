import paho.mqtt.client as mqtt
import os

from src.Utils.logger import setup_logger

class MqttService:
    _server = os.getenv("MQTT_BROKER_HOST", "server")
    _port = int(os.getenv("MQTT_BROKER_PORT", 1883))

    _client = mqtt.Client()
    _client.connect(_server, _port)

    _requests_topic = os.getenv("MQTT_REQUESTS_TOPIC", "vehicles/requests")

    _logger = setup_logger("MqttService")

    @classmethod
    def publish_request(cls, request_json: str):
        cls._logger.debug(f"Broker host: {cls._server}, port: {cls._port}")
        cls._logger.info(f"Publishing request to topic '{cls._requests_topic}': {request_json}")
        cls._client.publish(cls._requests_topic, request_json, qos=1)

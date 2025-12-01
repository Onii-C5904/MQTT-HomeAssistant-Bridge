# Python MQTT–Home Assistant Bridge

Full documentation is available here:

➡️ **[Project Documentation](docs/index_classes.md)**  

## Setup
To run the demo, ensure Docker is installed. 
1. Run `./docker-launch.sh`. This will build the image for the bridge container and create the HomeAssistant and Mosquitto MQTT broker containers.
    - NOTE: The default docker-compose file uses homeassistant and mosquitto folders in `/opt/`. The Mosquitto broker config is stored in `./config/mosquitto/`.
2. Go to http://beagleplay.local:8123/ and complete the HomeAssistant setup process.
3. Once your account is created in HomeAssistant, click the Settings button in the bottom left. 
4. Click Add integration. Search `mqtt` in the brand name field. Select the first result.
5. For MQTT connection information, enter `localhost` for the host. Enter the username and password of the MQTT broker. For the demo, use user `oniic` and password `Saltersimp5904`.
    - NOTE: If you wish to change the credentials, run `docker exec -it mosquitto mosquitto_passwd -c /mosquitto/config/password.txt YOUR_USERNAME_HERE`. Update the broker details in `./config/bridge_config.json`. Update the connection information in Home Assistant.
6. Home Assistant may prompt with "Device created" for each IIO sensor. Click "Skip and finish" or assign an Area.
7. To shut the demo down, run `./docker-quit.sh` to stop and remove the containers.
    - NOTE: The `/opt/homeassistant/` and `/opt/mosquitto/` directories will remain. Delete these if desired.

## Configuration Files
### Mosquitto MQTT Broker
`./config/mosquitto/mosquitto.conf`
```
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
listener 1883

## Authentication
allow_anonymous false
password_file /mosquitto/config/password.txt
```

`./config/mosquitto/password.txt`
```
USER:$7$101$fGrn8glRk+LsAWwt$I00jtYDPv8R7jN3YJrrA1E6AI3JKyPtuGFy8c2N1A7E25l8xDsahdsQ7su1+IXT2/qF1ouuz/3TBW7KRR5y6Fw==
```

## Bridge
`./config/bridge_config.json`
```json
{
    "username": "USER",
    "password": "PASSWORD",
    "host": "127.0.0.1",
    "port": 1883,
    "client_id": "client-1",
    "max_qos_packet_attempts": 1000,
    "publish_interval": 5
}
```
- `username` - MQTT broker user authentication.
- `password` - MQTT broker password authentication.
- `host` - Address of the MQTT broker server.
- `port` - Port of the MQTT broker server.
- `client_id` - Name for this instance of the bridge. Helps differentiate the IIO sensors attached to different BeaglePlay boards.
- `max_qos_packet_attempts` - Maximum number of attempts to QoS Send before giving up.
- `publish_interval` - Number of seconds to wait before publishing updated sensor data to the MQTT broker.

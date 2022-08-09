# EMA-Reader
Acquires solar generation metrics from AP Systems EMA web app.

### Config
All config variables are located in `config.py` with sections divided into separate dictionaries. 
| Name     | Value                                     |
|----------|-------------------------------------------|
| `webdriver` | Allows setting webdriver options |
| `auth` | Shouldn't need to change unless the web app changes URLs, DOM element values, etc. |
| `api` | Defines endpoints, headers, etc. |
| `mqtt` | MQTT Topics and non-sensitive config |
| `response_fields` | Maps MQTT topics to api response fields |
| `exception_handling` | Defines how the program will handle exceptions |

### Secrets
There are 2 methods to add secrets:

##### Environment Variables
The following environment variables are supported:
| Name     | Value                                     |
|----------|-------------------------------------------|
| `AUTH_USERNAME` | Your login username |
| `AUTH_PASSWORD` | Your login password |
| `MQTT_HOSTNAME` | Target mqtt host |
| `MQTT_PORT` | Target mqtt port |

##### Python file
A file named `secrets.py` can be created in the `/ema-reader` directory within the container with the following variables where a `.` denotes a dictionary:
| Name     | Value                                     |
|----------|-------------------------------------------|
| `auth.username` | Your login username |
| `auth.password` | Your login password |
| `mqtt.hostname` | Target mqtt host |
| `mqtt.port` | Target mqtt port; can be int or string |

Example:
```
auth:
  username: "your username"
  password: "your password"

mqtt:
  hostname: "mqtt hostname"
  port: 1883
```

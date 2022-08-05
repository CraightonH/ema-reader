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
A file `secrets.py` must be created with the following variables where a `.` denotes a dictionary:
| Name     | Value                                     |
|----------|-------------------------------------------|
| `auth.username` | Your login username |
| `auth.password` | Your login password |
| `mqtt.hostname` | Target mqtt host |
| `mqtt.port` | Target mqtt port |

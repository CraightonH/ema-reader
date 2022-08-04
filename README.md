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
| `response_fields` | Maps MQTT topics to response fields |

### Secrets
A file `secrets.py` must be created with the following variables where a `.` denotes a dictionary:
| Name     | Value                                     |
|----------|-------------------------------------------|
| `auth.username` | default: None<br/>Your login username |
| `auth.password` | default: None<br/>Your login password |
| `mqtt.hostname` | default: None<br/>Target mqtt host |
| `mqtt.port` | default: None<br/>Target mqtt port |

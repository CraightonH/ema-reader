# EMA-Reader
[![Pylint](https://github.com/CraightonH/ema-reader/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/CraightonH/ema-reader/actions/workflows/pylint.yml)

Acquires solar generation metrics from AP Systems EMA web app.

### Config
All config variables are located in a directory called `config/`. This means you can manage config for each section in separate files, if desired, or just one large file. The file name doesn't matter. Any files in this directory will be assumed to be config in `yaml` format. 
| Name     | Value                                     |
|----------|-------------------------------------------|
| `webdriver` | Allows setting webdriver options |
| `auth` | Shouldn't need to change unless the web app changes URLs, DOM element values, etc. |
| `api` | Defines endpoints, headers, etc. |
| `mqtt` | MQTT Topics and non-sensitive config |
| `response_fields` | Maps MQTT topics to api response fields |
| `exception_handling` | Defines how the program will handle exceptions |
| `logging` | Defines how logging should be configured |

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

##### YAML
All secret variables are located in a directory called `secrets/`. This means you can manage secrets for each section in separate files, if desired, or just one large file. The file name doesn't matter. Any files in this directory will be assumed to be secrets in `yaml` format. 
| Name     | Value                                     |
|----------|-------------------------------------------|
| `auth.username` | Your login username |
| `auth.password` | Your login password |
| `mqtt.hostname` | Target mqtt host |
| `mqtt.port` | Target mqtt port; can be int or string |

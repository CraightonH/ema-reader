# EMA-Reader
Acquires solar generation metrics from AP Systems EMA web app.

### Config
All config variables are located in `config.py`. These should not need to change unless the web app changes URLs, DOM element values, etc.

### Secrets
A file `secrets.py` must be created with the following variables:
| Name     | Value                                     |
|----------|-------------------------------------------|
| username | default: None<br/>Your login username |
| password | default: None<br/>Your login password |

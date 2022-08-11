"""
Logs into EMA web app and grabs metrics from EMA's API
"""
from time import sleep
import traceback
import os
import logging
from sys import exit as sys_exit
import yaml
from paho.mqtt import publish
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from requests import post

config = {}
secret = {}
log = logging.getLogger("app.py")

def app_setup():
    """
    Sets up config, secrets, and logging
    """
    log_level_opt = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "warn": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    try:
        config_dir = 'config'
        if os.getenv("CONFIG_DIRECTORY_NAME") is not None:
            config_dir = os.environ["CONFIG_DIRECTORY_NAME"]
        for file in os.listdir(config_dir):
            if os.path.isfile(os.path.join(config_dir, file)):
                with open(f'{config_dir}/{file}', 'r', encoding="utf-8") as config_stream:
                    config.update(yaml.safe_load(config_stream))
    except FileNotFoundError:
        # pylint: disable=C0301
        print("Could not find config file. Please review documentation on config file location/format.")
        sys_exit(1)

    log.setLevel(log_level_opt[config["logging"]["level"].lower()])
    log_handle = logging.StreamHandler()
    log_handle.setLevel(log_level_opt[config["logging"]["level"].lower()])
    log_handle.setFormatter(logging.Formatter(config["logging"]["format"]))
    log.addHandler(log_handle)

    try:
        secrets_dir = 'secrets'
        if os.getenv("SECRETS_DIRECTORY_NAME") is not None:
            secrets_dir = os.environ["SECRETS_DIRECTORY_NAME"]
        for file in os.listdir(secrets_dir):
            if os.path.isfile(os.path.join(secrets_dir, file)):
                with open(f'{secrets_dir}/{file}', 'r', encoding="utf-8") as secret_stream:
                    secret.update(yaml.safe_load(secret_stream))
    except FileNotFoundError:
        try:
            log.warning("Could not find secrets file. Using environment variables instead.")
            secret["auth"]["username"] = os.environ["AUTH_USERNAME"]
            secret["auth"]["password"] = os.environ["AUTH_PASSWORD"]
            secret["mqtt"]["hostname"] = os.environ["MQTT_HOSTNAME"]
            secret["mqtt"]["port"] = os.environ["MQTT_PORT"]
        except KeyError as err:
            log.error("Environment variable not found: %s. Quitting with non-zero exit code.", err)
            sys_exit(1)

def setup_driver():
    """
    Sets up the Firefox driver from config
    """
    options = Options()
    for opt in config["webdriver"]["driver_opts"]:
        options.add_argument(opt)
    return webdriver.Firefox(options=options)

def logout(driver: webdriver.Firefox):
    """
    Logs out of EMA web app
    """
    log.debug("(logout) driver.current_url: %s", driver.current_url)
    sleep(1)
    top_menu = driver.find_element(By.CLASS_NAME, "div_menu2")
    anchors = top_menu.find_elements(By.TAG_NAME, "a")
    sign_out = anchors[len(anchors) - 1]
    if not sign_out.text == config["auth"]["sign_out_text"]:
        raise Exception("Error in logout: Could not find sign out button")
    sign_out.click()
    driver.close()
    return True

def login(driver: webdriver.Firefox):
    """
    Logs in to EMA web app
    """
    log.info("(login) Logging in to %s", config["auth"]["login_url"])
    success = False
    driver.get(config["auth"]["login_url"])
    log.debug("(login) driver.current_url: %s", driver.current_url)
    input_username = driver.find_element(By.ID, config["auth"]["username_element_id"])
    input_username.clear()
    input_username.send_keys(secret["auth"]["username"])
    log.debug("(login) input.username: %s", input_username.get_attribute("value"))
    input_password = driver.find_element(By.ID, config["auth"]["password_element_id"])
    input_password.clear()
    input_password.send_keys(secret["auth"]["password"])
    if config["logging"]["redact_sensitive_fields"]:
        log.debug("(login) input.password: [REDACTED]")
    else:
        log.debug("(login) input.password: %s", input_password.get_attribute("value"))
    driver.find_element(By.ID, config["auth"]["login_button_element_id"]).click()
    success = config["auth"]["exception_page"] not in driver.current_url
    return success

def get_production_info(cookies):
    """
    Requests data from EMA getProductionInfo API endpoint
    """
    log.info("(get_production_info) Acquiring production info")
    headers = config["api"]["headers"]
    endpoint = config["api"]["endpoints"]["getProductionInfo"]
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict.update({cookie["name"]: cookie["value"]})
    response = post(url=endpoint, cookies=cookie_dict, headers=headers)
    if not response.ok:
        raise Exception("Error retrieving production info: " + response.reason)
    log.info("(get_production_info) Successfully acquired production info")
    return response.json()

def publish_production_info(data):
    """
    Send data to MQTT broker
    """
    hostname = secret["mqtt"]["hostname"]
    port = int(secret["mqtt"]["port"])
    # pylint: disable=C0301
    log.info("(publish_production_info) Publishing production info to mqtt broker at %s:%s", hostname, port)
    topic_prefix = config["mqtt"]["topic_prefix"]
    client_id = config["mqtt"]["client_id"]
    for topic in config["mqtt"]["topics"]:
        name = topic_prefix + topic["name"]
        qos = topic["qos"]
        retain = bool(topic["retain"])
        payload = data[config["response_fields"][topic["name"]]]
        publish.single(topic=name, payload=payload, qos=qos, retain=retain, hostname=hostname, port=port, client_id=client_id)

if __name__ == "__main__":
    app_setup()
    web_driver = setup_driver()
    interval = config["exception_handling"]["initial_interval"]
    max_attempts = config["exception_handling"]["max_attempts"]
    # pylint: disable=C0103
    num_attempts = 0
    while num_attempts != max_attempts:
        num_attempts += 1
        try:
            if login(web_driver):
                log.info("(__main__) Successfully logged in")
                json_data = get_production_info(web_driver.get_cookies())
                publish_production_info(json_data)
                if logout(web_driver):
                    log.info("(__main__) Successfully retrieved data. Exiting with success code 0.")
                    sys_exit(0)
                else:
                    # pylint: disable=C0301
                    log.warning("(__main__) Failed to logout properly. Data was collected, but logout issues should be investigated. Exiting with success code 0.")
                    sys_exit(0)
            else:
                raise Exception("Failed login")
        # pylint: disable=W0703
        except Exception as ex:
            trace = traceback.format_exc()
            log.error("(__main__) %s %s %s", type(ex), ex, trace)
        # pylint: disable=C0301
        log.info("(__main__) Initiating backoff. Attempts remaining: %i. Will retry in %i seconds.", (max_attempts - num_attempts), interval)
        if num_attempts > 0:
            interval = interval * config["exception_handling"]["backoff_multiplier"]
        sleep(interval)
    if num_attempts == max_attempts:
        log.error("(__main__) Unable to complete execution. Quitting with error code 1.")
        sys_exit(1)

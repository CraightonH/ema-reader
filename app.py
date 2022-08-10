from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from requests import post
from time import sleep
from sys import exit as sys_exit
import paho.mqtt.publish as publish, traceback, os, yaml, logging
config = {}
secret = {}
log = logging.getLogger("app.py")
def appSetup():
    log_level_opt = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "warn": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    try:
        config_dir = os.getenv('CONFIG_DIRECTORY_NAME') if os.getenv('CONFIG_DIRECTORY_NAME') is not None else 'config'
        for file in os.listdir(config_dir):
            if os.path.isfile(os.path.join(config_dir, file)):
                with open(f'{config_dir}/{file}', 'r') as config_stream:
                    config.update(yaml.safe_load(config_stream))
    except FileNotFoundError as err:
        print("Could not find config file. Please review documentation on config file location/format.")
        sys_exit(1)

    log.setLevel(log_level_opt[config["logging"]["level"].lower()])
    log_handle = logging.StreamHandler()
    log_handle.setLevel(log_level_opt[config["logging"]["level"].lower()])
    log_handle.setFormatter(logging.Formatter(config["logging"]["format"]))
    log.addHandler(log_handle)

    try:
        secrets_dir = os.getenv('SECRETS_DIRECTORY_NAME') if os.getenv('SECRETS_DIRECTORY_NAME') is not None else 'secrets'
        for file in os.listdir(secrets_dir):
            if os.path.isfile(os.path.join(secrets_dir, file)):
                with open(f'{secrets_dir}/{file}', 'r') as secret_stream:
                    secret.update(yaml.safe_load(secret_stream))
    except FileNotFoundError:
        try:
            log.warning("Could not find secrets file. Using environment variables instead.")
            secret["auth"]["username"] = os.environ["AUTH_USERNAME"]
            secret["auth"]["password"] = os.environ["AUTH_PASSWORD"]
            secret["mqtt"]["hostname"] = os.environ["MQTT_HOSTNAME"]
            secret["mqtt"]["port"] = os.environ["MQTT_PORT"]
        except KeyError as err:
            log.error("Environment variable not found: " + str(err) + ". Quitting with non-zero exit code.")
            sys_exit(1)

def setupDriver():
    options = Options()
    for opt in config["webdriver"]["driver_opts"]:
        options.add_argument(opt)
    return webdriver.Firefox(options=options)

def logout(driver: webdriver.Firefox):
    log.debug("(logout) driver.current_url: " + driver.current_url)
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
    log.info("(login) Logging in to " + config["auth"]["login_url"])
    success = False
    driver.get(config["auth"]["login_url"])
    log.debug("(login) driver.current_url: " + driver.current_url)
    input_username = driver.find_element(By.ID, config["auth"]["username_element_id"])
    input_username.clear()
    input_username.send_keys(secret["auth"]["username"])
    log.debug("(login) input.username: " + input_username.get_attribute("value"))
    input_password = driver.find_element(By.ID, config["auth"]["password_element_id"])
    input_password.clear()
    input_password.send_keys(secret["auth"]["password"])
    if config["logging"]["redact_sensitive_fields"]:
        log.debug("(login) input.password: [REDACTED]")
    else:
        log.debug("(login) input.password: " + input_password.get_attribute("value"))
    driver.find_element(By.ID, config["auth"]["login_button_element_id"]).click()
    success = config["auth"]["exception_page"] not in driver.current_url
    return success

def getProductionInfo(cookies):
    log.info("(getProductionInfo) Acquiring production info")
    headers = config["api"]["headers"]
    endpoint = config["api"]["endpoints"]["getProductionInfo"]
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict.update({cookie["name"]: cookie["value"]})
    response = post(url=endpoint, cookies=cookie_dict, headers=headers)
    if not response.ok:
        raise Exception("Error retrieving production info: " + response.reason)
    log.info("(getProductionInfo) Successfully acquired production info")
    return response.json()

def publishProductionInfo(data):
    log.info("(publishProductionInfo) Publishing production info to mqtt broker at " + secret["mqtt"]["hostname"] + ":" + str(secret["mqtt"]["port"]))
    publish.single(topic=config["mqtt"]["topic"]["prefix"] + config["mqtt"]["topic"]["current_power"], payload=data[config["response_fields"][config["mqtt"]["topic"]["current_power"]]], qos=config["mqtt"]["qos"], hostname=secret["mqtt"]["hostname"], port=int(secret["mqtt"]["port"]), client_id=config["mqtt"]["client_id"], retain=bool(config["mqtt"]["retainStatistics"]))
    publish.single(topic=config["mqtt"]["topic"]["prefix"] + config["mqtt"]["topic"]["energy_today"], payload=data[config["response_fields"][config["mqtt"]["topic"]["energy_today"]]], qos=config["mqtt"]["qos"], hostname=secret["mqtt"]["hostname"], port=int(secret["mqtt"]["port"]), client_id=config["mqtt"]["client_id"], retain=bool(config["mqtt"]["retainStatistics"]))
    publish.single(topic=config["mqtt"]["topic"]["prefix"] + config["mqtt"]["topic"]["energy_lifetime"], payload=data[config["response_fields"][config["mqtt"]["topic"]["energy_lifetime"]]], qos=config["mqtt"]["qos"], hostname=secret["mqtt"]["hostname"], port=int(secret["mqtt"]["port"]), client_id=config["mqtt"]["client_id"], retain=bool(config["mqtt"]["retainStatistics"]))
    publish.single(topic=config["mqtt"]["topic"]["prefix"] + config["mqtt"]["topic"]["co2_saved"], payload=data[config["response_fields"][config["mqtt"]["topic"]["co2_saved"]]], qos=config["mqtt"]["qos"], hostname=secret["mqtt"]["hostname"], port=int(secret["mqtt"]["port"]), client_id=config["mqtt"]["client_id"], retain=bool(config["mqtt"]["retainStatistics"]))
    publish.single(topic=config["mqtt"]["topic"]["prefix"] + config["mqtt"]["topic"]["monitor_status"], payload=data[config["response_fields"][config["mqtt"]["topic"]["monitor_status"]]], qos=config["mqtt"]["qos"], hostname=secret["mqtt"]["hostname"], port=int(secret["mqtt"]["port"]), client_id=config["mqtt"]["client_id"], retain=bool(config["mqtt"]["retainMonitorStatus"]))

if __name__ == "__main__":
    appSetup()
    driver = setupDriver()
    interval = config["exception_handling"]["initial_interval"]
    max_attempts = config["exception_handling"]["max_attempts"]
    num_attempts = 0
    while(num_attempts != max_attempts):
        num_attempts += 1
        try:
            if login(driver):
                log.info("(__main__) Successfully logged in")
                json_data = getProductionInfo(driver.get_cookies())
                publishProductionInfo(json_data)
                if logout(driver):
                    log.info("(__main__) Successfully retrieved data. Exiting with success code 0.")
                    sys_exit(0)
                else:
                    log.warning("(__main__) Failed to logout properly. Data was collected, but logout issues should be investigated. Exiting with success code 0.")
                    sys_exit(0)
            else:
                raise Exception("Failed login")
        except Exception as ex:
            trace = traceback.format_exc()
            log.error("(__main__) " + str(type(ex)) + " " + str(ex) + " " + str(trace))
        log.info("(__main__) Initiating backoff. Attempts remaining: " + str(max_attempts - num_attempts) + ". Will retry in " + str(interval) + " seconds.")
        if num_attempts > 0:
            interval = interval * config["exception_handling"]["backoff_multiplier"]
        sleep(interval)
    if num_attempts == max_attempts:
        log.error("(__main__) Unable to complete execution. Quitting with error code 1.")
        sys_exit(1)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import paho.mqtt.publish as publish
from requests import post
import config
import secret

def setupDriver():
    options = Options()
    for opt in config.webdriver["driver_opts"]:
        options.add_argument(opt)
    return webdriver.Firefox(options=options)

def logout(driver: webdriver.Firefox):
    top_menu = driver.find_element(By.CLASS_NAME, "div_menu2")
    anchors = top_menu.find_elements(By.TAG_NAME, "a")
    sign_out = anchors[len(anchors) - 1]
    assert sign_out.text == config.auth["sign_out_text"]
    sign_out.click()
    print(driver.current_url)
    driver.close()

def login(driver: webdriver.Firefox):
    # try:
    driver.get(config.auth["login_url"])
    # print("current url: " + driver.current_url)
    input_username = driver.find_element(By.ID, config.auth["username_element_id"])
    input_username.clear()
    input_username.send_keys(secret.auth["username"])
    # print("input.username: " + input_username.get_attribute("value"))
    input_password = driver.find_element(By.ID, config.auth["password_element_id"])
    input_password.clear()
    input_password.send_keys(secret.auth["password"])
    # print("input.password: " + input_password.get_attribute("value"))
    assert input_username.get_attribute("value") == secret.auth["username"] and input_password.get_attribute("value") == secret.auth["password"]
    driver.find_element(By.ID, config.auth["login_button_element_id"]).click()
    assert config.auth["exception_page"] not in driver.current_url
    return True

def getProductionInfo(cookies):
    print("Acquiring production info")
    headers = config.api["headers"]
    endpoint = config.api["endpoints"].get("getProductionInfo")
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict.update({cookie["name"]: cookie["value"]})
    response = post(url=endpoint, cookies=cookie_dict, headers=headers)
    assert response.ok
    print("Successfully acquired production info")
    return response.json()

def publishProductionInfo(data):
    print("Publishing production info to " + secret.mqtt["hostname"] + ":" + str(secret.mqtt["port"]))
    publish.single(topic=config.mqtt["topic_prefix"] + config.mqtt["topic_current_power"], payload=data[config.response_fields[config.mqtt["topic_current_power"]]], qos=config.mqtt["qos"], hostname=secret.mqtt["hostname"], port=secret.mqtt["port"], client_id=config.mqtt["client_id"])
    publish.single(topic=config.mqtt["topic_prefix"] + config.mqtt["topic_energy_today"], payload=data[config.response_fields[config.mqtt["topic_energy_today"]]], qos=config.mqtt["qos"], hostname=secret.mqtt["hostname"], port=secret.mqtt["port"], client_id=config.mqtt["client_id"])
    publish.single(topic=config.mqtt["topic_prefix"] + config.mqtt["topic_energy_lifetime"], payload=data[config.response_fields[config.mqtt["topic_energy_lifetime"]]], qos=config.mqtt["qos"], hostname=secret.mqtt["hostname"], port=secret.mqtt["port"], client_id=config.mqtt["client_id"])
    publish.single(topic=config.mqtt["topic_prefix"] + config.mqtt["topic_monitor_status"], payload=data[config.response_fields[config.mqtt["topic_monitor_status"]]], qos=config.mqtt["qos"], hostname=secret.mqtt["hostname"], port=secret.mqtt["port"], client_id=config.mqtt["client_id"])
    publish.single(topic=config.mqtt["topic_prefix"] + config.mqtt["topic_co2_saved"], payload=data[config.response_fields[config.mqtt["topic_co2_saved"]]], qos=config.mqtt["qos"], hostname=secret.mqtt["hostname"], port=secret.mqtt["port"], client_id=config.mqtt["client_id"])

if __name__ == "__main__":
    driver = setupDriver()
    print("Logging in to " + config.auth["login_url"])
    if login(driver):
        print("Successfully logged in")
        publishProductionInfo(getProductionInfo(driver.get_cookies()))
        logout(driver)
    else:
        print("ERROR: Unable to login")

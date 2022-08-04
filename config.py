webdriver = {
    "driver_opts": ["--headless"]
}

auth = {
    "login_url": "https://www.apsystemsema.com/ema/index.action",
    "username_element_id": "username",
    "password_element_id": "password",
    "login_button_element_id": "Login",
    "sign_out_text": "Sign out",
    "exception_page": "ema/exceptionIndex.action"
}

api = {
    "polling_interval": "300",
    "headers": {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Microsoft Edge\";v=\"103\", \"Chromium\";v=\"103\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "Referer": "https://www.apsystemsema.com/ema/security/optmainmenu/intoLargeDashboard.action",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    },
    "endpoints": {
        "getProductionInfo": "https://www.apsystemsema.com/ema/ajax/getDashboardApiAjax/getDashboardProductionInfoAjax"
    }
}

mqtt = {
    "client_id": "ema-reader",
    "qos": 0,
    "topic_prefix": "homeassistant/energy/solar/",
    "topic_current_power": "power_current",
    "topic_energy_today": "energy_today",
    "topic_energy_lifetime": "energy_lifetime",
    "topic_monitor_status": "monitor_status",
    "topic_co2_saved": "co2_saved"
}

response_fields = {
    "power_current": "lastPower",
    "energy_today": "today",
    "energy_lifetime": "lifetime",
    "monitor_status": "meterFlag",
    "co2_saved": "co2"
}
import os
import digitalio
import wifi
import time
import microcontroller
import board
import simpleio
import adafruit_requests
import ssl
import pwmio
from adafruit_motor import servo
# Get wifi details from a settings.toml file
print(os.getenv("test_env_file"))
ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
telegrambot = os.getenv("botToken")

# Telegram API url.
API_URL = "https://api.telegram.org/bot" + telegrambot


# Input-Output Initialization
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

CookMode = digitalio.DigitalInOut(board.GP1)
CookMode.direction = digitalio.Direction.OUTPUT

pb = digitalio.DigitalInOut(board.GP20)
pb.direction = digitalio.Direction.INPUT

mains=digitalio.DigitalInOut(board.GP2)
mains.direction=digitalio.Direction.OUTPUT
mains.value=True

servo_a_pin = pwmio.PWMOut(board.GP26, frequency=50)
servo_a = servo.Servo(servo_a_pin, min_pulse=750, max_pulse=2000)
\




def init_bot():
    get_url = API_URL
    get_url += "/getMe"
    r = requests.get(get_url)
    return r.json()['ok']

first_read = True
update_id = 0

def read_message():
    global first_read
    global update_id

    get_url = API_URL
    get_url += "/getUpdates?limit=1&allowed_updates=[\"message\",\"callback_query\"]"
    if first_read == False:
        get_url += "&offset={}".format(update_id)

    r = requests.get(get_url)
    #print(r.json())

    try:
        update_id = r.json()['result'][0]['update_id']
        message = r.json()['result'][0]['message']['text']
        chat_id = r.json()['result'][0]['message']['chat']['id']

        #print("Update ID: {}".format(update_id))
        print("Chat ID: {}\tMessage: {}".format(chat_id, message))

        first_read = False
        update_id += 1

        return chat_id, message

    except (IndexError) as e:
        #print("No new message")
        return False, False

def send_message(chat_id, message):
    get_url = API_URL
    get_url += "/sendMessage?chat_id={}&text={}".format(chat_id, message)
    r = requests.get(get_url)
    #print(r.json())

def modeSelect(mode):
    if mode=="warm":
        servo_a.angle=90
        #time.sleep(5)
        print("warm mode")
    elif mode=='cook':
        servo_a.angle=0
        #time.sleep(5)
        print("cooking")

def readIntTemp():
    data = microcontroller.cpu.temperature
    data = "Temperature: {:.2f} °C".format(data)
    return data

#  Connect to Wi-Fi AP
print(f"Initializing...")
print(ssid,password)
wifi.radio.connect(ssid, password)
print("connected!\n")
pool = socketpool.SocketPool(wifi.radio)
print("IP Address: {}".format(wifi.radio.ipv4_address))
print("Connecting to WiFi '{}' ... ".format(ssid), end="")
requests = adafruit_requests.Session(pool, ssl.create_default_context())

if init_bot() == False:
    print("\nTelegram bot failed.")
else:
    print("\nTelegram bot ready!\n")

while True:
    try:
        while not wifi.radio.ipv4_address or "0.0.0.0" in repr(wifi.radio.ipv4_address):
            print(f"Reconnecting to WiFi...")
            wifi.radio.connect(ssid, password)

        chat_id, message_in = read_message()
        if message_in == "/start":
            send_message(chat_id,"Hello!")
            send_message(chat_id,"Choose from one of the following options:")
            send_message(chat_id,"1) Cook:  /cook")
            send_message(chat_id,"2) Warm: /warm")
            send_message(chat_id,"3) On The Cooker: /oncooker")
            send_message(chat_id,"4) Off The Cooker: /offcooker")
            send_message(chat_id,"Check Status: /check")
        elif message_in == "/cook":
            modeSelect("cook")
            send_message(chat_id, "starting process...")
        elif message_in == "/warm":
            modeSelect("cook")
            send_message(chat_id, "cooker on warm mode!")
        elif message_in == "/oncooker":
            mains.value = False
            send_message(chat_id, "cooker turned on")
        elif message_in == "/offcooker":
            mains.value = True
            send_message(chat_id, "cooker turned off")
        elif message_in == "/check":
            if (mains!=True):
                send_message(chat_id, "cooker is on")
            else:
                send_message(chat_id, "cooker is off")
        else:
            send_message(chat_id, "Command is not available.")


    except OSError as e:
        print("Failed!\n", e)
        microcontroller.reset()
print(1)



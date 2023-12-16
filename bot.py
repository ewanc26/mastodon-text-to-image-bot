from PIL import Image
import json
import os
import random
from string import printable
from mastodon import Mastodon
import configparser
from cryptography.fernet import Fernet

src = os.path.dirname(os.path.abspath(__file__))
credentials = os.path.join(src, 'credentials', 'config.ini')
credentials_folder = os.path.join(src, 'credentials')
key_file = os.path.join(src, 'credentials', 'key.key')
encrypted_credentials = os.path.join(src, 'credentials', 'config.ini.encrypted')

if os.path.exists(credentials):
    os.remove(credentials)

if not os.path.exists(credentials_folder):
    os.makedirs(credentials_folder)

if os.path.exists(key_file):
    with open(key_file, 'rb') as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(key_file, 'wb') as f:
        f.write(key)

if not os.path.exists(encrypted_credentials):
    url = input("Enter the full URL (e.g., https://mastodon.social) of your Mastodon instance:\n")
    email = input("Enter your email address:\n")
    password = input("Enter your password:\n")

    app_info = Mastodon.create_app("Text to Image", api_base_url=url)
    client_id, client_secret = app_info

    mastodon = Mastodon(client_id=client_id, client_secret=client_secret, api_base_url=url)
    access_token = mastodon.log_in(email, password)

    config = configparser.ConfigParser()
    config['MASTODON'] = {'url': url,
                          'email': email,
                          'password': password,
                          'client_id': client_id,
                          'client_secret': client_secret,
                          'access_token': access_token}

    with open(credentials, 'w') as configfile:
        config.write(configfile)

    with open(credentials, 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)

    with open(encrypted_credentials, 'wb') as f:
        f.write(encrypted_data)

    os.remove(credentials)

config = configparser.ConfigParser()
with open(encrypted_credentials, 'rb') as f:
    encrypted_data = f.read()
fernet = Fernet(key)
data = fernet.decrypt(encrypted_data)

with open(credentials, 'wb') as f:
    f.write(data)

config.read(credentials)
url = config['MASTODON']['url']
email = config['MASTODON']['email']
password = config['MASTODON']['password']
client_id_str = config['MASTODON']['client_id']
client_secret_str = config['MASTODON']['client_secret']
access_token_str = config['MASTODON']['access_token']

mastodon = Mastodon(client_id=client_id_str, client_secret=client_secret_str, access_token=access_token_str, api_base_url=url)

json_file = rf"{src}\sorted_chars.json"

if not os.path.exists(json_file):
    print(rf"Please run {src}\colour generator.py first before continuing.")
    quit("No colour JSON dictionary found.")
else:
    print(rf"{json_file} found.")

with open(json_file) as f:
    colour_codes = json.load(f)

while True:
    try:
        width = int(round(random.randint(100, 100)))
        height = int(round(random.randint(100, 1000)))
        break
    except ValueError:
        print("Invalid input")

squares_per_row = width // 10
num_rows = height // 10

image = Image.new('RGB', (width, height), 'white')

slurs = [
    "arse",
    "ass",
    "bastard",
    "bitch",
    "bloody",
    "bollock",
    "brotherfucker",
    "bugger",
    "bullshit",
    "child-fucker",
    "Christ on a cracker",
    "Christ on a bike",
    "cock",
    "crap",
    "cunt",
    "damn",
    "dick",
    "dyke",
    "fatherfucker",
    "frigger",
    "fuck",
    "hell",
    "holy shit",
    "in shit",
    "horseshit",
    "jesus christ",
    "jesus h. christ",
    "jesus harold christ",
    "jesus wept",
    "jesus, mary and joseph",
    "kike",
    "motherfucker",
    "nigga",
    "nigger",
    "nigra",
    "piss",
    "prick",
    "pussy",
    "shit",
    "shit ass",
    "shite",
    "sisterfucker",
    "slut",
    "whore",
    "son of a bitch",
    "son of a whore",
    "spastic",
    "spaz",
    "sweet jesus",
    "turd",
    "twat",
    "wanker"
]

input_string = ''.join(random.choices(printable, k=random.randint(5, 200)))
for slur in slurs:
    if slur.lower() in input_string.lower():
        print(f"Slur detected: {slur}")
        input_string = input_string.replace(slur, "")

shift = random.randint(1, 10)
index = 0
x, y = 0, 0
for row in range(num_rows):
    for square_index in range(squares_per_row):
        if index >= len(input_string):
            index = 0
        char = input_string[index]
        colour_code = colour_codes.get(char, '000000')
        colour = tuple(int(colour_code[i:i+2], 16) for i in (0, 2, 4))
        square = (x, y, x+10, y+10)
        image.paste(colour, square)
        x += 10
        index_shift = 1 or 5
        index += index_shift
    y += 10
    x = 0

output_filename = rf'{src}\output.png'
image.save(output_filename)

status = f"Prompt: {input_string}"
media_dict = mastodon.media_post(output_filename)
media_ids = [media_dict['id']]
mastodon.status_post(status, media_ids=media_ids, visibility="public")

os.remove(output_filename)
import network
import socket
import time
import machine
import os
import urequests


# ==================================================
# ESP32 MicroPython GitHub OTA
# Version 1.0.9
# ==================================================

# -----------------------------
# WiFi
# -----------------------------

SSID = "labor"
PASSWORD = "98668800"


# -----------------------------
# ESP32
# -----------------------------

HOST_NAME = "esp32"


# -----------------------------
# Login
# -----------------------------

USERNAME = "PAN111"
USER_PASSWORD = "PAN222"


# -----------------------------
# OTA
# -----------------------------

CURRENT_VERSION = "1.0.9"

VERSION_URL = (
    "https://ap3168-bot.github.io/"
    "happygood/version.json"
)

FIRMWARE_PREFIX = (
    "https://ap3168-bot.github.io/"
    "happygood/"
)

# 6 hours
OTA_INTERVAL = 6 * 60 * 60


# ==================================================
# WiFi
# ==================================================

def connect_wifi():

    wlan = network.WLAN(network.STA_IF)

    wlan.active(True)

    if not wlan.isconnected():

        print("Connecting to WiFi...")

        wlan.connect(SSID, PASSWORD)

        while not wlan.isconnected():

            print(".", end="")

            time.sleep(0.5)

    print()
    print("WiFi connected")
    print("IP address:", wlan.ifconfig()[0])

    return wlan


# ==================================================
# Version
# ==================================================

def version_number(version):

    try:

        parts = version.split(".")

        return (
            int(parts[0]),
            int(parts[1]),
            int(parts[2])
        )

    except:

        return (0, 0, 0)


def is_newer_version(remote, current):

    return (
        version_number(remote)
        >
        version_number(current)
    )


# ==================================================
# OTA - Check Version
# ==================================================

def check_for_update():

    print()
    print("[OTA] Checking GitHub...")

    try:

        response = urequests.get(
            VERSION_URL
        )

        if response.status_code != 200:

            print(
                "[OTA] HTTP error:",
                response.status_code
            )

            response.close()

            return

        data = response.json()

        response.close()

        remote_version = data.get("version")

        firmware_url = data.get("firmware")

        if remote_version is None:

            print("[OTA] version missing")

            return

        if firmware_url is None:

            print("[OTA] firmware URL missing")

            return

        print(
            "[OTA] Current:",
            CURRENT_VERSION
        )

        print(
            "[OTA] GitHub:",
            remote_version
        )

        # -----------------------------
        # Security check
        # -----------------------------

        if not firmware_url.startswith(
            FIRMWARE_PREFIX
        ):

            print(
                "[OTA] Firmware URL rejected"
            )

            return

        # -----------------------------
        # Version check
        # -----------------------------

        if not is_newer_version(
            remote_version,
            CURRENT_VERSION
        ):

            print(
                "[OTA] Already up to date"
            )

            return

        print(
            "[OTA] New version found!"
        )

        print(
            "[OTA] Downloading..."
        )

        download_update(
            firmware_url,
            remote_version
        )

    except Exception as error:

        print(
            "[OTA] Check error:",
            error
        )


# ==================================================
# OTA - Download
# ==================================================

def download_update(url, new_version):

    try:

        response = urequests.get(url)

        if response.status_code != 200:

            print(
                "[OTA] Download HTTP error:",
                response.status_code
            )

            response.close()

            return

        print(
            "[OTA] Downloading:",
            url
        )

        # -----------------------------
        # Temporary file
        # -----------------------------

        new_file = "main_new.py"

        old_file = "main_old.py"

        current_file = "main.py"

        # Delete old backup
        if old_file in os.listdir():

            os.remove(old_file)

        # -----------------------------
        # Save new program
        # -----------------------------

        with open(new_file, "wb") as file:

            while True:

                chunk = response.raw.read(1024)

                if not chunk:

                    break

                file.write(chunk)

        response.close()

        print(
            "[OTA] Download complete"
        )

        # -----------------------------
        # Check file
        # -----------------------------

        if new_file not in os.listdir():

            print(
                "[OTA] New file not found"
            )

            return

        # -----------------------------
        # Backup current program
        # -----------------------------

        if current_file in os.listdir():

            os.rename(
                current_file,
                old_file
            )

        # -----------------------------
        # Install new program
        # -----------------------------

        os.rename(
            new_file,
            current_file
        )

        print(
            "[OTA] Update successful!"
        )

        print(
            "[OTA] New version:",
            new_version
        )

        print(
            "[OTA] Restarting ESP32..."
        )

        time.sleep(2)

        machine.reset()

    except Exception as error:

        print(
            "[OTA] Update error:",
            error
        )


# ==================================================
# Login Page
# ==================================================

def login_page():

    return """\
HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>ESP32 Login</title>

</head>

<body>

<h2>ESP32 Login Page</h2>

<form action="/login" method="POST">

Username:
<input type="text" name="userid">

<br><br>

Password:
<input type="password" name="pwd">

<br><br>

<button type="submit">
Login
</button>

</form>

</body>

</html>
"""


# ==================================================
# OTA Page
# ==================================================

def ota_page():

    return """\
HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>ESP32 OTA</title>

</head>

<body>

<h2>ESP32 GitHub OTA</h2>

<p>
Current version: 1.0.9
</p>

<p>
Automatic version checking:
Every 6 hours
</p>

<form action="/check" method="POST">

<button type="submit">

Check GitHub Version Now

</button>

</form>

</body>

</html>
"""


# ==================================================
# 404 Page
# ==================================================

def not_found_page():

    return """\
HTTP/1.1 404 Not Found
Content-Type: text/plain
Connection: close

404 Not Found
"""


# ==================================================
# Web Server
# ==================================================

def start_server():

    address = socket.getaddrinfo(
        "0.0.0.0",
        80
    )[0][-1]

    server = socket.socket()

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(address)

    server.listen(1)

    server.settimeout(0.2)

    print()
    print("Web server started")

    return server


# ==================================================
# Handle Web Request
# ==================================================

def handle_request(client):

    try:

        request = client.recv(4096)

        if not request:

            client.close()

            return

        request = request.decode(
            "utf-8"
        )

        first_line = request.split(
            "\r\n"
        )[0]

        print(
            "Request:",
            first_line
        )

        # ==========================================
        # Login Page
        # ==========================================

        if first_line.startswith(
            "GET / "
        ):

            client.send(
                login_page()
            )

        # ==========================================
        # Login
        # ==========================================

        elif first_line.startswith(
            "POST /login"
        ):

            if (
                "userid=PAN111"
                in request
                and
                "pwd=PAN222"
                in request
            ):

                response = (
                    "HTTP/1.1 302 Found\r\n"
                    "Location: /serverIndex\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )

                client.send(response)

            else:

                response = (
                    "HTTP/1.1 401 Unauthorized\r\n"
                    "Content-Type: text/plain\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    "Wrong username or password"
                )

                client.send(response)

        # ==========================================
        # OTA Page
        # ==========================================

        elif first_line.startswith(
            "GET /serverIndex"
        ):

            client.send(
                ota_page()
            )

        # ==========================================
        # Manual OTA Check
        # ==========================================

        elif first_line.startswith(
            "POST /check"
        ):

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Connection: close\r\n"
                "\r\n"
                "Version check started. "
                "See Thonny Shell."
            )

            client.send(response)

            client.close()

            check_for_update()

            return

        # ==========================================
        # Other
        # ==========================================

        else:

            client.send(
                not_found_page()
            )

    except Exception as error:

        print(
            "Web error:",
            error
        )

    finally:

        try:

            client.close()

        except:

            pass


# ==================================================
# MAIN
# ==================================================

print()
print("==============================")
print(" ESP32 MicroPython")
print(" GitHub OTA System")
print(" Version:", CURRENT_VERSION)
print("==============================")
print()


# -----------------------------
# WiFi
# -----------------------------

wlan = connect_wifi()


# -----------------------------
# Web Server
# -----------------------------

server = start_server()


# -----------------------------
# OTA timer
# -----------------------------

last_ota_check = time.time()


# -----------------------------
# Startup OTA Check
# -----------------------------

check_for_update()


# ==================================================
# Main Loop
# ==================================================

while True:

    try:

        # -------------------------
        # Web Server
        # -------------------------

        try:

            client, address = server.accept()

            print(
                "Client:",
                address
            )

            handle_request(client)

        except OSError:

            pass

        # -------------------------
        # OTA timer
        # -------------------------

        if (
            time.time()
            -
            last_ota_check
            >=
            OTA_INTERVAL
        ):

            last_ota_check = time.time()

            check_for_update()

        time.sleep(0.01)

    except Exception as error:

        print(
            "Main error:",
            error
        )

        time.sleep(2)
"""
MicroPython Script for XBee 3 Modules

Description:
    This script is designed to receive data from the XBee Transmitter (Tx)
    and parse it for further processing. It is specifically tailored for use
    with XBee 3 Modules running the 802.15.4 firmware.

Author: Anway Pimpalkar
Date: 03/05/2026
"""

import xbee
import utime
from parse_string import parse_string
from sys import stdin, stdout

# Unique ID for each robot
ROBOT_ID = "BA"

# Parsing parameters
startLen = 1
timeLen = 4
robotIDLen = 2
coordLen = 3
angleLen = 3

parsingParameters = [startLen, timeLen, robotIDLen, coordLen, angleLen]

lastDataTime = 0
timeout = 1000
last_payload = None

while True:
    payload = xbee.receive()

    if payload:
        last_payload = payload
        lastDataTime = utime.ticks_ms()

    data = stdin.buffer.read()

    if data:
        nowTime = utime.ticks_ms()

        if utime.ticks_diff(nowTime, lastDataTime) > timeout:
            last_payload = None

        try:
            decoded_data = data.decode()
        except Exception:
            decoded_data = ""

        if "?" in decoded_data:
            if last_payload is None:
                stdout.buffer.write("?,????,---,---\n".encode())
                continue

            try:
                receivedMsg = last_payload["payload"].decode("utf-8")

                if not receivedMsg:
                    stdout.buffer.write("?,????,---,---\n".encode())
                    continue

                start = receivedMsg.find(">")
                end = receivedMsg.find(";")

                if start == -1 or end == -1 or end <= start:
                    stdout.buffer.write("?,????,---,---\n".encode())
                    continue

                string = receivedMsg[start:end + 1]
                parsedDict = parse_string(string, parsingParameters)

                matchTime = parsedDict.get("time", "9" * timeLen)
                matchBit = parsedDict.get("matchbit", "9")
                robotCoords = parsedDict.get(
                    ROBOT_ID,
                    "9" * (coordLen * 2) + "9" * angleLen
                )

                out = matchTime + "," + matchBit + "," + robotCoords + "\n"
                stdout.buffer.write(out.encode())

            except Exception:
                stdout.buffer.write("?,????,---,---\n".encode())
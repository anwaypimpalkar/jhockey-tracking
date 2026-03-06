"""
MicroPython Script for XBee 3 Modules

Description:
    This script is designed to receive data from the Xbee Transmitter (Tx) and parse it for further processing. It is specifically tailored for use with XBee 3 Modules running the 802.15.4 firmware.

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

# Store the parameters (Start Length, Time Length, Robot ID Length, Coordinate Length, Angle Length) in a list
parsingParameters = [startLen, timeLen, robotIDLen, coordLen, angleLen]

lastDataTime = 0
nowTime = 0
timeout = 1000

# Variable to store the last payload received
last_payload = None

while True:
    # Check if there is any data to be received in a non-blocking way
    payload = xbee.receive()

    # If there is data, store it in last_payload
    if payload:
        last_payload = payload

    # Read data from stdin
    data = stdin.buffer.read()

    # If data is received, start processing it
    if data:
        nowTime = utime.ticks_ms()

        if utime.ticks_diff(nowTime, lastDataTime) > timeout:
            last_payload = None

        if b"?" in data:
            if last_payload is not None:
                # Decode the payload
                receivedMsg = last_payload["payload"].decode("utf-8")

                # If the payload is not empty, parse it
                if receivedMsg:
                    # Find the start and end of the payload
                    start = receivedMsg.find(">")
                    end = receivedMsg.find(";") + 1

                    # If the start and end are found, parse the payload
                    if start != -1 and end != 0:
                        # Extract the string from the payload
                        string = receivedMsg[start:end]

                        # Parse the string
                        parsedDict = parse_string(string, parsingParameters)

                        # Get match time if available, otherwise default
                        if "time" in parsedDict:
                            matchTime = parsedDict["time"]
                        else:
                            matchTime = "9" * timeLen

                        # Get match bit if available, otherwise default
                        if "matchbit" in parsedDict:
                            matchBit = parsedDict["matchbit"]
                        else:
                            matchBit = "9"

                        # Get robot coordinates if available, otherwise default
                        if ROBOT_ID in parsedDict:
                            robotCoords = parsedDict[ROBOT_ID]
                        else:
                            robotCoords = "9" * (coordLen * 2) + "9" * angleLen

                        # Create output string for stdout (Arduino/UART interface)
                        out = matchTime + "," + matchBit + "," + robotCoords + "\n"

                        # Write the output string to stdout
                        stdout.buffer.write(out.encode())

                        lastDataTime = utime.ticks_ms()
                    else:
                        out = "?,????,999999999\n"
                        stdout.buffer.write(out.encode())
            else:
                out = "no active tx found\n"
                stdout.buffer.write(out.encode())
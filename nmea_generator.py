#!/usr/bin/env python3

import datetime
import polyline
import requests
import argparse
import sys


def to_nmea_coord(degree, is_lat):
    """Convert decimal degrees to NMEA format (DDMM.MMMM)."""
    d = int(abs(degree))
    m = (abs(degree) - d) * 60.0
    direction = ""
    if is_lat:
        direction = 'N' if degree > 0 else 'S'
        return f"{d:02d}{m:07.4f},{direction}"
    else:
        direction = 'E' if degree > 0 else 'W'
        return f"{d:03d}{m:07.4f},{direction}"

def calculate_checksum(sentence):
    """Calculate the required NMEA XOR checksum."""
    calc_cksum = 0
    for s in sentence:
        calc_cksum ^= ord(s)
    return f"{calc_cksum:02X}"

def get_route_geometry(start_coords, end_coords):
    url = f"http://server:5000/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data["code"] != "Ok":
            return None

        encoded_geometry = data['routes'][0]['geometry']
        distance = data['routes'][0]['distance']
        duration = data['routes'][0]['duration']
        return polyline.decode(encoded_geometry), distance, duration

    except requests.RequestException as e:
        raise ConnectionError(f"Connection error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NMEA generator from a route (uses a local routing server)")

    parser.add_argument(
        "--cinit",
        nargs=2,
        type=float,
        default=[38.99062542667815, -3.920149267107538],
        metavar=("LAT", "LON"),
        help=(
            "Initial coordinates: LAT LON "
            "(default: 38.99062542667815 -3.920149267107538)"
        ),
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cend", nargs=2, type=float, metavar=("LAT","LON"),
                       help="Destination coordinates: LAT LON")
    group.add_argument("--cityend", choices=["BILBAO", "MADRID"],
                       help="Destination by city (BILBAO or MADRID)")

    args = parser.parse_args()

    start_coords = (args.cinit[0], args.cinit[1])

    if args.cend:
        end_coords = (args.cend[0], args.cend[1])
    elif args.cityend:
        if args.cityend == "BILBAO":
            end_coords = (43.262873, -2.947564)
        else:  # MADRID
            end_coords = (40.451843, -3.686502)

    try:
        route_result = get_route_geometry(start_coords, end_coords)
        if route_result is None:
            print("Error: routing API returned an invalid result.")
            sys.exit(1)
        coordinates, distance, duration = route_result
    except ConnectionError as e:
        print(f"Connection error: {e}")
        sys.exit(1)

    start_time = datetime.datetime.now(datetime.timezone.utc)

    for i, (lat, lon) in enumerate(coordinates):
        current_time = start_time + datetime.timedelta(seconds=i)
        time_str = current_time.strftime("%H%M%S")

        lat_nmea = to_nmea_coord(lat, True)
        lon_nmea = to_nmea_coord(lon, False)

        body = f"GPGGA,{time_str},{lat_nmea},{lon_nmea},1,08,0.9,545.4,M,46.9,M,,"

        checksum = calculate_checksum(body)
        nmea_sentence = f"${body}*{checksum}"

        with open("route.nmea", "a") as f:
            f.write(nmea_sentence + "\n")

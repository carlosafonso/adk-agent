#!/usr/bin/env
import json
import logging
import os
from typing import Any, Dict, List

import googlemaps
import requests
from fastmcp import FastMCP
from mobilitylabs.busemtmad import BusEMTMad
from mobilitylabs.bicimad import BiciMad


def error_response(reason: str | None) -> Dict[str, str | None]:
    return {"status": "error", "reason": reason}


def success_response(data: any) -> Dict[str, any]:
    return {"status": "success", "data": data}


class EnhancedBiciMad(BiciMad):
    def info_bike_stations_around_lng_lat(self, lng: float, lat: float, radius: int):
        url = "%s/transport/bicimad/stations/arroundxy/%s/%s/%s/" % (
            self.MLURL, lng, lat, radius)
        headers = {'accessToken': self._access_token}
        resp = requests.get(url, headers=headers)

        if resp.status_code == 200:
            logging.debug("Info of bike stations retrieved: %s" %
                          resp.json()['data'])
        return resp.json()['data']

        logging.error("Unable to retrieve the list of bike stations with code '%s' and message: %s" %
                      (resp.status_code, resp.reason))
        return None


def normalize_bike_station_info(station_data) -> Dict[str, any]:
    return {
        "id": station_data["id"],
        "number": station_data["number"],
        "name": station_data["name"],
        "address": station_data["address"],
        "total_slots": station_data["total_bases"],
        "occupied_slots": station_data["dock_bikes"],
        "free_slots": station_data["free_bases"],
        "operational": station_data["activate"] == 1,
    }


class EmtMadridMcpToolset:
    def __init__(self, emt_client: BusEMTMad):
        # self.__gmaps_client = gmaps_client
        self.__emt_client = emt_client

    def get_current_incidents(self):
        results = self.__emt_client.issues("all")

        if results is not None:
            return success_response(results)

        return error_response("API returned an error")


class BicimadMcpToolset:
    def __init__(self, gmaps_client: googlemaps.Client, bicimad: EnhancedBiciMad):
        self.__gmaps_client = gmaps_client
        self.__bicimad = bicimad

    def get_closest_bike_station_to_coordinates(self, latitude: float, longitude: float) -> Dict[str, Any]:
        results = self.__bicimad.info_bike_stations_around_lng_lat(
            longitude,
            latitude,
            500
        )

        if results is not None:
            return success_response(list(map(normalize_bike_station_info, results)))

        return error_response("API returned an error")

    def get_closest_bike_stations_to_address(self, address: str) -> Dict[str, Any]:
        geocoded_address = self.__gmaps_client.geocode(
            address=address,
            region="es",
            language="es"
        )

        if (len(geocoded_address)) < 1:
            return error_response("Could not geocode address")

        return self.get_closest_bike_station_to_coordinates(
            geocoded_address[0]["geometry"]["location"]["lat"],
            geocoded_address[0]["geometry"]["location"]["lng"],
        )

    def get_bike_station_info(self, station_id: int) -> Dict[str, Any]:
        results = self.__bicimad.info_bike_station(station_id)

        if results is not None:
            return success_response(normalize_bike_station_info(results[0]) if len(results) else [])

        return error_response("API returned an error")

    # def get_bike_info(self, bike_id: int) -> Dict[str, Any]:
    #     return {
    #         "at_station": 1,
    #         "battery_percentage": 96,
    #     }


def init_server():
    logging.basicConfig(level=logging.INFO)

    if "EMT_API_ACCESS_TOKEN" in os.environ:
        logging.info(
            "BiciMad API provided creds is access token. Will skip log in.")

        client_id = ""
        passkey = ""
        bicimad_client = EnhancedBiciMad(x_client_id="", pass_key="")
        bicimad_client._access_token = os.environ["EMT_API_ACCESS_TOKEN"]
    elif "EMT_API_CLIENT_ID" in os.environ and "EMT_API_PASSKEY" in os.environ:
        logging.info(
            "BiciMad API provided creds are Client ID and passkey. Will log in.")

        bicimad_client = EnhancedBiciMad(
            x_client_id=os.environ["EMT_API_CLIENT_ID"],
            pass_key=os.environ["EMT_API_PASSKEY"]
        )
        bicimad_client.log_in()

        emt_client = BusEMTMad(
            x_client_id=os.environ["EMT_API_CLIENT_ID"],
            pass_key=os.environ["EMT_API_PASSKEY"]
        )
        emt_client.log_in()
    else:
        raise Exception("No BiciMad API credentials available in env vars.")

    if "GOOGLE_MAPS_API_KEY" not in os.environ:
        raise Exception("No Google Maps API key present in env vars.")

    logging.info("Using API maps key {}".format(
        os.environ["GOOGLE_MAPS_API_KEY"])
    )

    bicimad_ts = BicimadMcpToolset(
        gmaps_client=googlemaps.Client(key=os.environ["GOOGLE_MAPS_API_KEY"]),
        bicimad=bicimad_client,
    )
    emt_ts = EmtMadridMcpToolset(emt_client=emt_client)

    mcp = FastMCP(
        "EMT Madrid API",
        instructions="This server allows interacting with the API of Madrid's municipal transportation authority (EMT). Includes access to information related to BiciMad (Madrid's municipal bike rental service) and Madrid's bus network."
    )

    mcp.tool(
        bicimad_ts.get_closest_bike_stations_to_address,
        description="Returns a list of the closest BiciMad bike stations to the provided address."
    )
    mcp.tool(
        bicimad_ts.get_bike_station_info,
        description="Returns information about a BiciMad bike station."
    )
    # mcp.add_tool(
    #     ts.get_bike_info,
    #     description="Returns information about an individual bike."
    # )

    mcp.tool(
        emt_ts.get_current_incidents,
        description="Returns a list of current incidents in Madrid's bus network."
    )

    return mcp


if __name__ == "__main__":
    mcp = init_server()

    port = int(os.environ.get("PORT", "8000"))

    # mcp.run()  # Default: uses STDIO transport
    mcp.run(transport="http", host="0.0.0.0", port=port)

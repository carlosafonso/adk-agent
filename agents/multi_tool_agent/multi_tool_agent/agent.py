import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent


def get_airports_in_city(city: str) -> dict:
    """Retrieves a list of airport codes for a given city.

    Args:
        city (str): The name of the city for which to retrieve airports.

    Returns:
        dict: status and list of IATA codes or error message.
    """
    normalized_city_name = city.lower().strip()
    if normalized_city_name == "new york":
        return {
            "status": "success",
            "airport_codes": ["JFK", "LGA", "EWR"],
        }
    if normalized_city_name == "london":
        return {
            "status": "success",
            "airport_codes": ["LHR", "LCY", "STN"],
        }
    if normalized_city_name == "madrid":
        return {
            "status": "success",
            "airport_codes": ["MAD"],
        }
    if normalized_city_name == "barcelona":
        return {
            "status": "success",
            "airport_codes": ["BCN"],
        }

    return {
        "status": "error",
        "error_message": f"No airports found for '{city}'.",
    }


def get_flights(origin_iata_code: str, destination_iata_code: str) -> dict:
    """Retrieves a list of flights between the given origin and destination airports.

    Args:
        origin_iata_code (str): The IATA code of the origin airport.
        destination_iata (str): The IATA code of the destination airport.

    Returns:
        dict: status and list of flights or error message.
    """
    flights = [
        ("Iberia", "IBE1923", "LHR", "JFK"),
        ("American Airlines", "AAL88", "LHR", "EWR"),
        ("British Airways", "BAW553", "JFK", "LHR"),
        ("Vueling", "VYG99", "MAD", "BCN"),
        ("Vueling", "VYG98", "BCN", "MAD"),
    ]

    filtered = filter(
        lambda f: f[2] == origin_iata_code and f[3] == destination_iata_code, flights
    )
    normalized = map(
        lambda f: {
            "airline": f[0],
            "flight_number": f[1],
            "origin": f[2],
            "destination": f[3]
        },
        filtered
    )

    results = list(normalized)
    if len(results) > 0:
        return {"status": "success", "flights": results}

    return {"status": "error", "error_message": f"No flights found between '{origin_iata_code}' and '{destination_iata_code}'."}


def get_flight_fares(flight_number: str) -> dict:
    """Retrieves the fares for a given flight.

    Args:
        flight_number (str): The flight number for which to retrieve fares.

    Returns:
        dict: status and list of fares or error message.
    """
    fares = [
        {"id": "1234", "name": "Economy SupaSave",
            "price": "613.00", "currency": "USD"},
        {"id": "5678", "name": "Premium Economy",
            "price": "863.00", "currency": "USD"},
        {"id": "9012", "name": "Business", "price": "1821.00", "currency": "USD"},
        {"id": "3456", "name": "Saudi Royalty",
            "price": "4399", "currency": "USD"},
    ]
    return {"status": "success", "fares": fares}


def book_flight(flight_number: str, fare_id: str) -> dict:
    """Books a flight with the given flight number.

    Args:
        flight_number (str): The flight number to book.
        fare_id (str): The ID of the fare to book.


    Returns:
        dict: status and confirmation ID of the booking or error message.
    """
    return {"status": "success", "confirmation_id": "C-1982-W1"}


flight_booking_agent = Agent(
    name="flight_booking_agent",
    model="gemini-2.5-flash-lite",
    description=(
        "Agent to help users book flights."
    ),
    instruction=(
        """You are a helpful agent who can help users book flights.

If a user wants to book a flight, do the following in order:
1. Ask for departure and destination cities.
2. Use the `get_airports_in_city` tool to retrieve IATA codes of the arirpots in each city.
3. Use the `get_flights` tool to find flights between the airports. Consider all airports in each city.
4. Ask the user to select which flight they would like to book.
5. Use the `get_flight_fares` tool to retrieve the fares for the selected flight.get_flight_fares
6. Ask the user to select which fare they would like to book.
7. Use the `book_flight` tool to book the flight and fare selected by the user, and provide the confirmation ID to the user.

Otherwise inform the user that their request cannot be fulfilled."""
    ),
    tools=[get_airports_in_city, get_flights, get_flight_fares, book_flight],
)

root_agent = Agent(
    name="travel_agent",
    model="gemini-2.5-flash-lite",
    description=(
        "Agent to help users booking travel reservations and flights."
    ),
    instruction=(
        """You are a helpful agent who can help users book travel reservations and flights.

* Delegate flight booking requests to `flight_booking_agent`.

For any other request, inform the user that their request cannot be fulfilled."""
    ),
    sub_agents=[flight_booking_agent],
    # tools=[],
)

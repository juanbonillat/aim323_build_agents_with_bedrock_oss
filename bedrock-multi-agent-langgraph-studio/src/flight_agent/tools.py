from datetime import datetime, timedelta
from contextlib import closing
import json
import random
import sqlite3
import pandas as pd
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig


def read_travel_data(file_path: str = "/app/src/destination_agent/synthetic_travel_data.csv") -> pd.DataFrame:
    """Read travel data from CSV file"""
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        return pd.DataFrame(
            columns=[
                "Id",
                "Name",
                "Current_Location",
                "Age",
                "Past_Travel_Destinations",
                "Number_of_Trips",
                "Flight_Number",
                "Departure_City",
                "Arrival_City",
                "Flight_Date",
            ]
        )


@tool
def search_flights(config: RunnableConfig, arrival_city: str, date: str = None) -> str:
    """
    Use this tool to search for flights between two cities. It knows the user's departure city

    Args:
        arrival_city (str): The city of arrival
        date (str, optional): The date of the flight in YYYY-MM-DD format. If not provided, defaults to 7 days from now.

    Returns:
        str: A formatted string containing flight information including airline, departure time, arrival time, duration, and price for multiple flights.
    """

    df = read_travel_data()
    user_id = config.get("configurable", {})["configurable"]["user_id"]
    print(user_id)

    if user_id not in df["Id"].values:
        return "User not found in the travel database."

    user_data = df[df["Id"] == user_id].iloc[0]
    current_location = user_data["Current_Location"]

    departure_city = current_location.capitalize()
    arrival_city = arrival_city.capitalize()

    if date is None:
        date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    # Generate mock flight data
    num_flights = random.randint(2, 5)
    airlines = ["AirEurope", "SkyWings", "TransContinental", "EuroJet", "GlobalAir"]
    flights = []

    for _ in range(num_flights):
        airline = random.choice(airlines)
        duration = timedelta(minutes=2)
        price = random.randint(100, 400)
        departure_time = datetime.strptime(date, "%Y-%m-%d") + timedelta(
            hours=random.randint(0, 23), minutes=random.randint(0, 59)
        )
        arrival_time = departure_time + duration

        flights.append(
            {
                "airline": airline,
                "departure": departure_time.strftime("%H:%M"),
                "arrival": arrival_time.strftime("%H:%M"),
                "duration": str(duration),
                "price": price,
            }
        )

    # Format the results

    flight_data = {
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "date": date,
        "flights": [],
    }
    for i, flight in enumerate(flights, 1):
        flight_info = {
            "flight_number": i,
            "airline": flight["airline"],
            "departure": flight["departure"],
            "arrival": flight["arrival"],
            "duration": str(flight["duration"]),
            "price": flight["price"],
        }
        flight_data["flights"].append(flight_info)

    return json.dumps(flight_data) + " FINISHED"


@tool
def retrieve_flight_booking(booking_id: int) -> str:
    """
    Retrieve a flight booking by ID

    Args:
        booking_id (int): The unique identifier of the booking to retrieve

    Returns:
        str: A string containing the booking information if found, or a message indicating no booking was found
    """
    booking = None
    with closing(sqlite3.connect("data/travel_bookings.db", timeout=10.0)) as conn:
        with closing(conn.cursor()) as cursor:
            # Execute the query to retrieve the booking
            cursor.execute(
                "SELECT * FROM flight_bookings WHERE booking_id = ?", (booking_id,)
            )
            booking = cursor.fetchone()
        # Close the connection
        conn.close()

    if booking:
        return f"Booking found: {booking} FINISHED"
    else:
        return f"No booking found with ID: {booking_id} FINISHED"


@tool
def change_flight_booking(booking_id: int, new_date: str) -> str:
    """
    Change the date of a flight booking

    Args:
        booking_id (int): The unique identifier of the booking to be changed
        new_date (str): The new date for the booking

    Returns:
        str: A message indicating the result of the booking change operation
    """
    # conn = sqlite3.connect("data/travel_bookings.db")
    # cursor = conn.cursor()
    result = ""
    with closing(sqlite3.connect("data/travel_bookings.db", timeout=10.0)) as conn:
        with closing(conn.cursor()) as cursor:
            # Execute the query to update the booking date
            cursor.execute(
                "UPDATE flight_bookings SET departure_date = ? WHERE booking_id = ?",
                (new_date, booking_id),
            )
            conn.commit()

            # Check if the booking was updated
            if cursor.rowcount > 0:
                result = f"Booking updated with ID: {booking_id}, new date: {new_date} FINISHED"
            else:
                result = f"No booking found with ID: {booking_id} FINISHED"

        # Close the connection
        conn.close()

    return result


@tool
def cancel_flight_booking(booking_id: int) -> str:
    """
    Cancel a flight booking. If the task complete, reply with "FINISHED"

    Args:
        booking_id (str): The unique identifier of the booking to be cancelled

    Returns:
        str: A message indicating the result of the booking cancellation operation

    """
    # conn = sqlite3.connect("data/travel_bookings.db")
    # cursor  = conn.cursor()
    result = ""
    with closing(sqlite3.connect("data/travel_bookings.db", timeout=10.0)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "DELETE FROM flight_bookings WHERE booking_id = ?", (booking_id,)
            )
            conn.commit()
            # Check if the booking was deleted
            if cursor.rowcount > 0:
                result = f"Booking canceled with ID: {booking_id} FINISHED"
            else:
                result = f"No booking found with ID: {booking_id} FINISHED"

        # Close the connection
        conn.close()

    return result

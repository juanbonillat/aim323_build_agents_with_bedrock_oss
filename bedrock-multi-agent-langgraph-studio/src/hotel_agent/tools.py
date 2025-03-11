from datetime import datetime, timedelta
from contextlib import closing
import random
import sqlite3
from langchain_core.tools import tool


@tool
def suggest_hotels(city: str, checkin_date: str) -> dict:
    """
    Use this tool to search for hotels in these cities

    Args:
        city (str): The name of the city to search for hotels
        checkin_date (str): The check-in date in YYYY-MM-DD format

    Returns:
        dict: A dictionary containing:
            - hotel (str): Name of the hotel in specified city
            - checkin_date (str): The provided check-in date
            - checkout_date (str): A randomly generated checkout date
            - price (int): A randomly generated price for the stay
    """
    hotels = {
        "New York": ["Hotel A", "Hotel B", "Hotel C"],
        "Paris": ["Hotel D", "Hotel E", "Hotel F"],
        "Tokyo": ["Hotel G", "Hotel H", "Hotel I"],
    }

    # Generate random checkout date and price
    checkin = datetime.strptime(checkin_date, "%Y-%m-%d")
    checkout = checkin + timedelta(days=random.randint(1, 10))
    price = random.randint(100, 500)

    hotel_list = hotels.get(city, ["No hotels found"])
    return {
        "hotel": "City Hotel " + city,
        "checkin_date": checkin_date,
        "checkout_date": checkout.strftime("%Y-%m-%d"),
        "price": price,
    }


@tool
def retrieve_hotel_booking(booking_id: int) -> str:
    """
    Retrieve a hotel booking by ID

    Args:
        booking_id (int): The unique identifier of the hotel booking to retrieve

    Returns:
        str: A string containing the hotel booking information if found, or a message indicating no booking was found
    """
    with closing(sqlite3.connect("./data/travel_bookings.db", timeout=10.0)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM hotel_bookings WHERE booking_id=?", (booking_id,)
            )
            booking = cursor.fetchone()

    if booking:
        return f"Booking found: {booking}"
    else:
        return f"No booking found with ID: {booking_id}"


@tool
def change_hotel_booking(
    booking_id: int, new_checkin_date: str = None, new_checkout_date: str = None
) -> str:
    """
    Change the dates of a hotel booking in the database. If the task completes, reply with "FINISHED"

    Args:
    booking_id (int): The unique identifier of the booking to be changed
    new_checkin_date (str, optional): The new check-in date in YYYY-MM-DD format
    new_checkout_date (str, optional): The new check-out date in YYYY-MM-DD format

    Returns:
    str: A message indicating the result of the booking change operation
    """

    with closing(sqlite3.connect("./data/travel_bookings.db", timeout=10.0)) as conn:
        with closing(conn.cursor()) as cursor:
            try:
                # First, fetch the current booking details
                cursor.execute(
                    """
                    SELECT * FROM hotel_bookings WHERE booking_id = ?
                """,
                    (booking_id,),
                )

                booking = cursor.fetchone()

                if booking is None:
                    return f"No hotel booking found with ID: {booking_id}"

                # Unpack the booking details
                (
                    _,
                    user_id,
                    user_name,
                    city,
                    hotel_name,
                    check_in_date,
                    check_out_date,
                    nights,
                    price_per_night,
                    total_price,
                    num_guests,
                    room_type,
                ) = booking

                # Update check-in and check-out dates if provided
                if new_checkin_date:
                    check_in_date = new_checkin_date
                if new_checkout_date:
                    check_out_date = new_checkout_date

                # Recalculate nights and total price
                checkin = datetime.strptime(check_in_date, "%Y-%m-%d")
                checkout = datetime.strptime(check_out_date, "%Y-%m-%d")
                nights = (checkout - checkin).days
                total_price = nights * price_per_night

                # Update the booking in the database
                cursor.execute(
                    """
                    UPDATE hotel_bookings
                    SET check_in_date = ?, check_out_date = ?, nights = ?, total_price = ?
                    WHERE booking_id = ?
                """,
                    (check_in_date, check_out_date, nights, total_price, booking_id),
                )

                conn.commit()

                return f"Hotel booking updated: Booking ID {booking_id}, New check-in: {check_in_date}, New check-out: {check_out_date}, Nights: {nights}, Total Price: {total_price} FINISHED"

            except sqlite3.Error as e:
                conn.rollback()
                return f"An error occurred: {str(e)} Booking ID {booking_id}, New check-in: {check_in_date} FINISHED"

            finally:
                pass


@tool
def cancel_hotel_booking(booking_id: int) -> str:
    """
    Cancel a hotel booking. If the task completes, reply with "FINISHED"

    Args:
        booking_id (int): The unique identifier of the booking to be cancelled

    Returns:
        str: A message indicating the result of the booking cancellation operation
    """
    with closing(sqlite3.connect("./data/travel_bookings.db", timeout=10.0)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "DELETE FROM hotel_bookings WHERE booking_id = ?", (booking_id,)
            )
            conn.commit()

            # Check if the booking was deleted
            if cursor.rowcount > 0:
                return f"Booking canceled with ID: {booking_id} FINISHED"
            else:
                return f"No booking found with ID: {booking_id} FINISHED"

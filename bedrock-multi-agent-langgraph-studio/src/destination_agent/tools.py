import pandas as pd
from collections import Counter
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig


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
def compare_and_recommend_destination(config: RunnableConfig) -> str:
    """This tool is used to check which destinations user has already traveled.
    Use the user id to fetch the information about the user.
    If user has already been to a city then do not recommend that city.

    Returns:
        str: Destination to be recommended.

    """

    df = read_travel_data()
    print(f"config: {config}")
    user_id = config.get("configurable", {})["configurable"]["user_id"]
    print(user_id)

    if user_id not in df["Id"].values:
        return "User not found in the travel database."

    user_data = df[df["Id"] == user_id].iloc[0]
    current_location = user_data["Current_Location"]
    age = user_data["Age"]
    past_destinations = user_data["Past_Travel_Destinations"].split(", ")

    # Get all past destinations of users with similar age (±5 years) and same current location
    similar_users = df[
        (df["Current_Location"] == current_location)
        & (df["Age"].between(age - 5, age + 5))
    ]
    all_destinations = [
        dest
        for user_dests in similar_users["Past_Travel_Destinations"].str.split(", ")
        for dest in user_dests
    ]

    # Count occurrences of each destination
    destination_counts = Counter(all_destinations)

    # Remove user's current location and past destinations from recommendations
    for dest in [current_location] + past_destinations:
        if dest in destination_counts:
            del destination_counts[dest]

    if not destination_counts:
        return f"No new recommendations found for users in {current_location} with similar age."

    # Get the most common destination
    recommended_destination = destination_counts.most_common(1)[0][0]

    return f"Based on your current location ({current_location}), age ({age}), and past travel data, we recommend visiting {recommended_destination}."

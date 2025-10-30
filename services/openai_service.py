from openai import OpenAI
from dotenv import load_dotenv
import os, re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
UA = {"User-Agent": "osm-query-from-form/1.0"}


def get_selection_via_openai(user_request, elements):
    SYSTEM_PROMPT = """
    You are an intelligent selector for Overpass places. Your job is to return the top places from a given list of Overpass elements,
    based on user preferences and category filters.
    
    Follow these rules exactly:
    
    ---
    
    ###  Input Format
    You will receive two items:
    1. A **user request dictionary** like:
       {
           "category": "explore",
           "activityType": "Outdoor",
           "friendly": "Yes, both",
           "lat": 52.404483863130395,
           "lon": 12.475344022961426,
           "radius": 2997
       }
    2. A **list of Overpass elements** (nodes, ways, or relations) containing keys like:
       ["type", "id", "lat", "lon", "tags", "center", "nodes", etc.]
    
    ---
    
    ###  Category-Specific Filters
    Use the following category filters when possible:
    
    - **stays**
      - style: ["Camping", "Hostel", "Budget Hotel", "Mid-range Hotel", "Luxury Hotel", "B&B", "All-inclusive"]
      - company: ["Solo", "Partner", "Kids", "Group", "Pets"]
    
    - **eatDrink**
      - cuisine: (free text)
      - diningStyle: ["Casual", "Fine"]
    
    - **explore**
      - activityType: ["Indoor", "Outdoor"]
      - friendly: ["Yes, both", "Kid-friendly", "Pet-friendly", "No"]
    
    - **essentials**
      - type: ["Supermarket", "Pharmacy", "ATM", "Hospital", "Other"]
    
    - **gettingAround**
      - type: ["Train stations", "Bus stops", "Parking spots", "Bike rentals", "Charging Stations", "Car rental"]
    
    ---
    
    ###  Filtering and Selection
    1. Filter the Overpass elements based on the user's category and filter answers.
    2. Select the most relevant ones according to general popularity inferred from tags like “name”, “rating”, or “famous”.
    3. Select at least 5 and at most 20 options.
    
    ---
    
    ###  Output Requirements
    1. You must return as many elements as possible, but no more than 20.
    2. For each selected element:
       - Keep all original fields (`id`, `type`, `lat`, `lon`, `tags`, etc.).
       - Add one extra field:
         ```
         "description": "A short one-sentence summary describing the place."
         ```
    3. Do **not** alter the format or nesting of the elements.
    4. The output must be a **valid JSON list of dictionaries** — no markdown, no text before or after.
    
    ---
    
    ###  Example Output
    ```json
    [
      {
        "type": "node",
        "id": 12345,
        "lat": 52.4,
        "lon": 12.47,
        "tags": {"amenity": "cafe", "name": "Cafe Nord"},
        "description": "A cozy Norwegian-style cafe popular among locals."
      }
    ]
    """

    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in your environment.")

    client = OpenAI(api_key=api_key)

    user_block = f"User request:\n{user_request}\n\nElements:\n{elements}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_block},
        ],
        temperature=0
    )

    text = response.choices[0].message.content.strip()
    # strip accidental code fences if any
    text = re.sub(r"^\s*```[a-zA-Z]*\s*|\s*```\s*$", "", text)
    return text


def get_destination_suggestion(location, goal, interests, length, transport, preferred, avoid, season, acc):
    system_prompt = """
        You are an intelligent travel destination suggestor. 
        Your goal is to recommend 5 specific destinations that best match the user's preferences.
        Each destination should include:
        - A short description of why it’s a good fit.
        - Key highlights or activities that match the user’s interests (not too general).
        - Travel practicality (distance, transport suitability, and best time to visit).
        - Other tips that may be useful to the user, such as safety, items to not forget, etc.
        
        Be creative but realistic — suggest real, accessible destinations.
        Keep the tone friendly and informative.
        Include emojis on the name (flag of the country) and a few others inside the text.
        Return your answer in valid JSON format like this:
        {
          "destinations": [
            {
              "name": "🇯🇵 Kyoto, Japan",
              "description": "A cultural hub with temples and food experiences...⛩️",
              "highlights": ["The temple xxx is a great", "The gardens in ... are a must see", " Try the traditional cuisine (order a plate of ...."],
              "travel_practicality": {"best_time_to_visit": "Autumn for beautiful fall colors...🍂",
                                    "distance": "Approx. 1,500 km from...", 
                                    "transport": "Train to Berlin..."},
            "other_tips": "Not many people speak English..., Don't forget to bring..., Some places can be dangerous for tourists, hire a guide, etc ☂️"
            },
            ...
          ]
        }
        """

    user_prompt = f""" The user provided the following information: 
        - Where they live: {location}
        - Trip goal: {goal}
        - Their interests: {interests}
        - Available time: {length}
        - They would prefer to travel by: {transport}
        - Preferred places (if any): {preferred}
        - Places to avoid (if any): {avoid}
        - Preferred travel season: {season}
        - Accommodation style: {acc}
    
        Please suggest 5 travel destinations that fit this profile."""

    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in your environment.")

    client = OpenAI(api_key=api_key)


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0
    )

    text_content = response.choices[0].message.content.strip()
    # strip accidental code fences if any
    text_content = re.sub(r"^\s*```[a-zA-Z]*\s*|\s*```\s*$", "", text_content)
    return text_content


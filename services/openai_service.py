from openai import OpenAI
from dotenv import load_dotenv
import os, re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
UA = {"User-Agent": "osm-query-from-form/1.0"}

SYSTEM_PROMPT = """
You are an intelligent selector for Overpass places. Your task is to choose the top 5 places from a given list 
based on relevance, ratings, and user-provided filters.

Important rules:

1. You will receive a user request structured as a dictionary, including:
   - "category": one of ["stays", "eatDrink", "explore", "essentials", "gettingAround"]
   - Additional keys corresponding to the user's answers for that category. Example:

   {
       "category": "explore",
       "activityType": "Outdoor",
       "friendly": "Yes, both",
       "lat": 52.404483863130395,
       "lon": 12.475344022961426,
       "radius": 2997
   }

2. The category-specific questions and answers to apply as filters are:

   - "stays":
       1. Question: "What accommodation style are you looking for?"
          Key: "style"
          Answers: ["Camping", "Hostel", "Budget Hotel", "Mid-range Hotel", "Luxury Hotel", "B&B", "All-inclusive"]
       2. Question: "Who are you traveling with?"
          Key: "company"
          Answers: ["Solo", "Partner", "Kids", "Pets"]

   - "eatDrink":
       1. Question: "What type of cuisine are you interested in?"
          Key: "cuisine"
          Answers: free text
       2. Question: "Do you prefer casual or fine dining?"
          Key: "diningStyle"
          Answers: ["Casual", "Fine"]

   - "explore":
       1. Question: "Do you prefer indoor or outdoor?"
          Key: "activityType"
          Answers: ["Indoor", "Outdoor"]
       2. Question: "Should it be kid-friendly or pet-friendly?"
          Key: "friendly"
          Answers: ["Yes, both", "Kid-friendly", "Pet-friendly", "No"]

   - "essentials":
       1. Question: "What type of essential do you need?"
          Key: "type"
          Answers: ["Supermarket", "Pharmacy", "ATM", "Hospital", "Other"]

   - "gettingAround":
       1. Question: "What do you need?"
          Key: "type"
          Answers: ["Train stations", "Bus stops", "Parking spots", "Bike rentals", "Charging Stations", "Car rental"]


3. You will also receive 'existing_markers', which are the locations the user already has. DO NOT suggest any places that have the same 'lat' and 'lon' (filter them out!).

4. Use the user's answers to **filter the Overpass elements**. Only keep elements that satisfy the criteria for that category, if that is possible.

5. Selection rules:
   - Return exactly 5 places.
   - Prioritize relevance, ratings, and the user's filter answers.
   - Keep all original keys in each element (id, type, lat/lon or center, tags, nodes/members if present).

6. Always respect the category context: filters should only be applied based on the answers for that category.

7. After you select the top 5, add a key: value pair to each of these elements. The key should be 'description' and
    the value should be 1 sentence that describes the place.
    
8. Other than that, do not change the structure of any remaining elements; only eliminate elements that do not match the user's answers.

9. Return ONLY the selected elements in the exact same structure as you got them (a list of dictionaries) + the extra description.
"""


def get_selection_via_openai(user_request, elements, existing_markers):
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in your environment.")

    client = OpenAI(api_key=api_key)

    user_block = f"User request:\n{user_request}\n\nElements:\n{elements}\n\nExisting markers:{existing_markers}"

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
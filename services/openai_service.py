from openai import OpenAI
from dotenv import load_dotenv
import os, re, json, requests

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

3. Use the user's answers to **filter the Overpass elements**. Only keep elements that satisfy the criteria for that category, if that is possible.

4. Selection rules:
   - Return exactly 5 places.
   - Prioritize relevance, ratings, and the user's filter answers.
   - Keep all original keys in each element (id, type, lat/lon or center, tags, nodes/members if present).

5. Always respect the category context: filters should only be applied based on the answers for that category.

6. Do not change the structure of any remaining elements; only eliminate elements that do not match the user's answers.

7. Return ONLY the selected elements in the exact same structure as you got them (a list of dictionaries).
"""



def get_selection_via_openai(user_request, elements):
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


def main():

    user_request = {
        "category": "essentials",
        "type": "Supermarket",
        "lat": 52.41289089264018,
        "lon": 12.54793167114258,
        "radius": 2000
    }

    elements = [
        {
            "id": 618658140,
            "lat": 52.4224094,
            "lon": 12.5498393,
            "tags": {
                "brand": "EDEKA",
                "brand:wikidata": "Q701755",
                "brand:wikipedia": "de:Edeka",
                "contact:email": "edeka.hoeppner.brandenburganderhavel@minden.edeka.de",
                "contact:phone": "+49 3381 300355",
                "contact:website": "https://www.edeka.de/eh/minden-hannover/edeka-h%C3%B6ppner-werner-seelenbinder-str.-51/index.jsp",
                "name": "EDEKA Höppner",
                "opening_hours": "Mo-Fr 07:00-20:00; Sa 07:00-19:00",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "node"
        },
        {
            "id": 651558378,
            "lat": 52.4138476,
            "lon": 12.5246426,
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "4",
                "addr:postcode": "14770",
                "addr:street": "Friedrich-Franz-Straße",
                "brand": "Lidl",
                "brand:wikidata": "Q151954",
                "brand:wikipedia": "en:Lidl",
                "contact:website": "https://www.lidl.de/f/brandenburg-an-der-havel/altstadt-friedrich-franz-str-4.html",
                "name": "Lidl",
                "opening_hours": "Mo-Sa 07:00-20:00",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "node"
        },
        {
            "id": 774915354,
            "lat": 52.4049091,
            "lon": 12.5719783,
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "23",
                "addr:postcode": "14776",
                "addr:street": "Potsdamer Straße",
                "brand": "Lidl",
                "brand:wikidata": "Q151954",
                "brand:wikipedia": "en:Lidl",
                "contact:website": "https://www.lidl.de/f/brandenburg-an-der-havel/neustadt-potsdamer-str-23.html",
                "name": "Lidl",
                "opening_hours": "Mo-Sa 07:00-20:00",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "node"
        },
        {
            "id": 1205694096,
            "lat": 52.4085465,
            "lon": 12.5650449,
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "23",
                "addr:postcode": "14776",
                "addr:street": "Sankt-Annen-Straße",
                "brand": "Rewe",
                "brand:wikidata": "Q16968817",
                "brand:wikipedia": "de:Rewe",
                "contact:phone": "+493381 211538",
                "contact:website": "https://www.rewe.de/marktseite/brandenburg-an-der-havel/4040190/rewe-markt-sankt-annen-str-23/",
                "level": "0",
                "name": "REWE",
                "opening_hours": "Mo-Sa 08:00-20:00",
                "shop": "supermarket",
                "toilets:wheelchair": "yes",
                "wheelchair": "yes"
            },
            "type": "node"
        },
        {
            "id": 1357500850,
            "lat": 52.4061972,
            "lon": 12.570632,
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "16",
                "addr:postcode": "14776",
                "addr:street": "Potsdamer Straße",
                "brand": "Netto Marken-Discount",
                "brand:wikidata": "Q879858",
                "brand:wikipedia": "de:Netto Marken-Discount",
                "name": "Netto Marken-Discount",
                "opening_hours": "Mo-Sa 07:00-20:00",
                "shop": "supermarket",
                "website": "https://www.netto-online.de/filialen/Brandenburg-an-der-Havel/Potsdamer-St-16/7768/",
                "wheelchair": "limited"
            },
            "type": "node"
        },
        {
            "id": 1425784569,
            "lat": 52.4030051,
            "lon": 12.569036,
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "30",
                "addr:postcode": "14776",
                "addr:street": "Geschwister-Scholl-Straße",
                "brand": "ALDI Nord",
                "brand:wikidata": "Q41171373",
                "brand:wikipedia": "en:Aldi",
                "name": "Aldi",
                "opening_hours": "Mo-Sa 07:00-21:00",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "node"
        },
        {
            "id": 2100544048,
            "lat": 52.3953409,
            "lon": 12.5446696,
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "8",
                "addr:postcode": "14776",
                "addr:street": "Göttiner Straße",
                "brand": "Netto Marken-Discount",
                "brand:wikidata": "Q879858",
                "brand:wikipedia": "de:Netto Marken-Discount",
                "check_date:opening_hours": "2024-08-08",
                "name": "Netto Marken-Discount",
                "opening_hours": "Mo-Sa 07:00-20:00",
                "shop": "supermarket",
                "website": "https://www.netto-online.de/filialen/Brandenburg-Havel/Goettiner-Str-8/7519/",
                "wheelchair": "yes"
            },
            "type": "node"
        },
        {
            "id": 3492938638,
            "lat": 52.4186108,
            "lon": 12.5518858,
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "20",
                "addr:postcode": "14770",
                "addr:street": "Willi-Sänger-Straße",
                "brand": "Netto Marken-Discount",
                "brand:wikidata": "Q879858",
                "brand:wikipedia": "de:Netto Marken-Discount",
                "internet_access": "wlan",
                "name": "Netto Marken-Discount",
                "opening_hours": "Mo-Sa 07:00-20:00",
                "operator": "Netto Marken-Discount AG & Co. KG",
                "shop": "supermarket",
                "website": "https://www.netto-online.de/filialen/Brandenburg/Willi-Saenger-Str-20/4839/",
                "wheelchair": "yes"
            },
            "type": "node"
        },
        {
            "id": 4916892248,
            "lat": 52.4080794,
            "lon": 12.5467648,
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "76",
                "addr:postcode": "14770",
                "addr:street": "Neuendorfer Straße",
                "brand": "Rewe",
                "brand:wikidata": "Q16968817",
                "brand:wikipedia": "de:Rewe",
                "building": "retail",
                "contact:phone": "+49 3381 2099031",
                "contact:website": "https://www.rewe.de/marktseite/brandenburg-an-der-havel/4040256/rewe-markt-neuendorfer-strasse-76/",
                "level": "0",
                "name": "REWE",
                "opening_hours": "Mo-Sa 06:00-22:00",
                "operator": "Emil Möbus",
                "organic": "yes",
                "payment:american_express": "yes",
                "payment:girocard": "yes",
                "payment:mastercard": "yes",
                "payment:visa": "yes",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "node"
        },
        {
            "id": 9397598413,
            "lat": 52.4140495,
            "lon": 12.5386592,
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "31",
                "addr:postcode": "14770",
                "addr:street": "Harlungerstraße",
                "name": "Yasmine Al Sham Orientalische Markt",
                "opening_hours": "Mo-Fr 08:00-20:00",
                "shop": "supermarket",
                "wheelchair": "no"
            },
            "type": "node"
        },
        {
            "center": {
                "lat": 52.4223888,
                "lon": 12.5409516
            },
            "id": 87601472,
            "nodes": [
                1018975916,
                1018976584,
                6109976961,
                10081122073,
                423909053,
                6109976962,
                10081122038,
                10081122044,
                1349764716,
                1018975549,
                10081122040,
                10081122039,
                1018975916
            ],
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "2",
                "addr:postcode": "14770",
                "addr:street": "Ruppinstraße",
                "brand": "NORMA",
                "brand:wikidata": "Q450180",
                "brand:wikipedia": "de:Norma (Supermarkt)",
                "building": "commercial",
                "name": "NORMA",
                "name:de": "Norma",
                "opening_hours": "Mo-Fr 07:00-20:00; Sa 07:00-20:00",
                "operator": "Norma",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "way"
        },
        {
            "center": {
                "lat": 52.4053148,
                "lon": 12.5570454
            },
            "id": 91305810,
            "nodes": [
                1060078246,
                7449627187,
                7449627186,
                1425718655,
                1686460006,
                1686459987,
                1060078403,
                7162279011,
                7162279009,
                1686460004,
                7595304706,
                7595304702,
                7595304703,
                1060078516,
                1060078246
            ],
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "2-3",
                "addr:postcode": "14776",
                "addr:street": "Jacobstraße",
                "brand": "Penny",
                "brand:wikidata": "Q284688",
                "brand:wikipedia": "en:Penny (supermarket)",
                "building": "supermarket",
                "cash_withdrawal": "yes",
                "cash_withdrawal:fee": "no",
                "cash_withdrawal:limit": "200",
                "cash_withdrawal:purchase_minimum": "10",
                "cash_withdrawal:purchase_required": "yes",
                "cash_withdrawal:type": "checkout",
                "name": "PENNY",
                "opening_hours": "Mo-Sa 07:00-22:00; Su,PH off",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "way"
        },
        {
            "center": {
                "lat": 52.4199714,
                "lon": 12.5470413
            },
            "id": 91305813,
            "nodes": [
                1060078208,
                6109976955,
                6109976954,
                6109976953,
                6109976956,
                1060078749,
                6109976952,
                6109976959,
                6109976960,
                6109976951,
                1060078356,
                1060078595,
                1060078208
            ],
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "46a",
                "addr:postcode": "14770",
                "addr:street": "Willi-Sänger-Straße",
                "brand": "PENNY",
                "brand:wikidata": "Q284688",
                "brand:wikipedia": "en:Penny (supermarket)",
                "building": "supermarket",
                "name": "PENNY",
                "opening_hours": "Mo-Sa 07:00-21:00",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "way"
        },
        {
            "center": {
                "lat": 52.4021771,
                "lon": 12.5512777
            },
            "id": 129169538,
            "nodes": [
                1425718523,
                1425718522,
                5921016408,
                7449871428,
                1022691517,
                7449871417,
                7449871414,
                1022692361,
                1425718528,
                1686459705,
                1425718523
            ],
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "4-6",
                "addr:postcode": "14776",
                "addr:street": "Wilhelmsdorfer Straße",
                "brand": "NORMA",
                "brand:wikidata": "Q450180",
                "brand:wikipedia": "de:Norma (Supermarkt)",
                "building": "retail",
                "check_date:opening_hours": "2025-01-12",
                "name": "NORMA",
                "opening_hours": "Mo-Sa 07:00-20:00",
                "shop": "supermarket"
            },
            "type": "way"
        },
        {
            "center": {
                "lat": 52.415446,
                "lon": 12.5380237
            },
            "id": 146921936,
            "nodes": [
                1601408035,
                1601407944,
                1601407946,
                1601407949,
                1601407957,
                1601407983,
                1601407966,
                1601407963,
                1405929636,
                1601408027,
                1601408033,
                1601408035
            ],
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "10",
                "addr:postcode": "14770",
                "addr:street": "Karl-Marx-Straße",
                "brand": "Netto",
                "brand:wikidata": "Q552652",
                "brand:wikipedia": "da:Netto (supermarkedskæde)",
                "building": "supermarket",
                "name": "Netto",
                "opening_hours": "PH off; Mo-Sa 07:00-20:00",
                "operator": "NETTO ApS & Co. KG",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "way"
        },
        {
            "center": {
                "lat": 52.4205579,
                "lon": 12.5449349
            },
            "id": 342265096,
            "nodes": [
                3492885553,
                11332962041,
                3492885555,
                3492885552,
                3492885551,
                3492885557,
                3492885556,
                3492885554,
                3492885553
            ],
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "66",
                "addr:postcode": "14770",
                "addr:street": "Willi-Sänger-Straße",
                "brand": "ALDI Nord",
                "brand:wikidata": "Q41171373",
                "brand:wikipedia": "en:Aldi",
                "building": "retail",
                "name": "ALDI Nord",
                "opening_hours": "Mo-Sa 07:00-21:00",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "way"
        },
        {
            "center": {
                "lat": 52.4064018,
                "lon": 12.5392797
            },
            "id": 807608439,
            "nodes": [
                7552263333,
                7552263334,
                7552263335,
                7552263336,
                7552263333
            ],
            "tags": {
                "addr:city": "Brandenburg an der Havel",
                "addr:country": "DE",
                "addr:housenumber": "52",
                "addr:postcode": "14770",
                "addr:street": "Neuendorfer Straße",
                "brand": "Rewe",
                "brand:wikidata": "Q16968817",
                "brand:wikipedia": "de:Rewe",
                "building": "yes",
                "contact:phone": "+49 3381 6042250",
                "contact:website": "https://www.rewe.de/marktseite/brandenburg-an-der-havel-stadt/1766097/rewe-center-neuendorfer-strasse-52/",
                "name": "REWE Center",
                "opening_hours": "Mo-Sa 07:00-21:30",
                "operator": "Karen Laute",
                "shop": "supermarket",
                "wheelchair": "yes"
            },
            "type": "way"
        }
    ]

    selection_string = get_selection_via_openai(user_request, elements)

    selection = json.loads(selection_string)
    print(len(selection))
    print(selection)
    return selection


if __name__ == "__main__":
    main()
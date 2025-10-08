# QUERIES
from typing import List


def query_places_explore_outdoor(lat: float, lon: float, radius: int) -> str:
    combined_query = f"""
    [out:json][timeout:180];
    (
      /* --- Natural features --- */
      node["natural"~"water|lake|waterfall|spring|gorge|peak|cliff|valley|ridge|rock|cave_entrance|forest"][name](around:{radius},{lat},{lon});
      way["natural"~"water|lake|waterfall|spring|gorge|peak|cliff|valley|ridge|rock|cave_entrance|forest"][name](around:{radius},{lat},{lon});
      relation["natural"~"water|lake|waterfall|spring|gorge|peak|cliff|valley|ridge|rock|cave_entrance|forest"][name](around:{radius},{lat},{lon});

      /* --- Water bodies --- */
      node["water"~"lake|basin"][name](around:{radius},{lat},{lon});
      way["water"~"lake|basin"][name](around:{radius},{lat},{lon});
      relation["water"~"lake|basin"][name](around:{radius},{lat},{lon});

      /* --- Leisure / nature --- */
      node["leisure"~"park|garden|nature_reserve"][name](around:{radius},{lat},{lon});
      way["leisure"~"park|garden|nature_reserve"][name](around:{radius},{lat},{lon});
      relation["leisure"~"park|garden|nature_reserve"][name](around:{radius},{lat},{lon});
    )->.natural;

    (
      /* --- All tourism attractions --- */
      node["tourism"~"attraction|viewpoint|picnic_site|theme_park"][name](around:{radius},{lat},{lon});
      way["tourism"~"attraction|viewpoint|picnic_site|theme_park"][name](around:{radius},{lat},{lon});
      relation["tourism"~"attraction|viewpoint|picnic_site|theme_park"][name](around:{radius},{lat},{lon});
    )->.all;

    (
      /* --- Indoor / building features to exclude --- */
      node["indoor"="yes"](around:{radius},{lat},{lon});
      way["indoor"="yes"](around:{radius},{lat},{lon});
      relation["indoor"="yes"](around:{radius},{lat},{lon});
      node["building"](around:{radius},{lat},{lon});
      way["building"](around:{radius},{lat},{lon});
      relation["building"](around:{radius},{lat},{lon});
    )->.indoors;

    /* --- Combine: all outdoor natural + attractions minus indoor --- */
    (
      .natural; 
      (.all; - .indoors;);
    );
    out center;
    """
    print (combined_query)
    return combined_query


def query_places_explore_indoor(lat: float, lon: float, radius: int) -> str:
    return f"""
        [out:json][timeout:180];
        (
          node["tourism"~"museum|theatre"][name](around:{radius},{lat},{lon});
          way["tourism"~"museum|theatre"][name](around:{radius},{lat},{lon});
          relation["tourism"~"museum|theatre"][name](around:{radius},{lat},{lon});
        
          node["amenity"="library"]["tourism"="attraction"][name](around:{radius},{lat},{lon});
          way["amenity"="library"]["tourism"="attraction"][name](around:{radius},{lat},{lon});
          relation["amenity"="library"]["tourism"="attraction"][name](around:{radius},{lat},{lon});
          node["amenity"="library"]["heritage"][name](around:{radius},{lat},{lon});
          way["amenity"="library"]["heritage"][name](around:{radius},{lat},{lon});
          relation["amenity"="library"]["heritage"][name](around:{radius},{lat},{lon});
        
          node["building"="church"]["historic"](around:{radius},{lat},{lon});
          way["building"="church"]["historic"](around:{radius},{lat},{lon});
          relation["building"="church"]["historic"](around:{radius},{lat},{lon});
        
          node["historic"][name](around:{radius},{lat},{lon});
          way["historic"][name](around:{radius},{lat},{lon});
          relation["historic"][name](around:{radius},{lat},{lon});
        );
        out center;
        """


def query_stays(lat: float, lon: float, radius: int, styles: List[str]) -> str:
    """
    styles: list of stay styles (can be multiple):
        ["Camping", "Hostel", "Budget Hotel", "Mid-range Hotel", "Luxury Hotel", "B&B", "All-inclusive"]
    """

    # Map frontend names to query keys
    name_map = {
        "Camping": "camping",
        "Hostel": "hostel",
        "Budget Hotel": "budget",
        "Mid-range Hotel": "midrange",
        "Luxury Hotel": "luxury",
        "B&B": "bnb",
        "All-inclusive": "allinclusive"
    }

    queries = {
        "camping": """
            node[tourism=camp_site];
            way[tourism=camp_site];
            relation[tourism=camp_site];
            node[tourism=caravan_site];
            way[tourism=caravan_site];
            relation[tourism=caravan_site];
        """,
        "hostel": """node[tourism=hostel]; way[tourism=hostel]; relation[tourism=hostel];""",
        "budget": """
            node[tourism=hotel][stars~"^[0-2]$"];
            way[tourism=hotel][stars~"^[0-2]$"];
            relation[tourism=hotel][stars~"^[0-2]$"];
        """,
        "midrange": """
            node[tourism=hotel][stars=3];
            way[tourism=hotel][stars=3];
            relation[tourism=hotel][stars=3];
            node[tourism=hotel][stars=4];
            way[tourism=hotel][stars=4];
            relation[tourism=hotel][stars=4];
        """,
        "luxury": """
            node[tourism=hotel][stars=4];
            way[tourism=hotel][stars=4];
            relation[tourism=hotel][stars=4];
            node[tourism=hotel][stars=5];
            way[tourism=hotel][stars=5];
            relation[tourism=hotel][stars=5];
            node[tourism=resort];
            way[tourism=resort];
            relation[tourism=resort];
        """,
        "bnb": """
            node[tourism=guest_house];
            way[tourism=guest_house];
            relation[tourism=guest_house];
            node[tourism=bed_and_breakfast];
            way[tourism=bed_and_breakfast];
            relation[tourism=bed_and_breakfast];
        """,
        "allinclusive": """
            node[tourism=resort];
            way[tourism=resort];
            relation[tourism=resort];
        """
    }

    # Normalize frontend names to internal keys
    normalized_styles = [name_map[s] for s in styles if s in name_map]

    if not normalized_styles:
        raise ValueError("No valid stay styles provided")

    # Combine selected queries
    combined_query = ""
    for style in normalized_styles:
        combined_query += queries[style]

    # Replace ; with the around syntax
    combined_query = combined_query.replace(';', f'(around:{radius},{lat},{lon});')

    # Wrap with Overpass JSON output and timeout
    print (f"[out:json][timeout:180];({combined_query});out center;")
    return f"[out:json][timeout:180];({combined_query});out center;"


def query_eat_drink(lat: float, lon: float, radius: int, cuisine: str = ".*") -> str:
    return f"""
        [out:json][timeout:180];
        (
          node[amenity~"^(restaurant|cafe|bar|fast_food)$"][cuisine~"{cuisine}",i](around:{radius},{lat},{lon});
          way[amenity~"^(restaurant|cafe|bar|fast_food)$"][cuisine~"{cuisine}",i](around:{radius},{lat},{lon});
          relation[amenity~"^(restaurant|cafe|bar|fast_food)$"][cuisine~"{cuisine}",i](around:{radius},{lat},{lon});
        );
        out center;
        """


def query_essentials(lat: float, lon: float, radius: int, ess_type: str) -> str:
    """
    ess_type: one of ['supermarket', 'pharmacy', 'atm', 'hospital', 'convenience', 'other']
    """
    queries = {
        "supermarket": """
            node[shop=supermarket][name];
            way[shop=supermarket][name];
            relation[shop=supermarket][name];
        """,
        "pharmacy": """
            node[amenity=pharmacy][name];
            way[amenity=pharmacy][name];
            relation[amenity=pharmacy][name];
        """,
        "atm": """
            node[amenity=atm][name];
            way[amenity=atm][name];
            relation[amenity=atm][name];
        """,
        "hospital": """
            node[amenity=hospital][name];
            way[amenity=hospital][name];
            relation[amenity=hospital][name];
        """,
        "other": """
            node[shop~"^(convenience|general|kiosk|variety_store)$",i][name];
            way[shop~"^(convenience|general|kiosk|variety_store)$",i][name];
            relation[shop~"^(convenience|general|kiosk|variety_store)$",i][name];
            node[amenity~"^(toilets|bank|post_office|bureau_de_change|clinic|fuel)$",i][name];
            way[amenity~"^(toilets|bank|post_office|bureau_de_change|clinic|fuel)$",i][name];
            relation[amenity~"^(toilets|bank|post_office|bureau_de_change|clinic|fuel)$",i][name];
        """
    }

    # Normalize type to lowercase
    ess_type = ess_type.lower()

    if ess_type not in queries:
        raise ValueError(f"Invalid essentials type: {ess_type}")

    # Replace radius/lat/lon in query
    query_body = queries[ess_type].replace(';', f'(around:{radius},{lat},{lon});')

    return f"[out:json][timeout:180];({query_body});out center;"



def query_getting_around(lat: float, lon: float, radius: int, around_types: list) -> str:
    """
    around_types: list of human-readable types from frontend, e.g.,
    ["Train stations", "Bus stops", "Parking spots", "Bike rentals", "Charging Stations", "Car rental"]
    """
    # Map frontend names to query keys
    name_map = {
        "Train stations": "train",
        "Bus stops": "bus",
        "Parking spots": "parking",
        "Bike rentals": "bike",
        "Charging Stations": "charging",
        "Car rental": "car"
    }

    queries = {
        "train": """
            node[railway=station][name];
            way[railway=station][name];
            relation[railway=station][name];
        """,
        "bus": """
            node[highway=bus_stop][name];
            way[highway=bus_stop][name];
            relation[highway=bus_stop][name];
        """,
        "parking": """
            node[amenity=parking][name];
            way[amenity=parking][name];
            relation[amenity=parking][name];
        """,
        "bike": """
            node[amenity=bicycle_rental][name];
            way[amenity=bicycle_rental][name];
            relation[amenity=bicycle_rental][name];
        """,
        "charging": """
            node[amenity=charging_station][name];
            way[amenity=charging_station][name];
            relation[amenity=charging_station][name];
        """,
        "car": """
            node[amenity=car_rental][name];
            way[amenity=car_rental][name];
            relation[amenity=car_rental][name];
        """
    }

    # Normalize frontend names to internal keys
    normalized_types = [name_map[t] for t in around_types if t in name_map]

    if not normalized_types:
        raise ValueError("No valid getting around types provided")

    # Combine selected queries
    combined_query = ""
    for t in normalized_types:
        combined_query += queries[t]

    # Replace ; with the around syntax
    combined_query = combined_query.replace(";", f"(around:{radius},{lat},{lon});")

    return f"[out:json][timeout:180];({combined_query});out center;"

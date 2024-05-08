import os
import json
import requests

from datetime import datetime
from ipyleaflet import Map, Marker


def extract_forces(type: str = None) -> list:
    """
    Extracts the forces data from the Police Data UK website.

    Parameters:
    -
    type (str): The type of data to extract. Options are: None, leicestershire, leicestershire/people

    Returns:
    -
    A list of dictionaries containing forces data.

    Raises:
    -
    ValueError: If the type parameter is not specified.

    Examples:
    -
    To extract forces data, you can use the following code:

    ```python
    location_data = extract_forces_api(type='leicestershire')
    ```
    """

    base_url = 'https://data.police.uk/api/forces'
    if type == None:
        url = base_url
    elif 'leicestershire' == type.lower():
        url = base_url + '/' + type.lower()
    elif 'leicestershire/people' == type.lower():
        url = base_url + '/' + type.lower()

    r = requests.get(url)
    list_of_dict = json.loads(r.content)
    return list_of_dict



def extract_street_level_crimes(lat: float = None, lng: float = None, date: str = None, poly: tuple = None, crime_type: str = None) -> list:
    """
    Extracts the street-level crimes data for a specific location or custom area.

    Parameters
    -
    lat - Latitude of the requested crime area (optional)\n
    lng - Longitude of the requested crime area (optional)\n
    date - Optional. "YYYY-MM" Limit results to a specific month. The latest month will be shown by default (optional)\n
    OR: \n
    poly - Limit results to a specific area. The lat/lng pairs which define the boundary of the custom area (optional)\n

    You can also specify the type of crime:\n
    crime_type - The type of crime. Options are: None, anti-social-behavior, burglary (optional)\n

    Returns
    -
    A list of dictionaries containing the street-level crimes data for the specified location or custom area.

    Raises
    -
    ValueError - If the lat/lng or poly parameters are not specified, or if the date parameter is not specified.

    Examples
    -
    - To extract street-level crimes data for a specific location, you can use the following code:

    ```python
    location_data = extract_street_level_crimes(lat=52.62372, lng=-1.15723)
    ```

    - To extract street-level crimes data for a custom area, you can use the following code:

    ```python
    location_data = extract_street_level_crimes(poly=((52.62372, -1.15723), (52.62372, -1.15723), (52.62372, -1.15723)))
    ```

    - To extract street-level crimes data for a specific type of crime, you can use the following code:

    ```python
    location_data = extract_street_level_crimes(crime_type='burglary')
    ```
    """
    # Get current year
    current_year = datetime.now().year

    # Get current month
    current_month = datetime.now().month

    if crime_type == None:
        base_url = "https://data.police.uk/api/crimes-street/all-crime?"
    elif crime_type != None:
        base_url = f"https://data.police.uk/api/crimes-street/{crime_type}?"

    if date == None:
        if lat and lng != None:
            url = base_url + f"lat={lat}&lng={lng}&date={current_year}-{current_month}"
        elif poly != None:
            url = base_url + f"poly={poly[0][0]}:{poly[0][1]},{poly[1][0]}:{poly[1][1]},{poly[2][0]},{poly[2][1]}&date={current_year}-{current_month}"
        else:
            raise ValueError(f'Specify the lat/lng, you passed {lat, lng} or poly {poly}')
    
    elif date != None:
        if lat and lng != None:
            url = base_url + f"lat={lat}&lng={lng}&date={date}"
        elif poly != None:
            url = base_url + f"poly={poly[0][0]}:{poly[0][1]},{poly[1][0]}:{poly[1][1]},{poly[2][0]}:{poly[2][1]}&date={date}"
        else:
            raise ValueError(f'Specify the lat/lang, you passed {lat, lng} or poly {poly}')
    else: 
        raise ValueError(f'Specify the date, you passed {date}')
   
   
    r = requests.get(url)
    list_of_dict = json.loads(r.content)
    
    return list_of_dict


########## THIS PART IS IN DEVELOPMENT ##########


# Global variable to store the markers
markers = []

def on_map_click(event, map_instance):
    global markers
    
    if event['type'] == 'click':  # Check for left-click
        lat, lon = event['coordinates']
        print("Latitude:", lat)
        print("Longitude:", lon)
        
        # Add marker for first three clicks
        if len(markers) < 3:
            marker = Marker(location=(lat, lon))
            map_instance.add_layer(marker)
            markers.append(marker)
            
            # Return None until the fourth click
            return None
        else:
            to_return = markers.copy()
            # Remove markers on the fourth click
            for marker in markers:
                map_instance.remove_layer(marker)
            markers.clear()
            
            # Return coordinates of the first three clicks
            return [(marker.location[0], marker.location[1]) for marker in to_return]
            
def create_map():
    # Create a map centered around London
    m = Map(center=(51.5074, -0.1278), zoom=10)

    # Add a click event handler to the map
    def click_handler(event=None, **kwargs):
        clicked = on_map_click(kwargs, m)
        if clicked is not None:
            print("Clicked points:", clicked)

    m.on_interaction(click_handler)

    # Display the map
    return m

def choose_poly():

    map_of_london = create_map()

    # Display the map 
    return map_of_london

#################################################


def extract_street_level_outcomes(location_id: int = None, lat: float = None, lng: float = None, date: str = None, poly: list = None) -> list:
    """
    Extracts the street-level outcomes for a specified location or area.

    Parameters
    -
    lat - Latitude of the requested crime area\n
    lng - Longitude of the requested crime area\n
    date - Optional. "YYYY-MM" Limit results to a specific month. \n
        The latest month will be shown by default
    poly - The lat/lng pairs which define the boundary of the custom area. \n
        The poly parameter is formatted in lat/lng pairs, separated by 
        colons: [lat],[lng]:[lat],[lng]:[lat],[lng]
    location_id - Crimes and outcomes are mapped to specific locations on the map. \n
        Valid IDs are returned by other methods which return location information.

    Returns
    -
    - A list of dictionaries containing the outcomes data for the specified location or area.

    Raises
    -
    - ValueError: If the lat/lng or poly or location_id parameter is not specified, or if the parameters are not provided correctly.

    Examples
    -
    - To extract street-level outcomes for a specified location, you can use the following code:

    ```python
    outcomes_data = extract_street_level_outcomes(location_id='12345')
    ```

    - To extract street-level outcomes for a specified lat/lng location, you can use the following code:

    ```python
    outcomes_data = extract_street_level_outcomes(lat=52.62372, lng=-1.157236)
    ```

    - To extract street-level outcomes for a specified custom area, you can use the following code:

    ```python
    outcomes_data = extract_street_level_outcomes(poly=[[52.62372, -1.157236], [52.62528, -1.157422], [52.62528, -1.157608]])
    ```
    """

    # Get current year
    current_year = datetime.now().year

    # Get current month
    current_month = datetime.now().month

    base_url = 'https://data.police.uk/api/outcomes-at-location?'

    if date == None:
        if lat and lng != None:
            url = base_url + f"date={current_year}-{current_month}&lat={lat}&lng={lng}"
        elif poly != None:
            url = base_url + f"date={current_year}-{current_month}&poly={poly[0][0]}:{poly[0][1]},{poly[1][0]}:{poly[1][1]},{poly[2][0]},{poly[2][1]}"
        elif location_id != None:
            url = base_url + f"date={current_year}-{current_month}&location_id={location_id}"
        else:
            raise ValueError(f'Specify the lat/lang or poly or location_id that you passed or make sure they are correct: location_id-{location_id}, lat/lng-{lat, lng}, poly={poly}')
    
    elif date != None:
        if lat and lng != None:
            url = base_url + f"date={date}&lat={lat}&lng={lng}"
        elif poly != None:
            url = base_url + f"date={date}&poly={poly[0][0]}:{poly[0][1]},{poly[1][0]}:{poly[1][1]},{poly[2][0]}:{poly[2][1]}"
        elif location_id != None:
            url = base_url + f"date={date}&location_id={location_id}"
        else:
            raise ValueError(f'Specify the lat/lang or poly or location_id that you passed or make sure they are correct: location_id-{location_id}, lat/lng-{lat, lng}, poly={poly}')
        
    else: 
        raise ValueError(f'Specify the date, you passed {date}')
   
   
    r = requests.get(url)
    list_of_dict = json.loads(r.content)
    
    return list_of_dict




def extract_crimes_at_location(lat: float = None, lng: float = None, date: str = None, location_id: int = None) -> list:
    """
    Extracts the crime data for a specific location based on latitude and longitude.

    Parameters
    -
    lat (float): Latitude of the requested crime area.\n
    lng (float): Longitude of the requested crime area.\n
    date (str): Optional. "YYYY-MM" Limit results to a specific month. The latest month will be shown by default.\n
    location_id (int): Crimes and outcomes are mapped to specific locations on the map. Valid IDs are returned by other methods which return location information.\n

    Returns
    -
    list: A list of dictionaries containing crime data for the specified latitude and longitude.

    Raises
    ------
    ValueError: If the lat/lng or location_id parameter is not specified, or if the parameters are not provided correctly.
    """

    # Get current year
    current_year = datetime.now().year

    # Get current month
    current_month = datetime.now().month

    base_url = 'https://data.police.uk/api/crimes-at-location?'

    if date == None:
        if lat and lng != None:
            url = base_url + f"date={current_year}-{current_month}&lat={lat}&lng={lng}"
        elif location_id != None:
            url = base_url + f"date={current_year}-{current_month}&location_id={location_id}"
        else:
            raise ValueError(f'Specify the lat/lang or location_id that you passed or make sure they are correct: location_id-{location_id}, lat/lng-{lat, lng}')
    
    elif date != None:
        if lat and lng != None:
            url = base_url + f"date={date}&lat={lat}&lng={lng}"
        elif location_id != None:
            url = base_url + f"date={date}&location_id={location_id}"
        else:
            raise ValueError(f'Specify the lat/lang or location_id that you passed or make sure they are correct: location_id-{location_id}, lat/lng-{lat, lng}')
        
    else: 
        raise ValueError(f'Specify the date, you passed {date}')
   
   
    r = requests.get(url)
    list_of_dict = json.loads(r.content)
    
    return list_of_dict




def extract_crimes_no_location(category: str = 'all-crime', force: str = 'leicestershire', date: str = None) -> list:
    """
    Extracts crimes data without location information.

    Parameters
    -
    category (str): The type of crime. Options are: None, anti-social-behavior, burglary\n
    date (str): Optional. "YYYY-MM" Limit results to a specific month. \n
        The latest month will be shown by default
    force (str): The name of the police force. If not specified, data for all forces will be returned.\n

    Returns
    -
    list: A list of dictionaries containing crimes data without location information.

    Raises
    -
    ValueError: If the category, force, or date parameters are not specified, or if the parameters are not provided correctly.

    Examples
    -
    - To extract crimes data without location information for a specific category and force, use the following code:

        crimes_data = extract_crimes_no_location(category='burglary', force='leicestershire')

    - To extract crimes data without location information for a specific category, force, and date, use the following code:

        crimes_data = extract_crimes_no_location(category='burglary', force='leicestershire', date='2021-01')
    """

    # Get current year
    current_year = datetime.now().year

    # Get current month
    current_month = datetime.now().month

    base_url = 'https://data.police.uk/api/crimes-no-location?'

    if date == None:
        if (category and force) != None:
            url = base_url + f"category={category}&force={force}&date={current_year}-{current_month}"
        else:
            raise ValueError(f'Specify the category and force that you passed or make sure they are correct: category-{category}, force-{force}')
    
    elif date != None:
        if (category and force) != None:
            url = base_url + f"category={category}&force={force}&date={date}"
        else:
            raise ValueError(f'Specify the category and force that you passed or make sure they are correct: category-{category}, force-{force}')
    
    else: 
        raise ValueError(f'Specify the date, you passed: date={date}')
   
   
    r = requests.get(url)
    list_of_dict = json.loads(r.content)
    
    return list_of_dict




def extract_crimes_categories_at_date(date: str = None) -> list:
    """
    Extracts crime categories data for a specific date.

    Parameters:
    -
    date (str): Optional. "YYYY-MM" Limit results to a specific month. The latest month will be shown by default.

    Returns:
    -
    A list of dictionaries containing crime categories data for the specified date.

    Raises:
    -
    ValueError: If the date parameter is not specified.

    Examples:
    -
    To extract crime categories data for a specific date, you can use the following code:

    ```python
    location_data = extract_crimes_categories_at_date(date='2021-01')
    ```
    """

    # Get current year
    current_year = datetime.now().year

    # Get current month
    current_month = datetime.now().month

    base_url = 'https://data.police.uk/api/crime-categories?'

    if date == None:
        
        url = base_url + f"date={current_year}-{current_month}"
        
    elif date != None:
        
        url = base_url + f"date={date}"
       
    else: 
        raise ValueError(f'Specify the date, you passed {date}')
   
   
    r = requests.get(url)
    list_of_dict = json.loads(r.content)
    
    return list_of_dict




def extract_last_updated():
    """
    Returns the last updated date and time for the data on the Police Data UK website.

    Returns:
    -
    A list of dictionaries containing the last updated date and time for the data on the Police Data UK website.

    Raises:
    -
    No exceptions are raised by this function.
    """

    url = 'https://data.police.uk/api/crime-last-updated'

    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict




def extract_outcome_for_specific_crime(crime_id: str = None) -> list:
    """
    Returns the outcomes (case history) for the specified crime.
    Note: Outcomes are not available for the Police Service of Northern Ireland.

    Parameters:
    -
    crime_id (str): 64-character identifier of the crime for which to retrieve outcomes.

    Returns:
    -
    A list of dictionaries containing outcomes data for the specified crime.

    Raises:
    -
    ValueError: If the crime_id parameter is not specified.

    Examples:
    -
    To extract outcomes data for a specific crime, you can use the following code:

    ```python
    outcomes_data = extract_outcome_for_specific_crime(crime_id='64-character-identifier')
    ```
    """

    base_url = 'https://data.police.uk/api/outcomes-for-crime/'

    if crime_id != None:
        url = base_url + f"{crime_id}"
    elif crime_id == None:
        raise ValueError(f"Specify the crime_id that you passed and make sure it's correct: crime_id={crime_id}")
    
    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict




def extract_neighbourhoods_for_a_force(force: str = 'leicestershire') -> list:
    """
    Returns the neighbourhoods for the specified force.

    Parameters:
    -
    force (str): The name of the police force for which to retrieve data. If not specified, data for all forces will be returned.

    Returns:
    -
    A list of dictionaries containing neighbourhood data for the specified force.

    Raises:
    -
    ValueError: If the force parameter is not specified, or if the parameter is not provided correctly.

    Examples:
    -
    To extract neighbourhood data for a specific force, you can use the following code:

    ```python
    location_data = extract_neighbourhoods_for_a_force(force='leicestershire')
    ```
    """

    if force != None:
        url = f'https://data.police.uk/api/{force}/neighbourhoods'

    elif force == None:
        raise ValueError(f"Specify the force that you passed and make sure it's correct: force={force}")

    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict




def extract_specific_neighbourhoods_for_a_force(force: str = 'leicestershire', neighbourhood_id: str = 'NC04') -> list:
    """
    Extracts the neighbourhood data for a specific location based on latitude and longitude.

    Parameters:
    -
    force (str): The name of the police force for which to retrieve data. If not specified, data for all forces will be returned.\n
    neighbourhood_id (str): The ID of the location to get stop and searches for.

    Returns:
    -
    A list of dictionaries containing neighbourhood data for the specified latitude and longitude.

    Raises:
    -
    ValueError: If the force or neighbourhood_id parameter is not specified.

    Examples:
    -
    To extract neighbourhood data for a specific location, you can use the following code:

    ```python
    location_data = extract_specific_neighbourhoods_for_a_force(force='leicestershire', neighbourhood_id='NC04')
    ```
    """
    base_url = 'https://data.police.uk/api/'

    if (force != None) and (neighbourhood_id != None):
        url = base_url + f"{force}/{neighbourhood_id}"
    elif (force == None) and (neighbourhood_id == None):
        return f'specify the neighbourhood_id and force'
    else:
        raise ValueError(f"Specify the force and neighbourhood that you passed and make sure it's correct: force={force}, neighbourhood_id={neighbourhood_id}")
    
    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict




def extract_neighbourhood_boundary_for_a_force(force: str = 'leicestershire', neighbourhood_id: str = 'NC04') -> list:
    """
    Extracts the neighbourhood data for a specific location based on latitude and longitude.

    Parameters:
    -
    force (str): The name of the police force for which to retrieve data. If not specified, data for all forces will be returned.\n
    neighbourhood_id (str): The ID of the location to get stop and searches for.

    Returns:
    -
    A list of dictionaries containing neighbourhood data for the specified latitude and longitude.

    Raises:
    -
    ValueError: If the force or neighbourhood_id parameter is not specified, or if the parameters are not provided correctly.

    Examples:
    -
    To extract neighbourhood data for a specific location, you can use the following code:

    ```python
    location_data = extract_neighbourhood_boundary_for_a_force(force='leicestershire', neighbourhood_id='NC04')
    ```
    """
    base_url = 'https://data.police.uk/api/'

    if (force != None) and (neighbourhood_id != None):
        url = base_url + f"{force}/{neighbourhood_id}/boundary"
    elif (force == None) and (neighbourhood_id == None):
        return f'specify the neighbourhood_id and force'
    else:
        raise ValueError(f"Specify the force and neighbourhood that you passed and make sure it's correct: force={force}, neighbourhood_id={neighbourhood_id}")
    
    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict




def extract_neighbourhood_team_for_a_force(force: str = 'leicestershire', neighbourhood_id: str = 'NC04') -> list:
    """
    Extracts the neighbourhood data for a specific location based on latitude and longitude.

    Parameters:
    -
    force (str): The name of the police force for which to retrieve data. If not specified, data for all forces will be returned.\n
    neighbourhood_id (str): The ID of the location to get stop and searches for.

    Returns:
    -
    A list of dictionaries containing neighbourhood data for the specified latitude and longitude.

    Raises:
    -
    ValueError: If the force or neighbourhood_id parameter is not specified.

    Examples:
    -
    To extract neighbourhood data for a specific location, you can use the following code:

    ```python
    location_data = extract_neighbourhood_team_for_a_force(force='leicestershire', neighbourhood_id='NC04')
    ```
    """
    base_url = 'https://data.police.uk/api/'

    if (force != None) and (neighbourhood_id != None):
        url = base_url + f"{force}/{neighbourhood_id}/people"
    elif (force == None) and (neighbourhood_id == None):
        return f'specify the neighbourhood_id and force'
    else:
        raise ValueError(f"Specify the force and neighbourhood that you passed and make sure it's correct: force={force}, neighbourhood_id={neighbourhood_id}")
    
    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict




def extract_neighbourhood_events_for_a_force(force: str = 'leicestershire', neighbourhood_id: str = 'NC04') -> list:
    """
    Extracts the neighbourhood data for a specific location based on latitude and longitude.

    Parameters:
    -
    force (str): The name of the police force for which to retrieve data. If not specified, data for all forces will be returned.\n
    neighbourhood_id (str): The ID of the location to get stop and searches for.

    Returns:
    -
    A list of dictionaries containing neighbourhood data for the specified latitude and longitude.

    Raises:
    -
    ValueError: If the force or neighbourhood_id parameter is not specified.

    Examples:
    -
    To extract neighbourhood data for a specific location, you can use the following code:

    ```python
    location_data = extract_neighbourhood_events_for_a_force(force='leicestershire', neighbourhood_id='NC04')
    ```
    """
    base_url = 'https://data.police.uk/api/'

    if (force != None) and (neighbourhood_id != None):
        url = base_url + f"{force}/{neighbourhood_id}/events"
    elif (force == None) and (neighbourhood_id == None):
        return f'specify the neighbourhood_id and force'
    else:
        raise ValueError(f"Specify the force and neighbourhood that you passed and make sure it's correct: force={force}, neighbourhood_id={neighbourhood_id}")
    
    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict



def extract_neighbourhood_priorities_for_a_force(force: str = 'leicestershire', neighbourhood_id: str = 'NC04') -> list:
    """
    Extracts the neighbourhood data for a specific location based on latitude and longitude.

    Parameters:
    -
    force (str): The name of the police force for which to retrieve data. If not specified, data for all forces will be returned.\n
    neighbourhood_id (str): The ID of the location to get stop and searches for.\n

    Returns:
    -
    A list of dictionaries containing neighbourhood data for the specified latitude and longitude.

    Raises:
    -
    ValueError: If the force or neighbourhood_id parameter is not specified.

    Examples:
    -
    To extract neighbourhood data for a specific location, you can use the following code:

    ```python
    location_data = extract_neighbourhood_priorities_for_a_force(force='leicestershire', neighbourhood_id='NC04')
    ```
    """
    base_url = 'https://data.police.uk/api/'

    if (force != None) and (neighbourhood_id != None):
        url = base_url + f"{force}/{neighbourhood_id}/priorities"
    elif (force == None) and (neighbourhood_id == None):
        return f'specify the neighbourhood_id and force'
    else:
        raise ValueError(f"Specify the force and neighbourhood that you passed and make sure it's correct: force={force}, neighbourhood_id={neighbourhood_id}")
    
    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict




def extract_neighbourhood_at_location(lat: float, lng: float) -> list:
    """
    Extracts the neighbourhood data for a specific location based on latitude and longitude.

    Parameters:
    -
    lat (float): Latitude of the requested crime area.\n
    lng (float): Longitude of the requested crime area.\n

    Returns:
    -
    A list of dictionaries containing neighbourhood data for the specified latitude and longitude.

    Raises:
    -
    ValueError: If the latitude or longitude parameters are not specified, or if the parameters are not provided correctly.

    Examples:
    -
    To extract neighbourhood data for a specific location, you can use the following code:

    ```python
    location_data = extract_neighbourhood_at_location(lat=51.5074, lng=-0.1278)
    ```
    """

    # Get current year
    current_year = datetime.now().year

    # Get current month
    current_month = datetime.now().month

    base_url = 'https://data.police.uk/api/locate-neighbourhood?'

    if (lat != None) and (lng != None):
        url = base_url + f"q={lat},{lng}"
    else:
        raise ValueError(f'specify the lat and lng that you passed and make sure they are correct: lat/lng-{lat, lng}')

    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict



def extract_stop_search(date: str = None, lng: float = None, lat: float = None, poly: list = None, location_id: str = None) -> list:
    """
    Extracts stop and search data for a specific location or custom area.

    Parameters:
    -
    lat - Latitude of the requested crime area (optional)\n
    lng - Longitude of the requested crime area (optional)\n
    date - Optional. "YYYY-MM" Limit results to a specific month. The latest month will be shown by default (optional)\n
    poly - The lat/lng pairs which define the boundary of the custom area. The poly parameter is formatted in lat/lng pairs, separated by colons: [lat],[lng]:[lat],[lng]:[lat],[lng] (optional)\n
    location_id - The ID of the location to get stop and searches for (optional)\n

    Returns:
    -
    A list of dictionaries containing stop and search data for the specified date and location or custom area.

    Raises:
    -
    ValueError - If the date or location parameters are not specified, or if the lat/lng or poly parameters are not provided correctly.

    Examples:
    -
    To extract stop and search data for a specific location, you can use the following code:

    ```python
    location_data = extract_stop_search(lat=51.5074, lng=-0.1278)
    ```

    To extract stop and search data for a custom area, you can use the following code:

    ```python
    poly_data = extract_stop_search(poly=[[51.5074, -0.1278], [51.5129, -0.1257], [51.5129, -0.1248]])
    ```

    To extract stop and search data for a specific date and location, you can use the following code:

    ```python
    date_location_data = extract_stop_search(date="2021-01", location_id="NC04")
    ```
    """

    # Get current year
    current_year = datetime.now().year

    # Get current month
    current_month = datetime.now().month
    if location_id != None:
        base_url = "http://data.police.uk/api/stops-at-location?"
    else: 
        base_url = 'https://data.police.uk/api/stops-street?'

    if date == None:
        if lat and lng != None:
            url = base_url + f"lat={lat}&lng={lng}&date={current_year}-{current_month}"
        elif poly != None:
            url = base_url + f"poly={poly[0][0]}:{poly[0][1]},{poly[1][0]}:{poly[1][1]},{poly[2][0]}:{poly[2][1]}&date={current_year}-{current_month}"
        elif location_id!= None:
            url = base_url + f"location_id={location_id}&date={current_year}-{current_month}"
        else:
            raise ValueError(f'Specify the lat/lang or poly that you passed or make sure they are correct: lat/lang-{lat, lng}, poly={poly}')
    
    elif date != None:
        if lat and lng != None:
            url = base_url + f"lat={lat}&lng={lng}&date={date}"
        elif poly != None:
            url = base_url + f"poly={poly[0][0]}:{poly[0][1]},{poly[1][0]}:{poly[1][1]},{poly[2][0]}:{poly[2][1]}&date={date}"
        elif location_id!= None:
            url = base_url + f"location_id={location_id}&date={date}"
        else:
            raise ValueError(f'Specify the lat/lang or poly that you passed or make sure they are correct: lat/lang-{lat, lng}, poly={poly}')
        
    else: 
        raise ValueError(f'Specify the date, you passed {date}')
   
   
    r = requests.get(url)
    list_of_dict = json.loads(r.content)

    return list_of_dict



def extract_stop_search_no_loc(date: str, force: str = None) -> list:
    """
    Extracts stop and search data for a specific police force without location.

    Parameters:
    -
    date (str): The date for which to retrieve data. If not specified,
        the current month will be used. The date should be specified in
        the format "YYYY-MM".
    force (str): The name of the police force for which to retrieve data.
        If not specified, data for all forces will be returned.

    Returns:
    -
    A list of dictionaries containing stop and search data for the specified
    date and force.

    Raises:
    -
    ValueError: If the date or force parameter is not specified.
    """

    base_url = 'https://data.police.uk/api/stops-no-location?'

    # Get current year
    current_year = datetime.now().year

    # Get current month
    current_month = datetime.now().month

    if date is None:
        if force is not None:
            url = f"https://data.police.uk/api/stops-no-location?force={force}&date={current_year}-{current_month}"
        else:
            raise ValueError("Please specify a date and force")
    elif force is not None:
        url = f"https://data.police.uk/api/stops-no-location?force={force}&date={date}"
    else:
        raise ValueError("Please specify a date and force")

    r = requests.get(url)
    list_of_dicts = json.loads(r.content)

    return list_of_dicts




def extract_stop_search_force(date: str = None, force: str = 'avon-and-somerset') -> list:
    """
    Extracts stop and search data for a specific police force.

    Parameters:
    ----------
    date (str): The date for which to retrieve data. If not specified,
        the current month will be used. The date should be specified in
        the format "YYYY-MM".
    force (str): The name of the police force for which to retrieve data.
        If not specified, data for all forces will be returned.

    Returns:
    -
    A list of dictionaries containing stop and search data for the specified
    date and force.

    Raises:
    -
    ValueError: If the date or force parameter is not specified.
    """
    # Get current year
    current_year = datetime.now().year

    # Get current month
    current_month = datetime.now().month

    if date is None:
        if force is not None:
            url = f"https://data.police.uk/api/stops-force?force={force}&date={current_year}-{current_month}"
        else:
            raise ValueError("Please specify a date and force")
    elif force is not None:
        url = f"https://data.police.uk/api/stops-force?force={force}&date={date}"
    else:
        raise ValueError("Please specify a date and force")

    r = requests.get(url)
    list_of_dicts = json.loads(r.content)

    return list_of_dicts



def download_file(url, save_dir):
    """
    Downloads a file from the specified URL and saves it to the specified directory.

    Parameters:
    url (str): The URL of the file to be downloaded.\n
    save_dir (str): The directory where the file will be saved.\n

    Returns:
    None

    Raises:
    None

    Examples:
    To download a file from a URL and save it to a directory, you can use the following code:

    ```python
    download_file("https://example.com/file.txt", "/path/to/save/directory")
    ```
    """
    # Extract filename from the URL
    filename = url.split('/')[-1]
    # Create directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    # Path to save the file
    save_path = os.path.join(save_dir, filename)
    # Send a GET request to the URL
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Write the content to the file
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully: {save_path}")
    else:
        print(f"Failed to download file from {url}")

    return save_path
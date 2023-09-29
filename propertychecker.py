import requests
import streamlit as st

def get_lat_lng_from_postcode(postcode, api_key):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={postcode}&key={api_key}"
    response = requests.get(geocode_url).json()
    if response['status'] == 'OK':
        location = response['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None

def get_distance_between_points(start_lat, start_lng, end_lat, end_lng, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lng}&destination={end_lat},{end_lng}&mode=walking&key={api_key}"
    response = requests.get(url).json()
    if response['status'] == 'OK':
        return response['routes'][0]['legs'][0]['distance']['text']
    return None

def get_commute_and_stations(start_postcode, end_postcode, api_key):
    # Convert start postcode to latitude and longitude
    start_lat, start_lng = get_lat_lng_from_postcode(start_postcode, api_key)
    if not start_lat or not start_lng:
        return "Unable to determine location for start postcode", [], None, None

    # Get commute time
    commute_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lng}&destination={end_postcode}&mode=transit&key={api_key}"
    commute_response = requests.get(commute_url).json()

    if commute_response['status'] == 'OK':
        commute_time = commute_response['routes'][0]['legs'][0]['duration']['text']
    else:
        commute_time = "Unable to determine commute time"

    # Get all train stations within the radius of the start location
    station_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={start_lat},{start_lng}&radius=3000&type=train_station&key={api_key}"
    station_response = requests.get(station_url).json()

    stations = []
    if station_response['status'] == 'OK':
        for station in station_response['results']:
            station_name = station['name']
            station_lat = station['geometry']['location']['lat']
            station_lng = station['geometry']['location']['lng']
            distance_to_station = get_distance_between_points(start_lat, start_lng, station_lat, station_lng, api_key)
            stations.append((station_name, distance_to_station))

    # Get all primary schools within the radius of the start location
    school_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={start_lat},{start_lng}&radius=1000&type=school&key={api_key}&keyword=primary"
    school_response = requests.get(school_url).json()

    primary_schools = []
    if school_response['status'] == 'OK':
        for school in school_response['results']:
            school_name = school['name']
            school_lat = school['geometry']['location']['lat']
            school_lng = school['geometry']['location']['lng']
            distance_to_school = get_distance_between_points(start_lat, start_lng, school_lat, school_lng, api_key)
            primary_schools.append((school_name, distance_to_school))

    return commute_time, stations, primary_schools

def main():
    st.title('Commute and Nearby Places Info')

    start_postcode = st.text_input("Enter Start Postcode:", "BR76PT")
    end_postcode = st.text_input("Enter End Postcode:", "SW1W 0DT")

    # Fetch the API key from Streamlit secrets
    api_key = st.secrets["google_maps_api_key"]

    if st.button('Get Info'):
        commute_time, stations, primary_schools = get_commute_and_stations(start_postcode, end_postcode, api_key)

        st.write(f"**Commute time:** {commute_time}")
        st.write("**Train stations within the radius:**")
        for station_name, distance in stations:
            st.write(f"{station_name} - {distance}")

        st.write("**Primary schools within the radius:**")
        for school_name, distance in primary_schools:
            st.write(f"{school_name} - {distance}")

if __name__ == "__main__":
    main()

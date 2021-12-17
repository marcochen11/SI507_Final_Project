
import json
import requests
import enquiries
from PIL import Image
from io import BytesIO
import webbrowser
import platform
import sys
import dataStruct

# get city list (either from local or new city list)
def get_cities():
    context = []
    f = open("./city_list.txt")
    context = f.readlines()
    f.close()
    city_list = []
    for line in context:
        city_list.append(line[:-1])
    return city_list

# Fetching data from yelp if using new city list
def fetch_data_from_yelp(city_list):
    yelp_data = {}
    url = "https://api.yelp.com/v3/businesses/search"
    api_key="slAadTod837ZvlDbMRIUDld3beBATuMgTU9O0_mfAqRsXSy3r4OkqjIYMXq8mQvvM_hnqrlpr5j1Up-u0mX_fCdz5pHN8U6duB0s8BCBabXcJpocwJUnaJWglgWfYXYx"
    headers = {'Authorization': 'Bearer %s' % api_key}
    for city in city_list:
        location=city
        location.replace(" ", "+")
        term = "restaurant"
        sort_by = "rating"
        params = {"term": term, "location": location, "sort_by": sort_by}
        yelp_response = requests.get(url, params=params, headers=headers)
        current_city_data=json.loads(yelp_response.text)
        yelp_data[city] = current_city_data
    dump_file = open("./new_raw_data.json", 'w')
    dump_file = json.dump(yelp_data, dump_file)
    return yelp_data

# Processing data in real time
def process_data(yelp_data, city_list):
    restaurant_info = dataStruct.restaurantsInfo(city_list)
    restaurant_info.put_info(yelp_data)
    selection_tree = dataStruct.selectionTree()
    selection_tree.build_tree(restaurant_info)
    dump_file = open("./restaurant_info.json", 'w')
    dump_file = json.dump(restaurant_info.return_info(), dump_file)
    dump_file = open("./selection_tree.json", 'w')
    dump_file = json.dump(selection_tree.return_tree(), dump_file)
    return restaurant_info, selection_tree

def main():
    city_list = get_cities()
    yelp_data = {}
    yelp_data = fetch_data_from_yelp(city_list)
    process_data(yelp_data, city_list)

if __name__ == "__main__":
    main()

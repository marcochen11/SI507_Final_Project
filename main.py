
import json
import requests
import enquiries
from PIL import Image
from io import BytesIO
import webbrowser
import platform
import sys

# get city list (either from local or new city list)
def get_cities(use_local):
    context = []
    if use_local=="true":
        f = open("./city_list.txt")
        context = f.readlines()
        f.close()
    else:
        f = open("./new_city_list.txt")
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
    dump_file = open("./new_raw_data", 'w')
    dump_file = json.dump(yelp_data, dump_file)
    return yelp_data

# Fetching data from local json is using local
def fetch_data_from_local_json():
    load_file = open("./raw_data", 'r')
    yelp_data = json.load(load_file)
    return yelp_data

def process_restaurant_dict(yelp_data, city_list):
    restaurant_dict = {}
    price_level = set()
    category_list = set()
    for city in city_list:
        restaurant_dict[city] = {}
        for business in yelp_data[city]["businesses"]:
            name = business["name"]
            try:
                price_level.add(business["price"])
            except:
                continue
            categories = []
            for category in business["categories"]:
                alias = category["alias"]
                categories.append(alias)
                category_list.add(alias)
            try:
                address = business["location"]["address1"] + business["location"]["city"]
            except:
                address = business["location"]["address1"]
            info = {"categories": categories, "price": business["price"], "image_url": business["image_url"], "url": business["url"], "address": address}
            restaurant_dict[city][name] = info
    return restaurant_dict

def process_selection_tree(restaurant_dict, city_list):
    selection_tree = {}
    for city in city_list:
        selection_tree[city] = {}
        restaurant_per_city = restaurant_dict[city]
        category_dict = {}
        for restaurant in restaurant_per_city.keys():
            info = restaurant_per_city[restaurant]
            for category in info["categories"]:
                if category in category_dict:
                    category_dict[category][restaurant] = (restaurant_per_city[restaurant])
                else:
                    category_dict[category] = {restaurant: restaurant_per_city[restaurant]}
        for category in category_dict.keys():
            selection_tree[city][category] = {}
            for restaurant in category_dict[category].keys():
                info = category_dict[category][restaurant]
                if info["price"] in selection_tree[city][category]:
                    selection_tree[city][category][info["price"]].append(restaurant)
                else:
                    selection_tree[city][category][info["price"]] = [restaurant]
    return selection_tree

# Processing data in real time
def process_data(yelp_data, city_list):
    restaurant_dict = process_restaurant_dict(yelp_data, city_list)
    selection_tree = process_selection_tree(restaurant_dict, city_list)
    dump_file = open("./processed_data", 'w')
    dump_file = json.dump(restaurant_dict, dump_file)
    dump_file = open("./processed_tree", 'w')
    dump_file = json.dump(selection_tree, dump_file)
    return restaurant_dict, selection_tree

# Using google API to calculate time to restaurant
def time_to_restaurant(start_address, dest_address):
    if start_address == "":
        start_address = "University of Michigan"
    start_address.replace(" ", "+")
    dest_address.replace(" ", "+")
    response = requests.get("https://maps.googleapis.com/maps/api/directions/json?origin=" + start_address + \
        "&destination=" + dest_address + "&key=AIzaSyAop8k5FFJsrzpzkIxlxu23n4zV3iO4z90")
    data=json.loads(response.text)
    # print(data["routes"][0]["legs"][0]["duration"]["text"])
    # print(data["routes"][0]["legs"][0]["duration"]["value"])
    return data["routes"][0]["legs"][0]["duration"]["text"]

def front_end(restaurant_dict, selection_tree):
    # Ask for user's preference
    city = enquiries.choose('Choose one of these cities you are looking for restaurant in: ', list(selection_tree.keys()))
    category = enquiries.choose('Choose category of your preferred type of restaurant: ', list(selection_tree[city].keys()))
    price_level = enquiries.choose('Choose price level your restaurant: ', list(selection_tree[city][category].keys()))
    restaurant = enquiries.choose('Choose your restaurant: ', selection_tree[city][category][price_level])
    address = input("Enter your current address(if enter nothing, your default address will be university of michigan): ")
    info = restaurant_dict[city][restaurant]
    # Popping info based on users preference
    print("here's an overview of your restaurant: ")
    print("City    : " + city)
    print("Name    : " + restaurant)
    print("Category: ", end = "")
    for alias in info["categories"]:
        print(alias, end = " ")
    print()
    print("Price   : " + info["price"])
    print("It will take you " + time_to_restaurant(address, info["address"]) + "' drive to the restaurant")
    url = info['image_url']
    # Popping image based on user's operating system
    show_image = enquiries.choose('Do you want to see some picture of the restaurant: ', ["yes","no"])
    if show_image=="yes":
        if platform.system() == "Windows":
            webbrowser.open(url)
        else:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            img.show()
    browser = enquiries.choose("Do you want to open the yelp page of this restaurant for more details? ", ["yes", "no"])
    if browser == "yes":
        webbrowser.open(info["url"])
    again = enquiries.choose("Are you satified with your search result? ", ["yes", "no"])
    # Recursively recommend restaurant if user is not satisfied with the result
    if again == "yes":
        print("Have a wonderful day!")
    else:
        front_end(restaurant_dict, selection_tree)

def main(use_local):
    city_list = get_cities(use_local)
    yelp_data = {}
    if use_local=="true":
        yelp_data = fetch_data_from_local_json()
    else:
        yelp_data = fetch_data_from_yelp(city_list)
    restaurant_dict, selection_tree = process_data(yelp_data, city_list)
    front_end(restaurant_dict, selection_tree)

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1][0:10] != "use_local=" or (sys.argv[1][10:] != "true" and sys.argv[1][10:] != "false"):
        print("Usage: python3 main.py use_local=[true/false]")
    else:
        main(sys.argv[1][10:])




import json
import requests
import enquiries
from PIL import Image
from io import BytesIO
import webbrowser
import platform
import sys
import processData

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

# Processing data in real time
def process_data(yelp_data, city_list):
    restaurant_info = processData.restaurantsInfo(city_list)
    restaurant_info.put_info(yelp_data)
    selection_tree = processData.selectionTree()
    selection_tree.build_tree(restaurant_info)
    dump_file = open("./processed_data", 'w')
    dump_file = json.dump(restaurant_info.return_info(), dump_file)
    dump_file = open("./processed_tree", 'w')
    dump_file = json.dump(selection_tree.return_tree(), dump_file)
    return restaurant_info, selection_tree

# Using google API to calculate time to restaurant
def time_to_restaurant(start_address, dest_address, key):
    if start_address == "":
        start_address = "University of Michigan"
    start_address.replace(" ", "+")
    dest_address.replace(" ", "+")
    response = requests.get("https://maps.googleapis.com/maps/api/directions/json?origin=" + start_address + \
        "&destination=" + dest_address + "&key=" + key)
    data=json.loads(response.text)
    return data["routes"][0]["legs"][0]["duration"]["text"]

def front_end(restaurant_info, selection_tree, key):
    # Ask for user's preference
    city = enquiries.choose('Choose one of these cities you are looking for restaurant in: ', sorted(selection_tree.get_city_list()))
    category = enquiries.choose('Choose category of your preferred type of restaurant: ', sorted(selection_tree.get_category_list(city)))
    price_level = enquiries.choose('Choose price level your restaurant: ', sorted(selection_tree.get_price_list(city, category)))
    restaurant = enquiries.choose('Choose your restaurant: ', sorted(selection_tree.get_final_recommend_list(city, category, price_level)))
    address = ""
    if key != "":
        address = input("Enter your current address(if enter nothing, your default address will be university of michigan): ")
    info = restaurant_info.get_restaurant_info(city, restaurant)
    # Popping info based on users preference
    print("here's an overview of your restaurant: ")
    print("City    : " + city)
    print("Name    : " + restaurant)
    print("Category: ", end = "")
    for alias in info["categories"]:
        print(alias, end = " ")
    print()
    print("Price   : " + info["price"])
    if key != "":
        print("It will take you " + time_to_restaurant(address, info["address"], key) + "' drive to the restaurant")
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
        front_end(restaurant_info, selection_tree, key)

def main(use_local, key):
    city_list = get_cities(use_local)
    yelp_data = {}
    if use_local=="true":
        yelp_data = fetch_data_from_local_json()
    else:
        yelp_data = fetch_data_from_yelp(city_list)
    restaurant_info, selection_tree = process_data(yelp_data, city_list)
    front_end(restaurant_info, selection_tree, key)

if __name__ == "__main__":
    if len(sys.argv) == 2 or len(sys.argv) == 3:
        if sys.argv[1][0:10] != "use_local=" or (sys.argv[1][10:] != "true" and sys.argv[1][10:] != "false"):
            print("Usage: python3 main.py use_local=[true/false]")
            print("Or   : python3 main.py use_local=[true/false] key=[key]")
        else:
            if len(sys.argv) == 2:
                main(sys.argv[1][10:], "")
            else:
                main(sys.argv[1][10:], sys.argv[2][4:])
    else:
        print("Usage: python3 main.py use_local=[true/false]")
        print("Or   : python3 main.py use_local=[true/false] key=[key]")



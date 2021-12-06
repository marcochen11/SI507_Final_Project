
import json
import requests
import enquiries
from PIL import Image
from io import BytesIO
import webbrowser
import platform

def get_cities():
    f = open("./city_list.txt")
    context = f.readlines()
    f.close()
    city_list = []
    for line in context:
        city_list.append(line[:-1])
    return city_list

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
    dump_file = open("./raw_data", 'w')
    dump_file = json.dump(yelp_data, dump_file)
    return yelp_data

def fetch_data_from_local_json():
    load_file = open("./raw_data", 'r')
    yelp_data = json.load(load_file)
    return yelp_data

def process_data(yelp_data, city_list):
    selection_tree = {}
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
    dump_file = open("./processed_data", 'w')
    dump_file = json.dump(restaurant_dict, dump_file)
    dump_file = open("./processed_tree", 'w')
    dump_file = json.dump(selection_tree, dump_file)
    return restaurant_dict, selection_tree

def front_end(restaurant_dict, selection_tree):
    city = enquiries.choose('Choose one of these cities you are looking for restaurant in: ', list(selection_tree.keys()))
    category = enquiries.choose('Choose category of your preferred type of restaurant: ', list(selection_tree[city].keys()))
    price_level = enquiries.choose('Choose price level your restaurant: ', list(selection_tree[city][category].keys()))
    restaurant = enquiries.choose('Choose your restaurant: ', selection_tree[city][category][price_level])
    info = restaurant_dict[city][restaurant]
    print("here's an overview of your restaurant: ")
    print("Name    : " + restaurant)
    print("Category: ", end = "")
    for alias in info["categories"]:
        print(alias, end = " ")
    print()
    print("Price   : " + info["price"])
    url = info['image_url']
    print(platform.system())
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
    if again == "yes":
        print("Have a wonderful day!")
    else:
        front_end(restaurant_dict, selection_tree)

def main():
    city_list = get_cities()
    yelp_data = {}
    use_local_data = True
    if use_local_data:
        yelp_data = fetch_data_from_local_json()
    else:
        yelp_data = fetch_data_from_yelp(city_list)
    restaurant_dict, selection_tree = process_data(yelp_data, city_list)
    front_end(restaurant_dict, selection_tree)

if __name__ == "__main__":
    main()



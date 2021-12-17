class restaurantsInfo:
    def __init__(self, city_list):
        self.info = {}
        self.city_list = city_list
        for city in city_list:
            self.info[city] = {}

    def get_city_list(self):
        return self.city_list
    
    def get_info_of_city(self, city):
        return self.info[city]

    def put_info(self, yelp_data):
        for city in self.city_list:
            self.put_info_per_city(city, yelp_data[city])
    
    def put_info_per_city(self, city, city_data):
        for business in city_data["businesses"]:
            name, price, categories, image_url, website_url, address = self.extract_info_of_restaurant(business)
            restaurant_info = {"categories": categories, "price": price, "image_url": image_url, "url": website_url, "address": address}
            self.info[city][name] = restaurant_info

    def extract_info_of_restaurant(self, business):
        name = business["name"]
        try:
            price = business["price"]
        except:
            price = "$"
        categories = []
        for category in business["categories"]:
            alias = category["alias"]
            categories.append(alias)
        try:
            address = business["location"]["address1"] + business["location"]["city"]
        except:
            address = business["location"]["address1"]
        image_url = business["image_url"]
        website_url = business["url"]
        return name, price, categories, image_url, website_url, address
    
    def return_info(self):
        return self.info
    
    def get_restaurant_info(self, city, name):
        return self.info[city][name]

    def load_from_json(self, info):
        self.info = info


class selectionTree:
    def __init__(self):
        self.tree = {}
        self.city_list = []

    def put_city_list(self, city_list):
        self.city_list = city_list
    
    def build_tree(self, restaurant_info):
        self.city_list = restaurant_info.get_city_list()
        for city in self.city_list:
            self.tree[city] = {}
            city_info = restaurant_info.get_info_of_city(city)
            self.build_city(city, city_info)

    def build_city(self, city, city_info):
        for restaurant in city_info:
            self.add_restaurant(city, restaurant, city_info[restaurant])
    
    def add_restaurant(self, city, restaurant, restaurant_info):
        for category in restaurant_info["categories"]:
            if category in self.tree[city]:
                if restaurant_info["price"] in self.tree[city][category]:
                    self.tree[city][category][restaurant_info["price"]].append(restaurant)
                else:
                    self.tree[city][category][restaurant_info["price"]] = [restaurant]
            else:
                self.tree[city][category] = {restaurant_info["price"]: [restaurant]}
    
    def return_tree(self):
        return self.tree
    
    def get_city_list(self):
        return self.city_list
    
    def get_category_list(self, city):
        return list(self.tree[city].keys())
    
    def get_price_list(self, city, category):
        return list(self.tree[city][category].keys())
    
    def get_final_recommend_list(self, city, category, price_level):
        return self.tree[city][category][price_level]
    
    def load_from_json(self, tree):
        self.tree = tree


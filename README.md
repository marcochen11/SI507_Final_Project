# SI507_Final_Project
Prerequirement:
1.  need to install enquiries module

    pip3 install enquiries

Usage:  python3 main.py use_local=[true/false]

Or   :  python3 main.py use_local=[true/false] key=[key] 

key is the API key provided in the report

Using the key will enable the function that tells your distance from your current location to destination

By setting use_local as false, you will fetch data from yelp fusion based on cities included in [new_city_list.txt] instead of using local data

You can change the city list by editing the [new_city_list.txt] file


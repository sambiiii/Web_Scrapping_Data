import config
from bs4 import SoupStrainer
from datetime import datetime

config.establishment_name = 'Greggs' #replace
n_menu_section_levels = 1 #1 or 2 may not match number for webscraping
config.scrape_date = "2023_04"#datetime.date.today().strftime('%Y_%m') ##replace
PC = "citrix" #"personal"/"citrix"/"work"  #replace

# location_menu_section_l1_tagname = "div" #replace
# location_menu_section_l1_attribute_name = "class" #replace
# location_menu_section_l1_attribute_content = "relative flex w-full flex-nowrap justify-start gap-1 overflow-x-auto whitespace-nowrap py-6" #replace

l1_sections_tagname = "span" #replace
l1_sections_attribute_name = "class" #replace
l1_sections_attribute_content = "text-brand-primary-blue inline-block flex-auto items-center text-lg font-semibold lg:mx-auto lg:mt-1 lg:max-w-[100px] lg:text-xl lg:font-bold lg:leading-10" #replace

# location_menu_section_l2_tagname = "xx" #replace
# location_menu_section_l2_attribute_name = "xx" #replace
# location_menu_section_l2_attribute_content = "xx" #replace

# l2_sections_tagname = "xx" #replace
# l2_sections_attribute_name = "xx" #replace
# l2_sections_attribute_content = "xx" #replace

item_tagname = "h1" #replace
item_attribute_name = "class" #replace
item_attribute_content = "text-brand-primary-blue lg:text-left text-center lg:text-8xl text-5xl mb-8 mt-8 lg:mb-0 lg:mt-15 px-5 lg:px-0 leading-sm lg:col-start-1 lg:col-span-3" #replace

# only_specified_tags = SoupStrainer([location_menu_section_l1_tagname, l1_sections_tagname, "xx", "xx"]) #Optional. Only for huge files that take forever to parse.
# if need to find element that INCLUDES attribute content: items_dict["item_name"].append(item.parent.parent.select('span[class*="name"]')[0].get_text().replace('\\n','').strip()) #Added [0] has the only way to find class names CONTAINING the word "name" was to use the Select (CSS selector), which find all elementS. While get_text() only works on single element.
# if need to find element with specific string:         items_dict["energy_kcal_per_serve"].append(item.parent.find("h5", {"data-testid": "per-serving-header"}).next_sibling.find("span", string = "Energy").next_sibling.get_text().strip().split("/")[0].strip(" kcal")) #.replace(",", "").strip()
#replace('\\n','')


#Need manual editing of block starting line ~140

# 0. SET-UP
print("***STEP 0: SET-UP***")
from bs4 import BeautifulSoup
import sqlite3
import itertools
import os.path
import os
import re
from pathlib import Path
import sys
import pandas as pd
from sqlalchemy import create_engine 
from sql_paths import *
from sql_retrieve_business_scrape_ids import *

# Path + Filenames
check_PC(PC)

# Check whether DB exists
check_DB()

# Retrieve business_id and scrape_no from the month's DB
sql_connect()
get_business_id() #If this function fails, it's probably because the establishment name is wrong in the All_OOH_Cohort excel file
get_scrape_no()

# 1. FROM HTML TO DATAFRAME
print("***STEP 1: FROM HTML TO DATAFRAME***")
html = open(config.html_fname, "r")
soup = BeautifulSoup(html, "lxml") #Can use "lxml" if too slow. #And/or can add ", parse_only = only_specified_tags" as last argument if  necessary

# 1.1 Find menu sections L1 in HTML
print("***STEP 1.1: find menu sections L1 in HTML***")
# location_menu_section_l1 = soup.find(location_menu_section_l1_tagname, attrs = {location_menu_section_l1_attribute_name: location_menu_section_l1_attribute_content})
l1_sections = soup.find_all(l1_sections_tagname, attrs={l1_sections_attribute_name: l1_sections_attribute_content}) 
print("Step 1.1: There are ", len(l1_sections), " menu sections.")

l1_sections_dict = {"l1_menu_section": [],
                    "business_id": []}
i_l1_section = 1
for l1_section in l1_sections:
    l1_sections_dict["l1_menu_section"].append(l1_section.text.replace('\\n','').strip())
    l1_sections_dict["business_id"].append(config.business_id) 
    print("loop done: section number ", i_l1_section)
    i_l1_section = i_l1_section + 1
    
l1_sections_df = pd.DataFrame.from_dict(l1_sections_dict).drop_duplicates(keep = "first")
print(l1_sections_df.head(5))

exec(open(config.sql_df_to_db_sections_l1_script).read())

if n_menu_section_levels == 2: 
    # 1.2 Find menu sections L2 in HTML
    print("***STEP 1.2: find menu sections L2 in HTML***")
    location_menu_section_l2 = soup.find(location_menu_section_l2_tagname, attrs = {location_menu_section_l2_attribute_name: location_menu_section_l2_attribute_content})
    l2_sections = location_menu_section_l2.find_all(l2_sections_tagname, attrs={l2_sections_attribute_name: l2_sections_attribute_content}) 
    print("Step 1.2: There are ", len(l2_sections), " menu sections.")
    
    l2_sections_dict = {"l2_menu_section": [],
                        "l1_menu_section_id": []}
    i_l2_section = 1
    for l2_section in l2_sections:
        l2_sections_dict["l2_menu_section"].append(l2_section.text.replace('\\n','').strip())
        config.l1_menu_section = l2_section.parent.parent.previous_sibling.previous_sibling.find(l1_sections_tagname, attrs={l1_sections_attribute_name: l1_sections_attribute_content}).get_text().strip()
        get_l1_menu_section_id()
        l2_sections_dict["l1_menu_section_id"].append(config.l1_menu_section_id) 
 
        print("loop done: section number ", i_l2_section)
        i_l2_section = i_l2_section + 1
        
    l2_sections_df = pd.DataFrame.from_dict(l2_sections_dict).drop_duplicates(keep = "first")
    print(l2_sections_df.head(5))

          
# 1.3 Find menu items in HTML
print("***STEP 1.3: find menu items in HTML***")
items = soup.find_all(item_tagname, attrs = {item_attribute_name: item_attribute_content})
print("Step 1.3: there are ", len(items), " items")
items_dict = {"l1_menu_section" : [],
              "l2_menu_section" : [],
              "item_name": [],
              "item_description" : [], 
              "ingredients_list" : [], 
              "portion_weight" : [], 
              "energy_kcal_per_serve" : [], 
              "energy_kcal_per_100" : [], 
              "carb_g_per_serve" : [], 
              "carb_g_per_100" : [], 
              "sugars_g_per_serve" : [], 
              "sugars_g_per_100" : [], 
              "totalfat_g_per_serve" : [], 
              "totalfat_g_per_100" : [], 
              "satfat_g_per_serve" : [], 
              "satfat_g_per_100" : [], 
              "protein_g_per_serve" : [], 
              "protein_g_per_100" : [], 
              "salt_g_per_serve" : [], 
              "salt_g_per_100" : [],
              "fibre_g_per_serve" : [], 
              "fibre_g_per_100" : [],
              "business_id" : [],
              "l1_menu_section_id" : [],
              "l2_menu_section_id" : [],
              "salt_target_id" : [],
              "scrape_no" : []}

i_item = 1
for item in items:
    items_dict["l1_menu_section"].append("NA") #13.09.2022. From what I've webscraped in 08.2022, there is no way to find out which menu section each item belongs to. That will need to be sorted at the next webscrape.
    # items_dict["l1_menu_section"].append(item.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.find("span", {"class": "text-brand-primary-blue inline-block flex-auto items-center text-lg font-semibold lg:mx-auto lg:mt-1 lg:max-w-[100px] lg:text-xl lg:font-bold lg:leading-10"}).get_text().replace('\\n','').strip())
    items_dict["l2_menu_section"].append("NA")
    items_dict["item_name"].append(item.get_text().replace('\\n','').strip())
    try: 
        items_dict["item_description"].append(item.next_sibling.next_sibling.next_sibling.next_sibling.get_text().replace('\\n','').strip())
    except: 
        items_dict["item_description"].append("NA")
    try: 
        items_dict["ingredients_list"].append(item.find("xx", {"xx": "xx"}).get_text().strip())
    except: 
        items_dict["ingredients_list"].append("NA")
    try: 
        items_dict["portion_weight"].append(item.parent.parent.parent.parent.parent.next_sibling.find_all("td", {"class": "text-blue-grey font-extrabold text-sm"})[1].get_text().split("(")[1].replace('g)','').replace('\\n','').strip())
    except: 
        items_dict["portion_weight"].append("NA")
    try: 
        items_dict["energy_kcal_per_serve"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Energy kcal')).next_sibling.next_sibling.next_sibling.next_sibling.get_text().replace('kcal','').replace('\\n','').strip()) #Convoluted way to find the extact string to look for (tricky because tehre are //n and /n.)
    except: 
        items_dict["energy_kcal_per_serve"].append("NA")
    try: 
        items_dict["energy_kcal_per_100"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Energy kcal')).next_sibling.next_sibling.get_text().replace('kcal','').replace('\\n','').strip())
    except: 
        items_dict["energy_kcal_per_100"].append("NA")
    try: 
        items_dict["carb_g_per_serve"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Carbohydrate')).next_sibling.next_sibling.next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["carb_g_per_serve"].append("NA")
    try: 
        items_dict["carb_g_per_100"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Carbohydrate')).next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["carb_g_per_100"].append("NA")
    try: 
        items_dict["sugars_g_per_serve"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'of which Sugars')).next_sibling.next_sibling.next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["sugars_g_per_serve"].append("NA")
    try: 
        items_dict["sugars_g_per_100"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'of which Sugars')).next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["sugars_g_per_100"].append("NA")
    try: 
        items_dict["totalfat_g_per_serve"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Fat')).next_sibling.next_sibling.next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["totalfat_g_per_serve"].append("NA")
    try: 
        items_dict["totalfat_g_per_100"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Fat')).next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["totalfat_g_per_100"].append("NA")
    try: 
        items_dict["satfat_g_per_serve"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'of which Saturates')).next_sibling.next_sibling.next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["satfat_g_per_serve"].append("NA")
    try: 
        items_dict["satfat_g_per_100"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'of which Saturates')).next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["satfat_g_per_100"].append("NA")
    try: 
        items_dict["protein_g_per_serve"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Protein')).next_sibling.next_sibling.next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["protein_g_per_serve"].append("NA")
    try: 
        items_dict["protein_g_per_100"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Protein')).next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["protein_g_per_100"].append("NA")
    try: 
        items_dict["salt_g_per_serve"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Salt')).next_sibling.next_sibling.next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["salt_g_per_serve"].append("NA")
    try: 
        items_dict["salt_g_per_100"].append(item.parent.parent.parent.parent.parent.next_sibling.find("table", class_ = "w-full").find("td", class_ = "text-blue-grey text-left", string = re.compile(r'Salt')).next_sibling.next_sibling.get_text().replace('g','').replace('\\n','').strip())
    except: 
        items_dict["salt_g_per_100"].append("NA")
    try: 
        items_dict["fibre_g_per_serve"].append(item.find("xx", {"xx": "xx"}).get_text().strip())
    except: 
        items_dict["fibre_g_per_serve"].append("NA")
    try: 
        items_dict["fibre_g_per_100"].append(item.find("xx", {"xx": "xx"}).get_text().strip())
    except: 
        items_dict["fibre_g_per_100"].append("NA")
    items_dict["business_id"].append(config.business_id) 
    items_dict["l1_menu_section_id"].append("NA") #leave as NA
    items_dict["l2_menu_section_id"].append("NA") #leave as NA
    items_dict["salt_target_id"].append("NA") #leave as NA
    items_dict["scrape_no"].append(config.scrape_no) #leave as NA
    print("loop done: item number ", i_item)
    i_item = i_item + 1
 
#13.09.2022 Extra lines to manually fix l1 menu section to each item. Temporary fix. 
# section 0: item 0-19 (20)
# section 1: item 20-29 (10)
# section 2: item 30-62 (33)
# section 3: item 63-80 (18)
# section 4: item 81-102 (22)
# section 5: item 103-111 (9)

# list_l1_sections = [list(l1_sections_df["l1_menu_section"])[0], list(l1_sections_df["l1_menu_section"])[1], list(l1_sections_df["l1_menu_section"])[2], list(l1_sections_df["l1_menu_section"])[3], list(l1_sections_df["l1_menu_section"])[4], list(l1_sections_df["l1_menu_section"])[5]]
list_l1_sections = list(l1_sections_df["l1_menu_section"])
list_repeat = [20, 10, 33, 18, 22, 9]

items_dict['l1_menu_section'] = []
for idx in range(len(list_l1_sections)):
    for count in range(list_repeat[idx]):
        items_dict['l1_menu_section'].append(list_l1_sections[idx])
    ##End of fix
items_df = pd.DataFrame.from_dict(items_dict).drop_duplicates(keep = "first")
print(items_df.head(5))

# # 2. FROM DATAFRAME TO SQL DB
exec(open(config.sql_df_to_db_sections_l2_script).read())
exec(open(config.sql_df_to_db_items_script).read())
# df = config.items_to_append_df.applymap(str) #Can be used to view items_to_append_df in case it isn't pickable itself 
config.items_to_append_df.to_sql(con = config.conn, name = "MenuItems", if_exists='append', index=False)

print("***FINISH**")    
config.conn.close()
    

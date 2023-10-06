PC = "citrix" #"personal"/"citrix"

# Brief description of website:
import config
config.name = 'Greggs' #replace
url = 'https://www.greggs.co.uk/menu' #replace
popups = "True"#"True"/"False" #replace
search_string_popups = '//*[@id="onetrust-reject-all-handler"]' #replace
method = 3 #replace (1 = scrape full page; 2 = scrape specific pages; 3 = pop-up items)


if method != 1:
    n_menu_section_levels = 1 #replace
    find_method_location_menu_section_l1 = 'By.CSS_SELECTOR' #replace
    search_string_location_menu_section_l1 = '#content > div > div.mb-8.md\:mb-16 > div.top-headerHeight.sticky.z-10.w-full.bg-white > div > div > div > div > div'#'#content > div > div.mb-8.md\:mb-16.storyblok__outline > div.max-w-8xl.container.space-y-12.px-5 > div > section > div'#'//*[@id="content"]/div/div/div[4]/div[3]/div/span/section/div' #replace
    find_method_elements_menu_section_l1 = 'xxx' #replace
    search_string_elements_menu_section_l1 = 'xxx' #replace
    #By.XPATH
    #By.CSS_SELECTOR
    #By.CLASS_NAME
    #By.ID
    #By.NAME
    #By.LINK_TEXT
    #By.PARTIAL_LINK_TEXT
    #By.TAG_NAME

    if n_menu_section_levels > 1:
        find_method_location_menu_section_l2 = 'xxx' #replace
        search_string_location_menu_section_l2 = 'xxx' #replace
        find_method_elements_menu_section_l2 = 'xxx' #replace
        search_string_elements_menu_section_l2 = 'xxx' #replace
        menu_section_l2_hidden = 'xxx' #"True"/"False" #replace

if method == 3:
    find_method_items = 'By.XPATH' #replace
    search_string_items = '//a[@href and contains(@class, "container")]' #replace
    find_method_close_items = 'xxx' #replace
    search_string_close_items = 'xxx' #replace




# element = driver.find_element(By.CLASS_NAME, "element_class_name")
# element = driver.find_element(By.ID, "element_id")
# element = driver.find_element(By.NAME, "element_name")
# element = driver.find_element(By.LINK_TEXT, "element_link_text")
# element = driver.find_element(By.PARTIAL_LINK_TEXT, "element_partial_link_text")
# element = driver.find_element(By.TAG_NAME, "element_tag_name")
# element = driver.find_element(By.CSS_SELECTOR, "element_css_selector")
# element = driver.find_element(By.XPATH, "element_xpath")


# 0. PREP

# 0.1 Import modules
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import os.path
import os
import re
from pathlib import Path
import sys
import datetime
from webscraping_functions import *
import webscraping_paths
import requests
from bs4 import BeautifulSoup

# 0.3 Set up config.folders and files
webscraping_paths.check_PC(PC) # Determine path for folders depending on which PC is used
config.html_file = os.path.join(config.folder, config.name + "_html_" + config.today + ".txt")

if os.path.exists(config.html_file):
    print("***ERROR: HTML FILE ALREADY EXISTS. QUITTING PROGRAMME NOW.***")
    exit()
    
# 0.4 Set up driver + sleep
navigate_to(url) #Will open browser, navigate to URL, maximise window

# 0.6 Close pop-ups, banners, etc.
if popups == "True":
    close_cookies = config.driver.find_element(By.XPATH, search_string_popups)
    click(close_cookies)
    
print("***Step 0.6 Close pop-ups : DONE***")

# 1. SCRAPE
print("HOMEPAGE START", file=open(config.html_file, "a"))
scrape_current_page() #Scrape home page to get menu sections
print("HOMEPAGE END", file=open(config.html_file, "a"))

items_urls = []

location_menu_section_l1 = config.driver.find_element(By.CSS_SELECTOR, search_string_location_menu_section_l1)  #replace
print("***Method 2: location_menu_section_l1 found***")
print(location_menu_section_l1.text)
items = location_menu_section_l1.find_elements(By.XPATH, search_string_items) #replace
print("***Method 3: items found. There are ", len(items), " different items in total (across all menu sections)***")

#Extracting URLs of each item in this given menu section
for item in items: 
    items_urls.append(item.get_attribute('href'))

print("***Extra: URLs of all items of all menu sections extracted.***") 
print(items_urls)

print("ITEM SCRAPE START", file=open(config.html_file, "a"))
i_items_url = 1
for items_url in items_urls: 
    print("***Extra: Navigating to URL item number ", i_items_url, " out of ", len(items_urls), " ***")
    print(items_url)
    try: 
        navigate_to(items_url)
    except:
        try: 
            sleep(120)
            navigate_to(items_url)
        except:
            sleep(240)
            navigate_to(items_url)
    scrape_current_page()
    i_items_url = i_items_url + 1
    
print("ITEM SCRAPE END", file=open(config.html_file, "a"))

# 2. FINISH OFF
print("***QUITTING***")
config.driver.quit()

method = 4
url = "https://www.greggs.co.uk/nutrition"

# 0.3 Set up config.folders and files
webscraping_paths.check_PC(PC) # Determine path for folders depending on which PC is used

if method == 4:
    config.pdf_file = os.path.join(config.folder, config.name + "_pdf_" + config.today + "1" + ".pdf")
    
    if os.path.exists(config.pdf_file):
        print("***ERROR: PDF FILE ALREADY EXISTS. QUITTING PROGRAMME NOW.***")
        exit()
    
# 0.4 Set up driver + sleep
navigate_to(url) #Will open browser, navigate to URL, maximise window

# 1. SCRAPE


if method == 4:
    # Requests URL and get response object
    response = requests.get(url, verify=False)
      
    # Parse text obtained
    soup = BeautifulSoup(response.text, 'html.parser')
      
    # Find all hyperlinks present on webpage
    links = soup.find_all('a')
      
    i = 0
      
    # From all links check for pdf link and
    # if present download file
    for link in links:
        if (('Nutrition' in link.get('href', []) or 'nutrition' in link.get('href', [])) and '.pdf' in link.get('href', [])):
            i += 1
            print("Downloading file: ", i)
      
            # Get response object for link
            response = requests.get(link.get('href'))
      
            # Write content in pdf file
            pdf = open(os.path.join(config.folder, config.name + "_pdf_" + config.today + "_file" + str(i) + ".pdf"), "wb")
            pdf.write(response.content)
            pdf.close()
            print("File ", i, " downloaded")
            sleep(10)
      
    print("All PDF files downloaded")

# 2. FINISH OFF
print("***QUITTING***")
config.driver.quit()

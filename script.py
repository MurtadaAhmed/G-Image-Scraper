from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import json
import urllib.request
import time
import requests
from PIL import Image
import io
import hashlib
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

cookies_accept_button_id = 'L2AGLb'
thumdnail_class_css_selector = 'img.YQ4gaf'
full_image_class_css_selector = 'img.sFlh5c.pT0Scc.iPVvYb'
firefox_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'

def fetch_image_urls(query, max_links_to_fetch, wd, sleep_between_interactions):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(sleep_between_interactions)

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    wd.get(search_url.format(q=query))

    try:
        accept_cookies_button = WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.ID, cookies_accept_button_id))  # Use the id to locate the button
        )
        accept_cookies_button.click()
    except Exception as e:
        print(f"Error accepting cookies: {e}")

    image_urls = set()
    image_count = 0
    result_start = 0

    while image_count < max_links_to_fetch:
        scroll_to_end(wd)
        thumbnail_results = wd.find_elements(By.CSS_SELECTOR, thumdnail_class_css_selector)
        number_results = len(thumbnail_results)

        print(f"Found {number_results} search results. Extracting links from {result_start}:{number_results}")

        for img in thumbnail_results[result_start:number_results]:
            try:
                ActionChains(wd).move_to_element(img).perform()
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            try:
                WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, full_image_class_css_selector)))
                actual_images = wd.find_elements(By.CSS_SELECTOR, full_image_class_css_selector)
            except Exception:
                continue

            for actual_image in actual_images:
                if actual_image.get_attribute("src") and "http" in actual_image.get_attribute("src"):
                    image_urls.add(actual_image.get_attribute("src"))
            
            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"found: {len(image_urls)} image links")
                break
        else:
            print(f"Found {len(image_urls)} image links, looking for more...")
            time.sleep(30)
        
        result_start = len(thumbnail_results)
    return image_urls

def persist_image(folder_path, url):
    try:
        image_content = requests.get(url, verify=False).content

    except Exception as e:
        print(f"Error - could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[0:10] + ".jpg")
        with open(file_path, "wb") as f:
            image.save(f, "JPEG", quality=85)
        print(f"Success - saved {url} - as {file_path}")
    except Exception as e:
        print(f"Error - could not save {url} - {e}")

def search_and_download(search_term, driver_path, number_images=10, target_path="./images" ):
    target_folder = os.path.join(target_path, "_".join(search_term.lower().split(" ")))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Create a new Firefox service
    s = Service(driver_path)

    # Specify the path to the Firefox binary
    options = Options()
    options.binary_location = firefox_path

    # Create a new instance of the Firefox driver
    with webdriver.Firefox(options=options, service=s) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)

    for elem in res:
        persist_image(target_folder, elem)

keyword_to_search = input("Enter the keyword to search: ")
number_of_images_to_download = int(input("Enter the number of images to download (default 10): "))


search_and_download(keyword_to_search, 'geckodriver.exe', number_of_images_to_download)


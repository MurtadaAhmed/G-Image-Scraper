import os
import sys
import time
import requests
from PIL import Image
import io
import hashlib
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from wand.image import Image as WandImage

cookies_accept_button_id = 'L2AGLb'
cookies_accept_button_id_2 = "VfPpkd-vQzf8d"
thumdnail_class_css_selector = 'img.YQ4gaf'
full_image_class_css_selector = 'img.sFlh5c.pT0Scc.iPVvYb'
firefox_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'
close_image_review_button = 'button.uj1Jfd.wv9iH.iM6qI'

if getattr(sys, 'frozen', False):
    script_dir = sys._MEIPASS  # If running as executable
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # If running as script

geckodriver_path = os.path.join(script_dir, 'geckodriver.exe')


def fetch_image_urls(query, max_links_to_fetch, wd, sleep_between_interactions):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    def scroll_to_top(wd):
        wd.execute_script("window.scrollTo(0, 0);")
        time.sleep(sleep_between_interactions)

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    wd.get(search_url.format(q=query))

    try:
        accept_cookies_button = WebDriverWait(wd, 1).until(
            EC.presence_of_element_located((By.ID, cookies_accept_button_id))  # Use the id to locate the button
        )
        accept_cookies_button.click()
    except Exception as e:
        print(f"Error accepting cookies: {e}")

    try:
        accept_cookies_button_2 = WebDriverWait(wd, 1).until(
            EC.presence_of_element_located((By.ID, cookies_accept_button_id_2))
        )
        accept_cookies_button_2.click()
    except Exception as e:
        print(f"Error accepting cookies: {e}")

    image_urls = set()
    image_count = 0
    result_start = 0

    scroll_to_end(wd)
    scroll_to_end(wd)
    scroll_to_end(wd)
    scroll_to_top(wd)

    while image_count < max_links_to_fetch:

        thumbnail_results = wd.find_elements(By.CSS_SELECTOR, thumdnail_class_css_selector)
        number_results = len(thumbnail_results)

        print(f"Found {number_results} search results. Extracting links from {result_start}:{number_results}")

        counter = 1

        number_results = len(wd.find_elements(By.CSS_SELECTOR, thumdnail_class_css_selector))
        counteven = 0
        for index in range(number_results):
            img = wd.find_elements(By.CSS_SELECTOR, thumdnail_class_css_selector)[index+result_start]

            try:
                img = wd.find_elements(By.CSS_SELECTOR, thumdnail_class_css_selector)[index]
                wd.execute_script("arguments[0].scrollIntoView();", img)
                ActionChains(wd).move_to_element(img).perform()
                original_window = wd.current_window_handle
                if counteven % 2 == 0:
                    img.click()
                time.sleep(sleep_between_interactions)
                print(f"{counter}. Clicked on {img}")
                counteven += 1
                counter += 1
                wd.switch_to.window(original_window)
            except Exception as e:
                print(f"{counter}. Error clicking on {img}: {e}")
                counter += 1
                continue

            try:
                actual_image = WebDriverWait(wd, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, full_image_class_css_selector)))

                img_url = actual_image.get_attribute("src")

            except Exception as e:
                print(f"{counter}. Error finding full image: {e}")
                continue



            print(f"{counter}. Found image: {img_url}")
            image_urls.add(img_url)
            print(f"{counter}. Successfully added {img_url} to image_urls")

            image_count = len(image_urls)

            print("**************************")
            print(f"Image count: {image_count}, max_links_to_fetch: {max_links_to_fetch}")
            print("**************************")
            if len(image_urls) >= max_links_to_fetch:
                print(f"found: {len(image_urls)} image links")
                print("**************************")
                print("Breaking FOR loop")
                break

        else:
            print(f"Found {len(image_urls)} image links, looking for more...")

        # scroll_to_end(wd)
        result_start = len(thumbnail_results)
    print("**************************")
    print("Breaking WHILE loop")
    return image_urls


def persist_image(folder_path, url):
    print(f"URL: {url}")
    try:
        image_content = requests.get(url).content


    except Exception as e:
        print(f"Error - could not download {url} - {e}")

    try:
        if url.endswith(".svg"):
            with WandImage(blob=image_content) as img:
                png_image = img.make_blob("png")
                image_file = io.BytesIO(png_image)
                image = Image.open(image_file).convert('RGB')
        else:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')

        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[0:10] + ".jpg")
        with open(file_path, "wb") as f:
            image.save(f, "JPEG", quality=85)
        print(f"Success - saved {url} - as {file_path}")

        with open(os.path.join(folder_path, "image_info.txt"), "a") as f:
            f.write(f"{os.path.basename(file_path)}: {url}\n")
    except Exception as e:
        print(f"Error - could not save {url} - {e}")


def search_and_download(search_term, driver_path, number_images=10, target_path="./images"):
    target_folder = os.path.join(target_path, "_".join(search_term.lower().split(" ")))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Create a new Firefox service
    s = Service(driver_path)

    # Specify the path to the Firefox binary
    options = Options()
    options.binary_location = firefox_path
    options.headless = True
    # Create a new instance of the Firefox driver
    with webdriver.Firefox(options=options, service=s) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)

    for elem in res:
        persist_image(target_folder, elem)


keyword_to_search = input("Enter the keyword to search: ")
number_of_images_to_download = int(input("Enter the number of images to download (default 10): "))

search_and_download(keyword_to_search, geckodriver_path, number_of_images_to_download)
input("Press Enter to exit...")

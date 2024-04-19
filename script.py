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
import subprocess

print("********************************************")
print("********** G-Image-Scraper *********")
print("********************************************")


def is_imagemagick_installed():
    try:
        subprocess.check_output(['magick', '-version'], stderr=subprocess.STDOUT)
        return True
    except Exception:
        return False


print("Checking if ImageMagick dependencies are installed...")
if is_imagemagick_installed():
    print("ImageMagick is installed")

if not is_imagemagick_installed():
    print("ImageMagick is not installed. Please install it from https://imagemagick.org/script/download.php and "
          "restart the program.")
    sys.exit(1)

cookies_accept_button_id = 'L2AGLb'
cookies_accept_button_id_2 = "VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.XWZjwc"
thumdnail_class_xpath_selector = '//img[@class="YQ4gaf"]'
full_image_class_css_selector = 'img.sFlh5c.pT0Scc.iPVvYb'
firefox_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'
close_image_review_button = 'button.uj1Jfd.wv9iH.iM6qI'

if getattr(sys, 'frozen', False):
    script_dir = sys._MEIPASS  # If running as executable
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # If running as script

geckodriver_path = os.path.join(script_dir, 'geckodriver.exe')


def fetch_image_urls(query, max_links_to_fetch, result_start_index, size_filter, target_folder, wd,
                     sleep_between_interactions):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    def scroll_to_top(wd):
        wd.execute_script("window.scrollTo(0, 0);")
        time.sleep(sleep_between_interactions)

    if size_filter == "l":
        size_filter = '&tbs=isz:l'
    elif size_filter == "m":
        size_filter = '&tbs=isz:m'
    elif size_filter == "i":
        size_filter = '&tbs=isz:i'

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img" + size_filter
    print(f"DEBUG - search_url: {search_url.format(q=query)}")
    wd.get(search_url.format(q=query))

    try:
        accept_cookies_button = WebDriverWait(wd, 1).until(
            EC.presence_of_element_located((By.ID, cookies_accept_button_id))  # Use the id to locate the button
        )
        accept_cookies_button.click()
    except Exception as e:
        print(f"Error accepting cookies 1: {e}")

    try:
        scroll_to_end(wd)
        accept_cookies_button_2 = WebDriverWait(wd, 1).until(
            EC.presence_of_element_located((By.ID, cookies_accept_button_id_2))
        )
        accept_cookies_button_2.click()
    except Exception as e:
        print(f"Error accepting cookies 2: {e}")

    image_urls = set()
    image_count = 0

    scroll_to_end(wd)
    scroll_to_end(wd)
    scroll_to_end(wd)
    scroll_to_top(wd)
    end_index = result_start_index + max_links_to_fetch
    while image_count < max_links_to_fetch:

        thumbnail_results = wd.find_elements(By.XPATH, thumdnail_class_xpath_selector)
        thumbnail_results = thumbnail_results[result_start_index:]
        number_results = len(thumbnail_results)

        print(f"Found {number_results} search results. Extracting links from {result_start_index}:{end_index}")

        counter = 1
        counteven = 0

        for img in thumbnail_results:
            try:
                wd.execute_script("arguments[0].scrollIntoView();", img)
                ActionChains(wd).move_to_element(img).perform()
                original_window = wd.current_window_handle

                img.click()
                time.sleep(sleep_between_interactions)
                print(f"{counter}. Clicked on {img}")

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
                counteven += 1
            except Exception as e:
                print(f"{counter}. Error finding full image: {e}")
                counter += 1
                continue

            print(f"{counter}. Found image: {img_url}")
            download = persist_image(target_folder, img_url)
            if download:
                image_urls.add(img_url)

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
        image_extension = url.rsplit('.', 1)[-1]
        if not image_extension or len(image_extension) > 4:
            image_extension = 'jpg'
        if url.endswith(".svg"):
            with WandImage(blob=image_content) as img:
                png_image = img.make_blob("png")
                image_file = io.BytesIO(png_image)
                image = Image.open(image_file).convert('RGB')
        else:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')

        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[0:10] + "." + image_extension)
        with open(file_path, "wb") as f:
            f.write(image_content)
        print(f"Success - saved {url} - as {file_path}")

        with open(os.path.join(folder_path, "image_info.txt"), "a") as f:
            f.write(f"{os.path.basename(file_path)}: {url}\n")
        return True
    except Exception as e:
        print(f"Error - could not save {url} - {e}")
        return False


def search_and_download(search_term, driver_path, number_images, result_start, size_filter, target_path="./images"):
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
        fetch_image_urls(search_term, number_images, result_start, size_filter, target_folder, wd=wd,
                         sleep_between_interactions=0.5)

    # for elem in res:
    #     persist_image(target_folder, elem)


keyword_to_search = input("Enter the keyword to search: ")
while not keyword_to_search:
    keyword_to_search = input("You must enter the keyword to search: ")
number_of_images_to_download = input("Enter the number of images to download: ")
while not number_of_images_to_download:
    number_of_images_to_download = input("You must enter the number of images to download: ")
while not number_of_images_to_download.isdigit():
    number_of_images_to_download = input("You must enter a 'number' for the number of images to download: ")
result_start = input("Enter the start number for the images (default 0): ")
while not result_start:
    result_start = input("You must enter the start number for the images: ")
while not result_start.isdigit():
    result_start = input("You must enter a 'number' for the start number for the images: ")
image_size = input("Enter the image size (l: large, m: medium, i: icon, Enter: default): ")
while image_size not in ["l", "m", "i", ""]:
    image_size = input("You must enter a valid image size (l: large, m: medium, i: icon, Enter: default): ")
search_and_download(keyword_to_search, geckodriver_path, int(number_of_images_to_download), int(result_start),
                    image_size)
input("Press Enter to exit...")

import os
import sys
import time
import requests
from PIL import Image
import io
import hashlib

from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from wand.image import Image as WandImage
import subprocess
from selenium.common.exceptions import NoSuchFrameException

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
cookies_accept_button_id_2 = "//*[@id='yDmH0d']/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button"
thumdnail_class_xpath_selector = '//img[@class="YQ4gaf"]'
full_image_class_css_selector = 'img.sFlh5c.pT0Scc.iPVvYb'
firefox_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'
close_image_review_button = 'button.uj1Jfd.wv9iH.iM6qI'
supported_image_extensions = ['BMP', 'EPS', 'GIF', 'ICNS', 'ICO', 'IM', 'JPEG', 'JPEG 2000', 'MSP', 'PCX', 'PNG', 'PPM',
                              'SGI', 'SPIDER', 'TGA', 'TIFF', 'WebP', 'XBM', 'SVG']
need_to_check_secondary_images = False
secondary_image_button = "/html/body/c-wiz/div[1]/div/div[1]/div[1]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div/div[5]/div/div[1]/a"
image_source_page = "div.tvh9oe:nth-child(2) > c-wiz:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2)"
image_source_page2 = "div.tvh9oe:nth-child(2) > c-wiz:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(1) > a:nth-child(1)"
if getattr(sys, 'frozen', False):
    script_dir = sys._MEIPASS  # If running as executable
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # If running as script

geckodriver_path = os.path.join(script_dir, 'geckodriver.exe')


def fetch_image_urls(query, max_links_to_fetch, result_start_index, size_filter, max_secondary_images, target_folder,
                     wd, sleep_between_interactions):
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
    print(f"Search_url: {search_url.format(q=query)}")
    wd.get(search_url.format(q=query))

    try:
        accept_cookies_button = WebDriverWait(wd, 1).until(
            EC.presence_of_element_located((By.ID, cookies_accept_button_id))  # Use the id to locate the button
        )
        accept_cookies_button.click()
    except Exception as e:
        ...

    try:
        scroll_to_end(wd)
        accept_cookies_button_2 = WebDriverWait(wd, 1).until(
            EC.presence_of_element_located((By.XPATH, cookies_accept_button_id_2))
        )
        accept_cookies_button_2.click()
    except Exception as e:
        ...

    image_urls = set()
    main_image_count = 0

    scroll_to_end(wd)
    scroll_to_end(wd)
    scroll_to_end(wd)
    scroll_to_top(wd)
    end_index = result_start_index + max_links_to_fetch
    while main_image_count < max_links_to_fetch:

        thumbnail_results = wd.find_elements(By.XPATH, thumdnail_class_xpath_selector)
        thumbnail_results = thumbnail_results[result_start_index:]
        number_results = len(thumbnail_results)

        print(f"There are {number_results} search results in the main page.")

        counter = 1

        for img in thumbnail_results:
            try:
                time.sleep(sleep_between_interactions)
                wd.execute_script("arguments[0].scrollIntoView();", img)
                ActionChains(wd).move_to_element(img).perform()
                img.click()
                time.sleep(sleep_between_interactions)

                counter += 1

            except Exception as e:
                print(f"Error clicking on image.")
                counter += 1
                continue

            try:
                actual_image = WebDriverWait(wd, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, full_image_class_css_selector)))

                img_url = actual_image.get_attribute("src")

            except Exception as e:
                print(f"{counter}. Error finding full image: {e}")
                counter += 1
                # continue
            source_page_url = ""
            try:
                source_page = WebDriverWait(wd, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, image_source_page))
                )
                source_page_url = source_page.get_attribute("href")
                print(f"Source page URL: {source_page_url}")
            except Exception as e:
                print(f"Error finding source page: {e}")

            download = ""
            if img_url:
                print(f"Found image: {img_url}")
                download = persist_image(target_folder, img_url, source_page_url)

            if download:
                image_urls.add(img_url)


            main_image_count = len(image_urls)

            print("**************************")
            print(f"Main image count: {main_image_count}, max_links_to_fetch: {max_links_to_fetch}")
            print("**************************")
            # if len(image_urls) >= max_links_to_fetch:
            #     print(f"found: {len(image_urls)} image links")
            #     print("**************************")
            #
            #     os.startfile(target_folder)
            #     break

            # **************************************************************************
            if need_to_check_secondary_images:
                ActionChains(wd).key_down(Keys.CONTROL).click(img).key_up(Keys.CONTROL).perform()
                time.sleep(sleep_between_interactions)
                windows_handles = wd.window_handles
                wd.switch_to.window(windows_handles[-1])
                print(f"Current secondary URL: {wd.current_url}")

                try:
                    second_button = WebDriverWait(wd, 2).until(
                        EC.presence_of_element_located((By.XPATH, secondary_image_button)))

                    second_button_url = second_button.get_attribute("href")

                    wd.get(second_button_url)
                    scroll_to_end(wd)
                    scroll_to_top(wd)

                    secondary_image_counter = 0
                    while secondary_image_counter < max_secondary_images:
                        thumbnail_results2 = wd.find_elements(By.XPATH, thumdnail_class_xpath_selector)
                        thumbnail_results2 = thumbnail_results2[result_start_index:]
                        number_results2 = len(thumbnail_results2)
                        print(f"Found {number_results2} search results in the new page.")

                        for img2 in thumbnail_results2:
                            try:
                                time.sleep(sleep_between_interactions)
                                wd.execute_script("arguments[0].scrollIntoView();", img2)
                                ActionChains(wd).move_to_element(img2).perform()
                                img2.click()
                                time.sleep(sleep_between_interactions)
                                counter += 1

                            except Exception as e:
                                print(f"Error clicking on secondary image{img2}.")
                                counter += 1
                                continue

                            try:
                                actual_image2 = WebDriverWait(wd, 2).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, full_image_class_css_selector)))

                                img_url2 = actual_image2.get_attribute("src")

                            except Exception as e:
                                print(f"Error finding full secondary image.")
                                counter += 1
                                continue

                            source_page_url2 = ""
                            try:
                                source_page = WebDriverWait(wd, 2).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, image_source_page2))
                                )
                                source_page_url2 = source_page.get_attribute("href")
                                print(f"Source page URL: {source_page_url2}")
                            except Exception as e:
                                print(f"Error finding source page.")
                            print(f"Found image: {img_url}")

                            if img_url2:
                                download = persist_image(target_folder, img_url2, source_page_url2)

                            if download:
                                secondary_image_counter += 1

                            main_image_count = len(image_urls)

                            print("**************************")
                            print(f"Main image count: {main_image_count}\n"
                                  f"Seconday image count: {secondary_image_counter}\n"
                                  f"Max main images: {max_links_to_fetch}")
                            print("**************************")

                            if secondary_image_counter == max_secondary_images:
                                print(f"Already downloaded {max_secondary_images} secondary images.")
                                print("Returning to the main page")
                                break
                        else:

                            print(f"Found {len(image_urls)} image links, looking for more...")

                    wd.close()
                    wd.switch_to.window(windows_handles[0])
                    if len(image_urls) >= max_links_to_fetch:
                        os.startfile(target_folder)
                        break
                except Exception as e:
                    print(f"Error finding second button.")
                    wd.close()
                    wd.switch_to.window(windows_handles[0])
                    counter += 1
                    continue
            else:
                print("Not checking secondary images")
            # **************************************************************************

            if len(image_urls) >= max_links_to_fetch:
                print(f"found: {len(image_urls)} image links")
                print("**************************")

                os.startfile(target_folder)
                break


        else:

            print(f"Found {len(image_urls)} image links, looking for more...")

        # scroll_to_end(wd)
    print("**************************")

    return image_urls


def persist_image(folder_path, url, page_source_url):
    print(f"URL: {url}")
    try:
        image_content = requests.get(url, timeout=5).content
    except requests.exceptions.Timeout:
        print(f"Timeout - could not download {url}")
        return False

    except Exception as e:
        print(f"Error - could not download {url} - {e}")

    try:
        image_extension = url.rsplit('.', 1)[-1]
        if not image_extension or len(image_extension) > 4 or image_extension.upper() not in supported_image_extensions:
            image_extension = 'jpg'
        if url.endswith(".svg"):
            with WandImage(blob=image_content) as img:
                png_image = img.make_blob("png")
                image_file = io.BytesIO(png_image)
                image_extension = 'svg'
                image = Image.open(image_file).convert('RGB')
        else:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')

        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[0:10] + "." + image_extension)

        if os.path.exists(file_path):
            print(f"The file {url} already exists in the folder.")
            return False

        with open(file_path, "wb") as f:
            f.write(image_content)
        print(f"Success - saved {url} - as {file_path}")

        with open(os.path.join(folder_path, "image_info.txt"), "a") as f:
            f.write(f"{os.path.basename(file_path)}: {page_source_url}\n")
        return True
    except Exception as e:
        print(f"Error - could not save {url} - {e}")
        return False


def search_and_download(search_term, driver_path, number_images, result_start, size_filter, max_secondary_images,
                        target_path="./images"):
    target_folder = os.path.join(target_path, "_".join(search_term.lower().split(" ")))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Create a new Firefox service
    s = Service(driver_path)

    # Specify the path to the Firefox binary
    options = Options()
    options.binary_location = firefox_path
    #options.add_argument("-headless")
    # Create a new instance of the Firefox driver
    with webdriver.Firefox(options=options, service=s) as wd:
        fetch_image_urls(search_term, number_images, result_start, size_filter, max_secondary_images, target_folder,
                         wd=wd,
                         sleep_between_interactions=1)

    # for elem in res:
    #     persist_image(target_folder, elem)


keyword_to_search = input("Enter the keyword to search: ")
while not keyword_to_search:
    keyword_to_search = input("You must enter the keyword to search: ")

number_of_images_to_download = input("Please tell me how many main photos should I download :): ")
while not number_of_images_to_download:
    number_of_images_to_download = input("Dont play with me, how many main photos should I check?? :( : ")
while not number_of_images_to_download.isdigit():
    number_of_images_to_download = input("You must enter a 'number' for the main images to download: ")

result_start = input("Enter the start number for the images (default 0): ")
if not result_start:
    result_start = 0
while not result_start.isdigit():
    result_start = input("You must enter a 'number' for the start number for the images: ")

image_size = input("Enter the image size (l: large, m: medium, i: icon, Enter: default): ")
while image_size not in ["l", "m", "i", ""]:
    image_size = input("You must enter a valid image size (l: large, m: medium, i: icon, Enter: default): ")

max_secondary_images = input("Enter the number of secondary images per main one: Default is 0: ")
while not max_secondary_images.isdigit() or not max_secondary_images:
    print("You must enter a number for maximum secondary images")
if int(max_secondary_images) > 0:
    need_to_check_secondary_images = True

search_and_download(keyword_to_search, geckodriver_path, int(number_of_images_to_download), int(result_start),
                    image_size, int(max_secondary_images))
input("Press Enter to exit...")

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# the target website
url = "https://scrapeme.live/shop/"

# the interface for turning on headless mode
options = Options()
options.add_argument("-headless")

# using Firefox headless webdriver to secure connection to Firefox
with webdriver.Firefox(options=options) as driver:
    # opening the target website in the browser
    driver.get(url)

    # printing the target website url and title
    print(driver.current_url)  # https://scrapeme.live/shop/
    print(driver.title)  # Products - ScrapeMe
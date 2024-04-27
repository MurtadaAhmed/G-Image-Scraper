<br/>
<div align="center">

<h3 align="center"> G-Image-Scraper</h3>
<p align="center">
A scraper for Google images. It searches the images and download them based on some predefined criteria by the user. 
</p>
</div>

 ## About The Project

![Product Screenshot](https://i.imgur.com/LrW5K0E.png)

G-Image-Scraper is a scraper for Google images based on Python and Selenium. It searches the images and download them based on some predefined criteria by the user. The script is developed to work mainly for Windows OS users.
 ### Built With

- [Python](https://www.python.org)
- [Selenium](https://www.selenium.dev/)
 ### Prerequisites

The app will need the following dependencies:

1. ImageMagick
- support for .svg photos. It can be downloaded from here:
https://imagemagick.org/script/download.php

2. Python:
- can be downloaded from here
https://www.python.org/

3. Additional dependencies:
can be installed from requirements.txt:
``` pip install -r requirements.txt ```
 ### Installation

1. Clone the repo:
```
git clone https://github.com/MurtadaAhmed/G-Image-Scraper
```
2. Install dependencies:
``` 
cd G-Image-Scraper
```
``` 
pip install -r requirements.txt 
```
3. Run the app:

``` python .\script.py```
 ## Usage

Upon running the app, you will be prompted to enter the following:
1. How many main photos to be download from the main google images page?
2. From which index to start downloading the photos (the first photo is index 0)
3. Select image size (l: large, m: medium, i: icon, Enter: default).
4. How many secondary images to download for each selected main image (secondary images are the one that show on the right side after you click on the any image in google result)
5. Do you want to see the browser while scrapping the images or to be hidden?
6. If you selected 5 as "y", it will ask you if you need to interact with the browser in the beginning to add more advanced features (from https://www.google.com/advanced_image_search) before the search starts.
7. Once the search finishes, you will be prompted with:

-- Do you want to open the folder with the downloaded images?

-- Do you want to start another search?
 ## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
 ## License

Distributed under the MIT License. See [MIT License](https://opensource.org/licenses/MIT) for more information.

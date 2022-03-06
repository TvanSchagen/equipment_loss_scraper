from bs4 import BeautifulSoup
import urllib.request
import shutil
from os import path, mkdir
import time

# set a delay to not get blocked for doing too many requests
DELAY_SECONDS = 1

number_succeeded = 0
number_already_downloaded = 0
number_unable_to_download = 0
number_failed = 0

start = time.time()

# Download file
if not path.isfile("file.html"):
    print("Downloading file..")
    url = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html?m=1"
    output_file = "file.html"
    with urllib.request.urlopen(url) as response, open(output_file, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print("Downloaded file")

# Read file contents
with open("file.html", "r", encoding="utf8") as file:
    soup = BeautifulSoup(file.read(), "html.parser")
    body = soup.find("div", {"class": "post-body entry-content"})

    # create images directory if not exists
    if not path.isdir("images"):
        mkdir("images")

    idx = 0
    for category in body.find_all("ul"):

        # get category title from the h3 tags above the ul
        title = category.find_previous_sibling(
            "h3").text.strip().split("(", 1)[0]

        # create path from the current script execution path
        new_path = path.join(path.dirname(
            path.realpath(__file__)), "images", title.strip())

        if not path.isdir(new_path):
            mkdir(new_path)

        # get all objects from the current category
        for element in category.find_all("li"):
            idx = idx + 1
            text = element.text.strip()
            number_and_type = text.split(":", 1)[0].strip()
            number = number_and_type.split(maxsplit=1)[0]
            type = number_and_type.split(maxsplit=1)[1]

            print("Object: " + type)

            # get all images from each object
            img_idx = 0
            for img in element.find_all("a"):
                try:
                    img_idx = img_idx + 1
                    href = img["href"].strip()

                    # get state from the image names
                    state = img.text.strip().split(
                        ",")[1].replace(")", "").strip()

                    # some images are from links without a direct image, so check file type of link
                    if (href.endswith(".png") or href.endswith(".jpg")):

                        # create a file name with the model, number, and state
                        file_name = type + "_" + \
                            str(img_idx) + "_[" + state + "]." + \
                            href.split(".")[-1]

                        # replace forward and backward slashes to prevent invalid filenames
                        full_file_name = path.join(
                            new_path, file_name.replace("\\", " ").replace("/", " "))

                        if (path.exists(full_file_name)):
                            print("File already exists: " + full_file_name)
                            number_already_downloaded = number_already_downloaded + 1
                        else:
                            print("Downloading from: " + href +
                                  ", saving to: " + full_file_name)

                            with urllib.request.urlopen(href.strip()) as response, open(full_file_name, 'wb') as out_file:
                                shutil.copyfileobj(response, out_file)
                                number_succeeded = number_succeeded + 1
                                time.sleep(DELAY_SECONDS)
                    else:
                        print("Unable to download: " + href)
                        number_unable_to_download = number_unable_to_download + 1
                except Exception as e:
                    print("Error occurred while trying to download image: ", e)
                    number_failed = number_failed + 1

print(" --- SUMMARY --- ")
print("Time took ", round(time.time() - start, 2), "s")
print("No. Succeeded: ", number_succeeded)
print("No. Already downloaded: ", number_already_downloaded)
print("No. Unable to download: ", number_unable_to_download)
print("No. Failed:", number_failed)

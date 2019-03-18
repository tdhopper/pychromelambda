import boto3
import json

from selenium import webdriver
from PIL import Image
from hashlib import md5

BUCKET = "stiglerimages"
DEBUG = False
BASEPATH = "pychromelambda"
SCREENSHOT = "/tmp/img.png"
ELEMENT = "/tmp/img_cropped.png"
URL = "https://en.wikipedia.org/wiki/Main_Page"
ELEMENT_ID = "mp-left"
DEFAULT_ARGS = (
    "--headless",
    "--disable-gpu",
    "--disable-application-cache",
    "--disable-infobars",
    "--no-sandbox",
    "--window-size=1280x1696",
    "--hide-scrollbars",
    "--enable-logging",
    "--log-level=0",
    "--single-process",
    "--ignore-certificate-errors",
    "--homedir=/tmp",
)


def get_driver(
    binary_location="/opt/headless-chromium",
    chrome_driver="/opt/chromedriver",
    arguments=DEFAULT_ARGS,
):
    options = webdriver.ChromeOptions()
    options.binary_location = binary_location
    for arg in arguments:
        options.add_argument(arg)

    driver = webdriver.Chrome(chrome_driver, options=options)
    return driver


def screenshot(events=None, context=None):
    url = (events or {}).get("queryStringParameters", {}).get("url") or URL
    element_id = (events or {}).get("queryStringParameters", {}).get(
        "element_id"
    ) or ELEMENT_ID
    XPATH = f"//*[@id='{element_id}']"

    driver = get_driver()
    driver.get(url)

    element = driver.find_element_by_xpath(XPATH)
    location = element.location
    size = element.size
    driver.save_screenshot(SCREENSHOT)
    x = location["x"]
    y = location["y"]
    width = location["x"] + size["width"]
    height = location["y"] + size["height"]
    im = Image.open(SCREENSHOT)
    im = im.crop((int(x), int(y), int(width), int(height)))
    im.save(ELEMENT)

    with open(ELEMENT, "rb") as f:
        hasher = md5()
        buf = f.read()
        hasher.update(buf)
        filename = hasher.hexdigest()

    args = {"ACL": "public-read", "ContentType": "image/png"}
    (
        boto3.resource("s3")
        .Bucket(BUCKET)
        .upload_file(ELEMENT, f"{BASEPATH}/{filename}.png", ExtraArgs=args)
    )

    body = {
        "image_url": f"https://s3.amazonaws.com/{BUCKET}/{BASEPATH}/{filename}.png",
        "source_url": url,
        "xpath": XPATH,
    }
    if DEBUG is True:
        body["debug"] = {"events": events}
    return {"statusCode": 200, "body": json.dumps(body)}

    return response

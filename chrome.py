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
    for event in events["Records"]:
        r = json.loads(event["body"])
        _screenshot(**r)


def _screenshot(
    url, element_id, filename=None, output_bucket=BUCKET, output_basepath=BASEPATH
):
    capture_image(url, element_id)
    filename = filename or get_hash()
    save_image(output_bucket, output_basepath, filename)


def save_image(bucket, basepath, filename):
    args = {"ACL": "public-read", "ContentType": "image/png"}
    (
        boto3.resource("s3")
        .Bucket(bucket)
        .upload_file(ELEMENT, f"{basepath}/{filename}.png", ExtraArgs=args)
    )


def get_hash():
    with open(ELEMENT, "rb") as f:
        hasher = md5()
        buf = f.read()
        hasher.update(buf)
        filename = hasher.hexdigest()
    return filename


def capture_image(url, element_id):
    driver = get_driver()
    driver.get(url)

    xpath = f"//*[@id='{element_id}']"
    element = driver.find_element_by_xpath(xpath)
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

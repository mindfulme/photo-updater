from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as BS
import time

FIRST_SHARE_XPATH = '/html/body/div[1]/div/c-wiz/div[5]/c-wiz[1]/c-wiz[2]/div/div[2]/span/div/div/div[1]/div[2]/a'
RIGTH_ARROW_XPATH = '/html/body/div[1]/div/c-wiz/div[5]/c-wiz[2]/div[1]/c-wiz[3]/div[2]/div[2]'
IMG_CLASS_NAME = 'SzDcob'

options = webdriver.FirefoxOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--width=1040')
options.add_argument('--height=1040')
options.headless = True
driver = webdriver.Firefox(executable_path="./geckodriver", options=options)

def get_redirects(sharedAlbumUrl, width, mediaItemsCount):
    status = "Generating redirect links"
    shared_redirect_links = list()
    driver.get(sharedAlbumUrl)
    shared_object = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, FIRST_SHARE_XPATH)))
    shared_object.click()
    while True:
        soup = BS(driver.page_source, 'html.parser')
        img = soup.find("img", IMG_CLASS_NAME)
        if img is not None:
            break
        time.sleep(1)
    shared_redirect_links.append(img.get("src"))
    if mediaItemsCount == 1:
        print(status.ljust(width)[:-7] + "100.00%")
        return shared_redirect_links
    for i in range(mediaItemsCount-1):
        percent = "%.2f" % float(((i+1) / (mediaItemsCount-1))*100) + "%"
        try:
            go_to_next = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, RIGTH_ARROW_XPATH)))
            go_to_next.click()
        except:
            pass
        time.sleep(3)
        while True:
            soup = BS(driver.page_source, 'html.parser')
            img = soup.find("img", IMG_CLASS_NAME)
            if img is not None:
                break
            time.sleep(1)
        shared_redirect_links.append(img.get("src"))
        end = "\n" if i+1 == mediaItemsCount-1 else "\r"
        print(status.ljust(width)[:-len(percent)] + percent, end=end)
    return shared_redirect_links

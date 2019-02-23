from bs4 import BeautifulSoup
import requests
import csv 
import os
import time
import random
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# ///////////////
# 
# 
# General Notes: 
# Will need proxies
# Many of these items are currently unavailable
# 100 takes maybe 10 mins -> 15000 takes around 10 hours even with three simultaneous 
# works for around 60% of items first try
# Need to resstart the driver every 50 or so to prevent fuckups
# 
# \\\\\\\\\\\\\\\\\
# ///////////////
# 
# 
# CONFIG
# 
# 
# \\\\\\\\\\\\\\\\\
# Proxy Server
PROXY = "23.88.194.125:8800" # IP:PORT or HOST:PORT
# file directory
fileDir = os.path.dirname(os.path.realpath('__file__'))
#For accessing the file in a folder contained in the current folder
readfile = os.path.join(fileDir, 'fifteengroups/focal2.csv')
writefile = os.path.join(fileDir, 'fifteenouts/' + 'renamemeto_focal2' + str(today()) + '.csv')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=%s' % PROXY)

# Change proxy
# Change in file
# change outfile

# ///////////////
# 
# 
# USEFUL FUNCTIONS FOR BELOW
# 
# 
# \\\\\\\\\\\\\\\\\
# asin and title as string
def urlspoof(asin, title):
    start = "https://www.amazon.com/"
    titlearray = title.split()
    # print titlearray
    try:
        if len(titlearray) > 0:
            randguy = random.random()
            titSlug = None
            # 30% of the time 
            if randguy <= .3:
                titSlug1 = titlearray[0] + "-" + titlearray[1] + "-" + titlearray[2] + "-"
                if len(titSlug1) < 150:
                    titSlug2 = titSlug1 + "-" + titlearray[3] + "-" + titlearray[4]
                if len(titSlug2) < 150:
                    titSlug = titSlug2
                else:
                    titSlug = titSlug1
            elif randguy < .6:
                titSlug1 = titlearray[0] + "-" + titlearray[2] + "-" + titlearray[1] + "-"
                if len(titSlug1) < 150:
                    titSlug2 = titSlug1 + "-" + titlearray[3] + "-" + titlearray[4]
                if len(titSlug2) < 150:
                    titSlug = titSlug2
                else:
                    titSlug = titSlug1
            else:
                titSlug1 = titlearray[0] + "-" + titlearray[2] + "-" + titlearray[1] + "-"
                if len(titSlug1) < 150:
                    titSlug2 = titSlug1 + "-" + titlearray[4] + "-" + titlearray[3]
                if len(titSlug2) < 150:
                    titSlug = titSlug2
                else:
                    titSlug = titSlug1
        
        if titSlug != None:
            if random.random() < .65:
                return start + titSlug + "/dp/" + asin + "/" + "ref=sr_1_1?ie=UTF8&qid=" + str(int(time.time())) + "&sr=1-1&keywords=" +  titlearray[0] + "-" + titlearray[1]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            elif random.random() < .9:
                return start + titSlug + "/dp/" + asin + "/" 
            else:
                return start +  "dp/" + titSlug + "/" + asin + "/"
    except:
            print 'title error!' 
            return "https://www.amazon.com/dp/" + asin

def today():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%m%d')



# ///////////////
# 
# 
# OPEN INPUT FILE AND READ
# 
# 
# \\\\\\\\\\\\\\\\\
# indexes for use below
ASIN = 0
TITLE = 1

with open(readfile, 'r') as csvinfile, open(writefile, 'w') as csvoutfile:
    lines = csv.reader(csvinfile, dialect='excel')
    csvwriter = csv.writer(csvoutfile, dialect='excel')
    
    # skips header
    # headers = lines.next()
    headers = ["ASIN", "Title"]
    # add the new date, review ,etc stuff to headers
    headers.append('date')
    headers.append('avg review')
    headers.append('item quantity')
    # write headers
    csvwriter.writerow( headers )

    # stores as tuple of ASIN, Title for any that didnt work.
    messedUp = []

    drivercount = 53

    for row in lines:
        # item is asin, title is title
        item = row[ASIN]
        title = row[TITLE]

        # add scrape date to row
        row.append(str(today()))

        # strip whitespace, call urlspoof
        url = urlspoof(item.strip(), title)

        # ideally this would be in the begin scraper session but had to init driver and actionchains 
        # outside of the for loop so it doesnt keep opening new widows while running
        if drivercount > 50:
            driver = webdriver.Chrome("/Users/mattsciamanna/Documents/code/scraper/chromedriver", chrome_options=chrome_options)
            actions = ActionChains(driver)
            drivercount = 0
        drivercount += 1

        # ///////////////
        # 
        # 
        # Begin actual Scraper
        # 
        # 
        # \\\\\\\\\\\\\\\\\

        # make avg rating a dict of ASIN -> avg rating
        avgratings = {}


        # start scrape
        time.sleep(0.5 * random.random())
        # uses the spoofed URL we made above 
        driver.get(url)
        errors = 0
        # gets html just like a get request woulda & Beautiful soups it 
        try:
            website = driver.page_source
            soup = BeautifulSoup(website, 'lxml')
            # get the actual important content --> the ratings -->
            article = soup.find("div", {"id": "reviewsMedley"}).find("span", {"class": "a-icon-alt"}).contents
            # get the rating that we found
            rate =  article[0].encode("utf-8").split()

            # error handle, not finding avg rating
            if article == None:
                print "didn't find it!"
                avgratings[item] = str(9999)
            else:
                avgratings[item] = rate[0]

            # end avg rating, onto next page.
            driver.find_element_by_xpath('//*[@id="quantity"]/option[11]').click()
            time.sleep(0.245)
            # find add cart button, scroll the add to cart into view, then click it 
            addTo = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="add-to-cart-button"]')))
            driver.execute_script("window.scrollTo(0, 200)") 
            addTo.click()
            # go to next page
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="hlb-view-cart-announce"]')))
            driver.find_element_by_xpath('//*[@id="hlb-view-cart-announce"]').click()
            # quantity box
            quantity = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-action-quantity input')))

            quantity.clear()
            quantity.send_keys(Keys.BACKSPACE)
            quantity.send_keys(Keys.BACKSPACE)
            quantity.send_keys("999")
            quantity.send_keys(Keys.RETURN)
            # quantity.send_keys(Keys.ENTER)

            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="activeCartViewForm"]/div[2]/div/div[4]/div/div[3]/div/div/div/span/span/a')))
            time.sleep(.75)
            newQuantity = driver.find_element_by_css_selector('.sc-action-quantity input')
            number = newQuantity.get_attribute("value")
            print number
            
            driver.execute_script("window.scrollTo(0, 300)") 
            # keeps snagging on delete :
            dele = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Delete']")))
            dele.click()
            
            
            row.append(avgratings[item])
            row.append(number)

            csvwriter.writerow( row )

            if errors > 0:
                errors -= 1
        except:
            print "error!"
            # error checking where once we have ten issues in a row, we exit
            errors += 1
            if errors > 10:
                break
            messedUp.append([item, title])

    # this part works pretty well
    csvwriter.writerow(["start errors"])
    for product in messedUp:
        csvwriter.writerow(product)

        #activeCartViewForm > div.sc-list-body.sc-java-remote-feature > div > div.sc-list-item-content > div.a-row.a-spacing-base.a-spacing-top-base > div.a-column.a-span8 > div > div > div.a-fixed-left-grid-col.a-col-right > div > span.a-size-small.sc-action-delete
       #activeCartViewForm > div.sc-list-body.sc-java-remote-feature > div > div.sc-list-item-content > div.a-row.a-spacing-base.a-spacing-top-base > div.a-column.a-span8 > div > div > div.a-fixed-left-grid-col.a-col-right > div > span.a-size-small.sc-action-delete > span > input[type="submit"]
        # #  once we have that box, send keys enter
        
        # at this point, the scraper is done so we add the data to make a new row
        
        # now we write this row to outfile
        



# test links
# a = "https://www.amazon.com/Rachael-Ray-Nutrish-Natural-Chicken/dp/B01AHOMBDC/ref=sr_1_1?s=pet-supplies&ie=UTF8&qid=1542948282&sr=1-1-spons&keywords=dog+food&psc=1#customerReviews"
# b = "https://www.amazon.com/Rachael-Ray-Nutrish-Natural-Chicken/dp/B00FBT7XAK/ref=pd_sim_199_4?_encoding=UTF8&pd_rd_i=B00FBT7XAK&pd_rd_r=8ed4022d-eeda-11e8-b188-2fb63616cf11&pd_rd_w=ydTs5&pd_rd_wg=9IR6y&pf_rd_i=desktop-dp-sims&pf_rd_m=ATVPDKIKX0DER&pf_rd_p=18bb0b78-4200-49b9-ac91-f141d61a1780&pf_rd_r=TEDYA3AHVV7VV22J3N0W&pf_rd_s=desktop-dp-sims&pf_rd_t=40701&psc=1&refRID=TEDYA3AHVV7VV22J3N0W"
# c = "https://www.amazon.com/gp/slredirect/picassoRedirect.html/ref=pd_cart_sspa_dk_ct_pt_sub_1?ie=UTF8&adId=A076258213SEW9BUDWLB0&qualifier=1543600781&id=64446609165107&widgetName=sp_cart_percolate&url=%2FKINTOR-Assembly-Rough-surfaced-Stainless-S-5-1x4-3x5-1inch%2Fdp%2FB07DNFZ6H1%2Fref%3Dpd_cart_sspa_dk_ct_pt_sub_1_2%3F_encoding%3DUTF8%26pd_rd_i%3DB07DNFZ6H1%26pd_rd_r%3D41086241-9781-4f40-8d34-a0284da03b20%26pd_rd_w%3DV3veo%26pd_rd_wg%3D5qnEj%26pf_rd_i%3Dcart-page-widgets%26pf_rd_m%3DATVPDKIKX0DER%26pf_rd_p%3Ddb9c4345-afe3-409a-a7a4-87af748a0cca%26pf_rd_r%3DTRZK6PWR67EMTCD0NWZF%26pf_rd_s%3Dcart-page-widgets%26pf_rd_t%3D40701%26psc%3D1%26refRID%3DTRZK6PWR67EMTCD0NWZF"
# # c = "https://www.amazon.com/gp/product/B00AOJM6MM/ref=s9_acsd_top_hd_bw_b3FLmHL_c_x_w?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-3&pf_rd_r=3QM8ZMZN44YHMHAJKKHQ&pf_rd_r=3QM8ZMZN44YHMHAJKKHQ&pf_rd_t=101&pf_rd_p=213efcae-1132-5293-afe0-aaeeb265ed55&pf_rd_p=213efcae-1132-5293-afe0-aaeeb265ed55&pf_rd_i=2975234011"



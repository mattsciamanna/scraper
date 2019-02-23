from bs4 import BeautifulSoup
import requests
import subprocess
import csv 
import os
import sys
import time
import random
import csv
import datetime
import redis
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from twilio.rest import Client
from pyvirtualdisplay import Display

# ///////////////
# General Notes: 
# Will need proxies
# Many of these items are currently unavailable
# 100 takes maybe 10 mins -> 15000 takes around 10 hours even with three simultaneous 
# works for around 60% of items first try
# Need to resstart the driver every 50 or so to prevent fuckups
# Need to call ua.update() from time to time.
# NEED TWO ARGS, THREAD NUMBER AND THE FILE WE READ FROM
# In the case of a sorry message, ya gotta put the asin into the search bar and that will go quite a long ways
# BIG changes:
# now if quantbox is less than eleven, it will simply wait 1-12 seconds then get another.
# TODO:
# Make Stuff Timed Better
# THings with sizes dont woek qwell
# Reseed proxies
# Make error logging 
# CHECK Fix the thing where it doesnt get item quantity until that bubble
# URL redis instead of shitty files
# delete something with 579 units
# CHEKC not teztinf me!
# CHECK drop it to like 5-17 items a proxy 
# Add a user input like control h to get us a nice new proxy
# It always manages to search the correct product from a dog page but rarely if ever chooses the product 
# Fix Broken Proxy Button
# Start storing total number of reviews
# CHECK Let it return  items to the queuse
# CHECK HOPEFULLY: There's gonna be a loop once we run out of items to draw, need to mess
# with the way that get item returns when empty. 
# WHen there arent eleven in stock? Is it taking a long time? 
# go down to inline add stuff and add in that if a product waits out without becoming visible there's no need to sleep it.
# When there are less than 20 items dont add to cart, that just messes up your logger
# STart tracking best seller number in addition to category!
# maybe onlypopfrom likstwhen the item isnt scraped? no thats not reasonable 
# This weird article failed error seems to be originating from the times when a proxy doesnt work out right
# 
# How to do this with redis?
# Maybe have a key as product:date? 
# Rightnow it only cleans the first asin in a run
# \\\\\\\\\\\\\\\\\
# test link where seller has a limit per customer note it doesnt work
# https://www.amazon.com/dp/B07D56WLM2
# \\\\\\\\\
# Test Screen -t command with a 

# ///////////////
# 
# 
# CONFIG
# 
# 
# \\\\\\\\\\\\\\\\\
print ("run started at" + str(datetime.datetime.now()) ) 

def today():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%m%d%H')

fileDir = os.path.dirname(os.path.realpath('__file__'))
#For accessing the file in a folder contained in the current folder
# \\\\\\
# //////
# readfile = os.path.join(fileDir, 'fifteengroups/250' + sys.argv[1] + '.csv')
writefile = os.path.join(fileDir, 'realscrapeout/successes' + sys.argv[1] + str(today()) + '.csv')
errorfile = os.path.join(fileDir, 'realscrapeout/errors' + sys.argv[1] + str(today()) + '.csv')
try:
    asinfile = open(os.path.join(fileDir, 'realscrapeout/asins.txt'), 'w')
except:
    pass


# starts up our redis and our ua stuff
# step 2: define our connection information for Redis
# Replaces with your configuration information
redis_host = "redis-17827.c57.us-east-1-4.ec2.cloud.redislabs.com"
redis_port = 17827
redis_password = "dFFYSFXQlu5E28IrN8fL6Y7yXt7iX4Hm"

#got rid of try except because if this fails, we're gonna wanna know.

# The decode_repsonses flag here directs the client to convert the responses from Redis into Python strings
# using the default encoding utf-8.  This is client specific.
r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)


# ///////////////
# 
# 
# USEFUL FUNCTIONS FOR BELOW
# 
# 
# \\\\\\\\\\\\\\\\\
# testing method to get a proxy ua combo
def get_proxy():
    packed = r.blpop(['queue:proxies'], 30)

    if not packed:
        print "failure"
    else:
        # had to turn it back into a json for no real reason
        obj =  json.loads(packed[1].encode('utf8'))
       
        r.rpush('queue:proxies', json.dumps(obj) )
        if len(obj) == 2:
            # NOTE: the zero in the first part of tuple, no clue why it's like that
            return [obj['proxy'][0].encode('utf8'), obj['useragent'].encode('utf8')]
        else:
            print "malformed proxy/useragent row"
            get_proxy()

def get_item():
    item = r.blpop(['queue:products'], 30)

    r.incr('count:products')

    if not item:
        raise ValueError('item didnt come off queue')
    else:
        # had to turn it back into a json for no real reason
        obj =  json.loads(item[1].encode('utf8'))
        try:
            asinfile.write(str(obj['asin']) + " \n")
        except:
            pass
       
        if len(obj) == 3:
            # NOTE: the zero in the first part of tuple, is gone no clue why it's needed for proxy
            return [obj['asin'].encode('utf8'), obj['title'].encode('utf8'), obj['attempts']]
        else:
            print "malformed item row"
            get_item()

def return_item(item):
    ASIN = item[0]
    TITLE = item[1]
    ATTEMPTS = item[2]
    # print "preincr attempts"
    # print ATTEMPTS
    ATTEMPTS += 1
    # print "postincr" +" " + str(ATTEMPTS)
    data = {
            'asin': ASIN,
            'title': TITLE,
            'attempts': ATTEMPTS
           }
    print data
    r.rpush('queue:products', json.dumps(data))
    r.incr('count:failed')

def failed_product(item):
    ASIN = item[0]
    TITLE = item[1]
    ATTEMPTS = item[2]
    # print "preincr attempts"
    # print ATTEMPTS
    ATTEMPTS += 1
    # print "postincr" +" " + str(ATTEMPTS)
    data = {
            'asin': ASIN,
            'title': TITLE,
            'attempts': ATTEMPTS
           }
    print 'Failed Product Requed!'
    r.rpush('queue:errorproducts', json.dumps(data))
    r.incr('count:errors')


    
# if our last proxy was robot checked, pop it out of list
# then pushes too loggging redis for broken proxies 
# doesnt necessarily work except when the robot check is first!!
def broken_proxy():
    broken = r.brpop(['queue:proxies'], 30)

    obj =  json.loads(broken[1].encode('utf8'))
       
    r.rpush('queue:brokeproxies', json.dumps(obj) )


# asin and title as string
def urlspoof(asin, title):
    # start = "https://www.amazon.com/"
    # titlearray = title.split()
    return "https://www.amazon.com/dp/" + asin

def robotCheck():

    # Your Account Sid and Auth Token from twilio.com/console
    account_sid = 'ACeed4f93dcfe622ac3bc7e5a2a742d9fb'
    # note: You're gonna need to get an actual auth token
    auth_token = 'f4e3908ce2cc7ceb5a75c42927f3b624'
    client = Client(account_sid, auth_token)

    message = client.messages \
    .create(
            body="Robot Check on yer dedicated proxies from aws" + sys.argv[1],
            from_='+14847465219',
            to='+14432070862'
        )
    
    time.sleep(100)
    return


# indexes for use below
ASINKEY = 0
TITLEKEY = 1

with open(writefile, 'w') as csvoutfile, open(errorfile, 'w') as erroroutfile:
    csvwriter = csv.writer(csvoutfile, dialect='excel')
    errorlogger = csv.writer(erroroutfile, dialect='excel')
    # testlink = "https://www.amazon.com/Supershieldz-All-New-Tempered-Protector-Generation/dp/B078DMYPB1/"
    
    # skips header
    headers = ["ASIN", "Title", "Attempts"]
    # add the new date, review ,etc stuff to headers
    headers.append('date')
    headers.append('avg review')
    headers.append('total reviews')
    headers.append('item quantity')
    # write headers
    csvwriter.writerow(headers)

    # stores as tuple of ASIN, Title for any that didnt work.
    drivercount = 77
    needToSwitch = 0
    # If you switch this guy up, be sure to switch up the one online 123
    switchingBar = random.randint(12,18)

    # for all of our items 
    # does this work? 
    while True:
        messedUp = []
        try:
            row = get_item()
        except ValueError as err:
            print (err.args)
            print "we've reached the end of the queue"
            print "we've reached the end of the queue!"
            print "we've reached the end of the queue!!"
            subprocess.call(["sudo", "halt"])
            break
        
        # item is asin, title is title
        item = row[ASINKEY][0:10]
        title = row[TITLEKEY]
        attempts = row[2]
        # if we've already tried scraping 2x, add it to failed products and move on!
        if attempts > 1:
            failed_product(row)
            continue

        # add scrape date to row
        row.append(str(today()))

        # strip whitespace, call urlspoof
        url = urlspoof(item.strip(), title)

        # ideally this would be in the begin scraper session but had to init driver and actionchains 
        # outside of the for loop so it doesnt keep opening new widows while running
        # also want to change user agents here ideally
        if drivercount > switchingBar or needToSwitch >= 16:
            needToSwitch = 0
            pandu = get_proxy()
            PROXY = pandu[0]
            userAgent = pandu[1]
            print "Proxy changed to: " + str(PROXY)
            switchingBar = random.randint(12,18)
            chrome_options = webdriver.ChromeOptions()
          
            chrome_options.add_argument('--proxy-server=%s' % PROXY)
            chrome_options.add_argument('user-agent={userAgent}')
            chrome_options.add_argument('--start-maximized')

            try:
                driver.quit() 
                # only the display action
                display.stop()
            except:
                print "First run through, no driver detected!"
                # Clean the item form the BOM Chars, if we frick ourselves we still just move right throught
                if len(item) > 5:
                    item = 'B' + str(item.split('B', 1)[1])
                else:
                    continue


            # check this later
            display = Display(visible=0, size=(1200, 800))  
            display.start()
            time.sleep(2)
            driver = webdriver.Chrome("/home/ec2-user/scraper/chromedriver", chrome_options=chrome_options)
            driver.delete_all_cookies()
            actions = ActionChains(driver)
            drivercount = 0

        # iterate
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
        time.sleep(5 * random.random())
        # uses the spoofed URL we made above 
        # titlelink = "https://www.amazon.com/dp/B00LAAZ9MS"
        # !!!!!!!!!work to do
        try:
            driver.get(url)
        except:
            return_item(row)
            continue

        # gets html & Beautiful soups it 
        try:
            website = driver.page_source
            soup = BeautifulSoup(website, 'lxml')
        except:
            print "BeautifulSoup fricked up!"

        # try getting num of reviews with a wait
        try:
            numReviewsSpan = WebDriverWait(driver, 4).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#acrCustomerReviewText')))
            numReviews = numReviewsSpan.text
            numReviews = numReviews.split()
            numReviews = numReviews[0]
        except:
            numReviews = 0
            print "couldnt get the raw number of reviews from er " + str(item)

        # Next try getting the avg review content
        try:
        # get the actual important content --> the ratings -->
            article = soup.find("div", {"id": "reviewsMedley"}).find("span", {"class": "a-icon-alt"}).contents
        except:
            # random number times the wait period of er
            time.sleep(random.random() * 11)
            # WORKS! 
            if soup.title.string == "Sorry! Something went wrong!":
                try:
                    return_item(row)
                    needToSwitch += 2
                    searchField = WebDriverWait(driver, 6).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#e')))
                    # driver.find_element_by_css_selector('.f')
                    time.sleep(6 * random.random())
                    searchField.send_keys(item)
                    time.sleep(3 * random.random())
                    go = driver.find_element_by_css_selector('#f')
                    go.click()
                    # RARELY WORKS
                    firstResult = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="result_0"]/div/div/div/div[2]/div[1]/div[1]/a/h2')))
                    firstResult.click()     
                except Exception as e:
                    print(e)
                    print "something went wrong but searching it didnt help"
            elif "Robot" in soup.title.string:
                try:
                    return_item(row)
                    robotCheck()
                    broken_proxy()
                    needToSwitch = 12
                except:
                    print "robotCheck failed"
            


        
        try:
            rate =  article[0].encode("utf-8").split()
        except:
            article = None
            'rate =  article[0].encode("utf-8").split() is messed up!'
        
        # error handle, not finding avg rating
        if article == None:
            print "The Avg Rating could not be found!"
            avgratings[item] = str(9999)
        else:
            avgratings[item] = rate[0]


        # this is where we should look for currently unavailable and/hurry only x left
            # outStock = soup.find("div", {"id": "outOfStock"})
            # lt21  = soup.find("div", {"id": "availabilityInsideBuyBox_feature_div"}).find_all(text=True)
                # lt21  = soup.find_all("span", {"class": "a-color-price"}).find(text=common_str)
        # \\\\\\
        # search front page for what we want
        the_word = "left in stock - order soon."
        try:
            tags = soup.find_all('span', {"class":"a-color-price"}, text=lambda t: t and the_word in t)
            # make the first only statement into a string
            tag = str(tags[0])
        except Exception: 
            tags = []
            pass

        if tags != []:
            splittag  = tag.split('Only ',1)
            # this handles two digit numbers but keeps spaces in the case of 1 digit
            firstpagequantity = splittag[1][0] + splittag[1][1]
            print 'quantity found on first page'
            try:
                # how do i know this aint gonna frick my shit up?
                # remove spaces
                quantnospace = firstpagequantity.split()
                row.append(avgratings[item])
                row.append(numReviews)
                # the zero item should be what we want
                row.append(quantnospace[0])
                # 
                row.append('firstpage quantity')
                csvwriter.writerow(row)

                # no reason for this but frck it
                row = []
                time.sleep((12 * random.random()) + 2)
                continue
            except:
                print "VERY BAD ERROR HERE -- Line 412 -- something's wrong with our firstpagequantity"

        # \\\\\\
        # Begin adding 11 tocart, doing 999 trick
        # //////
        try:
            quantbox = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="quantity"]/option[11]')))
            quantbox.click()
            time.sleep(4*random.random())
        except:
            # If we hit this, ideally it means
            # and the quantity was 0 for some reason like unavailble
            if attempts == 0:
                return_item(row)
            else:
                messedUp.append(item)
                messedUp.append(title)
                messedUp.append(avgratings[item])
                messedUp.append(numReviews)
                messedUp.append('0')
                messedUp.append('Unavailable item')
                errorlogger.writerow(messedUp)
                print "ERROR WRITTEN TO OUTFILE ON: " + str(item)
                try:
                    failed_product(row)
                except: 
                    print "FATAL ERROR, PRODUCT RETURN DIDN'T WORK"
                    pass

            print "WE COULD NOT GET THE QUANTITIY FOR ASIN " + str(item)
            time.sleep((12 * random.random()) + 2)
            continue
            print "I should never print, check Line 444!"

        # if we hit this block, we've added 11 to our quantity box
        try:
            # one unit at a time to cart when failed which is annoying
            time.sleep(4 * random.random())
            # find add cart button, scroll the add to cart into view, then click it 
            addTo = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="add-to-cart-button"]')))
            driver.execute_script("window.scrollTo(0, 200)")
            time.sleep(3 * random.random())
            addTo.click()
        except:
            print "WE Couldnt use the normal add to cart for some reason" + str(item)
        # old stuff below
        # driver.find_element_by_xpath('//*[@id="quantity"]/option[11]').click()
        try:
            # when they try to upsell ya a modal
            warrantymodal = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#a-popover-4 > div > header > button > i')))
            time.sleep(1 * random.random())
            warrantymodal.click()
        except:
            try:
                # inline add to cart ie https://www.amazon.com/Nail-Art-Tools--Manicure-Kit/dp/B01MR6ZH51
                inlineAdd = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#smartShelfAddToCartNative')))
                time.sleep(2 * random.random())
                inlineAdd.click()
            except:
                # dont append to messed up herer because sometimes we're already at the view cart page
                print "we should be on middle screen or attempts at adding to cart have failed"
            
        try:
            element = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="hlb-view-cart-announce"]')))
            if random.random() <= .01:
                try:
                    driver.save_screenshot('screen' + item + '.png')
                except:
                    print "Didnt manage to take yer screenshot"
            time.sleep(4*random.random())
            driver.find_element_by_xpath('//*[@id="hlb-view-cart-announce"]').click()
        except:
            print "Made it through the view cart screen"
        # quantity box
        try:
            quantity = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sc-action-quantity input')))

            if random.random() <= .01:
                try:
                    driver.save_screenshot('screenie' + item + '.png')
                except:
                    print "Didnt manage to take yer screenshot"

            quantity.clear()
            quantity.send_keys(Keys.BACKSPACE)
            quantity.send_keys(Keys.BACKSPACE)
            quantity.send_keys("999")
            time.sleep(3 * random.random())
            quantity.send_keys(Keys.RETURN)

            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="activeCartViewForm"]/div[2]/div/div[4]/div/div[3]/div/div/div/span/span/a')))
            time.sleep(2.75 * random.random())
            newQuantity = driver.find_element_by_css_selector('.sc-action-quantity input')
            number = newQuantity.get_attribute("value")
            
            
            
            driver.execute_script("window.scrollTo(0, 300)") 
            # keeps snagging on delete :
            dele = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Delete']")))
            time.sleep(3 * random.random())
            dele.click()
            
            row.append(avgratings[item])
            row.append(numReviews)
            row.append(number)
            row.append('success')

            csvwriter.writerow( row )

            time.sleep(4 * random.random())
        except Exception as e:
            print "messed up while adding to cart somehow! Below see exception"
            print e
            # if we haven't logged an error
        try:
            if not number:
                # might write everytime who knows
                messedUp.append(item)
                messedUp.append(title)
                messedUp.append( "Other Issue")
                errorlogger.writerow(messedUp)
                try:
                    failed_product(row)
                except: 
                    print "FATAL ERROR, PRODUCT RETURN DIDN'T WORK"
                    pass
        except:
            pass

    csvoutfile.close()

      
        
       
# test links
# a = "https://www.amazon.com/Rachael-Ray-Nutrish-Natural-Chicken/dp/B01AHOMBDC/ref=sr_1_1?s=pet-supplies&ie=UTF8&qid=1542948282&sr=1-1-spons&keywords=dog+food&psc=1#customerReviews"
# b = "https://www.amazon.com/Rachael-Ray-Nutrish-Natural-Chicken/dp/B00FBT7XAK/ref=pd_sim_199_4?_encoding=UTF8&pd_rd_i=B00FBT7XAK&pd_rd_r=8ed4022d-eeda-11e8-b188-2fb63616cf11&pd_rd_w=ydTs5&pd_rd_wg=9IR6y&pf_rd_i=desktop-dp-sims&pf_rd_m=ATVPDKIKX0DER&pf_rd_p=18bb0b78-4200-49b9-ac91-f141d61a1780&pf_rd_r=TEDYA3AHVV7VV22J3N0W&pf_rd_s=desktop-dp-sims&pf_rd_t=40701&psc=1&refRID=TEDYA3AHVV7VV22J3N0W"
# c = "https://www.amazon.com/gp/slredirect/picassoRedirect.html/ref=pd_cart_sspa_dk_ct_pt_sub_1?ie=UTF8&adId=A076258213SEW9BUDWLB0&qualifier=1543600781&id=64446609165107&widgetName=sp_cart_percolate&url=%2FKINTOR-Assembly-Rough-surfaced-Stainless-S-5-1x4-3x5-1inch%2Fdp%2FB07DNFZ6H1%2Fref%3Dpd_cart_sspa_dk_ct_pt_sub_1_2%3F_encoding%3DUTF8%26pd_rd_i%3DB07DNFZ6H1%26pd_rd_r%3D41086241-9781-4f40-8d34-a0284da03b20%26pd_rd_w%3DV3veo%26pd_rd_wg%3D5qnEj%26pf_rd_i%3Dcart-page-widgets%26pf_rd_m%3DATVPDKIKX0DER%26pf_rd_p%3Ddb9c4345-afe3-409a-a7a4-87af748a0cca%26pf_rd_r%3DTRZK6PWR67EMTCD0NWZF%26pf_rd_s%3Dcart-page-widgets%26pf_rd_t%3D40701%26psc%3D1%26refRID%3DTRZK6PWR67EMTCD0NWZF"
# # c = "https://www.amazon.com/Nail-Art-Tools--Manicure-Kit/dp/B01MR6ZH51"



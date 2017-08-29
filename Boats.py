############## Name : Gaurav Kulkarni, Gandhar Arvind Pathak
############## Data Mining (ISM 6136) - University of South Florida, Tampa
############## UID: U66784122
############## Final Project: Real Time Webscrapping through Python and Applied Exploratory Data Analysis
############## Date: November 12, 2016

############## Objective: This code is written to fetch basic details of a Boat, from an advertisement website " http://www.boattrader.com "
##############            The search limits to 500 miles radius from the user location: precisely zipcode: 33613 (Tampa). The collected data is to be subjected to
##############            exploratory data analysis for different data visualizations and data mining. This is achieved through webscrapping in Python.

__author__ = 'gandh'
# Initial imports
import requests
import re  # For String manupulation like removing special characters from string
import csv  # To write output to CSV file

#make sure Beautiful Soup 4 is installed
from bs4 import BeautifulSoup, SoupStrainer
import bs4  # import main module first
print "Beautiful Soup Version " + bs4.__version__


# Function definations

# Opens each listing by the URL and creates a structure of the internal HTML elements
def Open_listing(each_listing):
    html = each_listing  # you'll need to define this.
    r = requests.get(html)
    html = r.text
    # we start with getting the soup for each page.
    list_struct = BeautifulSoup(html, "html.parser")
    return list_struct
#Function End

# For each listing, fetches information like Price, Length, Location, Class, Seller Contact, etc
def fetch_AdInfo(ad_page):
    page_info = {}  # temporary dict to hold page information-- returned as 'details' dictionary
    try:
        # Find Boat details
        for detail in ad_page.find_all('div', {'class': 'collapsible open'}):
            tables = detail.findChildren('table')
            Boat_Details_table = tables[0]
            rows = Boat_Details_table.findChildren(['tr'])
            for cell in rows:
                th_val = cell.findChildren('th')
                td_val = cell.findChildren('td')
                page_info[th_val[0].string] = td_val[0].string
    except:
        pass

    # find Sellers contact number
    temp = ad_page.find('div', {'class': 'contact'})
    try:
        if temp is None:
             page_info['Seller_Contact'] = "0"
        else:
            try:
                for contact in ad_page.find_all('div', {'class': 'contact'}):
                    page_info['Seller_Contact'] = re.sub('\W+', '',contact.string)  # remove special characters from contact number and store in the page_info list
            except:
                pass
    except:
        pass

    # Find ZIPCODE of the Boat Location
    temp = ad_page.find('span', {'class': 'postal-code'})
    try:
        if temp is None:
            page_info['ZipCode'] = "0"
        else:
            for zipcode in ad_page.find_all('span', {'class': 'postal-code'}):
                page_info['ZipCode'] = zipcode.string
    except:
        pass

    # Find Price of the Boat
    temp= ad_page.find_all('span', {'class': 'bd-price contact-toggle'})
    try:
        if temp is None:
            page_info['Price'] = "0"
        else:
            for price in ad_page.find_all('span', {'class': 'bd-price contact-toggle'}):
                page_info['Price'] = re.sub('\W+', '', price.string)  # removes '$' ','  and spaces
    except:
        pass

    return page_info

#Function End


# Write Ad information to excel CSV
# Make sure CSV file is created at given path

def write_to_excel(details, flag):
    inputFileName = "F:\PythonFiles\FinalProject\TestCsv.csv"
    len_of_details = details.__len__()
    for key, value in details.iteritems():
        temp = {}
        temp = value[0]
        with open(inputFileName, "ab") as f:
            w = csv.writer(f)
            if flag == 0:
                wh = csv.DictWriter(f, temp.keys())
                wh.writeheader()
                w.writerow(temp.values())
                flag = 1
            else:
                w.writerow(temp.values())
    return flag

#Function end


# Finds total number of pages and listings per page returned by the search results
def find_search_results_details(raw_html):
    r = requests.get(raw_html)
    raw_html = r.text
    lastpage_struct = BeautifulSoup(raw_html, "html.parser")
    for lastpage in lastpage_struct.find_all('a', {'class': 'last'}, href=True):
        href = lastpage['href'].encode('utf-8')
        href = href.split(",")
        listings_per_page = re.sub('\W+', '', href[1])  # removes special characters
        total_search_pages = href[0][-3:]  # Extracts the last 3 characters of the string which is the total pages in the search results
        return listings_per_page, total_search_pages
#Function End


def main():
    raw_html = "http://www.boattrader.com/search-results/NewOrUsed-any/Type-any/Category-all/Zip-33613/Radius-500/Sort-Length:DESC/Page-1,28"  # master  link to fetch data from
    page_number = 1 # maintains count of page number of the search results
    count_per_page, total_pages = find_search_results_details(raw_html)
    flag = 0  # to maintain record of headers
    while page_number <= total_pages:
        linklist = [] #Holds the individual advertisement links on each page
        details = {} # Dictionary which holds the required details of each advertisement, fetched from each page out of 'n' different advertisement pages
        raw_html = "http://www.boattrader.com/search-results/NewOrUsed-any/Type-any/Category-all/Zip-33647/Radius-200/Sort-Updated:DESC/Page-%s,%s"%(page_number,count_per_page)# you'll need to define this.
        r = requests.get(raw_html)
        raw_html = r.text
        # we start with getting the soup for each page.
        bs_struct = BeautifulSoup(raw_html, "html.parser")
        # we then look for all the <li>
        for listing in bs_struct.find_all('section', {'class': 'boat-listings'}):
            for ol_tag in listing.find_all('ol', {'class': 'boat-list'}):
                for listing_link in ol_tag.find_all('li'):
                    links = listing_link.find_all('a', href=True)
                    if len(links) != 0:  # make sure it found something.
                        link = links[0]
                        url = link['href'].encode('utf-8')
                        linklist.append(url)  # store the URL of each listing on a particular page
        page_number += 1

        # Enter Each listing and find information

        for each_listing in linklist:
            each_listing = "http://www.boattrader.com" + each_listing
            ad_page = Open_listing(each_listing)  #opens connection to each listing
            details[each_listing] = [fetch_AdInfo(ad_page)] #fetches details of the connected listing: Details like Price, Length, Location, Class, Seller Contact, etc

        flag = write_to_excel(details, flag) #write fetched information to a CSV file
        print "Completed Processing Page: %s out of %s " % (page_number - 1, total_pages)


main()

# Name:   		 Web Crawler 
# Description :  A robust text scraper to connect to page on www.sears.com and 
# 				 return results about a given keyword. 
#                To inlude all the the dependencies, I used virtualenv in this 
#                assignment. To run this .py file, first run the virtualenv by 
#                typing source bin/activate.
# Author: 		 Gongxun (Jack) Liu
# Created: 		 2014.9.30

import urllib2
from bs4 import BeautifulSoup
import argparse
import re
import requests


# parse command line args 
# @ returns an array of [unparsedKeyword,parsedKeyword,parsedPageNum]
def parseArgs():

    parser = argparse.ArgumentParser()
    parser.add_argument("keyword",help="enter the keyword",nargs="?",default="noitem")
    parser.add_argument("pageNum",help="enter the page number",nargs="?",default=0, type=int)
    args = parser.parse_args()
    
    inputKeyword=args.keyword
    inputPagenum=args.pageNum

    parsed=[]
    parsed.append(inputKeyword)
    parsed.append(inputKeyword.replace(" ","%20"))
    parsed.append(inputPagenum)
    return parsed


# Check spelling of the command line input  

# there is not spelling check in sears
# @returns 0 if there is no autocorrect for the keyword
#          autocorrected keyword if there is any 
def autoCorrectCheck(soup):
    spellcheck=soup.find("span",{"class":"searchTerm"})
    if spellcheck!=None:
        return spellcheck.text.strip()
    else:
        return 0

# Check the case of no result 
# @returns 1 if there are no result for key word
#          0 if there are items for key word  
def noresultCheck(soup):
    noresult=soup.find("div",{"id":"noResultsHeading"})
    if noresult!=None:
         return 1
    return 0



# Check if the keyword is a department name
# @returns 1 if the keyword belongs to a department name
#          0 if the keyword doesn't belong to a department name
def departmentCheck(soup):
    numProdItems=soup.find('div',{'id':'nmbProdItems'})
    if numProdItems==None:        
        return 1
    return 0


# this fuction handles the redirect of the url
# @ returns the newly redirected url
def handleRedirect(baseurl,parsedkeyword,viewItems):
    url=baseurl+"/search="+parsedkeyword +"?"+viewItems #assemble url
    req = urllib2.Request(url)
    thing = urllib2.HTTPRedirectHandler()
    thing2 = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(thing, thing2)
    try:
        page = opener.open(req).read()

        rawurl = re.findall(r"var url = \"(.+?)\";",page)
        if rawurl==[]: # that's a noresult
           return url
        return baseurl+rawurl[0].replace("\\","")
    except:

        r = requests.get(url, allow_redirects=True)
        return r.url



def main():


    # parse command line input
    parsed=parseArgs()
    
    keyword=parsed[0]
    parsedkeyword=parsed[1]
    pageNum=parsed[2]


    if keyword.isspace() or parsedkeyword=='' or parsedkeyword=="noitem":
        print "Enter someting,bro~"
        return 
    
    baseurl="http://www.sears.com" # base url of the site
    viewItems="viewItems=25"    # default viewItem=25

    redirectedurl=handleRedirect(baseurl,parsedkeyword,viewItems).replace(" ","%20")
    req = urllib2.Request(redirectedurl)
    try:
        r = urllib2.urlopen(req).read()
    except:
        print "Java Script is messing up with my crawler!"
        #print redirectedurl
        return 
    # soup
    soup=BeautifulSoup(r)
         
        # check no resulf for keyword
    if noresultCheck(soup)==1:
            print '--------------------'
            print "Sorry we could not find any matches for "+'''"'''+keyword+'''"'''+"."
            return 
         
         # check if the input is department store name
    if departmentCheck(soup)==1:
            text=soup.find('title').text
            print '--------------------'

            print 'You are in catagory of '+text+'.'
            print 'Find what you want here by searching something more specific.'
            return

    if autoCorrectCheck(soup)!=0:
            print '--------------------'
            print "You are searching for: ",autoCorrectCheck(soup)

    # get the container for numbers of all products and sears only products
    Items=soup.find_all('span',{'class':'tab-filters-count'})
                
    allnum=Items[0].text.replace("(","").replace(")","")

    #--------------------------Query 1 return total number of results---------    
    if parsed[2]==0:
    
        print "All products found: ",allnum
        
        print "Sears only found: ",Items[1].text.replace("(","").replace(")","")

    
    #--------------------------Query 2 return object---------    
    else: 
        
        try:
            allnum=int(allnum)
            pageUpBound=allnum/25+1
        except:
            pageUpBound=20 # could modify to a bigger one
        
        # check if pageNumber is valid 
        if pageNum>pageUpBound or pageNum<1:
            print "Invalid page number! Try one between 1 and "+str(pageUpBound)+"."
            return 


        # assemble new url with pageNum
        if '?' in redirectedurl:
            pageurl=redirectedurl+"&pageNum="+str(pageNum)
        else:
            pageurl=redirectedurl+"?pageNum="+str(pageNum)

        #print pageurl

        req_page = urllib2.Request(pageurl)
        r_page = urllib2.urlopen(req_page).read()

        # new soup
        soup_page=BeautifulSoup(r_page)

        

        # get all containers
        containers=soup_page.find_all('div',{'class':'cardContainer\
         addToCartEnabled'})

        
        i=1 # label all items 

        for container in containers:
            # fetch title from the page
            title=container.find('h2',{'itemprop':'name'})
            print '--------------------'
            print i
            i+=1
            
            print "Title:"+title.find('a').text
            # handle the no price case
            try:
                price=container.find('span',{'class':'price_v2 intShipHide'}).text
            except:
                price="unavailable"
            print "Price:"+price
            
            # handle the no vendor case
            # note that the for loop is to find vendor information in different cases
            try:
                vendors=container.find('div',{'id':'mrkplc'}).find_all('p')
                #[-1].text
                vendor=""
                for v in vendors:
                    if v.text.startswith("Sold by"):
                        vendor=v.text
            except:
                vendor="Sold by Sears"
            print vendor
        


if __name__ == "__main__":
   main()
   
	

    
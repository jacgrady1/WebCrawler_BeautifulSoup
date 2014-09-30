# Name:   		 Web Crawler 
# Description :  A robust text scraper to connect to page on www.walmart.com and 
# 				 return results about a given keyword. 
# Author: 		 Gongxun (Jack) Liu
# Created: 		 2014.9.30

import urllib2
from bs4 import BeautifulSoup
import argparse
import re

# parse command line args 
# @ returns an array of [unparsedKeyword,parsedKeyword,parsedPageNum]
def parseArgs():

    parser = argparse.ArgumentParser()
    parser.add_argument("keyword",help="enter the keyword",nargs="?",default="digital camera")
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
    #print numProdItems
    if numProdItems==None:        
        return 1
    return 0


# Count the number of items appears on that page
def countItem(url):
    r=requests.get(url)
    soup=BeautifulSoup(r.content)
    items = soup.find_all("div",{"class":"tile-content-wrapper"})
    return len(items)


# this fuction handles the redirect of the url
# returns the newly redirected url
def handleRedirect(baseurl,parsedkeyword,viewItems):
    #print parsedkeyword
    url=baseurl+"/search="+parsedkeyword+"?"+viewItems #assemble url
    
    req = urllib2.Request(url)
    r = urllib2.urlopen(req).read()
    rawurl = re.findall(r"var url = \"(.+?)\";",r)
    if rawurl==[]: # that's a noresult
        return url
    return baseurl+rawurl[0].replace("\\","")


def main():


    # parse command line input
    parsed=parseArgs()
    
    keyword=parsed[0]
    parsedkeyword=parsed[1]
    pageNum=parsed[2]


    if keyword.isspace() or parsedkeyword=='':
        print "Enter someting,bro~"
        return 


    
    baseurl="http://www.sears.com" # base url of the site
    viewItems="viewItems=25"    # default viewItem=25

    #--------------------------Query 1 return total number of results---------    
    if parsed[2]==0:

        # get the redirected url
        redirectedurl=handleRedirect(baseurl,parsedkeyword,viewItems).replace(" ","%20")

        req = urllib2.Request(redirectedurl)
        r = urllib2.urlopen(req).read()
        
        # soup
        soup=BeautifulSoup(r)
        #print soup
         
        # check no resulf for keyword
        if noresultCheck(soup)==1:
            print '--------------------'
            print "Sorry we could not find any matches for "+'''"'''+keyword+'''"'''+"."
            return 
         
         # check if the input is department store name
        if departmentCheck(soup)==1:
            print '--------------------'
            print 'You are in department of '+keyword+'.'
            print 'Please search something specific.'
            return

        if autoCorrectCheck(soup)!=0:
            print '--------------------'
            print "You are searching for: ",autoCorrectCheck(soup)


        #print num
        #test=soup.find_all('strong')
        #print test
        Items=soup.find_all('span',{'class':'tab-filters-count'})
        #num=numProdItems.find('span')
        
        #print len(Items)
        print "All products found: ",Items[0].text.replace("(","").replace(")","")

        
        print "Sears only found: ",Items[1].text.replace("(","").replace(")","")

    #--------------------------Query 2 return object---------    
    else: 
        print type(pageNum)
        print pageNum
        redirectedurl=handleRedirect(baseurl,parsedkeyword,viewItems).replace(" ","%20")
        req = urllib2.Request(redirectedurl)
        r = urllib2.urlopen(req).read()
        
        # soup
        soup=BeautifulSoup(r)








        





if __name__ == "__main__":
   main()
   #print("--- %s seconds ---" % str(time.time() - start_time))

	

    
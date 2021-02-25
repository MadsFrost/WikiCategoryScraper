# Import packages
from collections import defaultdict
from bs4 import BeautifulSoup
import requests
import re
import Json

# A scraper class to individually scrape data
class dynamicScraper:
    def __init__(self, letter):
        self.letter = letter
        self.subUrls = []
        self.articleUrls = []
        self.articleData = []
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
    def scrapeArticles (self):
        for i in self.articleUrls:
            req = requests.get(i, self.headers)
            soup = BeautifulSoup(req.content)
            content = soup.find("div", {"id": "content"})
            title = content.findChildren("h1", {"id": "firstHeading"})[0]
            
            if title is None:
                title = "No title available"
            else:
                title = title.get_text()
                
            paragraphs = content.findChildren("div", {"class": "mw-parser-output"})[0]
            published = ""
            published = content.find("strong", {"class": "published"}).get_text()
            

           
                
            cleanedContent = ""
            for i in paragraphs.findChildren("p", recursive=False):
                cleanedContent += (i.get_text())
            cleanedContent = cleanedContent[cleanedContent.find('\xa0')+2:]
            cleanedContent = cleanedContent.replace('\n', ' ')
            cleanedContent = cleanedContent.replace("\\", "")
            #print("Couldn't format data on article: " + title)
            self.articleData.append([title, published, cleanedContent])
        return self.articleData

                                        
    def wikiSubCategoryLinks(self, subUrls, domain):
        for i in subUrls:
            req = requests.get(i, self.headers)
            soup = BeautifulSoup(req.content)
            categories = soup.find_all("div", {"class": "mw-content-ltr"})
            counter = 0
            for a in categories[1].findAll('a'):
                self.articleUrls.append(domain + a['href'])
        return self.scrapeArticles()



    def wikiCategoryLinks(self, URL):
        pattern = re.compile("^"+ self.letter)
        req = requests.get(URL, self.headers)
        soup = BeautifulSoup(req.content)
        header = soup.find('h3', string=self.letter) 
        if header == None:
            return self.letter + " - does not exist on page."
        parent = header.parent()

        
        #find('h3', string=self.letter)
        #Tags = child.parent()

        #print(parent[1].findAll('a', href=re.compile(self.letter)))

        for a in parent[1].findAll('a', href=re.compile(self.letter)):
            self.subUrls.append(URL[:23] + a['href'])     
            
        return self.wikiSubCategoryLinks(self.subUrls, URL[:23])
  
    
    
# Data Module containing the entire hashtable of scraped keywords
class Data:
    def __init__(self, letterFilter, Url):
        self.letterFilter = letterFilter          # ['N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Z']
        self.Url = Url                            # https://en.wikinews.org/wiki/Category:Politics_and_conflicts
        self.scrapeDict = defaultdict(list)       # Dictionary with letter keys and scrape class for each
        self.dataDict = defaultdict(list)         # cleaned Data Dictionary - Get filled after scraping each individual characters category
                                                  # - urls and goes through each link content and will fill dataDict

    def initalizeScrapeDict(self):
        for i in self.letterFilter:
            self.scrapeDict[i] = dynamicScraper(i)  # Initalize a scrape dictionary and fill corresponding: 
                                                    # 'N' : new Class(dynamicScraper('N', []))

    def scrapeWiki(self):
        self.initalizeScrapeDict()
        for i in self.scrapeDict:
            self.dataDict[i] = self.scrapeDict[i].wikiCategoryLinks(self.Url)      
                                                        # Looping through each individual key's scrape class and calling 
                                                        # the method wikiLetterScraper, where the scraper already  
                                                        # knows each individual letter
    def getData(self):
        return self.dataDict

# Get the letters to be scraped from Wiki and assign the keys to the defaultdict
searchString = list("ABCDEFGHIJKLMNOPRSTUVWZABCDEFGHIJKLMNOPRSTUVW"[13%23:13%23+10])
WikiData = Data(['B', 'D'], "https://en.wikinews.org/wiki/Category:Politics_and_conflicts") # Initalizes a new data class
WikiData.scrapeWiki() # Starts scraping each letters category corresponding urls


"""
1. Make a pandas data-frame 
"""

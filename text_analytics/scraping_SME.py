
# coding: utf-8

# In[2]:

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


# In[3]:

class ScrapeSME:
    def __init__(self):
        # Base soup object
        self.page = requests.get("http://www.sme.sk")
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        
        # I will be adding links here constantly so needs to be class variable
        # loading old links from disk
        try:
            self.scraped_links = list(pd.read_csv(data_path + "sme_links.csv", sep = "|").links.values)
            print len(self.scraped_links), "links loaded from disk"
        except IOError:    
            # Empty link list if no data are on the disk
            self.scraped_links = []
        self.scraped_links = []
    
    def find_body(self, soup = None):
        if soup is None:
            soup = self.soup
        main_content = list(soup.children)
        for i in main_content:
            #ked zacina cast <html tak to je main part
            if str(i).find("<html") == 0:
                inner_content = i
                for j in inner_content:
                    if str(j).find("<body") == 0:
                        body = j
                        print "Find HTML <body>: Successfull!!"
        if 'body' not in locals():
            print "body wasn't find"
            body = None
        return body
    
    def find_initial_links(self):
        article_links = []
        summaries = []
        body = self.find_body()
        for i in body.select('div.col-responsive div a.js-smphr-item'):
            link = str(i.get("href"))
            if link.find("?") != -1:
                link = link[:link.find("?")]
            summaries.append(i.get_text())
            article_links.append(link)
    
        return article_links, summaries
            
    def scrape(self):
        # initial links to scrape
        article_links, summaries = self.find_initial_links()
        self.sme_articles = {}
        i = 0
        while i < len(article_links):
            print "Number of articles for download:",len(article_links)
            print "Scraping article number", i+1
            link = article_links[i]
            print link
            summary = summaries[i]
            # skip this interation if link is already parsed
            if link in self.scraped_links:
                print "Link already scraped, skipping...!"
                print ""
                i = i + 1
                continue
            
            # sometimes link doesn't work
            try:
                article = requests.get(link)
            except:
                print "link was corrupted"
                print ""
                i = i + 1
                # skips rest of the loop
                continue
            
            local_soup = BeautifulSoup(article.content, 'html.parser')
            # find HTML <body> tag
            body = self.find_body(soup = local_soup)
            if body == None:
                print "link was corrupted"
                print ""
                i = i + 1
                # skips rest of the loop
                continue
            # label is group of news from webpage
            label = re.search('//(.*).sme.sk', link).group(1)
            text = ""
            # identification of text of the article
            for article_part in body.select('article p'):
                 text = text + "\n" + article_part.get_text()
            self.sme_articles[i] = (label,summary, text)
            
            #identification of next articles:
            for next_article in body.select('div.media-body h2.media-heading a'):
                # getting new links from current article
                new_link = str(next_article.get("href"))
                # sometimes, there is a source page after the "?" leading to duplicates in the link
                if new_link.find("?") != -1:
                    # removing part after the "?"
                    new_link = new_link[:new_link.find("?")]
                new_summary = next_article.get_text()
                # if new_link is not in the list, then it will be added
                if new_link not in article_links:
                    article_links.append(new_link)
                    summaries.append(new_summary)
                    
            #identification of next articles:
            for next_article in body.select('div.cr-box div.cr-content h4 a'):
                new_link = str(next_article.get("href"))
                if new_link.find("?") != -1:
                    new_link = new_link[:new_link.find("?")]
                new_summary = next_article.get_text()
                if new_link not in article_links:
                    article_links.append(new_link)
                    summaries.append(new_summary)
            
            i = i + 1
            self.scraped_links.append(link)
            print "Done!!"
            print ""
            
            # Saving to disk temp results
            if (i%100 == 0) & (len(self.sme_articles) > 1):
                print "Saving partial results to disk!"
                df_articles = pd.DataFrame(self.sme_articles).transpose()
                df_articles.columns = ["label","summary","text"]
                df_articles.to_csv(data_path + "temp_sme_articles.csv", sep = "|", index=False, encoding="utf-8")
                df_links = pd.DataFrame(self.scraped_links)
                df_links.columns = ["links"]
                df_links.to_csv(data_path + "temp_sme_links.csv", sep = "|", index=False, encoding="utf-8")
        
        # Creating final dataframe and saving to disk
        # TODO better savings
        if len(self.sme_articles) > 0:
            postfix = str(time.time())
            if postfix.find(".") != -1:
                postfix = postfix[:postfix.find(".")]
            
            print "Saving final results to disk!"
            df_articles = pd.DataFrame(self.sme_articles).transpose()
            df_articles.columns = ["label","summary","text"]
            df_articles.to_csv(data_path + "sme_articles"+ postfix + ".csv", sep = "|", index=False, encoding="utf-8")
            df_links = pd.DataFrame(self.scraped_links)
            df_links.columns = ["links"]
            df_links.to_csv(data_path + "sme_links.csv", sep = "|", index=False, encoding="utf-8")
        else:
            print "No new articles scraped"
        return self.sme_articles, self.scraped_links


# In[4]:

# x = ScrapeSME()
# articles, links = x.scrape()


# In[5]:

data_path = "/Users/jurajkapasny/Data/sk_text_for_api/"


# In[6]:

if __name__ == '__main__':
    start_time = time.time()
    scraper = ScrapeSME()
    articles, links = scraper.scrape()
    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed / 60)
    seconds = elapsed % 60
    print "Number of scraped articles:", len(articles)
    print "Time Elapsed:", minutes, "minutes and", seconds, "seconds"
    print "================================="
    print ""    


# In[ ]:




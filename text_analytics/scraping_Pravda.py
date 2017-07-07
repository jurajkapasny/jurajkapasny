
# coding: utf-8

# In[1]:

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


# In[2]:

class ScrapePravda:
    def __init__(self):
        # Base soup object
        self.page = requests.get("http://www.pravda.sk")
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        
        # I will be adding links here constantly so needs to be class variable
        # loading old links from disk
        try:
            self.scraped_links = list(pd.read_csv(data_path + "pravda_links.csv", sep = "|").links.values)
            print len(self.scraped_links), "links loaded from disk"
        except IOError:    
            # Empty link list if no data are on the disk
            self.scraped_links = []
#         self.scraped_links = []
    
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
        body = self.find_body()
        for i in body.select('section.hp-box-spravy div.article-square div.no-padding-side'):
            # link is always first elementh in the paragraph, sometimes is missings (taking from minuta po minute)
            try:
                link = str(i.select('h4 a')[0].get("href"))
            except IndexError:
                continue
            if link.find("?") != -1:
                link = link[:link.find("?")]

            article_links.append(link)
    
        return article_links
            
    def scrape(self):
        # initial links to scrape
        article_links = self.find_initial_links()
        self.sme_articles = {}
        i = 0
        while i < len(article_links):
        #while i < 4:
            print "Number of articles for download:",len(article_links)
            print "Scraping article number", i+1
            link = article_links[i]
            print link            
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
            # label is group of news from webpage
            try:
                label = re.search('.pravda.sk/(.*?)/', link).group(1)
            except AttributeError:
                label = ""

            # summary is in the first paragraph
            for desc in body.select('article.article-detail div.article-detail-perex p'):
                 summary = desc.get_text()
            # identification of text of the article
            text = ""
            for article_part in body.select('article.article-detail div.article-detail-body p'):
                 text = text + "\n" + article_part.get_text()
            
            
            self.sme_articles[i] = (label,summary, text)
            
            #identification of next articles:
            for next_article in body.select('aside.article-detail-body-odporucame div.article-head h3 a'):
                # getting new links from current article
                new_link = str(next_article.get("href"))
                # sometimes, there is a source page after the "?" leading to duplicates in the link
                if new_link.find("?") != -1:
                    # removing part after the "?"
                    new_link = new_link[:new_link.find("?")]
                if new_link.find("pravda.sk") == -1:
                    new_link = "https://spravy.pravda.sk/" + new_link
                # if new_link is not in the list, then it will be added
                if new_link not in article_links:
                    article_links.append(new_link)
                    
            #identification of next articles:
            for next_article in body.select('aside.hp-box-najcitanejsie li a'):
                new_link = str(next_article.get("href"))
                if new_link.find("?") != -1:
                    new_link = new_link[:new_link.find("?")]
                if new_link.find("pravda.sk") == -1:
                    new_link = "https://spravy.pravda.sk/" + new_link
                
                if new_link not in article_links:
                    article_links.append(new_link)
            
            i = i + 1
            self.scraped_links.append(link)
            print "Done!!"
            print ""
            
            # Saving to disk temp results
            if (i%100 == 0) & (len(self.sme_articles) > 1):
                print "Saving partial results to disk!"
                df_articles = pd.DataFrame(self.sme_articles).transpose()
                df_articles.columns = ["label","summary","text"]
                df_articles.to_csv(data_path + "temp_pravda_articles.csv", sep = "|", index=False, encoding="utf-8")
                df_links = pd.DataFrame(self.scraped_links)
                df_links.columns = ["links"]
                df_links.to_csv(data_path + "temp_pravda_links.csv", sep = "|", index=False, encoding="utf-8")
        
        # Creating final dataframe and saving to disk
        # TODO better savings
        if len(self.sme_articles) > 0:
            postfix = str(time.time())
            if postfix.find(".") != -1:
                postfix = postfix[:postfix.find(".")]
            
            print "Saving final results to disk!"
            df_articles = pd.DataFrame(self.sme_articles).transpose()
            df_articles.columns = ["label","summary","text"]
            df_articles.to_csv(data_path + "pravda_articles"+ postfix + ".csv", sep = "|", index=False, encoding="utf-8")
            df_links = pd.DataFrame(self.scraped_links)
            df_links.columns = ["links"]
            df_links.to_csv(data_path + "pravda_links.csv", sep = "|", index=False, encoding="utf-8")
        else:
            print "No new articles scraped"
        return self.sme_articles, self.scraped_links


# In[3]:

# x = ScrapePravda()
# articles, links = x.scrape()


# In[4]:

data_path = "/Users/jurajkapasny/Data/sk_text_for_api/"


# In[ ]:

if __name__ == '__main__':
    start_time = time.time()
    scraper = ScrapePravda()
    articles, links = scraper.scrape()
    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed / 60)
    seconds = elapsed % 60
    print "Number of scraped articles:", len(articles)
    print "Time Elapsed:", minutes, "minutes and", seconds, "seconds"
    print "================================="
    print ""


# In[57]:

# this_lin = pd.read_csv(data_path+"temp_pravda_links.csv", sep ="|")


# In[14]:

# def find_body(soup):
#     main_content = list(soup.children)
#     for i in main_content:
#         #ked zacina cast <html tak to je main part
#         if str(i).find("<html") == 0:
#             inner_content = i
#             for j in inner_content:
#                 if str(j).find("<body") == 0:
#                     body = j
#                     print "Find HTML <body>: Successfull!!"
#     return body


# In[55]:

# link = links.links[751]


# In[56]:

# # sometimes link doesn't work
# try:
#     article = requests.get(link)
# except:
#     print "link was corrupted"
#     print ""



# local_soup = BeautifulSoup(article.content, 'html.parser')
# # find HTML <body> tag
# body = find_body(soup = local_soup)

# # label is group of news from webpage
# # label is group of news from webpage
# try:
#     label = re.search('.pravda.sk/(.*?)/', link).group(1)
# except AttributeError:
#     label = ""

# # summary is in the first paragraph
# for desc in body.select('article.article-detail div.article-detail-perex p'):
#      summary = desc.get_text()
# # identification of text of the article
# text = ""
# for article_part in body.select('article.article-detail div.article-detail-body p'):
#      text = text + "\n" + article_part.get_text()

# article_links = []
# #identification of next articles:
# for next_article in body.select('aside.article-detail-body-odporucame div.article-head h3 a'):
#     # getting new links from current article
#     new_link = str(next_article.get("href"))
#     # sometimes, there is a source page after the "?" leading to duplicates in the link
#     if new_link.find("?") != -1:
#         # removing part after the "?"
#         new_link = new_link[:new_link.find("?")]
#     if new_link.find("pravda.sk") == -1:
#         new_link = "https://spravy.pravda.sk/" + new_link
#     # if new_link is not in the list, then it will be added
#     if new_link not in article_links:
#         article_links.append(new_link)

# #identification of next articles:
# for next_article in body.select('aside.hp-box-najcitanejsie li a'):
#     new_link = str(next_article.get("href"))
#     if new_link.find("?") != -1:
#         new_link = new_link[:new_link.find("?")]
#     if new_link.find("pravda.sk") == -1:
#         new_link = "https://spravy.pravda.sk/" + new_link

#     if new_link not in article_links:
#         article_links.append(new_link)

# print text
# print ""
# print summary


# In[ ]:




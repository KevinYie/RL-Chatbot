from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import pandas as pd

def webscraper(depth):
    # Final Dataframe
    final = pd.DataFrame.from_dict({"query": ["None"], "response": ["None"], "author": ["None"]})
    queries = []
    responses = []
    authors = []
    # Iterating through pages of forum
    for i in range(depth):
        # Finding all posts on forum page 
        url = "https://patient.info/forums/discuss/browse/depression-683?page={}#group-discussions".format(int(i))
        page = urlopen(Request(url, headers = {"User-Agent": "Mozilla/5.0"})).read()
        soup = BeautifulSoup(page, 'html.parser')
        
        href = [i["href"] for i in soup.find_all("a", href = True)]
        post_links = list(filter(lambda x:re.match(r"/forums/discuss/", x), href))
        post_links = list(set(post_links))
        
        # Iterating through every post on forum page
        for x in post_links:
            posturl = "https://patient.info/{}".format(str(x))
            postpage = urlopen(Request(posturl, headers = {"User-Agent": "Mozilla/5.0"})).read()
            soup = BeautifulSoup(postpage, 'html.parser')
            query = soup.find("div", {"class": "post__content"}).get_text()

            # Creating list in case of multiple responses
            temp = []
            
            for el in soup.findAll("div", {"class": "post__content break-word"}):
                temp.append(el.get_text())
                
            # Creating list in case of multiple authors
            author_temp = []
            
            for el in soup.findAll("a", {"class": "author__name"}):
                author_temp.append(el.get_text())
                
            

            # Appending all to respective lists
            if len(temp) == 1:  
                queries.append(query)
                responses.append(temp[0])
                authors.append(author_temp[1])
            elif len(temp) > 1:
                queries += [query]*len(temp)
                responses += temp
                authors += author_temp[1:]
                
            else:
                queries.append("None")
                responses.append("None")
                authors.append("None")
                
            
                
    final = final.append(pd.DataFrame.from_dict({"query": queries, "response": responses, "author": authors}), ignore_index = True)
    final.drop(0, inplace = True)

    return final, queries, responses, authors

df, queries, responses, authors = webscraper(100)
df.to_csv("unprocessed_posts_with_authors.csv", index = False)

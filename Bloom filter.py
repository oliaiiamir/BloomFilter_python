#!/usr/bin/env python
# coding: utf-8

#  ##   bloom filter

# ## 1- scraping

# In[ ]:


import requests 
from bs4 import BeautifulSoup
from IPython.display import clear_output
import time



base_url = "https://time.com"


def add_to_file(url):  #add urls in page into txt
    with open('1- url.txt','a') as file:
        file.write(url + '\n')

for page in range(1,74):      #73  #each page have 7 article

    url = f"https://time.com/section/tech/?page={page}"

    res = requests.get(url)

    soup = BeautifulSoup(res.text,'lxml')

    for article in soup.find_all('article'):
        add_to_file(base_url + article.a['href'])
    clear_output(wait=True)
    print('Page number {}'.format(page))
    print('Waiting at least for 5 sec for each page... ')
    time.sleep(5)


# ## 2- Download Text and Title

# In[ ]:


from newspaper import Article
from newspaper import Config


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'  #Google this: 'what is my user agent'

config = Config()
config.browser_user_agent = user_agent
config.request_timeout = 50  #Set default timeout


def text_to_file(articleTxt):  #Articles text to txt file: '2- text.txt'
    with open('2- text.txt','a',encoding="utf-8") as file:
        file.write( articleTxt + '\n' )

def article_title(articleTitle,c):  #Article titles to txt file: '2- TitleList.txt'
    with open('2- TitleList.txt','a',encoding='utf-8') as file:
        file.write( c + '\n' + articleTitle + '\n' )
        
        
urlfile = '1- url.txt'

with open(urlfile) as f:  #Read urls and download news text and title
    line = f.readline()
    c = 0
    error = 1
    while line:
        line = line.rstrip('\n')
        a = Article(line,source_url="https://time.com",config=config)
        a.download()
        try:  #Use try/except for urls with read timeout error
            a.parse()
            text_to_file(a.text.lower())
            article_title(a.title.lower(),str(c))
        except :
            error +=1
            pass

        
        a = 'None'
        line = f.readline()
        clear_output(wait=True)
        print(c)
        time.sleep(2)
        c += 1
        
'{} article download corectly and {} article had downloading problem...!!'.format(c,error)        


# ### 3- Find keywords

# In[ ]:


#Find N keyword from text

from gensim.summarization import keywords

tf = open('2- text.txt',encoding='utf-8')
tf = tf.read()

N = input('Number of keywords : ')
keyword = keywords(tf , words=N,split=True,lemmatize = True)
keyword


# ## 4- Bloom filter and hash

# ### 4.1- Using formula

# In[ ]:


#Find best number of hashs for bloom filter
# m = length of each hash
# n = number of words in bloomFilter

m=10**4
n=N
ln2 = 0.693147181
k = round((m/N)*ln2)

print(k)    


# ### 4.2- Using threshold..

# In[ ]:


# Find first best number of hash tables base on 'flase positive probability '

from lhbf import BloomFilter

h = 1
fppPre = 99
m=10**4

while True:
    bf = BloomFilter(m=m , k=h )  # m can't be less than 50
    
    for key in keyword:  #n = 20
        bf.add(key)
    
    fpp = bf.estimate_fpp()    
    if (fpp >= fppPre):
        h -= 1
        fpp = fppPre
        bf = BloomFilter(m=m , k=h )
        for key in keyword:  #n = 20
            bf.add(key)
        break    
    else:
        h +=1
        fppPre = fpp

'Number of hash functions are : {} and flase positive probability is : {} '.format(h , fpp)


# ## 5- Find news with keyword...

# In[ ]:


# This one save the first Word that were in bloom filter and title(might be a false positive)
# C -> news(url) number
# And title itself
def filtered_news(Word , Title , C):
    with open('3- PassedTitles.txt','a') as file:
        file.write(C + '\n' + Word + '\n' + Title + '\n');

        
        
Title = '2- TitleList.txt'  
q = 0


# And this one read title file and check each word in it to see if it's in the bloom filter or not...
with open(Title) as f:
    f.readline()
    line = f.readline()
    c = 0
    while line:
        title = line.rstrip('\n')
        TitleWords = title.split()
        for i in range(len(TitleWords)):
            
            if (bf.might_contain(TitleWords[i])):
                filtered_news(TitleWords[i] , title , str(c))
                q += 1
                break
        
        clear_output(wait=True)
        print(c)
        c += 1
        f.readline()
        line = f.readline()


'{} news title had at least one keyword...'.format(q)       


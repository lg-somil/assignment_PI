import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import copy
import random
# from google.cloud import bigquery
import os

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__),'./../config/service_account_GCP.json')
# 

def write_to_bigquery(data, project_id, dataset_id, table_id):
    
    client = bigquery.Client(project=project_id)

    table_ref = client.dataset(dataset_id).table(table_id)
    
    try:
        table = client.get_table(table_ref)
    except Exception as e:
        print(f"Table {dataset_id}.{table_id} not found. Please check the table name.")
        return

    errors = client.insert_rows_json(table, data)

    if errors:
        print(f"Errors occurred while inserting rows: {errors}")
    else:
        print(f"Successfully inserted {len(data)} rows into {dataset_id}.{table_id}")



def fetch_finshots_articles2(*argv):
    print(argv)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://finshots.in")
    time.sleep(3)
    search_icon = driver.find_element(By.CSS_SELECTOR, ".icon.icon--ei-search.icon--s.c-nav__icon:nth-child(1)")
    search_icon.click()
    time.sleep(2)
    all_keyword_articles = {}
    for keyword in argv:
        search_input = driver.find_element(By.CSS_SELECTOR, "input[aria-label='Search Finshots']")
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)
        time.sleep(5)
        article_container = driver.find_element(By.XPATH, "//div[@class='c-search-results js-search-results']")
        article_links = article_container.find_elements(By.TAG_NAME, "a")
        article_urls = []
        for link in article_links:
            url = link.get_attribute("href")
            article_urls.append(url)
        all_keyword_articles.update({keyword: copy.deepcopy(article_urls)})

    return all_keyword_articles

def fetch_article_content(url):
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')            
            main_title = soup.title.string
            article_content = ' '.join([p.text for p in soup.find_all('p')])
            
            return main_title, article_content
        else:
            return None, f"Error: Unable to fetch article, status code: {response.status_code}"
    except Exception as e:
        return None, str(e)

def requests_post(url, json):
    random_number = random.randint(0, 1)
    return {'sentiment_score': random_number}

def get_sentiment_score(news_text):
    api_url = "https://mock-api.com/sentiment"
    payload = {"text": news_text}
    response = requests_post(api_url, json=payload)
    
    # Assuming the response returns a JSON with the sentiment score
    sentiment_score = response.get("sentiment_score")
    
    return sentiment_score


def scrape_finshot():
    article_urls = fetch_finshots_articles2('HDFC', 'TATA Motors')
    data = []
    for k,v in article_urls.items():
        for url in v:
            title, content = fetch_article_content(url)
            row = {}
            row.update({'Keyword': k })
            row.update({'Title': title })
            print(row)
            row.update({'Content': content })
            row.update({'sentiment_score': get_sentiment_score(content)})
            data.append(row)
    return data




scraping_output = scrape_finshot()
print(scraping_output[0].get('Keyword'))
print(scraping_output[0].get('Title'))
print(scraping_output[0].get('Content'))
print(scraping_output[0].get('sentiment_score'))



# project_id = "your_project_id"
# dataset_id = "your_dataset_id"
# table_id = "your_table_id"

# write_to_bigquery(scraping_output, project_id, dataset_id, table_id)


    

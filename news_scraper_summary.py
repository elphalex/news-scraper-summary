# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:15:01 2023

This script scrapes the latest news article titles from Google News for specific economic keywords, 
summarizes them using OpenAI's GPT-3, and creates an informative daily report.

"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import openai
import re

openai.api_key = "YOUR_API_KEY"

def get_article_titles(search_term):
    url = f"https://news.google.com/search?q={search_term}&hl=en-US&gl=US&ceid=US%3Aen"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("a", {"class": "DY5T1d"})
    titles = [article.text for article in articles]
    return titles[:25]

search_terms = ["inflation", "interest rates", "economic indicators", "geopolitical events", "regulation", "stock market", "commodities", "technology"]
df = pd.DataFrame(columns=search_terms)

for search_term in search_terms:
    titles = get_article_titles(search_term)
    df[search_term] = titles

delimiter = ". "
chunks = []
for search_term in search_terms:
    titles = df[search_term].tolist()
    text = delimiter.join(titles)
    for i in range(0, len(text), 4096):
        chunk = text[i:i+4096]
        chunks.append(chunk)

summaries = []
for chunk in chunks:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"These are the most recent news article titles from google from a certain economic keyword please create a 4 sentence summary of the current state of the market and economy based off titles. The titles that would have the biggest impact on the economy are the most important: {chunk}"}
        ]
    )
    summary = response.choices[0].message.content
    summaries.append(summary)

final_summary = "\n".join(summaries)
final_summary = re.sub('\s{2,}', ' ', final_summary)

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": f"You just created economic summaries from recent news article titles related to key words including inflation, interest rates, economic indicators, geopolitical events, regulation, stock market, commodities, and technology. Can you create an informative and detailed daily report, with paragraphs containing similar topics, that a day trading investor would use for fundamental analysis that highlights the events from the following summaries that are most probable to have an impact on the economy. Please include a final paragraph that describes the most likely effects the news has on the stock market and forex: {final_summary}"}
    ]
)

final = response.choices[0].message.content
print(final)

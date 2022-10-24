import json
import requests
import openai

BASE_URL = "https://www.googleapis.com/customsearch/v1"
SEARCH_ENG_ID = "33d96791f7ddc438a"  # The author's search engine, which is just a full web Google search; you can replace this with your own

GOOG_API_KEY = ""
OPENAI_API_KEY = ""
try:
    with open("goog_apikey.txt") as fhand:
        GOOG_API_KEY = fhand.read()

    with open("openai_apikey.txt") as fhand:
        OPENAI_API_KEY = fhand.read()
except FileNotFoundError:
    print("""This code expects a Google Search api key to be stored in goog_apikey.txt \
and an openai api key to be stored in openai_apikey.txt. The Google api key can be requested from \
https://developers.google.com/webmaster-tools/search-console-api/v1/configure, and the openai key can be requested by \
following instructions from https://beta.openai.com/.""")
    exit(1)
    

def search(query, output_file="res.html"):
    url = BASE_URL + "?key=" + GOOG_API_KEY + "&q=" + query + "&cx=" + SEARCH_ENG_ID
    x = requests.get(url)
    
    with open("test.json", "w") as fhand:
        fhand.write(x.text)

    x = x.json()
    with open(output_file, "w") as fhand:
        fhand.write("<html>\n")
        fhand.write("""
        <head>
            <link rel="stylesheet" href="results.css">
        </head>
        """)
        fhand.write("<body>\n")
        fhand.write("<div class='query'>Query: " + query + "</div>")
        for item in x["items"]:
            fhand.write("<div class='res'>")
            fhand.write("<div class=res-link>" + item["displayLink"] + "</div>")
            fhand.write("<div class=res-title><a href=" + item["link"] + "/>" + item["title"] + "</a></div>")
            fhand.write("<div class=res-snippet>" + item["snippet"] + "</div>")
            fhand.write("</div>")
        fhand.write("</body>\n")
        fhand.write("</html>\n")

# search("Find the stationary distribution of a Markov chain")

def make_gpt_req(query):

    with open("prompt.txt", "r") as fhand:
        prompt = fhand.read().format(query=query)
    
    openai.api_key = OPENAI_API_KEY
    x = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        max_tokens=256,
        temperature=1,
        presence_penalty=1.5,
        frequency_penalty=2,
        best_of=4
    )
    return x['choices'][0]['text']

# print(make_gpt_req("python api bearer authentication"))
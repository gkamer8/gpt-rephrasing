import json
from math import prod
import requests
import openai
import os
import pickle

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

ERROR_STR = "<Parse Error>"

    

def search(query, output_file="res.html"):
    url = BASE_URL + "?key=" + GOOG_API_KEY + "&q=" + query + "&cx=" + SEARCH_ENG_ID
    x = requests.get(url)
    
    with open("test.json", "w") as fhand:
        fhand.write(x.text)

    x = x.json()

    results = [{"displayLink": y["displayLink"], "link": y["link"], "snippet": y["snippet"], "title": y["title"]} for y in x["items"]]
    return results

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


def parse_gpt_req(gpt_text):
    by_quote = gpt_text.split("\"")

    try:
        first = by_quote[0].strip()
        second = by_quote[2].strip()
        third = by_quote[4].strip()
    except:
        first = ERROR_STR
        second = ERROR_STR
        third = ERROR_STR
        print(f"Error parsing text: {gpt_text}")

    try:
        answer = by_quote[6].strip()
    except:
        answer = ERROR_STR

    
    return [first, second, third, answer]


def get_all():
    results = []
    lines = []
    with open("queries.txt") as fhand:
        lines = fhand.readlines()
    for i, line in enumerate(lines):
        print(f"On index {i} of {len(lines)}")
        gpt = make_gpt_req(line.rstrip())
        parsed = parse_gpt_req(gpt)
        results.append(parsed)
    
    # Output to files
    for i, res in enumerate(results):
        os.mkdir(os.path.join("queries", str(i)))
        with open(os.path.join("queries", str(i), str(i) + ".txt"), "w") as fhand:
            fhand.write(lines[i])  # the first output line is the original query
            for r in res:
                fhand.write(r + "\n")


def write_html(result, output_file, query):
    with open(output_file, "w") as fhand:
        fhand.write("<html>\n")
        fhand.write("""
        <head>
            <link rel="stylesheet" href="results.css">
        </head>
        """)
        fhand.write("<body>\n")
        fhand.write("<div class='query'>Query: " + query + "</div>")
        for item in result:
            fhand.write("<div class='res'>")
            fhand.write("<div class=res-link>" + result["displayLink"] + "</div>")
            fhand.write("<div class=res-title><a href=" + result["link"] + "/>" + result["title"] + "</a></div>")
            fhand.write("<div class=res-snippet>" + result["snippet"] + "</div>")
            fhand.write("</div>")
        fhand.write("</body>\n")
        fhand.write("</html>\n")


def produce():
    # Use get_all() to write all of the GPT-3 queries + the original query
    get_all()
    # Go through the files and search using each query; place the results of each individual query in separate pickle files.
    folders = os.listdir(os.path.join("queries"))
    for folder in folders:
        p = os.path.join(folder, folder + ".txt")
        with open(p, "r") as fhand:
            lines = fhand.readlines(p)
            for i, line in enumerate(lines):
                line = line.strip()
                if line == ERROR_STR:
                    continue
                res = search(line)
                to_write = open(os.path.join(p, str(i) + ".pkl"), "wb")
                pickle.dump(res, to_write)
    
    # Produce a ranking of results
    # TODO

    # Write HTML for the original results and the re-ranked results
    # TODO


produce()
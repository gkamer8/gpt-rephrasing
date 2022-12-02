import json
from math import prod
import requests
import openai
import os
import pickle
from make_test import gen_test

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

FINAL_RESULTS_N = 10

    

def search(query):
    url = BASE_URL + "?key=" + GOOG_API_KEY + "&q=" + query + "&cx=" + SEARCH_ENG_ID
    x = requests.get(url)
    
    with open("test.json", "w") as fhand:
        fhand.write(x.text)

    x = x.json()
    if 'error' in x:
        print(x)
        print(query)
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


def get_all(limit=None):
    results = []
    lines = []
    with open("queries.txt") as fhand:
        lines = fhand.readlines()
    for i, line in enumerate(lines):
        if limit and i >= limit:
            break
        print(f"On index {i} of {len(lines)}")
        gpt = make_gpt_req(line.rstrip())
        parsed = parse_gpt_req(gpt)
        results.append(parsed)
    
    # Output to files
    for i, res in enumerate(results):
        try:
            os.mkdir(os.path.join("queries", str(i)))
        except FileExistsError:
            pass
        with open(os.path.join("queries", str(i), str(i) + ".txt"), "w") as fhand:
            fhand.write(lines[i] + "\n")  # the first output line is the original query
            for r in res:
                fhand.write(r + "\n")


def write_html(results, output_file, query):
    with open(output_file, "w") as fhand:
        for item in results:
            fhand.write("<div class='res'>")
            fhand.write("<div class=res-link>" + item["displayLink"] + "</div>")
            fhand.write("<div class=res-title><a href=" + item["link"] + ">" + item["title"] + "</a></div>")
            fhand.write("<div class=res-snippet>" + item["snippet"] + "</div>")
            fhand.write("</div>")


def produce(rerun_gpt=False, rerun_search=False, limit=None):
    # Use get_all() to write all of the GPT-3 queries + the original query
    if rerun_gpt:
        get_all(limit=limit)
    # Go through the files and search using each query; place the results of each individual query in separate pickle files.
    folders = os.listdir(os.path.join("queries"))
    if rerun_search:
        for folder in folders:
            print(f"On folder {folder}")
            p = os.path.join("queries", folder, folder + ".txt")
            with open(p, "r") as fhand:
                lines = fhand.readlines()
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line == ERROR_STR or not line or line.strip()=="":
                        continue
                    res = search(line)
                    to_write = open(os.path.join("queries", folder, str(i) + ".pkl"), "wb")
                    pickle.dump(res, to_write)
    
    # Produce a ranking of results
    link_to_res = {}
    for folder in folders:
        files = os.listdir(os.path.join("queries", folder))
        bordas = {}
        for f in files:
            # for all the pickle files
            if '.pkl' not in f:
                continue
            with open(os.path.join('queries', folder, f), 'rb') as fhand:
                i = 0
                while True:
                    try:
                        pick = pickle.load(fhand)
                    except:
                        break
                    if not pick:
                        continue
                    for i, res in enumerate(pick):
                        if res['link'] in bordas:
                            bordas[res['link']] += len(pick) - i
                        else:
                            bordas[res['link']] = len(pick) - i
                            link_to_res[res['link']] = res
        
        # Produce re-ranked results
        sorted_bordas = sorted(bordas.items(), key=lambda item: item[1], reverse=True)
        final_results = [link_to_res[sorted_bordas[i][0]] for i in range(FINAL_RESULTS_N)]
        with open(os.path.join('queries', folder, 'aggregated.pkl'), 'wb') as fhand:
            pickle.dump(final_results, fhand)

    for folder in folders:
        query = ""
        with open(os.path.join("queries", folder, folder + '.txt')) as fhand:
            txt = fhand.readline().rstrip()
            query = txt

        aggregated_path = os.path.join("queries", folder, 'aggregated.pkl')
        orig_path = os.path.join("queries", folder, '0.pkl')
        with open(orig_path, 'rb') as fhand:
            try:
                pick = pickle.load(fhand)
            except:
                break
            if not pick:
                continue
            write_html(pick, os.path.join("queries", folder, 'orig.html'), query)

        with open(aggregated_path, 'rb') as fhand:
            try:
                pick = pickle.load(fhand)
            except:
                break
            if not pick:
                continue
            write_html(pick, os.path.join("queries", folder, 'aggregated.html'), query)


def make_test_html():
    # go through html files
    # add to query dict, which is of the form:
    # {'query': query, 'agg': agghtml, 'orig': orightml}
    # call gen_test(query dict)
    folders = os.listdir(os.path.join("queries"))
    queries = []
    for folder in folders:
        query = ""
        agg = ""
        orig = ""
        with open(os.path.join("queries", folder, folder + '.txt')) as fhand:
            txt = fhand.readline().rstrip()
            query = txt

        aggregated_path = os.path.join("queries", folder, 'aggregated.html')
        orig_path = os.path.join("queries", folder, 'orig.html')
        with open(orig_path, 'r') as fhand:
            orig = fhand.read()

        with open(aggregated_path, 'r') as fhand:
            agg = fhand.read()
        
        to_add = {'query': query, 'agg': agg, 'orig': orig}
        queries.append(to_add)

    gen_test(queries)


# produce(rerun_gpt=False, rerun_search=False)
produce(rerun_gpt=True, rerun_search=True, limit=3)
# produce()

make_test_html()
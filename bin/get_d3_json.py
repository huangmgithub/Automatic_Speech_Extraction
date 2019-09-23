import json
from collections import defaultdict
import os

BASE_DIR = '../data'
JSON_DIR = '../static'

def save_json():
    res = defaultdict(list)
    res["nodes"] = []
    res["links"] = []

    with open(os.path.join(BASE_DIR, 'result.txt'),  encoding='utf-8') as f, \
        open(os.path.join(JSON_DIR, 'news.json'), "w", encoding='utf-8') as f_j:
        res["nodes"].append({"id":"梦开始的地方", "group":1})
        for line in f:
            l = line.split(' ', 2) #分割成三部分
            # nodes
            if {"id":l[0], "group":2} not in res["nodes"]:
                res["nodes"].append({"id":l[0], "group":2})
            if {"id": l[1], "group":3} not in res["nodes"]:
                res["nodes"].append({"id":l[1], "group":3})
            if {"id": l[2], "group":4} not in res["nodes"]:
                res["nodes"].append({"id":l[2], "group":4})
            # links
            if {"source":"梦开始的地方", "target":l[0]} not in res["links"]:
                res["links"].append({"source":"梦开始的地方", "target":l[0]})
            if {"source":l[0], "target":l[1]} not in res["links"]:
                res["links"].append({"source":l[0], "target":l[1]})
            if {"source":l[1], "target":l[2]} not in res["links"]:
                res["links"].append({"source": l[1], "target": l[2]})


        json.dump(res, f_j, ensure_ascii=False)

if __name__ == "__main__":
    save_json()
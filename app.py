#!/usr/bin/env python3
import requests #pip3 install requests
import bs4 #pip3 install bs4
import json # builtins


def grab_source(username):
    
    r = requests.get("https://linktr.ee/"+username)
    return r.text

def parse_html(source):
    if source is None:
        return
    soup = bs4.BeautifulSoup(source, 'lxml')
    NEXT_DATA = soup.find('script', {'crossorigin':'anonymous', 'id':"__NEXT_DATA__"})
    dt = json.loads(NEXT_DATA.text)['props']
    dt = dt['pageProps']
    dt = dt['account']
    keys = [
                "username", 
                "description",
                "profilePictureUrl"
            ]
    info = dict(zip(keys,list(map(dt.get, keys))))
    links = dt['links']
    info['links'] = list(map(lambda x: {x.get("title").capitalize():x.get("url")},links))
    return info

if __name__ == "__main__":
    username = input("Enter the Username (Linktree Username): ")
    dt = grab_source(username)
    data = parse_html(dt)
    print(data)

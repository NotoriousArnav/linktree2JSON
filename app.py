#!/usr/bin/env python3
import requests #pip3 install requests
import bs4 #pip3 install bs4
import json # builtins

def grab_source(username, headers=None):
    if headers:
        r = requests.get("https://linktr.ee/"+username, headers=headers)
    else:
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
    import argparse
    parser = argparse.ArgumentParser(
            description="A Tool to Scrape Linktr.ee Profiles (Default Output Format: JSON)"
            )
    parser.add_argument(
                "--username",
                help="Username of the Linktr.ee Profile"
            )
    parser.add_argument(
                "--headersFile",
                help="Provide Headers.json file containing headers that you want to Specify",
                type=argparse.FileType('r')
            )
    parser.add_argument(
                "--outfile",
                help="Write to Desired Outfile.json (Default: stdout)",
                type=argparse.FileType("w")
            )
    args = parser.parse_args()
    if args.username is None:
        print("No username Given")
        exit()
    if args.headersFile:
        dt = grab_source(args.username, headers=json.load(args.headersFile))
    else:
        dt = grab_source(args.username)
    data = parse_html(dt)
    if args.outfile:
        json.dump(data, args.outfile)
        exit()
    print(json.dumps(data))

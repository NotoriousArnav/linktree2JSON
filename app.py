#!/usr/bin/env python3
import requests #pip3 install requests
import bs4 #pip3 install bs4
import json # builtins
import sys # For stderr

def grab_source(username, headers=None):
    url = f"https://linktr.ee/{username}"
    try:
        if headers:
            r = requests.get(url, headers=headers)
        else:
            r = requests.get(url)
        r.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(f"Oops: Something Else: {err}", file=sys.stderr)
        sys.exit(1)
    # This line should only be reached if no exceptions occurred
    return r.text

def parse_html(source):
    if source is None:
        print("Error: No source HTML provided to parse.", file=sys.stderr)
        sys.exit(1)

    soup = bs4.BeautifulSoup(source, 'lxml')
    next_data_script = soup.find('script', {'crossorigin':'anonymous', 'id':"__NEXT_DATA__"})

    if not next_data_script:
        print("Error: Could not find the __NEXT_DATA__ script tag in the HTML.", file=sys.stderr)
        print("This might indicate a change in Linktree page structure or a non-profile page.", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(next_data_script.text)
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from __NEXT_DATA__ script tag.", file=sys.stderr)
        sys.exit(1)

    try:
        account_data = data['props']['pageProps']['account']
    except KeyError:
        print("Error: Unexpected JSON structure in __NEXT_DATA__. Could not find 'props.pageProps.account'.", file=sys.stderr)
        sys.exit(1)

    keys = [
        "username",
        "description",
        "profilePictureUrl"
    ]
    info = {key: account_data.get(key) for key in keys}

    raw_links = account_data.get('links', [])
    if not isinstance(raw_links, list):
        print("Warning: 'links' data is not in the expected list format. Skipping links.", file=sys.stderr)
        info['links'] = []
    else:
        info['links'] = []
        for link in raw_links:
            if isinstance(link, dict) and link.get("title") and link.get("url"):
                info['links'].append({link.get("title").capitalize(): link.get("url")})
            else:
                print(f"Warning: Skipping malformed link item: {link}", file=sys.stderr)
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
        print("Error: No username given. Use --username <username>", file=sys.stderr)
        sys.exit(1) # Consistently exit with 1 on error

    headers = None
    if args.headersFile:
        try:
            headers = json.load(args.headersFile)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from headers file: {args.headersFile.name}", file=sys.stderr)
            sys.exit(1)
        finally:
            args.headersFile.close()

    html_source = grab_source(args.username, headers=headers)
    # grab_source now sys.exit(1) on error, so no need to check html_source for None

    data = parse_html(html_source)
    # parse_html now sys.exit(1) on error, so no need to check data for None

    if args.outfile:
        try:
            json.dump(data, args.outfile)
        except Exception as e: # Catch potential errors during file write
            print(f"Error writing JSON to outfile: {e}", file=sys.stderr)
            sys.exit(1) # main function will exit, no need for separate sys.exit here if main handles it
        finally:
            if args.outfile: # Ensure it's not None before closing
                args.outfile.close() # Ensure file is closed
    else:
        try:
            print(json.dumps(data))
        except Exception as e: # Catch potential errors during print (less likely for JSON)
            print(f"Error printing JSON to stdout: {e}", file=sys.stderr)
            sys.exit(1) # main function will exit

def main(argv=None):
    import argparse # Keep argparse import local to main if it's only used here
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

    # If argv is None, argparse uses sys.argv[1:] by default.
    # For testing, we can pass a list of strings.
    args = parser.parse_args(argv)

    if args.username is None:
        print("Error: No username given. Use --username <username>", file=sys.stderr)
        sys.exit(1)

    headers = None
    if args.headersFile:
        try:
            headers = json.load(args.headersFile)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from headers file: {args.headersFile.name}", file=sys.stderr)
            sys.exit(1)
        finally:
            if args.headersFile: # Ensure it's not None
                 args.headersFile.close()

    html_source = grab_source(args.username, headers=headers)
    data = parse_html(html_source)

    if args.outfile:
        try:
            json.dump(data, args.outfile)
        except Exception as e:
            print(f"Error writing JSON to outfile: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            if args.outfile:
                args.outfile.close()
    else:
        try:
            print(json.dumps(data))
        except Exception as e:
            print(f"Error printing JSON to stdout: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()

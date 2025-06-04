# linktree2JSON
A small Script that can Parse linktr.ee data into Usable JSON Format and can be also used as a Module for Other Projects.

## Installation
To Install this Script and its dependencies (including `lxml` for parsing):
```bash
git clone https://github.com/NotoriousArnav/linktree2JSON.git
cd linktree2JSON
pip3 install -r requirements.txt
```

## Usage
The Usage of this Script is Pretty Straight Forward.
```bash
python3 app.py --help # or ./app.py
usage: app.py [-h] [--username USERNAME] [--headersFile HEADERSFILE]
              [--outfile OUTFILE]

A Tool to Scrape Linktr.ee Profiles (Default Output Format: JSON)

options:
  -h, --help            show this help message and exit
  --username USERNAME   Username of the Linktr.ee Profile
  --headersFile HEADERSFILE
                        Provide Headers.json file containing headers that you
                        want to Specify
  --outfile OUTFILE     Write to Desired Outfile.json (Default: stdout)
```

### Options that can be Utilized:
1. --help
This is Pretty Self-Explanatory, that it prints the help info.
2. --username
This is Required, obviously, to Parse the profile page of a User
3. --headersFile
To advoid Bot Detection, you can use Custom Headers that are saved in headers.json or any JSON file.
For Example Refer the headers.json file Provided
4. --outfile
To Save the Output result to a File. If not then It will print to stdout in JSON format so that other programs can Utilize it.

#### Example Usage:
1. Without Saving the Output
```bash
python3 app.py --username riyagogoi
```
```json
{
	"username": "riyagogoi", 
	"description": null, 
	"profilePictureUrl": "https://d1fdloi71mui9q.cloudfront.net/iSM4QpzHTTyVp7uKOPsI_k8z7Mi5jEBQ278y3", 
	"links": [
		{
			"Youtube": "https://www.youtube.com/c/RIYAGOGOI"
		}, 
		{
			"Twitter": "https://twitter.com/_riyagogoi_"
		}, 
		{
			"Instagram": "https://www.instagram.com/_riyagogoi_/"
		}
	]
}
```
2. With Saving the Output
```bash
python3 app.py --username riyagogoi --outfile riyagogoi.json
```
This will save the JSON output to `riyagogoi.json` instead of printing it to the console.

3. Using a Custom Headers File
```bash
python3 app.py --username riyagogoi --headersFile headers.json # You can also add --outfile riyagogoi.json to save the output
```
If `--outfile` is not specified, the output will be printed to standard output:
```json
{
  "username": "riyagogoi",
  "description": null,
  "profilePictureUrl": "https://d1fdloi71mui9q.cloudfront.net/iSM4QpzHTTyVp7uKOPsI_k8z7Mi5jEBQ278y3",
  "links": [
    {
      "Youtube": "https://www.youtube.com/c/RIYAGOGOI"
    },
    {
      "Twitter": "https://twitter.com/_riyagogoi_"
    },
    {
      "Instagram": "https://www.instagram.com/_riyagogoi_/"
    }
  ]
}
```

## Using as a Module

You can also use `linktree2JSON` as a module in your own Python projects to fetch and parse Linktree profile data.
The primary functions you would use are `grab_source` and `parse_html` from `app.py`.

1.  **`grab_source(username, headers=None)`**:
    *   Fetches the HTML source code of the Linktree profile page.
    *   `username` (str): The Linktree username.
    *   `headers` (dict, optional): A dictionary of HTTP headers to use for the request.
    *   Returns the HTML source code as a string.
    *   Exits the script with an error message if the HTTP request fails (e.g., profile not found, network issues).

2.  **`parse_html(source)`**:
    *   Parses the HTML source code to extract profile information.
    *   `source` (str): The HTML source code obtained from `grab_source`.
    *   Returns a dictionary containing the profile information (username, description, profile picture URL, and links).
    *   Exits the script with an error message if parsing fails (e.g., `__NEXT_DATA__` not found, unexpected JSON structure).

### Example:

Here's how you can use these functions in your script:

```python
from app import grab_source, parse_html
import json # For pretty printing
import sys # For stderr

# Replace 'USERNAME' with the actual Linktree username
linktree_username = "riyagogoi"

# Optional: Define custom headers if needed
# my_headers = {
#     "User-Agent": "MyCoolBot/1.0",
#     "Accept-Language": "en-US,en;q=0.5"
# }
# html_source = grab_source(linktree_username, headers=my_headers)

# Fetch the HTML source (without custom headers in this example)
try:
    html_source = grab_source(linktree_username)

    # Parse the HTML
    # Note: grab_source and parse_html will call sys.exit() on error.
    # If you want to handle errors differently, you'll need to modify them
    # or wrap calls in a way that can catch SystemExit or convert them to exceptions.
    profile_data = parse_html(html_source)

    # Print some of the retrieved data
    print(f"Username: {profile_data.get('username')}")
    print(f"Description: {profile_data.get('description')}")
    print(f"Profile Picture URL: {profile_data.get('profilePictureUrl')}")

    print("\nLinks:")
    if profile_data.get('links'):
        for link_dict in profile_data['links']:
            for title, url in link_dict.items():
                print(f"- {title}: {url}")
    else:
        print("No links found.")

    # Or print the whole data structure
    # print("\nFull data:")
    # print(json.dumps(profile_data, indent=2))

except SystemExit as e:
    # The grab_source and parse_html functions call sys.exit() on error.
    # This block will catch such exits if they occur.
    print(f"Script exited with error code: {e.code}", file=sys.stderr)

```

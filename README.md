# linktree2JSON
A small Script that can Parse linktr.ee data into Usable JSON Format and can be also used as a Module for Other Projects.

## Installation
To Install this Script:
```bash
git clone https://github.com/NotoriousArnav/linktree2JSON.git
cd linktree2JSON
pip3 install -r requirements.txt
```

## Usage
The Usage of this Script is Pretty Straight Forward.
```bash
python3 app.py --help #or ./app.py
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
```bash
python3 app.py --username riyagogoi
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

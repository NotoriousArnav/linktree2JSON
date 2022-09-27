#linktree2JSON
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

# ratebeer_crawler

This project has the aim of crawling all the breweries, beers, reviews and users from the website 
[RateBeer](http://wwww.ratebeer.com). We do not guarantee that everything has been crawled. 
However, the majority of the website has been crawled. 

**TO UPDATE**

In the folder code, you will find a code called `run.py`. It is used to crawl everything. This file is
using two classes:
- `Crawler`: used to crawl the different HTML pages of this website
- `Parser`: used to parse the HTML files after they have been crawled

After running the code, you will get a folder called `data` with several subfolders:
- `misc` contains just a few miscalleneous files
- `places` contains the information about the places. Each place is represented by a folder with its name.
 Inside these folders, you will find the HTML pages with all the breweries from the given place.
- `breweries` contains all the HTML files of all the breweries. Inside these HTML files, the links
 to all the beers are written.
- `beers` contains all the pages of all the beers. Inside this folder, you will find all the folders
 from all the breweries. Inside the breweries folders, you will find the folders for all the beers 
 from this given brewery. Inside the beers folders, you will find the HTML pages with all the reviews.
- `parsed` **contains all the parsed data**. In particular, it contains the files: 
 *breweries.csv* and *beers.csv*. (MORE TO COME)

## Link to the scraped data

**TO BE UPDATED!!**

## Procedure

1. **Crawl** all the places (countries and regions)
2. **Parse** the breweries from these places and create a CSV file (*breweries.csv*)
3. **Crawl** all the breweries (pages with links to the beers)
4. **Parse** all the breweries to add the number of beers to the CSV file (*breweries.csv*) and to get the beers and 
create a CSV file (*beers.csv*)
5. **Crawl** all the beers and their reviews

## Dates and Time when the data were scraped

Everything has been crawled at the same time. It started the 21st of July at XX and it lasted for XX hours.

## Required packages

* `multiprocessing`
* `requests`
* `pandas`
* `numpy`
* `shutil`
* `html`
* `json`
* `re`

This code has been developed on Linux (Linux Mint 18.1). Therefore, we do not guarantee that it works on another OS.



# ratebeer_crawler

This project has the aim of crawling all the breweries, beers, reviews and users from the website 
[RateBeer](http://wwww.ratebeer.com). We do not guarantee that everything has been crawled. 
However, the majority of the website has been crawled. 

**TO UPDATE**

In the folder code, you will find a code called `run.py`. It is used to crawl everything. This file is
using two classes:
- `Crawler`: used to crawl the different HTML pages of this website
- `Parser`: used to parse the HTML files after they have been crawled

After running the code, you will get a folder called `data` with several sub-folders:
- `misc` contains just a few miscellaneous files
- `places` contains the information about the places. Each place is represented by a folder with its name.
 Inside these folders, you will find the HTML pages with all the breweries from the given place.
- `breweries` contains all the HTML files of all the breweries. Inside these HTML files, the links
 to all the beers are written.
- `beers` contains all the pages of all the beers. Inside this folder, you will find all the folders
 from all the breweries. Inside the breweries folders, you will find the folders for all the beers 
 from this given brewery. Inside the beers folders, you will find the HTML pages with all the reviews.
- `parsed` **contains all the parsed data**. In particular, it contains the files: 
 *breweries.csv*, *beers.csv*, *users.csv*, and *ratings.txt.gz*.
 
## Ratings

The collection of ratings are in the file *ratings.txt.gz* in the folder `parsed`. In the folder `code`, there is an 
example in python how to parse this file called [example_parser](./code/example_parser.py). The function parse (that you can reuse) is creating an iterator from the 
file. Then, you will go through each item (being a full rating). Each item can be treated as a dict or a JSON. Here is 
the list of key-value pairs with their type (that you have to change):

| Keys             | Type  | Description                           | **Warning**                                           |
| :--------------- | :---- | :------------------------------------ | :---------------------------------------------------- |
| **beer_name**    | str   | Name of the beer                      |                                                       |
| **beer_id**      | int   | ID of the beer                        |                                                       |
| **brewery_name** | str   | Name of the brewery                   |                                                       |
| **brewery_id**   | int   | ID of the brewery                     |                                                       |
| **style**        | str   | Style of the beer                     |                                                       |
| **abv**          | float | ABV (Alcohol By Volume) in percentage |                                                       |
| **user_name**    | str   | Name of the user                      |                                                       |
| **user_id**      | int   | ID of the user                        |                                                       |
| **appearance**   | int   | Rating for appearance                 | On a 5 points scale                                   |
| **aroma**        | int   | Rating for aroma                      | On a 10 points scale                                  |
| **palate**       | int   | Rating for palate                     | On a 5 points scale                                   |
| **taste**        | int   | Rating for taste                      | On a 10 points scale                                  |
| **overall**      | int   | Rating for overall                    | On a 20 points scale                                  |
| **rating**       | float | Final rating                          |                                                       |
| **text**         | str   | Text of the rating                    |                                                       |
| **date**         | int   | Date of the review in UNIX Epoch      | No access to time of the day. => Time is always noon. |

## Crawled data

Please contact directly [Robert West](mailto:robert.west@epfl.ch) and/or [Gael Lederrey](mailto:gael.lederrey@epfl.ch) to get the data. 

## Some Numbers

We give here the table with the different number of objects you can find in the parsed data, see folder `parsed`.

| Elements                  | Numbers   |
| :------------------------ | :-------- |
| Breweries                 | 24'189    |
| Beers                     | 460'116   |
| Beers (at least 1 rating) | 301'049   |
| Users                     | 70'174    |
| Ratings                   | 7'636'401 |

## Procedure

1. **Crawl** all the places (countries and regions)
2. **Parse** the breweries from these places and create a CSV file (*breweries.csv*)
3. **Crawl** all the breweries (pages with links to the beers)
4. **Parse** all the breweries to add the number of beers to the CSV file (*breweries.csv*) and to get the beers and 
create a CSV file (*beers.csv*)
5. **Crawl** all the beers and their reviews
6. **Parse** all the beers to add some information in the CSV file (*beers.csv*)
7. **Parse** all the beers to get all the reviews and save them in a gzip file (*ratings.txt.gz*)
8. Get (**Parse**) the users from the file (*ratings.txt.gz*) and save them in the CSV file (*users.csv*)
9. **Crawl** all the users 
10. **Parse** all the users to get some information and update the CSV (*users.csv*)

## Dates of crawling

The places, the breweries and the beers have been crawled between the 25th of July and the 1st of August 2017. 
The users have been crawled between the 2nd and the 3rd of August 2017.

## Required packages

* `requests`
* `pandas`
* `numpy`
* `shutil`
* `html`
* `json`
* `re`

This code has been developed on Linux (Linux Mint 18.1). Therefore, we do not guarantee that it works on another OS.



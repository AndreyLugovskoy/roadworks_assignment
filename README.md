# Before you start

Python version I used is 3.6.5, I did a test run for 
python 3.5, and didn't find any problems.

Please install the dependencies


In general this should be enough

```
pip3 isntall pandas
```

To plot the maps geopandas library needs to be installed.
I had small problem installing, depending on OS and python version.
Anyway, the pictures are already in the reopistory. In the end
I was able to install it on linux machine by just running.

```
pip3 isntall geopandas
pip3 install descartes
```

How to run
--

To see the report, please download report_page.html and report_page.files

python simple_analysis.py produces most of the text and tables
of the report page in separate files:

header.txt
longest_r.txt
busy.txt
busy.html
delay_message.txt
delay_table.html

I typested (not generated, used WYSIWYG editor) the final report_page.html
using this data, and changing text a little bit.

# roadworks_assignment
Repository with the assignment code and description

Data on roadworks from 2016-02-29 and 2016_03_07
--

Data are presented in two xml files. The xml trees have unified structure,
every entry contains 14 fields. The roads and local authorities names,
implies, that the data deals with the roadworks in UK.

The structure of the data with comments on meaning:

**reference_number** 1535041 -- Number of particular work in database.\
**road M1** --  Name of the road, only primary roads and motorways are presented.\
**local_authority** -- Derbyshire / Leicestershire / Nottinghamshire -- Authority, responsible for roadworks. Can be None.\
**location** Jct 24 to Jct 27 (100130) -- Part of the road, affected by the roadworks.\
**start_date** 2016-03-21T20:00:00 -- When the roadworks start.\
**end_date** 2016-03-31T06:00:00 -- When the roadworks end.\
**expected_delay** Slight (less than 10 mins) -- Estimated delay time.\
**description** Lane closures north and southbound 2000 - 0600 hrs for safety fence works. -- Relatively verbose roadworks description.\
**traffic_management** Lane Closure -- How the traffic is changed at work sight to ensure safety of workers and drivers\
**closure_type** Planned Works -- Indicates, if it is a planned or emergency work.\
**centre_easting** 448783 -- Easting of works center British National Grid coordinates (EPSG:27700).\
**centre_northing** 339811 -- Northing of works center in British National Grid coordinates (EPSG:27700).\
**status** Firm -- Indicates, if work is confirmed.\
**published_date** 2014-08-06T09:33:58

Data preparation
--

I first convert \*.xml files to pandas.DataFrame (DataFrame) to simplify basic operations
on data like sorting, cleaning, grouping and creating views. The processing is preformed
using the function ``read_roadworks_xml(filename)``.

Simple characterization
--

I start with simple analysis of the data and some cleanup. Here I answer certain simple
questions, which do not require any complex analysis or additional data.
I find the most important parameters to be connected with:
- Places, where works take place
- Time periods at which works take place 
- Delays related to works

Doing all that I generate the text containing the data, which will then enter my final
report for this assignment. I believe this data to be in general interesting. 

A clue, to where exactly works take place can be estimated from the ''local_authority''
data. Unique entries in this column correspond to various administrative divisions of UK
such as Counties, Cities and other. One can logically assume, that County administration
would be somewhat responsible for local roads.

To access the ''local_authorities'' data, certain cleanup needs to be done, since data is
stored either as a single string with a name or as '/' separated names the following way:
'Derbyshire / Leicestershire / Nottinghamshire', converting it to list will provide
additional flexibility in case of further processing. 

#### Unique roads and authorities 

Here I determine how many unique regions of the UK are affected by works, as well as how
many unique roads are being repaired.

#### The longest (shortest) roadwork

Here I determine the time limits of roadworks in question. Besides that I find the longest
(shortest) roadwork in the dataset. 

#### The longest road in UK

I have a hypothesis, that the road, that have the most number of Local Authorities
responsible for it is the longest one. To find this out, I will group my data by road 
names and calculate independent entities in 'local_authorities'.

### Improving analysis with open data

I added the data on area of the Counties, which gave a more resonable result.


### Easter bank holiday

Here I analyse, how loaded are English roads duet to roadworks during the Easter holidays.
I do this in two steps, answering the questions : what are the regions, with the most 
amount of works, and what are the regions with the highest total delay.

User view
--
The data is vast and it can be interesting for a broad audience of users, e.g. drivers. 
The date parameter can be changed in __main__ section of the function. What it outputs is

Plot view
--
It would be a pitty, if geographical data (Easting-Northing) in datafile would be wasted.
I created two maps, using this information and maps, avaliable from open sources, using 
python library "geopandas". Maps are, respectively for the whole time period, and Easter 
holidays. Geodata in '\*.shp' and accompanying formats are stored in directory with the same name. 

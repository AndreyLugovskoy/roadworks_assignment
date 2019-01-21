# Before you start

Please install the dependencies
### this should be enough

```
pip3 isntall pandas
```


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
- Place, where works take place
- Time period at which works take place 
- Delays related to works

A clue, to where exactly works take place can be estimated from the ''local_authority''
data. Unique entries in this column correspond to various administrative divisions of UK
such as Counties, Cities and other. One can logically assume, that County administration
would be somewhat responsible for local roads.

To access the ''local_authorities'' data certain cleanup need to be done, since data is
stored either as a single string with a name or as '/' separated names the following way:
'Derbyshire / Leicestershire / Nottinghamshire', converting it to list will provide
additional flexibility in case of further processing. 

#### The longest roadwork

Here I determine the time limits of roadworks in question. Besides that I find the longest
roadwork in the dataset. 

#### The longest road in UK

I have a hypothesis, that the road, that have the most number of Local Authorities
responsible for it is the longest one. To find this out, I will group my data by road 
names and calculate independent entities in 'local_authorities'.

### Improving analysis with open data


I noticed, that, (citites->Counties)

User view
--
The data is vast and it can be interesting for a broad audience of users, e.g. drivers. 
I created a simple function, `user_view(date_range)`, which should generate a report, 
based on user input, and which can be used in dynamical environment.

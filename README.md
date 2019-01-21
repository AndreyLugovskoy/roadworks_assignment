# roadworks_assignment
Repository with the assignment code and description

Data on roadworks from 2016-02-29 and 2016_03_07
--

Data are presented in two xml files. The xml trees have unified structure,
every entry contains 14 fields. The roads and local authorities names,
implies, that the data deals with the roadworks in UK.

The structure of the data with comments on meaning:

**reference_number** 1535041 -- Number of particular work in database.

**road M1** --  Name of the road, only primary roads and motorways are presented.

**local_authority** -- Derbyshire / Leicestershire / Nottinghamshire -- Authority, responsible for roadworks. Can be None.

**location** Jct 24 to Jct 27 (100130) -- Part of the road, affected by the roadworks.

**start_date** 2016-03-21T20:00:00 -- When the roadworks start.

**end_date** 2016-03-31T06:00:00 -- When the roadworks end.

**expected_delay** Slight (less than 10 mins) -- Estimated delay time.

**description** Lane closures north and southbound 2000 - 0600 hrs for safety fence works. -- Relatively verbose roadworks description

**traffic_management** Lane Closure -- How the traffic is changed at work sight to ensure safety of workers and drivers

**closure_type** Planned Works -- Indicates, if it is a planned or emergency work.

**centre_easting** 448783 -- Easting of works center British National Grid coordinates (EPSG:27700). 

**centre_northing** 339811 -- Northing of works center in British National Grid coordinates (EPSG:27700).

**status** Firm -- Indicates, if work is confirmed.

**published_date** 2014-08-06T09:33:58

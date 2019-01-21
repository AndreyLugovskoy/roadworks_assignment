#!/usr/bin/python3

"""
NB
This module contains the __main__, where the actual analysis is preformed.
The rest of the module contains functions for data processing and cleaning.
"""



import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime


def read_roadworks_xml(filename):
    """Read and process roadworks xml file.

    Args:
        filename: string with path to .xml file

    Returns:
        pandas.DataFrame
    """

    rawXML = ET.parse(filename)
    rawROOT = rawXML.getroot()
    xmlList = []

    # get header from first entry
    header = [entry.tag for entry in rawROOT[0]]

    '''Header columns:
    'reference_number', 'road', 'local_authority',
    'location', 'start_date', 'end_date',
    'expected_delay', 'description', 'traffic_management',
    'closure_type', 'centre_easting', 'centre_northing',
    'status', 'published_date'
    '''

    

    # this xml has no attributes, just tags with values.
    # xml was an overkill for this purpose, they should
    # have stored in csv, would have saved space:)
    for child in rawROOT:
        # couple of lists to absorb the data and check for
        # unique values.
        lineList = []
        headerList = [entry.tag for entry in child]

        # if some entry have unique tags, notify me
        if headerList != header:
            print('Unique tags')

            # print the 'reference_number' and unique tags
            print('reference_number: ', child.find('reference_number').text)
            print(headerList)
            print(set(header) - set(headerList))

        for sub in child:
            lineList.append(sub.text)
        xmlList.append(lineList)

    roadWorks = pd.DataFrame(xmlList, columns=header)\
                    .set_index('reference_number')
    return roadWorks




def process_roadworks_data(data):
    """Reformat and clean roadworks DataDrame.

    Args:
        data: DataFrame containing xml information

    Returns:
        nothing
    """
    data[['start_date', 'end_date']] = data[['start_date', 'end_date']]\
                                          .astype('datetime64')

    # convert / separated strings into list
    data['local_authority'] = data['local_authority']\
                            .astype(str)\
                            .apply(lambda x: x.replace(' / ', '/').split('/'))
    
    # minimal string cleanup, more can be done
    data[['location', 'closure_type']] = \
    data[['location', 'closure_type']].apply(lambda x : x.str.strip())


if __name__ == "__main__":
    print("Executing as main program")
    print("Value of __name__ is: ", __name__)

    d0209 = read_roadworks_xml('./he_roadworks_2016_02_29.xml')
    d0307 = read_roadworks_xml('./he_roadworks_2016_03_07.xml')

    # While d0307 is structurally the same to d0209, the two have
    # overlapping rows.
    roadWorks = pd.concat([d0209, d0307], join='outer', axis=0)\
                  .drop_duplicates()

    process_roadworks_data(roadWorks)    

    # can be outputted as
    #print(roadWorks[0:10].to_string())
    
    # The longest roadwork:
    # here I estimate the time limits of all works and find out what is the longest
    # roadwork by estimating timedelta.

    # obvious
    start_max = roadWorks.loc[roadWorks['start_date'].idxmax()]['start_date']

    # too early
    start_min = roadWorks.loc[roadWorks['start_date'].idxmin()]['start_date']

    # 
    end_max = roadWorks.loc[roadWorks['end_date'].idxmax()]['end_date']

    # obvious
    end_min = roadWorks.loc[roadWorks['end_date'].idxmin()]['end_date']
   
    print('Datafiles contain information about roadworks, that happened in UK in the '\
          +'period between ' + str(start_min.date()) + ' and ' + str(end_max.date()) + '.') 

    # The busiest day of 2016    

    # The longest road in UK 
    
    

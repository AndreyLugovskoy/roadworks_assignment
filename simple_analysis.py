#!/usr/bin/python3

"""
NB
This module contains the __main__, where the actual analysis is preformed.
The rest of the module contains functions for data processing and cleaning.
"""


import textwrap 
import pandas as pd
import numpy as np
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
    # I use array, because it would be easier to flatten next
    data['local_authority'] = data['local_authority']\
                            .astype(str)\
                            .apply(lambda x: np.array(x.replace(' / ', '/').split('/')))
    
    # minimal string cleanup, more can be done
    data[['location', 'closure_type']] = \
    data[['location', 'closure_type']].apply(lambda x : x.str.strip())

def long_short_string(data, dt, length = 'longest'):
    out = "The " + length + " road work lasts between "\
      + str(data['start_date'].date())\
      + " and " + str(data['end_date'].date()) \
      + " and takes " + str(dt) + ' h:m:s.'
    return out

if __name__ == "__main__":
    print("Simple analysis results")
    #print("Value of __name__ is: ", __name__)

    d0209 = read_roadworks_xml('./he_roadworks_2016_02_29.xml')
    d0307 = read_roadworks_xml('./he_roadworks_2016_03_07.xml')

    # While d0307 is structurally the same to d0209, the two have
    # overlapping rows.
    roadWorks = pd.concat([d0209, d0307], join='outer', axis=0)\
                  .drop_duplicates()

    process_roadworks_data(roadWorks)    

    # can be outputted as
    #print(roadWorks[0:10].to_string())
    
    ''' Unique places and roads'''
 
    # cleanup 
    # this values are negligable for overall statistics
    roadWorks = roadWorks[roadWorks['local_authority']!='None']
    roadWorks = roadWorks[roadWorks['local_authority']!='Not Specified'] 

    # flatten the local_authorities and find unique entries
    authList = roadWorks['local_authority'].values

    # values do not flatten well due to type inconsistency
    authSet = set( item for sublist in authList for item in sublist)

    # now the same for roads, but much faster.
    roadsList = roadWorks['road'].unique()

    ''' 
    The longest roadwork:
    here I estimate the time limits of all works and find out what is the longest
    roadwork by estimating timedelta.
    '''

    # obvious
    start_max = roadWorks.loc[roadWorks['start_date'].idxmax()]['start_date']
    # too early
    start_min = roadWorks.loc[roadWorks['start_date'].idxmin()]['start_date']
    # 
    end_max = roadWorks.loc[roadWorks['end_date'].idxmax()]['end_date']
    # obvious
    end_min = roadWorks.loc[roadWorks['end_date'].idxmin()]['end_date']

    # longest and shortest works are obvious 
    lWork = (roadWorks['end_date'] - roadWorks['start_date']).max()
    sWork = (roadWorks['end_date'] - roadWorks['start_date']).min()

    # corresponding entries in DataFrame     
    lWorkEntry = roadWorks.loc[(roadWorks['end_date']
                 - roadWorks['start_date']).idxmax()]

    sWorkEntry = roadWorks.loc[(roadWorks['end_date']
                 - roadWorks['start_date']).idxmin()]
    
    out = 'Datafiles contain information about roadworks, that happened in ' \
          + str(len(authSet)) +' regions in Great Britain in the '\
          +'period between ' + str(start_min.date()) + ' and ' + str(end_max.date())+'.'
    out += 'Roadworks were performed on ' + str(len(roadsList)) + ' roads.'

    # some beautification I can use latter.
    wrapper = textwrap.TextWrapper(initial_indent = "  ", width = 70, replace_whitespace = True)

    out += long_short_string(lWorkEntry, lWork,)\
           + long_short_string(sWorkEntry, sWork, length='shortest')

    print(wrapper.fill(out))

    # A small plot, which gives a clue about the distirbution of dates.
    axs[0].set_ylim([ 0, len(roadWorks)])
    axs[0].set_xlim([ start_min, end_max])
    axs[0].plot(roadWorks['start_date'],y, marker='o',linestyle='None', alpha = 0.35, markersize = 5, label='Work start')
    axs[0].plot(roadWorks['end_date'],y, marker='o',linestyle='None', alpha = 0.5, markersize = 5,   label='Work end')  
    axs[0].axvspan(('2016-01-01'), ('2016-12-31'), color='y', alpha=0.3, lw=0)
    axs[0].legend(loc='upper left')
    
    axs[1].set_xlim([pd.Timestamp('2016-01-01'), pd.Timestamp('2016-12-31')])
    axs[1].axvspan(pd.Timestamp('2016-01-01'), pd.Timestamp('2016-12-31'), color='y', alpha=0.3, lw=0)
    axs[1].axvspan(pd.Timestamp('2016-03-22'), pd.Timestamp('2016-05-1'), color='tab:green', alpha=0.2, lw=0)
    axs[1].plot(roadWorks['start_date'],y, marker='o',linestyle='None', alpha = 0.35, markersize = 5)
    axs[1].plot(roadWorks['end_date'],y, marker='o',linestyle='None', alpha = 0.5, markersize = 5)
    axs[1].set_ylabel('Roadworks', fontsize=14)
    axs[1].set_xlabel('Date', fontsize=14)
    axs[1].yaxis.set_label_coords(-0.09, 1.2)
    fig.show()
    fig.savefig('date_distr.png', bbox_inches='tight',dpi = 150)

    ''' The maximum ammount of start and end dates is distributed around the 
    "publication" date of the datasets, which is not suprising.
    This limits the "pridictive" power of the analysis. I will continue with the
    "predictions" within the time period of a month, starting from 2016-03-22, the
    date of the newset file'''

    ''' The busiest day'''

    # From now on I perform analysis between 2016-03-22 to 2016-05-1,
    # this includes such dates as Easter holidays of 2016 and school,
    # holidays and may be interesting for the drivers.
    

    ''' The region of UK with the busiest road in March-May 2016'''
    
    date_min = start_max
    date_max = datetime.strptime('Dec 31 2016  11:59PM', '%b %d %Y %I:%M%p')

    # limiting
    busyView = roadWorks[ ((roadWorks['start_date']<=date_min) & (roadWorks['end_date']>=date_min))
                    | ((roadWorks['start_date']>=date_min) & (roadWorks['end_date']<=date_max))
                    | ((roadWorks['start_date']>=date_min) & (roadWorks['start_date']<=date_max))
                    ]

    conversion_list = []

    city_header = ['local_authority', 'reference_number', 
          'start_date', 'end_date', 'expected_delay',
          'centre_easting', 'centre_northing']

    # TODO refactor into function
    for i,d in busyView.reset_index()[city_header].drop(columns=['local_authority']).iterrows():
         for c in authList[i]:        
             conversion_list.append([c]+d.tolist())

    laWorks = pd.DataFrame(conversion_list, columns=city_header)
    
    laWorks = laWorks.set_index(['local_authority'])

    # a nice Series with the number of works per period
    worksCount = laWorks.index.value_counts() 
    
    maxRegion = works_count.idxmax()
    max_works = works_count.max()

    works_count = works_count.reset_index().rename(
            columns={'local_authority':'Of works', 'index' : 'Region'})\
                         .set_index('Of works')
     
    ten_most_loaded = works_count\
                .groupby(works_count.index)\
                .agg(lambda x: ', '.join(str(i) for i in x)).iloc[::-1]\
                .reset_index().set_index('Region')

    out_busy = wrapper.fill(
            'According to our data there are {0} works in 2016 in {1} regions of UK.'.format(len(busyView), len(uniqueRegions)-1))
    out_busy += wrapper.fill('Most of the works ({0}) will take place on the roads of the County of {1}.\n'.format(max_works,max_region))
    out_busy += wrapper.fill('Ten most busy administrative regions of UK in 2016 are given in the table below.')
    print(out_busy)
    print(HTML((ten_most_loaded[0:10]).to_html()))

    ''' The longest road in UK '''

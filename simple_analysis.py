#!usr/bin/python3

"""
NB
This module contains the __main__, where the actual analysis is preformed.
The rest of the module contains functions for data processing and cleaning.
"""


import textwrap 
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import os.path as path

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

def split_local_authority(data, header = None):
    """Function to get DataFrame, splited by local authority entries.
    
    Keyword args:
        header: if header is given, it MUST contain the index name, among others
    Args:
        data: DataFrame containing xml information

    Returns:
        process dataframe
    """
    conversion_list = []                                                           

    aList = data['local_authority'].values

    conversion_list = []

    if header == None:
        header = data.reset_index().columns.tolist()

    rh = header
    rh.remove('local_authority')

    # TODO refactor into function
    for i,d in data.reset_index()[rh].iterrows():
         for c in aList[i]:
             conversion_list.append([c]+d.tolist())

    splited = pd.DataFrame(conversion_list, columns=['local_authority']+rh)\
              .set_index(data.index.names)
    return splited

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
 
    # flatten the local_authorities and find unique entries
    authList = roadWorks['local_authority'].values

    # values do not flatten well due to type inconsistency
    authSet = set( item for sublist in authList for item in sublist)

    # now the same for roads, but much faster.
    roadsList = roadWorks['road'].unique()

    # fast cleanup
    authSet.remove('None')
    authSet.remove('Not Specified')


    ''' 
    The longest roadwork:
    here I estimate the time limits of all works and find out what is the longest
    roadwork by estimating timedelta.
    '''

    # nothing starts after that
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
    out += ' Roadworks were performed on ' + str(len(roadsList)) + ' roads.'

    # some beautification I can use latter.
    wrapper = textwrap.TextWrapper(initial_indent = "  ", width = 70, replace_whitespace = True)

    out += long_short_string(lWorkEntry, lWork,)\
           + long_short_string(sWorkEntry, sWork, length='shortest')

    print(wrapper.fill(out),file=open('header.txt','w'))

    ''' The longest road in UK '''
    ''' Here I try to roughly estimate, which road in UK is the longest one.
        I first estimate the work, for which the most number of authorities
        are responsible. After that I update the estimate with the external
        data on municipal regions area. While the answer is correct, this 
        method is highly inaccurate, since the statistics is very limited. 
    ''' 
    roadsView = split_local_authority(roadWorks, header = ['reference_number',
    'local_authority','road'])

    results_auth_number = roadsView.drop_duplicates().groupby('road')\
    .count().sort_values(by=['local_authority'],ascending=False)

    # This data doesn't give us the correct answer, but gives
    # us a clue abot the longest road in UK - A1. The "prediction"
    # can be imporved using the number of junctions or the area
    # of the crossed regions.

    # I downloaded some open data on area and population of large
    # administative areas of UK and stored it as csv, now I will
    # merge the datasets and try to estimate the length.

   
    area_pop = pd.read_csv('./Counties_area_pop.csv',header=0)
    roads_area = pd.merge(roadsView, area_pop[['Name','Area km2']],
              left_on = 'local_authority',   right_on='Name')

    roads_area = roads_area.drop(columns = ['Name'])

    roads_area['Area km2'] = roads_area['Area km2']\
                              .apply(lambda x: x**0.5)

    roads_area = roads_area.rename(columns = {'Area km2' : 'Approx Length, km'})

    results_area = roads_area.drop_duplicates().groupby('road').sum().sort_values(by='Approx Length, km',
    ascending=False)

    print(results_area[0:3],'\n',results_auth_number[0:3],'\n')
    quit()
    """
         I do obtain the right value for the A1, 
         but the inaccuracy of this method is obviously too big.
         All other roads are ordered wrongly and the length values are ~40-50
         percent wrong.
    """

    roads_area.drop_duplicates().groupby('road').sum().sort_values(by='Approx Length, km',
    ascending=False)

    
    

    # A plot, which gives a clue about the distribution of dates.
    if path.isfile('./date_distr.png') == False:
        import matplotlib.pyplot as plt

        # A range for works axis
        y = range(len(roadWorks))

        (fig, axs) = plt.subplots(2, 1, figsize=(10, 7),  sharey=True)

        axs[0].set_ylim([ 0, len(roadWorks)])

        axs[0].set_xlim([ start_min, end_max])

        axs[0].plot(roadWorks['start_date'], y, marker='o',linestyle='None',
        alpha = 0.35, markersize = 5, label='Work start')
        
        axs[0].plot(roadWorks['end_date'], y, marker='o',linestyle='None', 
        alpha = 0.5, markersize = 5,   label='Work end')  

        axs[0].axvspan(('2016-01-01'), ('2016-12-31'), color='y', alpha=0.3, lw=0)

        axs[0].legend(loc='upper left')
        
        axs[1].set_xlim([pd.Timestamp('2016-01-01'), pd.Timestamp('2016-12-31')])

        axs[1].axvspan(pd.Timestamp('2016-01-01'), pd.Timestamp('2016-12-31'),
        color='y', alpha=0.3, lw=0)
        
        axs[1].axvspan(pd.Timestamp('2016-03-22'), pd.Timestamp('2016-05-1'), 
        color='g', alpha=0.2, lw=0)

        axs[1].plot(roadWorks['start_date'], y, marker='o', linestyle='None',
        alpha = 0.35, markersize = 5)

        axs[1].plot(roadWorks['end_date'], y, marker='o', linestyle='None',
        alpha = 0.5, markersize = 5)

        axs[1].set_ylabel('Roadworks', fontsize=14)
        axs[1].set_xlabel('Date', fontsize=14)
        axs[1].yaxis.set_label_coords(-0.09, 1.2)
        
        # Save fig for latter
        #fig.show()
        fig.savefig('date_distr.png', bbox_inches='tight', dpi = 150)

    '''
    The plot shows, that data is very unhomogeneous. 
    Now I will do "predictions" within the time period of Easter holidays in 
    (2016-03-25, 2016-03-28). This period is close enough to data file dates,
    at the same time "prediction" for this period will have some use.'''

    ''' The busiest day'''

    # From now on I perform analysis between 2016-03-25 to 2016-03-28,
    # this includes such dates as Easter holidays of 2016 and school,
    # holidays and may be interesting for the drivers.
   
   

    ''' The region of UK with the busiest roads (due to works) during 
        Easter bank-holiday 2016'''

    #print('#Some data processing\n')   
 
    date_min = datetime.strptime('Mar 25 2016  11:59PM', '%b %d %Y %I:%M%p')
    date_max = datetime.strptime('Mar 28 2016  11:59PM', '%b %d %Y %I:%M%p')

    # limiting
    busyView = roadWorks[ ((roadWorks['start_date']<=date_min) & (roadWorks['end_date']>=date_min)) ]

    conversion_list = []

    city_header = ['local_authority', 'reference_number', 
          'start_date', 'end_date', 'expected_delay',
          'centre_easting', 'centre_northing']

    busyAList = busyView['local_authority'].values

    # TODO refactor into function
    for i,d in busyView.reset_index()[city_header].drop(columns=['local_authority']).iterrows():
         for c in busyAList[i]:
             conversion_list.append([c]+d.tolist())

    
    laWorks = pd.DataFrame(conversion_list, columns=city_header)

    # cleanup 

    laWorks = laWorks[laWorks['local_authority'] != 'None']
    laWorks = laWorks[laWorks['local_authority'] != 'Not specified']   

    uniqueBusyRegions = list(set(laWorks['local_authority']))  
    laWorks = laWorks.set_index(['local_authority'])

    

    # a nice Series with the number of works per period
    worksCount = laWorks.index.value_counts() 
    
    maxRegion = worksCount.idxmax()
    maxWorks = worksCount.max()

    worksCount = worksCount.reset_index().rename(
            columns={'local_authority':'Of works', 'index' : 'Region'})\
                         .set_index('Of works')
     
    ten_most_loaded = worksCount\
                .groupby(worksCount.index)\
                .agg(lambda x: ', '.join(str(i) for i in x)).iloc[::-1]\
                .reset_index().set_index('Region')

    out_busy = wrapper.fill('According to our data there are {0} works between {1}'\
                            ' and {2} in {3} regions of UK.'.format(
                            date_min.date(),date_max.date(),
                            len(busyView), len(uniqueBusyRegions))
                                                                    )

    out_busy += wrapper.fill('Most of the works ({0}) will take place on the roads'\
                             ' of the County of {1}.\n'.format(maxWorks,maxRegion))

    out_busy += wrapper.fill('Ten regions in the UK with the most busy roadworks '\
                             'schedule during Easter holidays in 2016.')

    print('out_busy', file=open('./busy.text', 'a'))
    #print((ten_most_loaded[0:10]).to_html())
    print(ten_most_loaded[0:10].to_html(), file = open('./busy.html','w'))

    '''Average delay due to works in the same period'''
    
    # Now I want to estimate an average delay in regions.

    # First I will drop No Delay values
    laWorks[laWorks['expected_delay'] == 'No Delay']


    # I replace them with the values based on delay range, provided.
    # The delay values can be improved with better statistics.
    # I astimated 'Severe delay' time as a median value
    # between 30 min and 120 min (two hours) delay.
    delay = {
        'Slight (less than 10 mins)' : 5,
        'Moderate (10 - 30 mins)' : 20,
        'Severe (more than 30 mins)' : 75
            }

    laDelay = laWorks['expected_delay'].map(delay)
    laDelay = laDelay.dropna()
    delayTable = laDelay.groupby(laDelay.index)\
                        .agg(np.sum)\
                        .sort_values(ascending = False)\
                        .to_frame()

    delayTable['expected_delay'] = delayTable['expected_delay'].astype(int)
 
    delay_out = wrapper.fill('Total delay during the same period in various regions.'\
                            ' Only values with delay above two hours are given.')

    delayTable=delayTable.reset_index().set_index('expected_delay')

    delayTable = delayTable.groupby(['expected_delay'])\
                     .agg(lambda x: ', '.join(str(i) for i in x))\
                     .reset_index()
                     
    delayTable.rename(columns={\
                     'expected_delay' : 'Total delay in minutes',\
                     'local_authority' : 'Region'}, inplace=True)\
      
    # 

    delayTable=delayTable.set_index('Region')\
                .sort_values(by=['Total delay in minutes'],ascending=False)

    print(delay_out, file = open('./delay_message.txt','w'))
    print(delayTable[delayTable['Total delay in minutes']>120].to_html(), file =
open('./delay_table.html', 'w')) 

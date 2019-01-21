#!/usr/bin/python3

import pandas as pd
from datetime import datetime


def firm_provisonal(status):
    """Utility function to process roadworks status.
    """
    if status == 'Provisional':
        return 'expected'
    else:
        return 'confirmed'


def expected_delay(delay):
    """Utility function to add proper wording to delay data.
    """
    return delay + ' delay'


def user_view(data, date = '2016-03-02 22:00:00', place = None ):
       '''Print human readable data on road delays for travelers.

           Args:
               date: the date of interest to estimate delays

           Returns:
               nothing yet
       '''
       user_columns = ['road', 'location', 'expected_delay',
                       'description', 'traffic_management',
                       'closure_type', 'status']

       #if type=tuple define limits
       #if single date, do something else

       htlm_data = ''

       # create a user view, with only human readable information

       # first I limit the selection to works
       userView = roadWorks[
                  (roadWorks['start_date'] <= date) &
                  (roadWorks['end_date'] >= date)
                  ][user_columns]\
                  .sort_values(by=['expected_delay'], ascending = False)

       # Some situation string do not have points in the end., some have ' .' situation.
       engl=lambda x: ('is', '') if x == 1 else ('are', 's')

       v, s = engl(len(userView))
       print('There {v} {l} roadwork situation{s} on {d}.\n'.format(v=v, s=s,
                                                                 l=len(userView), d=date))

       output = '' 
       for i, entry in userView.iterrows():

           
           

           # No delay case has a "delay" in description. 
           if entry['expected_delay'] == 'No Delay':
               output += 'Please be careful on ' + entry['road']\
                                                 + ', '\
                                                 + entry['location']\
                                                 + '.\n'

           else:
               output += '{d} is {s} on {r}, {l}.\n'.format(
                                        d=expected_delay(entry['expected_delay']),
                                        s=firm_provisonal(entry['status']),
                                        r=entry['road'], l = entry['location']
                                        )

           output += 'Situation: ' + entry['description'].strip()\
                                   + '\n'\
                                   + 'Reason: '\
                                   + entry['closure_type'] + '.\n\n'\
                                                                                   
       print(output)
                        
                        
                        
                        


if __name__ == "__main__":
    print("Executing as main program")
    print("Value of __name__ is: ", __name__)

    from simple_analysis import read_roadworks_xml, process_roadworks_data 
    
    d0209 = read_roadworks_xml('./he_roadworks_2016_02_29.xml')
    d0307 = read_roadworks_xml('./he_roadworks_2016_03_07.xml')
    
    roadWorks = pd.concat([d0209, d0307], join='outer', axis=0)\
                  .drop_duplicates()

    process_roadworks_data(roadWorks)

    date=('2016-09-21 20:14:00')
    user_view(roadWorks)


import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
from pyproj import Proj, transform
from shapely.geometry import Point, Polygon
from datetime import datetime
from simple_analysis import read_roadworks_xml, process_roadworks_data

def plot_map(data, name, title = 'None'):
    # TODO: add comment here
    # Plots nice plots for final report
  
    
    
    roadsMap2=gp.read_file('./geodata/slim_roads.shp')
    cont=gp.read_file('./geodata/ne_10m_admin_0_countries.shp')
    #cities=pd.read_csv('./GB.csv')
    cities=gp.read_file('./geodata/Major_Towns_and_Cities_December_2015_Boundaries.geojson')


    fig,ax = plt.subplots(figsize = (15,15))

    data_copy=data.copy()

    data_copy[['centre_easting', 'centre_northing']] = data_copy[['centre_easting', 'centre_northing']].astype(float)

    ax.set_xlim([-6,2])
    ax.set_ylim([50,56])

    inProj = Proj(init='epsg:27700')  # projected
    outProj = Proj(init='epsg:4326') # lat/long

    e_n = list(zip(data_copy.centre_easting, data_copy.centre_northing))
    e_n = [ transform(inProj,outProj,x,y) for x,y in e_n ]

    gs = gp.GeoSeries([Point(pnt[0],pnt[1]) for pnt in e_n])
   
    ax.axis('off')    

    if title == None:
        start_max = data_copy.loc[data_copy['start_date'].idxmax()]['start_date']
        ax.set_title('Active road roadworks in UK by '+str('22 Mar 2016'))
    ax.set_title(title)

    cont.plot(ax=ax, alpha=0.3, color = 'g')
    roadsMap2.plot(ax = ax, alpha=1.0, color='grey', label = 'Primary roads')
    gs.plot(ax=ax, marker='o', color='blue', markersize=20, label = 'Active road works')
    
    cities['geometry'].plot(ax=ax, alpha=0.7, color = 'c', label = 'Populated areas')
    
    import seaborn as sns
    sns.set_palette(sns.color_palette("hls", 20))
    
    # Adding large cities points
    plot_data = zip(cities.geometry.centroid.x, cities.geometry.centroid.y,
        cities.tcity15nm, cities.st_areashape)
    for i, p  in enumerate(plot_data):
        x, y, n, s = p
        if s > 6.00e+07:
            ax.plot(x,y, markersize = 20, marker='*', color='r') 
            if i%2: 
                ha='left'
                va='bottom'
            else:
                ha='right'
                va='top'
            # I was running out of time...
            # I did my best to avoid it
            if n == 'Coventry':
                va='top'
            if n == 'Kingston upon Hull':
                ha='left'
            if n == 'Stroke-on-Trent':
                ha='left'
                va='top'
            if n == 'Notingham':
                ha='left'
                va='bottom'
            ax.annotate(n, xy=(x,y), xytext=(3, 3), horizontalalignment=ha,
                        verticalalignment=va, textcoords="offset points", fontsize = 18)
            
    
    
    ax.legend(loc='upper right')    
    cities
    
    fig.savefig(name+'.png', bbox_inches='tight',dpi = 300)

if __name__ == "__main__":
    print("Plot two maps: one for all data.")
    print("And one for easter holidays.")
 
    d0209 = read_roadworks_xml('./he_roadworks_2016_02_29.xml')
    d0307 = read_roadworks_xml('./he_roadworks_2016_03_07.xml')
    
    roadWorks = pd.concat([d0209, d0307], join='outer', axis=0)\
                  .drop_duplicates()

    process_roadworks_data(roadWorks)

    date_min = datetime.strptime('Mar 25 2016  11:59PM', '%b %d %Y %I:%M%p')
    date_max = datetime.strptime('Mar 28 2016  11:59PM', '%b %d %Y %I:%M%p')

    busyView = roadWorks[ ((roadWorks['start_date']<=date_min) & (roadWorks['end_date']>=date_min)) ]

    plot_map(roadWorks,'general', title='Roadworks in England by Mar 22 2016')
    plot_map(busyView, 'easter', title='Roadworks during Easter holidays 2016.')

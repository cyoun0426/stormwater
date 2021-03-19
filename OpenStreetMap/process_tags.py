import pandas as pd
from pyproj import Proj, transform
from tqdm import tqdm


education_tag_list = ['college','school','university','dormitory']
residential_tag_list = ['apartments','bungalow','residential','house']
commercial_tag_list = ['hotel','commercial','industrial','office','retail','warehouse','service','construction']
agriculture_tag_list = ['farm','barn','cowshed','farm_auxiliary','greenhouse','slurry_tank','stable','sty','digester']
road_tag_list = ['motorway','trunk','primary','secondary','tertiary','residential','unclassified','motorway_link','trunk_link','primary_link','secondary_link',
                'tertiary_link','living_street','service','pedestrian','track','construction']
smoothness_tag_list = ['excellent','good','intermediate','bad','very_bad','horrible']
road_surface_tag_list = ['paved','unpaved','asphalt','concrete','paving_stones','sett','cobblestone','metal','wood','compacted','fine_gravel','gravel','pebblestone',
'plastic','grass_paved','grass','dirt','earth','mud','sand','ground']
#Basin = An area artificially graded to hold water.Together with basin=* for stormwater/rainwater infiltration/detention/retention basins.
landuse_tag_list = ['commercial','construction','industrial','residential','retail','allotments','farmland','farmyard','basin','landfill','quarry','reservoir']
# works = A factory or industrial production plant
# water_works = A place where drinking water is found and applied to the local waterpipes network.
manmade_tag_list = ['wastewater_plant','water_works','works']
# wetland = A natural area subject to inundation or with waterlogged ground
water_related_tag_list = ['wetland']

def amenity_score():
    
    masterlist = education_tag_list + residential_tag_list + commercial_tag_list + agriculture_tag_list + road_surface_tag_list + landuse_tag_list + manmade_tag_list + water_related_tag_list
    masterlist = list(set(masterlist))
    score = [10] * len(masterlist)
    
    out = pd.DataFrame({'amenity': masterlist, 'score': score})
    out.to_csv('amenity_score.csv',index=False)


# Visual mapping of OSM and SWMM input file
# Using Subcatchment c008
#           X               Y
# OSM   -117.8951        33.5993
# SWMM  6061091.827    2165508.734
# OSM-> SWMM   X* -51410.88838297775  Y*64451.00743170245 

def swmm_coord_extract():    
    with open('../Newport_Baseline_WithLID_20190418.inp','r') as openfile:
        lines = [line.rstrip() for line in openfile]

    coordinate_line = 0
    vertices_lines = 0
    for n, l in enumerate(lines):
        if l == '[COORDINATES]':
            coordinate_line = n
        if l == '[VERTICES]':
            vertices_lines = n

    lines = lines[coordinate_line:vertices_lines]
    lines = lines[3:-1]

    out_proj = Proj(init='epsg:4326') #OSM WGS84 coordinate system
    in_proj = Proj(init='epsg:2230') # SWMM inp file NAD83 coordinate system
    coordinate_df = pd.DataFrame(columns = ['node','x','y'])
    for line in tqdm(lines):
        line = line.replace('\t',' ')
        line = line.split()
        line[1] = float(line[1])
        line[2] = float(line[2])
        line[1],line[2] = transform(in_proj,out_proj,line[1],line[2])
        coordinate_df.loc[len(coordinate_df)] = line
    print(coordinate_df)
    coordinate_df.to_csv('swmm_coordinate_mapping.csv',index=False)
        


def osm_tag_mapping():
    amenity_df = pd.read_csv('amenity_score.csv')
    df = pd.read_csv('./extracted_tags.csv')
    '''
    Selecting only valid locations within the bounding box of the SWMM model
    '''
    df = df[(df['longitude'] >= -117.9544) & (df['longitude'] <=-117.6114)]
    df = df[(df['latitude'] >= 33.5906) & (df['latitude'] <=33.8060)]
    df = df.loc[df['tagvalue'].isin(amenity_df['amenity'])]
    df.columns = ['id','longitude','latitude','visible','tagkey','amenity']
    df = pd.merge(df, amenity_df, on=['amenity'])

    # 1 degree difference is approx 110 km
    # difference of 0.02 degree is approx 2.2 km 
    swmm_node = pd.read_csv('swmm_coordinate_mapping.csv')

    output_df = pd.DataFrame(columns=['node','score'])

    for index, row in tqdm(swmm_node.iterrows(),desc='getting node scores'):
        node,x,y = row[0],row[1],row[2]
        bbox = [row[1] - 0.02, row[1] + 0.02, row[2] - 0.02, row[2] + 0.02]
        temp_df = df[(df['longitude'] >= bbox[0]) & (df['longitude'] <= bbox[1])]
        temp_df = temp_df[(temp_df['latitude'] >= bbox[2]) & (temp_df['latitude'] <= bbox[3])]
        score = temp_df['score'].sum()
        output_df.loc[len(output_df)] = [node,score]

    print(output_df)
    output_df.to_csv('swmm_node_score.csv',index=False)



if __name__ == '__main__':
    # amenity_score()
    # swmm_coord_extract()
    osm_tag_mapping()

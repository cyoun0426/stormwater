import osmium as osm
import pandas as pd
import numpy as np

class OSMHandler(osm.SimpleHandler):
    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.osm_data = []
        self.osm_loc = []

    def tag_inventory(self, elem, elem_type):
        # Longitude = X ; Latitude = Y
        if elem_type == "node":
            for tag in elem.tags:
                self.osm_loc.append([elem.id, elem.location.lon_without_check(), elem.location.lat_without_check(), elem.visible, tag.k, tag.v])
        
        elif elem_type == "way":
            for node in elem.nodes:
                for tag in elem.tags:
                    self.osm_loc.append([node.ref, node.location.lon_without_check(), node.location.lat_without_check(), elem.visible, tag.k, tag.v])
        
        elif elem_type == "relation":
            for member in elem.members:
                if member.type == "node":
                    for tag in elem.tags:
                        osm_loc.append([member.ref, member.lon_without_check(). member.lat_without_check(), elem.visible, tag.k, tag.v])
                elif member.type == "way":
                    for node in member.nodes:
                        for tag in elem.tags:
                            self.osm_loc.append([node.ref, node.location.lon_without_check(), node.location.lat_without_check(), elem.visible, tag.k, tag.v])
            


    def node(self, n):
        self.tag_inventory(n, "node")

    def way(self, w):
        self.tag_inventory(w, "way")

    def relation(self, r):
        self.tag_inventory(r, "relation")


if __name__ == '__main__':
    osmhandler = OSMHandler()
    # scan the input file and fills the handler list accordingly
    osmhandler.apply_file("map.osm")

    # transform the list into a pandas DataFrame
    loc_colnames = ['id', 'longitude', 'latitude', 'visible', 'tagkey', 'tagvalue']

    df_loc = pd.DataFrame(osmhandler.osm_loc, columns = loc_colnames)
    df_loc = df_loc.sort_values(by=['id'])
    print(df_loc.head())
    df_loc.drop_duplicates(inplace=True)
    df_loc.to_csv('./extracted_tags.csv', index=False)
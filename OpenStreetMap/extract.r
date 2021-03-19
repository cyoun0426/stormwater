library("osmar")

#### RUN THE OSMOSIS COMMANDS ######
# system("osmosis --read-xml extracted_maryland.osm --tf accept-nodes amenity=* --tf reject-ways --tf reject-relations --write-xml outputnode.osm")
# system("osmosis --rx extracted_maryland.osm --tf reject-relations --tf accept-ways amenity=* aeroway=* highway=motorway highway=trunk highway=primary highway=secondary highway=tertiary --used-node --wx outputway.osm")
####################################
# Now we extract the amenities and ways from the 2 files 

ua = get_osm(complete_file(),source = osmsource_file("outputnode.osm"))
# print(summary(ua$nodes))
# temp_df = as.data.frame(ua$nodes$tags)
# temp_df$v = gsub('\\s+','',temp_df$v)
# temp_df = temp_df[,-1]
# required_rows = which(temp_df$k == 'amenity')
# temp_df = temp_df[required_rows,]    # Get the rows corresponding to amenities
# required_vector = sort(table(temp_df$v),decreasing=TRUE) # Get the frequency table
# write.csv(required_vector,"amenitylist.csv",row.names=FALSE)

ub = get_osm(complete_file(),source = osmsource_file("outputway.osm"))
# print(summary(ub$ways))
# temp_df = as.data.frame(ub$ways$tags)
# temp_df$v = gsub('\\s+','',temp_df$v)
# temp_df = temp_df[,-1]
# required_rows = which(temp_df$k %in% c('amenity','highway','aeroway'))
# temp_df = temp_df[required_rows,]
# required_vector = sort(table(temp_df$v),decreasing=TRUE)
# write.csv(required_vector,"waylist.csv",row.names=FALSE)

######################## Following section is to choose the required amenities #######################

amenity_list = c("school","place_of_worship","bank","pharmacy","post_office","fire_station",
	"police","post_box","library","clinic","hospital","nursing_home","public_building",
	"radiology","townhall","veterinary","restaurant")

amenity_score = c(7,7,8,7,6,9,9,5,5,10,10,10,8,10,9,10,6)

way_list = c("tertiary","school","place_of_worship","restaurant","bank","taxiway","pharmacy",
	"runway","shelter","hospital","apron","community_centre","fire_station","aerodrome",
	"clinic","public_building","helipad","library","police","post_office","prison","terminal",
	"townhall","university","veterinary")
way_score = c(6,7,7,6,8,10,7,10,8,10,10,9,9,10,10,6,10,5,9,7,9,10,9,7,10)

total_df = data.frame()

for(i in 1:length(amenity_list))
{
	print(i)
	current_amenity = amenity_list[i]
	current_score = amenity_score[i]
	ts_ids = find(ua,node(tags(v == current_amenity)))
	ts = subset(ua,node_ids=ts_ids)
	current_amenity = rep(current_amenity,length(ts$nodes$attrs$id))
	current_score = rep(current_score,length(ts$nodes$attrs$id))
	temp_df = data.frame(cbind(current_amenity,current_score,ts$nodes$attrs$id,ts$nodes$attrs$lon,ts$nodes$attrs$lat))
	colnames(temp_df) = c("place","score","id","lon","lat")
	total_df = rbind(total_df,temp_df)
}


for(i in 1:length(way_list))
{
	print(i)
	current_way = way_list[i]
	current_score = way_score[i]
	ts_ids = find(ub,way(tags(v == current_way)))
	ts_ids <- find_down(ub, way(ts_ids))
	ts <- subset(ub, ids = ts_ids)
	current_way = rep(current_way,length(ts$nodes$attrs$id))
	current_score = rep(current_score,length(ts$nodes$attrs$id))
	temp_df = data.frame(cbind(current_way,current_score,ts$nodes$attrs$id,ts$nodes$attrs$lon,ts$nodes$attrs$lat))
	colnames(temp_df) = c("place","score","id","lon","lat")
	total_df = rbind(total_df,temp_df)
}

total_df = total_df[!duplicated(total_df[c('place','id')]),]

write.csv(total_df,"final_extraction_coordinates.csv",row.names=FALSE)
# ts_ids <- find(ub, way(tags(v == "school")))
# ts_ids <- find_down(ub, way(ts_ids))
# print(str(ts_ids))

# ts <- subset(ub, ids = ts_ids)
# # print(summary(ts))
# # print((ts$ways$attrs))
# # print(summary(ts$nodes))
# print(ts$nodes$attrs)
# print(ts$nodes$attrs$id)
# temp_df = data.frame(cbind(ts$nodes$attrs$id,ts$nodes$attrs$lat,ts$nodes$attrs$lon))
# print(temp_df)
# end.time <- Sys.time()
# time.taken <- end.time - start.time
# print(time.taken)
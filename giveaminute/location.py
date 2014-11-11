"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

from framework.log import log
  
def getLocationsWithScoring(db):
    data = []
    
    log.info("*** hit locations")

    try:
        # TODO
        # this is temporary until actual scoring is determined
        sql = """
select l.location_id,
    l.name,
    l.lat,
    l.lon,
    count(distinct p.project_id) as num_projects,
    count(distinct i.idea_id) as num_ideas,
    count(distinct r.project_resource_id) as num_project_resources
from location l 
	left join project p on p.location_id = l.location_id and p.is_active=1
    left join project__user pu on p.project_id=pu.project_id and pu.is_project_admin = 1 and p.is_active=1
	left join idea i on l.location_id = i.location_id and i.is_active=1
	left join project_resource r on l.location_id = r.location_id and r.is_active=1 and r.is_hidden=0
where l.location_id > 0
group by l.location_id+l.lat+l.lon
order by l.location_id""";

        data = list(db.query(sql))
    except Exception, e:
        log.info("*** couldn't get locations")
        log.error(e)

    return data 
        
def getLocations(db):
    data = []

    try:
        sql = """select l.location_id, l.name, l.lat, l.lon, l.geometry from location l where l.location_id > 0
                order by l.location_id""";
        data = list(db.query(sql))
    except Exception, e:
        log.info("*** couldn't get locations")
        log.error(e)

    return data

def getAllLocations(db):
    data = []

    try:
        sql = """select l.location_id, l.name, l.lat, l.lon, l.geometry from location l
                order by l.location_id""";
        data = list(db.query(sql))
    except Exception, e:
        log.info("*** couldn't get all locations")
        log.error(e)

    return data

def getLocationInfo(db, locationId):
    info = {}
    
    try:
        sql = """select 'n_projects' as key_name, count(*) as num from project where location_id = $id
union
select 'n_ideas' as key_name, count(*) as num from idea where location_id = $id
union
select 'n_resources' as key_name, count(*) as num from project_resource where location_id = $id;"""
        data = list(db.query(sql, {'id': locationId}))

        for item in data:
            info[item.key_name] = item.num
    except Exception, e:
        log.info("*** couldn't get location info")
        log.error(e)

    return info

# deprecated ?
def getSimpleLocationDictionary(db):
    data = getLocations(db)
    
    locations = []
    
    for item in data:
        locations.append({'name': item.name, 'location_id': item.location_id, 'location_geometry': item.geometry})
        
    return locations

def getSimpleLocationDictionaryIncludingCity(db):
    data = getAllLocations(db)

    locations = []

    for item in data:
        locations.append({'name': item.name, 'location_id': item.location_id, 'location_geometry': item.geometry})

    return locations


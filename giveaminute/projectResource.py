"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

from framework.log import log
import helpers.censor as censor


class ProjectResource():
    def __init__(self, db, projectResourceId):
        self.id = projectResourceId
        self.db = db
        self.data = self.populateResourceData()

    def populateResourceData(self):
        sql = """select pr.project_resource_id, 
                        pr.title, 
                        pr.description, 
                        pr.url, 
                        pr.contact_name, 
                        pr.contact_email, 
                        pr.image_id, 
                        pr.location_id, 
                        pr.is_official,
                        o.user_id as owner_user_id,
                        o.first_name as owner_first_name,
                        o.last_name as owner_last_name,
                        o.email as owner_email
                from project_resource pr 
                left join user o on o.user_id = pr.contact_user_id
                where pr.project_resource_id = $id;"""

        try:
            data = list(self.db.query(sql, {'id': self.id}))

            if len(data) > 0:
                return data[0]
            else:
                return None
        except Exception, e:
            log.info("*** couldn't get project resource info")
            log.error(e)
            return None

    def getFullDictionary(self):
        data = dict(image_id=self.data.image_id,
                    project_resource_id=self.data.project_resource_id,
                    description=self.data.description,
                    title=self.data.title,
                    url=self.data.url,
                    location_id=self.data.location_id,
                    is_official=self.data.is_official)
        return data


def searchProjectResourcesCount(db, terms, locationId):
    count = 0
    match = ' '.join([(item + "*") for item in terms])

    try:
        sql = """select count(*) as count
                from project_resource
                    where
                    is_active = 1 and is_hidden = 0
                    and ($locationId is null or location_id = $locationId)
                    and ($match = '' or match(title, keywords, description) against ($match in boolean mode))"""

        data = list(db.query(sql, {'match': match, 'locationId': locationId}))

        count = data[0].count
    except Exception, e:
        log.info("*** couldn't get resources search data")
        log.error(e)

    return count


def searchProjectResources(db, terms, locationId, limit=1000, offset=0):
    data = []

    match = ' '.join([(item + "*") for item in terms])

    try:
        sql = """select project_resource_id as link_id, title, url, image_id, is_official 
                from project_resource
                    where
                    is_active = 1 and is_hidden = 0
                    and ($locationId is null or location_id = $locationId)
                    and ($match = '' or match(title, keywords, description) against ($match in boolean mode))
                    order by created_datetime desc
                    limit $limit offset $offset"""

        data = list(db.query(sql, {'match': match, 'locationId': locationId, 'limit': limit, 'offset': offset}))
    except Exception, e:
        log.info("*** couldn't get resources search data")
        log.error(e)

    return data


def updateProjectResourceImage(db, projectResourceId, imageId):
    try:
        db.update('project_resource', where="project_resource_id = $id", image_id=imageId,
                  vars={'id': projectResourceId})
        return True
    except Exception, e:
        log.info("*** couldn't update project image")
        log.error(e)
        return False


def updateProjectResourceLocation(db, projectResourceId, locationId):
    try:
        db.update('project_resource', where="project_resource_id = $id", location_id=locationId,
                  vars={'id': projectResourceId})
        return True
    except Exception, e:
        log.info("*** couldn't update project location")
        log.error(e)
        return False


def updateProjectResourceTextData(db, projectResourceId, field, text):
    isHidden = (censor.badwords(db, text) > 0)

    try:
        sql = "update project_resource set %s = $text, is_hidden = $isHidden where project_resource_id = $id" % field
        db.query(sql, {'id': projectResourceId, 'text': text, 'isHidden': isHidden})
        return True
    except Exception, e:
        log.info("*** couldn't update project %s" % field)
        log.error(e)
        return False


def getUnreviewedProjectResources(db, limit=10, offset=0):
    data = []

    try:
        sql = """select pr.project_resource_id, 
                        pr.title, pr.description, 
                        pr.image_id, 
                        pr.location_id, 
                        pr.url,
                        pr.twitter_url,
                        pr.facebook_url,
                        pr.physical_address,
                        pr.contact_name,
                        pr.contact_email,
                        pr.message,
                        replace(pr.keywords, ' ', ',') as keywords,
                        l.name as location_name
                    from project_resource pr 
                    left join location l on l.location_id = pr.location_id
                    where pr.is_active = 1 and pr.is_hidden = 1 
                    limit $limit offset $offset"""

        data = list(db.query(sql, {'limit': limit, 'offset': offset}))
    except Exception, e:
        log.info("*** couldn't get unreviewed resources")
        log.error(e)

    return data


def approveProjectResource(db, projectResourceId, isOfficial=False):
    try:
        db.update('project_resource', where="project_resource_id = $projectResourceId", is_hidden=0,
                  is_official=isOfficial, vars={'projectResourceId': projectResourceId})
        return True
    except Exception, e:
        log.info("*** couldn't approve project resource %s" % projectResourceId)
        log.error(e)
        return False
"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

from framework.controller import *
import framework.util as util
import giveaminute.location as mLocation
import giveaminute.projectResource as mProjectResource

class Resource(Controller):
    def GET(self, action = None, param0 = None):
        self.require_login("/login")
        
        return self.showAddResource()    
    
    def POST(self, action = None, param0 = None):
        if (self.user):
            if (not action):
                return self.addResource()
            elif (action == 'edit'):
                if (param0 == 'image'):
                    return self.updateResourceImage()
                elif (param0 == 'location'):
                    return self.updateResourceLocation()
                elif (param0 == 'description'):
                    return self.updateResourceDescription()
                elif (param0 == 'url'):
                    return self.updateResourceUrl()
                elif (param0 == 'contactemail'):
                    return self.updateResourceContactEmail()
                elif (param0 == 'address'):
                    return self.updateResourceAddress()
                elif (param0 == 'keywords'):
                    return self.updateResourceKeywords()
                elif (param0 == 'facebook_url'):
                    return self.updateResourceFacebookUrl()
                elif (param0 == 'twitter_url'):
                    return self.updateResourceTwitterUrl()
                elif (param0 == 'message'):
                    return self.updateResourceMessage()
                else:
                    #return self.not_found()
                    return 'param0 not found'
            else:
#                 return self.not_found() 
                return 'param0 not found'
        else:
            return self.not_found()
        
    def showAddResource(self):
        locationData = mLocation.getSimpleLocationDictionary(self.db)
        locations = dict(data = locationData, json = json.dumps(locationData))
        self.template_data['locations'] = locations
        
        return self.render('resource')    
        
        
    def addResource(self):
        if (self.request('main_text')): return False

        title = self.request('title')
        description = self.request('description')
        physical_address = self.request('physical_address')
        location_id = util.try_f(int, self.request('location_id'), -1)
        url = util.makeUrlAbsolute(self.request('url')) if self.request('url')  else None
        keywords = ' '.join([word.strip() for word in self.request('keywords').split(',')]) if not util.strNullOrEmpty(self.request('keywords')) else None
        contact_name = self.request('contact_name')
        contact_email = self.request('contact_email')
        facebook_url = util.makeUrlAbsolute(self.request('facebook_url')) if self.request('facebook_url') else None
        twitter_url = util.makeUrlAbsolute(self.request('twitter_url')) if self.request('twitter_url') else None
        image_id = util.try_f(int, self.request('image'))
        message = self.request('message') if self.request('message') else None
        
        # TODO this is a temp fix for a form issue
        if (contact_name == 'null'):
            contact_name = None
            
        try:
            projectResourceId = self.db.insert('project_resource', 
                                        title = title,
                                        description = description,
                                        physical_address = physical_address,
                                        location_id = location_id,
                                        url = url,
                                        facebook_url = facebook_url,
                                        twitter_url = twitter_url,
                                        keywords = keywords,
                                        contact_name = contact_name,
                                        contact_email = contact_email,
                                        created_datetime = None,
                                        image_id = image_id,
                                        is_hidden = 1,
                                        contact_user_id = self.user.id,
                                        message = message)
            
            return True
        except Exception,e:
            log.info("*** couldn't add resource to system")
            log.error(e)
            return False
            
    def updateResourceImage(self):
        resourceId = util.try_f(int, self.request('resource_id'))

        if (not self.user or not self.user.isResourceOwner(resourceId)): 
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False

        imageId = util.try_f(int, self.request('image_id'))
        
        if (imageId):
            return mProjectResource.updateProjectResourceImage(self.db, resourceId, imageId)
        else:

            log.error("*** resource edit attempt without image id, resource id %s" % resourceId)
            return False
        
    def updateResourceLocation(self):
        resourceId = util.try_f(int, self.request('resource_id'))

        if (not self.user or not self.user.isResourceOwner(resourceId)): 
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False

        locationId = util.try_f(int, self.request('location_id'))
        
        if (locationId):
            return mProjectResource.updateProjectResourceLocation(self.db, resourceId, locationId)
        else:
            log.error("*** resource edit attempt without location id, resource id %s" % resourceId)
            return False
        
    def updateResourceDescription(self):
        resourceId = util.try_f(int, self.request('resource_id'))

        if (not self.user or not self.user.isResourceOwner(resourceId)): 
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False

        description = self.request('description')
        
        if (description):
            return mProjectResource.updateProjectResourceTextData(self.db, resourceId, 'description', description)
        else:
            log.error("*** resource edit attempt without description, resource id %s" % resourceId)
            return False
        
    def updateResourceUrl(self):
        resourceId = util.try_f(int, self.request('resource_id'))

        if (not self.user or not self.user.isResourceOwner(resourceId)): 
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False

        url = self.request('url')
        
        if (url):
            return mProjectResource.updateProjectResourceTextData(self.db, resourceId, 'url', util.makeUrlAbsolute(url))
        else:
            log.error("*** resource edit attempt without url, resource id %s" % resourceId)
            return False
                
    def updateResourceContactEmail(self):
        resourceId = util.try_f(int, self.request('resource_id'))

        if (not self.user or not self.user.isResourceOwner(resourceId)): 
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False

        email = self.request('contactemail')
        
        if (email):
            return mProjectResource.updateProjectResourceTextData(self.db, resourceId, 'contact_email', email)
        else:
            log.error("*** resource edit attempt without email, resource id %s" % resourceId)
            return False
        
    def updateResourceAddress(self):
        resourceId = util.try_f(int, self.request('resource_id'))

        if (not self.user or not self.user.isResourceOwner(resourceId)): 
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False

        address = self.request('address')
        
        if (address):
            return mProjectResource.updateProjectResourceTextData(self.db, resourceId, 'physical_address', address)
        else:
            log.error("*** resource edit attempt without address, resource id %s" % resourceId)
            return False

    def updateResourceFacebookUrl(self):
        resourceId = util.try_f(int, self.request('resource_id'))
        if (not self.user or not self.user.isResourceOwner(resourceId)):
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False
        facebook_url = self.request('facebook_url')
        return mProjectResource.updateProjectResourceTextData(self.db, resourceId, 'facebook_url', facebook_url)

    def updateResourceTwitterUrl(self):
        resourceId = util.try_f(int, self.request('resource_id'))
        if (not self.user or not self.user.isResourceOwner(resourceId)):
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False
        twitter_url = self.request('twitter_url')
        return mProjectResource.updateProjectResourceTextData(self.db, resourceId, 'twitter_url', twitter_url)

    def updateResourceKeywords(self):
        resourceId = util.try_f(int, self.request('resource_id'))

        if (not self.user or not self.user.isResourceOwner(resourceId)): 
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False

        keywords = ' '.join([word.strip() for word in self.request('keywords').split(',')]) if not util.strNullOrEmpty(self.request('keywords')) else None
        
        return mProjectResource.updateProjectResourceTextData(self.db, resourceId, 'keywords', keywords)

    def updateResourceMessage(self):
        resourceId = util.try_f(int, self.request('resource_id'))

        if (not self.user or not self.user.isResourceOwner(resourceId)):
            log.error("*** resource edit attempt without ownership, resource id %s" % resourceId)
            return False

        message = self.request('message')

        return mProjectResource.updateProjectResourceTextData(self.db, resourceId, 'message', message)

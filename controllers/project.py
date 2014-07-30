"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

from framework.controller import *
import framework.util as util
import giveaminute.project as mProject
import giveaminute.idea as mIdea
import giveaminute.projectResource as mProjectResource
import giveaminute.messaging as mMessaging
import giveaminute.models as models
import helpers.censor
import json
import giveaminute.formattingUtils as formattingUtils
import re
import datetime

class Project(Controller):
    def GET(self, action=None, param0=None, param1=None):
        if (action == 'resource'):
            if (param0 == 'info'):
                return self.getResourceInfo()
            else:
                return self.not_found()
        elif (action == 'resources'):
            if (param0 == 'related'):
                return self.getRelatedResources()
            else:
                return self.getResourcesAndLinks()
        elif (action == 'messages'):
            return self.getMessages()
        elif (action == 'featured'):
            return self.getFeaturedProjects()
        elif (action == 'small'):
            return self.getProjectData()
        elif (action == 'rss'):
            return self.showConversationRSS(param0)
        else:
            return self.showProject(action)

    def POST(self, action=None, param0=None, param1=None):
        if (action == 'join'):
            return self.join()
        elif (action == 'endorse'):
            if (param0 == 'remove'):
                return self.removeEndorsement()
            else:
                return self.endorse()
        elif (action == 'link'):
            if (param0 == 'add'):
                return self.addLink()
            elif (param0 == 'remove'):
                return self.removeLink()
            else:
                return self.not_found()
        elif (action == 'resource'):
            if (param0 == 'add'):
                return self.addResource()
            elif (param0 == 'remove'):
                return self.removeResource()
            else:
                return self.not_found()
        elif (action == 'message'):
            if (param0 == 'add'):
                return self.addMessage()
            elif (param0 == 'remove'):
                return self.removeMessage()
            else:
                return self.not_found()
        elif (action == 'tag'):
            if (param0 == 'add'):
                return self.addKeywords()
            elif (param0 == 'remove'):
                return self.removeKeyword()
            else:
                return self.not_found()
        elif (action == 'invite'):
            return self.invite()
        elif (action == 'leave'):
            return self.leaveProject()
        elif (action == 'user'):
            if (param0 == 'remove'):
                return self.removeUser()
            elif (param0 == 'admin'):
                if (param1 == 'add'):
                    return self.setAdmin(True)
                elif (param1 == 'remove'):
                    return self.setAdmin(False)
                else:
                    return self.not_found()
            else:
                return self.not_found()
        elif (action == 'photo'):
            return self.updateImage()
        elif (action == 'description'):
            return self.updateDescription()
        elif (action == 'title'):
            return self.updateTitle()
        else:
            return self.not_found()

    def getProject(self, project_id):
        """Get the SQL Alchemy project object"""
        project = self.orm.query(models.Project).get(project_id)
        return project

    def showProject(self, projectId):
        """The main project detail view controller."""
        if (projectId):
            project = mProject.Project(self.db, projectId)

            if (project.data):
                projDictionary = project.getFullDictionary()

                project_user = self.getProjectUser(projectId)
                self.template_data['project_user'] = dict(data = project_user, json = json.dumps(project_user))

                project_proxy = self.getProject(projectId)
                project_proxy.json = json.dumps(projDictionary)
                project_proxy.data = projDictionary

                self.template_data['project'] = project_proxy

                import giveaminute.filters as gam_filters
                gam_filters.register_filters()
                return self.render('project')
            else:
                return self.not_found()
        else:
            return self.not_found()


    def showConversationRSS(self, projectId):
        if (projectId):
            project = mProject.Project(self.db, projectId)
            projDictionary = project.getFullDictionary()

            self.template_data['project'] = dict(json = json.dumps(projDictionary), data = projDictionary)

            msgs = self.template_data['project']['data']['info']['messages']['items']

            for item in msgs:
                item['created'] = datetime.datetime.strptime(item['created'], '%Y-%m-%d %H:%M:%S').strftime('%a, %d %b %Y %H:%M:%S EST')

            return self.render('project/conversation_rss', suffix='xml.rss', content_type = 'application/rss+xml')
        else:
            return self.not_found()

    def getProjectUser(self, projectId):
        projectUser = dict(is_project_admin = False, is_member = False, is_invited_by_idea = False, can_endorse = False)

        if (self.user):
            sqlInvited = """select pi.project_id from project_invite pi
                              inner join idea i on i.idea_id = pi.invitee_idea_id
                              where pi.project_id = $projectId and i.user_id = $userId
                              limit 1"""
            dataInvited = list(self.db.query(sqlInvited, {'userId':self.user.id, 'email':self.user.email, 'projectId':projectId}))

            projectUser['is_invited_by_idea'] = (len(dataInvited) == 1)

            sqlMember = "select is_project_admin from project__user where user_id = $userId and project_id = $projectId limit 1"
            dataMember = list(self.db.query(sqlMember, {'userId':self.user.id, 'projectId':projectId}))

            if (len(dataMember)== 1):
                projectUser['is_member'] = True

                if (dataMember[0].is_project_admin == 1):
                    projectUser['is_project_admin'] = True

            # # #
            if (self.user.isLeader):
                sqlEndorse = "select user_id from project_endorsement where project_id = $projectId and user_id = $userId limit 1"
                dataEndorse = list(self.db.query(sqlEndorse,  {'userId':self.user.id, 'projectId':projectId}))

                projectUser['can_endorse'] = (len(dataEndorse) == 0)
            else:
                projectUser['can_endorse'] = False

        return projectUser

    def join(self):
        projectId = self.request('project_id')

        if (not self.user):
            log.error("*** join submitted w/o logged in user")
            return False
        elif (not projectId):
            log.error("*** join submitted w/o logged project id")
            return False
        
        else:
            isJoined = mProject.join(self.db, projectId, self.user.id)

            if (isJoined):
                project = mProject.Project(self.db, projectId)
                
                # add a message to the queue about the join
                message = 'New Member! Your project now has %s total!' % project.data.num_members

                # email admin
                if (not mMessaging.emailProjectJoin(project.data.owner_email,
                                                    projectId,
                                                    project.data.title,
                                                    self.user.id,
                                                    formattingUtils.userNameDisplay(self.user.firstName,
                                                                             self.user.lastName,
                                                                             self.user.affiliation,
                                                                             formattingUtils.isFullLastName(self.user.groupMembershipBitmask)))):
                    log.error("*** couldn't email admin on user_id = %s joining project %s" % (self.user.id, projectId))

                if (not mProject.addMessage(self.db,
                                            projectId,
                                            message,
                                            'join',
                                            self.user.id)):
                    log.error("*** new message not created for user %s on joining project %s" % (self.user.id, projectId))

        return isJoined

    def invite(self):
        projectId = self.request('project_id')
        ideaId = self.request('idea_id')
        emails = self.request('email_list')
        message = self.request('message')

        if (not self.user):
            log.error("*** invite w/o logged in user")
            return False
        elif (not projectId):
            log.error("***invite w/o project id")
            return False
        else:
            if (ideaId):
                return mProject.inviteByIdea(self.db, projectId, ideaId, message, self.user)
            elif (emails):
                return mProject.inviteByEmail(self.db, projectId, emails.split(','), message, self.user)
            else:
                log.error("*** invite w/o idea or email")
                return False


    def endorse(self):
        projectId = self.request('project_id')

        if (not self.user or not self.user.isLeader):
            log.error("*** endorsement submitted w/o logged in user or with non-project leader user account")
            return False
        else:
            isEndorsed = mProject.endorse(self.db, projectId, self.user.id)

            if (isEndorsed):
                # TODO do we need to get the whole project here?
                project = mProject.Project(self.db, projectId)

                # email admin
                if (not mMessaging.emailProjectEndorsement(project.data.owner_email,
                                                    project.data.title,
                                                    "%s %s" % (self.user.firstName, self.user.lastName))):
                    log.error("*** couldn't email admin on user_id = %s endorsing project %s" % (self.user.id, projectId))

                # add a message to the queue about the join
                message = 'Congratulations! Your group has now been endorsed by %s %s.' % (self.user.firstName, self.user.lastName)

                if (not mProject.addMessage(self.db,
                                            projectId,
                                            message,
                                            'endorsement',
                                            self.user.id)):
                    log.error("*** new message not created for user %s on endorsing project %s" % (self.user.id, projectId))

            return isEndorsed

    def removeEndorsement(self):
        projectId = self.request('project_id')
        userId = util.try_f(int, self.request('user_id'))

        if (self.user and
            ((self.user.isLeader and self.user.id == userId) or
            self.user.isAdmin)):
            isRemoved = mProject.removeEndorsement(self.db, projectId, userId)

            # if successfully removed, remove messages as well
            if (isRemoved):
                mProject.removeEndorsementMessage(self.db, projectId, userId)

            return isRemoved
        else:
            log.error("*** attempt to remove endorsement w/o proper credentials")
            return False

    def addLink(self):
        if (self.request('main_text')): return False

        projectId = self.request('project_id')
        title = self.request('title')
        url = util.makeUrlAbsolute(self.request('url')) if self.request('url') else None

        if (not projectId or util.strNullOrEmpty(title) or util.strNullOrEmpty(url)):
            log.error("*** link submitted w/o id, title, or url")
            return False
        else:
            return mProject.addLinkToProject(self.db, projectId, title, url)

    def removeLink(self):
        projectId = self.request('project_id')
        linkId = self.request('link_id')

        if (not linkId):
            log.error("*** link removal submitted missing an id")
            return False
        else:
            if (not self.user.isAdmin and
                not self.user.isModerator and
                not self.user.isProjectAdmin(projectId)):
                log.warning("*** unauthorized link removal attempt by user_id = %s" % self.user.id)
                return False
            else:
                return mProject.setLinkIsActive(self.db, linkId, 0)


    def addResource(self):
        projectId = self.request('project_id')
        projectResourceId = self.request('project_resource_id')

        if (not projectId or not projectResourceId):
            log.error("*** resource submitted missing an id")
            return False
        else:
            if (mProject.addResourceToProject(self.db, projectId, projectResourceId)):
                # TODO do we need to get the whole project here?    
                project = mProject.Project(self.db, projectId)
                res = mProjectResource.ProjectResource(self.db, projectResourceId)

                if (not mMessaging.emailResourceNotification(res.data.contact_email, projectId, project.data.title, project.data.description, res.data.title)):
                    log.error("*** couldn't email resource id %s" % projectResourceId)
            else:
                log.error("*** couldn't add resource %s to project %s" % (projectResourceId, projectId))
                return False

    def removeResource(self):
        projectId = self.request('project_id')
        projectResourceId = self.request('project_resource_id')

        if (not projectId or not projectResourceId):
            log.error("*** resource removal submitted missing an id")
            return False
        else:
            if (not self.user.isAdmin and
                not self.user.isModerator and
                not self.user.isProjectAdmin(projectId)):
                log.warning("*** unauthorized resource removal attempt by user_id = %s" % self.user.id)
                return False
            else:
                return mProject.removeResourceFromProject(self.db, projectId, projectResourceId)


    def getResourceInfo(self):
        projectResourceId = self.request('project_resource_id')
        info = None
        resource = mProjectResource.ProjectResource(self.db, projectResourceId)

        if (resource.data):
            info = self.json(resource.getFullDictionary())

        return info

    def getResourcesAndLinks(self):
        projectId = self.request('project_id')

        data = dict(links = mProject.getLinks(self.db, projectId),
                    resources = mProject.getResources(self.db, projectId))

        return self.json(data)

    def getRelatedResources(self):
        projectId = self.request('project_id')
        resources = []

        project = mProject.Project(self.db, projectId)

        keywords = project.data.keywords.split()
        locationId = project.data.location_id

        resources = mProjectResource.searchProjectResources(self.db, keywords, locationId)

        obj = dict(resources = resources)

        return self.json(obj)

    def addMessage(self):
        """
        Add a message to the project discussion stream.

        POST Parameters:
        ---------------
        project_id -- The id of the project
        main_text -- The message contents
        attachment_id -- (optional) The file attachment on the message. If no
            file attachment is available, it should be an empty string or left
            off of the request entirely.

        """
        if (self.request('main_text')): return False

        projectId = self.request('project_id')
        message = self.request('message')

        # If the file_id is None or empty string, record it as None.
        attachmentId = self.request('attachment_id') or None

        if (not projectId):
            log.error("*** message add attempted w/o project id")
            return False
        elif (util.strNullOrEmpty(message)):
            log.error("*** message add attempted w/ no message")
            return False
        else:
            return mProject.addMessage(self.db, projectId, message,
                                       'member_comment', self.user.id,
                                       attachmentId=attachmentId)


    def removeMessage(self):
        messageId = self.request('message_id')

        if (not messageId):
            log.error("*** message remove attempted w/o ids")
            return False
        else:
            return mProject.removeMessage(self.db, messageId)

    def getMessages(self):
        projectId = self.request('project_id')
        limit = util.try_f(int, self.request('n_messages'), 10)
        offset = util.try_f(int, self.request('offset'), 0)
        filterBy = self.request('filter')

        return self.json(mProject.getMessages(self.db, projectId, limit, offset, filterBy))

    def getFeaturedProjects(self):
        # overkill to get the full dictionary, but it's a small admin-only call
        projects = mProject.getFeaturedProjectsDictionary(self.db)

        return self.json(projects)


    def getProjectData(self):
        projectId = self.request('project_id')

        project = mProject.Project(self.db, projectId)

        return self.json(formattingUtils.smallProject(project.id,
                                                project.data.title,
                                                project.data.description,
                                                project.data.image_id,
                                                project.data.num_members,
                                                project.data.owner_user_id,
                                                project.data.owner_first_name,
                                                project.data.owner_last_name,
                                                project.data.owner_image_id))

    def addKeywords(self):
        projectId = self.request('project_id')
        keywords = self.request('text')
                
        if (projectId and keywords):
            return mProject.addKeywords(self.db, projectId, keywords.split(','))
        else:
            log.error("*** add keyword attempted w/o project id or keywords")
            return False

    def removeKeyword(self):
        projectId = self.request('project_id')
        keyword = self.request('text')

        return mProject.removeKeyword(self.db, projectId, keyword)

    def leaveProject(self):
        userId = self.session.user_id
        projectId = self.request('project_id')

        return mProject.removeUserFromProject(self.db, projectId, userId)

    def removeUser(self):
        projectId = self.request('project_id')
        userId = self.request('user_id')

        return mProject.removeUserFromProject(self.db, projectId, userId)

    def updateImage(self):
        projectId = self.request('project_id')
        imageId = self.request('image_id')

        return mProject.updateProjectImage(self.db, projectId, imageId)

    def updateDescription(self):
        projectId = self.request('project_id')
        description = self.request('text')

        return mProject.updateProjectDescription(self.db, projectId, description)

    def updateTitle(self):
        project_id = self.request('project_id')
        title = self.request('title')

        num_flags = helpers.censor.badwords(self.db, title)
        if num_flags == 2:
            return False

        project = self.orm.query(models.Project).get(project_id)
        if project is None:
            return False

        project.title = title
        self.orm.commit()

        return True

    def setAdmin(self, b):
        projectId = self.request('project_id')
        userId = self.request('user_id')
        
        projectUser = self.orm.query(models.ProjectMember).get((userId, projectId))
        
        # TODO prevent last admin from being deleted
        # TODO on delete of creator, make oldest admin creator
        
        if projectUser:
            projectUser.is_project_admin = b
            self.orm.commit()
            
            return True
        else:
            return False

"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

import giveaminute.idea as mIdea
import giveaminute.keywords as mKeywords
import giveaminute.project as mProject
import giveaminute.messaging as mMessaging
import framework.util as util
from framework.controller import *
from framework.config import *


class Idea(Controller):
    def GET(self, action=None, id=None):
        if (action == 'related'):
            return self.getRelatedProjects()
        else:
            return self.showIdea(action)


    def POST(self, action=None):
        if (action == 'flag'):
            return self.flagIdea()
        elif (action == 'remove'):
            return self.removeIdea()
        else:
            return self.newIdea()


    def getIdea(self, idea_id):
        """Get the SQL Alchemy project object"""
        idea = self.orm.query(models.Idea).get(idea_id)
        return idea

    def showIdea(self, ideaId):
        """The main idea detail view controller."""
        if (ideaId):
            try:
                idea = mIdea.Idea(self.db, ideaId)

                if (idea.data):
                    ideaDictionary = idea.getFullDictionary()

                    # idea_proxy = self.getIdea(ideaId)
                    # idea_proxy.json = json.dumps(ideaDictionary)
                    # idea_proxy.data = ideaDictionary
                    messages = dict(total=2,
                                    n_returned=2,
                                    items=[dict(type='member_comment', body="First!11!!!", owner=dict(u_id=1, image_id=7, name="John")),
                                           dict(type='member_comment', body="Damn you first!!!", owner=dict(u_id=2, image_id=8, name="Bill"))])
                    conversation = dict(
                                        messages=messages
                                        )
                    ideaDictionary['conversation'] = conversation
                    # self.template_data['idea'] = idea_proxy
                    self.template_data['idea'] = ideaDictionary

                    #TODO: here also load the "conversation" around the idea

                    import giveaminute.filters as gam_filters

                    gam_filters.register_filters()
                    return self.render('idea')
                else:
                    return self.not_found()
            except Exception, e:
                log.error("Couldn't load idea with ideaId %s", ideaId)
                log.error(e)
                return self.not_found()
        else:
            return self.not_found()

    def newIdea(self):
        if (self.request('main_text')): return False

        description = self.request('text')
        locationId = util.try_f(int, self.request('location_id'), -1)

        if (self.user):
            userId = self.user.id
            email = self.user.email
        else:
            userId = None
            email = self.request('email')

        ideaId = mIdea.createIdea(self.db, description, locationId, 'web', userId, email)

        if (ideaId):
            mMessaging.emailIdeaConfirmation(email, Config.get('email').get('from_address'), locationId)

            return ideaId
        else:
            return False

        return ideaId if ideaId else False

    def flagIdea(self):
        ideaId = self.request('idea_id')

        if (ideaId):
            return mIdea.flagIdea(self.db, ideaId)
        else:
            return False

    def removeIdea(self):
        ideaId = self.request('idea_id')

        if (ideaId):
            idea = mIdea.Idea(self.db, ideaId)

            if (idea.data):
                if (not self.user.isAdmin and
                        not self.user.isModerator and
                        not self.user.id == idea.data.user_id):
                    log.warning("*** unauthorized idea removal attempt by user_id = %s" % self.user.id)
                    return False
                else:
                    return mIdea.setIdeaIsActive(self.db, ideaId, 0)
            else:
                log.error("*** idea does not exist for idea id %s" % ideaId)
        else:
            log.error("*** attempting to delete idea with no id")
            return False

    def likeIdea(self):
        ideaId = self.request('idea_id')

        if (ideaId):
            idea = mIdea.Idea(self.db, ideaId)
        # TODO: add +1 to the idea
        else:
            log.error("*** attempting to like idea with no id")
            return False

    def getRelatedProjects(self):
        ideaId = self.request('idea_id')
        limit = int(self.request('n_limit')) if self.request('n_limit') else 5
        relatedProjects = []
        citywideProjects = []
        kw = []
        isLocationOnlyMatch = False

        if (not ideaId):
            log.error("No idea id")
        else:
            idea = mIdea.Idea(self.db, ideaId)

            if (idea):
                kw = mKeywords.getKeywords(self.db, idea.description)

                if (idea.locationId != -1):
                    relatedProjects = mProject.searchProjects(self.db, kw, idea.locationId, limit)

                    if (len(relatedProjects) == 0):
                        isLocationOnlyMatch = True
                        relatedProjects = mProject.searchProjects(self.db, [], idea.locationId, limit)

                citywideProjects = mProject.searchProjects(self.db, kw, -1, limit)
            else:
                log.error("No idea found for id = %s" % ideaId)

        obj = dict(is_location_only_match=isLocationOnlyMatch, related=relatedProjects, citywide=citywideProjects,
                   search_terms=','.join(kw))

        return self.json(obj)

    def getIdeaUser(self, ideaId):
        projectUser = dict()

        if (self.user):
            sqlInvited = """select pi.project_id from project_invite pi
                              inner join idea i on i.idea_id = pi.invitee_idea_id
                              where pi.project_id = $projectId and i.user_id = $userId
                              limit 1"""
            dataInvited = list(
                self.db.query(sqlInvited, {'userId': self.user.id, 'email': self.user.email, 'projectId': projectId}))

            projectUser['is_invited_by_idea'] = (len(dataInvited) == 1)

            sqlMember = "select is_project_admin from project__user where user_id = $userId and project_id = $projectId limit 1"
            dataMember = list(self.db.query(sqlMember, {'userId': self.user.id, 'projectId': projectId}))

            if (len(dataMember) == 1):
                projectUser['is_member'] = True

                if (dataMember[0].is_project_admin == 1):
                    projectUser['is_project_admin'] = True

            # # #
            if (self.user.isLeader):
                sqlEndorse = "select user_id from project_endorsement where project_id = $projectId and user_id = $userId limit 1"
                dataEndorse = list(self.db.query(sqlEndorse, {'userId': self.user.id, 'projectId': projectId}))

                projectUser['can_endorse'] = (len(dataEndorse) == 0)
            else:
                projectUser['can_endorse'] = False

        return projectUser
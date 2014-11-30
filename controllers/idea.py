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
        elif (action == 'messages'):
            return self.getMessages()
        else:
            return self.showIdea(action)


    def POST(self, action=None, param0=None):
        if (action == 'flag'):
            return self.flagIdea()
        elif (action == 'like'):
            return self.likeIdea()
        elif (action == 'unlike'):
            return self.unlikeIdea()
        elif (action == 'remove'):
            return self.removeIdea()
        elif (action == 'message'):
            if (param0 == 'add'):
                return self.addMessage()
            elif (param0 == 'remove'):
                return self.removeMessage()
            else:
                return self.not_found()
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
                    likers = mIdea.searchLikers(self.db, ideaId)
                    related_projects = mIdea.findProjectsRelatedToIdea(self.db, ideaId)
                    self.template_data['related_projects'] = related_projects

                    ideaDictionary['likes'] = len(likers)
                    ideaDictionary['likers'] = likers
                    ideaDictionary['liked'] = mIdea.isLikedByUser(self.user.id, likers) if self.user is not None else False

                    # idea_proxy = self.getIdea(ideaId)
                    # idea_proxy.json = json.dumps(ideaDictionary)
                    # idea_proxy.data = ideaDictionary
                    # self.template_data['idea'] = idea_proxy

                    messages_limit = util.try_f(int, self.request('n_messages'), 10)
                    messages_offset = util.try_f(int, self.request('offset'), 0)
                    messages_filterBy = self.request('filter')
                    messages = mIdea.getMessages(self.db, ideaId, messages_limit, messages_offset, messages_filterBy)
                    messages_dict = dict(total=len(messages), n_returned=len(messages), items=messages)

                    conversation = dict(messages=messages_dict)
                    ideaDictionary['conversation'] = conversation

                    idea_proxy = self.getIdea(ideaId)
                    idea_proxy.json = json.dumps(ideaDictionary)
                    idea_proxy.data = ideaDictionary

                    self.template_data['idea'] = idea_proxy

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
        homepage_question_id = self.request('homepage_question_id')

        if (self.user):
            userId = self.user.id
            email = self.user.email
        else:
            userId = None
            email = self.request('email')

        ideaId = mIdea.createIdea(self.db, description, locationId, 'web', userId, email, None, homepage_question_id)

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
        if (self.user is None):
            return False

        if (ideaId):
            return mIdea.upvoteIdea(self.db, ideaId, self.user.id)
        else:
            log.error("*** attempting to like idea with no id")
            return False

    def unlikeIdea(self):
        ideaId = self.request('idea_id')

        if (ideaId):
            return mIdea.downvoteIdea(self.db, ideaId, self.user.id)
        else:
            log.error("*** attempting to unlike idea with no id")
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


    def addMessage(self):
        """
        Add a message to the idea discussion stream.

        POST Parameters:
        ---------------
        idea_id -- The id of the idea
        main_text -- The message contents
        attachment_id -- (optional) The file attachment on the message. If no
            file attachment is available, it should be an empty string or left
            off of the request entirely.

        """
        if (self.request('main_text')): return False

        idea_id = self.request('idea_id')
        message = self.request('message')

        # If the file_id is None or empty string, record it as None.
        attachmentId = self.request('attachment_id') or None

        if (not idea_id):
            log.error("*** idea comment add attempted w/o idea id")
            return False
        elif (util.strNullOrEmpty(message)):
            log.error("*** idea comment add attempted w/ no message")
            return False
        else:
            result = mIdea.addMessage(self.db, idea_id, message,
                                    'member_comment', self.user.id,
                                    attachmentId=attachmentId)
            this_idea = self.orm.query(models.Idea).get(idea_id)
            if this_idea.user_id is None:
                return result
            else:
                #The idea may have been sent anonymously, from a non-registered user
                idea_author = self.orm.query(models.User).get(this_idea.user_id)
                email = idea_author.email
                if result:
                    if not mMessaging.emailIdeaComment(email, idea_id, this_idea.description):
                        log.error("*** idea comment was added but no email was sent")
                        return False
                    else:
                        return True
                else:
                    return False


    def removeMessage(self):
        messageId = self.request('message_id')

        if not messageId:
            log.error("*** message remove attempted w/o ids")
            return False
        else:
            return mIdea.removeMessage(self.db, messageId)

    def getMessages(self):
        ideaId = self.request('idea_id')
        limit = util.try_f(int, self.request('n_messages'), 10)
        offset = util.try_f(int, self.request('offset'), 0)
        filterBy = self.request('filter')

        return self.json(mIdea.getMessages(self.db, ideaId, limit, offset, filterBy))
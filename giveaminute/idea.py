"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

import framework.util as util
import helpers.censor as censor
import formattingUtils
import helpers.censor
from framework.log import log


class Idea:
    def __init__(self, db, ideaId):
        self.id = ideaId
        self.db = db
        self.data = self.populateIdeaData()
        self.description = self.data.description  # This throws exception if the ideaId is not present in the database
        self.locationId = self.data.location_id

    def populateIdeaData(self):
        sql = """select i.idea_id, i.description, i.location_id, i.submission_type, i.user_id, i.email as idea_email, i.phone, i.num_flags, i.created_datetime,
                        u.first_name, u.last_name, u.email as user_email,
                        coalesce(u.email, i.email) as email
                from idea  i               
                left join user u on u.user_id = i.user_id
                                where idea_id = $id"""

        try:
            data = list(self.db.query(sql, {'id': self.id}))

            if len(data) > 0:
                return data[0]
            else:
                return None
        except Exception, e:
            log.info("*** couldn't get idea into")
            log.error(e)
            return None

    def getFullDictionary(self):
        # TODO: this method needs to return also the list of people who like the idea and the number of likes...  #GM
        if self.data is None:
            return None

        data = dict(idea_id=self.id,
                    idea_description=self.data.description,
                    idea_user_id=self.data.user_id,
                    idea_email=self.data.email,
                    idea_location=self.data.location_id,
                    idea_num_flags=self.data.num_flags,
                    idea_created=str(self.data.created_datetime),
                    idea_submission_type=self.data.submission_type,
                    idea_user_name=ideaName(self.data.first_name, self.data.last_name, None))
        return data


def createIdea(db, description, locationId, submissionType, userId=None, email=None, phone=None):
    try:
        # censor behavior
        numFlags = censor.badwords(db, description)
        isActive = 0 if numFlags == 2 else 1

        ideaId = db.insert('idea', description=description,
                           location_id=locationId,
                           submission_type=submissionType,
                           user_id=userId,
                           email=email,
                           phone=phone,
                           is_active=isActive,
                           num_flags=numFlags)
    except Exception, e:
        log.info("*** problem creating idea")
        log.error(e)
        return None

    return ideaId


def deleteIdea(db, ideaId):
    try:
        sql = """delete from idea where idea.idea_id = $id"""
        db.query(sql, {'id': ideaId})
        return True;
    except Exception, e:
        log.info("*** problem deleting id with id %s" % str(ideaId))
        log.error(e)
        return False


def attachIdeasByEmail(db, email):
    try:
        sql = """
update idea i, user u 
set i.user_id = u.user_id
where i.email = u.email 
    and u.email = $email
    and u.is_active = 1
"""
        db.query(sql, {'email': email})
        return True;
    except Exception, e:
        log.info("*** problem updating ideas by email")
        log.error(e)
        return False


def attachIdeasByPhone(db, phone):
    try:
        sql = """
update idea i, user u 
set i.user_id = u.user_id
where (i.phone is not null and i.phone <> '' and i.phone = u.phone) 
    and u.phone = $phone
    and u.is_active = 1
"""
        db.query(sql, {'phone': phone})
        return True;
    except Exception, e:
        log.info("*** problem updating ideas by phone")
        log.error(e)
        return False


def findIdeasByPhone(db, phone):
    try:
        sql = "select idea_id from idea where phone = $phone"
        return list(db.query(sql, {'phone': phone}))
    except Exception, e:
        log.info("*** problem getting ideas by phone")
        log.error(e)
        return None


def searchIdeasCount(db, terms, locationId, excludeProjectId=None):
    count = 0
    match = ' '.join([(item + "*") for item in terms])

    try:
        sql = """select count(*) as count
                from idea i
                where
                i.is_active = 1 
                and ($locationId is null or i.location_id = $locationId)
                and ($match = '' or match(i.description) against ($match in boolean mode))
                and ($projectId is null or i.idea_id not in (select pi.idea_id from project__idea pi where pi.project_id = $projectId))"""

        data = list(db.query(sql, {'match': match, 'locationId': locationId, 'projectId': excludeProjectId}))

        count = data[0].count
    except Exception, e:
        log.info("*** couldn't get idea search count")
        log.error(e)

    return count


def searchLikers(db, ideaId):
    try:
        sql = 'select user_id from idea__user where idea_id = $idea_id'
        data = list(db.query(sql, {'idea_id': ideaId}))
        return data

    except Exception, e:
        log.info("*** couldn't get users who like idea")
        log.error(e)
        return list()


def searchIdeas(db, terms, locationId, limit=1000, offset=0, excludeProjectId=None, user_id=None):
    betterData = []
    match = ' '.join([(item + "*") for item in terms])

    try:
        sql = """select i.idea_id
                       ,i.description
                      ,i.submission_type
                      ,i.created_datetime
                      ,u.user_id
                      ,u.first_name
                      ,u.last_name
                      ,u.affiliation
                      ,u.image_id
                      ,(select count(*) from idea__user iu where iu.idea_id = i.idea_id) as likes
                from idea i
                left join user u on u.user_id = i.user_id
                where
                i.is_active = 1 
                and ($locationId is null or i.location_id = $locationId)
                and ($match = '' or match(i.description) against ($match in boolean mode))
                and ($projectId is null or i.user_id not in (select pu.user_id from project__user pu where pu.project_id = $projectId))
                order by i.created_datetime desc
                limit $limit offset $offset"""

        data = list(db.query(sql, {'match': match, 'locationId': locationId, 'limit': limit, 'offset': offset,
                                   'projectId': excludeProjectId}))

        for item in data:
            owner = None
            if user_id is not None:
                likers = searchLikers(db, item.idea_id)
            else:
                likers = []

            if (item.user_id is not None):
                # repeating smallUser method from giveaminute.project to avoid circular reference
                owner = dict(u_id=item.user_id,
                             image_id=item.image_id,
                             name=ideaName(item.first_name, item.last_name, item.affiliation))

            betterData.append(dict(idea_id=item.idea_id,
                                   message=item.description,
                                   created=str(item.created_datetime),
                                   submission_type=item.submission_type,
                                   owner=owner,
                                   likes=item.likes,
                                   liked=any(user_id == y.user_id for y in likers)))
    except Exception, e:
        log.info("*** couldn't get idea search data")
        log.error(e)

    return betterData


def findIdeasByUser(db, userId, limit=100):
    ideas = []

    try:
        sql = """select i.idea_id, i.description, i.location_id, i.submission_type, i.user_id, u.first_name, u.last_name, i.created_datetime
                    from idea i 
                    inner join user u on u.user_id = i.user_id
                    where i.is_active = 1 and u.is_active = 1 and u.user_id = $userId
                order by i.created_datetime desc
                limit $limit"""

        ideas = list(db.query(sql, {'userId': userId, 'limit': limit}))
    except Exception, e:
        log.info("*** problem getting ideas for user %s" % userId)
        log.error(e)

    return ideas


def flagIdea(db, ideaId):
    try:
        sql = "update idea set num_flags = num_flags + 1 where idea_id = $ideaId"
        db.query(sql, {'ideaId': ideaId})
        return True
    except Exception, e:
        log.info("*** problem flagging idea")
        log.error(e)
        return False


def setIdeaIsActive(db, ideaId, b):
    try:
        sql = "update idea set is_active = $b where idea_id = $ideaId"
        db.query(sql, {'ideaId': ideaId, 'b': b})
        return True
    except Exception, e:
        log.info("*** problem setting idea is_active = %s for idea_id = %s" % (b, ideaId))
        log.error(e)
        return False


def addIdeaToProject(db, ideaId, projectId):
    try:
        db.insert('project__idea', idea_id=ideaId, project_id=projectId)

        return True
    except Exception, e:
        log.info("*** problem adding idea to project")
        log.error(e)
        return False


def addInvitedIdeaToProject(db, projectId, userId):
    try:
        sql = """insert into project__idea (project_id, idea_id)
                  select $projectId, inv.invitee_idea_id from project_invite inv
                    inner join idea i on i.idea_id = inv.invitee_idea_id and i.user_id = $userId
                    where project_id = $projectId
                    limit 1"""
        db.query(sql, {'projectId': projectId, 'userId': userId})

        return True
    except Exception, e:
        log.info("*** couldn't add invited idea(s) from user id %s to project %s" % (userId, projectId))
        log.error(e)
        return False


def getMostRecentIdeas(db, limit=100, offset=0):
    data = []
    betterData = []

    sql = """select i.idea_id, i.description as text, u.user_id, u.first_name, u.last_name, u.affiliation, i.submission_type as submitted_by 
            from idea i
            left join user u on u.user_id = i.user_id and u.is_active = 1
            where i.is_active = 1
            order by i.created_datetime desc
            limit $limit offset $offset"""

    try:
        data = list(db.query(sql, {'limit': limit, 'offset': offset}))

        for item in data:
            betterData.append(dict(idea_id=item.idea_id,
                                   text=item.text,
                                   user_id=item.user_id,
                                   name=ideaName(item.first_name, item.last_name, item.affiliation),
                                   submitted_by=str(item.submitted_by)))

    except Exception, e:
        log.info("*** couldn't get most recent ideas")
        log.error(e)

    return betterData


# TODO put this with the rest of the formatting functions
def ideaName(first, last, affiliation=None):
    if (first and last):
        # TODO should use general username formatter
        # return userName(first, last, False)
        return "%s %s." % (first, last[0])
    elif (affiliation):
        return affiliation
    else:
        return None


def toggleVoteIdea(db, ideaId, userId):
    try:
        sql = "select count(*) from idea__user where where idea_id = $ideaId and user_id = $userId)"
        data = list(db.query(sql, {'ideaId': ideaId, 'userId': userId}))
        count = data[0].count
        if count > 0:
            return downvoteIdea(db, ideaId, userId)
        else:
            return upvoteIdea(db, ideaId, userId)
    except Exception, e:
        log.info("*** problem toggling vote on idea")
        log.error(e)
        return False


def upvoteIdea(db, ideaId, userId):
    try:
        sql = "insert into idea__user (idea_id, user_id) VALUES( $ideaId, $userId)"
        db.query(sql, {'ideaId': ideaId, 'userId': userId})
        return True
    except Exception, e:
        log.info("*** problem upvoting idea")
        log.error(e)
        return False


def downvoteIdea(db, ideaId, userId):
    try:
        sql = "delete from idea__user where idea_id = $ideaId and user_id = $userId"
        db.query(sql, {'ideaId': ideaId, 'userId': userId})
        return True
    except Exception, e:
        log.info("*** problem downvoting idea")
        log.error(e)
        return False

def ideamessage(id,
            type,
            message,
            createdDatetime,
            userId,
            name,
            imageId,
            attachmentId=None,
            ideaId=None,
            idea=None,
            ideaSubType=None,
            ideaCreatedDatetime=None,
            attachmentMediaType=None,
            attachmentMediaId=None,
            attachmentTitle=None):
    """
    Construct and return a dictionary consisting of the data related to a
    message, given by the parameters.  This data is usually pulled off of
    several database tables with keys linking back to a message_id.

    NOTE: It is recommended to specify all of these as keyword arguments, not
          positional. If the model changes, the positions of the arguments may
          as well.

    **Return:**

    A ``dict`` with keys:

    - ``message_id`` -- Primary key
    - ``message_type`` -- ``'join'``,  ``'endorsement'``,
      ``'member_comment'``, or ``'admin_comment'``
    - ``file_id`` -- The primary key of the attachment, if any
    - ``owner`` -- The user that owns the message
    - ``body`` -- The content of the message
    - ``created`` -- The creation date
    - ``idea`` -- The idea instance attached to the message, if any

    """
    if (ideaId):
        ideaObj = formattingUtils.smallIdea(ideaId, idea, None, None, ideaSubType)
    else:
        ideaObj = None

    attachmentObj = formattingUtils.smallAttachment(attachmentMediaType,
                                    attachmentMediaId,
                                    attachmentTitle)

    return dict(message_id=id,
                message_type=type,
                file_id=attachmentId,
                owner=formattingUtils.smallUserDisplay(userId, name, imageId),
                body=message,
                created=str(createdDatetime - formattingUtils.timedelta(hours=util.local_utcoffset())),
                idea=ideaObj,
                attachment=attachmentObj,
    )

def addMessage(db, ideaId, message, message_type, userId=None, attachmentId=None):
    """
    Insert a new record into the idea_message table.  Return true if
    successful.  Otherwise, if any exceptions arise, log and return false.

    """
    try:
        # censor behavior
        numFlags = helpers.censor.badwords(db, message)
        isActive = 0 if numFlags == 2 else 1

        db.insert('idea_message', idea_id=ideaId,
                  message=message,
                  user_id=userId,
                  file_id=attachmentId,
                  num_flags=numFlags,
                  is_active=isActive)

        return True;
    except Exception, e:
        log.info("*** problem adding message to idea")
        log.error(e)
        return False


def removeMessage(db, messageId):
    try:
        db.update('idea_message', where="idea_message_id = $messageId", is_active=0,
                  vars={'messageId': messageId})

        return True
    except Exception, e:
        log.info("*** problem removing message  ")
        log.error(e)
        return False


def getMessages(db, ideaId, limit=10, offset=0, filterBy=None):
    """
    Return a list of dictionaries with data representing project messages
    associated with the given projectId.  This data come from the tables
    project_message, user, and idea.

    """
    messages = []

    if (filterBy not in ['member_comment', 'admin_comment', 'join', 'endorsement']):
        filterBy = None

    try:
        sql = """select
                    m.idea_message_id,
                    m.message,
                    m.file_id,
                    m.created_datetime,
                    a.type as attachment_type,
                    a.media_id as attachment_id,
                    a.title as attachment_title,
                    u.user_id,
                    u.first_name,
                    u.last_name,
                    u.affiliation,
                    u.group_membership_bitmask,
                    u.image_id,
                    i.idea_id,
                    i.description as idea_description,
                    i.submission_type as idea_submission_type,
                    i.created_datetime as idea_created_datetime
                from idea_message m
                inner join user u on u.user_id = m.user_id
                left join idea i on i.idea_id = m.idea_id
                left join attachments a on a.id = m.file_id
                where m.project_id = $id and m.is_active = 1
                and ($filterBy is null or m.message_type = $filterBy)
                order by m.created_datetime desc
                limit $limit offset $offset"""
        data = list(db.query(sql, {'id': ideaId, 'limit': limit, 'offset': offset, 'filterBy': filterBy}))

        for item in data:
            messages.append(ideamessage(id=item.idea_message_id,
                                    type=item.message_type,
                                    message=item.message,
                                    attachmentId=item.file_id,
                                    createdDatetime=item.created_datetime,
                                    userId=item.user_id,
                                    name=formattingUtils.userNameDisplay(item.first_name, item.last_name, item.affiliation,
                                                         formattingUtils.isFullLastName(item.group_membership_bitmask)),
                                    imageId=item.image_id,
                                    ideaId=item.idea_id,
                                    idea=item.idea_description,
                                    ideaSubType=item.idea_submission_type,
                                    ideaCreatedDatetime=item.idea_created_datetime,
                                    attachmentMediaType=item.attachment_type,
                                    attachmentMediaId=item.attachment_id,
                                    attachmentTitle=item.attachment_title))
    except Exception, e:
        log.info("*** couldn't get messages for idea %d", ideaId)
        log.error(e)

    return messages
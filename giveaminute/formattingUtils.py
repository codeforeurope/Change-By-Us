import os
import framework.util as util
from datetime import timedelta
from framework.config import Config

# # FORMATTING FUNCTIONS

def userName(first, last, isFullLast=False):
    if (isFullLast):
        return "%s %s" % (first, last)
    else:
        return "%s %s." % (first, last[0])

def userNameDisplay(first, last, affiliation=None, isFullLast=False):
    name = None

    if (first and last):
        name = userName(first, last, isFullLast)

    if (affiliation):
        if (name):
            name = "%s, %s" % (name, affiliation)
        else:
            name = affiliation
    return name
    #return jinja2.Markup(name).unescape()

def isFullLastName(bitmask):
    # if site config does not request to always display full last names, check bitmask if is admin or lead
    features = Config.get('features')
    if features.get('is_users_last_name_displayed') == True:
        return True
    else:
        return (util.getBit(bitmask, 1) or util.getBit(bitmask, 3))

def smallAttachment(media_type, media_id, title):
    """Returns a dictionary representing basic attachment information"""
    if media_type and media_id:
        return dict(type=media_type,
                    id=media_id,
                    title=title,
                    url=getAttachmentUrl(media_type, media_id),
                    small_thumb_url=getAttachmentThumbUrl(media_type, media_id, 'small'),
                    medium_thumb_url=getAttachmentThumbUrl(media_type, media_id, 'medium'),
                    large_thumb_url=getAttachmentThumbUrl(media_type, media_id, 'large'))
    else:
        return None

def smallProject(id, title, description, imageId, numMembers, ownerUserId, ownerFirstName, ownerLastName, ownerImageId):
    return dict(project_id=id,
                title=title,
                description=description,
                image_id=imageId,
                num_members=numMembers,
                owner=smallUser(ownerUserId, ownerFirstName, ownerLastName, ownerImageId))


def message(id,
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
            attachmentTitle=None,
            projectId=None,
            projectTitle=None):
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
    - ``project_id`` -- The primary key of the project that the message is for
    - ``project_title`` -- The title of the project

    """
    if (ideaId):
        ideaObj = smallIdea(ideaId, idea, None, None, ideaSubType)
    else:
        ideaObj = None

    attachmentObj = smallAttachment(attachmentMediaType,
                                    attachmentMediaId,
                                    attachmentTitle)

    return dict(message_id=id,
                message_type=type,
                file_id=attachmentId,
                owner=smallUserDisplay(userId, name, imageId),
                body=message,
                created=str(createdDatetime - timedelta(hours=util.local_utcoffset())),
                idea=ideaObj,
                attachment=attachmentObj,
                project_id=projectId,
                project_title=projectTitle,
    )

def getAttachmentUrl(media_type, media_id):
    """Get the URL to wherever the media is stored."""
    if media_type in ('file', 'image'):
        media_root = Config.get('media').get('root')

        return os.path.join(media_root, media_id)


def getAttachmentThumbFileName(media_type, media_id, size):
    """Get a file name for an image representation of the media."""
    if media_type == 'file':
        return 'generic_file_thumbnail.png'

    elif media_type == 'image':
        return '%s_thumb_%s' % (media_id, size)


def getAttachmentThumbUrl(media_type, media_id, size):
    """
    Get the URL to an image representation of the media. For images, this may be
    used for getting a thumbnail. Specify max width and height in that case.
    Otherwise you'll probably just get a generic file image.

    """
    if media_type == 'file':
        static_root = Config.get('staticfiles').get('root')
        stub_thumb_name = 'generic_file_thumbnail.png'

        return os.path.join(static_root, 'images', stub_thumb_name)

    elif media_type == 'image':
        media_root = Config.get('media').get('root')
        image_thumb_name = getAttachmentThumbFileName(media_type, media_id, size)

        return os.path.join(media_root, image_thumb_name)


def smallUser(id, first, last, image):
    if (id and first and last):
        return dict(u_id=id,
                    image_id=image,
                    name=userName(first, last))
    else:
        return None


def smallUserDisplay(id, fullDisplayName, image=None):
    if (id and fullDisplayName):
        return dict(u_id=id,
                    image_id=image,
                    name=fullDisplayName)
    else:
        return None


def smallIdea(ideaId, description, firstName, lastName, submissionType):
    return dict(idea_id=ideaId,
                text=description,
                f_name=firstName,
                l_name=lastName,
                submitted_by=submissionType)


def endorsementUser(id, first, last, image_id, title, org):
    return dict(u_id=id,
                name="%s %s" % (first, last),
                image_id=image_id,
                title=title,
                organization=org)


def link(id, title, url, imageId):
    return dict(link_id=id, title=title, url=url, image_id=imageId)


def resource(id, title, url, imageId):
    return dict(organization=id, title=title, url=url, image_id=imageId)


def idea(id, description, userId, firstName, lastName, createdDatetime, submissionType, projects_count=0):
    return dict(idea_id=id,
                message=description,
                owner=smallUser(userId, firstName, lastName, None),
                created=str(createdDatetime),
                submission_type=submissionType,
                projects_count=projects_count)


## END FORMATTING FUNCTIONS

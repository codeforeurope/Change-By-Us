"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

"""
Module to handle general messaging, though mostly emailing.
Emailing templates can be found in templates/email.

"""
import helpers.sms
import os, gettext
from framework.emailer import Emailer
from framework.log import log
from framework.config import Config

# # EMAIL FUNCTIONS

# send email to invited users
def emailInvite(email, inviterName, projectId, title, description, message=None):
    """
    Send invitation email.  Using template: project_invite
        
    @type   email: string
    @param  email: Email address to send to
    ...
    
    @rtype: Boolean
    @returns: Whether emailer was successful or not.
    
    """
    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    subject = translations.gettext("You have been invited by %(username)s to join a project on %(sitename)s") % {'username': inviterName, 'sitename': Config.get('site')['name']}
    link = "%sproject/%s" % (Config.get('default_host'), str(projectId))
    template_values = {
        'inviter': inviterName,
        'title': title,
        'description': description,
        'link': link,
        'message': message,
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/project_invite', template_values, suffix='txt')
    html = Emailer.render('email/project_invite', template_values, suffix='html')

    # Send email.
    try:
        return Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                            from_address=emailAccount['from_email'])
    except Exception, e:
        log.info("*** couldn't send invite email")
        log.error(e)
        return False


def emailProjectJoin(email, projectId, title, userId, userName):
    """
    Email project admins when new user joins.  Using template: project_join
        
    @type   email: string
    @param  email: Email address to send to
    ...
    
    @rtype: Boolean
    @returns: Whether emailer was successful or not.
    
    """
    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    defaultUrl = Config.get('default_host')
    subject = translations.gettext("A new member %(membername)s has joined your project %(projectname)s on %(sitename)s") % {'membername': userName, 'projectname': title, 'sitename': Config.get('site')['name'] }
    userLink = "%suseraccount/%s" % (defaultUrl, str(userId))
    memberLink = "%sproject/%s#show,members" % (defaultUrl, str(projectId))
    template_values = {
        'title': title,
        'user_name': userName,
        'user_link': userLink,
        'member_link': memberLink,
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/project_join', template_values, suffix='txt')
    html = Emailer.render('email/project_join', template_values, suffix='html')

    # Send email.
    try:
        return Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                            from_address=emailAccount['from_email'])
    except Exception, e:
        log.info("*** couldn't send join email")
        log.error(e)
        return False


def emailProjectEndorsement(email, title, leaderName):
    """
    Email project admins about endorsements.  Using template: project_endorsement
        
    @type   email: string
    @param  email: Email address to send to
    ...
    
    @rtype: Boolean
    @returns: Whether emailer was successful or not.
    
    """
    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    subject = translations.gettext("%(leader)s endorsed your project!") % {'leader': leaderName}
    template_values = {
        'title': title,
        'leader_name': leaderName,
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/project_endorsement', template_values, suffix='txt')
    html = Emailer.render('email/project_endorsement', template_values, suffix='html')

    # Send email.
    try:
        return Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                            from_address=emailAccount['from_email'])
    except Exception, e:
        log.info("*** couldn't send endorsement email")
        log.error(e)
        return False


def emailResourceNotification(email, projectId, title, description, resourceName):
    """
    Email resource contacts on resource add.  Using template: resource_notification
        
    @type   email: string
    @param  email: Email address to send to
    ...
    
    @rtype: Boolean
    @returns: Whether emailer was successful or not.
    
    """
    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    subject = translations.gettext("A project on %(sitename)s has added %(resourcename)s as a resource") % {'sitename': Config.get('site')['name'], 'resourcename': resourceName}
    link = "%sproject/%s" % (Config.get('default_host'), str(projectId))
    template_values = {
        'title': title,
        'description': description,
        'resource_name': resourceName,
        'link': link,
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/resource_notification', template_values, suffix='txt')
    html = Emailer.render('email/resource_notification', template_values, suffix='html')

    # If dev, don't email resources
    if (Config.get('dev')):
        log.info("*** body = %s" % body)
        return True

    # Send email.
    try:
        return Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                            from_address=emailAccount['from_email'])
    except Exception, e:
        log.info("*** couldn't send resource notification email")
        log.error(e)
        return False


def emailResourceApproval(email, title):
    """
    Email resource owner on approval.  Using template: resource_approval
        
    @type   email: string
    @param  email: Email address to send to
    ...
    
    @rtype: Boolean
    @returns: Whether emailer was successful or not.
    
    """
    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    subject = translations.gettext("Your resource has been approved")
    template_values = {
        'link': Config.get('default_host'),
        'title': title,
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/resource_approval', template_values, suffix='txt')
    html = Emailer.render('email/resource_approval', template_values, suffix='html')

    # Send email.
    try:
        return Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                            from_address=emailAccount['from_email'])
    except Exception, e:
        log.info("*** couldn't send resource approval email")
        log.error(e)
        return False


def emailAccountDeactivation(email):
    """
    Email deleted users.  Using template: account_deactivation
        
    @type   email: string
    @param  email: Email address to send to
    ...
    
    @rtype: Boolean
    @returns: Whether emailer was successful or not.
    
    """

    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    subject = translations.gettext("Your account has been deactivated")
    link = "%stou" % Config.get('default_host')
    template_values = {
        'link': link,
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/account_deactivation', template_values, suffix='txt')
    html = Emailer.render('email/account_deactivation', template_values, suffix='html')

    # Send email.
    try:
        return Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                            from_address=emailAccount['from_email'])
    except Exception, e:
        log.info("*** couldn't send account deactivation email")
        log.error(e)
        return False


def emailTempPassword(email, password):
    """
    Email temporary password.  Using template: forgot_password
        
    @type   email: string
    @param  email: Email address to send to
    ...
    
    @rtype: Boolean
    @returns: Whether emailer was successful or not.
    
    """
    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    subject = translations.gettext("Your password has been reset")
    link = "%slogin" % Config.get('default_host')
    template_values = {
        'password': password,
        'link': link,
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/forgot_password', template_values, suffix='txt')
    html = Emailer.render('email/forgot_password', template_values, suffix='html')

    # Send email.
    try:
        return Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                            from_address=emailAccount['from_email'])
    except Exception, e:
        log.info("*** couldn't send forgot password email")
        log.error(e)
        return False


def directMessageUser(db, toUserId, toName, toEmail, fromUserId, fromName, message):
    """
    Email user about direct message.  Using template: direct_message
        
    @type   email: string
    @param  email: Email address to send to
    ...
    
    @rtype: Boolean
    @returns: Whether emailer was successful or not.
    
    """
    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    #email = "%s <%s>" % (toName, toEmail)
    email = toEmail
    subject = translations.gettext("%(sitename)s message from %(username)s") % {'sitename': Config.get('site')['name'], 'username': fromName}
    link = "%suseraccount/%s" % (Config.get('default_host'), fromUserId)
    template_values = {
        'name': fromName,
        'message': message,
        'link': link,
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/direct_message', template_values, suffix='txt')
    html = Emailer.render('email/direct_message', template_values, suffix='html')

    # Send email.
    try:
        isSent = Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                              from_address=emailAccount['from_email'])

        if (isSent):
            db.insert('direct_message', message=message, to_user_id=toUserId, from_user_id=fromUserId)
            return True
        else:
            log.info("*** couldn't log direct message")
            # Not sure if best to return False
            return False

    except Exception, e:
        log.info("*** couldn't send direct message email")
        log.error(e)
        return False


def emailUnauthenticatedUser(email, authGuid):
    """
    Send unauthenticated user a link to authenticate.  Using 
    template: auth_user
        
    @type   email: string
    @param  email: Email address to send to
    
    @rtype: *
    @returns: Emailer send response.
    
    """
    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    subject = translations.gettext('Please authenticate your account on %(sitename)s') % {'sitename': Config.get('site')['name']}
    link = "%sjoin/auth/%s" % (Config.get('default_host'), authGuid)
    template_values = {
        'link': link,
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/auth_user', template_values, suffix='txt')
    html = Emailer.render('email/auth_user', template_values, suffix='html')

    # Send email.            
    try:
        return Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                            from_address=emailAccount['from_email'])
    except Exception, e:
        log.info("*** couldn't send authenticate user email")
        log.error(e)
        return False


def emailIdeaConfirmation(email, responseEmail, locationId):
    """
    Email upon idea submission.  Using template: idea_confirmation
        
    @type   email: string
    @param  email: Email address to send to
    ...
    
    @rtype: Boolean
    @returns: Whether emailer was successful or not.
    
    """

    #Get translations
    translations = get_gettext_translation(get_default_language())

    # Create values for template.
    emailAccount = Config.get('email')
    host = Config.get('default_host')
    subject = translations.gettext('Thanks for submitting an idea to %(sitename)s!') % {'sitename': Config.get('site')['name']}
    searchLink = "%ssearch?location_id=%s" % (host, locationId)
    createLink = "%screate" % host
    template_values = {
        'search_link': searchLink,
        'create_link': createLink,
        'response_email': emailAccount['from_email'],
        'config': Config.get_all()
    }

    # Render email body.
    body = Emailer.render('email/idea_confirmation', template_values, suffix='txt')
    html = Emailer.render('email/idea_confirmation', template_values, suffix='html')

    # Send email.
    try:
        return Emailer.send(email, subject, body, html, from_name=emailAccount['from_name'],
                            from_address=emailAccount['from_email'])
    except Exception, e:
        log.info("*** couldn't send authenticate user email")
        log.error(e)
        return False


### SMS FUNCTIONS

# add phone number to table of stopped numbers
def stopSMS(db, phone):
    try:
        db.insert('sms_stopped_phone', phone=phone)
        return True
    except Exception, e:
        log.info("*** couldn't stop messages to phone number %s.  Number may already be in database." % phone)
        log.error(e)
        return False


def isPhoneStopped(db, phone):
    try:
        sql = "select phone from sms_stopped_phone where phone = $phone limit 1";
        data = list(db.query(sql, {'phone': phone}))

        return len(data) > 0
    except Exception, e:
        log.info("*** couldn't get sms stopped value for %s" % phone)
        log.error(e)

        # in this case, we err on NOT sending messages and thus return True
        return True


def sendSMSConfirmation(db, phone):
    log.info("*** sending confirmation to %s" % phone)

    if (not isPhoneStopped(db, phone)):
        message = "Thanks for adding your idea to changeby.us Visit %smobile to browse and join projects related to your idea." % Config.get('default_host')

        return helpers.sms.send(phone, message)
    else:
        return False


def sendSMSInvite(db, phone, projectId):
    log.info("*** sending invite to %s" % phone)

    try:
        if (not isPhoneStopped(db, phone)):
            link = "%sproject/%s" % (Config.get('default_host'), str(projectId))
            message = "You've been invited to a project on changeby.us. Visit %s to see the project. Reply 'STOP' to stop changeby.us messages." % link
            return helpers.sms.send(phone, message)
        else:
            return False
    except Exception, e:
        log.info("*** something failed in sending sms invite")
        log.error(e)
        return False    


# Localization functions
def get_gettext_translation(locale_id):
    """
    Returns the translation object for the specified locale.
    """
    # i18n directory.
    locale_dir = get_i18n_dir()

    # Look in the translaton for the locale_id in locale_dir. Fallback to the
    # default text if not found.
    return gettext.translation('messages', locale_dir, [locale_id], fallback=True)


def get_default_language():
    """
    Gets the language that has been set by in the configuration file.

    """
    lang = ""
    try:
        lang = Config.get('default_lang')
    except:
        pass
    return lang

def get_i18n_dir():
    """Return the path to the directory with the locale files"""
    cur_dir = os.path.abspath(os.path.dirname(__file__))

    # i18n directory.
    locale_dir = os.path.join(cur_dir, '..', 'i18n')
    return locale_dir
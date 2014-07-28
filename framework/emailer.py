"""
    :copyright: (c) 2011 Local Projects, all rights reserved
    :license: Affero GNU GPL v3, see LICENSE for more details.
"""

"""
Emailing utility.  Emailing is ultimately handled through webpy.

"""
import smtplib
import os
import gettext
import helpers.custom_filters as custom_filters
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import Encoders
from lib.web.contrib.template import render_jinja
from lib.jinja2.exceptions import TemplateNotFound
import jinja2
from framework.log import log
from framework.config import Config
# from framework.controller import *
import lib.web.utils as webpyutils
import lib.web.webapi as webapi


class Emailer():
    """
    Email class for handling emailing for the application.
    """

    @classmethod
    def send_from_template(cls, addresses, subject, template_name, template_values=None, attachment=None,
                           from_name=None, from_address=None, **kwags):
        """
        Create HTML and text emails from template, then send.
        
        """
        log.info("Emailer.send_from_template (%s)" % template_name)

        # Render email template as HTML.
        try:
            html = cls.render(template_name, template_values)
        except TemplateNotFound:
            log.warning("HTML template not found.")
            html = None

        try:
            text = cls.render(template_name, template_values, suffix="txt")
        except TemplateNotFound:
            log.warning("Text template not found.")
            text = None

        log.debug(html)
        return cls.send(addresses, subject, text, html, attachment, from_name, from_address)

    @classmethod
    def send(cls, addresses, subject, text, html=None, attachment=None, from_name=None, from_address=None, **kwargs):
        """
        Send email to recipients.
        
        """
        log.info("Emailer.send [%s] [%s]" % (addresses, subject))
        if isinstance(addresses, basestring):
            addresses = [r.strip() for r in addresses.split(',')]

        try:
            if webapi.config.get('email_engine') == 'aws':
                try:
                    send_email_via_ses(addresses, subject, text, html, attachment, from_name, from_address, **kwargs)
                except:
                    send_email_via_smtp(addresses, subject, text, html, attachment, from_name, from_address, **kwargs)
            else:
                send_email_via_smtp(addresses, subject, text, html, attachment, from_name, from_address, **kwargs)
        except Exception, e:
            log.error("Could not send email due to: %s" % e)
            return False

        return True


    # if html:
    #            # SR: Theres' a problem with gmail and multi-part messages. So may as well just send html
    #            # msg = MIMEMultipart('alternative')
    #            # msg.attach(MIMEText(html, 'html'))
    #            # msg.attach(MIMEText(text, 'plain'))
    #            msg = MIMEText(html, 'html')
    #        else:
    #            msg = MIMEText(text, 'plain')
    #
    #        if attachment:
    #            tmpmsg = msg
    #            msg = MIMEMultipart()
    #            msg.attach(tmpmsg)
    #            msg.attach(MIMEText("\n\n", 'plain')) # helps to space the attachment from the body of the message
    #            log.info("--> adding attachment")
    #            part = MIMEBase('application', 'octet-stream')
    #            part.set_payload(open(attachment, 'rb').read())
    #            Encoders.encode_base64(part)
    #            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attachment))
    #            msg.attach(part)
    #
    #        sender = from_name + "<" + from_address + ">"
    #
    #        msg['Subject'] = subject
    #        msg['From'] = sender
    #        msg['To'] = ", ".join(addresses)
    #
    #        try:
    #            # The use_msg_directly parameter should be set to True if we're adding message headers. This is the case
    #            # with MIMEText() usage. If we send text directly (ie without MIMEText()) then use_msg_directly should be False
    #            webpyutils.sendmail(from_address=sender, to_address=addresses, subject=subject, message=msg, attachment=attachment, use_msg_directly=True, **kwargs)
    #
    #        except Exception, e:
    #            log.error("Could not send email (%s)" % e)
    #
    #            return False
    #        return True


    @classmethod
    def render(cls, template_name, template_values=None, suffix="html"):
        if template_values is None:
            template_values = {}
        template_values['template_name'] = template_name
        renderer = render_jinja(os.path.dirname(__file__) + '/../templates/',
                                extensions=['jinja2.ext.i18n',
                                            'jinja2.ext.with_', ])
        renderer._lookup.filters.update(custom_filters.filters)

        # Install the translation
        translation = get_gettext_translation(get_default_language())
        renderer._lookup.install_gettext_translations(translation)

        return (renderer[template_name + "." + suffix](template_values)).encode('utf-8')


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

# Local methods
def listify(x):
    if not isinstance(x, list):
        return [webpyutils.safestr(x)]
    else:
        return [webpyutils.safestr(a) for a in x]


def send_email_via_smtp(addresses, subject, text, html=None, attachment=None, from_name=None, from_address=None,
                        **kwargs):
    """
    Send email via SMTP
    """
    server = webapi.config.get('smtp_server')
    port = webapi.config.get('smtp_port', 0)
    username = webapi.config.get('smtp_username')
    password = webapi.config.get('smtp_password')
    debug_level = webapi.config.get('smtp_debuglevel', None)
    starttls = webapi.config.get('smtp_starttls', False)

    import smtplib

    smtpserver = smtplib.SMTP(server, port)

    if debug_level:
        smtpserver.set_debuglevel(debug_level)

    if starttls:
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()

    if username and password:
        smtpserver.login(username, password)

    if html and text:
        message = MIMEMultipart('alternative')
        message.attach(MIMEText(html, 'html'))
        message.attach(MIMEText(text, 'plain'))
    elif html:
        message = MIMEText(html, 'html')
    else:
        message = MIMEText(text, 'plain')

    if attachment:
        tmpmessage = message
        message = MIMEMultipart()
        message.attach(tmpmessage)
        message.attach(MIMEText("\n\n", 'plain'))  # helps to space the attachment from the body of the message
        log.info("--> adding attachment")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attachment, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attachment))
        message.attach(part)

    sender = from_name + "<" + from_address + ">"
    cc = listify(kwargs.get('cc', []))
    bcc = listify(kwargs.get('bcc', []))

    message['Subject'] = subject
    message['From'] = sender
    message['To'] = ", ".join(addresses)
    message['Cc'] = ','.join(cc)
    message['Bcc'] = ','.join(bcc)

    smtpserver.sendmail(sender, addresses, message.as_string())
    smtpserver.quit()


def send_email_via_ses(addresses, subject, text, html=None, attachment=None, from_name=None, from_address=None,
                       **kwargs):
    """
    BCC is in kwargs
    If SES has any error, the request will be passed back to the caller and domino down to SMTP 
    """
    import boto.ses

    try:
        sesConn = boto.ses.SESConnection(aws_access_key_id=webapi.config.get('aws_access_key_id'),
                                         aws_secret_access_key=webapi.config.get('aws_secret_access_key'))
    except Exception, e:
        raise

    cc = listify(kwargs.get('cc', []))
    bcc = listify(kwargs.get('bcc', []))
    sender = from_name + "<" + from_address + ">"

    # First send emails without attachments and not multipart
    if (text and not html and not attachment) or \
            (html and not text and not attachment):
        return sesConn.send_email(sender, subject,
                                  text or html,
                                  addresses, cc, bcc,
                                  format='text' if text else 'html')
    else:
        if not attachment:
            message = MIMEMultipart('alternative')

            message['Subject'] = subject
            message['From'] = sender
            if isinstance(addresses, (list, tuple)):
                message['To'] = ','.join(addresses)
            else:
                message['To'] = addresses
            message['Cc'] = ','.join(cc)
            message['Bcc'] = ','.join(bcc)

            message.attach(MIMEText(text, 'plain'))
            message.attach(MIMEText(html, 'html'))
        else:
            # This raise should fall back into SMTP
            raise NotImplementedError, 'SES does not currently allow ' + \
                                       'messages with attachments.'

    # send_raw does not seem to support bcc or cc,
    # So let's force all our emails to go out as HTML
    return sesConn.send_email(sender, subject,
                              text or html,
                              addresses, cc, bcc,
                              format='html')

    # TODO: Fix the send_raw_email() so it support bcc and cc correctly!
    # return sesConn.send_raw_email(sender, message.as_string(), destinations=addresses)                                           

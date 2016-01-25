import os, sys
import smtpmail

import config
import utils
import doc
import ui

class SentDoc (doc.Doc):

  def __init__ (self, request, language, subject, message, referer=None):
    doc.Doc.__init__ (self, request, language, use_fs_cache=False)
    self.subject = subject or u"<No subject>"
    self.message = message or u"<No message>"
    self.n_secs_timeout = 10
    self.redirect_to_url = referer or self.url (u"/%s/" % language)

  def title (self):
    return self.translate ("contact_message_sent")

  def header_plugin (self):
    return '<meta http-equiv="refresh" content="%d;URL=%s">' % (self.n_secs_timeout, self.redirect_to_url)

  def body (self):
    return u"""
<p>%s</p>
<hr>
<b><pre>%s</pre></b>
<pre>%s</pre>
""" % (self.translate ("contact_confirmed"), self.subject, self.message)

class ContactDoc (doc.Doc):

  def __init__ (self, request, language):
    doc.Doc.__init__ (self, request, language, use_fs_cache=False)

  def title (self):
    return self.translate ("contact_title")

  def form (self):
    yield u'<form method="POST" action="%s">' % self.url ("/%s/intouch/send" % self.language)
    yield u'<p><label>%s </label> <input type="text" size="60" name="name" value="">&nbsp;' % self.translate ("contact_your_name")
    yield u'<label>%s </label> <input type="text" size="60" name="email" value=""></p>' % self.translate ("contact_your_email")
    yield u'<p><label>%s </label> <input type="text" size="130" name="email-subject" value="%s">' % (self.translate ("contact_subject"), self.request.form.get ("subject", "").decode ("iso_8859_1"))
    yield u'<p><label>%s</label></p>' % self.translate ("contact_message")
    yield u'<input type="hidden" value=%s" name="referer">' % self.request.environ.get ("HTTP_REFERER", "/%s/" % self.language)
    yield u'<textarea rows="20" cols="120" name="message"></textarea>'
    yield u'<p><input type="submit" value="%s"></p>' % self.translate ("contact_send_button")
    yield u'</form>'

  def body (self):
    html = []
    html.append('''<p><b>Note:</b> This message will go to the administrator of this website (<a href="/">weekdaymasses.org.uk</a>), NOT to the parish.<br/>'''
    '''So if you require baptism or marriage certificates or for more information regarding a specific parish,<br/>'''
    '''please email the parish directly.</p>''')
    ##html.append ('''<p>We regret that the contact form is temporarily unavailable. In the meantime, please contact <a href="mailto:info@weekdaymasses.org.uk">info@weekdaymasses.org.uk</a></p>''')
    html.extend (self.form ())
    return "\n".join (html)

class ContactUI (ui.UI):

  _q_exports = ["_q_index", "send"]

  def __init__ (self, language):
    ui.UI.__init__ (self, language)

  def send (self, request):
    form = request.form
    name = form.get ("name", u"Anonymous").decode (config.INPUT_ENCODING)
    email = form.get ("email", u"anon@weekdaymasses.org.uk").decode (config.INPUT_ENCODING)
    message = form.get ("message", u"").decode (config.INPUT_ENCODING).strip ()
    subject = form.get ("email-subject", "")
    referer = form.get ("referer", "/%s/" % self.language)
    if isinstance (subject, list):
      subject = u" ".join (s.decode (config.INPUT_ENCODING).strip () for s in subject)
    else:
      subject = subject.decode (config.INPUT_ENCODING).strip ()
    if not message:
      return request.redirect ("/%s/" % self.language)
    if not subject:
      if len (message) < 100:
        subject = message
      else:
        subject = message[:100] + u"..."
    session = smtpmail.smtp_session ("smtp.webfaction.com", "tgolden_weekdaymasses", "Weetabix")
    smtpmail.send (
      recipients=[config.CONTACT_EMAIL],
      subject=u"<<<" + subject,
      message_text=message,
      attachments=[],
      ostensible_sender=u"%s <%s>" % (name, email),
      session=session
    )
    return SentDoc (request, self.language, subject, message, referer)

  def _q_index (self, request):
    return ContactDoc (request, self.language)
  __call__ = _q_index

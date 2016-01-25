"""quixote.errors

Exception classes used by Quixote
"""
from quixote.html import htmltext, htmlescape


class PublishError(Exception):
    """PublishError exceptions are raised due to some problem with the
    data provided by the client and are raised during the publishing
    process.  Quixote will abort the current request and return an error
    page to the client.

    public_msg should be a user-readable message that reveals no
    inner workings of your application; it will always be shown.

    private_msg will only be shown if the config option SECURE_ERRORS is
    false; Quixote uses this to give you more detail about why the error
    occurred.  You might want to use it for similar, application-specific
    information.  (SECURE_ERRORS should always be true in a production
    environment, since these details about the inner workings of your
    application could conceivably be useful to attackers.)

    The formatting done by the Quixote versions of these exceptions is
    very simple.  Applications will probably wish to raise application
    specific subclasses which do more sophisticated formatting or provide
    a _q_except handler to format the exception.

    """

    status_code = 400 # bad request
    title = "Publishing error"
    description = "no description"

    def __init__(self, public_msg=None, private_msg=None):
        self.public_msg = public_msg
        self.private_msg = private_msg # cleared if SECURE_ERRORS is true

    def __str__(self):
        return self.private_msg or self.public_msg or "???"

    def format(self, request):
        msg = htmlescape(self.title)
        if not isinstance(self.title, htmltext):
            msg = str(msg) # for backwards compatibility
        if self.public_msg:
            msg = msg + ": " + self.public_msg
        if self.private_msg:
            msg = msg + ": " + self.private_msg
        return msg


class TraversalError(PublishError):
    """
    Raised when a client attempts to access a resource that does not
    exist or is otherwise unavailable to them (eg. a Python function
    not listed in its module's _q_exports list).

    path should be the path to the requested resource; if not
    supplied, the current request object will be fetched and its
    get_path() method called.
    """

    status_code = 404 # not found
    title = "Page not found"
    description = ("The requested link does not exist on this site.  If "
                   "you arrived here by following a link from an external "
                   "page, please inform that page's maintainer.")

    def __init__(self, public_msg=None, private_msg=None, path=None):
        PublishError.__init__(self, public_msg, private_msg)
        if path is None:
            import quixote
            path = quixote.get_request().get_path()
        self.path = path

    def format(self, request):
        msg = htmlescape(self.title) + ": " + self.path
        if not isinstance(self.title, htmltext):
            msg = str(msg) # for backwards compatibility
        if self.public_msg:
            msg = msg + ": " + self.public_msg
        if self.private_msg:
            msg = msg + ": " + self.private_msg
        return msg

class RequestError(PublishError):
    """
    Raised when Quixote is unable to parse an HTTP request (or its CGI
    representation).  This is a lower-level error than QueryError -- it
    either means that Quixote is not smart enough to handle the request
    being passed to it, or the user-agent is broken and/or malicious.
    """
    status_code = 400
    title = "Invalid request"
    description = "Unable to parse HTTP request."


class QueryError(PublishError):
    """Should be raised if bad data was provided in the query part of a
    URL or in the content of a POST request.  What constitutes bad data is
    solely application dependent (eg: letters in a form field when the
    application expects a number).
    """

    status_code = 400
    title = "Invalid query"
    description = ("An error occurred while handling your request.  The "
                   "query data provided as part of the request is invalid.")



class AccessError(PublishError):
    """Should be raised if the client does not have access to the
    requested resource.  Usually applications will raise this error from
    an _q_access method.
    """

    status_code = 403
    title = "Access denied"
    description = ("An error occurred while handling your request.  "
                   "Access to the requested resource was not permitted.")



class SessionError(PublishError):
    """Raised when a session cookie has an invalid session ID.  This
    could be either a broken/malicious client or an expired session.
    """

    status_code = 400
    title = "Expired or invalid session"
    description = ("Your session is invalid or has expired.  "
                   "Please reload this page to start a new session.")

    def __init__(self, public_msg=None, private_msg=None, session_id=None):
        PublishError.__init__(self, public_msg, private_msg)
        self.session_id = session_id

    def format(self, request):
        from quixote import get_session_manager
        get_session_manager().revoke_session_cookie(request)
        msg = PublishError.format(self, request)
        if self.session_id:
            msg = msg + ": " + self.session_id
        return msg


def default_exception_handler(request, exc):
    """(request : HTTPRequest, exc : PublishError) -> string

    Format a PublishError exception as a web page.  This is the default
    handler called if no '_q_exception_handler' function was found while
    traversing the path.
    """
    return htmltext("""\
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN"
        "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html>
      <head><title>Error: %s</title></head>
      <body>
      <p>%s</p>
      <p>%s</p>
      </body>
    </html>
    """) % (exc.title, exc.description, exc.format(request))

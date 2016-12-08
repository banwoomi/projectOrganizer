import sys
from datetime import datetime, timedelta
from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.urlresolvers import RegexURLResolver
from django.shortcuts import redirect

from pjo.util.PjoUtil import CommonUtil

class AutoLogout:

    def process_request(self, request):
        
        member_id = request.session.get("member_id")
        if member_id is None:
            # Can't log out if not logged in
            return
        else:

            try:
                if datetime.now() - request.session['last_touch'] > timedelta(0, settings.AUTO_LOGOUT_DELAY * 60, 0):
                     
                    # delete session
                    CommonUtil().delSession(request)
            
                    # redirect to sign in page
                    return redirect(reverse("pjo:signinForm"))
                     
            except Exception:
                # delete session
                CommonUtil().delSession(request)
                 
            request.session['last_touch'] = datetime.now()
             
            return
    
    


class ExceptionHandler(object):

    print "@@@@@@@@@@@@@@@@@@@@@@@@@@"
    def process_exception(self, request, exception):
        print "@@@@@@@@@@@@@@@@@@@@@@@@@@ process_exception"
        # Get the exception info now, in case another exception is thrown later.
        if isinstance(exception, http.Http404):
            print "#############1"
            return self.handle_404(request, exception)
        else:
            print "#############2"
            return self.handle_500(request, exception)


    def handle_404(self, request, exception):
        print "@@@@@@@@@@@@@@@@@@@@@@@@@@ handle_404"
        if settings.DEBUG:
            print "#############3"
            from django.views import debug
            return debug.technical_404_response(request, exception)
        else:
            print "#############4"
            callback, param_dict = resolver(request).resolve404()
            return callback(request, **param_dict)


    def handle_500(self, request, exception):
        print "@@@@@@@@@@@@@@@@@@@@@@@@@@ handle_500"
        exc_info = sys.exc_info()
        if settings.DEBUG:
            print "#############5"
            return self.debug_500_response(request, exception, exc_info)
        else:
            print "#############6"
            self.log_exception(request, exception, exc_info)
            return self.production_500_response(request, exception, exc_info)


    def debug_500_response(self, request, exception, exc_info):
        print "@@@@@@@@@@@@@@@@@@@@@@@@@@ debug_500_response"
        print "#############7"
        from django.views import debug
        return debug.technical_500_response(request, *exc_info)


    def production_500_response(self, request, exception, exc_info):
        print "@@@@@@@@@@@@@@@@@@@@@@@@@@ production_500_response"
        '''Return an HttpResponse that displays a friendly error message.'''
        print "#############8"
        
        callback, param_dict = resolver(request).resolve500()
        return callback(request, **param_dict)


#     def exception_email(self, request, exc_info):
#         subject = 'Error (%s IP): %s' % ((request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS and 'internal' or 'EXTERNAL'), request.path)
#         try:
#             request_repr = repr(request)
#         except:
#             request_repr = "Request repr() unavailable"
#         message = "%s\n\n%s" % (_get_traceback(exc_info), request_repr)
#         return subject, message


    def log_exception(self, request, exception, exc_info):
        print "@@@@@@@@@@@@@@@@@@@@@@@@@@ log_exception"
#         subject, message = self.exception_email(request, exc_info)
#         mail_admins(subject, message, fail_silently=True)
        pass



def resolver(request):
    print "@@@@@@@@@@@@@@@@@@@@@@@@@@ resolver"
    """
    Returns a RegexURLResolver for the request's urlconf.

    If the request does not have a urlconf object, then the default of
    settings.ROOT_URLCONF is used.
    """
    
    urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
    return RegexURLResolver(r'^/', urlconf)

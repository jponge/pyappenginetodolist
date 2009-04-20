import wsgiref.handlers

import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class TodoEntry(db.Model):
    user = db.UserProperty()
    text = db.StringProperty()

class TodoHandler(webapp.RequestHandler):
    
    def authenticate(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            return user
        
    def get(self):
        user = self.authenticate()
        if not user:
            return
            
        if self.request.get('delkey'):
            entry = db.get(self.request.get('delkey'))
            if entry:
                entry.delete()
        
        entries = db.GqlQuery("SELECT * FROM TodoEntry WHERE user = :userid", userid=user)

        values = {
            'userid': user.nickname(),
            'entries': entries,
            'logout_url': users.create_logout_url(self.request.uri)
        }
        
        tpl = os.path.join(os.path.dirname(__file__), 'todo.html')
        self.response.out.write(template.render(tpl, values))
        
    def post(self):
        user = users.get_current_user()
        if not user:
            return
                
        textdata = self.request.get('textdata')
        entry = TodoEntry(user=user,
                          text=textdata)
        if textdata:
            entry.put()
        
        self.redirect('/')


def main():
    mappings = [
        ('/', TodoHandler),
        ('/todo', TodoHandler),
        ('/add', TodoHandler)
    ]
    application = webapp.WSGIApplication(mappings, debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
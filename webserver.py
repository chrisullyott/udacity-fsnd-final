import cgi
import re
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import update
from restaurants import Base, Restaurant, MenuItem


class webServerHandler(BaseHTTPRequestHandler):

    def getRestaurants(self):
      engine = create_engine('sqlite:///restaurantmenu.db')
      Base.metadata.bind=engine
      DBSession = sessionmaker(bind = engine)
      session = DBSession()

      restaurant_query = session.query(Restaurant).all()
      return restaurant_query

    def getRestaurantNameById(self, restaurantId):
      engine = create_engine('sqlite:///restaurantmenu.db')
      Base.metadata.bind=engine
      DBSession = sessionmaker(bind = engine)
      session = DBSession()

      query = session.query(Restaurant).filter_by(id=restaurantId).one()
      return str(query.name)

    def addRestaurant(self, restaurantName):
      engine = create_engine('sqlite:///restaurantmenu.db')
      Base.metadata.bind=engine
      DBSession = sessionmaker(bind = engine)
      session = DBSession()

      newRestaurant = Restaurant(name = restaurantName)

      session.add(newRestaurant)
      session.commit()
      return True

    def editRestaurantName(self, restaurantId, newRestaurantName):
      engine = create_engine('sqlite:///restaurantmenu.db')
      Base.metadata.bind=engine
      DBSession = sessionmaker(bind = engine)
      session = DBSession()

      session.query(Restaurant).filter_by(id=restaurantId).update({"name":newRestaurantName})
      session.commit()
      return True

    def deleteRestaurant(self, restaurantId):
      engine = create_engine('sqlite:///restaurantmenu.db')
      Base.metadata.bind=engine
      DBSession = sessionmaker(bind = engine)
      session = DBSession()

      session.query(Restaurant).filter_by(id=restaurantId).delete()
      session.commit()
      return True

    def getStyles(self):
      styles = ""
      styles += "<link href='https://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css'>"
      styles += "<style>"
      styles += "body{font-family:'Open Sans';line-height:normal;padding:1%}"
      styles += "div{margin:50px 0}"
      styles += "</style>"
      return styles

    def splitSelect(self, string, delimiter, index):
      string = string.strip(delimiter)
      array = string.split(delimiter)
      try:
        return array[index]
      except:
        return False

    def do_GET(self):
        try:

            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html>"
                output += self.getStyles()
                output += "<body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                #print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html>"
                output += self.getStyles()
                output += "<body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                #print output
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html>"
                output += self.getStyles()
                output += "<body>"
                output += "<h1>Restaurants</h1>"
                output += "<p><a href='/restaurants/new'>Add new restaurant</a></p>"

                restaurants = self.getRestaurants()
                for r in restaurants:
                  output += "<div>"
                  output += "<h3>"+ r.name +"</h3>"
                  output += "<ul class='actions'>"
                  output += "<li><a href='/restaurants/"+str(r.id)+"/edit'>Edit</a></li>"
                  output += "<li><a href='/restaurants/"+str(r.id)+"/delete'>Delete</a></li>"
                  output += "</ul>"
                  output += "</div>"

                output += "</body></html>"
                self.wfile.write(output)
                #print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html>"
                output += self.getStyles()
                output += "<body>"
                output += "<h1>Add restaurant</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Name:</h2><input name="restaurantName" type="text"><input type="submit" value="Submit"> </form>'''
                output += "<p><a href='/restaurants'>&larr; back</a></p>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if re.match('/restaurants/\d{1,}\/edit', self.path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurantId = int(self.splitSelect(self.path, '/', 1))
                restaurantName = self.getRestaurantNameById(restaurantId)
                output = ""
                output += "<html>"
                output += self.getStyles()
                output += "<body>"
                output += "<h1>Edit restaurant \""+restaurantName+"\"</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='"+self.path+"'>"
                output += "<h2>New name:</h2>"
                output += "<input type='text' name='newRestaurantName' placeholder='"+restaurantName+"'>"
                output += "<input type='hidden' name='restaurantId' value='"+str(restaurantId)+"'>"
                output += "<input type='submit' value='Rename'>"
                output += "</form>"
                output += "<p><a href='/restaurants'>&larr; back</a></p>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if re.match('/restaurants/\d{1,}\/delete', self.path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurantId = int(self.splitSelect(self.path, '/', 1))
                restaurantName = self.getRestaurantNameById(restaurantId)
                output = ""
                output += "<html>"
                output += self.getStyles()
                output += "<body>"
                output += "<h1>Delete \""+restaurantName+"\"</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='"+self.path+"'>"
                output += "<h2>Really delete this restaurant?</h2>"
                output += "<input type='hidden' name='restaurantId' value='"+str(restaurantId)+"'>"
                output += "<input type='submit' value='Confirm'>"
                output += "</form>"
                output += "<p><a href='/restaurants'>&larr; back</a></p>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/test"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html>"
                output += self.getStyles()
                output += "<body>"
                output += "<h1>"+self.path+"</h1>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
          if self.path.endswith("/restaurants/new"):
              self.send_response(301)
              self.send_header('Content-type', 'text/html')
              self.end_headers()
              ctype, pdict = cgi.parse_header(
                  self.headers.getheader('content-type'))
              if ctype == 'multipart/form-data':
                  fields = cgi.parse_multipart(self.rfile, pdict)
                  restaurantName = fields.get('restaurantName')[0]
                  try:
                    self.addRestaurant(restaurantName)
                  except Exception, e:
                    print e
              output = ""
              output += "<html>"
              output += self.getStyles()
              output += "<body>"
              output += "<h2>You just added:</h2>"
              output += "<h1> \"%s\" </h1>" % restaurantName
              output += "<p><a href='/restaurants'>&larr; back</a></p>"
              output += "</body></html>"
              self.wfile.write(output)
              #print output

          if re.match('/restaurants/\d{1,}\/edit', self.path):
              self.send_response(301)
              self.send_header('Content-type', 'text/html')
              self.end_headers()
              ctype, pdict = cgi.parse_header(
                  self.headers.getheader('content-type'))
              if ctype == 'multipart/form-data':
                  fields = cgi.parse_multipart(self.rfile, pdict)
                  restaurantId = int(fields.get('restaurantId')[0])
                  newRestaurantName = fields.get('newRestaurantName')[0]
                  try:
                    self.editRestaurantName(restaurantId, newRestaurantName)
                  except Exception, e:
                    print e
              output = ""
              output += "<html>"
              output += self.getStyles()
              output += "<body>"
              output += "<h2>Name changed to:</h2>"
              output += "<h1> \"%s\" </h1>" % newRestaurantName
              output += "<p><a href='/restaurants'>&larr; back to all</a></p>"
              output += "</body></html>"
              self.wfile.write(output)
              #print output

          if re.match('/restaurants/\d{1,}\/delete', self.path):
              self.send_response(301)
              self.send_header('Content-type', 'text/html')
              self.end_headers()
              ctype, pdict = cgi.parse_header(
                  self.headers.getheader('content-type'))
              if ctype == 'multipart/form-data':
                  fields = cgi.parse_multipart(self.rfile, pdict)
                  restaurantId = int(fields.get('restaurantId')[0])
                  try:
                    self.deleteRestaurant(restaurantId)
                  except Exception, e:
                    print e
              output = ""
              output += "<html>"
              output += self.getStyles()
              output += "<body>"
              output += "<h2>Restaurant deleted.</h2>"
              output += "<p><a href='/restaurants'>&larr; back to all</a></p>"
              output += "</body></html>"
              self.wfile.write(output)
              #print output

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()


if __name__ == '__main__':
    main()



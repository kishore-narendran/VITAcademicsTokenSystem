import _mechanize, logging
import webapp2, cookielib
from _mechanize import Browser
from BeautifulSoup import BeautifulSoup
from google.appengine.ext import db
from cookielib import Cookie
import datetime, json
from google.appengine.api import mail

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<h1>VITacademics Scraping Engine</h1> <h2>Running On Google App Engine.</h2> \n<h4>Last Update: 28th January 2012 </h4><h4>\n\n(c) 2013 CollegeCODE</h4>')

class CaptchaGen(webapp2.RequestHandler):
	def get(self, regno):
		regno=regno.upper()
		br= _mechanize.Browser()
		cj = cookielib.CookieJar()
		br.set_cookiejar(cj)
		br.set_handle_equiv(True)
		br.set_handle_redirect(True)
		br.set_handle_referer(True)
		br.set_handle_robots(False)
		r=br.open('https://academics.vit.ac.in/parent/parent_login.asp')
		html=r.read()
		soup=BeautifulSoup(html)
		img = soup.find('img', id='imgCaptcha')
		image_response = br.open_novisit(img['src'])
		user_key = db.Key.from_path('User', regno, parent=None, namespace=None)
		tempuser = db.get(user_key)
		if(tempuser==None):
			tempuser=User(key_name=regno)
			tempuser.tot_count=0
			tempuser.cap_count=0
			tempuser.mark_count=0
			tempuser.att_count=0
			tempuser.valid=0
		for cook in cj:
			tempuser.cookievalue = cook.value
			tempuser.cookiename = cook.name
		tempuser.sestime=datetime.datetime.now()
		tempuser.put()
		self.response.headers['Content-Type'] = 'image/jpeg'
		self.response.out.write(image_response.read())
		

class CaptchaSub(webapp2.RequestHandler):
	def get(self, regno, dob, captcha):
		regno=regno.upper()
		captcha = captcha.upper()
		thevalue = "i didnt get it"
		thecookiename = "ASPSESSIONIDQUFTTQDA"
		user_key = db.Key.from_path('User', regno, parent=None, namespace=None)
		x = db.get(user_key)
		thevalue=x.cookievalue
		thecookiename=x.cookiename
		thetime=x.sestime
		nowtime=datetime.datetime.now()
		if((thetime-nowtime).total_seconds()<30):
			captcha = captcha.upper()
			br1 = _mechanize.Browser()
			ck = cookielib.Cookie(version=0, name=thecookiename, value=thevalue, port=None, port_specified=False, domain='academics.vit.ac.in', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=True, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
			r=br1.open('https://academics.vit.ac.in/parent/parent_login.asp')
			html=r.read()
			newcj = cookielib.CookieJar()
			newcj.set_cookie(ck)
			br1.set_cookiejar(newcj)
			br1.set_handle_equiv(True)
			br1.set_handle_redirect(True)
			br1.set_handle_referer(True)
			br1.set_handle_robots(False)
			br1.select_form('parent_login')
			br1.form['wdregno']=regno
			br1.form['vrfcd']=str(captcha)
			br1.form['wdpswd'] = dob
			response=br1.submit()
			if(response.geturl()=="https://academics.vit.ac.in/parent/home.asp"):
				self.response.write("success")
				for cook in newcj:
					x.cookievalue = cook.value
					x.cookiename = cook.name
				x.sestime=nowtime
				x.dob=dob
				x.valid=1
				x.cap_count=x.cap_count+1
				x.tot_count=x.tot_count+1
				x.put()
			else:
				self.response.write("captchaerror")
		else:
			self.response.write("timedout")


		
class TTExtractor(webapp2.RequestHandler):
	def get(self, regno, dob):
		regno = regno.upper()
		thevalue = "i didnt get it"
		thecookiename = "ASPSESSIONIDQUFTTQDA"
		user_key = db.Key.from_path('User', regno, parent=None, namespace=None)
		x = db.get(user_key)
		if(x==None):
			self.response.write("timedout")
		else:
			thevalue = x.cookievalue
			thecookiename = x.cookiename
			thetime=x.sestime
			nowtime=datetime.datetime.now()
			if((thetime-nowtime).total_seconds()<30):
				br1 = _mechanize.Browser()
				ck = cookielib.Cookie(version=0, name=thecookiename, value=thevalue, port=None, port_specified=False, domain='academics.vit.ac.in', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=True, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
				newcj = cookielib.CookieJar()
				newcj.set_cookie(ck)
				br1.set_cookiejar(newcj)
				br1.set_handle_equiv(True)
				br1.set_handle_redirect(True)
				br1.set_handle_referer(True)
				r=br1.open('https://academics.vit.ac.in/parent/timetable.asp?sem=WS')
				br1.set_handle_robots(False)
				if(r.geturl()=="https://academics.vit.ac.in/parent/timetable.asp?sem=WS"):
					page=r.read()
					self.response.headers['Content-Type'] = "text/plain"
					self.response.write("valid%")
					soup=BeautifulSoup(page)
                                        trs=soup.findAll('tr')
                                        data=""
                                        count=0
                                        for tr in trs:
                                            if(count!=0):   
                                                if("Total Credits" in tr.text):
                                                    break
                                                else:
                                                    tas=tr.findChildren()
                                                    for ta in tas:
                                                        data=data+ta.text+"\n"
                                            count=count+1
                                        refinedData=""
                                        temp=1
                                        for da in data.split("\n"):
                                            if (temp==1 and da!=""):
                                                refinedData=refinedData+da+"\n"
                                                temp=0
                                            else:
                                                temp=1
                                        data=refinedData[135:]
                                        subs=[]
                                        temp=1
                                        sub={}
                                        for da  in data.split("\n"):
                                            if(temp==1):
                                                sub.update({"Sl_No":da})
                                            elif(temp==2):
                                                sub.update({"Class Nbr":da})
                                            elif(temp==3):
                                                sub.update({"Code":da})
                                            elif(temp==4):
                                                sub.update({"Title":da})
                                            elif(temp==6):
                                                sub.update({"ltpc":da})
                                            elif(temp==7):
                                                sub.update({"bl":da})
                                            elif(temp==9):
                                                sub.update({"slot":da})
                                            elif(temp==10):
                                                sub.update({"venue":da})
                                            elif(temp==11):
                                                sub.update({"faculty":da})
                                            elif(temp==12):
                                                sub.update({"bill_date":da})
                                            elif(temp==13):
                                                temp=0
                                                subs.append(sub)
                                                sub={}
                                            temp=temp+1
					self.response.write(json.dumps(subs))
			    		for cook in newcj:
						x.cookievalue = cook.value
						x.cookiename = cook.name
					x.sestime=nowtime
					x.att_count=x.att_count+1
					x.tot_count=x.tot_count+1
					x.put()	
				else:
					self.response.write("timedout")
			else:
				self.response.write("timedout")


class Cleanup(webapp2.RequestHandler):
	def get(self):
		q = User.all()
		msg="<h2>Purged the following bogus users</h2>"
		msg+="<ul>"
		c=0
		for a in q:
			if(a.valid==0):
				db.delete(a.key())
				msg=msg+"<pre><li><h3>USER:\t"
				msg=msg+a.key().name()
				msg=msg+"</h3></pre>"
				c=c+1
		msg=msg+"</ul>"
		if(c==0):
			self.response.write("<h3>Nothing to purge today!</h3>")
		else:	
			self.response.write(msg)
			message = mail.EmailMessage(sender="VITacademics Purger <karthikb351@gmail.com>",subject="The following bogus users have been purged")
			message.to = "Karthik Balakrishnan <karthikb351@gmail.com>"
			message.html=msg
			message.send()

class Viewer(webapp2.RequestHandler):
	def get(self):
		q = User.all()
		q.order('-tot_count')
		self.response.write("<ul>")
		for x in q:
			self.response.write("<pre><li><h3>USER:")
			self.response.write(x.key().name())
			self.response.write("\nDOB:")
			self.response.write(x.dob)
			self.response.write("</h3><h4>Total Number of requests:\t")
			self.response.write(x.tot_count)
			self.response.write("</h4>Captcha Sub Count:\t\t")
			self.response.write(x.cap_count)
			self.response.write("\nAttendance Count:\t\t")
			self.response.write(x.att_count)
			self.response.write("\nMarks Count:\t\t\t")
			self.response.write(x.mark_count)
			self.response.write("</li>")
			self.response.write("\n\n</pre>")
		self.response.write("</ul>")
			
			
		
class User(db.Model):
	valid = db.IntegerProperty()	
	tot_count = db.IntegerProperty()
	cap_count = db.IntegerProperty()
	att_count = db.IntegerProperty()
	mark_count = db.IntegerProperty()
	dob = db.StringProperty()
	cookiename = db.StringProperty()
	cookievalue = db.StringProperty()
	sestime = db.DateTimeProperty(auto_now=True)
		



app = webapp2.WSGIApplication([('/', MainPage),('/purge', Cleanup),('/view', Viewer), ('/captchasub/(.*)/(.*)/(.*)', CaptchaSub), ('/captcha/(.*)', CaptchaGen), ('/tt/(.*)/(.*)', TTExtractor) ] ,debug=True)

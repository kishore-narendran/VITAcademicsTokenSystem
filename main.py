import webapp2, string, random, urllib2, json
from datetime import *
from PIL import Image
from StringIO import StringIO
from mechanize import _mechanize
from BeautifulSoup import BeautifulSoup
from cookielib import Cookie
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import mail
from ttform import TimeTable
from CaptchaParser import CaptchaParser

class Notice(db.Model):
	text = db.TextProperty()
	author = db.StringProperty()
	timestamp = db.DateTimeProperty(auto_now = True)
	cnum = db.IntegerProperty()

class GCMclient(db.Model):
	gcmclients = db.StringListProperty()

class AddClient(webapp2.RequestHandler):
	def post(self):
		cnums = self.request.get_all("cnum")
		gcmid = self.request.get("gcmid")
		if gcmid == '' or cnums == None:
			status = {'status':'failure'}
		else:
			for cnum in cnums:
				GCMclientobject = GCMclient.get_by_key_name(cnum)
				if GCMclientobject == None:
					GCMclientobject = GCMclient(key_name = cnum)
					GCMclientobject.gcmclients.append(str(gcmid))
					GCMclientobject.put()
					status = {'status':'success'}
				else:
					GCMclientobject.gcmclients.append(str(gcmid))
					GCMclientobject.put()
					status = {'status':'success'}
		self.response.write(json.dumps(status))

class AddEditNotice(webapp2.RequestHandler):
	def post(self):
		text = self.request.get("text")
		author = self.request.get("author")
		cnum = self.request.get("cnum")
		nid = self.request.get("id")
		if nid == '':
			notice = Notice(text = text, author = author, cnum = int(cnum)).put()
			status = {'status':'created'}
			#Add GCM push here for all students belonging to the cnum mentioned above
		else:
			notice = Notice.get_by_id(int(nid))
			if text != '':
				notice.text = text
			if author != '':
				notice.author = author
			if cnum != '':
				notice.cnum = int(cnum)
			notice.put()
			status = {'status':'edited'}
		self.response.write(json.dumps(status))

class RetrieveNoticeByClassNum(webapp2.RequestHandler):
	def get(self, cnum):
		notices = Notice.all()
		notices.filter("cnum =", int(cnum))
		notices.order("-timestamp")
		njsons = []
		for notice in notices:
			njson = {'text':notice.text, 'author':notice.author, 'id':notice.key().id(), 'timestamp':str(notice.timestamp), 'cnum':notice.cnum}
			njsons.append(njson)
		njsons = {'notices':njsons}
		self.response.write(json.dumps(njsons))

class RetrieveNoticesByStudent(webapp2.RequestHandler):
	def post(self):
		cnums = self.request.get_all("cnum")
		masternotices = []
		for cnum in cnums:
			notices = Notice.all()
			notices.filter("cnum =", int(cnum))
			notices.order("-timestamp")
			njsons = []
			for notice in notices:
				njson = {'text':notice.text, 'author':notice.author, 'id':notice.key().id(), 'timestamp':str(notice.timestamp), 'cnum':notice.cnum}
				njsons.append(njson)
			njsons = {'cnum':cnum, 'notices':njsons}
			masternotices.append(njsons)
		masternotices = {'masternotices':masternotices}
		self.response.write(json.dumps(masternotices))

class DeleteNotice(webapp2.RequestHandler):
	def get(self, nid):
		notice = Notice.get_by_id(int(nid))
		if notice != None:
			notice.delete()
			status = {'status':'success'}
		else:
			status = {'status':'failure'}
		self.response.write(json.dumps(status))


def token_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

class GetToken(webapp2.RequestHandler):
	def get(self, regno, dob):
		flag = True
		while flag is True:
			token = token_generator()
			checkvalue = memcache.get(token)
			if checkvalue is None:
				flag = False
				memcache.set(key = token, value = {"regno":regno.upper(),"dob":dob}, time = 86400)
				time = datetime.now()
				expiry = time + timedelta(seconds = 86400)
				result = {'regno':regno.upper(), 'token':token, 'expiry':expiry.strftime('%Y-%m-%d %H:%M:%S'), 'dob':dob}
				self.response.write(json.dumps(result))

class AccessToken(webapp2.RequestHandler):
	def get(self, token):
		token = token.upper()
		response = memcache.get(token)
		if response is None:
			result = {'status':'failure','regno':''}
		else:
			result = {'status':'success','regno':response["regno"],'dob':response["dob"]}
		self.response.write(json.dumps(result))

class GetTimeTable(webapp2.RequestHandler):
	def get(self, regno, dob):
		result = memcache.get(regno.upper())
		if result != None:
			self.response.write(json.dumps(result))
			return
		regno = regno.upper()
		br = _mechanize.Browser()
		br.set_handle_equiv(True)
		br.set_handle_redirect(True)
		br.set_handle_referer(True)
		br.set_handle_robots(False)
		r=br.open('https://academics.vit.ac.in/parent/parent_login.asp')
		html=r.read()
		soup=BeautifulSoup(html)
		img = soup.find('img', id='imgCaptcha')
		image_response = br.open_novisit(img['src'])
		image = Image.open(StringIO(image_response.read()))
		parser = CaptchaParser()
		captcha = parser.getCaptcha(image)
		br.select_form('parent_login')
		br.form['wdregno'] = regno
		br.form['vrfcd'] = str(captcha)
		br.form['wdpswd'] = dob
		response = br.submit()
		if (response.geturl() == "https://academics.vit.ac.in/parent/home.asp"):
			r=br.open('https://academics.vit.ac.in/parent/timetable.asp?sem=WS')
			page=r.read()
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
					sub.update({"slno":da})
				elif(temp==2):
					sub.update({"cnum":da})
				elif(temp==3):
					sub.update({"code":da})
				elif(temp==4):
					sub.update({"title":da})
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
					sub.update({"billdate":da})
				elif(temp==13):
					temp=0
					subs.append(sub)
					sub={}
				temp=temp+1
			final = {'subjects':subs}
			t = TimeTable(json.dumps(final))
			tt = t.formTT()
			final = {"subjects":subs}
			final.update({"timetable":tt})
			final.update({"dob":dob})
			memcache.set(key = regno, value = final)
			self.response.write(json.dumps(final))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/gettimetable/(.*)/(.*)', GetTimeTable),
    ('/accesstoken/(.*)', AccessToken),
    ('/getnewtoken/(.*)/(.*)', GetToken),
    ('/addeditnotice', AddEditNotice),
    ('/noticesbycnum/(.*)', RetrieveNoticeByClassNum),
    ('/noticesbystudent', RetrieveNoticesByStudent),
    ('/addclient', AddClient)
], debug=True)


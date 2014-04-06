import objc, re, os
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
import urllib2
import urllib
from bs4 import BeautifulSoup
from LoginWindow import *
from CaseMenu import *

class iBugz(NSObject):
  baseurl = "https://fogbugz.logos.com/api.asp?"
  token = ''
  cases = []

  def applicationDidFinishLaunching_(self, notification):
    self.loginWindow = LoginWindow.alloc().initWithWindowNibName_("LoginWindow")
    self.loginWindow.registerApi(self)

    statusbar = NSStatusBar.systemStatusBar()
    self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
    self.statusitem.setTitle_('iBugz')
    self.statusitem.setHighlightMode_(1)
    self.statusitem.setToolTip_('iBugz')

    self.menu = CaseMenu.alloc().init()
    self.menu.registerApi(self)
    self.menu.initialDisplay()
    self.statusitem.setMenu_(self.menu)

  def showLogin_(self, notification):
    self.loginWindow.showWindow_(self.loginWindow)

  def login(self, username, password):
    self.executeRequest({'cmd':'logon', 'email':username, 'password':password}, self.loginWindow.handleLogin)

  def setCurrentFilter(self):
    self.executeRequest({'cmd':'setCurrentFilter', 'sFilter':'ez', 'token':self.token}, self.getCurrentCase)

  def getCurrentCase(self, response):
    self.executeRequest({'cmd':'viewPerson', 'token':self.token}, self.fetchCases)

  def fetchCases(self, response):
    self.workingCase = response.response.person.find('ixbugworkingon').string
    self.executeRequest({'cmd':'search', 'cols':'sTitle', 'token':self.token}, self.updateCases)

  def updateCases(self, response):
    self.cases = response.find_all('case')
    self.menu.updateMenu()

  def selectCase_(self, notification):
    casenum = notification._.representedObject.get('ixbug')
    self.executeRequest({'cmd':'startWork', 'ixbug':casenum, 'token':self.token}, None)
    self.workingCase = casenum
    self.menu.updateMenu()

  def stopWork_(self, notification):
    self.executeRequest({'cmd':'stopWork', 'token':self.token}, None)
    self.workingCase = 0
    self.menu.updateMenu()

  def executeRequest(self, data, callback):
    thread.start_new_thread(self.executeRequestCore, (data, callback))

  def executeRequestCore(self, data, callback):
    response = urllib2.urlopen(self.baseurl + urllib.urlencode(data))
    if (callback != None):
      callback(BeautifulSoup(response.read()))

if __name__ == "__main__":
  app = NSApplication.sharedApplication()
  delegate = iBugz.alloc().init()
  app.setDelegate_(delegate)
  AppHelper.runEventLoop()

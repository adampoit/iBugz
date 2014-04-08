import objc, re, os
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
import urllib2
import urllib
from bs4 import BeautifulSoup
from LoginWindow import *
from CaseMenu import *
import time

class iBugz(NSObject):
  baseurl = "https://fogbugz.logos.com/api.asp?"
  token = ''
  cases = []
  casesToRemove = []

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

    self.lock = thread.allocate_lock()

  def showLogin_(self, notification):
    self.loginWindow.showWindow_(self.loginWindow)

  def login(self, username, password):
    self.executeRequest({'cmd':'logon', 'email':username, 'password':password}, self.handleLogin)

  def handleLogin(self, response):
    self.loginWindow.handleLogin()

    if (response.response.token != None):
      self.token = response.response.token.string
      self.setCurrentFilter()
      self.menu.hideLogin()
      self.loginWindow.close()

  def setCurrentFilter(self):
    self.executeRequest({'cmd':'setCurrentFilter', 'sFilter':'ez', 'token':self.token}, self.getCurrentCase, 5)

  def getCurrentCase(self, response):
    self.executeRequest({'cmd':'viewPerson', 'token':self.token}, self.fetchCases)

  def fetchCases(self, response):
    with self.lock:
      self.workingCase = response.response.person.find('ixbugworkingon').string

    self.executeRequest({'cmd':'search', 'cols':'sTitle', 'token':self.token}, self.updateCases)

  def updateCases(self, response):
    newCases = response.find_all('case')

    with self.lock:
      self.casesToRemove = list(set(self.cases) - set(newCases))
      self.cases = newCases

    AppHelper.callAfter(self.menu.updateMenu)

  def selectCase_(self, notification):
    casenum = notification._.representedObject.get('ixbug')
    self.executeRequest({'cmd':'startWork', 'ixbug':casenum, 'token':self.token}, None)

    with self.lock:
      self.workingCase = casenum

    self.menu.updateMenu()

  def stopWork_(self, notification):
    self.executeRequest({'cmd':'stopWork', 'token':self.token}, None)

    with self.lock:
      self.workingCase = 0

    self.menu.updateMenu()

  def executeRequest(self, data, callback, repeatEvery=0):
    thread.start_new_thread(self.executeRequestCore, (data, callback, repeatEvery))

  def executeRequestCore(self, data, callback, repeatEvery):
    while (True):
      response = urllib2.urlopen(self.baseurl + urllib.urlencode(data))

      if (callback != None):
        callback(BeautifulSoup(response.read()))

      if (repeatEvery == 0):
        break

      time.sleep(repeatEvery)

if __name__ == "__main__":
  app = NSApplication.sharedApplication()
  delegate = iBugz.alloc().init()
  app.setDelegate_(delegate)
  AppHelper.runEventLoop()

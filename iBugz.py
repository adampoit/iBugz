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
from Quartz.CoreGraphics import *

class iBugz(NSObject):
  baseurl = "https://fogbugz.logos.com/api.asp?"
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

    self.userDefaults = NSUserDefaults.standardUserDefaults()
    self.token = self.userDefaults.objectForKey_("token")

    if (self.token != None):
      self.setCurrentFilter()
      self.menu.hideLogin()

    self.statusitem.setMenu_(self.menu)

    self.lock = thread.allocate_lock()

  def initialDisplay(self):
    AppHelper.callAfter(self.menu.initialDisplay)
    AppHelper.callAfter(self.loginWindow.showWindow)

  def showLogin_(self, notification):
    self.loginWindow.showWindow()

  def login(self, username, password):
    self.executeRequest({'cmd':'logon', 'email':username, 'password':password}, self.handleLoginSuccess, self.handleLoginFailure)

  def handleLoginSuccess(self, response):
    self.token = response.response.token.string
    self.userDefaults.setObject_forKey_(self.token, "token")
    self.setCurrentFilter()
    self.menu.hideLogin()
    self.loginWindow.close()

  def handleLoginFailure(self):
    self.loginWindow.handleLoginFailure()

  def setCurrentFilter(self):
    self.executeRequest({'cmd':'setCurrentFilter', 'sFilter':'ez', 'token':self.token}, self.getCurrentCase, self.initialDisplay, 5)

  def getCurrentCase(self, response):
    self.executeRequest({'cmd':'viewPerson', 'token':self.token}, self.fetchCases, self.initialDisplay)

  def fetchCases(self, response):
    with self.lock:
      self.workingCase = response.response.person.find('ixbugworkingon').string

    self.executeRequest({'cmd':'search', 'cols':'sTitle', 'token':self.token}, self.updateCases, self.initialDisplay)

  def updateCases(self, response):
    newCases = response.find_all('case')

    with self.lock:
      self.casesToRemove = list(set(self.cases) - set(newCases))
      self.cases = newCases

    AppHelper.callAfter(self.menu.updateMenu)

  def selectCase_(self, notification):
    casenum = notification._.representedObject.get('ixbug')
    self.executeRequest({'cmd':'startWork', 'ixbug':casenum, 'token':self.token}, None, self.initialDisplay)

    with self.lock:
      self.workingCase = casenum

    self.menu.updateMenu()

  def stopWork_(self, notification):
    self.executeRequest({'cmd':'stopWork', 'token':self.token}, None, self.initialDisplay)

    with self.lock:
      self.workingCase = 0

    self.menu.updateMenu()

  def executeRequest(self, data, callback, callbackOnFail = None, repeatEvery = 0):
    def executeRequestCore():
      while (True):
        request = urllib2.urlopen(self.baseurl + urllib.urlencode(data))
        response = BeautifulSoup(request.read())

        if (response.response.error != None):
          if (callbackOnFail != None):
            callbackOnFail()
          break

        if (callback != None):
          callback(response)

        if (repeatEvery == 0):
          break

        time.sleep(repeatEvery)

    thread.start_new_thread(executeRequestCore, ())

if __name__ == "__main__":
  app = NSApplication.sharedApplication()
  delegate = iBugz.alloc().init()
  app.setDelegate_(delegate)
  AppHelper.runEventLoop()

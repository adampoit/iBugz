import objc, re, os
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
import urllib2
import urllib
from bs4 import BeautifulSoup
from LoginWindow import *

class iBugz(NSObject):
  baseurl = "https://fogbugz.logos.com/api.asp?"
  token = ''
  cases = []
  workingCase = 0

  def applicationDidFinishLaunching_(self, notification):
    self.loginWindow = LoginWindowController.alloc().initWithWindowNibName_("LoginWindow")
    self.loginWindow.registerApi(self)

    statusbar = NSStatusBar.systemStatusBar()
    self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
    self.statusitem.setTitle_('iBugz')
    self.statusitem.setHighlightMode_(1)
    self.statusitem.setToolTip_('iBugz')

    self.menu = NSMenu.alloc().init()
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Login', 'login:', '')
    self.menu.addItem_(menuitem)
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
    self.menu.addItem_(menuitem)
    self.statusitem.setMenu_(self.menu)

  def login_(self, notification):
    self.loginWindow.showWindow_(self.loginWindow)

  def login(self, username, password):
    self.executeRequest({'cmd':'logon', 'email':username, 'password':password}, self.loginWindow.handleLogin)

  def setCurrentFilter(self):
      self.executeRequest({'cmd':'setCurrentFilter', 'sFilter':'ez', 'token':self.token}, self.fetchCases)

  def fetchCases(self, response):
    self.executeRequest({'cmd':'search', 'cols':'sTitle', 'token':self.token}, self.updateCases)

  def updateCases(self, response):
    self.cases = response.find_all('case')
    self.updateMenu()

  def selectCase_(self, notification):
    casenum = notification._.representedObject.get('ixbug')
    self.executeRequest({'cmd':'startWork', 'ixbug':casenum, 'token':self.token}, None)
    self.workingCase = casenum
    self.updateMenu()

  def stopWork_(self, notification):
    self.executeRequest({'cmd':'stopWork', 'token':self.token}, None)
    self.workingCase = 0
    self.updateMenu()

  def updateMenu(self):
    self.menu = NSMenu.alloc().init()
    for case in self.cases:
        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(case.stitle.string, 'selectCase:', '')
        if (self.workingCase == case.get('ixbug')):
            menuitem.setState_(NSOnState)
        menuitem.setRepresentedObject_(case)
        self.menu.addItem_(menuitem)
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Stop Work', 'stopWork:', '')
    self.menu.addItem_(menuitem)
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
    self.menu.addItem_(menuitem)
    self.statusitem.setMenu_(self.menu)

  def executeRequest(self, data, callback):
    thread.start_new_thread(self.executeRequestCore, (data, callback, ) )

  def executeRequestCore(self, data, callback):
    response = urllib2.urlopen(self.baseurl + urllib.urlencode(data))
    if (callback != None):
      callback(BeautifulSoup(response.read()))

if __name__ == "__main__":
  app = NSApplication.sharedApplication()
  delegate = iBugz.alloc().init()
  app.setDelegate_(delegate)
  AppHelper.runEventLoop()
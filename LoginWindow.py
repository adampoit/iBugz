from Cocoa import *
from Foundation import *
import thread

class LoginWindowController(NSWindowController):
  username = objc.IBOutlet()
  password = objc.IBOutlet()
  loginfailed = objc.IBOutlet()
  spinindicator = objc.IBOutlet()
  loginbutton = objc.IBOutlet()

  def registerApi(self, api):
    self.api = api

  def windowDidLoad(self):
    NSWindowController.windowDidLoad(self)

  @objc.IBAction
  def login_(self, sender):
    self.loginfailed.setHidden_(True)
    self.spinindicator.setHidden_(False)
    self.spinindicator.startAnimation_(self)
    self.loginbutton.setHidden_(True)
    self.api.login(self.username._.stringValue, self.password._.stringValue)

  def handleLogin(self, response):
    self.spinindicator.setHidden_(True)
    self.loginbutton.setHidden_(False)
    if (response.response.token == None):
      self.loginfailed.setHidden_(False)
    else:
      self.api.token = response.response.token.string
      self.api.setCurrentFilter()
      self.close()

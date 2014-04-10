from Cocoa import *
from Foundation import *
import thread

class LoginWindow(NSWindowController):
  username = objc.IBOutlet()
  password = objc.IBOutlet()
  loginfailed = objc.IBOutlet()
  spinindicator = objc.IBOutlet()
  loginbutton = objc.IBOutlet()

  def registerApi(self, api):
    self.api = api

  def windowDidLoad(self):
    NSWindowController.windowDidLoad(self)
    self._.window.center()
    self._.window.setTitle_("Login")

  def showWindow(self):
    self.showWindow_(self)
    self._.window.setLevel_(NSMainMenuWindowLevel)

  @objc.IBAction
  def login_(self, sender):
    self.loginfailed.setHidden_(True)
    self.spinindicator.setHidden_(False)
    self.spinindicator.startAnimation_(self)
    self.loginbutton.setHidden_(True)
    self.api.login(self.username._.stringValue, self.password._.stringValue)

  def handleLoginFailure(self):
    self.spinindicator.setHidden_(True)
    self.loginbutton.setHidden_(False)
    self.loginfailed.setHidden_(False)

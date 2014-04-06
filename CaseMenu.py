from Cocoa import *
from Foundation import *
from LoginWindow import *

class CaseMenu(NSMenu):
  def registerApi(self, api):
    self.api = api

  def initialDisplay(self):
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Login', 'showLogin:', '')
    self.addItem_(menuitem)
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
    self.addItem_(menuitem)

  def updateMenu(self):
    self.removeAllItems()
    for case in self.api.cases:
        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(case.stitle.string, 'selectCase:', '')
        if (self.api.workingCase == case.get('ixbug')):
            menuitem.setState_(NSOnState)
        menuitem.setRepresentedObject_(case)
        self.addItem_(menuitem)
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Stop Work', 'stopWork:', '')
    self.addItem_(menuitem)
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
    self.addItem_(menuitem)

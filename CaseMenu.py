from Cocoa import *
from Foundation import *
from LoginWindow import *

class CaseMenu(NSMenu):
  thisTime = False

  def registerApi(self, api):
    self.api = api

  def initialDisplay(self):
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Login', 'showLogin:', '')
    self.addItem_(menuitem)
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
    self.addItem_(menuitem)

  def hideLogin(self):
    self.removeItem_(self.itemWithTitle_('Login'))
    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Stop Work', 'stopWork:', '')
    self.insertItem_atIndex_(menuitem, 0)

  def updateMenu(self):
    with self.api.lock:
      for case in self.api.casesToRemove:
        index = self.indexOfItemWithRepresentedObject_(case)
        self.removeItemAtIndex_(index)

      self.casesToRemove = []

      for case in self.api.cases:
        index = self.indexOfItemWithRepresentedObject_(case)

        if (index == -1):
          menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(case.stitle.string, 'selectCase:', '')
          menuitem.setRepresentedObject_(case)
          self.insertItem_atIndex_(menuitem, 0)
        elif (self.api.workingCase == case.get('ixbug')):
          self.itemAtIndex_(index).setState_(NSOnState)
        else:
          self.itemAtIndex_(index).setState_(NSOffState)

    self.update()

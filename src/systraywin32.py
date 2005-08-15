## src/systraywin32.py
##
## Gajim Team:
##	- Yann Le Boulanger <asterix@lagaule.org>
##	- Vincent Hanquez <tab@snarc.org>
##	- Nikos Kouremenos <kourem@gmail.com>
##	- Dimitur Kirov <dkirov@gmail.com>
##
## code initially based on 
## http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/334779
##
##	Copyright (C) 2003-2005 Gajim Team
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 2 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##

__version__ = '1.01'


import sys
import win32gui
import win32con
import systray

GWL_WNDPROC = -4
GWL_EXSTYLE = -20
WM_TASKBARCREATED = win32gui.RegisterWindowMessage('TaskbarCreated')
WM_USER = 1024
WM_TRAYMESSAGE = WM_USER + 20

import gtk
WM_LBUTTONUP = 0x0202

from common import gajim
from common import i18n
_ = i18n._
APP = i18n.APP
gtk.glade.bindtextdomain(APP, i18n.DIR)
gtk.glade.textdomain(APP)

GTKGUI_GLADE = 'gtkgui.glade'

class SystrayWINAPI:
	def __init__(self, gtk_window):
		self._window = gtk_window
		self._hwnd = gtk_window.window.handle
		self._message_map = {}

		self.notify_icon = None            

		# Sublass the window and inject a WNDPROC to process messages.
		self._oldwndproc = win32gui.SetWindowLong(self._hwnd, GWL_WNDPROC,
												self._wndproc)

		gtk_window.connect('unrealize', self.remove)


	def add_notify_icon(self, menu, hicon=None, tooltip=None):
		""" Creates a notify icon for the gtk window. """
		if not self.notify_icon:
			if not hicon:
				hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
			self.notify_icon = NotifyIcon(self._hwnd, hicon, tooltip)

			# Makes redraw if the taskbar is restarted.   
			self.message_map({WM_TASKBARCREATED: self.notify_icon._redraw})


	def message_map(self, msg_map={}):
		""" Maps message processing to callback functions ala win32gui. """
		if msg_map:
			if self._message_map:
				duplicatekeys = [key for key in msg_map.keys()
								if self._message_map.has_key(key)]
				
				for key in duplicatekeys:
					new_value = msg_map[key]
					
					if isinstance(new_value, list):
						raise TypeError('Dict cannot have list values')
					
					value = self._message_map[key]
					
					if new_value != value:
						new_value = [new_value]
						
						if isinstance(value, list):
							value += new_value
						else:
							value = [value] + new_value
						
						msg_map[key] = value
			self._message_map.update(msg_map)

	def message_unmap(self, msg, callback=None):
		if self._message_map.has_key(msg):
			if callback:
				cblist = self._message_map[key]
				if isinstance(cblist, list):
					if not len(cblist) < 2:
						for i in range(len(cblist)):
							if cblist[i] == callback:
								del self._message_map[key][i]
								return
			del self._message_map[key]

	def remove_notify_icon(self):
		""" Removes the notify icon. """
		if self.notify_icon:
			self.notify_icon.remove()
			self.notify_icon = None

	def remove(self, *args):
		""" Unloads the extensions. """
		self._message_map = {}
		self.remove_notify_icon()
		self = None

	def show_balloon_tooltip(self, title, text, timeout=10,
							icon=win32gui.NIIF_NONE):
		""" Shows a baloon tooltip. """
		if not self.notify_icon:
			self.add_notifyicon()
		self.notify_icon.show_balloon(title, text, timeout, icon)

	def _wndproc(self, hwnd, msg, wparam, lparam):
		""" A WINDPROC to process window messages. """
		if self._message_map.has_key(msg):
			callback = self._message_map[msg]
			if isinstance(callback, list):
				for cb in callback:
					cb(hwnd, msg, wparam, lparam)
			else:
				callback(hwnd, msg, wparam, lparam)

		return win32gui.CallWindowProc(self._oldwndproc, hwnd, msg, wparam,
									lparam)
									

class NotifyIcon:

	def __init__(self, hwnd, hicon, tooltip=None):

		self._hwnd = hwnd
		self._id = 0
		self._flags = win32gui.NIF_MESSAGE | win32gui.NIF_ICON
		self._callbackmessage = WM_TRAYMESSAGE
		self._hicon = hicon

		win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, self._get_nid())
		if tooltip: self.set_tooltip(tooltip)


	def _get_nid(self):
		""" Function to initialise & retrieve the NOTIFYICONDATA Structure. """
		nid = (self._hwnd, self._id, self._flags, self._callbackmessage,
			self._hicon)
		nid = list(nid)

		if not hasattr(self, '_tip'): self._tip = ''
		nid.append(self._tip)

		if not hasattr(self, '_info'): self._info = ''
		nid.append(self._info)
			
		if not hasattr(self, '_timeout'): self._timeout = 0
		nid.append(self._timeout)

		if not hasattr(self, '_infotitle'): self._infotitle = ''
		nid.append(self._infotitle)
			
		if not hasattr(self, '_infoflags'):self._infoflags = win32gui.NIIF_NONE
		nid.append(self._infoflags)

		return tuple(nid)
		
	
	def remove(self):
		""" Removes the tray icon. """
		win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, self._get_nid())


	def set_tooltip(self, tooltip):
		""" Sets the tray icon tooltip. """
		self._flags = self._flags | win32gui.NIF_TIP
		self._tip = tooltip
		win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, self._get_nid())
		
		
	def show_balloon(self, title, text, timeout=10, icon=win32gui.NIIF_NONE):
		""" Shows a balloon tooltip from the tray icon. """
		self._flags = self._flags | win32gui.NIF_INFO
		self._infotitle = title
		self._info = text
		self._timeout = timeout * 1000
		self._infoflags = icon
		win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, self._get_nid())

	def _redraw(self, *args):
		""" Redraws the tray icon. """
		self.remove
		win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, self._get_nid())

#FIXME: subclass us under Systray
class SystrayWin32(systray.Systray):
	def __init__(self, plugin):
		# Note: gtk window must be realized before installing extensions.
		systray.Systray.__init__(self, plugin)
		self.plugin = plugin
		self.jids = []
		self.status = 'offline'
		self.xml = gtk.glade.XML(GTKGUI_GLADE, 'systray_context_menu', APP)
		self.systray_context_menu = self.xml.get_widget('systray_context_menu')
		
		self.systray_winapi = SystrayWINAPI(self.plugin.roster.window)
		#self.systray_winapi.add_notify_icon(self.systray_context_menu)

		self.xml.signal_autoconnect(self)
		
		# Set up the callback messages
		self.systray_winapi.message_map({
			WM_TRAYMESSAGE: self.on_clicked
			}) 

	def show_icon(self):
		self.systray_winapi.add_notify_icon(self.systray_context_menu, tooltip = 'Gajim')
		self.systray_winapi.notify_icon.menu = self.systray_context_menu
		self.set_img()

	def hide_icon(self):
		self.systray_winapi.remove_notify_icon()

	def on_clicked(self, hwnd, message, wparam, lparam):
		if lparam == win32con.WM_RBUTTONUP: # Right click
			self.make_menu()
			self.systray_winapi.notify_icon.menu.popup(None, None, None, 0, 0)
		elif lparam == win32con.WM_MBUTTONUP: # Middle click
			self.on_middle_click()
		elif lparam == WM_LBUTTONUP: # Left click
			self.on_left_click()
			#self.systray_winapi.notify_icon.menu.popdown()
			#self.systray_winapi.notify_icon.menu.popup(None, None, None, 0, 0)


	def add_jid(self, jid, account):
		print 'FIXME: add_jid'
		return
		list = [account, jid]
		if not list in self.jids:
			self.jids.append(list)
			self.set_img()
		#we look for the number of unread messages
		#in roster
		nb = self.plugin.roster.nb_unread
		for acct in gajim.connections:
			#in chat / groupchat windows
			for kind in ['chats', 'gc']:
				jids = self.plugin.windows[acct][kind]
				for jid in jids:
					if jid != 'tabbed':
						nb += jids[jid].nb_unread[jid]
		if nb > 1:
			label = _('Gajim - %s unread messages') % nb
		else:
			label = _('Gajim - 1 unread message')
		self.tip.set_tip(self.t, label)

	def set_img(self):
		print 'set_img'
		self.systray_winapi.remove_notify_icon()
		if len(self.jids) > 0:
			status = 'message'
		else:
			#status = self.status
			path_to_ico = '../data/pixmaps/gajim.ico'
		hinst = win32gui.GetModuleHandle(None)
		icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
		hicon = win32gui.LoadImage(hinst, 
								path_to_ico,  #FIXME: path
								win32con.IMAGE_ICON, 
								0, 
								0, 
								icon_flags)
		self.systray_winapi.add_notify_icon(self.systray_context_menu, hicon, 'Gajim')
		self.systray_winapi.notify_icon.menu = self.systray_context_menu

	def remove_jid(self, jid, account):
		print 'FIXME: remove_jid'
		return
		list = [account, jid]
		if list in self.jids:
			self.jids.remove(list)
			self.set_img()
		#we look for the number of unread messages
		#in roster
		nb = self.plugin.roster.nb_unread
		for acct in gajim.connections:
			#in chat / groupchat windows
			for kind in ['chats', 'gc']:
				for jid in self.plugin.windows[acct][kind]:
					if jid != 'tabbed':
						nb += self.plugin.windows[acct][kind][jid].nb_unread[jid]
		if nb > 1:
			label = _('Gajim - %s unread messages') % nb
		elif nb == 1:
			label = _('Gajim - 1 unread message')
		else:
			label = 'Gajim'
		self.tip.set_tip(self.t, label)

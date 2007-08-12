# Settings.py - Settings of Reportbug-NG.
# Copyright (C) 2007  Bastian Venthur
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import ConfigParser

class Settings:
    
    def __init__(self, configfile):
       
        self.configfile = configfile
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.configfile)
        
        # Users preferred mailclient
        self.lastmua = "default"
        
        # Sorting option
        self.sortByCol = 2
        self.sortAsc = False
        
        # Mainwindow
        self.x = 0
        self.y = 0
        self.width = 800
        self.height = 600
        self.menubar = True
        
        # ListView
        self.bugnrWidth = 100
        self.summaryWidth = 350
        self.statusWidth = 100
        self.severityWidth = 100
        self.lastactionWidth = 100
        
        
    def load(self):
    
        if self.config.has_option("general", "lastMUA"):
            self.lastmua = self.config.get("general", "lastMUA")
        if self.config.has_option("general", "sortByCol"):
            self.sortByCol = self.config.getint("general", "sortByCol")
        if self.config.has_option("general", "sortAsc"):
            self.sortAsc = self.config.getboolean("general", "sortAsc")
            
        if self.config.has_option("mainwindow", "x"):
            self.x = self.config.getint("mainwindow", "x")
        if self.config.has_option("mainwindow", "y"):
            self.y = self.config.getint("mainwindow", "y")
        if self.config.has_option("mainwindow", "width"):
            self.width = self.config.getint("mainwindow", "width")
        if self.config.has_option("mainwindow", "height"):
            self.height = self.config.getint("mainwindow", "height")
        if self.config.has_option("mainwindow", "menubar"):
            self.menubar = self.config.getboolean("mainwindow", "menubar")

        if self.config.has_option("listview", "bugnrwidth"):
            self.bugnrWidth = self.config.getint("listview", "bugnrwidth")
        if self.config.has_option("listview", "summarywidth"):
            self.summaryWidth = self.config.getint("listview", "summarywidth")
        if self.config.has_option("listview", "statuswidth"):
            self.statusWidth = self.config.getint("listview", "statuswidth")
        if self.config.has_option("listview", "severitywidth"):
            self.severityWidth = self.config.getint("listview", "severitywidth")
        if self.config.has_option("listview", "lastactionwidth"):
            self.lastactionWidth = self.config.getint("listview", "lastactionwidth")

    
    def save(self):

        if not self.config.has_section("general"):
            self.config.add_section("general")
        self.config.set("general", "lastMUA", self.lastmua)
        self.config.set("general", "sortByCol", self.sortByCol)
        self.config.set("general", "sortAsc", self.sortAsc)
        
        if not self.config.has_section("mainwindow"):
            self.config.add_section("mainwindow")
        self.config.set("mainwindow", "x", self.x)
        self.config.set("mainwindow", "y", self.y)
        self.config.set("mainwindow", "width", self.width)
        self.config.set("mainwindow", "height", self.height)
        self.config.set("mainwindow", "menubar", self.menubar)
        
        if not self.config.has_section("listview"):
            self.config.add_section("listview")
        self.config.set("listview", "bugnrwidth", self.bugnrWidth)
        self.config.set("listview", "summarywidth", self.summaryWidth)
        self.config.set("listview", "statuswidth", self.statusWidth)
        self.config.set("listview", "severitywidth", self.severityWidth)
        self.config.set("listview", "lastactionwidth", self.lastactionWidth)
        
        # Write everything to configfile
        self.config.write(open(self.configfile, "w"))

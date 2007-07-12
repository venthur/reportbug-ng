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
        self.lastmua = ""
        
        # Mainwindow
        self.x = 0
        self.y = 0
        self.width = 800
        self.height = 600
        self.menubar = True
        
        
    def load(self):
    
        if self.config.has_option("general", "lastMUA"):
            self.lastmua = self.config.get("general", "lastMUA")
            
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

    
    def save(self):

        if not self.config.has_section("general"):
            self.config.add_section("general")
        self.config.set("general", "lastMUA", self.lastmua)
        
        if not self.config.has_section("mainwindow"):
            self.config.add_section("mainwindow")
        self.config.set("mainwindow", "x", self.x)
        self.config.set("mainwindow", "y", self.y)
        self.config.set("mainwindow", "width", self.width)
        self.config.set("mainwindow", "height", self.height)
        self.config.set("mainwindow", "menubar", self.menubar)
        
        # Write everything to configfile
        self.config.write(open(self.configfile, "w"))

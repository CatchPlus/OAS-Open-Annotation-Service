## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of 
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
# This file is part of "Open Annotation Service"
# 
# "Open Annotation Service" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "Open Annotation Service" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "Open Annotation Service"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

from optparse import OptionParser, Option

from sys import exit

from re import compile as reCompile

VALIDNAMES=reCompile(r'^[A-Za-z0-9]+$')

alloptions = dict((o.dest, o) for o in [
    Option('-n', '--name', help="Service name, characters allowed A-Za-z0-9", dest="name"),
    Option('-p', '--port', type='int', help="Default port number", dest="port"),
    Option('', '--stateDir', help="Directory to write state.", dest="stateDir"),
    Option('', '--solrDataDir', help="Directory for solr data.", dest="solrDataDir"),
    Option('-c', '--configFile', help="Config file.", dest="configFile"),
    Option('', '--storeLocation', help="Directory for OWLIM data.", dest="storeLocation"),
    Option('', '--updatePort', type='int', help="Port number of Search Service update", dest="updatePort"),
    ])

applicationProfiles = {
    'search': dict(
        options=['configFile'],
        mandatoryKeys=['configFile']),
    'resolve': dict(
        options=['configFile'],
        mandatoryKeys=['configFile']),
    'solr': dict(
        options=['port', 'solrDataDir', 'configFile'],
        mandatoryKeys=['port', 'configFile', 'solrDataDir']),
    'owlim': dict(
        options=['port', 'storeLocation'],
        mandatoryKeys = ['port', 'storeLocation']),
}

class ParseArguments(object):
    def __init__(self, application):
        self._parser = OptionParser()
        profile = applicationProfiles.get(application, None)
        if profile is None:
            raise KeyError("Unknown application: %s" % application)

        for option in profile['options']:
            self._parser.add_option(alloptions[option])
        self._mandatoryKeys = profile['mandatoryKeys']

        self.print_help = self._parser.print_help

    @classmethod
    def parseForSearch(cls, args=None):
        return cls._parseFor('search', args)

    @classmethod
    def parseForSolr(cls, args=None):
        return cls._parseFor('solr', args)
    
    @classmethod
    def parseForOwlim(cls, args=None):
        return cls._parseFor('owlim', args)

    @classmethod
    def parseForResolve(cls, args=None):
        return cls._parseFor('resolve', args)

    @classmethod
    def _parseFor(cls, application, args):
        parser = cls(application)
        try:
            return parser.parse(args)
        except ValueError:
            parser.print_help()
            exit(1)

    def parse(self, args=None):
        options, arguments = self._parser.parse_args(args)
        for key in self._mandatoryKeys:
            if getattr(options, key, None) == None:
                raise ValueError("Argument '%s' is missing." % key)
        if 'name' in self._mandatoryKeys:
            self._assertValidName(options.name)
        return options, arguments

    @staticmethod
    def _assertValidName(name):
        if not VALIDNAMES.match(name):
            raise ValueError("Not a valid name.")
        

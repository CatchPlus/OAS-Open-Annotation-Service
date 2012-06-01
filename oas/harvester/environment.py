## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
# Copyright (C) 2012 Meertens Instituut (KNAW) http://meertens.knaw.nl
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

from simplejson import dump as jsonSave, load as jsonLoad

from os.path import join, isfile, isdir, abspath
from os import makedirs, rename, listdir
from shutil import rmtree
from urllib import urlencode
from glob import glob

CONFIG_FILENAME = 'config.json'
STATE_FILENAME = 'state.json'

class Environment(object):
    def __init__(self, root):
        self._root = root
        if not isdir(self._root):
            makedirs(self._root)

    def getRepositories(self):
        for name in glob(join(self._root, "*")):
            if Repository.isRepository(name):
                yield self.getRepository(name)

    def addRepository(self, name, **kwargs):
        repository = Repository(name=name, directory=self._repositoryDirectory(name), **kwargs)
        repository.save()
        return repository

    def deleteRepository(self, name):
        self.getRepository(name).delete()

    def getRepository(self, name):
        return Repository.read(self._repositoryDirectory(name))

    def _repositoryDirectory(self, name):
        return join(self._root, name)

class Repository(object):
    def __init__(self, name, baseUrl='', metadataPrefix='', setSpec='', active=False, apiKey='', directory=''):
        self.name = name
        self.baseUrl = baseUrl
        self.metadataPrefix = metadataPrefix
        self.setSpec = setSpec
        self.active = active
        self.apiKey = apiKey
        self.directory = directory
        self.errorLogPath = join(directory, 'errors.log')
        self.resumptionToken = None
        self.lastHarvest = None

    def listRecordsUrl(self):
        arguments = dict(verb='ListRecords')
        if self.resumptionToken:
            arguments['resumptionToken'] = self.resumptionToken
        else:
            arguments['metadataPrefix'] = self.metadataPrefix
            if self.setSpec:
                arguments['set'] = self.setSpec
        return self.baseUrl + '?' + urlencode(arguments)

    def logException(self, exception):
        self.logError(str(exception))

    def logError(self, text):
        open(self.errorLogPath, 'a').write(text)
        
    def readErrorLog(self):
        if not isfile(self.errorLogPath):
            return ''
        return open(self.errorLogPath, 'r').read()

    def save(self):
        if not isdir(self.directory):
            makedirs(self.directory)

        configFile = join(self.directory, CONFIG_FILENAME)
        tmpFile = '%s.tmp' % configFile
        jsonSave({
            'name': self.name,
            'baseUrl': self.baseUrl,
            'metadataPrefix': self.metadataPrefix,
            'setSpec': self.setSpec,
            'active': self.active,
            'apiKey': self.apiKey,
            },
            open(tmpFile, 'w'))
        rename(tmpFile, configFile)

        stateFile = join(self.directory, STATE_FILENAME)
        tmpFile = '%s.tmp' % stateFile
        jsonSave({
            'resumptionToken': self.resumptionToken,
            'lastHarvest': self.lastHarvest
        }, open(tmpFile, 'w'))
        rename(tmpFile, stateFile)

    def delete(self):
        rmtree(self.directory)

    @staticmethod
    def isRepository(path):
        return isdir(path) and isfile(join(path, CONFIG_FILENAME))

    @staticmethod
    def read(directory):
        jsonData = jsonLoad(open(join(directory, CONFIG_FILENAME)))
        repository = Repository(
            name=jsonData['name'],
            baseUrl=jsonData['baseUrl'],
            metadataPrefix=jsonData['metadataPrefix'],
            setSpec=jsonData['setSpec'],
            active=jsonData['active'],
            apiKey=jsonData['apiKey'],
            directory=directory
        )
        repository.readState()
        return repository
        
    def readState(self):
        jsonData = jsonLoad(open(join(self.directory, STATE_FILENAME)))
        self.resumptionToken = jsonData['resumptionToken']
        self.lastHarvest = jsonData['lastHarvest']


    def __eq__(self, other):
        return self.name == other.name and \
            self.baseUrl == other.baseUrl and \
            self.metadataPrefix == other.metadataPrefix and \
            self.setSpec == other.setSpec and \
            self.apiKey == other.apiKey


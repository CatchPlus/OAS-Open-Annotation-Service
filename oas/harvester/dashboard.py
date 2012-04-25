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

from meresco.core import Observable
from meresco.components.http.utils import redirectHttp
from cgi import parse_qs

class Dashboard(Observable):
    def __init__(self, home="/", name=None):
        Observable.__init__(self, name=name)
        self._home = home
        self._actions = {
            'create': self.handleCreate,
            'update': self.handleUpdate,
            'delete': self.handleDelete,
        }

    def handleRequest(self, Method, path, session, **kwargs):
        if Method == 'GET':
            yield redirectHttp % self._home
            return

        prefix, action = path.rsplit('/', 1)
        if 'user' in session and session['user'].isAdmin():
            session['Harvester.formValues'] = {}
            yield self._actions[action](session=session, **kwargs)
            return

        yield redirectHttp % self._home
        return

    def handleCreate(self, session, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        repositoryName = bodyArgs['repository'][0]
        repository = self.call.addRepository(name=repositoryName)
        formUrl = bodyArgs['formUrl'][0] % {'repository': repository.name}
        session['Harvester.formValues']['message'] = {'class': 'success', 'text': 'Repository created.'}
        yield redirectHttp % formUrl

    def handleUpdate(self, session, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        repository = bodyArgs['repository'][0]
        baseUrl = bodyArgs['baseUrl'][0]
        metadataPrefix = bodyArgs['metadataPrefix'][0]
        setSpec = bodyArgs['setSpec'][0]
        apiKey = bodyArgs['apiKey'][0]
        formUrl = bodyArgs['formUrl'][0]
        active = 'active' in bodyArgs
        self.call.addRepository(name=repository, baseUrl=baseUrl, metadataPrefix=metadataPrefix, setSpec=setSpec, apiKey=apiKey, active=active)
        session['Harvester.formValues']['message'] = {'class': 'success', 'text': 'Repository updated.'}
        yield redirectHttp % formUrl

    def handleDelete(self, session, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        repository = bodyArgs['repository'][0]
        formUrl = bodyArgs['formUrl'][0]
        self.call.deleteRepository(name=repository)
        session['Harvester.formValues']['message'] = {'class': 'success', 'text': 'Repository deleted.'}
        yield redirectHttp % formUrl
        

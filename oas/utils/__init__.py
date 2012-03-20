from parsearguments import ParseArguments
from annotation import identifierFromXml, validIdentifier, aboutNode, filterAnnotations, filterOacBodies, filterFoafAgents

def parseHeaders(headers):
    return dict((k, v.strip()) 
        for k,v in (l.split(':',1) 
            for l in headers.split('\r\n') 
                if ':' in l))



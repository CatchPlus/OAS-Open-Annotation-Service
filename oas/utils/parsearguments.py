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
    'solr': dict(
        options=['name', 'port', 'solrDataDir', 'configFile'],
        mandatoryKeys=['name', 'port', 'configFile', 'solrDataDir']),
    'owlim': dict(
        options=['name', 'port', 'storeLocation'],
        mandatoryKeys = ['name', 'port', 'storeLocation']),
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
        

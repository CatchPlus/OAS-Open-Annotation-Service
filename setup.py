from distutils.core import setup

version = '$Version: trunk$'[9:-1].strip()

setup(
    name='oas',
    packages=[
        'oas',
        'oas.login',
        'oas.resolve',
        'oas.harvester',
        'oas.utils',
    ],
    package_data={
        'oas': [
            'dynamic/*.sf',
            'static/*.css',
            'static/*.png',
            'static/dummy_*',
        ]
    },
    scripts=[
        'bin/start-oas-harvester',
        'bin/start-oas-owlim-server',
        'bin/start-oas-resolve-service',
        'bin/start-oas-server',
        'bin/start-oas-solr-server',
        'bin/start-oas-userdelete-service',
    ],
    version=version,
    url='http://avarus.seecr.nl',
    author='Seecr',
    author_email='development@seecr.nl',
    maintainer='Seecr',
    maintainer_email='development@seecr.nl',
    description='Exchange, storage and search of heterogeneous annotations.',
    long_description='Exchange, storage and search of heterogeneous annotations using a uniform format (Open Annotation format) and a uniform web service interface.',
    license='All rights reserved.',
    platforms='all',
)


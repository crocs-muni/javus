#!/usr/bin/env python3
import argparse
import logging
import os
import re
import subprocess as sp
import sys
import time

import pymongo

log = logging.getLogger(__file__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

LOG_LEVELS = [
    logging.DEBUG, logging.INFO, logging.WARNING,
    logging.ERROR, logging.CRITICAL
]

# kudos to: https://medium.com/@ramojol/python-context-managers-and-the-with-statement-8f53d4d9f87
class MongoConnection(object):
    def __init__(self, host='localhost', port='27017',
            database='card-analysis', collation='commands'):
        self.host = host
        self.port = port
        self.connection = None
        self.db_name = database
        self.collation_name = collation

    def __enter__(self, *args, **kwargs):
        conn_str = f'mongodb://{self.host}:{self.port}'
        log.debug('Starting the connection with %s', conn_str)

        self.connection = pymongo.MongoClient(conn_str)
        self.db = self.connection[self.db_name]
        self.col = self.db[self.collation_name]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.debug('Closing the connection to the database')
        self.connection.close()

class Timer(object):
    # naive timer, but to get at least an idea
    def __init__(self):
        self.start = None
        self.end = None
        self.duration = None

    def __enter__(self, *args, **kwargs):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        self.duration = self.end - self.start


class CommandLineApp():
    '''
    Template for Python command line applications.
    '''
    APP_DESCRIPTION = None

    def __init__(self):
        self.verbosity = logging.ERROR
        self.args = None

        self.parser = argparse.ArgumentParser(
                description=self.APP_DESCRIPTION,
        )
        self.add_options()
        self.parse_options()

        log.setLevel(self.verbosity)
        log.debug('Logging level changed')

    def add_options(self):
        levels = ', '.join([str(lvl) for lvl in LOG_LEVELS])
        self.parser.add_argument(
            '-v', '--verbose',
            help='Set the verbosity {' + levels + '}',
            type=self.validate_verbosity,
        )

    def validate_verbosity(self, value):
        try:
            value = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError('verbosity is not and integer')
        if value not in LOG_LEVELS:
            raise argparse.ArgumentTypeError('verbosity level not from expected range')
        return value

    def parse_options(self):
        self.args = self.parser.parse_args()
        if self.args.verbose is not None:
            self.verbosity = self.args.verbose

    def run(self):
        raise RuntimeError('Not implemented yet!')
        pass

if __name__ == '__main__':
    app = CommandLineApp()
    app.run()
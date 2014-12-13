class ConnectionNotSetup(Exception):

    def __str__(self):
        return 'No connection defined. Setup connection with rod.connection.setup'
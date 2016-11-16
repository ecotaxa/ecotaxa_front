#serveur FTP gérant le fait d'avoir plusieurs home pour un user et
from appli.ftpserver.multirootserver import MultiRootAuthorizer,MultiRootHandler,MultiRootFS
from appli.ftpserver.pyftpdlib.servers import FTPServer
import os

def MyAuthenticator(username, password):
    if username == 'paul' and password == '12345':
        return {
            'home': {'common': os.path.join(os.getcwd(),'..','testftp','common')
                     ,'paul': os.path.join(os.getcwd(),'..','testftp','paul')
                     },
            'perm': 'elradfmwM',
            'operms': {},
            'msg_login': "Hello",
            'msg_quit': "Bye"
        }
    return None


def main():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = MultiRootAuthorizer()

    # Define a new user having full r/w permissions and a read-only
    # anonymous user

    # authorizer.add_user('paul', '12345',
    #                     {'common': os.path.join(os.getcwd(),'..','testftp','common')
    #                      ,'paul': os.path.join(os.getcwd(),'..','testftp','paul')
    #                       }
    #                     , perm='elradfmwM')
    # authorizer.add_anonymous(os.getcwd())

    # Instantiate FTP handler class
    handler = MultiRootHandler
    handler.authorizer = authorizer
    handler.abstracted_fs = MultiRootFS
    authorizer.alternateautheticator=MyAuthenticator

    # Define a customized banner (string returned when client connects)
    handler.banner = "pyftpdlib based ftpd ready."

    # Specify a masquerade address and the range of ports to use for
    # passive connections.  Decomment in case you're behind a NAT.
    # handler.masquerade_address = '151.25.42.11'
    # handler.passive_ports = range(60000, 65535)

    # Instantiate FTP server class and listen on 0.0.0.0:2121
    address = ('0.0.0.0', 21)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()

if __name__ == '__main__':
    main()

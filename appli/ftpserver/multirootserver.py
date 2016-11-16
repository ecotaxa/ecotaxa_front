#!/usr/bin/env python

# Copyright (C) 2007-2016 Giampaolo Rodola' <g.rodola@gmail.com>.
# Use of this source code is governed by MIT license that can be
# found in the LICENSE file.

"""A basic FTP server which uses a DummyAuthorizer for managing 'virtual
users', setting a limit for incoming connections.
"""

import os

from .pyftpdlib.authorizers import DummyAuthorizer,AuthenticationFailed
from .pyftpdlib.handlers import FTPHandler
from .pyftpdlib.filesystems import AbstractedFS,FilesystemError

import os,time,stat
import pathlib
from .pyftpdlib._compat import unicode


class MultiRootFS(AbstractedFS):
    """Represents a file system with multiple root associated to the login.


    """

    def __init__(self, root, cmd_channel):
        # AbstractedFS.__init__(self, root, cmd_channel)
        self._cwd = '/'
        self._root = root
        self.cmd_channel = cmd_channel


    def ftp2fs(self, ftppath):
        assert isinstance(ftppath, unicode), ftppath
        # as far as I know, it should always be path traversal safe...
        p = self.ftpnorm(ftppath)[1:]
        if p=='':
            return os.path.normpath('/VirtualRoot');
        splittedpath=pathlib.Path(p).parts
        # if splittedpath[0]=='': # s'il n'y a pas de / à la fin du path [0] est vide
        #     splittedpath=splittedpath[1::]
        root = self.root[splittedpath[0]]
        return os.path.normpath(os.path.join(root, *(splittedpath[1::])))
        return root;
        return os.path.normpath(os.path.join(self.root, p))

    def fs2ftp(self, fspath):
        assert isinstance(fspath, unicode), fspath
        for name,r in self.root.items():
            root = self.realpath(r)
            path = self.realpath(fspath)
            if path[0:len(root)] == root:
                return '/'+name+(path[len(root):].replace("\\",'/'))

        return '/' # sinon retourne /


    def chdir(self, path):
        if path[1::]=='VirtualRoot':
            self._cwd = '/'
            return # On ne fait rien car c'est une racine virtuelle

        """Change the current directory."""
        # note: process cwd will be reset by the caller
        assert isinstance(path, unicode), path
        os.chdir(path)
        self._cwd = self.fs2ftp(path)

    def listdir(self, path):
        if path[1::]=='VirtualRoot':
            return list(self._root.keys())

        """List the content of a directory."""
        assert isinstance(path, unicode), path
        return os.listdir(path)

    def isdir(self, path):
        if path[1::]=='VirtualRoot':
            return True
        """Return True if path is a directory."""
        assert isinstance(path, unicode), path
        return os.path.isdir(path)

    def validpath(self, path):
        """Check whether the path belongs to user's home directory.
        Expected argument is a "real" filesystem pathname.

        If path is a symbolic link it is resolved to check its real
        destination.

        Pathnames escaping from user's root directory are considered
        not valid.
        """
        if path[1::]=='VirtualRoot':
            return True # on peut toujours être dans la racine
        assert isinstance(path, unicode), path
        for r in self.root.values():
            root = self.realpath(r)
            path = self.realpath(path)
            if not root.endswith(os.sep):
                root = root + os.sep
            if not path.endswith(os.sep):
                path = path + os.sep
            if path[0:len(root)] == root:
                return True
        return False


    def format_mlsx(self, basedir, listing, perms, facts, ignore_err=True):
        """Return an iterator object that yields the entries of a given
        directory or of a single file in a form suitable with MLSD and
        MLST commands.

        Every entry includes a list of "facts" referring the listed
        element.  See RFC-3659, chapter 7, to see what every single
        fact stands for.

         - (str) basedir: the absolute dirname.
         - (list) listing: the names of the entries in basedir
         - (str) perms: the string referencing the user permissions.
         - (str) facts: the list of "facts" to be returned.
         - (bool) ignore_err: when False raise exception if os.stat()
         call fails.

        Note that "facts" returned may change depending on the platform
        and on what user specified by using the OPTS command.

        This is how output could appear to the client issuing
        a MLSD request:

        type=file;size=156;perm=r;modify=20071029155301;unique=8012; music.mp3
        type=dir;size=0;perm=el;modify=20071127230206;unique=801e33; ebooks
        type=file;size=211;perm=r;modify=20071103093626;unique=192; module.py
        """
        assert isinstance(basedir, unicode), basedir
        if self.cmd_channel.use_gmt_times:
            timefunc = time.gmtime
        else:
            timefunc = time.localtime
        permdir = ''.join([x for x in perms if x not in 'arw'])
        permfile = ''.join([x for x in perms if x not in 'celmp'])
        if ('w' in perms) or ('a' in perms) or ('f' in perms):
            permdir += 'c'
        if 'd' in perms:
            permdir += 'p'
        show_type = 'type' in facts
        show_perm = 'perm' in facts
        show_size = 'size' in facts
        show_modify = 'modify' in facts
        show_create = 'create' in facts
        show_mode = 'unix.mode' in facts
        show_uid = 'unix.uid' in facts
        show_gid = 'unix.gid' in facts
        show_unique = 'unique' in facts
        for basename in listing:
            retfacts = dict()
            if basedir[1::]=='VirtualRoot':
                file=self.root.get(basename)
            else:
                file = os.path.join(basedir, basename)
            # in order to properly implement 'unique' fact (RFC-3659,
            # chapter 7.5.2) we are supposed to follow symlinks, hence
            # use os.stat() instead of os.lstat()
            try:
                st = self.stat(file)
            except (OSError, FilesystemError):
                if ignore_err:
                    continue
                raise
            # type + perm
            # same as stat.S_ISDIR(st.st_mode) but slightly faster
            isdir = (st.st_mode & 61440) == stat.S_IFDIR
            if isdir:
                if show_type:
                    if basename == '.':
                        retfacts['type'] = 'cdir'
                    elif basename == '..':
                        retfacts['type'] = 'pdir'
                    else:
                        retfacts['type'] = 'dir'
                if show_perm:
                    retfacts['perm'] = permdir
            else:
                if show_type:
                    retfacts['type'] = 'file'
                if show_perm:
                    retfacts['perm'] = permfile
            if show_size:
                retfacts['size'] = st.st_size  # file size
            # last modification time
            if show_modify:
                try:
                    retfacts['modify'] = time.strftime("%Y%m%d%H%M%S",
                                                       timefunc(st.st_mtime))
                # it could be raised if last mtime happens to be too old
                # (prior to year 1900)
                except ValueError:
                    pass
            if show_create:
                # on Windows we can provide also the creation time
                try:
                    retfacts['create'] = time.strftime("%Y%m%d%H%M%S",
                                                       timefunc(st.st_ctime))
                except ValueError:
                    pass
            # UNIX only
            if show_mode:
                retfacts['unix.mode'] = oct(st.st_mode & 511)
            if show_uid:
                retfacts['unix.uid'] = st.st_uid
            if show_gid:
                retfacts['unix.gid'] = st.st_gid

            # We provide unique fact (see RFC-3659, chapter 7.5.2) on
            # posix platforms only; we get it by mixing st_dev and
            # st_ino values which should be enough for granting an
            # uniqueness for the file listed.
            # The same approach is used by pure-ftpd.
            # Implementors who want to provide unique fact on other
            # platforms should use some platform-specific method (e.g.
            # on Windows NTFS filesystems MTF records could be used).
            if show_unique:
                retfacts['unique'] = "%xg%x" % (st.st_dev, st.st_ino)

            # facts can be in any order but we sort them by name
            factstring = "".join(["%s=%s;" % (x, retfacts[x])
                                  for x in sorted(retfacts.keys())])
            line = "%s %s\r\n" % (factstring, basename)
            yield line.encode('utf8', self.cmd_channel.unicode_errors)


class MultiRootAuthorizer(DummyAuthorizer):
    def __init__(self):
        DummyAuthorizer.__init__(self)
        self.alternateautheticator=None


    def validate_authentication(self, username, password, handler):
        if username == 'anonymous':
            msg = "Anonymous access not allowed."
            raise AuthenticationFailed(msg)
        res=self.alternateautheticator(username, password)
        if res is not NotADirectoryError:
            self.user_table[username]=res
        else:
            raise AuthenticationFailed(msg)


    def add_user(self, username, password, homedirs, perm='elr',
                 msg_login="Login successful.", msg_quit="Goodbye."):
        if self.has_user(username):
            raise ValueError('user %r already exists' % username)
        for name,homedir in homedirs.items():
            if not isinstance(homedir, unicode):
                homedir = homedir.decode('utf8')
            if not os.path.isdir(homedir):
                raise ValueError('no such directory: %r' % homedir)
            homedirs[name] = os.path.realpath(homedir)
        self._check_permissions(username, perm)
        dic = {'pwd': str(password),
               'home': homedirs,
               'perm': perm,
               'operms': {},
               'msg_login': str(msg_login),
               'msg_quit': str(msg_quit)
               }
        self.user_table[username] = dic

class MultiRootHandler(FTPHandler):
    def __init__(self, conn, server, ioloop=None):
        FTPHandler.__init__(self, conn, server, ioloop=None)

    def handle_auth_success(self, home, password, msg_login):
        if len(msg_login) <= 75:
            self.respond('230 %s' % msg_login)
        else:
            self.push("230-%s\r\n" % msg_login)
            self.respond("230 ")
        self.log("USER '%s' logged in." % self.username)
        self.authenticated = True
        self.password = password
        self.attempted_logins = 0

        self.fs = self.abstracted_fs(home, self)
        self.on_login(self.username)


    def ftp_RNFR(self, path):
        """Rename the specified (only the source name is specified
        here, see RNTO command)"""
        if not self.fs.lexists(path):
            self.respond("550 No such file or directory.")
        else:
            for r in self.fs.root.values():
                if self.fs.realpath(path) == self.fs.realpath(r):
                    self.respond("550 Can't rename home directory.")
                    break;
            else:
                self._rnfr = path
                self.respond("350 Ready for destination name.")

# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from flask_security import SQLAlchemyUserDatastore

import werkzeug.contrib.cache
import threading

# Ce datastore permet de mettre en cache les utilisateurs
class SQLAlchemyUserDatastoreCACHED (SQLAlchemyUserDatastore):
    """ Version integrant un cache du Datastore
    """
    def __init__(self, db, user_model, role_model):
        # print("******************* SQLAlchemyUserDatastoreCACHED INIT  ********************* ")
        SQLAlchemyUserDatastore.__init__(self, db, user_model, role_model)
        self.cache_users = werkzeug.contrib.cache.SimpleCache(threshold=500, default_timeout=300) # 5 minutes
        self.lock = threading.Lock()  # on compense que simple cache n'est pas thread safe

    def get_user(self, identifier):
        #A Chaque login on cleanne le cache, ca permet d'avoir un effet immediat sur les modification en base
        with self.lock:
            self.cache_users.clear()
        return super().get_user(identifier)

    def find_user(self, **kwargs):
        # print("******************* find_user  ********************* %s"%kwargs)
        with self.lock:
            if "id" in kwargs:
                u=self.cache_users.get(kwargs["id"])
            else:
                u=None
            if u is None:
                u=self.user_model.query.filter_by(**kwargs).first()
                if (u is not None) and ("id" in kwargs):
                    tmprole=u.roles # used to force quering Database
                    self.cache_users.set(kwargs["id"],u)
            return u
    def ClearCache(self):
        with self.lock:
            self.cache_users.clear()
    # MAJ impossible  les objets ne sont pas muttable et current user n'est pas picklable
    # donc on prend la strategie de clear du cache quand c'est requis.
    # def update_user(self,user):
    #     with self.lock:
    #         u=self.cache_users.get(str(getattr(user,"id")))
    #         if u is not None:
    #             for k in user.__dict__.keys():
    #                 u[k]=user.__dict__.get(k)
    #             self.cache_users.set(getattr(user,"id"),u)




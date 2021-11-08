import datetime

from flask import g
import psycopg2.extras

# Use EcoTaxa DB interface, TODO: Remove
from appli import db

GlobalDebugSQL = False


def GetAssoc2Col(sql, params=None, debug=False, dicttype=dict):
    from .ecopart_blueprint import part_app
    if g.db is None:
        g.db = db.engine.raw_connection()
    cur = g.db.cursor()
    starttime = datetime.datetime.now()
    try:
        cur.execute(sql, params)
        res = dicttype()
        for r in cur:
            res[r[0]] = r[1]
    except psycopg2.InterfaceError:
        part_app.logger.debug("Connection was invalidated!, Try to reconnect for next HTTP request")
        db.engine.connect()
        raise
    except:  # noqa
        part_app.logger.debug("GetAssoc2Col  Exception SQL = %s %s", sql, params)
        cur.connection.rollback()
        raise
    finally:
        if debug or GlobalDebugSQL:
            part_app.logger.debug("GetAssoc2Col (%s) SQL = %s %s",
                                  (datetime.datetime.now() - starttime).total_seconds(),
                                  sql, params)
        cur.close()
    return res

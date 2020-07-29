from typing import Any, Dict, List, Tuple

from psycopg2.extras import DictCursor


class RawConnection(object):
    """
        A wrapper onto SQLAlchemy/DBApi raw connection.
    """

    def __init__(self, cnx):
        self.cnx = cnx

    def get(self, sql: str, params: Any) -> List[Tuple]:
        """ Simple select """
        with self.cnx.cursor() as cur:
            cur.execute(sql, params)
            ret = cur.fetchall()
        return ret

    def get_as_dict(self, sql: str, params: Any, index_on: str) -> Dict[Any, Dict]:
        """ Select, then output a dict of dicts with given column (unique) as index """
        with self.cnx.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, params)
            # Index the result
            ret = {row[index_on]: row for row in cur.fetchall()}
        return ret

    def execute(self, sql: str, params: Any) -> int:
        """ Execute an insert/delete/update, return the number of updated rows """
        with self.cnx.cursor() as cur:
            cur.execute(sql, params)
            ret = cur.rowcount
        return ret

    def executemany(self, sql: str, params: Any):
        with self.cnx.cursor() as cur:
            cur.executemany(sql, params)
            ret = cur.rowcount
        return ret

    def commit(self):
        self.cnx.commit()

    def rollback(self):
        self.cnx.rollback()

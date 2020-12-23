# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
# Some classes around displayed parts in page
#
from appli.database import GetAll


class ClassificationPageStats(object):
    """
        Top animated bar with statistics about current project + current filters.
    """

    def __init__(self, where_clause: str, sql_param: dict):
        sqlcount = """select count(*)
            ,count(case when classif_qual='V' then 1 end) NbValidated
            ,count(case when classif_qual='D' then 1 end) NbDubious
            ,count(case when classif_qual='P' then 1 end) NbPredicted
            from objects o
                 JOIN acquisitions acq on o.acquisid=acq.acquisid
            """ + where_clause
        # Optimisation pour des cas simples et fréquents
        if where_clause == ' where o.projid=%(projid)s ':
            sqlcount = """select sum(nbr),sum(nbr_v) NbValidated,sum(nbr_d) NbDubious,sum(nbr_p) NbPredicted 
                        from projects_taxo_stat 
                        where projid=%(projid)s """
        if where_clause == ' where o.projid=%(projid)s  and o.classif_id=%(taxo)s ':
            sqlcount = """select sum(nbr),sum(nbr_v) NbValidated,sum(nbr_d) NbDubious,sum(nbr_p) NbPredicted 
                    from projects_taxo_stat 
                    where projid=%(projid)s and id=%(taxo)s"""
        if where_clause == " where o.projid=%(projid)s  and o.classif_id=%(taxo)s  and o.classif_qual!='V'":
            sqlcount = """select sum(nbr-nbr_v),0 NbValidated,sum(nbr_d) NbDubious,sum(nbr_p) NbPredicted 
                    from projects_taxo_stat 
                    where projid=%(projid)s and id=%(taxo)s"""

        (self.nbrtotal, self.nbrvalid, self.nbrdubious, self.nbrpredict) = GetAll(sqlcount, sql_param, debug=False)[0]
        if self.nbrtotal is None:
            # Empty table
            self.nbrtotal = self.nbrvalid = self.nbrdubious = self.nbrpredict = 0
            self.are_valid = False
        else:
            self.are_valid = True

    def render(self):
        if self.nbrtotal > 0:
            pctvalid = 100 * self.nbrvalid / self.nbrtotal
            pctpredict = 100 * self.nbrpredict / self.nbrtotal
            pctdubious = 100 * self.nbrdubious / self.nbrtotal
            nbrothers = self.nbrtotal - self.nbrvalid - self.nbrpredict - self.nbrdubious
            txtpctvalid = "<span style=\"color:#0A0\">%0d </span>, " \
                          "<span style=\"color:#5bc0de\">%0d </span>, " \
                          "<span style=\"color:#F0AD4E\">%0d</span>, " \
                          "<span style=\"color:#888\">%0d </span>" % (
                              self.nbrvalid, self.nbrpredict, self.nbrdubious, nbrothers)
        else:
            txtpctvalid = "-"
            pctdubious = pctpredict = pctvalid = 0
        return """
        <script>
            $('#objcount').html('{0} / {1} ');
            $('#progress-bar-validated').css('width','{2}%');
            $('#progress-bar-predicted').css('width','{3}%');
            $('#progress-bar-dubious').css('width','{4}%');
        </script>""".format(txtpctvalid, self.nbrtotal, pctvalid, pctpredict, pctdubious)

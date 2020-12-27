# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
# Some classes around displayed parts in page
#
from appli import ScaleForDisplay, ntcv
from appli.database import GetAll


class ClassificationPageStats(object):
    """
        Top animated bar with statistics about current project + current filters.
    """

    def __init__(self, where_clause: str, sql_params: dict):
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

        (self.nbrtotal, self.nbrvalid, self.nbrdubious, self.nbrpredict) = GetAll(sqlcount, sql_params, debug=False)[0]
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


class PopoverPane(object):
    """
        A small hint-style window giving a set of information about the image.
    """

    def __init__(self, field_list, row):
        self.fielf_list = field_list
        self.row = row

    def render(self, width_on_row):
        row = self.row
        poptitletxt = "%s" % (row['orig_id'],)
        poptxt = ""
        # poptxt="<p style='white-space: nowrap;color:black;'>cat. %s"%(r['taxoname'],)
        if ntcv(row['classifwhoname']) != "":
            poptxt += "<em>by</em> %s<br>" % (row['classifwhoname'])
        poptxt += "<em>parent</em> " + ntcv(row['taxoparent'])
        poptxt += "<br><em>in</em> " + ntcv(row['samplename'])
        for k, v in self.fielf_list.items():
            if k == 'classif_auto_score' and row["classif_qual"] == 'V':
                poptxt += "<br>%s : %s" % (v, "-")
            else:
                poptxt += "<br>%s : %s" % (v, ScaleForDisplay(row["extra_" + k]))
        if row['classif_when']:
            poptxt += "<br>Validation date : %s" % (ntcv(row['classif_when']),)
        return "data-title=\"{0}\" data-content=\"{1}\" data-placement='{2}'". \
            format(poptitletxt, poptxt, 'left' if width_on_row > 500 else 'right')

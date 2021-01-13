# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
# Some classes around displayed parts in page
#
import json

from appli import ScaleForDisplay, ntcv


class ClassificationPageStats(object):
    """
        Top animated bar with statistics about current project + current filters.
    """
    @staticmethod
    def render(filters, projid):
        # Make API call params from filters
        form_json = json.dumps(filters)
        ajax_call = """
        <script>
            $.ajax({
              type: "POST",
              url: "/api/object_set/%s/summary?only_total=False",
              data: JSON.stringify(%s),""" % (projid, form_json)
        ajax_call += """  
              contentType: "application/json; charset=utf-8",
              dataType: "json",
              success: function(rsp) {
                nbr = rsp['total_objects'];
                if (nbr == 0) {
                  txt_valid = "-";
                  pct_valid = 0;
                  pct_predict = 0;
                  pct_dubious = 0;
                } else {
                  nbr_v = rsp['validated_objects'];
                  nbr_d = rsp['dubious_objects'];
                  nbr_p = rsp['predicted_objects'];
                  nbr_o = nbr - nbr_v - nbr_d - nbr_p;
                  txt_valid = '<span style="color:#0A0">'+nbr_v+' </span>,'+ 
                              '<span style="color:#5bc0de"> '+nbr_p+' </span>,'+ 
                              '<span style="color:#F0AD4E"> '+nbr_d+' </span>,'+
                              '<span style="color:#888"> '+nbr_o+' </span> / '+nbr;
                  pct_valid = Math.round(100 * nbr_v / nbr);
                  pct_predict = Math.round(100 * nbr_p / nbr);
                  pct_dubious = Math.round(100 * nbr_d / nbr);
                }
                $('#objcount').html(txt_valid);
                $('#progress-bar-validated').css('width',pct_valid+'%');
                $('#progress-bar-predicted').css('width',pct_predict+'%');
                $('#progress-bar-dubious').css('width',pct_dubious+'%');
              },
              error: function(jqXHR, textStatus, errorThrown) {
                $('#objcount').html('<span>'+textStatus+errorThrown+'</span>');
              }
            });
        </script>"""
        return ajax_call


class PopoverPane(object):
    """
        A small hint-style window giving a set of information about the image.
    """

    def __init__(self, field_list, row):
        self.field_list = field_list
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
        for k, v in self.field_list.items():
            if k == 'classif_auto_score' and row["classif_qual"] == 'V':
                poptxt += "<br>%s : %s" % (v, "-")
            else:
                poptxt += "<br>%s : %s" % (v, ScaleForDisplay(row["extra_" + k]))
        if row['classif_when']:
            poptxt += "<br>Validation date : %s" % (ntcv(row['classif_when']),)
        return "data-title=\"{0}\" data-content=\"{1}\" data-placement='{2}'". \
            format(poptitletxt, poptxt, 'left' if width_on_row > 500 else 'right')

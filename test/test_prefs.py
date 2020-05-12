import json
from unittest import TestCase
from appli.database import users

prefs_json = """{"1342": {"magenabled": "0", "dispfield": "", "ipp": "100", 
"sortby": "", "zoom": "200", "popupenabled": "0", "sortorder": "asc", "statusfilter": "V", "ts": 1554131253.4825027}, 
"50": {"MapN": "", "freenum": "", "instrum": "", "sortby": "depth_min", "freenumend": "", "popupenabled": "0", 
"daytime": "", "filt_annot": "", "freetxtval": "", "freetxt": "", "zoom": "200", "fromtime": "", 
"samples": "19732,19756,19704,19739,19720,19733,19726,19759,19718,19749", "inverttime": "", "MapE": "", 
"magenabled": "0", "freenumst": "", "MapW": "", "todate": "", "depthmin": "", "sortorder": "asc", "month": "", 
"totime": "", "dispfield": " dispfield_n19 dispfield_depth_min dispfield_n16 dispfield_n02", "fromdate": "", "MapS": "",
 "depthmax": "", "ipp": "1000", "statusfilter": "", "ts": 1569857780.572837}}"""


class TestPrefs(TestCase):
    def test_TooBig(self):
        prefs = json.loads(prefs_json)
        assert len(prefs) == 2
        prefs["998"] = prefs["1342"].copy()
        prefs["999"] = prefs["1342"].copy()
        prefs["999"]["ts"] = 5666 # _Really_ old one as it's a timestamp
        assert len(prefs) == 4
        # Enough space to hold the extra entries
        same_prefs = json.loads(users.keep_last_if_too_large(prefs, 40000))
        assert len(same_prefs) == 4
        # Remove oldest one
        smaller_prefs = json.loads(users.keep_last_if_too_large(prefs, 1000))
        assert len(smaller_prefs) == 3
        # 999 is gone
        assert "999" not in smaller_prefs
        # Extreme case
        no_prefs_left = json.loads(users.keep_last_if_too_large(prefs, 100))
        assert len(no_prefs_left) == 0

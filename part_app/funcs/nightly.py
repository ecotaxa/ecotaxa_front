from part_app.db_utils import ExecSQL


def ComputeOldestSampleDateOnProject():
    # EcoPart stats update
    ExecSQL("update part_projects pp  "
            "   set oldestsampledate=(select min(sampledate) "
            "                          from part_samples ps "
            "                         where ps.pprojid=pp.pprojid)")
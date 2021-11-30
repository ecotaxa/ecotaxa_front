__all__ = ["drawchart", "sampleedit", "prjedit", "prj", "part_main", "filesystem", "security"]

from flask import render_template, g

from ..db_utils import GetAssoc2Col
from ..remote import EcoTaxaInstance


def part_AddTaskSummaryForTemplate(ecotaxa_if: EcoTaxaInstance):
    """
        Set in global 'g' a structure to show what is currently ongoing on task side.
        @see part/layout.html
    """
    ecotaxa_user = ecotaxa_if.get_current_user()
    if ecotaxa_user is not None:
        g.tasksummary = GetAssoc2Col(
            "SELECT taskstate,count(*) from temp_tasks WHERE owner_id=%(owner_id)s group by taskstate"
            , {'owner_id': ecotaxa_user.id})
    # TODO (or not) g.google_analytics_id = app.config.get('GOOGLE_ANALYTICS_ID', '')


def part_PrintInCharte(ecotaxa_if: EcoTaxaInstance, txt, title=None):
    """
    Permet d'afficher un texte (qui ne sera pas echappé dans la charte graphique)
    :param txt: Texte à afficher
    :return: Texte rendu
    """
    part_AddTaskSummaryForTemplate(ecotaxa_if)
    if not title:
        title = 'EcoPart'
    return render_template('part/layout.html', bodycontent=txt, title=title)


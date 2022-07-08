# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from typing import List, Dict, Optional
from flask import g, render_template, request
from flask_login import current_user
from appli.constants import GUI_PATH, TRANSLATION_PATH, DEFAULT_LOCALE
from gettext import NullTranslations


def ExperimentalHeader() -> str:
    # Add experimental URL
    path = request.path

    if path.find(GUI_PATH) < 0:
        print("gui_path new=" + GUI_PATH)
        hint = "A better version of this page is available."
        experimental = (
            "<a class="
            + '"inline-block py-2 px-3 text-center whitespace-nowrap align-baseline" style="margin-top:0;margin-right:175px;z-index:100;color:#333;font-weight:bold;font-size:0.925rempadding:.25rem .5rem;text-shadow:2px 2px 6px #FFaa00;" href="'
            + GUI_PATH
            + path
            + '" title="'
            + hint
            + '">'
            + "New!</a>"
        )

    else:
        hint = "Back to current version."
        experimental = (
            '<a  class="experimental" href="'
            + path.replace(GUI_PATH, "")
            + '"  title="'
            + hint
            + '">Back</a>'
        )
    return experimental


def JobsSummaryData() -> Dict:
    """
    Return a structure to show what is currently ongoing on jobs side.
    """
    if current_user.is_authenticated:
        # Summarize from back-end
        from appli.jobs.emul import _build_jobs_summary

        return _build_jobs_summary()
    return ""


def WebStats(app) -> str:
    return app.config.get("GOOGLE_ANALYTICS_ID", "")


def RenderTemplate(
    filename="index", templates="v2/", title="EcoTaxa 2.6", webstats=""
) -> str:
    import os

    jobs_summary = JobsSummaryData()
    experimental = ExperimentalHeader()
    if filename[-1] == "/":
        filename = filename[:-1]
    if not os.path.exists("appli/templates/" + templates + filename + ".html"):
        return render_template(
            templates + filename + ".html",
            jobs_summary=jobs_summary,
            webstats=webstats,
            experimental=experimental,
            title=title,
            gui=GUI_PATH + "/",
        )


def find_language() -> NullTranslations:

    # Get the browser current language
    import gettext

    # see https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1 to get all the 2 digits country codes
    KNOWN_LANGAGES = [
        "en",
        "pt",
        "zh",
        "fr",
    ]  # TODO put this constant in ecotaxa_dev/appli/project/__init__.py ?
    curLang: str = ""
    prefLangs = request.accept_languages
    if prefLangs is not None:
        # Here, there is at least one language
        # First one is the prefered language in the list of handled languages
        for l in prefLangs:
            curLang = l[0][
                :2
            ]  # first 2 letters show the country, and translations tables folders are organised this way
            if curLang in KNOWN_LANGAGES:
                try:  # N.B. [curLang] and not curLang in the following line
                    lang = gettext.translation(
                        "ecotaxa", "messages", [curLang]
                    )  # curLang == 'fr' or 'en' or 'zh' or 'pt' ...
                    okCurLang = True
                except:  # language corrupted or not existing
                    okCurLang = False
                if okCurLang:
                    lang.install()
                    return lang
            # try the next language
    # Tried all the languages without success, or there is no supported langage
    curLang = "en"  # desperate, so take english as last solution
    lang = gettext.translation("ecotaxa", "messages", [curLang])
    lang.install()
    return lang

from gettext import NullTranslations

from flask import request, render_template

from appli.project.index_vue import PrintInCharte_bs5


def index_vue() -> str:
    language = find_language()
    return PrintInCharte_bs5(
        # EcoTaxa_about_page and Welcome_to_EcoTaxa not yet used here
        render_template("project/about_ecotaxa.html",
                        EcoTaxa_is_a_web_application=language.gettext("EcoTaxa_is_a_web_application"),
                        If_you_use_EcoTaxa=language.gettext("If_you_use_EcoTaxa"),
                        The_development_of_EcoTaxa=language.gettext("The_development_of_EcoTaxa"),
                        Sorbonne_Universite_and_CNRS=language.gettext("Sorbonne_Universite_and_CNRS"),
                        The_Programme_Investissements_d_Avenir=language.gettext(
                            "The_Programme_Investissements_d_Avenir"),
                        The_Partner_University_Fund=language.gettext("The_Partner_University_Fund"),
                        The_CNRS_LEFE_program=language.gettext("The_CNRS_LEFE_program"),
                        The_Belmont_Forum=language.gettext("The_Belmont_Forum"),
                        The_Watertools_company=language.gettext("The_Watertools_company"),
                        The_maintenance_of_the_software=language.gettext("The_maintenance_of_the_software"),
                        The_persons_who_made_EcoTaxa=language.gettext("The_persons_who_made_EcoTaxa"),
                        Marc_Picheral_and=language.gettext("Marc_Picheral_and"),
                        Sebastien_Colin=language.gettext("Sebastien_Colin"),
                        Developers=language.gettext("Developers"),
                        Deep_learning=language.gettext("Deep_learning"),
                        testing_and_feedback=language.gettext("testing_and_feedback"),
                        Disclaimer=language.gettext("Disclaimer")
                        )
    )


def find_language() -> NullTranslations:
    # Get the browser current language
    import gettext
    # see https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1 to get all the 2 digits country codes
    KNOWN_LANGAGES = ['en', 'pt', 'zh',
                      'fr']  # TODO put this constant in ecotaxa_dev/appli/project/__init__.py ?
    curLang: str = ''
    prefLangs = request.accept_languages
    if prefLangs is not None:
        # Here, there is at least one language
        # First one is the prefered language in the list of handled languages
        for l in prefLangs:
            curLang = l[0][
                      :2]  # first 2 letters show the country, and translations tables folders are organised this way
            if curLang in KNOWN_LANGAGES:
                try:  # N.B. [curLang] and not curLang in the following line
                    lang = gettext.translation('ecotaxa', 'messages',
                                               [curLang])  # curLang == 'fr' or 'en' or 'zh' or 'pt' ...
                    okCurLang = True
                except:  # language corrupted or not existing
                    okCurLang = False
                if okCurLang:
                    lang.install()
                    return lang
            # try the next language
    # Tried all the languages without success, or there is no supported langage
    curLang = 'en'  # desperate, so take english as last solution
    lang = gettext.translation('ecotaxa', 'messages', [curLang])
    lang.install()
    return lang

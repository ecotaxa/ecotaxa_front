from flask_babel import _

# 2 Marc ,4 JO ,5 Amanda, 75 Laetitia, 1267 & 1604 Julie, 760 & 1080 & 878 Laurent, 193 Louis , 847 Zoe,768 Camille, 1001 Lucas , Bea 1562, 358 Solène // 1601 pour test sur db test
vip_list = [2, 4, 5, 75, 1001, 847, 1267, 1604, 358, 1562, 1601]
# paths
newpath = [
    "login",
    "prj",
    "prj/edit",
    "prj/",
    "prj/listall",
    "prj/listall/",
    "about",
    "privacy",
]
# sponsors - page about ecotaxa
sponsors = list(
    [
        {
            "name": _("Sorbonne Universite and CNRS"),
            "sponsors": [
                {
                    "url": "https://www.sorbonne-universite.fr/",
                    "logo": "Logo_Sorbonne_Universite.png",
                    "name": "Sorbonne Université",
                },
                {
                    "url": "http://www.cnrs.fr/",
                    "logo": "LOGO_CNRS_2019_RVB.png",
                    "name": "CNRS",
                },
            ],
            "text": _(
                "Sorbonne University and the CNRS, which pay the salaries of the permanent staff responsible for supervising its development."
            ),
        },
        {
            "name": _("The Programme Investissements d'Avenir"),
            "url": "https://www.gouvernement.fr/le-programme-d-investissements-d-avenir",
            "logo": "marianne.png",
            "text": _(
                "The Future Investments Program  which financed the development of the original version of the application through the Oceanomics project, dedicated to the analysis of Tara Oceans samples [45k €]."
            ),
        },
        {
            "name": _("The Partner University Fund"),
            "url": "https://face-foundation.org/higher-education/partner-university-fund/",
            "logo": "Face-Logo.svg",
            "text": _(
                "The Partner University Fund  that funded the hardware on which EcoTaxa ran for several years and the machine learning solution it permitted, through a joint project between Université Pierre et Marie Curie (now Sorbonne Université) and the University of Miami [15k€]."
            ),
        },
        {
            "name": _("The CNRS LEFE program"),
            "url": "https://programmes.insu.cnrs.fr/lefe/",
            "logo": "Logo-LEFE.jpg",
            "text": _(
                "The CNRS LEFE program that allowed to renew the machine learning backend, through the project DL-PIC [10k€]."
            ),
        },
        {
            "name": _("The Belmont Forum"),
            "url": "https://www.belmontforum.org/",
            "logo": "bf-logo.png",
            "text": _(
                "The Belmont Forum, which funds an overall review of the application through the WWWPIC project [500k€]."
            ),
        },
        {
            "name": _("The Watertools company"),
            "url": "http://www.watertools.cn/",
            "logo": "bocweb_logo.png",
            "text": _(
                "The Watertools company, who donated money to make the interface of EcoTaxa easier to translate, in Chinese in particular [30k€]."
            ),
        },
    ]
)
py_messages = dict(
    {
        "nomanager": _(
            "A manager person needs to be designated among the current project persons"
        ),
        "nobody": _("One person, at least, needs to be related to the project"),
        "nocontact": _(
            "A contact person needs to be designated among the current project managers."
        ),
        "emptyname": _(
            "A privilege is incomplete. Please select a member name or delete the privilege row"
        ),
        "oneatleast": _(
            "One member at least is required with Manage privilege and contact property  "
        ),
        "uhasnopriv": _("privilege is missing"),
        "taxosynchro": _(
            "Taxonomy synchronization and Ecotaxa version check wasn’t done during the last 7 days. Ask application administrator to do it."
        )
        + ' <a href="/taxo/browse/" class="underline underline-offset-2 font-normal text-sm">'
        + _("Synchronize to check Ecotaxa version")
        + "</a>",
        "possiblemodel404": _("Error retrieving possible models"),
        "license404": _("Error retrieving licenses"),
        "project404": _("Project does not exist"),
        "page404": _("The page does not exists."),
        "access403": _("Access not authorized "),
        "cannotaccessinfo": _("You cannot access this information"),
        "cannoteditsettings": _("You cannot edit settings for this project"),
        "nouserslist": _("No users list"),
        "noauthoprjcreate": _("Not authorized to create a project"),
        "noauthoprjedit": _("Not authorized to edit a project"),
        "titleinstrumentrequired": _("A project must have a title and instrument"),
        "modinstrumentwarning": _(
            "Changing the instrument associated with a project may affect the behaviour of EcoTaxa in various ways and should not be done except to correct a mistake."
        ),
        "errorprojectcreate": _("Error in project creation"),
        "scnerased": _("SCN features erased"),
        "memberexistdifferentpriv": _(
            "Member already registered with differents privileges "
        ),
        "privnotsetfor": _("Privileges are not set for member "),
        "membernomoreinlist": _("Error member to be added is no more in users list "),
        "getcontactuserinmanagers": _(
            "A contact person needs to be designated among the current project managers. "
        ),
        "managerrequired": _("At least one manager is needed"),
        "updateexception": _("Update problem: "),
        "projectupdated": _("Project updated"),
        "importpriverror": _("Privileges where not imported correctly."),
    }
)

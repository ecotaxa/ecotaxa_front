from flask_babel import _

# sponsors - page about ecotaxa
sponsors = list(
    [
        dict(
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
            }
        ),
        dict(
            {
                "name": _("The Future Investments Program"),
                "url": "https://www.gouvernement.fr/le-programme-d-investissements-d-avenir",
                "logo": "marianne.png",
                "text": _(
                    "which financed the development of the original version of the application through the Oceanomics project, dedicated to the analysis of Tara Oceans samples."
                ),
            }
        ),
        dict(
            {
                "name": _("The Partner University Fund"),
                "url": "https://face-foundation.org/higher-education/partner-university-fund/",
                "logo": "Face-Logo.svg",
                "text": _(
                    "funded the hardware on which EcoTaxa ran for several years and the machine learning solution it permitted, through a joint project between Université Pierre et Marie Curie (now Sorbonne Université) and the University of Miami."
                ),
            }
        ),
        dict(
            {
                "name": _("The CNRS LEFE program"),
                "url": "https://programmes.insu.cnrs.fr/lefe/",
                "logo": "Logo-LEFE.jpg",
                "text": _(
                    "which allowed to renew the machine learning backend, through the project DL-PIC."
                ),
            }
        ),
        dict(
            {
                "name": _("The Belmont Forum"),
                "url": "https://www.belmontforum.org/",
                "logo": "bf-logo.png",
                "text": _(
                    "which that funded an overall review of the application through the WWWPIC project."
                ),
            }
        ),
        dict(
            {
                "name": _("The Watertools company"),
                "url": "http://www.watertools.cn/",
                "logo": "bocweb_logo.png",
                "text": _(
                    "which donated money to make the interface of EcoTaxa easier to translate, in Chinese in particular."
                ),
            }
        ),
        dict(
            {
                "name": _("The France Relance program"),
                "url": "https://www.enseignementsup-recherche.gouv.fr/fr/le-plan-de-relance-pour-l-enseignement-superieur-la-recherche-et-l-innovation-49706",
                "logo": "mesri-logo-ia-et-france-relance-13037.jpg",
                "text": _(
                    "that funded a joint project with the company FOTONOWER [https://fotonower.com/], which explored machine learning solutions to improve the automatic classification system in EcoTaxa as well as implement visual similarity search."
                ),
            }
        ),
        dict(
            {
                "name": _("The European Commission"),
                "url": "https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe_en",
                "logo": "European_Commission_logo.png",
                "text": _(
                    "that funded EcoTaxa's development through the Horizon programs, via the projects presented thereafter."
                ),
            }
        ),
        dict(
            {
                "name": _("The JERICO-S3 project"),
                "url": "https://www.jerico-ri.eu/projects/jerico-s3/",
                "logo": "jerico-s3-logo.png",
                "text": _(
                    "which allowed the development of software pipelines to input data in EcoTaxa and supported the overall running of the service."
                ),
            }
        ),
        dict(
            {
                "name": _("The Blue-Cloud project"),
                "url": "https://cordis.europa.eu/project/id/101094227",
                "logo": "blue-cloud-logo.png",
                "text": _(
                    "which funded the extension of EcoTaxa's Application Programming Interface to allow it to interact with their data querying system."
                ),
            }
        ),
        dict(
            {
                "name": _("The Blue-Cloud2026 project"),
                "url": "https://blue-cloud.org/",
                "logo": "eosc-blue-cloud-2026-logo.png",
                "text": _(
                    "which extended the work of the first Blue-Cloud project to allow finer querying of EcoTaxa's data through its Application Programming Interface and more accessible data thanks to the increased use of standard vocabularies."
                ),
            }
        ),
        dict(
            {
                "name": _("The DTO-BioFlow project"),
                "url": "https://dto-bioflow.eu/",
                "logo": "dto-bioflow-logo.jpg",
                "text": _(
                    "which facilitated the flow of high quality data from EcoTaxa to the Digital Twin of the Ocean by improving quality control procedures before EcoTaxa and in its output as a DarwinCore Archive files."
                ),
            }
        ),
        dict(
            {
                "name": _("The ANERIS project"),
                "url": "https://aneris.eu/",
                "logo": "aneris-logo.png",
                "text": _(
                    "which funded the development of dedicated pipelines for the automatic processing of images using EcoTaxa as a quality checking solution."
                ),
            }
        ),
    ]
)

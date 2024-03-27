from flask_babel import _


# breadcrumb tree
apptree = dict(
    {
        "": "Home",
        "prj": {
            "root": _("Projects"),
            "one": _("Project"),
            "children": {
                "create": _("create"),
                "edit": _("settings"),
                "import": _("import"),
                "export": _("export"),
                "predict": _("predict"),
                "annotate": _("annotate"),
                "about": _("about"),
                "merge": _("merge"),
                "editannot": _("edit or erase"),
                "editdatamass": _("batch edit"),
                "resettopredicted": _("reset"),
                "purge": _("delete"),
                "taxofix": _("fix"),
            },
        },
        "collection": {
            "root": _("Collections"),
            "one": _("Collection"),
            "children": {
                "create": _("create"),
                "edit": _("settings"),
                "import": _("import"),
                "export": _("export"),
                "about": _("about"),
                "purge": _("delete"),
            },
        },
        "jobs": _("Jobs"),
        "job": {
            "root": _("Job"),
            "children": {
                "show": _("View"),
                "create": {
                    "children": {
                        "GenExport": _("export"),
                        "GeneralExport": _("general export"),
                        "BackupExport": _("backup export"),
                        "SummaryExport": _("summary export"),
                        "Subset": _("subset"),
                    }
                },
            },
        },
        "privacy": _("Privacy"),
        "about": _("About Ecotaxa"),
    }
)
# flash and error messages
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
        "notauthorized": _("Not authorized"),
        "noduplicate": _(
            "It is strongly recommended to modify this field to avoid duplicates"
        ),
        "modify": _("Modify"),
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
        "access403": _("Access denied "),
        "accessonly": {
            "manage": _("Visible only by managers"),
            "manageannotate": _("Visible only by managers and annotators"),
        },
        "cannotaccessinfo": _("You cannot access this information"),
        "cannoteditsettings": _("You cannot edit settings for this project"),
        "selectotherproject": _("Select another project"),
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
        "projectcreated": _("Project created"),
        "projectupdated": _("Project updated"),
        "importpriverror": _("Privileges where not imported correctly."),
        "viewfull": _("view full message"),
        "alerttype": {
            "danger": _("IMPORTANT :"),
            "warning": _("WARNING:"),
            "info": _("INFORMATION:"),
            "success": _("SUCCESS:"),
            "error": _("ERROR:"),
            "maintenance": _("MAINTENANCE"),
        },
    }
)
py_user = dict(
    {
        "invalidpassword": _("Invalid credentials"),
        "invaliddata": _("Data are not valid"),
        "notadmin": _("Not an administrator"),
        "notfound": _("Not found"),
        "exists": _("User exists"),
        "novalidationservices": _("Service is not active"),
        "notauthorized": _("Not authorized"),
        "checkspam": _(
            "Please, check spam and junk mails if you can't find this email in your inbox."
        ),
        "badsignature": _("Token is not valid"),
        "signexpired": _("Signature expired"),
        "status": {
            "active": "Account active",
            "pending": "Account waiting for email confirmation",
            "blocked": "Account blocked",
            "inactive": "Account desactivated",
        },
        "profilesuccess": {
            "create": _("Account created"),
            "update": _("Account updated"),
            "activate": _("Thank you for the confirmation. You can log in."),
        },
        "mailsuccess": _(
            " A confirmation email has been sent to the email address provided. Click on the link therein to verify it."
        ),
        "profileerror": {
            "create": _("Account not created"),
            "update": _("Account not updated"),
            "activate": _("Account not activated."),
        },
        "mailerror": _("Confirmation email  not sent."),
        "errusrid": _("Wrong user id"),
        "usernoaction": _("No action specified"),
        "passwordrequired": _("Password required"),
        "activationrequest": _(
            "An activation request has been sent to the administrator. You will receive instructions to modify your email which is no longer accepted."
        ),
        "passwordrule": _(
            "The password must be : - minimum length 8 - 1 or more numeric - 1 or more uppercase - 1 or more lowercase - 1 or more  "
        ),
        "wrongstatus": _("Status value error"),
        "statusnotauthorized": {
            "2": _("Please modify your personal data as requested before by email."),
            "-1": _("Access denied "),
            "0": _("Account desactivated."),
            "00": _("Account desactivated. Could be waiting for email confirmation."),
            "01": _(
                "Account waiting for validation. We will verify your informations and activate your account. You will be informed by email of any issue.",
            ),
            "waiting": _("Account is waiting for mail confirmation."),
            "emailchanged": _(
                "You have changed your email address and need to verify this new address. A confirmation email has been sent to this new address. Click on the link therein to verify it. "
            ),
        },
    }
)
py_project_rights = dict(
    {
        "managers": _("Manage"),
        "annotators": _("Annotate"),
        "viewers": _("View"),
    }
)
py_user_roles = dict(
    {
        "managers": _("Manager"),
        "annotators": _("Annotator"),
        "viewers": _("Viewer"),
    }
)
py_project_status = dict(
    {
        "Annotate": _("Annotate"),
        "ExploreOnly": _("Explore Only"),
        "Annotate No Prediction": _("Annotate No Prediction"),
    }
)
py_messages_titles = dict(
    {
        "danger": _("IMPORTANT :"),
        "warning": _("WARNING:"),
        "info": _("INFORMATION:"),
        "success": _("SUCCESS:"),
        "error": _("ERROR:"),
        "close": _("Close"),
        "cancel": _("Cancel"),
        "ok": _("Ok"),
    }
)

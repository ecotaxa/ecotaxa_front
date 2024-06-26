## 2024-06-10 : v2.7.5
    Feature: users list speed - use of api summary parameter
    Feature : users list : text status instead of int 
    Mod : users admin activate always return to profile page
    Mod: users update message 
	 
## 2024-05-17 : Hot fixes
    Fix: strip project title in projects list job_interface
    Fix: templates/v2/project/merge.html table search add cellidname to th
    Mod: templates/v2/project/purge.html  remove "DELETE ALL" btn when filters are "on"
    Fix: templates/v2/users/_user.html code error
    Add: new key in config.cfg APP_GUI_MESSAGE_COOKIE_NAME
    Fix: modules/table-component.js manage cellid variable name
    Fix: modules/table-component.js sorting function
## 2024-04-03: V 2.7.4.2
    Fix: import privileges users list
    Fix: bug tom select alert message
    Feature : add EcoTaxa version on footer
    Fix: bug in delta delay for maintenance messages
    Mod: form tabs toogle icon
    Feature: button to reset import list
## 2024-03-26: V 2.7.4.1
    Fix: final action for all jobs types
    Mod: help user profile
## 2024-03-26: V 2.7.4
    Fix removed "Fix categories issues"
    Feature Notification module
    Feature form fields error and warning messages with translations
    Feature & Fix Maintenance messages
    Fix removed add_ticket in users
    Improve Help project settings get licenses def from back
    Feature spinner icon on save form buttons
    Fix in filtered delete removed checkbox "delete project"
    Feature added delete objects and / or project confirmation
    Fix project privileges no duplicate user
    Feature project privileges sorted by privilege and name
    Fix job monitor stayed at 99%
    Feature link to "About project" in classification page
    Fix homepage message - active , no expiration
## 2024-02-09: V 2.7.3.2
    Fix && Feature import from projects : re-enable selected rows
    Feature js-submit prevent form enter submit (needed for modal)
    Fix webpack config contenthash
## 2024-02-06: V 2.7.3.1
    Fix list projects to import
    Fix help scroll
    Fix form fields error messages
    Fix Safari bug on details
## 2024-02-06: V 2.7.3
    Fix project setting title
    Mod Change Preset to Sorting tools in porject Settings
    Feature add email to name in members seach list
    Fix export filters
    Feature new export parameters
    Upgrade tailwindcss
    Feature dist unique id for js and css
## 2023-12-18: V 2.7.2.3
    Fix _google_captcha
    Fix recaptcha
    Fix jobs import url
    Modify job show -> better display
## 2023-12-15: V 2.7.2.2
    Fix main search for projects
## 2023-12-08: V 2.7.2.1
    Fix or try to script version
    Fix url relative in tables script
    Fix stats export csv
    Fix stats display
## 2023-12-08: V 2.7.2
    Fix Safari bug ( js in user mod profile )
    Fix Chrome bug (js my-files filepath)
    Fix current_user in security_on_backend
    Feature js-captcha
    Feature user register better response and error message
    Feature ticket for user validation in admin validation
    Feature new UI pages for projects list, project settings, about project, project tools, project export
    Modify classification page navigation - send to new UI if exists
    Feature google analytics tags version upgrade
    Fix: remove experimental "new"
    Feature : better top navigation
    Featrure : logo parameter
    Feature : homepage message and top maintenance and info message
## 2023-10-03: V 2.7.1
    Features : login , register , admin , user profile replaced by new version - user login and registration follow major modification in the API users
    Fix error reporting (merge new and current error handling)
    Fix error 500 in  missing files in new contextual help ( 404 )
    Fix removed everything related to Flask_security
## 2023-05-26: V 2.7.0
## 2023-05-25: V 2.7.0_beta
    Features : new front features - users - login - validation - removed js component simple-datatables
## 2023-04-04: V 2.6.9.1
    Fix table samples sort
    Fix menus
## 2023-03-31: V 2.6.9
    Feature: Registration
    Feature: Jobs
    Feature: Tools
## 2022-10-21: V 2.6.6
    Feature : optimize tables display , optimize speed
    Feature: about project page and details in tables
    Feature: stats display
## 2022-10-14: V 2.6.6
    Feature : new ui for pages projects list, project create, login, about, privacy - tools to import settings, taxonomy, privileges.
    Feature : Babel translations for the new ui.
## 2022-09-01: V 2.6.5
    Feature : routing to new ui for pages projects list, project create, login, about, privacy - tools to import settings.
    Features #824:  add functionalities  to projects list - done for selection page ( left to do merge & prediction , select for collection)
## 2022-05-30 : V 2.6.4
    Bug #820: Difference in country treatment between self-registration and admin form
    Bug #818: Importing a zip file of a few MB is impossible
    Bug #817: page 2 Train&Predict : deletion of input not possible
    Bug #815: Sample information on map not pulled form the correct project
    Feature #813: removed mail to marc.picheral@obs-vlfr.fr download line from the frontpage.
    Bug #794: Nice error message when same user is twice in the members list during rights on a project
    Bug #734: Overriding an existing user in privileges list keeps him/her
    Feature : client side validation  + add member  in Privileges list
    Bug #808: "Other filters" tab keeps memory of previous classification label
    Feature #589: ui Display the contact name (rather than manager name)  in the project list
## 2022-05-03 : V 2.6.3
    Feature #804: Make the front-end deliverable as a Docker image.
    Feature #798: Clean the configuration file(s) for proper source/config separation.
    Feature #799: Allow the back-end to serve image files.
    Feature #801: Make ML models owned by back-end, add an entry point in /api
    Bug #800: Project visibility was lost when modifying project rights _only_.
    Bug (back) #42: Check rights in /object_set/export.
    Bug (back) #40: Add Content-Length http header while getting a job file.
## 2022-03-16 : V 2.6.2
    Feature #751: Improve display of classification history in object details.
    Feature #473: Make score available for use as a filter.
    Feature #522: Rename EMODnet export to Darwin Core.
    Feature #264: Promote instrument as a project-level field.
    Feature #730: Remove funding notes.
    Feature #784: Restrict exposed mail for permission queries to _the_ app administrator.
    Feature #778: Add internal taxonomic ID to DOI export.
## 2022-02-23 : V 2.6.1
    Feature #738: Relax constraint on acquisition ID unicity per project.
    Feature #729: Maps are now fed from back-end only.
    Feature #724: latin-1 encoding option for reports is now gone
    Arch feature #765: Make python front-end use only the back-end as data source.
    Feature #675: Put limits on the number of files/objects which can be imported.
## 2022-01-13 : V 2.6.0
    Feature #747: Remove EcoPart related code from EcoTaxa.
## 2021-10-26 : V 2.5.15
    Feature #745: Move deep features generation to back-end.
## 2021-10-26 : V 2.5.14
    Feature #740: Add a keyboard shortcut for setting selection to Dubious.
    Feature #731: Clear-up difference between project description and comments.
    Feature #605: Move (partly) prediction AKA auto classification execution into back-end.
    Feature #593: Simplify taxonomy filters possibilities/syntax.
    Feature #462: Remove the option to subset without images.
    Feature #354: Split Home/Explore menu item into separate items.
    Bug #148: Setting "Use Deep Learning features" is not remembered between predictions (fixed as side-effect of #605)
## 2021-09-28 : V 2.5.13
    Feature #530: After an import, remind the import source.
    Feature #665: Improve a bit the wording in prediction pages.
    Bug #518: Projects choices is lost in prediction page 1 if filtering is used.
    Feature #142: Prediction target choice is confusing, if on a filtered set then it's just redundant.
    Feature #65: More wording in prediction pages (step 3).
    Feature #517: In prediction step 2, remind the data source(s) chosen at step 1.
    Feature #572: Remove "Predict identifications from trained model" which is very limited and never used.
    Bug #728: Various, small and annoying issues in the most used control of the whole application (category marking select)
    Feature #690: Add a 150% zoom option.
    Feature #554: It's now possible to add sample and acquisition names in the fields displayed during classification.
## 2021-09-21 : V 2.5.12
    Feature: General performance improvement on back-end and python front-end
    Bug #490: Private projects could appear in classification models.
    Bug #716: Subset failed when too many samples in selection.
    Feature #707: Remove "merge 2 categories" admin function.
    Feature #717: Allow some users to experiment new Vue frontend.
    Feature #256: Switch all encoding to UTF-8.
    Bug #712: It should not be possible to validate an object without category.
    API Bug #694: Missing value in /projects/search response.
    Feature/bug #715: Improvement of taxon creation dialog.
## 2021-09-15 : V 2.5.11
    Bug #653: Too many projects are visible in /prjothers/
    Feature #606: Move cron AKA nightly clean-up operations to back-end.
    Bug #648: nbrobj and nbrobjcum columns of taxonomy table now have a more intuitive content.
    Bug #697: Jobs remain in 'pending' state if database is restarted
    Feature #609: Move taxonomy management to back-end
    Feature #573: Reduce taxon operations on EcoTaxa (a bit is missing)
    Bug #637: Taxonomy filter creation label does not accurately reflect current user rights.
    Feature #462: Any user managing any project can create a taxon.
    Feature #645: Browse taxonomy page allows to get information about taxa including their usage.
    Feature #509: Deal with deprecated taxa. Implemented in a dedicated page.
    (part of) Feature #709: Change (many) objects to WoRMS-compatible taxonomy.
    Bug #714: Annotation reversal did not work for Predicted only objects.
## 2021-06-16 : V 2.5.10
    Bug #686: Ensure that project link is present for new export jobs.
    Feature #605: (start): Automatic classification result can now be stored by calling an API endpoint.
    Bug #687: When an import job goes wild, it can generate an un-displayable number of errors.
    Bug #688: Seldom but confusing python error when a job starts.
## 2021-06-10 : V 2.5.9
    Feature #600: Move export function(s) to back-end
    Feature #603: Add image references to exported data, even if without images themselves
    Feature #678: Remove XML export which is in a specific unused format
    Bug #679: Duplicates pathes inside exported zip files
    Bug #676: Hard-coded relative pathes in export code
    Feature #539: Include export log files in produced zip. Should be useful for non-fatal problems.
    Feature #682: Avoid historical trouble with leading 0s in times by enabling a formatted time
    Bug #683: Images without file name (in historically imported UVP6 projects)
## 2021-05-26 : V 2.5.8
    Feature #360: Allow to subset by sampling various entities, not only categories.
    Bug #595: Project managers should be able to clone their own projects, even if they are not Project Creator.
    Bug #543: A corrupted PNG could make an import operation fail with a cryptic error.
    Feature #590: Move file navigation to back-end.
    Features #673: #672: Add/adapt API entry points for new front-end. See #382:
    Bug #614: Api could not be used interactively from /api/docs generated page.
    Bug #657: A TIFF file could crash the import.
## 2021-05-05 : V 2.5.7
    Feature #660: Add a column to Collection and expose a search API entry point using it.
    Bug #659: In a mirrored DB setup, project creation is sometime not visible immediately.
    Bug #656: Subset (and other GET-based launched tasks) fails when behind a uWSGI server (NOT A CODE FIX).
    Bug #652: Some actions in object details window make the selection behind silently empty.
    Feature #608: In parallel with tasks, create back-end job entities and mix the two kinds for users.
## 2021-04-22 : V 2.5.6
    Feature #607: Ensure that any information visible in the main classification page can be queried via the API.
    Features #624: #631: #625: Export in Darwin Core Archive format a collection. API only.
    Bug #640: Taxo tree could be logically inconsistent.
    Bug #583: Re-import of the same file ended up with multiple identical images for each object.
## 2021-02-11 : V 2.5.5
    Feature #603: Export abundances / concentrations of 0 in DwCA export
    Bug #583: (starting): Set-up database storage of information about images on disk. Add an API
        entry point to store MD5 of present files.
    Feature #579: Amend database to store users email validity information.
    Bug #602: (Api): PUT projects/{project_id} i.e. project update fails silently on some errors
    Feature #612: Relocate admin app in a dedicated sub-app.
    Bug #587: "Visible for all visitors" checkbox cannot be changed in project settings".
## 2021-02-03 : V 2.5.4
    Bug #548: (starting): Move object orig_id from obj_field DB table to obj_head.
    Bug #523: Cosmetic fix (order of categories in project settings page).
    Feature #436:(continues): Use more entry points from backend, around Samples and Taxonomy.
    Feature #411: Remove DB export and import. App. export is better even if slower.
## 2021-01-28 : V 2.5.3
    Feature #430: Move selection using CTRL-key + arrows in manual classification page
    Bug #371: Manual classification layout is broken (scrolls) with too long taxa names.
    Regression #574: Instrument list does not show in Other Filters when clicking ?
    Regression #576: When last page in manual classification does not match filtering criterion, it appears
        empty after a save. Used to jump automatically back to previous one.
    Feature #399: CTRL-SHIFT+left/right arrow to move b/w pages in manual classification page.
    Data consistency bug #544: It was possible to have several paths to reach an object.
## 2021-01-21 : V 2.5.2
    Feature #557: Rename some API endpoints for naming consistency
    Feature #511: Add a legal license per project.
    Feature #564: Add a second "Save" button in Project Settings page
    Feature #565: Add a Contact Person per project
    Feature #4: Add a "Recent projects" list (with last accesses projects)
    Bug #541: Ensure that the objects hierarchy is consistent
    Bug #567: Under some conditions, FastAPI framework leaks request resource (DB session)
## 2021-01-14 : V 2.5.1
    Feature #529: Show a progress bar while loading in the manual classification window.
    Bug #549: Cryptic error when import update fails due to rights problem.
    Bug #556: Fields are not updated in object_set/update when mixing plain and free columns.
    Bug #538: Space in sample names made them unselectable in "Pick from other projects" child window.
    Regression due to #523: fix: Preset were erased from project after editing rights only.
## 2020-12-08 : V 2.5.0
    Bug #542: During export with images, arrange that resultsets from DB are flushed to disk instead of remaining opened.
    Bug #537: There is now a decent progress bar during export.
    Bug #540: It's not possible anymore to have a NULL orig_id in Samples and Acquisitions.
    Bug #546: (partial fix): orig_id is now unique for Samples and Acquisitions. Process is not relevant anymore. Object remains.
    Feature #144: Check the hierarchy in data identifiers at import time.
    Feature #367: Merge acquisition and process into a single entity.
## 2020-11-25 : V 2.4.7
    Feature #389: Force presence of sample/acquisition/process for each object.
    Features #43: #523: More functions go thru API from flask app.
## 2020-11-10 : V 2.4.6
    Bug #503: Inconsistency in database schema on samples, acquisitions and process tables.
    Bug #523: #524: Project settings page layout is damaged and predefined taxonomy not saved.
    Bug #501: It was possible to delete objects outside current project.
    Bug #499: Last imported path was not recorded for 'import update'.
    Bug #68: Inconsistency in 'Import Database' UI.
    Bug #345: Users were told late that nothing has to be done during automatic classification.
## 2020-10-29 : V 2.4.5
    Bug #516: No title for project in anonymous view mode.
    Feature #426: Minimal UI to export a project in DwC format. Menu is hidden.
    Feature #244: Add a license field for projects.
    Feature #435: Project edit now on back-end (excluding CNN list).
## 2020-10-14 : V 2.4.4
    Bug #500: Base view for queries should be simpler and faster.
    Feature #497: Sort tasks by more recents first.
    Feature #435: Object details is now implemented on back-end.
    Bug #414: Useless commit appears as a warning in PG logs.
    Feature #321: Proper message when a user who cannot create a taxon needs one.
    Bug #342: Taxon select box has no MRU or create link in object details window.
    Bug #422: Update sun position when related metadata changes.
    Bug #341: Filter "NaN" and "NA" even in text columns.
    Feature #435: Move classification/validation to back-end.
    Bug #464: Last used taxa should not be random.
## 2020-09-30 : V 2.4.3
    Bug: Ecopart #451: Too long project title makes layout of EcoPart prjedit page ugly.
    Bug: Ecopart #437: Stack trace when displaying TIME.
    Bug: Ecopart #433: Single-line TIME_LPM files cannot be imported.
    Feature: Ecopart #288: Add date+time in map popup.
    Feature: Ecopart #438: View pressure in TIME mode.
    Feature: Ecopart #432: Improve UVP6 remote import (http* support).
    Documentation: Ecopart #442: Indicate polling frequency for UVP remote files.
    Documentation: Ecopart #378: Indicate data origin in import task.
    Feature #452: No more confusion matrix page.
    Feature #435: Edit / Erase annotation massively is now implemented on back-end.
    Feature #383: Mouse move + click in manual classification page sometimes fails to select.
    Feature: Ecopart #202: Choice between Zoo and LPM formats during export.
    Documentation: Ecopart #356: Indicate units in export page.
    Bug #475: Some user fields could start/end with blanks.
    Bug #477: Category assignment using ENTER did not work with same category.
    Bug #463: Re-fix. Behavior was different when typing into the input and outside, e.g. in vignettes pane.
    Bug #459: _One_ of the tens of missing user input controls is now implemented.
    Bug #458: SCN Network presence is checked before using it during prediction.
    Bug #344: Export summary crashed when current filter was on an object feature.
    Bug #368: Saving with opened autocompletion left an unused window in the page upper left corner.
    Bug #483: Cryptic error during import with too large image files.
    Bug #484: Right checking was wrong for READ action.
    Bug #466: Make optional a previously mandatory column during import update.
## 2020-09-16 : V 2.4.2
    Feature #245: More API primitives implemented on back-end, namely mass update and reset to predicted.
    Bugfix #465: Right-click menu in category is cropped and moves with right pane.
    Feature #445: Remember, per project, the directory used during last import operation.
    Bugfix #463: Recent categories were not filtered as they should have.
## 2020-09-02 : V 2.4.1
    Feature #245: More API primitives implemented on back-end.
    Bugfix #350: Object mappings are now re-ordered during merge.
    Bugfix #352: Merge is now impossible when it would mean data loss.
    Bugfix #408: Subset operation now uses same bulk operations as import.
    Removal of some dead code.
## 2020-07-02 : V 2.3.4
    Bugfix #419: Add preset/add extra unusable due to HTML escape.
    Feature #282: Subset extraction page improvement.
    Feature: Ecopart #423: Allow a special value for last image.
## 2020-06-10 : V 2.3.3
    Bugfix #391: #418: #420: Rewrite of manual classification entry point for safer multi-session access.
    Feature #400: Move simple import to back-end.
## 2020-05-27 : V 2.3.2
    Bugfix #357: Outdated logos.
    Feature #401: Add a mailto: link to owner for each task in task list.
    Feature #222: Add a link to project for each task in task list.
    Bugfix #413: Daily Task (cron) fails.
    Feature #406: EcoPart: Share current filters by mail.
    Feature #400: Move import update to back-end.
    Bugfix #403: EcoPart: Last graph in series is damaged.
## 2020-05-18 : V 2.3.1
    Bugfix #402: Under server load or for big page sizes, vignettes could appear after a delay.
## 2020-05-13 : V 2.3
    Architecture #400: Move some code to back-end, potentially in a container.
    Bugfix #349: Time format wrongly hinted in Mass Update page.
    Bugfix #320: "Dust" instead of "Dusk" in parts of day display.
    Bugfix #322: Document limit of custom fields for each table in import page.
    Bugfix #395: Ensure preferences do not overflow the DB column.
    Feature #379: EcoPart: Allow negative values in particle import.
    Feature #380: EcoPart: Remove descent filter for UVP6 datasets.
    Bugfix #300: EcoPart: User cannot export restricted project when not annotator.
    Bugfix #363: In details page, tasks are always flagged as "with error" while running.
    Bugfix #361: "Ecotaxa Administration" is a dead link in admin home.
    Bugfix #328: No country in a freshly created DB.
## 2020-05-05 : V 2.2.7
    Bugfix #334: L'utilisateur reçoit un indice en cas de nom de fichier problématique lors de l'import.
    Bugfix #281: Correction des rechargements aléatoires pendant la classification manuelle.
    Début de nettoyage du code #381:
## 2020-04-27 : V 2.2.6
    Bugfix #364: #366: Import de fichiers encodés latin_1 sous Linux.
    Bugfix #351: Exception python lors de l'import si la 2eme ligne du TSV n'est pas conforme.
## 2020-04-23 : V 2.2.5
    Amélioration du texte d'information sur le serveur FTP lors des exports.
## 2020-04-20 : V 2.2.4
    Bugfix/Regression #340: les imports d'objets sont en notation degrée decimaux et non pas degree.minutes
    Réduction du nombre de décimales lors des conversions des latitudes et longitudes exprimées en minutes
    Suppression de warning de dépraciation sur WTForm validators.required
## 2020-02-07 : V 2.2.3
    Ajout de normpath sur certaines resolution de chemin suite à problème avec des lien sympboliques
## 2020-01-29 : V 2.2.2
    Part : Modification comportement default_depthoffset now override
    Part import : uvp6 sample use Pressure_offset
    Part export : Divers bugfix
    Part view : Ajustement groupe de classes
## 2020-01-14 : V 2.2.1
    Generation vignette : Largeur minimale pour voir au moins l'echelle
    Gestion UVP6 Remote : Format LOV TSV
    Fix python 3.7
    Améliorations performances import
    Part : Gestion graphique temporel temps absolu
    Part : Gestion graphique 1 couleur par sample + legende si un seul projet
    Part export : gestion aggregation des TSV sur détaillé et réduit + nom projet dans les summary
    Part import : ajustement format LOV TSV
    Part import : ignore les samples sans depth si profil vertical sinon si depth invalide mise à 0

## 2019-08-18 : V 2.2.0
    Intégration of UVPApp Data Format
## 2019-04-18 : V 2.1.0
    Fix #304,#316,#317
## 2019-04-03 : V 2.1.0
    Fix #111,#277,#304,#305,#306,#307,#311,#312,#314
## 2019.02.01 : V 2.0.1
    Fix implementation minor bug
## 2019.01.25 : V 2.0.0
    Integration with EcotaxoServer
    Handling new display_name child<parent #87,#172
    Python Packages upgrade (flask, numpy, scikit, .... ), Bootstrap Upgrade
    fix/improve #216,#274,#284,#280
## 2018.11.22 : V 1.6.1
    Minor fix
## 2018.11.14 : V 1.6
    RandomForestClassifier modified from balanced to auto
    Export redesigned
    Import #224,#243,#248: Robustified issues with Sun Position computation, lat/lon of sample always recomputed
    ReImport : Added sun position computation, lat/lon of sample always recomputed
    Subset #255 : Added duplication of CNN features
    Admin Project : Enhanced user management
    Manual classif #169,#164 : Refresh counter at each save, use separated badges
    Manual classif #163,#162,#260 : autoremove autoadded by sort displayed fields, Validation,ObjDate,Lat,Long date available on list and added on popup
    Manual classif #161,#159,#158 : autorefresh on top filter value change, added Ctrl+L for Validate selection, Keep vertical position on save
    Manual classif #211,#210,#209,#207,#205,#183 : Help for TaxoFilter,Improved validator filter, Added filter on validation date, added save dubious
    Manual classif #212,#217: duplicated saving status, Annotator can import
    Maps : #208 added informations on the sample
    EcoPart Fix : computation of Plankton abondance include only Validated Now (then Reduced & Détailled export too)
    EcoPart Fix #201 : Export of raw now handle not-living exclusion
    EcoPart Fix #196: computation of Plankton abondance use the Deepth offset now, also substracted
    EcoPart Fix #184 : When ecotaxa project are merged, associated PartProject are now associated to the target project
    Also #214,#220,#186,#179,#178,#176,#175,#152,#107
    User Management : Handle Self creation and Country
    Privacy : Added privacy page and Google Analytics Opt-out
## 2018.08.16 : V 1.5.2
              Added hability to work on database without trust connection configured on pg_hba
              Added CSRF Token on AdminForms most sensibles screens
              Added CSRF protection on console screen
              Added CSP policies to reduce impact of XSS attack
              Fixed several SQL Inject vulnerabilities
              Fixed no more errors if folder SCN_networks is missing
              Removed dead code
## 2018.03.14 : V 1.5.1b
              Moved Daily task in external launch using cron.py
              fixed computation on particle
              modified handling of ftp export copy due to issue on LOV FTP is on NFS volume
## 2018.01.16 : V 1.5.1
              Bugfix on privilèges on part module causing performance issues
## 2017.12.23 : V 1.5
              Minor adjustements
## 2017.11.08 : V 1.4
              Deep machine learning Integration
              Optimization of classification update query
              Added a table for Statistics by taxo/project to optimize displays on classification
              Bugfix on Particle module
## 2017.11.03 : V 1.3.2
              On manual classification splitted menu on 2 menu : Project wide and filtered
              Implementing Automatic classification V2
              - Filtered prediction
              - Can save/and predict from model
              - New Screen for PostPredictionMapping
              - Multiple project for Learning Set
              - Handling Nan,+/- Inf as empty value
## 2017.09.16 : V 1.3.1
              Evolution of Confusion matrix for sklearn,numpy,matplotlib upgrade
              Evolution of RandomForest parameters
## 2017.07.05 : V 1.3.0
              Introduction of Particle module
## 2017.03.28 : V 1.2.3
              Bugfix in display annotator on image Popup
              Bugfix is Manage.py where using global db routine.
## 2017.03.22 : V 1.2.2
              Added composite taxon Taxon(parent) in metadata update screen
## 2017.03.12 : V 1.2.1
              Improved database transaction management to avoid long transaction
## 2017.01.30 : V 1.2
              Explore : Improved no result, improved taxo filter
              Explore : Public user can go on manual classification of any visible project
              Explore : Map on home of explore
              Map : Filter by project and Taxo
              Details page : MailTo to notify classif error, display on map,
              Details page : edit data by manager
              Import : Wizard to premapping, added taxo (parent) format allowed at import
              Import : Image import only with form to fill metadata
              Export BD at project level.
              Prediction : Limit count for statistics, predict only filtered taxon on target set
              Conf Matrix : Export TSV
              Topper : Progress bar, improved button clic, improved clear filter
              Contribute : Display selection count, change line selection behavior
              Contribute : Show taxo children
              Task : New menu for app admin + can see all task of all users


## 2016.12.07 : V 1.1 Several changes on annotation page, filters
              Select project : filter on name, instrument, subset
              Select project : display email
              Manual Classif : Several minor changes
              Manual Classif : Propose last 5 classification
              New Filters : Instrument, Annotator, Free Field, Month, Day period
              Import : New feature to update matadata from file
              Import : Bugfix on uppercase column name
              Project : New status to block prediction
              Filter on feature : Purge, subset, Export
              TSV Export : split in multiple file, predefined check, separate internalID, add 2nd line for reimport
              AutoClean empty sample
              Zoom : 200%
              Admin : All manager can create a project
              Home Page : Custom message by App manager
              Prediction : added PostClassifMapping
## 2016.06.10 : Removed X before Object name
             if file home.html or homebottom.html is missing use home-model.html and homebottom-model.html
             Theses file are read as UTF-8 Format instead of target platform settings.
             Integration of licenses files as md format before integration to GitHub
## 2016.03.15 : Added CreateDirConcurrentlyIfNeeded to avoid conflinct in creation of images directory by concurrent task
## 2016.01.17 : Added parameter PYTHONEXECUTABLE in Config.cfg
             Added objects view creation in Manage CreateDB
             Added a Matplotlib uses to execute correctly on GraphicLess server.
             Added Cascade delete on DB Definition to create them during CreateDB (obj_field & Histo)
             During ImportDb compare Taxon Name and Parent Taxon Name to detect correctly Name duplicate
## 2015.12.14 : Bugfix in import task, use only ecotaxa prefixed files
## 2015.12.11 : Improved CSV export to include Direct Taxonomy parent name and Taxonomy hierarchy
             Included license.txt File

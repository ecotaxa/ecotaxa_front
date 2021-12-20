# INSTALL ECOTAXA TRANSLATIONS MECHANISM ON A PC Ubuntu
### Please fix this doc when you use it and find improvements
### See the sites :
### https://docs.readthedocs.io/en/stable/development/i18n.html
### https://docs.python.org/fr/3.6/library/gettext.html
### https://www.mattlayman.com/blog/2015/i18n/
### https://lokalise.com/blog/beginners-guide-to-python-i18n/
### https://phrase.com/blog/posts/detecting-a-users-locale/
## 0) Detect and mark the strings that you want to "internationalize"
### A solution to detect all the strings in a python project is :
### a) Use *pyinstaller* to build a unique executable from you python project.
### b) Then run the *strings* command on this executable to get all the strings : only a subset of them will be "internationalized".
## 1) If not done, install the virtualenv tool :
```
pip3 install virtualenv
```
## 2) Create and use a temporary working directory
```
mkdir /tmp/proj
cd /tmp/proj
```
## 3) Create a python virtual environment, and activate it
```
virtualenv venv
. venv/bin/activate
```
### From now, you should see the "(venv)" prompt on the left of the command line
## 4) Install Babel in the virtual environment
```
pip3 install Babel
```
## 5) Verify the Babel version
```
pybabel --version
```
### Important : the version should be 2.9.1 or higher
## 6) Create a locale folder, that will be used by the Babel tool
```
mkdir locale
```

## 7) Extract the "international" strings from your python working folder. Those are strings used inside the .py files like
```
...gettext("ONE_TRANSLATION_ID")
```
or
```
..._("OTHER_TRANSLATION_ID")
```
### N.B. _() is an alias for gettext(), and Babel understands both
### N.B. Do NOT use accents of special latin characters in the translation IDs
### The extraction command is (~/ecotaxa/ecotaxa_dev is our python folder):
```
pybabel extract ~/ecotaxa/ecotaxa_dev -o locale/base.pot
```
### a base.pot is created (pot means portable object template), that looks like :
```
# Translations template for PROJECT.
# Copyright (C) 2021 ORGANIZATION
# This file is distributed under the same license as the PROJECT project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2021.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PROJECT VERSION\n"
"Report-Msgid-Bugs-To: EMAIL@ADDRESS\n"
"POT-Creation-Date: 2021-12-15 10:33+0100\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel 2.9.1\n"

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:59
msgid "EcoTaxa_is_a_web_application"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:60
msgid "If_you_use_EcoTaxa"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:61
msgid "The_development_of_EcoTaxa"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:62
msgid "Sorbonne_Universite_and_CNRS"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:63
msgid "The_Programme_Investissements_d_Avenir"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:64
msgid "The_Partner_University_Fund"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:65
msgid "The_CNRS_LEFE_program"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:66
msgid "The_Belmont_Forum"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:67
msgid "The_Watertools_company"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:68
msgid "The_maintenance_of_the_software"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:69
msgid "The_persons_who_made_EcoTaxa"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:70
msgid "Marc_Picheral_and"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:71
msgid "Sebastien_Colin"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:72
msgid "Developers"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:73
msgid "Deep_learning"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:74
msgid "testing_and_feedback"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:75
msgid "Disclaimer"
msgstr ""
```
### Important : if an error like
```
File "/tmp/proj/venv/lib/python3.6/site-packages/babel/util.py", line 112, in parse_future_flags
    body = fp.read().decode(encoding)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe0 in position 1990: invalid continuation byte
```
### is encountered, go to the line calling "decode(encoding)"
### and add the following instruction just above (line 111 of util.py in our example):
```
encoding='latin-1'
```
### TODO : better understand this work around.
## 8) Create a .po file (portable object) from the .pot file, and for a given language ('fr' in the following line)
```
pybabel init -i locale/base.pot -l fr -d messages -D ecotaxa
```
### This will create a catalog for the french language :
### messages/fr/LC_MESSAGES/ecotaxa.po
### N.B. Our ecotaxa translation structure is :
### ecotaxa/ecotaxa_dev/messages/fr/LC_MESSAGES/ecotaxa.po
### and the generated ecotaxa.po will look like :
```
# French translations for PROJECT.
# Copyright (C) 2021 ORGANIZATION
# This file is distributed under the same license as the PROJECT project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2021.
#
msgid ""
msgstr ""
"Project-Id-Version: PROJECT VERSION\n"
"Report-Msgid-Bugs-To: EMAIL@ADDRESS\n"
"POT-Creation-Date: 2021-12-15 10:33+0100\n"
"PO-Revision-Date: 2021-12-15 10:55+0100\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language: fr\n"
"Language-Team: fr <LL@li.org>\n"
"Plural-Forms: nplurals=2; plural=(n > 1)\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel 2.9.1\n"

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:59
msgid "EcoTaxa_is_a_web_application"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:60
msgid "If_you_use_EcoTaxa"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:61
msgid "The_development_of_EcoTaxa"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:62
msgid "Sorbonne_Universite_and_CNRS"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:63
msgid "The_Programme_Investissements_d_Avenir"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:64
msgid "The_Partner_University_Fund"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:65
msgid "The_CNRS_LEFE_program"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:66
msgid "The_Belmont_Forum"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:67
msgid "The_Watertools_company"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:68
msgid "The_maintenance_of_the_software"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:69
msgid "The_persons_who_made_EcoTaxa"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:70
msgid "Marc_Picheral_and"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:71
msgid "Sebastien_Colin"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:72
msgid "Developers"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:73
msgid "Deep_learning"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:74
msgid "testing_and_feedback"
msgstr ""

#: /home/laurentr/ecotaxa/ecotaxa_dev/appli/main.py:75
msgid "Disclaimer"
msgstr ""
```
### if other new translated texts arrive in the python code, repeat step 7, and instead of an "init" command at step 8, just update by :
```
pybabel update -i locale/base.pot -l fr -d messages -D ecotaxa
```
### This will update the corresponding .po file with other new translations, without damaging the old translations
## 9) Fill in this .po file with all the necessary msgstr translated strings
## 10) Build the corresponding .mo (machine object) file that will be used when running the python executable, by :
```
msgfmt -c -o ecotaxa.mo ecotaxa.po
```
### If you forget this step, the executable will not use the appropriate translations
### N.B. To install the msgfmt tool :
```
apt-get install gettext
```


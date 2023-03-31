#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n
# keep appli/i18n as  translations path or modify as well in constants.py
# extract messages
1- pybabel extract -F config/babel.cfg -k _l -o messages/gui/messages.pot appli
#generate translation catalog
2- pybabel init -i ./messages/gui/messages.pot -d ./appli/i18n -l fr


# to update NullTranslations
1 - extract again
# update catalog
2 - pybabel update -i ./messages/gui/messages.pot -d ./appli/i18n

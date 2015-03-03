#! /bin/sh

I18NDOMAIN="vs.knowledge"

# Synchronise the templates and scripts with the .pot.
# All on one line normally:
i18ndude rebuild-pot --pot locales/${I18NDOMAIN}.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with all .po files
for po in locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
    i18ndude sync --pot locales/${I18NDOMAIN}.pot $po
done

# Same for the plone domain.  We must not search in python files
# though, as that will just look for _('...') calls, regardless of the
# domain.  Usually .pt or .cpt files are not interesing either, as
# they will have been copied from standard Plone, so translations are
# already done in plone.app.locales.  Really, only the profiles
# directory is interesting.
#I18NDOMAIN="plone"
#i18ndude rebuild-pot --pot locales/${I18NDOMAIN}.pot --create ${I18NDOMAIN} profiles
#i18ndude rebuild-pot --pot locales/${I18NDOMAIN}.pot --merge locales/plone.manual.pot --create ${I18NDOMAIN} profiles
# Synchronise the resulting .pot with all .po files
#for po in locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
#    i18ndude sync --pot locales/${I18NDOMAIN}.pot $po
#done

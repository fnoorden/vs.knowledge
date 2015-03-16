# -*- coding: utf-8 -*-

from Acquisition import aq_parent

from zope.interface import implements

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class GroupsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(uself, context):
        kp = aq_parent(context)
        return SimpleVocabulary([
            SimpleTerm(value=eg, token=eg, title=' / '.join(eg.split('|'))) 
            for eg in kp.expertises_groups])

GroupsVocabularyFactory = GroupsVocabulary()

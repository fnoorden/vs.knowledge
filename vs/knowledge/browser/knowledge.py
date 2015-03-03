from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.interface import implements

from vs.knowledge.interfaces import IKnowledgeView


class KnowledgeView(BrowserView):
    implements(IKnowledgeView)

    # Utility methods

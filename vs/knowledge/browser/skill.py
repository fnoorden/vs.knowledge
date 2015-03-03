from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.interface import implements

from ..interfaces import ISkillView


class SkillView(BrowserView):
    implements(ISkillView)

    # Utility methods

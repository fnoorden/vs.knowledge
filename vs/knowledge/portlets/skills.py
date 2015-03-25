from plone.portlets.interfaces import IPortletDataProvider
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from zope import schema

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base

from vs.knowledge.utils import Knowledge

from Products.PythonScripts.standard import url_unquote_plus


class ISkillsPortlet(IPortletDataProvider):
    """ A portlet displaying a member selected skills with appropriate levels
    """


class Assignment(base.Assignment):
    implements(ISkillsPortlet)

    @property
    def title(self):
        return _(u"Skills")


class Renderer(base.Renderer, Knowledge):

    render = ViewPageTemplateFile('skills.pt')

    @property
    def author(self):
        request = self.request
        author = (
            len(request.traverse_subpath) > 0 and
            url_unquote_plus(request.traverse_subpath[0])
            ) or request.get('author', None)
        return author

    @property
    def author_skills(self):
        return self.grouped_skills(only_show=True)

    @property
    def available(self):
        _available = False
        if self.author:
            _available = True
        else:
            template_id = getattr(
                self.request.get('PUBLISHED', None), 'getId', None)
            if template_id:
                if template_id() == 'author':
                    _available = True
        if _available and self.author_skills:
            return _available
        return False

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()

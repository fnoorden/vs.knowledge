from plone import api

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import implements

from vs.knowledge.interfaces import ISkillView
from vs.knowledge.utils import Skill

import time


class ChangeSkill(BrowserView, Skill):
    """ Change skill values
    """

    def __call__(self):
        request = self.request
        form = request.form
        self.current()
        position, (member, self.level, self.show) = self.current_entry()

        if form:
            self.change_skill(position, member, self.level, self.show, form)
            from_url = form.get('from_url', '')
            return request.response.redirect(from_url)


class SkillView(BrowserView, Skill):
    """ Walkthrough view
    """
    implements(ISkillView)

    def __call__(self):
        self.current()
        self.directions()

        request = self.request
        form = request.form
        position, (member, self.level, self.show) = self.current_entry()

        if form:
            self.change_skill(position, member, self.level, self.show, form)

            response = request.response
            change = form.get('change', None)
            if change == 'Update' and self.up:
                return response.redirect(self.up)
            if change == '<<' and self.back:
                return response.redirect(self.back)
            if change == '>>' and self.forward:
                return response.redirect(self.forward)

        return self.template()

    def directions(self):
        """
        """
        skills = self.skills
        self.amount = len(skills)

        if not skills or self.amount < 2:
            return (None, None)

        self.index = skills.index(self.context)
        self.back, self.forward = '', ''
        if self.index > 0:
            self.back = skills[self.index - 1].absolute_url()
        if self.index < (self.amount - 1):
            self.forward = skills[self.index + 1].absolute_url()

        self.up = '/'.join([
            self.knowledge_profile.absolute_url(), 'knowledge-profile'])

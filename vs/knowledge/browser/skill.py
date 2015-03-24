from plone import api

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import implements

from vs.knowledge.interfaces import ISkillView
from vs.knowledge.browser.knowledge import Knowledge

import time

class Skill(Knowledge):
    """ Skill base
    """

    def change_skill(self, position, member, level, show, form):
        """
        """

        mls = self.context.member_level_show

        new_level = form.get('level', '')
        new_show = form.get('show', '')
        new = u'|'.join([member, new_level, new_show])

        if position < 0:
            mls.append(new)
        else:
            mls[position] = new

        setattr(self.context, 'member_level_show', mls)


class ChangeSkill(Skill):
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
            # if from_url and self.level in ['X', 'x', False]:


class SkillView(Skill):
    implements(ISkillView)

    template = ViewPageTemplateFile('templates/skill.pt')

    def __call__(self):
        self.current()
        self.directions()

        request = self.request
        form = request.form
        position, (member, self.level, self.show) = self.current_entry()

        if form:
            update = form.get('update', None)
            self.change_skill(position, member, self.level, self.show, form)

            response = request.response
            if update == 'Update' and self.up:
                return response.redirect(self.up)
            if update == '<<' and self.back:
                return response.redirect(self.back)
            if update == '>>' and self.forward:
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

from plone import api

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import implements

from vs.knowledge.interfaces import ISkillView
from vs.knowledge.browser.knowledge import Knowledge


class SkillView(Knowledge):
    implements(ISkillView)

    template = ViewPageTemplateFile('templates/skill.pt')

    def __call__(self):
        self.current()
        self.directions()
        form = self.request.form
        position, (member, self.level, self.show) = self.current_entry()

        if form:
            update = form.get('update', None)
            self.update(position, member, self.level, self.show, form)

            if update == 'Update' and self.up:
                return self.request.response.redirect(self.up)
            if update == '<<' and self.back:
                return self.request.response.redirect(self.back)
            if update == '>>' and self.forward:
                return self.request.response.redirect(self.forward)

        return self.template()

    def update(self, position, member, level, show, form):
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

    def directions(self):
        """
        """
        skills = self.skills()
        self.amount = len(skills)

        if not skills or self.amount < 2:
            return (None, None)

        self.index = skills.index(self.context)
        self.back, self.forward = '', ''
        if self.index > 0:
            self.back = skills[self.index - 1].absolute_url()
        if self.index < (self.amount - 1):
            self.forward = skills[self.index + 1].absolute_url()

        self.up = self.knowledge_profile().absolute_url()

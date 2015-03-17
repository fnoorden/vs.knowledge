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
        form = self.request.form
        position, (member, self.level, self.show) = self.current_entry()

        if form:
            update = form.get('update', None)
            self.update(position, member, level, show, form)

            directions = self.directions()
            if update == 'Update' and directions['up']:
                return self.request.response.redirect(directions['up'])
            if update == '<<' and directions['back']:
                return self.request.response.redirect(directions['back'])
            if update == '>>' and directions['forward']:
                return self.request.response.redirect(directions['forward'])

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
        amount = len(skills)

        if not skills or amount < 2:
            return (None, None)

        index = skills.index(self.context)
        back = skills[index-1].absolute_url() if index > 0 else ''
        forward = skills[index+1].absolute_url() if index < (amount-1) else ''
        up = self.knowledge_profile().absolute_url()
        return {'up': up, 'back': back, 'forward': forward}

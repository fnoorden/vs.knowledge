from plone import api

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.interface import implements

from vs.knowledge.interfaces import ISkillView
from vs.knowledge.browser.knowledge import Knowledge


class SkillView(Knowledge):
    implements(ISkillView)

    def update(self, position, member, level, show, values):
        """
        """

        mls = self.context.member_level_show

        new_level = values.get('level', '')
        new_show = values.get('show', '')
        new = u'|'.join([member, new_level, new_show])

        if position < 0:
            mls.append(new)
        else:
            mls[position] = new

    def values(self):
        values = self.request.form
        position, (member, level, show) = self.current_entry()

        update = values.get('update', None)
        if update:
            self.update(position, member, level, show, values)

            directions = self.directions()
            if update == 'Update' and directions['up']:
                return self.request.response.redirect(directions['up'])
            if update == '<<' and directions['back']:
                return self.request.response.redirect(directions['back'])
            if update == '>>' and directions['forward']:
                return self.request.response.redirect(directions['forward'])

            import sys;sys.stdout=file('/dev/stdout','w')
            import pdb; pdb.set_trace()

        return {'level': level, 'show': show}

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


    def next(self):
        """
        """

    def update_next(self):
        """
        """

    def previous(self):
        """
        """

    def update_previous(self):
        """
        """

    def status(self):
        """
        """
        position, (member, level, show) = self.current_entry()

        if position == -1:
            return None
        if level == 'X':
            return 'x-value'
        if level == '':
            return 'no-value'
        return 'level-%s' % level

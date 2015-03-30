from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from vs.knowledge import VSKnowledgeMessageFactory as _
from vs.knowledge.interfaces import ISkillView, IChangeSkill
from vs.knowledge.utils import Skill
from zope.interface import implements
import time

LEVEL = '                <option value="%s"%s>%s</option>'
SELECTED = ' selected="selected"'
LEVELS = """            <select
                name="level">
%s
            </select>"""
SHOW = """
            <label>
                <input type="checkbox" name="show"%s/>
                %s
            </label>"""
TEMPLATE = """<form 
    class="form-inline" method="POST" action="%s/change" id="change-skill-%s">
        <span class="control-group">
            %s
            %s
        </span>
    <input type="hidden" name="from_url" value="%s"/>
</form>"""

class ChangeSkill(BrowserView, Skill):
    """ Change skill values
    """
    implements(IChangeSkill)

    def __call__(self):
        request = self.request
        form = request.form
        self.current()
        ajax = request.get('HTTP_X_REQUESTED_WITH', None)
        position, (member, level, show) = self.current_entry()

        from_url = ''
        if form:
            self.change_skill(position, member, level, show, form)
            from_url = form.get('from_url', '')
            if not ajax:
                return request.response.redirect(from_url)

        context = self.context
        url = context.absolute_url()
        if not ajax:
            return request.response.redirect(url)

        position, (member, level, show) = self.current_entry()
        levels = []
        if level in ['x', 'X']:
            title = context.translate(_(u"(Experience level unknown)"))
            levels.append(LEVEL % ('X', SELECTED, title))
        e_val = True if level is False else False
        for l in self.levels:
            v, t = l[:2]
            s = SELECTED if v == level or v == '' and e_val else ''
            levels.append(LEVEL % (v, s, t))
        levels = LEVELS % '\n'.join(levels)
        show = SHOW % (
            ' checked="checked"' if show not in ['', 'n', False] else '', 
            context.translate(_(u'Public')))

        return TEMPLATE % (url, position, levels, show, from_url)


class SkillView(BrowserView, Skill):
    """ Walkthrough view
    """
    implements(ISkillView)

    template = ViewPageTemplateFile('templates/skill.pt')

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

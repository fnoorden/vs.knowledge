from Acquisition import aq_parent
from collections import defaultdict
from plone import api
from Products.Five import BrowserView
from vs.knowledge.interfaces import IKnowledgeView
from zope.interface import implements


class Knowledge(BrowserView):

    def current(self):
        return api.user.get_current()

    def current_properties(self):
        current = self.current()
        c_id = current.getId()
        cteam = current.getProperty('cteam')
        fullname = current.getProperty('fullname')
        return { 'id': c_id, 'cteam': cteam, 'fullname': fullname }

    def current_entry(self, skill=None):
        """
        """
        c_id = self.current().getId()
        if not skill:
            skill = self.context
            # Check assumption and escape if necessary
            if skill.portal_type != 'skill':
                return (-1, (c_id, None, None))

        for position, mls in enumerate(skill.member_level_show):
            member, level, show = tuple(mls.split('|'))
            if member == c_id:
                return (position, (member, level, show))

        return (-1, (c_id, None, None))

    def knowledge_profile(self):
        context = self.context
        if context.portal_type == 'knowledge_profile':
            return context
        if context.portal_type == 'skill':
            parent = aq_parent(context)
            if parent.portal_type != 'knowledge_profile':
                return False
            return parent
        return False

    def skills(self):
        context = self.knowledge_profile()
        eg = context.expertises_groups
        return sorted(
            context.contentValues(), key=lambda x: (eg.index(x.group), x.id))

    def levels(self):
        kp = self.knowledge_profile()
        return [l.split('|') for l in kp.levels if l.index('|') > -1]


class KnowledgeView(Knowledge):
    implements(IKnowledgeView)

    def add_column(self):
        self.column_totals += [0]

    def set_column_totals(self, memberorder):
        amount = 0
        for cteam in memberorder:
            amount += len(cteam[1])
        self.column_totals = [0] * amount        
        # import sys;sys.stdout=file('/dev/stdout','w')
        # import pdb; pdb.set_trace()

    def update_column_totals(self, i, value):
        try:
            self.column_totals[i] += value
        except:
            pass
            # import sys;sys.stdout=file('/dev/stdout','w')
            # import pdb; pdb.set_trace()

    def members(self):
        userdict = defaultdict(list)
        for u in sorted(api.user.get_users(), 
                        key=lambda x: x.getProperty('fullname')):
            cteam = u.getProperty('cteam').strip()
            userdict[cteam if cteam else 'other'].append(u)
        return userdict

    def memberorder(self, members=None):
        if not members:
            members = self.members()
        return tuple([(k, tuple([m.getId() for m in members[k]])) 
                      for k in sorted(members.keys())])

    def current_skills(self):
        grouped_skills = defaultdict(list)

        for skill in self.skills():
            position, (member, level, show) = self.current_entry(skill)

            if level:
                group = skill.group.split('|')[1]
                if level == 'X':
                    grouped_skills[group].append(skill.title)
                else:
                    grouped_skills[group].append('%s (%s)' % (
                        skill.title, level))
                if ('o' not in grouped_skills or 
                    group not in grouped_skills.get('o', [])):
                    grouped_skills['o'].append(group)

        return grouped_skills

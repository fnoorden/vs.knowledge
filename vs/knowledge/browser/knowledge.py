from Acquisition import aq_parent
from cStringIO import StringIO
from collections import defaultdict
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from vs.knowledge import VSKnowledgeMessageFactory as _
from vs.knowledge.interfaces import IKnowledgeView
from zope.interface import implements


import csv, time

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

    def data(self):
        """
        """
        context = self.context
        members = self.members()
        skills = self.skills()
        memberorder = self.memberorder(members)

        ordered_members = []
        group_lengths = []
        for cteam, cteam_members in memberorder:
            group_lengths.append(len(cteam_members))
            ordered_members += cteam_members

        # Row with employee names
        names = [''] * 4 # Prefill with 5 empties
        Total = context.translate(_(u"Total"))
        names.append(Total)
        for cteam in sorted(members.keys()):
            names += [m.getProperty('fullname') for m in members[cteam]]
        employee_count = len(names) - 5

        # Row with headers and column_counts
        Expertise = context.translate(_(u"Expertise"))
        Subgroup = context.translate(_(u"Subgroup"))
        Name = context.translate(_(u"Name"))
        Searchterms = context.translate(_(u"Searchterms"))

        total = 0
        totals = [Expertise, Subgroup, Name, Searchterms]
        totals += [0] * employee_count

        # Full data set
        _d = [] # Data
        _expertise, _group = '', ''
        for skill in skills:
            row_total = 0

            # Headers
            expertise_group = skill.group.split('|')
            expertise = expertise_group[0] if len(expertise_group) == 2 else ''
            group = expertise_group[1] if len(expertise_group) == 2 else ''
            title = skill.title
            description = skill.description

            # Fill row data
            row = [expertise if expertise != _expertise else '',
                   group if group != _group else '',
                   title, description]
            levels = dict([
                (x.split('|')[0], x.split('|')[1]) 
                for x in skill.member_level_show if len(x.split('|')) == 3])
            for i, member in enumerate(ordered_members):
                value = levels.get(member, False)
                # Add value to row
                row.append(value if value else '')

                # Calculations
                try:
                    amount = int(value)
                except ValueError:
                    amount = 1 if value in ['x', 'X'] else 0
                row_total += amount
                total += amount
                totals[i + 4] += amount
            row.insert(4, row_total)
            _d.append(row)

        totals.insert(4, total)
        _d.insert(0, names)
        _d.insert(1, totals)

        return _d

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


class KnowledgeView(Knowledge):
    implements(IKnowledgeView)

    def set_column_totals(self, memberorder):
        amount = 0
        for cteam in memberorder:
            amount += len(cteam[1])
        self.column_totals = [0] * amount

    def update_column_totals(self, i, value):
        self.column_totals[i] += value

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


class KnowledgeExport(Knowledge):
    implements(IKnowledgeView)

    def processEntry(self, entry):
        """ Some processing to clean up entries
        """
        if not entry:
            return ''

        # normalize to list
        result = []
        if not isinstance(entry, (list, tuple)):
            entry = [entry,]
        for e in entry:
            if e is None:
                e = ''
            elif not isinstance(e, str) and hasattr(e, 'Title'):
                e = e.Title()
            elif isinstance(e, unicode):
                e = e.encode('utf-8')
            elif not isinstance(e, str):
                e = str(e)
            result.append(e)
        return "\n".join(result)

    def export_csv(self, name, data, RESPONSE):
        """ Do a CSV export from a Python list
        """
        buffer = StringIO()
        writer = csv.writer(buffer, quoting=1)
        for row in data:
            writer.writerow(row)
        value = buffer.getvalue()
        value = unicode(value, "utf-8").encode("iso-8859-1", "replace")
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition', 
            'attachment;filename=%s-%s.csv' % (
                name, time.strftime("%Y%m%d-%H%M")))
        return value

    def __call__(self):
        """ 
        """
        data = self.data()

        # Add legend with some space
        data.append([])
        data.append([])
        data.append([self.context.translate(_(u"Legend"))])
        data += self.levels()[1:]

        # Clean up entries
        data = [[self.processEntry(column) for column in row] for row in data]

        # Create and send back a *.csv file
        return self.export_csv('knowledge', data, self.request.RESPONSE)


class KnowledgeCleanup(Knowledge):
    """
    """

    template = ViewPageTemplateFile('templates/knowledge-cleanup.pt')

    def __call__(self):
        skills = self.skills()

        form = self.request.form
        if 'remove' in form:
            remove = form['remove']
            if isinstance(remove, str):
                remove = [remove,]
            self.cleanup_skills(remove, skills)

        self.cleanup = self.missing_members(skills)

        return self.template()

    def cleanup_skills(self, remove, skills):
        for skill in skills:
            new_member_level_show = []
            for mls in skill.member_level_show:
                member, level, show = mls.split('|')
                member = member.strip()
                if member not in remove:
                    new_member_level_show.append(mls)
            skill.member_level_show = new_member_level_show
            self.context.plone_utils.addPortalMessage(
                'The following users were removed from all skills: %s' % 
                    ', '.join(remove))

    def missing_members(self, skills):
        missing_members = set()
        existing_members = set()

        for skill in skills:
            for mls in skill.member_level_show:
                member, level, show = mls.split('|')
                member = member.strip()
                if (member not in existing_members and
                    member not in missing_members):
                    if not api.user.get(member):
                        missing_members.add(member)
                    else:
                        existing_members.add(member)

        return missing_members

from Acquisition import aq_parent
from cStringIO import StringIO
from collections import defaultdict
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from vs.knowledge import VSKnowledgeMessageFactory as _
from vs.knowledge import interfaces
from zope.interface import implements

import csv, time

class Knowledge(BrowserView):

    def current(self):
        """ Current member
        """
        current = api.user.get_current()
        c_id = current.getId()
        self.current_id = c_id
        self.current_cteam = current.getProperty('cteam')
        self.current_fullname = current.getProperty('fullname') or c_id

    @property
    def knowledge_profile(self):
        """ For contained skills and itself return the knowledge_profile object
        """
        context = self.context

        if context.portal_type == 'knowledge_profile':
            return context

        if context.portal_type == 'skill':
            parent = aq_parent(context)
            if parent.portal_type != 'knowledge_profile':
                return False
            return parent

        return False

    @property
    def skills(self):
        """ Return the skills sorted by the order of expertises and groups
            set on the knowledge_profile
        """
        context = self.knowledge_profile
        eg = context.expertises_groups

        skills = sorted(
            context.contentValues(), key=lambda x: (eg.index(x.group), x.id))
        self.skill_count = len(skills)
        return skills

    def current_entry(self, skill=None):
        """ Entry of the current member in member_level_show
        """
        if not skill:
            skill = self.context
            # Check assumption and escape if necessary
            if skill.portal_type != 'skill':
                return (-1, (self.current_id, None, None))

        for position, mls in enumerate(skill.member_level_show):
            member, level, show = tuple(mls.split('|'))
            if member == self.current_id:
                return (position, (member, level, show))

        return (-1, (self.current_id, None, None))

    @property
    def levels(self):
        context = self.knowledge_profile
        levels = [l.split('|') for l in context.levels if l.index('|') > -1]
        self.legend = levels[1:]
        return levels

    def _setup_members(self, single):
        """ Member handling
        """
        self.current()
        if not single:
            self.order_members()
        else:
            self.ordered_members = [self.current_id]

    def _set_messages(self):
        """ Add portal messages
        """
        ptools = self.context.plone_utils
        if self.e_count:
            if self.e_count == self.skill_count:
                ptools.addPortalMessage(
                    _(u'You have empty profile, '
                       'please qualify your experience level for each skill.'),
                    'error')
            else:
                ptools.addPortalMessage(
                    _(u'You have empty entries in your profile, '
                       'please add an experience level.'),
                    'error')
        if self.x_count:
            ptools.addPortalMessage(
                _(u'You have entries with an x value in your profile, '
                   'please qualify your experience level.'),
                'warning')

    def data(self, single=False):
        """ Build up data table
        """
        context = self.context

        self._setup_members(single)

        # Set up headers
        Expertise = context.translate(_(u"Expertise"))
        Subgroup = context.translate(_(u"Subgroup"))
        Name = context.translate(_(u"Name"))
        Searchterms = context.translate(_(u"Searchterms"))
        if not single:
            Total = context.translate(_(u"Total"))

            # Row with employee names
            names = [''] * 4 # Prefill with 5 empties
            names.append(Total)
            names += self.fullnames
            employee_count = len(self.fullnames)

            # Row with headers and column_counts
            total = 0
            totals = [Expertise, Subgroup, Name, Searchterms]
            totals += [0] * employee_count
        else:
            # Row with headers
            headers = [
                Expertise, Subgroup, Name, Searchterms, self.current_fullname]

        # Full data set
        _d = [] # Data

        self.x_count, self.e_count = 0, 0 # Count
        _expertise, _group = '', '' # Sticky expertise and group

        for skill in self.skills:
            row_total = 0

            # Row headers
            expertise_group = skill.group.split('|')
            if len(expertise_group) == 2:
                expertise, group = expertise_group
            else:
                expertise, group = ('', '')
            title = skill.title
            description = skill.description

            # Prepend headers
            row = [expertise if expertise != _expertise else '',
                   group if group != _group else '',
                   title, description]

            # Update sticky expertise and group
            _expertise, _group = expertise, group

            # Parse member_level_show
            levels = dict([
                (x.split('|')[0], (x.split('|')[1], x.split('|')[2])) 
                for x in skill.member_level_show if len(x.split('|')) == 3])
            for i, member in enumerate(self.ordered_members):
                level, show = levels.get(member, (False, False))
                is_current = member == self.current_id
                cell_class, x_val = '', False

                # Calculations
                if level:
                    try:
                        amount = int(level)
                    except ValueError:
                        if level in ['x', 'X']:
                            amount = 1
                            x_val = True
                            if is_current:
                                self.x_count += 1
                                cell_class = 'update'
                else:
                    amount = 0
                if level is False and is_current:
                    self.e_count += 1
                    cell_class = 'empty'

                # Add level to row
                if not single:
                    row.append(level if level else '')
                    row_total += amount
                    total += amount
                    totals[i + 4] += amount
                else:
                    row.append({
                        "level": level if level else '',
                        "x_val": x_val,
                        "show": (
                            True if show not in ['', 'n', False] else False),
                        'url': skill.absolute_url(),
                        'cclass': cell_class
                    })

            if not single:
                row.insert(4, row_total)
            _d.append(row)

        if not single:
            totals.insert(4, total)
            _d.insert(0, names)
            _d.insert(1, totals)
        else:
            _d.insert(0, headers)

        self._set_messages()

        return _d

    def members(self):
        userdict = defaultdict(list)

        for u in sorted(api.user.get_users(), 
                        key=lambda x: x.getProperty('fullname')):
            cteam = u.getProperty('cteam').strip()
            userdict[cteam if cteam else 'other'].append(u)

        return userdict

    def order_members(self, members=None):
        if not members:
            members = self.members()

        self.ordered_cteams = [] # Tuples of (cteam, member_ids)
        self.ordered_members = [] # Memberids ordered on cteam
        self.column_classes = []
        self.fullnames = []
        for k in sorted(members.keys()):
            cteam, cteam_members = k, []
            for m in members[k]:
                m_id = m.getId()
                cteam_members.append(m_id)
                self.ordered_members.append(m_id)
                self.fullnames.append(m.getProperty('fullname'))
                if m_id == self.current_id:
                    self.column_classes.append(k + ' current')
                else:
                    self.column_classes.append(k)
            self.ordered_cteams.append((cteam, cteam_members))


class KnowledgeView(Knowledge):
    implements(interfaces.IKnowledgeView)


class ProfileView(Knowledge):
    implements(interfaces.IProfileView)


class CVView(Knowledge):
    implements(interfaces.ICVView)

    def data(self):
        # Member handling
        self.current()

        skills = defaultdict(list)
        order = []
        for skill in self.skills:
            position, (member, level, show) = self.current_entry(skill)

            if level:
                group = skill.group.split('|')[1]
                if level == 'X':
                    skills[group].append(skill.title)
                else:
                    skills[group].append('%s (%s)' % (
                        skill.title, level))
                if group not in order:
                    order.append(group)

        return [(i, skills[i]) for i in order]


class KnowledgeExport(Knowledge):
    implements(interfaces.IKnowledgeExport)

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
        levels = self.levels
        data.append([])
        data.append([])
        data.append([self.context.translate(_(u"Legend"))])
        data += self.legend

        # Clean up entries
        data = [[self.processEntry(column) for column in row] for row in data]

        # Create and send back a *.csv file
        return self.export_csv('knowledge', data, self.request.RESPONSE)


class CleanupView(Knowledge):
    implements(interfaces.ICleanupView)

    template = ViewPageTemplateFile('templates/cleanup.pt')

    def __call__(self):
        skills = self.skills

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
                _(u'The following users were removed from all skills: ')
                + ', '.join(remove))

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

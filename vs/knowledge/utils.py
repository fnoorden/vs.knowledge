from Acquisition import aq_parent
from collections import defaultdict
from plone import api
from Products.CMFCore.utils import getToolByName

try:
    from plone.app import ldap
    from Acquisition import aq_inner
    from zope.component import getMultiAdapter
    from itertools import chain
    HAS_LDAP = True
except ImportError:
    HAS_LDAP = False

from vs.knowledge import VSKnowledgeMessageFactory as _


class Knowledge(object):
    """ Knowledge utils mixin
    """

    def current(self):
        """ Current member
        """
        current = api.user.get_current()
        self.authenticated_id = current.getId()

        if hasattr(self, 'author'):
            c_id = self.other_id = self.author
        elif hasattr(self, 'other_id'):
            c_id = self.other_id
        else:
            c_id = self.other_id = self.request.get('other', None)

        if c_id:
            current = api.user.get(c_id)
        else:
            c_id = current.getId()
        self.current_id = c_id
        self.current_cteam = current.getProperty('cteam')
        self.current_fullname = current.getProperty('fullname') or c_id
        self.current_firstname = self.current_fullname.split()[0]

        if self.other_id:
            other = api.user.get(self.other_id)
            self.other_cteam = other.getProperty('cteam')
            self.other_fullname = other.getProperty('fullname') or c_id
            self.other_firstname = self.other_fullname.split()[0]


    @property
    def knowledge_profile(self):
        """ For contained skills and itself return the knowledge_profile object
        """
        context = self.context

        # We are on a knowledge profile
        if context.portal_type == 'knowledge_profile':
            return context

        # We are on a skill
        if context.portal_type == 'skill':
            parent = aq_parent(context)
            if parent.portal_type == 'knowledge_profile':
                return parent

        # We are somewhere else
        pc = getToolByName(self.context, "portal_catalog")
        kps = pc(portal_type="knowledge_profile")
        if len(kps) > 0:
            # Return the first knowledge profile
            return kps[0].getObject()

        return False

    @property
    def skills(self):
        """ Return the skills sorted by the order of expertises and groups
            set on the knowledge_profile
        """
        kp = self.knowledge_profile
        eg = kp.expertises_groups

        skills = sorted(
            kp.contentValues(), key=lambda x: (eg.index(x.group), x.id))
        self.skill_count = len(skills)
        return skills

    def current_entry(self, skill=None):
        """ Entry of the current member in member_level_show
        """
        empty = (-1, (self.current_id, None, None))
        if not skill:
            skill = self.context
            # Check assumption and escape if necessary
            if skill.portal_type != 'skill':
                return empty

        if not skill.member_level_show:
            return empty

        for position, mls in enumerate(skill.member_level_show):
            member, level, show = tuple(mls.split('|'))
            if member == self.current_id:
                return (position, (member, level, show))

        return empty

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
                for x in skill.member_level_show if len(x.split('|')) == 3]
                if  skill.member_level_show else [])
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

        if not self.other_id:
            self._set_messages()

        return _d

    def grouped_skills(
        self, only_group=False, only_show=False, from_level=None):
        self.current()
        skills = defaultdict(list)
        order = []

        # If we don't have the flags from code, do we have them in the request?
        request = self.request
        if not only_show and 'only_show' in request:
            only_show = True
        if not from_level and 'from_level' in request:
            from_level = request.get('from_level')

        # Stricky exptertise
        _expertise, _group = '', ''
        for skill in self.skills:
            position, (member, level, show) = self.current_entry(skill)

            # Do we have level?
            # Is level high enough (string comparison) and not 'X'?
            # Does show have to be checked?
            if (not level or
                from_level and level in ['X', 'x'] or
                from_level and level < from_level or
                only_show and show in [False, '', 'n']):
                continue

            group = skill.group.split('|')
            _group = group[1]
            if only_group:
                expertise = group.pop(0) # Remove expertise header
            else:
                expertise = group[0]
                group[0] = expertise if expertise != _expertise else ''
                _expertise = expertise
            group = tuple(group)

            if level in ['X', 'x']:
                if (_expertise, _group) in skills:
                    skills[(_expertise, _group)].append(skill.title)
                else:
                    skills[group].append(skill.title)
            else:
                if (_expertise, _group) in skills:
                    skills[(_expertise, _group)].append('%s (%s)' % (
                        skill.title, level))
                else:
                    skills[group].append('%s (%s)' % (
                        skill.title, level))
            if (_expertise, _group) not in order and group not in order:
                order.append(group)

        return [(i, skills[i]) for i in order]

    def members(self):
        userdict = defaultdict(list)

        if HAS_LDAP:
            searchString, ignore = '', []

            mtool = getToolByName(self, 'portal_membership')
            searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')
            userResults = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['name', 'fullname', 'email']]), 'userid')
            userResults = [mtool.getMemberById(u['id']) for u in userResults if u['id'] not in ignore]
        else:
            userResults = api.user.get_users()

        for u in sorted(userResults, key=lambda x: x.getProperty('fullname')):
            cteam = u.getProperty('cteam').strip()
            userdict[cteam if cteam else 'other'].append(u)

        return userdict

    def order_members(self, members=None):
        exclude = self.knowledge_profile.exclude or []
        if not members:
            members = self.members()

        self.ordered_cteams = [] # Tuples of (cteam, member_ids)
        self.ordered_members = [] # Memberids ordered on cteam
        self.column_classes = []
        self.fullnames = []
        self.memberids = []
        for k in sorted(members.keys()):
            cteam, cteam_members = k, []

            for m in members[k]:
                m_id = m.getId()

                if m_id in exclude:
                    continue
                cteam_members.append(m_id)
                self.ordered_members.append(m_id)
                fn = m.getProperty('fullname')
                self.fullnames.append(fn)
                if m_id == self.current_id:
                    self.memberids.append((fn, None))
                    self.column_classes.append(k + ' current')
                else:
                    self.memberids.append((fn, m_id))
                    self.column_classes.append(k)

            self.ordered_cteams.append((cteam, cteam_members))
        self.memberids = dict(self.memberids)


class Skill(Knowledge):
    """ Skill utils mixin
    """

    def change_skill(self, position, member, level, show, form):
        """
        """
        mls = self.context.member_level_show or []

        new_level = form.get('level', '')
        new_show = form.get('show', '')
        new = u'|'.join([member, new_level, new_show])

        if position < 0:
            mls.append(new)
        else:
            mls[position] = new

        setattr(self.context, 'member_level_show', mls)

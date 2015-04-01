from cStringIO import StringIO
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from vs.knowledge import interfaces
from vs.knowledge import VSKnowledgeMessageFactory as _
from vs.knowledge.utils import Knowledge
from zope.interface import implements
import csv
import time


class KnowledgeView(BrowserView, Knowledge):
    implements(interfaces.IKnowledgeView)


class ProfileView(BrowserView, Knowledge):
    implements(interfaces.IProfileView)

    @property
    def experience(self):
        return _(u"Experience")


class CVView(BrowserView, Knowledge):
    implements(interfaces.ICVView)


class KnowledgeExport(BrowserView, Knowledge):
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


class CleanupView(BrowserView, Knowledge):
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

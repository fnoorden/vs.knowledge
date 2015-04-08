from plone import api
from Products.CMFCore.utils import getToolByName

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('vs.knowledge_various.txt') is None:
        return

    # On installation of this Plone add-on we want the initial 
    # Knowlegde Profile to be generated out of the provided table data.
    # It is a complex data table with the first four colums functioning as 
    # row headers. The top row are the headers for the columns.
    _data = context.readDataFile('import.csv')
    if _data is None:
        return

    # Turn the data from a *.cvs into a list-of-lists
    data = [l.split(';') for l in _data.split('\n')]

    # Split the header row from the actual table data
    headers = data.pop(0)

    # Get membership tools for matching the member names with a user object
    portal = api.portal.get()
    mtool = getToolByName(portal, 'portal_membership')
    for i, h in enumerate(headers):
        # The first four headers accompany the column headers
        if i < 4:
            continue
        # The following headers are the fullname of a user, e.g. 'John Doe'
        fullname = headers[i]
        members = mtool.searchForMembers(name=fullname) # returns a list
        if members:
            # Swap out the initial fullname with the member id. It is better to
            # get user objects with it's unique id.
            member = members[0]
            headers[i] = member.getId()

    # Build up the allowed values for Expertise and Group, to choose from
    # when creating a table row. This is one of the values that needs to be 
    # filled in for the Knowledge Profile content type. Skills created
    # withing the Knowledge Profile can choose one of the Groups defined on
    # the Knowledge Profile.
    #
    # Only the first cell from the top has a value for both expertise and 
    # group. Example:
    #
    #    Expertise 1   | Group 1   | Title 1
    #                  |           | Title 2
    #                  | Group 2   | Title 3
    #    Expertise 2   | Group 3   | Title 4 
    # 
    # We want the following result:
    #   
    #   Expertise 1|Group 1
    #   Expertise 1|Group 2
    #   Expertise 2|Group 3
    #
    expertise = ''
    expertises_groups = []
    for c in data:
        # In case of empty row, or empty values for both expertise and group,
        # continue.
        if len(c) < 2 or not (c[0] or c[1]):
            continue
        if c[0]:
            # Expertise is outside of the loop and has a 'sticky' value
            expertise = c[0].strip()
        try:
            group = c[1].strip()
        except:
            import sys;sys.stdout=file('/dev/stdout','w')
            import pdb; pdb.set_trace()
        expertises_groups.append('|'.join([expertise, group]))

    # Create the Knowledge Profile content item
    profile = api.content.create(
        container=portal,
        type="knowledge_profile",
        title="Competence Profiel",
        levels=[
            "|Geen ervaring",
            "1|Beginner",
            "2|Gevorderde beginner",
            "3|Competent",
            "4|Bedreven",
            "5|Expert",
            ],
        exclude=[
            "cseegers",
            "jvanrossum",
            "kvanrossum",
            "mvandenberg",
            "pvanderwaals",
            "rthoonsen",
            "tliefting",
            ],
        expertises_groups = expertises_groups,
        )
    api.content.move(source=profile, target=portal.cteams)
    profile.reindexObject()

    # Fill the Knowledge Profile with skills, prefilled for the known users
    expertise, group = '', ''
    for c in data:
        # The first four columns provide the title, description and group, 
        # the columns after that fill the data values for the row.
        # each line in the values field contains userid|value|show_in_profile.
        if len(c) < 4 or not c[2]:
            continue
        if c[0]:
            # Expertise has a 'sticky' value
            expertise = c[0].strip()
        if c[1]:
            # Expertise has a 'sticky' value
            group = c[1].strip()
        # Title is always present and used to create the objects id on
        # generation. Description can be empty, e.g. ''.
        title, description = c[2].strip(), c[3].strip()
        # The userids and the skill level data
        userids = headers[4:]
        entries = c[4:]
        values = []
        for i, e in enumerate(entries):
            values.append('|'.join([userids[i], e, 'n']))
        skill = api.content.create(
            container=profile,
            type="skill",
            title=title,
            description=description,
            group="|".join([expertise, group]),
            member_level_show=values,
            )
        skill.reindexObject()

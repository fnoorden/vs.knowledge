from plone.app.upgrade.utils import loadMigrationProfile

def v1_to_v2(context):
    """ Invokes an extension profile which in turn performs a migration """
    loadMigrationProfile(context, 'profile-cmaas.sciencelab:v1-v2')  

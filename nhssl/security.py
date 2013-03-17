from pyramid.traversal import find_root
from pyramid.security import authenticated_userid
GROUPS = {'student': ['group:students'],
          'officer': ['group:officers'],
          'advisor': ['group:advisors']}


def groupfinder(user_id, request):
    groups = []
    if user_id is not None:
        groups.append('group:registered')
        profile = find_root(request.context)['users'][user_id]
        if profile.isStudent:
            groups.append('group:students')
        if profile.isOfficer:
            groups.append('group:officers')
        if profile.isAdvisor:
            groups.append('group:advisors')
    return groups

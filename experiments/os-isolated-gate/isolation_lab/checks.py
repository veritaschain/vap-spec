"""Complete inventories are required before an isolation observation can pass."""
import errno
from . import ROLES


def filesystem_permissions_match(files):
    if not isinstance(files, dict) or set(files) != set(ROLES):
        return False
    for role, observation in files.items():
        if not isinstance(observation, dict):
            return False
        own = observation.get('own_config_readable', {})
        canaries = observation.get('canaries')
        if not isinstance(own, dict) or own.get('allowed') is not True or not isinstance(canaries, dict) or set(canaries) != set(ROLES):
            return False
        for other, result in canaries.items():
            if not isinstance(result, dict):
                return False
            if other == role:
                if result.get('allowed') is not True or result.get('errno') is not None:
                    return False
            elif (result.get('allowed') is not False or type(result.get('errno')) is not int
                  or result['errno'] != errno.EACCES):
                return False
    return True


def runtime_mounts_match(role, runtime, project):
    expected = {
        '/run/role': ('volume', project + '_' + role + '-config', False),
        '/data': ('volume', project + '_' + role + '-data', True),
        '/canaries': ('volume', project + '_canaries', False),
    }
    tmpfs = runtime.get('tmpfs')
    if not isinstance(tmpfs, dict) or set(tmpfs) != {'/tmp'} or not isinstance(tmpfs['/tmp'], str):
        return False
    options = set(tmpfs['/tmp'].split(','))
    if not {'rw', 'noexec', 'nosuid'}.issubset(options) or options & {'ro', 'exec', 'suid'}:
        return False
    mounts = runtime.get('mounts')
    if not isinstance(mounts, list) or len(mounts) != len(expected):
        return False
    if any(not isinstance(m, dict) for m in mounts):
        return False
    if {m.get('destination') for m in mounts} != set(expected):
        return False
    return all(m.get('type') == expected[m['destination']][0]
               and m.get('name') == expected[m['destination']][1]
               and m.get('rw') is expected[m['destination']][2] for m in mounts)

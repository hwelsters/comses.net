from invoke import Collection

from . import borg, database, docs, elasticsearch, drupal, permission
from .base import clean, collect_static, coverage, deny_robots, quality_check_openabm_files_with_db, sh, test, server, setup_site


ns = Collection()
ns.add_task(clean)
ns.add_task(collect_static)
ns.add_task(coverage)
ns.add_task(deny_robots)
ns.add_task(quality_check_openabm_files_with_db)
ns.add_task(sh)
ns.add_task(test)
ns.add_task(server)
ns.add_task(setup_site)
ns.add_collection(borg)
ns.add_collection(Collection.from_module(database, 'db'))
ns.add_collection(docs)
ns.add_collection(Collection.from_module(elasticsearch, 'es'))
ns.add_collection(drupal)
ns.add_collection(Collection.from_module(permission, 'perm'))

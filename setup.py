#
# Run with: $ python setup.py build_ext --inplace
#
# Erase with: $ find appli to_back -name "*.so" -delete; rm *.so
#
from setuptools import setup

from mypyc.build import mypycify

setup(
    name='ecotaxa_front',
    packages=['appli'],
    ext_modules=mypycify([
        # 'appli/__init__.py', Problems in gvg and gvp, as flask typing is wrong
        'appli/api_proxy.py',
        'appli/constants.py',
        'appli/main.py',
        'appli/utils.py',
        'appli/project',
        'appli/search',
        'appli/taxonomy',
        'appli/jobs/emul.py',
        'appli/jobs/Job.py',
        'appli/jobs/views.py',
        'to_back/booster.py', # Problem was visible in category search boxes, and in project setting - "Pick from other projects"
    ]),
)

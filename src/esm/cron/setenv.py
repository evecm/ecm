import os, sys

ISM = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
PARENT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))

sys.path.append(ISM)
sys.path.append(PARENT)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ism.settings'

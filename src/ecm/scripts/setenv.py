import os, sys

ECM = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
PARENT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))

sys.path.append(ECM)
sys.path.append(PARENT)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ecm.settings'

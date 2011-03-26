from ecm.data.common.models import UpdateDate
from ecm.core import utils
#------------------------------------------------------------------------------
def getScanDate(model_name):
    try:
    date = UpdateDate.objects.get(model_name=model_name) 
        return utils.print_time_min(date.update_date)
    except:
        return "<no data>"

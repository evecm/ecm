# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2010-03-29"
__author__ = "diabeteman"


from django.db import transaction
from ecm.core import api
from ecm.core.parsers.utils import checkApiVersion
from ecm.data.accounting.models import EntryType
import logging


logger = logging.getLogger(__name__)


#------------------------------------------------------------------------------
@transaction.commit_manually
def update():
    try:
        logger.info("fetching /eve/RefTypes.xml.aspx...")
        # connect to eve API
        api_conn = api.connect()
        # retrieve /corp/CorporationSheet.xml.aspx
        typesApi = api_conn.eve.RefTypes()
        checkApiVersion(typesApi._meta.version)

        currentTime = typesApi._meta.currentTime
        cachedUntil = typesApi._meta.cachedUntil
        logger.debug("current time : %s", str(currentTime))
        logger.debug("cached util : %s", str(cachedUntil))
        logger.debug("parsing api response...")
        
        
        for type in typesApi.refTypes:
            entryType = EntryType()
            entryType.refTypeID = type.refTypeID
            entryType.refTypeName = type.refTypeName
            entryType.save()
        
        logger.debug("Saving to database...")
        transaction.commit()
        logger.info("Update successfull")
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("update failed")




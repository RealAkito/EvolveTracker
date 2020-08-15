from twisted.internet.defer import succeed
from twisted.application import internet
from twisted.web import static, server, proxy
from klein import Klein
from BlissBotMain import logger
import json

################################################################
# Web events
webapp = Klein()


@webapp.route('/', methods=['POST'])
def Submission(request):
    content = json.loads(request.content.read())
    logger.info(f"Received data:\n{str(content)}")

    # TODO: find the channel/bot it needs to be in and announce.
    return succeed(None)


def InitializeDelivery(application):
    logger.info("Initializing Delivery.")
    w = server.Site(webapp.resource())
    website = internet.TCPServer(2222, w)
    website.setServiceParent(application)
    return website

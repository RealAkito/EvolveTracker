# For accessing the terminal
from twisted.cred import checkers, portal
from twisted.internet import protocol
from twisted.conch.manhole import ColoredManhole
from twisted.conch.insults import insults
from twisted.conch.telnet import TelnetTransport, TelnetBootstrapProtocol
from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm
from twisted.application import service, internet
from BlissBotMain import logger


def _makeService(args):
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(
        admin="password")

    f = protocol.ServerFactory()
    f.protocol = lambda: TelnetTransport(
        TelnetBootstrapProtocol, insults.ServerProtocol, args[
            'protocolFactory'], *args.get('protocolArgs', ()),
        **args.get('protocolKwArgs', {}))
    tsvc = internet.TCPServer(args['telnet'], f)

    def chainProtocolFactory():
        return insults.ServerProtocol(args['protocolFactory'],
                                      *args.get('protocolArgs', ()),
                                      **args.get('protocolKwArgs', {}))

    rlm = TerminalRealm()
    rlm.chainedProtocolFactory = chainProtocolFactory
    ptl = portal.Portal(rlm, [checker])
    f = ConchFactory(ptl)
    #csvc = internet.TCPServer(args['ssh'], f)

    m = service.MultiService()
    tsvc.setServiceParent(m)
    #csvc.setServiceParent(m)
    return m


def CreateManhole(application, arguments):
    logger.info("Creating new manhole on port 6023")
    _makeService({
        'protocolFactory': ColoredManhole,
        'protocolArgs': arguments,
        'telnet': 6023
    }).setServiceParent(application)

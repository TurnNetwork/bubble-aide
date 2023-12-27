import functools
import json
import os
import sys
import warnings
from os.path import abspath
from typing import cast

from bubble import Web3, HTTPProvider, WebsocketProvider, IPCProvider
from bubble._utils.threads import Timeout
from bubble.datastructures import AttributeDict
from bubble.exceptions import ContractLogicError
from bubble.middleware import node_poa_middleware
from bubble.types import RLPEventData

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport

from bubble_aide.statics.economic import new_economic

precompile_contracts = [
    '0x1000000000000000000000000000000000000001',
    '0x1000000000000000000000000000000000000002',
    # '0x1000000000000000000000000000000000000003',    # Incentive pool address, no built-in contract
    '0x1000000000000000000000000000000000000004',
    '0x1000000000000000000000000000000000000005',
    '0x1000000000000000000000000000000000000006',
    # '0x2000000000000000000000000000000000000001',
    # '0x2000000000000000000000000000000000000002',
    # '0x1000000000000000000000000000000000000020',
]


def get_web3(uri, timeout=10, modules=None):
    """ Obtain web3 objects through rpc uri
    """
    if uri.startswith('http'):
        provider = HTTPProvider
    elif uri.startswith('ws'):
        provider = WebsocketProvider
    elif uri.startswith('ipc'):
        provider = IPCProvider
    else:
        raise ValueError(f'unidentifiable uri {uri}')

    with Timeout(timeout) as t:
        while True:
            web3 = Web3(provider(uri), modules=modules)
            if web3.is_connected():
                break
            t.sleep(1)

    return web3


def get_economic(aide):
    """ To obtain economic model data from a node, the node needs to open the debug interface
    """
    data = ''
    try:
        data = aide.debug.economic_config()
    except IOError:
        warnings.warn('The debug api is not open, cannot get the economic data automatically')

    economic = new_economic(data) if data else None

    return economic


def get_gql(uri):
    """ Obtain the gql object through the gql uri.
    """
    if uri.startswith('http'):
        transport = AIOHTTPTransport
    elif uri.startswith('ws'):
        transport = WebsocketsTransport
    else:
        raise ValueError(f'unidentifiable uri {uri}')

    # todo: Add timeout handling
    return Client(transport=transport(uri), fetch_schema_from_transport=True)


def execute_cmd(cmd):
    r = os.popen(cmd)
    out = r.read()
    r.close()
    return out


def mock_duplicate_sign(dtype, sk, blskey, block_number, epoch=0, view_number=0, block_index=0, index=0):
    if sys.platform in "linux,linux2":
        tool_file = abspath("tool/linux/duplicateSign")
        execute_cmd("chmod +x {}".format(tool_file))
    else:
        tool_file = abspath("tool/win/duplicateSign.exe")
    print("{} -dtype={} -sk={} -blskey={} -blockNumber={} -epoch={} -viewNumber={} -blockIndex={} -vindex={}".format(
        tool_file, dtype, sk, blskey, block_number, epoch, view_number, block_index, index))
    output = execute_cmd(
        "{} -dtype={} -sk={} -blskey={} -blockNumber={} -epoch={} -viewNumber={} -blockIndex={} -vindex={}".format(
            tool_file, dtype, sk, blskey, block_number, epoch, view_number, block_index, index))
    print(output)
    if not output:
        raise Exception("unable to use double sign tool")
    return output.strip("\n")

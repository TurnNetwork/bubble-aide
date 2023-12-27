import functools
from functools import wraps, partial
from typing import TYPE_CHECKING

from bubble._utils.abi import filter_by_name
from bubble.contract.contract import ContractFunction

from bubble_aide.abc.module import PrecompileContract

if TYPE_CHECKING:
    from bubble_aide import Aide


class Contract:

    def __init__(self,
                 aide: "Aide",
                 abi,
                 bytecode=None,
                 address=None,
                 ):
        self.aide = aide
        self.abi = abi
        self.bytecode = bytecode
        self.address = address
        self.origin = self.aide.bub.contract(address=self.address, abi=self.abi, bytecode=self.bytecode)
        self.functions = self.origin.functions
        self.events = self.origin.events
        self._set_functions(self.origin.functions)
        self._set_events(self.origin.events)
        self._set_fallback(self.origin.fallback)

    def _set_functions(self, functions):
        # The contract event and function will not have the same name, so there is no need to worry about attributes already existing
        for func in functions:
            warp_function = self._function_wrap(getattr(functions, func))
            setattr(self, func, warp_function)

    def _set_events(self, events):
        # The contract event and function will not have the same name, so there is no need to worry about attributes already existing
        for event in events:
            # Obtain method by method name
            warp_event = self._event_wrap(event)
            setattr(self, event.event_name, warp_event)

    def _set_fallback(self, fallback):
        if type(fallback) is ContractFunction:
            warp_fallback = self._fallback_wrap(fallback)
            setattr(self, fallback, warp_fallback)
        else:
            self.fallback = fallback

    def _function_wrap(self, func):
        abis = filter_by_name(func.fn_name, self.abi)
        if len(abis) == 0:
            raise ValueError('The method ABI is not found.')

        # todo：Handling overload methods
        abi = abis[0]

        if abi.get('stateMutability') in ['view', 'pure']:
            return contract_call(func)
        else:
            return partial(contract_transaction(func), self)

    @staticmethod
    def _event_wrap(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func().process_receipt(*args, **kwargs)

        return wrapper

    @staticmethod
    def _fallback_wrap(func):
        return contract_transaction(func)


def contract_call(func):
    """ Packaging class for Solidity contract call
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).call()

    return wrapper


def contract_transaction(func):
    """ Packaging class for Solidity contract transactions
    """

    @functools.wraps(func)
    def wrapper(self, *args, txn: dict = None, private_key=None, **kwargs):
        # Fill in the from address to prevent contract transactions from failing to verify the address when estimating gas
        txn = txn or {}
        if not txn.get('from'):
            account = self.aide.bub.account.from_key(private_key) if private_key else self.aide.account
            if account:
                txn['from'] = account.address

        txn = func(*args, **kwargs).build_transaction(txn)
        return self.aide.send_transaction(txn, private_key=private_key)

    return wrapper

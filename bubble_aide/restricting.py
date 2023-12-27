from typing import TYPE_CHECKING

from bubble_aide.abc.module import PrecompileContract
from bubble_aide.utils.wrapper import contract_transaction

if TYPE_CHECKING:
    from bubble_aide import Aide


class Restricting(PrecompileContract):
    restrictingGas: int = 100000

    def __init__(self, aide: "Aide"):
        super().__init__(aide)
        self.address = self.aide.web3.restricting.ADDRESS
        self._result_type = 'event'

    @contract_transaction()
    def restricting(self, release_address, plans, txn=None, private_key=None):
        return self.aide.web3.restricting.create_restricting(release_address, plans)

    def get_restricting_info(self, release_address):
        return self.aide.web3.restricting.get_restricting_info(release_address).call()

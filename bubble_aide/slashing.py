from typing import TYPE_CHECKING

from bubble_aide.abc.module import PrecompileContract
from bubble_aide.utils.wrapper import contract_transaction

if TYPE_CHECKING:
    from bubble_aide import Aide


class Slashing(PrecompileContract):

    def __init__(self, aide: "Aide"):
        super().__init__(aide)
        self.address = self.aide.web3.dpos.slashing.ADDRESS

    @contract_transaction()
    def report_duplicate_sign(self,
                              report_type,
                              data,
                              txn=None,
                              private_key=None,
                              ):
        return self.aide.web3.dpos.slashing.report_duplicate_sign(report_type, data)

    def check_duplicate_sign(self,
                             report_type,
                             block_identifier,
                             node_id=None,
                             ):
        node_id = node_id or self.aide.constant.node_id
        return self.aide.web3.dpos.slashing.check_duplicate_sign(report_type, node_id, block_identifier).call()

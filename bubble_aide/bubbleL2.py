from typing import TYPE_CHECKING
from bubble.datastructures import AttributeDict

from bubble_aide.abc.module import PrecompileContract
from bubble_aide.utils.wrapper import contract_transaction

if TYPE_CHECKING:
    from bubble_aide import Aide


class BubbleL2(PrecompileContract):

    def __init__(self, aide: "Aide"):
        super().__init__(aide)
        self.address = self.aide.web3.subChain.bubbleL2.ADDRESS

    @contract_transaction()
    def mint_token(self,
                   tx_hash,
                   address,
                   amount,
                   tokens,
                   private_key=None,
                   txn=None,
                   ):
        return self.aide.web3.subChain.bubbleL2.mint_token(tx_hash=tx_hash, address=address, amount=amount,
                                                           tokens=tokens)

    @contract_transaction()
    def settle_bubble(self,
                      private_key=None,
                      txn=None,
                      ):
        return self.aide.web3.subChain.bubbleL2.settle_bubble()

    def get_L2hash_byL1hash(self, tx_hash):
        l2hash = self.aide.web3.subChain.bubbleL2.get_L2_hash_by_L1_hash(tx_hash).call()
        return l2hash





from typing import TYPE_CHECKING
from bubble.datastructures import AttributeDict

from bubble_aide.abc.module import PrecompileContract
from bubble_aide.utils.wrapper import contract_transaction

if TYPE_CHECKING:
    from bubble_aide import Aide


class Bubble(PrecompileContract):

    def __init__(self, aide: "Aide"):
        super().__init__(aide)
        self.address = self.aide.web3.subChain.bubble.ADDRESS

    @contract_transaction()
    def create_bubble(self,
                      size,
                      private_key=None,
                      txn=None,
                      ):

        return self.aide.web3.subChain.bubble.select_bubble(size)

    # @contract_transaction()
    # def release_bubble(self,
    #                  bubble_id,
    #                  private_key=None,
    #                  txn=None,
    #                  ):
    #     return self.aide.web3.subChain.bubble.release_bubble(bubble_id)


    def get_bubble_info(self, bubble_id):
        bubble_info = self.aide.web3.subChain.bubble.get_bubble_info(bubble_id).call()
        return bubble_info

    @contract_transaction()
    def staking_token(self,
                      bubble_id,
                      address,
                      amount,
                      tokens,
                      private_key=None,
                      txn=None,
                      ):
        return self.aide.web3.subChain.bubble.deposit_token(bubble_id, address, amount, tokens)

    @contract_transaction()
    def withdrew_token(self,
                       bubble_id,
                       private_key=None,
                       txn=None,
                       ):
        return self.aide.web3.subChain.bubble.withdrew_token(bubble_id=bubble_id)

    @contract_transaction()
    def settle_bubble(self,
                      tx_hash,
                      bubble_id,
                      settlement_info,
                      private_key=None,
                      txn=None,
                      ):
        return self.aide.web3.subChain.bubble.settle_bubble(tx_hash=tx_hash,
                                                            bubble_id=bubble_id,
                                                            settlement_info=settlement_info)


    def get_L1hash_byL2hash(self,
                            bubble_id,
                            tx_hash):
        l1hash = self.aide.web3.subChain.bubble.get_L1_hash_by_L2_hash(bubble_id=bubble_id,tx_hash=tx_hash).call()
        return l1hash

    def get_bub_txhash_list(self,
                            bubble_id,
                            tx_type):
        txhash_list = self.aide.web3.subChain.bubble.get_bub_txhash_list(bubble_id=bubble_id,tx_type=tx_type).call()
        return txhash_list
        
        


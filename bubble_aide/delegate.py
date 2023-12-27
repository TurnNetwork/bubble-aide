from typing import TYPE_CHECKING
from bubble.datastructures import AttributeDict

from bubble_aide.abc.module import PrecompileContract
from bubble_aide.utils.wrapper import contract_transaction

if TYPE_CHECKING:
    from bubble_aide import Aide


class Delegate(PrecompileContract):

    def __init__(self, aide: "Aide"):
        super().__init__(aide)
        self.address = self.aide.web3.dpos.delegate.ADDRESS

    @property
    def staking_block_number(self):
        return self.aide.staking.staking_info.StakingBlockNum

    @contract_transaction()
    def delegate(self,
                 amount=None,
                 balance_type=0,
                 node_id=None,
                 txn=None,
                 private_key=None,
                 ):
        """ Delegate nodes to obtain their reward dividends
        """
        amount = amount or self.aide.economic.delegate_limit
        node_id = node_id or self.aide.constant.node_id
        return self.aide.web3.dpos.delegate.delegate(node_id, balance_type, amount)

    @contract_transaction(1005)
    def withdrew_delegate(self,
                          amount=0,
                          staking_block_identifier=None,
                          node_id=None,
                          txn=None,
                          private_key=None,
                          ):
        """
        Revoke delegation to node, partial delegation can be revoked
        Note：Because the node may have pledged/revoked multiple times, which may leave the entrusted information behind, it is necessary to specify the node's pledge block when revoking the entrustment
        """
        node_id = node_id or self.aide.constant.node_id
        amount = amount or self.aide.economic.delegate_limit
        staking_block_identifier = staking_block_identifier or self.aide.staking.staking_info.StakingBlockNum

        return self.aide.web3.dpos.delegate.withdrew_delegate(node_id,
                                                              staking_block_identifier,
                                                              amount,
                                                              )

    @contract_transaction(1006)
    def redeem_delegate(self,
                        txn=None,
                        private_key=None,
                        ):
        """
        Claim unlocked commission money
        """
        return self.aide.web3.dpos.delegate.redeem_delegate()

    def get_delegate_info(self,
                          address=None,
                          node_id=None,
                          staking_block_identifier=None,
                          ):
        """ Obtain the delegation information for a certain pledge of an address to a node
        Note: Because the node may have pledged/revoked multiple times, it may leave the entrusted information behind. Therefore, when obtaining the entrusted information, it is necessary to specify the node's pledge block
        """
        if self.aide.account:
            address = address or self.aide.account.address
        node_id = node_id or self.aide.constant.node_id
        staking_block_identifier = staking_block_identifier or self.aide.staking.staking_info.StakingBlockNum

        delegate_info = self.aide.web3.dpos.delegate.get_delegate_info(address, node_id,
                                                                       staking_block_identifier).call()
        if delegate_info == 'Query delegate info failed:Delegate info is not found':
            return None
        else:
            return DelegateInfo(delegate_info)

    def get_delegate_lock_info(self,
                               address=None,
                               ):
        """ Obtain delegation information for addresses that are in the lock period
        """
        address = address or self.aide.account.address

        delegate_lock_info = self.aide.web3.dpos.delegate.get_delegate_lock_info(address).call()
        # todo: Complete according to actual situation
        if delegate_lock_info == 'Query delegate info failed:Delegate info is not found':
            return None
        else:
            return delegate_lock_info

    def get_delegate_list(self, address=None):
        """ Obtain all delegation information for the address
        """
        if self.aide.account:
            address = address or self.aide.account.address
        delegate_list = self.aide.web3.dpos.delegate.get_delegate_list(address).call()
        if delegate_list == 'Retreiving delegation related mapping failed:RelatedList info is not found':
            return []
        else:
            return [DelegateInfo(delegate_info) for delegate_info in delegate_list]


class DelegateInfo(AttributeDict):
    """ Attribute dictionary class for delegation information
    """
    Addr: str
    NodeId: str
    StakingBlockNum: int
    DelegateEpoch: int
    Released: int
    ReleasedHes: int
    RestrictingPlan: int
    RestrictingPlanHes: int
    CumulativeIncome: int
    LockReleasedHes: int
    LockRestrictingPlanHes: int

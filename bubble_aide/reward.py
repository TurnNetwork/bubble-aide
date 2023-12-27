from typing import TYPE_CHECKING
from bubble.datastructures import AttributeDict

from bubble_aide.abc.module import PrecompileContract
from bubble_aide.utils.wrapper import contract_transaction

if TYPE_CHECKING:
    from bubble_aide import Aide


class Reward(PrecompileContract):

    def __init__(self, aide: "Aide"):
        super().__init__(aide)
        self.address = self.aide.web3.dpos.reward.ADDRESS

    @property
    def staking_block_number(self):
        return self.aide.staking.staking_info.StakingBlockNum

    @contract_transaction(5000)
    def withdraw_delegate_reward(self,
                                 txn=None,
                                 private_key=None,
                                 ):
        """ Extracting delegated rewards will extract delegated rewards for all nodes that have been delegated
        """
        return self.aide.web3.dpos.reward.withdraw_delegate_reward()

    def get_delegate_reward(self,
                            address=None,
                            node_ids=None
                            ):
        """ Obtain commission reward information, which can be filtered based on node IDs
        """
        if self.aide.account:
            address = address or self.aide.account.address
        node_ids = node_ids or []
        return self.aide.web3.dpos.reward.get_delegate_reward(address, node_ids).call()


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

from typing import TYPE_CHECKING
from bubble.datastructures import AttributeDict

from bubble_aide.abc.module import PrecompileContract
from bubble_aide.utils.wrapper import contract_transaction

if TYPE_CHECKING:
    from bubble_aide import Aide


class StakingL2(PrecompileContract):

    def __init__(self, aide: "Aide"):
        super().__init__(aide)
        self.address = self.aide.web3.subChain.stakingL2.ADDRESS

    @contract_transaction()
    def create_staking(self,
                       node_id,
                       electron_uri,
                       p2p_uri,
                       node_version,
                       bls_pubkey,
                       name,
                       detail,
                       amount=200 * 10 ** 18,
                       is_operator=False,
                       rpc_uri=b'',
                       benefit_address=None,
                       private_key=None,
                       txn=None,
                       ):

        if not benefit_address:
            benefit_account = self.aide.bub.account.from_key(private_key)
            if not benefit_account:
                raise ValueError('the benefit address cannot be empty')
            benefit_address = benefit_account.address

        return self.aide.web3.subChain.stakingL2.create_staking(node_id, amount, benefit_address, name, detail,
                                                                electron_uri, p2p_uri,
                                                                node_version, bls_pubkey,
                                                                is_operator, rpc_uri)

    @contract_transaction()
    def edit_staking(self,
                     node_id,
                     benefit_address=None,
                     node_name=None,
                     detail=None,
                     rpc_uri=None,
                     private_key=None,
                     txn=None,
                     ):
        return self.aide.web3.subChain.stakingL2.edit_staking(node_id, benefit_address, node_name, detail, rpc_uri)

    @contract_transaction()
    def withdrew_staking(self,
                         node_id,
                         private_key=None,
                         txn=None,
                         ):
        return self.aide.web3.subChain.stakingL2.withdrew_staking(node_id)

    def get_candidate_list(self):
        candidate_list = self.aide.web3.subChain.stakingL2.get_candidate_list().call()
        if type(candidate_list) != list:
            return candidate_list
        else:
            return [StakingInfo(candidate) for candidate in candidate_list]

    def get_candidate_info(self, node_id):
        staking_info = self.aide.web3.subChain.stakingL2.get_candidate_info(node_id).call()
        if staking_info == 'Query candidate info failed:Candidate info is not found':
            return None
        else:
            return StakingInfo(staking_info)


class StakingInfo(AttributeDict):
    """ Attribute Dictionary Class for Pledge Information
    """
    NodeId: str
    BlsPubKey: str
    StakingAddress: str
    BenefitAddress: str
    StakingTxIndex: int
    ProgramVersion: int
    Status: int
    StakingEpoch: int
    StakingBlockNum: int
    Shares: int
    Released: int
    ReleasedHes: int
    Name: str
    Detail: str
    ElectronURI: str
    P2PURI: str

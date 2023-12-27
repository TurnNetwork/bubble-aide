from time import time
from typing import TYPE_CHECKING, Union, Literal

from bubble.datastructures import AttributeDict
from eth_typing import HexStr, NodeID, BlockIdentifier

from bubble_aide.abc.module import PrecompileContract
from bubble_aide.utils.wrapper import contract_transaction

if TYPE_CHECKING:
    from bubble_aide import Aide


def to_attribute_proposal(proposal):
    _type = proposal['ProposalType']
    wizard = {
        1: TextProposal,
        2: VersionProposal,
        3: ParamProposal,
        4: CancelProposal,
    }
    attribute_proposal = wizard[_type]
    return attribute_proposal(proposal)


class Govern(PrecompileContract):
    textGasPrice: int = 1500000000000000
    versionGasPrice: int = 2100000000000000
    paramGasPrice: int = 2000000000000000
    cancelGasPrice: int = 3000000000000000

    def __init__(self, aide: "Aide"):
        super().__init__(aide)
        self.address = self.aide.web3.proposal.ADDRESS

    def chain_version(self, version=None):
        """ Obtain version information on the chain or convert specified version information
        Supports the following forms：int: 66048, string: '1.2.0', list: [1, 2, 0]
        """
        version = version or self.aide.web3.proposal.get_chain_version()
        version_bytes = None

        if type(version) is int:
            version_bytes = int(version).to_bytes(length=3, byteorder='big')

        elif type(version) is list:
            version_bytes = bytes(version)

        elif type(version) is str:
            vs = str(version).split('.')
            version_bytes = bytes([int(v) for v in vs])

        else:
            ValueError('unrecognized version information')

        return ChainVersion({
            'integer': int.from_bytes(version_bytes, 'big'),
            'major': version_bytes[0],
            'minor': version_bytes[1],
            'patch': version_bytes[2],
        })

    @contract_transaction(default_txn={'gasPrice': versionGasPrice})
    def version_proposal(self,
                         version: int,
                         voting_rounds: int = 4,
                         pip_number: str = None,
                         node_id: Union[NodeID, HexStr] = None,
                         txn=None,
                         private_key=None,
                         ):
        """ Submit a version proposal to upgrade the on chain consensus hard fork version
        """
        pip_number = pip_number or str(time())
        node_id = node_id or self.aide.constant.node_id
        return self.aide.web3.proposal.submit_version_proposal(node_id, pip_number, version, voting_rounds)

    @contract_transaction(default_txn={'gasPrice': paramGasPrice})
    def param_proposal(self,
                       module: str,
                       name: str,
                       value: str,
                       pip_number: str = None,
                       node_id: Union[NodeID, HexStr] = None,
                       txn=None,
                       private_key=None,
                       ):
        """ Submit parameter proposals to modify on chain manageable parameters
        """
        pip_number = pip_number or str(time())
        node_id = node_id or self.aide.constant.node_id
        return self.aide.web3.proposal.submit_param_proposal(node_id, pip_number, module, name, value)

    @contract_transaction(default_txn={'gasPrice': cancelGasPrice})
    def cancel_proposal(self,
                        proposal_id: str,
                        voting_rounds: int = 4,
                        node_id: Union[NodeID, HexStr] = None,
                        pip_number: str = None,
                        txn=None,
                        private_key=None,
                        ):
        """ Submit cancellation proposal
        """
        pip_number = pip_number or str(time())
        node_id = node_id or self.aide.constant.node_id
        return self.aide.web3.proposal.submit_cancel_proposal(node_id, pip_number, voting_rounds, proposal_id)

    @contract_transaction(default_txn={'gasPrice': textGasPrice})
    def text_proposal(self,
                      pip_number: str = None,
                      node_id: Union[NodeID, HexStr] = None,
                      txn=None,
                      private_key=None,
                      ):
        """ Submit a text proposal that does not have any impact on the chain and only serves as a pip voting opinion collection function
        """
        pip_number = pip_number or str(time())
        node_id = node_id or self.aide.constant.node_id
        return self.aide.web3.proposal.submit_text_proposal(node_id, pip_number)

    @contract_transaction()
    def vote(self,
             proposal_id: Union[bytes, HexStr],
             option: int,
             node_id: Union[NodeID, HexStr] = None,
             version: int = None,
             version_sign: Union[bytes, HexStr] = None,
             txn=None,
             private_key=None,
             ):
        """ Vote on proposals
        """
        node_id = node_id or self.aide.constant.node_id
        version = version or self.aide.constant.node_version
        version_sign = version_sign or self.aide.constant.version_sign
        return self.aide.web3.proposal.vote(node_id, proposal_id, option, version, version_sign)

    @contract_transaction()
    def declare_version(self,
                        node_id: Union[NodeID, HexStr] = None,
                        version: int = None,
                        version_sign: Union[bytes, HexStr] = None,
                        txn=None,
                        private_key=None,
                        ):
        """ Declare node versions on the chain to obtain eligibility to participate in consensus block generation
        """
        node_id = node_id or self.aide.constant.node_id
        version = version or self.aide.constant.node_version
        version_sign = version_sign or self.aide.constant.version_sign
        return self.aide.web3.proposal.declare_version(node_id, version, version_sign)

    def get_proposal(self, proposal_id: Union[bytes, HexStr]):
        """ Obtain proposal information
        """
        proposal = self.aide.web3.proposal.get_proposal(proposal_id).call()
        return to_attribute_proposal(proposal)

    def get_newest_proposal(self, proposal_type: Literal[1, 2, 3, 4] = None):
        """ Obtain the latest activation status proposal information
        """
        block_number = self.aide.web3.bub.block_number
        proposal_list = self.proposal_list(proposal_type)

        proposals = [proposal for proposal in proposal_list if proposal.EndVotingBlock > block_number]

        if not proposals:
            return None

        return proposals[0]

    def get_proposal_result(self, proposal_id: Union[bytes, HexStr]):
        """ Obtain information on proposal voting results
        """
        proposal_result = self.aide.web3.proposal.get_proposal_result(proposal_id).call()
        if not proposal_result:
            raise ValueError('proposal is not found.')
        if type(proposal_result) is str:
            raise ValueError(f'{proposal_result}.')

        partici_count = proposal_result['yeas'] + proposal_result['nays'] + proposal_result['abstentions']
        proposal_result['particiRatio'] = partici_count / proposal_result['accuVerifiers']
        proposal_result['yeasRatio'] = proposal_result['yeas'] / partici_count if partici_count else 0

        return ProposalResult(proposal_result)

    def get_proposal_votes(self,
                           proposal_id: Union[bytes, HexStr],
                           block_identifier: BlockIdentifier == 'latest'
                           ):
        """ Obtain real-time voting information for proposals
        """
        proposal_votes = self.aide.web3.proposal.get_proposal_votes(proposal_id, block_identifier).call()
        if not proposal_votes:
            raise ValueError('proposal is not found.')

        partici_count = proposal_votes[1] + proposal_votes[2] + proposal_votes[3]

        return ProposalVotes({
            'accuVerifiers': proposal_votes[0],
            'yeas': proposal_votes[1],
            'nays': proposal_votes[2],
            'abstentions': proposal_votes[3],
            'particiRatio': partici_count / proposal_votes[0],
            'yeasRatio': proposal_votes[1] / partici_count if partici_count else 0,
        })

    def proposal_list(self, proposal_type: Literal[1, 2, 3, 4] = None):
        """ Obtain a list of proposals, which can be filtered based on the type of proposal
        """
        proposal_list = self.aide.web3.proposal.proposal_list().call()

        if proposal_list == 'Object not found':
            proposal_list = []

        proposals = [to_attribute_proposal(proposal) for proposal in proposal_list]

        if proposal_type:
            return [proposal for proposal in proposals if proposal.ProposalType == proposal_type]

        return proposals

    def get_govern_param(self, module, name):
        """ Obtain the value of governable parameters
        """
        return self.aide.web3.proposal.get_govern_param(module, name).call()


class ChainVersion(AttributeDict):
    integer: int
    major: int
    minor: int
    patch: int


class BaseProposal(AttributeDict):
    ProposalID: str
    Proposer: str
    ProposalType: int
    PIPID: str
    SubmitBlock: int
    EndVotingBlock: int


class VersionProposal(BaseProposal):
    EndVotingRounds: int
    ActiveBlock: int
    NewVersion: int


class ParamProposal(BaseProposal):
    Module: str
    Name: str
    NewVersion: str


class CancelProposal(BaseProposal):
    EndVotingRounds: str
    EndVotingBlock: str
    TobeCanceled: str


class TextProposal(BaseProposal):
    pass


class ProposalVotes(AttributeDict):
    accuVerifiers: int
    yeas: int
    nays: int
    abstentions: int
    particiRatio: float
    yeasRatio: float


class ProposalResult(ProposalVotes):
    proposalID: str
    status: int
    canceledBy: str

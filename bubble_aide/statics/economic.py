import json
import math
from typing import Union
from dataclasses import dataclass

from dacite import from_dict


@dataclass
class CommonData:
    maxEpochMinutes: int
    nodeBlockTimeWindow: int
    perRoundBlocks: int
    maxConsensusVals: int
    additionalCycleTime: int


@dataclass
class StakingData:
    stakeThreshold: int
    operatingThreshold: int
    maxValidators: int
    unStakeFreezeDuration: int
    rewardPerMaxChangeRange: int
    rewardPerChangeInterval: int


@dataclass
class SlashingData:
    slashFractionDuplicateSign: int
    duplicateSignReportReward: int
    maxEvidenceAge: int
    slashBlocksReward: int
    zeroProduceCumulativeTime: int
    zeroProduceNumberThreshold: int
    zeroProduceFreezeDuration: int


@dataclass
class GovernData:
    versionProposalVoteDurationSeconds: int
    versionProposalSupportRate: int
    textProposalVoteDurationSeconds: int
    textProposalVoteRate: int
    textProposalSupportRate: int
    cancelProposalVoteRate: int
    cancelProposalSupportRate: int
    paramProposalVoteDurationSeconds: int
    paramProposalVoteRate: int
    paramProposalSupportRate: int


@dataclass
class RewardData:
    newBlockRate: int
    bubbleFoundationYear: int
    increaseIssuanceRatio: int
    theNumberOfDelegationsReward: int


@dataclass
class RestrictingData:
    minimumRelease: int


@dataclass
class Economic:
    common: CommonData
    restricting: RestrictingData
    staking: StakingData
    gov: GovernData
    reward: RewardData
    slashing: SlashingData

    # 区块
    @property
    def block_time(self):
        """ Block duration/s
        """
        # todo: Obtain block average time
        return int(self.common.nodeBlockTimeWindow // self.common.perRoundBlocks)

    # 窗口期
    @property
    def round_time(self):
        """ Window duration/m
        """
        return self.round_blocks * self.block_time

    @property
    def round_blocks(self):
        """ Number of blocks during the window period
        """
        return self.common.perRoundBlocks

    # 共识轮
    @property
    def consensus_time(self):
        """ Consensus round duration/m
        """
        return self.consensus_rounds * self.round_time

    @property
    def consensus_blocks(self):
        """ Number of consensus round blocks
        """
        return self.consensus_rounds * self.round_blocks

    @property
    def consensus_rounds(self):
        """ Number of consensus round window periods
        """
        return self.verifier_count

    # 结算周期
    @property
    def epoch_time(self):
        """ Settlement cycle duration/m
        """
        return self.epoch_consensus * self.consensus_time

    @property
    def epoch_blocks(self):
        """ Number of settlement cycle blocks
        """
        return self.epoch_consensus * self.consensus_blocks

    @property
    def epoch_rounds(self):
        """ Number of settlement period window periods
        """
        return self.epoch_consensus * self.consensus_rounds

    @property
    def epoch_consensus(self):
        """ Number of consensus rounds in settlement cycle
        """
        return (self.common.maxEpochMinutes * 60) // self.consensus_time

    @property
    def increasing_time(self):
        """ Duration of issuance cycle/m
        """
        return self.increasing_epoch * self.epoch_time

    @property
    def increasing_blocks(self):
        """ Number of blocks in the issuance cycle
        """
        return self.increasing_rounds * self.round_blocks

    @property
    def increasing_rounds(self):
        """ Number of window periods for issuance cycles
        """
        return self.increasing_consensus * self.consensus_rounds

    @property
    def increasing_consensus(self):
        """ Number of consensus rounds for the issuance cycle
        """
        return self.increasing_epoch * self.epoch_consensus

    @property
    def increasing_epoch(self):
        """ Number of additional issuance cycles and settlement cycles
        """
        # todo: Change to real-time calculation
        return math.ceil((self.common.additionalCycleTime * 60) / self.epoch_time)

    @property
    def verifier_count(self):
        """ Maximum number of consensus validators
        """
        return self.common.maxConsensusVals

    @property
    def validator_count(self):
        """ Maximum number of validators
        """
        return self.staking.maxValidators

    @property
    def staking_limit(self):
        """ Pledge minimum amount limit
        """
        return self.staking.stakeThreshold

    @property
    def add_staking_limit(self):
        """ Minimum amount limit for increased pledge
        """
        return self.staking.operatingThreshold

    @property
    def delegate_limit(self):
        """ Commission minimum amount limit
        """
        return self.staking.operatingThreshold

    @property
    def unstaking_freeze_epochs(self):
        """ The number of settlement cycles in which the pledged amount is frozen after the release of the pledge
        """
        return self.staking.unStakeFreezeDuration

    @property
    def not_block_slash_rate(self):
        """ When node zero out block penalty is applied, the corresponding block reward multiple of the penalty
        """
        return self.slashing.slashBlocksReward

    @property
    def param_proposal_epochs(self):
        """ Number of settlement cycles for parameter proposal voting period
        """
        return self.gov.paramProposalVoteDurationSeconds // self.epoch_time

    @property
    def text_proposal_epochs(self):
        """ The number of settlement cycles during the voting period of text proposals
        """
        return self.gov.textProposalVoteDurationSeconds // self.epoch_time


def new_economic(data: Union[dict, str]):
    """ Convert data to economic objects
    """
    if type(data) is str:
        data = json.loads(data)

    return from_dict(Economic, data)

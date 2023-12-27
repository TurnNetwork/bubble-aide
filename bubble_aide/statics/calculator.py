import math
import warnings

from decimal import Decimal
from typing import Literal, TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from bubble_aide import Aide


class Calculator:

    def __init__(self, aide: "Aide"):
        self.aide = aide

    def get_verifier_count(self):
        """ Obtain the number of validators for the settlement cycle
        remark：At present, only the number of validators for the current settlement cycle can be obtained on the chain
        """
        verifier_list = self.aide.web3.dpos.staking.get_verifier_list().call()
        return len(verifier_list)

    def get_block_count(self, node_id, start_bn=None, end_bn=None):
        """ Get the number of nodes out of blocks
        """
        start_bn = start_bn or 0
        end_bn = end_bn or self.aide.bub.block_number
        if end_bn - start_bn > 1000:
            warnings.warn('too many blocks to analyze, it will be a long wait')

        block_count = 0
        for bn in range(start_bn, end_bn + 1):
            public_key = self.aide.ec_recover(bn)
            if node_id in public_key:
                block_count = block_count + 1

            if bn % 100 == 0:
                logger.info(f'analyzed to {bn}th block, count: {block_count}, waiting...')

        return block_count

    def get_period_info(self,
                        block_number=None,
                        period_type: Literal['round', 'consensus', 'epoch', 'increasing'] = 'epoch'
                        ):
        """ Obtain the number of cycles in which the block is located and the height of the block at the end of the cycle by using the block height and cycle type
        """
        if period_type not in ['round', 'consensus', 'epoch', 'increasing']:
            raise ValueError('unknown period type.')

        blocks = {
            'round': self.aide.economic.round_blocks,
            'consensus': self.aide.economic.consensus_blocks,
            'epoch': self.aide.economic.epoch_blocks,
            'increasing': self.aide.economic.increasing_blocks,
        }
        period_blocks = blocks[period_type]

        if not block_number:
            block_number = self.aide.bub.block_number

        period = math.ceil(block_number / period_blocks) or 1
        start_block, end_block = self.get_period_ends(period, period_type)

        return period, start_block, end_block

    def get_period_ends(self,
                        period,
                        period_type: Literal['round', 'consensus', 'epoch', 'increasing'] = 'epoch'
                        ):
        """ Obtain the starting and ending block height of the cycle by the number and type of cycles
        """
        if period_type not in ['round', 'consensus', 'epoch', 'increasing']:
            raise ValueError('unknown period type.')

        blocks = {
            'round': self.aide.economic.round_blocks,
            'consensus': self.aide.economic.consensus_blocks,
            'epoch': self.aide.economic.epoch_blocks,
            'increasing': self.aide.economic.increasing_blocks,
        }
        period_blocks = blocks[period_type]
        start_block, end_block = (period - 1) * period_blocks + 1, period * period_blocks

        return start_block, end_block

    def get_reward_info(self):
        """ Obtain reward information for the current settlement period
        """
        # todo: Delete this method
        total_staking_reward = self.aide.web3.dpos.staking.get_staking_reward().call()
        per_block_reward = self.aide.web3.dpos.staking.get_block_reward().call()
        return total_staking_reward, per_block_reward

    # def get_node_reward(self, node_id):
    #     """ Instantly calculate the total reward for the node in the previous settlement cycle
    #     """
    #     total_staking_reward = self.web3.dpos.staking.get_staking_reward()
    #     verifier_count = self.get_verifier_count()
    #     per_block_reward = self.web3.dpos.staking.get_block_reward()
    #     # Obtain the number of blocks produced by nodes in the previous settlement cycle
    #     epoch, _, _ = self.get_period_info(self.web3.bub.block_number, 'epoch')
    #     start_bn, end_bn = self.get_period_ends(epoch - 1)
    #     block_count = self.get_block_count(node_id, start_bn, end_bn)
    #     self.calc_node_reward(total_staking_reward,
    #                           verifier_count,
    #                           per_block_reward,
    #                           block_count
    #                           )

    @staticmethod
    def calc_node_reward(total_staking_reward,
                         verifier_count,
                         per_block_reward,
                         block_count,
                         ):
        """ Calculate the total reward for a settlement cycle for a node (excluding trading gas rewards)

        Args:
            total_staking_reward: The total pledge reward for the settlement period can be obtained through self.get_reward_info
            verifier_count: Number of validators for settlement cycle，can be obtained through self.get_verifier_count
            per_block_reward: Reward for block out during settlement period，can be obtained through self.get_reward_info
            block_count: The number of blocks produced by a node in the settlement cycle，can be obtained through self.get_block_count
        """
        staking_reward = int(Decimal(total_staking_reward) / Decimal(verifier_count))
        block_reward = int(Decimal(per_block_reward) * Decimal(block_count))
        node_reward = staking_reward + block_reward
        return node_reward

    # def get_staking_reward(self, node_id):
    #     """ Instantly calculate the pledge reward for nodes in the previous settlement cycle
    #     """
    #     total_staking_reward = self.aide.web3.dpos.staking.get_staking_reward()
    #     verifier_count = self.get_verifier_count()
    #     per_block_reward = self.aide.web3.dpos.staking.get_block_reward()
    #     # Obtain the number of blocks produced by nodes in the previous settlement cycle
    #     epoch, _, _ = self.get_period_info(self.web3.bub.block_number, 'epoch')
    #     start_bn, end_bn = self.get_period_ends(epoch - 1)
    #     block_count = self.get_block_count(node_id, start_bn, end_bn)
    #
    #     node_reward_ratio = self._staking.get_candidate_info(node_id).RewardPer
    #
    #     return self.calc_staking_reward(total_staking_reward,
    #                                     verifier_count,
    #                                     per_block_reward,
    #                                     block_count,
    #                                     node_reward_ratio,
    #                                     )

    @staticmethod
    def calc_staking_reward(total_staking_reward,
                            verifier_count,
                            per_block_reward,
                            block_count,
                            node_reward_ratio,
                            ):
        """
        Calculate a settlement cycle and the pledge reward for nodes

        Args:
            total_staking_reward: The total pledge reward for the settlement period can be obtained through self.get_reward_info
            verifier_count: Number of validators for settlement cycle，can be obtained through self.get_verifier_count
            per_block_reward: Reward for block out during settlement period，can be obtained through self.get_reward_info
            block_count: The number of blocks produced by a node in the settlement cycle，can be obtained through self.get_block_count
            node_reward_ratio: The commission dividend ratio of nodes in the settlement period
        """
        node_reward = Calculator.calc_node_reward(total_staking_reward,
                                                  verifier_count,
                                                  per_block_reward,
                                                  block_count,
                                                  )

        delegate_reward = Calculator.calc_delegate_reward(total_staking_reward,
                                                          verifier_count,
                                                          per_block_reward,
                                                          block_count,
                                                          node_reward_ratio,
                                                          )

        staking_reward = node_reward - delegate_reward
        return staking_reward

    # def get_delegate_reward(self,
    #                         node_id,
    #                         delegate_amount,
    #                         delegate_total_amount,
    #                         ):
    #     """
    #     Instantly calculate the commission reward for the account at the node in the previous settlement cycle
    #
    #     Args:
    #         node_id: Delegate Node ID
    #         delegate_amount: During the settlement period, the total amount of account delegation during the locking period of the node
    #         delegate_total_amount: The total amount of delegation for the locking period of the node in this settlement cycle
    #     """
    #     total_staking_reward = self.web3.dpos.staking.get_staking_reward()
    #     verifier_count = self.get_verifier_count()
    #     per_block_reward = self.web3.dpos.staking.get_block_reward()
    #     # Obtain the number of blocks generated by the delegated node in the previous settlement cycle
    #     epoch, _, _ = self.get_period_info(self.web3.bub.block_number, 'epoch')
    #     start_bn, end_bn = self.get_period_ends(epoch - 1)
    #     block_count = self.get_block_count(node_id, start_bn, end_bn)
    #
    #     node_reward_ratio = self._staking.get_candidate_info(node_id).RewardPer
    #
    #     return self.calc_delegate_reward(total_staking_reward,
    #                                      verifier_count,
    #                                      per_block_reward,
    #                                      block_count,
    #                                      node_reward_ratio,
    #                                      delegate_total_amount,
    #                                      delegate_amount,
    #                                      )

    @staticmethod
    def calc_delegate_reward(total_staking_reward,
                             verifier_count,
                             per_block_reward,
                             block_count,
                             node_reward_ratio,
                             delegate_total_amount=None,
                             delegate_amount=None,
                             ):
        """
        Calculate the commission rewards for accounts at nodes within a settlement cycle

        Args:
            total_staking_reward: The total pledge reward for the settlement period can be obtained through self.get_reward_info
            verifier_count: Number of validators for settlement cycle，can be obtained through self.get_verifier_count
            per_block_reward: Reward for block out during settlement period，can be obtained through self.get_reward_info
            block_count: The number of blocks produced by a node in the settlement cycle，can be obtained through self.get_block_count
            node_reward_ratio: The commission dividend ratio of nodes in the settlement period
            delegate_total_amount: The total amount of delegation for nodes during the lock up period of the settlement cycle
            delegate_amount: During the settlement period, the total amount of lock up period delegation from the account to the node
        """
        dividend_ratio = Decimal(node_reward_ratio) / Decimal(10000)
        # Calculate collateral reward dividends based on underlying algorithms
        staking_reward = int(Decimal(total_staking_reward) / Decimal(verifier_count))
        staking_dividends = int(Decimal(staking_reward) * dividend_ratio)
        # Calculate block reward dividends according to the underlying algorithm
        per_block_delegate_reward = Decimal(per_block_reward) * dividend_ratio
        block_dividends = per_block_delegate_reward * Decimal(block_count)
        # Calculate all delegated dividends for nodes
        all_delegate_reward = int(staking_dividends + block_dividends)
        if not delegate_total_amount and not delegate_amount:
            return all_delegate_reward
        # Calculate entrusted dividends for the account
        delegate_reward = math.floor(
            Decimal(all_delegate_reward) * Decimal(delegate_amount) / Decimal(delegate_total_amount))
        return delegate_reward

    def calc_report_multi_sign_reward(self, staking_amount):
        """ Calculate rewards for reporting double signatures
        """
        slashing_ratio = self.aide.economic.slashing.slashFractionDuplicateSign
        slashing_amount = Decimal(staking_amount) * (Decimal(slashing_ratio) / 10000)

        reward_ratio = self.aide.economic.slashing.duplicateSignReportReward
        report_reward = slashing_amount * (Decimal(reward_ratio) / 100)

        to_incentive_pool_amount = slashing_amount - report_reward
        return int(report_reward), int(to_incentive_pool_amount)

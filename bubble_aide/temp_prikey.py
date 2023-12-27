from typing import TYPE_CHECKING

from bubble.types import InnerFunction

from bubble_aide.abc.module import PrecompileContract
from bubble_aide.utils.wrapper import contract_transaction

if TYPE_CHECKING:
    from bubble_aide import Aide


class TempPrikey(PrecompileContract):

    def __init__(self, aide: "Aide"):
        super().__init__(aide)
        self.address = self.aide.web3.subChain.temp_private_key.ADDRESS

    @contract_transaction()
    def bind_temp_prikey(self,
                         game_contract_address,
                         temp_address,
                         period,
                         private_key=None,
                         txn=None,
                         ):
        return self.aide.web3.subChain.temp_private_key.bind_temp_pri_key(game_contract_address,
                                                                          temp_address,
                                                                          period)

    @contract_transaction()
    def behalf_signature(self,
                         work_address,
                         game_contract_address,
                         period,
                         call_data,
                         private_key=None,
                         txn=None,
                         ):
        return self.aide.web3.subChain.temp_private_key.behalf_signature(work_address,
                                                                         game_contract_address,
                                                                         period,
                                                                         call_data
                                                                         )

    @contract_transaction()
    def invalidate_temp_prikey(self,
                               game_contract_address,
                               temp_address,
                               private_key=None,
                               txn=None,
                               ):
        return self.aide.web3.subChain.temp_private_key.invalidate_temp_private_key(
            game_contract_address,
            temp_address)

    @contract_transaction()
    def add_line_of_credit(self,
                           game_contract_address,
                           work_address,
                           add_value,
                           private_key=None,
                           txn=None,
                           ):
        return self.aide.web3.subChain.temp_private_key.add_line_of_credit(game_contract_address,
                                                                           work_address,
                                                                           add_value)

    def get_line_of_credit(self,
                           game_contract_address,
                           work_address,
                           ):
        return self.aide.web3.subChain.temp_private_key.get_line_of_credit(game_contract_address).call(
            transaction={'from': work_address})

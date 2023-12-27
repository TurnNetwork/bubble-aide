from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bubble_aide import Aide


class Constant:

    def __init__(self, aide: "Aide"):
        self.aide = aide

    @property
    def node_id(self):
        node_info = self.aide.admin.node_info()
        node_id = node_info['enode'].split('//')[1].split('@')[0]  # 请使用enode中的节点id
        return node_id

    @property
    def node_version(self):
        version_info = self.aide.admin.get_program_version()
        return version_info['Version']

    @property
    def bls_pubkey(self):
        node_info = self.aide.admin.node_info()
        return node_info['blsPubKey']

    @property
    def bls_proof(self):
        return self.aide.admin.get_schnorr_NIZK_prove()

    @property
    def version_sign(self):
        version_info = self.aide.admin.get_program_version()
        return version_info['Sign']

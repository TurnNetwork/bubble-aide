from gql import gql

from bubble_aide.utils.utils import get_gql


class Graphql:

    def __init__(self, uri: str):
        self.client = get_gql(uri)

    def execute(self, content):
        """ Execute GQL statement and obtain the return result
        """
        return self.client.execute(gql(content))

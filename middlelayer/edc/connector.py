import requests

from .transfer_process import TransferProcessDto
from .contract_agreement import ContractAgreementDto
from ..logging import logger


class EdcClient():

    def __init__(self) -> None:
        self.connector_host = "http://192.168.205.10"
        self.connector_management_api = f"{self.connector_host}:8182/api/v1/management"
        self.headers = {
            'x-api-key': 'password'
        }

    def get_transfer_process(self, transfer_process_id: str):
        """
        requests the transfer process of a given id
        """
        url = f"{self.connector_management_api}/transferprocess/{transfer_process_id}"

        response = requests.request(
            "GET",
            url,
            headers=self.headers,
            timeout=30)

        logger.debug("url: %s\tdata: %s", url, response.content)

        return TransferProcessDto.parse_obj(response.json())

    def get_contract_agreement(self, contract_id):
        """
        requests the contract agreement of a given id
        """
        url = f"{self.connector_management_api}/contractagreements/{contract_id}"

        response = requests.request("GET",
                                    url,
                                    headers=self.headers,
                                    timeout=30)

        logger.debug("url: %s\tdata: %s", url, response.content)

        return ContractAgreementDto.parse_obj(response.json())

import aiohttp
import asyncio
import time

link_to_confirm_payment = "https://sandbox-apis.bankofcyprus.com/df-boc-org-sb/sb/psd2/oauth2/authorize?response_type=code&redirect_uri=https://t.me/moctezumaEUbot&scope=UserOAuth2Security&client_id={}&paymentid={}"
link_to_subscribe = "https://sandbox-apis.bankofcyprus.com/df-boc-org-sb/sb/psd2/oauth2/authorize?response_type=code&redirect_uri=https://t.me/moctezumaEUbot&scope=UserOAuth2Security&client_id={}&subscriptionid={}"
base_url = 'https://sandbox-apis.bankofcyprus.com/df-boc-org-sb/sb/psd2'

client_id = '155228ba393f3e32c9a688c0b88a38b0'
client_secret = '83ad323f2161baca67fe792f2e92c456'

class PaymentClient:
    def __init__(
            self,
            client_id: str = client_id,
            client_secret: str = client_secret,
            base_url: str = base_url,
            grant_type: str = "client_credentials",
            scope: str = 'TPPOAuth2Security'
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type
        self.scope = scope

    async def get_api_key(self):
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': self.grant_type,
            'scope': self.scope
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.base_url}/oauth2/token', data=payload, headers=await self._get_headers('getAuthorization')) as resp:

                if resp.status == 200:
                    return (await resp.json()).get('access_token')
                else:
                    print(f"Error: {resp.status}, Response: {await resp.json()}", flush=True)

    async def get_balance(self):
        """Получение баланса аккаунта"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.base_url}/balance', headers=await self._get_headers()) as response:
                return await response.json()

    async def create_payment(self, amount: float, debtor_id: str, creditor_id: str):
        """
        Full Proccess to Create Payment

        returns link for Submit Payment
        """

        payload = await self.create_sign(amount, debtor_id, creditor_id)
        pmtId = await self.initiate_payment(payload)
        return link_to_confirm_payment.format(self.client_id, pmtId)

    async def create_sign(self, amount: float, debtor_id: str, creditor_id: str):
        """Creating payment by debtor and creditor ID's"""

        data = {
            "debtor": {
                 "bankId": "",
                 "accountId": debtor_id
            },
            "creditor": {
                "bankId": "BCYPCY2N",
                "accountId": creditor_id
            },
            "transactionAmount": {
                "amount": amount,
                "currency": "EUR"
            },
            "paymentDetails": "SWIFT Transfer"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                        'https://sandbox-apis.bankofcyprus.com/df-boc-org-sb/sb/jwssignverifyapi/sign',
                        json=data,
                        headers=await self._get_headers("createSignPayment")
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"Error: {resp.status}, Response: {await resp.json()}", flush=True)

    async def initiate_payment(self, payload: dict):
        """Final step to create payment"""
        headers = await self._get_headers('initiatePayment')
        headers['Authorization'] = headers.get('Authorization').format(await self.get_api_key())

        async with aiohttp.ClientSession() as session:
            async with session.post(
                      f'{self.base_url}/v1/payments/initiate',
                    json=payload,
                    headers=headers
            ) as resp:
                if resp.status == 201:
                    return (await resp.json()).get('payment').get('paymentId')
                else:
                    print(f"Error: {resp.status}, Response: {await resp.json()}", flush=True)

    async def execute_payment(self):
        return True

    async def get_status(self, id: int):
        return {
            'amount': 500.0,
            'status': 'succces'
        }

    async def _get_headers(self, request: str = None):

        if request == 'getAuthorization':
            return {"Content-Type": "application/x-www-form-urlencoded"}

        elif request == 'createSignPayment':
            return {
                "Content-Type": "application/json",
                "tppId": "singpaymentdata",
            }
        elif request == 'initiatePayment':
            return {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}",
                "timestamp": str(time.time()),
                "customerIP": "10.0.0.1",
                "customerSessionId": "1232545908",
                "loginTimeStamp": str(time.time()),
                "customerDevice": "Telegram",
                "journeyId": "1234"
            }
        return {
            "Content-Type": "application/json"
        }



class SubsClient:
    def __init__(
            self,
            client_id: str = client_id,
            client_secret: str = client_secret,
            base_url: str = base_url,
            grant_type: str = "client_credentials",
            scope: str = 'TPPOAuth2Security'
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type
        self.scope = scope

    async def get_api_key(self):

        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': self.grant_type,
            'scope': self.scope
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.base_url}/oauth2/token', data=payload,
                                    headers=await self._get_headers('getAuthorization')) as resp:
                if resp.status == 200:
                    return (await resp.json()).get('access_token')
                else:
                    print(f"Error: {resp.status}, Response: {await resp.json()}", flush=True)

    async def create_subscription(self):
        data = {
            "accounts": {
                "transactionHistory": True,
                "balance": True,
                "details": True,
                "checkFundsAvailability": True
            },
            "payments": {
                "limit": 99999999,
                "currency": "EUR",
                "amount": 999999999
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.base_url}/v1/subscriptions', json=data, headers=await self._get_headers('getSubscription')) as resp:
                if resp.status == 201:
                    return link_to_subscribe.format(self.client_id, (await resp.json()).get("subscriptionId"))
                else:
                    print(f"Error: {resp.status}, Response: {await resp.json()}", flush=True)

    async def _get_headers(self, request: str = None):

        if request == 'getAuthorization':
            return {"Content-Type": "application/x-www-form-urlencoded"}

        elif request == 'getSubscription':
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await self.get_api_key()}",
                "timeStamp": str(time.time()),
                "journeyId": "1234"
            }
        elif request == 'createSignPayment':
            return {
                "Content-Type": "application/json",
                "tppId": "singpaymentdata",
            }
        elif request == 'initiatePayment':
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await self.get_api_key()}",
                "timestamp": str(time.time()),
                "customerIP": "10.0.0.1",
                "customerSessionId": "1232545908",
                "loginTimeStamp": str(time.time()),
                "customerDevice": "Telegram",
                "journeyId": "1234"
            }
        return {
            "Content-Type": "application/json"
        }




async def main():
    print(await PaymentClient(
        base_url = 'https://sandbox-apis.bankofcyprus.com/df-boc-org-sb/sb/psd2',
        client_id = '155228ba393f3e32c9a688c0b88a38b0',
        client_secret = '83ad323f2161baca67fe792f2e92c456'
        ).create_payment(30, "351092345676", "351092345675")
    )
    print(await SubsClient(
        base_url = 'https://sandbox-apis.bankofcyprus.com/df-boc-org-sb/sb/psd2',
        client_id = '155228ba393f3e32c9a688c0b88a38b0',
        client_secret = '83ad323f2161baca67fe792f2e92c456'
            ).create_subscription()
        )


#if __name__ == '__main__':
#asyncio.run(main())
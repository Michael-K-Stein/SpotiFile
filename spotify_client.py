from config import *
from exceptions import SpotifyClientException


class SpotifyClient:
    _proxy = PROXY
    _client_token = ''
    _access_token = ''
    _client_id = ''
    __USER_AGENT = USER_AGENT
    _verify_ssl = VERIFY_SSL

    user_data = None

    def __init__(self, sp_dc=None, sp_key=None):
        self.dc = sp_dc
        self.key = sp_key
        self.__HEADERS = {
                'User-Agent': self.__USER_AGENT,
                'Accept': 'application/json',
                'Origin': 'https://open.spotify.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Referer': 'https://open.spotify.com/',
                'Te': 'trailers',
                'App-Platform': 'WebPlayer'
            }
        self.get_tokens(sp_dc, sp_key)

    def get_tokens(self, sp_dc=None, sp_key=None):
        self._access_token, self._client_id = self.get_access_token(sp_dc=sp_dc, sp_key=sp_key)
        self._client_token = self.get_client_token(self._client_id)

        print('Client token: ', self._client_token)
        print('Access token: ', self._access_token)

    def refresh_tokens(self):
        self.get_tokens(self.dc, self.key)

    def get_client_token(self, client_id: str):
        with requests.session() as session:
            session.proxies = self._proxy
            session.headers = self.__HEADERS

            # Clear old tokens, otherwise we will get 400 Bad Request
            if 'client_token' in session.headers:
                session.headers.pop('client_token')
            if 'Authorization' in session.headers:
                session.headers.pop('Authorization')
            
            data = {
                "client_data": {
                    "client_version": "1.2.13.477.ga4363038",
                    "client_id": client_id,
                    "js_sdk_data": 
                    {
                        "device_brand": "",
                        "device_id": "",
                        "device_model": "",
                        "device_type": "",
                        "os": "",
                        "os_version": ""
                    }
                } 
            }

            response = session.post('https://clienttoken.spotify.com/v1/clienttoken', json=data, verify=self._verify_ssl)
            try:
                rj = response.json()
            except Exception as ex:
                print('Failed to parse client token response as json!', ex)
                exit(0)
            return rj['granted_token']['token']

    def get_access_token(self, keys=None, sp_dc=None, sp_key=None):
        with requests.session() as session:
            session.proxies = self._proxy
            session.headers = self.__HEADERS
            cookie = {}
            if keys is not None:
                cookie = keys
            if sp_dc is not None:
                cookie['sp_dc'] = sp_dc
            if sp_key is not None:
                cookie['sp_key'] = sp_key
            response = session.get('https://open.spotify.com/get_access_token', verify=self._verify_ssl, cookies=cookie)
            try:
                rj = response.json()
            except Exception as ex:
                print('An error occured when generating an access token!', ex)
                exit(0)
            print('Access token is anon: ', rj['isAnonymous'])
            self.is_anonymous = rj['isAnonymous']
            return rj['accessToken'], rj['clientId'] if rj['clientId'].lower() != 'unknown' else self._client_id

    def get_me(self):
        with requests.session() as session:
            session.proxies = self._proxy
            session.headers = self.__HEADERS
            session.headers.update({
                                    'Client-Token': self._client_token,
                                    'Authorization': f'Bearer {self._access_token}'
                                    })

            response_json = session.get('https://api.spotify.com/v1/me', verify=self._verify_ssl).json()
        self.user_data = response_json
        if not 'product' in self.user_data:
            raise SpotifyClientException('Spotify client keys are invalid.\nVerify that you have entered valid SP_KEY & SP_DC values.')
        if self.user_data['product'] == 'premium':
            raise SpotifyClientException('THIS USER IS PREMIUM!')
        return response_json

    def get_premium_keys(self):
        page = requests.get('https://www.rkstore.tn/2022/03/spotify-premium-cookies.html', verify=self._verify_ssl)
        root = html.document_fromstring(page.content)
        cookies_element = root.get_element_by_id('download_link')
        cookies = json.loads(cookies_element.text_content())
        prem_keys = {}
        for cookie in cookies:
            prem_keys[cookie['name']] = cookie['value']
        return prem_keys

    def get(self, url: str) -> Response:
        with requests.session() as session:
            session.proxies = self._proxy
            session.headers = self.__HEADERS
            session.headers.update({
                                    'Client-Token': self._client_token,
                                    'Authorization': f'Bearer {self._access_token}'
                                    })

            response = session.get(url, verify=self._verify_ssl)
            return response

    def post(self, url: str, payload=None) -> Response:
        with requests.session() as session:
            session.proxies = self._proxy
            session.headers = self.__HEADERS
            session.headers.update({
                                    'Client-Token': self._client_token,
                                    'Authorization': f'Bearer {self._access_token}'
                                    })

            response = session.post(url, verify=self._verify_ssl, data=payload)
            return response


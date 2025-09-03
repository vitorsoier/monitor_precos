import os
from datetime import datetime
from urllib import response
import requests
from dotenv import dotenv_values

class MercadoLivreAPI:

    def __init__(self, env_path = '.env'):
        self.base_url = "https://api.mercadolibre.com"
        self.env_path = env_path

    def get_envs(self):
        return dotenv_values(self.env_path)

    @staticmethod
    def _transform_in_dict(lines):
        return dict(line.strip().split('=', 1) for line in lines)

    @staticmethod
    def _dict_to_env(env_dict):
        env = ''
        for i in env_dict:
            env += f'{i}={env_dict[i]}\n'
        return env

    def read_env(self):
        if not os.path.exists(self.env_path):
            print("Você não possuí um arquivo .env\n Crie com:\n - Client_id\n - Cliente Secret\n - Redirect URI\n - TG token")
            exit()
        with open(self.env_path, 'r') as file:
            lines = file.readlines()
        return lines

    def write_env(self, env_dict):
        if not os.path.exists(self.env_path):
            print("Você não possuí um arquivo .env\n Crie com:\n - Client_id\n - Cliente Secret\n - Redirect URI\n - TG token")
            exit()
        env = self._dict_to_env(env_dict)
        with open(self.env_path, 'w') as file:
            file.write(env)

    def upsert_env(self, att_dict):
        lines = self.read_env()
        env_dict = self._transform_in_dict(lines)
        for i in att_dict:
            env_dict[i] = att_dict[i]
        self.write_env(env_dict)
        print(f'Arquivo {self.env_path} atualizado com novos codigos')
    
    def get_access_token(self):
        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded'
        }
        envs = self.get_envs()
        autentication_url = f'{self.base_url}/oauth/token'
        if envs.get('TOKEN') is None:
            payload = f'grant_type=authorization_code&client_id={envs.get('API_KEY')}&client_secret={envs.get('API_SECRET')}&code={envs.get('CODE')}&redirect_uri={envs.get('REDIRECT_URI')}'
        else:
            payload = payload = f'grant_type=refresh_token&client_id={envs.get('API_KEY')}&client_secret={envs.get('API_SECRET')}&refresh_token={envs.get('CODE')}&redirect_uri={envs.get('REDIRECT_URI')}'
        try:
            print(payload)
            response = requests.post(autentication_url, headers=headers, data=payload)
            print(response.json())
            response.raise_for_status()
            self.upsert_env({
                'NEXT_CODE' : response.json()['refresh_token'],
                'TOKEN': response.json()['access_token'] 
            })
        except: 
            payload = payload = f'grant_type=refresh_token&client_id={envs.get('API_KEY')}&client_secret={envs.get('API_SECRET')}&refresh_token={envs.get('NEXT_CODE')}&redirect_uri={envs.get('REDIRECT_URI')}'
            response = requests.post(autentication_url, headers=headers, data=payload)
            print(f'TESTE ------------------------------------------------ \n{response.json()}\n -----------------------------------------------------------------')
            response.raise_for_status()
            self.upsert_env({
                'CODE' : envs.get('NEXT_CODE'),
                'NEXT_CODE' : response.json()['refresh_token'],
                'TOKEN': response.json()['access_token']
            })

    def criar_usuario_test(self, site_id="MLB"):
        envs = self.get_envs()
        token = envs.get("TOKEN")
        if not token:
            raise ValueError("TOKEN não encontrado nas envs")

        url = f"{self.base_url}/users/test_user"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {"site_id": site_id} 

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            print(response.json())  
        
        except requests.HTTPError as e:
            print("Status:", response.status_code)
            try:
                print("Resposta JSON de erro:", response.json())
            except Exception:
                print("Resposta de erro (texto):", response.text)
            raise e

    def obter_preco_produto(self, item_id, chanel='channel_marketplace'):
        envs = self.get_envs()
        token = envs.get("TOKEN")
        url_preco = f'{self.base_url}/items/{item_id}/prices'
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url_preco, headers=headers)
        print(response.json())

ml_api = MercadoLivreAPI('.env')
ml_api.get_access_token()
ml_api.obter_preco_produto('MLB3128412969')

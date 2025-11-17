import unittest
import os
import sqlite3
from app import app, banco_de_dados 


app.config['TESTING'] = True

class CupcakeStoreTestCase(unittest.TestCase):
    
    
    def setUp(self):
        
        self.client = app.test_client()

    

    def test_1_home_page_loads(self):
        """Teste 1: Verifica se a Página Inicial (/) carrega (Código 200)"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        self.assertIn(b'NOSSOS CUPCAKES', response.data)
        print("v Teste da Home: SUCESSO")

    def test_2_login_page_loads(self):
        """Teste 2: Verifica se a Página de Login (/login) carrega (Código 200)"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        
        self.assertIn(b'CRIAR CONTA', response.data)
        print("v Teste da Pagina de Login: SUCESSO")

    def test_3_database_has_10_cupcakes(self):
        """Teste 3: Verifica se o banco de dados tem os 10 cupcakes cadastrados"""
        
        conn = sqlite3.connect(banco_de_dados)
        cupcakes = conn.execute('SELECT * FROM Cupcake').fetchall()
        conn.close()
        
        self.assertEqual(len(cupcakes), 10)
        print(f"v Teste do Banco de Dados: SUCESSO (Encontrados {len(cupcakes)} produtos)")

    def test_4_carrinho_redirects_if_not_logged_in(self):
        """Teste 4: Verifica se a rota /carrinho (protegida) redireciona para /login"""
        response = self.client.get('/carrinho')
        
        self.assertEqual(response.status_code, 302)
        
        self.assertIn('/login', response.location)
        print("v Teste de Rota Protegida (Carrinho): SUCESSO")


if __name__ == '__main__':
    print("--- Iniciando Testes Automatizados ---")
    unittest.main()
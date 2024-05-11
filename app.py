import os
import time

import dotenv
import flet as ft
import pyodbc
import logging

# Configuração do logger com info e error
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

dotenv.load_dotenv(dotenv.find_dotenv())

driver = '{SQL Server}'
server=os.getenv("SERVER")
database=os.getenv("DATABASE")
username=os.getenv("USER")
password=os.getenv("PASSWORD")

user_login = os.getenv("USER_LOGIN")
password_login = os.getenv("PASSWORD_LOGIN")

# Função para conectar ao banco de dados SQL Server
def conectar_banco():
    while True:
        try:
            conn = pyodbc.connect(
                f'DRIVER={driver};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password};'
            )
            logging.info("Conexão ao banco de dados estabelecida com sucesso.")
            return conn
        except pyodbc.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            logging.error(f"Erro ao conectar ao banco de dados: {e} - Verifique as configurações de conexão ou o banco de dados pode esta offline.")
            time.sleep(20)


def main(page: ft.Page):
    connect = conectar_banco()
    title = ft.Text("Usuários Sapiens Conectados", size=20)
    idUser = ft.TextField(label="ID User", width=100)
    # page.window_always_on_top = True
    page.window_width = 1200
    page.window_height = 800
    page.title = "Usuários Sapiens"
    # row = ft.Row(wrap=True, scroll="always", expand=True)
    # page.add(row)
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.update()

    cursor = connect.cursor()

    SQL_QUERY = """
    SELECT
    CASE modnam
        WHEN 'R' THEN 'MERCADO'
        WHEN 'S' THEN 'SUPRIMENTOS'
        WHEN 'F' THEN 'FINANÇAS'
        WHEN 'C' THEN 'CONTROLADORIA'
        ELSE 'LIVRE'
    END AS MODULOS,
    sec.numsec as ID_CONEXAO,
    CONVERT(
        VARCHAR, DATEADD(DAY, dattim, '1899-12-30'), 103
    ) + ' ' + RIGHT(
        '0' + CONVERT(
            VARCHAR, FLOOR(dattim % 1 * 24)
        ), 2
    ) + ':' + RIGHT(
        '0' + CONVERT(
            VARCHAR, FLOOR(dattim * 24 * 60) % 60
        ), 2
    ) AS DATA_CONEXAO,
    comnam AS NAME_SERVER,
    usrnam AS CONNECT_SERVER,
    appnam AS NAME_APP,
    appusr AS CONNECT_SAPIENS
    FROM sapiens.dbo.r911sec AS sec
    FULL OUTER JOIN sapiens.dbo.r911mod AS modulo ON sec.numsec = modulo.numsec
    WHERE appnam = 'SAPIENS' ORDER BY modnam;
    """

    page.scrollable = True
    table = ft.DataTable(
        border=ft.border.all(2, "blue"),
        border_radius=10,
        columns=[
            ft.DataColumn(ft.Text("MODULOS")),
            ft.DataColumn(ft.Text("ID_CONEXAO")),
            ft.DataColumn(ft.Text("DATA_CONEXAO")),
            ft.DataColumn(ft.Text("NAME_SERVER")),
            ft.DataColumn(ft.Text("CONNECT_SERVER")),
            ft.DataColumn(ft.Text("NAME_APP")),
            ft.DataColumn(ft.Text("CONNECT_SAPIENS"))
        ],
        rows=[]
    )

    def load_data():
        cursor.execute(SQL_QUERY)
        records = cursor.fetchall()

        for row in records:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row[0])),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(ft.Text(str(row[2]))),
                        ft.DataCell(ft.Text(str(row[3]))),
                        ft.DataCell(ft.Text(str(row[4]))),
                        ft.DataCell(ft.Text(str(row[5]))),
                        ft.DataCell(ft.Text(str(row[6])))
                    ]
                )
            )
        page.update()


 
    
    def close_modal(e):
        modal.open = False
        page.update()
        
    def login(e):
        user = 'admin'
        password = 'admin'

        if user == user_login and password == password_login:
            print("Login efetuado com sucesso!")
            modal.open = False
            page.add(desconectar_usuario)
            page.update()
        else:
            print("Usuário ou senha inválidos!")
            page.update()
    
    
    modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Login"),
        content=ft.Column([
            ft.TextField(label="Usuário", value=""),
            ft.TextField(label="Senha", value="", password=True),
        ]),
        actions=[
            ft.ElevatedButton(
                "Entrar",
                on_click=login
            ),
            ft.ElevatedButton(
                "Sair",
                on_click=close_modal
            )
        ]
    )
    
    def modal_login(e):
        page.dialog = modal
        modal.open = True
        page.update()

    def delete(e):
        try:
            id = idUser.value
            cursor.execute(f"DELETE FROM sapiens.dbo.r911mod WHERE numsec = {id}")
            cursor.execute(f"DELETE FROM sapiens.dbo.r911sec WHERE numsec = {id}")
            connect.cursor().commit()
            table.rows.clear()
            load_data()
            page.snack_bar = ft.SnackBar(
                ft.Text("Usuário Desconectado com Sucesso!",
                        size=30, color="white"),
                bgcolor="green",
            )
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            print(e)
            page.snack_bar = ft.SnackBar(
                ft.Text("Erro ao desconectar usuário!",
                        size=30, color="white"),
                bgcolor="red",
            )
            page.snack_bar.open = True
            page.update()

        idUser.value = ""
        page.update()

    load_data()
    
    desconectar_usuario = ft.Row([
    idUser,
    ft.ElevatedButton(
        "Desconectar",
        on_click=delete,
        height=50,
    ),
])
     
    page.padding = 100       
    page.add(
        title,        
        ft.Column([
            ft.Row([ft.ElevatedButton("ADMIN",on_click=modal_login)], alignment=ft.MainAxisAlignment.START),
            ft.Row([table], alignment=ft.MainAxisAlignment.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER),
        # ft.ElevatedButton(
        #     "UpDate",
        #     on_click=upDate
        # ),
        # ft.Row([
        #     idUser,
        #     ft.ElevatedButton(
        #         "Desconectar",
        #         on_click=delete,
        #         height=50,
        #     ),
        # ])
    )

    def run():
        while True:
            time.sleep(20)
            table.rows.clear()
            load_data()
            page.update()
    
    run()
            
            
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8181)



import os

import dotenv
import flet as ft
import pymssql

dotenv.load_dotenv()

# Connect to the database
conn = pymssql.connect(
    server=os.getenv("SERVER"),
    database=os.getenv("DATABASE"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    as_dict=True
)


def main(page: ft.Page):
    title = ft.Text("Usuarios Sapiens Conectados", size=20)
    idUser = ft.TextField(label="ID User", width=100)
    page.window_always_on_top = True
    page.window_width = 1200
    page.window_height = 800
    page.title = "Usuarios Sapiens"
    # row = ft.Row(wrap=True, scroll="always", expand=True)
    # page.add(row)
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.update()

    cursor = conn.cursor()

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
    usrnam AS CONECT_SERVER,
    appnam AS NAME_APP,
    appusr AS CONECT_SAPIENS
    FROM sapiens.dbo.r911sec AS sec
    FULL OUTER JOIN sapiens.dbo.r911mod AS modulo ON sec.numsec = modulo.numsec
    WHERE
    appnam = 'SAPIENS' ORDER BY modnam;
    """

    page.scrollable = True
    table = ft.DataTable(
        border=ft.border.all(2, "blue"),
        border_radius=10,
        columns=[
            ft.DataColumn(ft.Text("MODULOSss")),
            ft.DataColumn(ft.Text("ID_CONEXAO")),
            ft.DataColumn(ft.Text("DATA_CONEXAO")),
            ft.DataColumn(ft.Text("NAME_SERVER")),
            ft.DataColumn(ft.Text("CONECT_SERVER")),
            ft.DataColumn(ft.Text("NAME_APP")),
            ft.DataColumn(ft.Text("CONECT_SAPIENS"))
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
                        ft.DataCell(ft.Text(row['MODULOS'])),
                        ft.DataCell(ft.Text(row['ID_CONEXAO'])),
                        ft.DataCell(ft.Text(str(row['DATA_CONEXAO']))),
                        ft.DataCell(ft.Text(str(row['NAME_SERVER']))),
                        ft.DataCell(ft.Text(str(row['CONECT_SERVER']))),
                        ft.DataCell(ft.Text(str(row['NAME_APP']))),
                        ft.DataCell(ft.Text(str(row['CONECT_SAPIENS'])))
                    ]
                )
            )
        page.update()

    def upDate(e):
        table.rows.clear()
        load_data()

    def delete(e):
        try:
            id = idUser.value
            cursor.execute(
                f"DELETE FROM sapiens.dbo.r911mod WHERE numsec = {id}")
            conn.commit()
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

    page.add(
        title,
        ft.Row([
            table,
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.ElevatedButton(
            "UpDate",
            on_click=upDate
        ),
        ft.Row([
            idUser,
            ft.ElevatedButton(
                "Desconectar",
                on_click=delete,
                height=50,
            ),
        ])
    )


ft.app(target=main)

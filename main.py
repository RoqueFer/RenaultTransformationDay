import tkinter as tk
import random
from tkinter import *
from tkinter import messagebox
import mysql.connector

def create_connection():
    #Conexão com o banco de dados MySQL
    connection = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'root',
        database = 'renault'
    )

    return connection

def convert_to_int(tuple_list):
    #Conversor de tupla de 1 digito em int ex: (2,) 🠞 2 (int)
    if len(tuple_list) == 1 and len(tuple_list[0]) == 1:
        return tuple_list[0][0]
    else:
        raise ValueError("Input must be a list containing a single tuple with a single integer.")
    
def default_values_column(id_objetivo):
    # Cria 3 riscos com nomes aleatorios
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            for _ in range(3):
                cursor.execute(f"INSERT INTO riscos (nome_risco, id_objetivo_origem) VALUES ('risco{random.randint(1, 9999)}', {id_objetivo})")
    
            conn.commit()
    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")
    finally:
        if conn.is_connected():
            conn.close()

def create_tables():
    # Criação das tabelas objetivos, riscos e pesos
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `objetivos` (
            `id` int NOT NULL AUTO_INCREMENT,
            `nome_objetivo` varchar(50) NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    ''')
    conn.commit()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `riscos` (
            `id` int NOT NULL AUTO_INCREMENT,
            `nome_risco` varchar(45) DEFAULT NULL,
            `id_objetivo_origem` int NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    ''')
    conn.commit()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `pesos` (
            `id` int NOT NULL AUTO_INCREMENT,
            `nome_combinacao` varchar(45) DEFAULT NULL,
            `peso_combinacao` int NOT NULL,
            `id_objetivo_origem` int DEFAULT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;              
    ''')
    conn.commit()
    conn.close()

class telaObjetivos(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Objetivos")
        self.geometry("800x600")
        self.resizable(False, False)
        
        self.frameObjetivos = tk.Frame(self)
        self.frameObjetivos.pack(expand=True)

        self.botaoAdicionar = tk.Button(self, text="Adicionar Objetivo", command=self.adicionaObjetivo)
        self.botaoAdicionar.pack(pady=10)

        self.objetivos = self.carregaObjetivos()
        self.ticados = []
        self.atualizaObjetivos()

        self.frame = tk.Frame(self)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.botaoRiscos = tk.Button(self, text="Adicionar Risco", command=self.adicionarRisco)
        self.botaoRiscos.pack(pady=10)

        self.botaoProximo = tk.Button(self, text="🡆", command=self.excluiResto)
        self.botaoProximo.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

    def adicionarRisco(self):
        JanelaAddRisco(self)

    def carregaObjetivos(self):
        conn = create_connection()
        cursor = conn.cursor()
        query = "SELECT id, nome_objetivo FROM objetivos"
        cursor.execute(query)
        objetivos = cursor.fetchall()
        conn.close()

        objetivos_array = []

        for item in objetivos:
            objetivos_array.append(list(item))

        return objetivos_array

    def atualizaObjetivos(self):
        self.objetivos = self.carregaObjetivos()

        for widget in self.frameObjetivos.winfo_children():
            widget.destroy()

        self.ticados = []

        for _, objetivo in self.objetivos:
            taTicado = tk.BooleanVar()
            checkBox = tk.Checkbutton(self.frameObjetivos, text=f"{objetivo.capitalize()}", variable=taTicado)
            checkBox.pack(anchor="w")
            self.ticados.append(taTicado)

    def adicionaObjetivo(self):
        JanelaAddObjetivo(self)

    def excluiResto(self):
        self.ticados = [objetivo for objetivo, taTicado in zip(self.objetivos, self.ticados) if taTicado.get()]

        if len(self.ticados) < 1:
            self.atualizaObjetivos()
            self.wrong_data()
            return

        self.ticados_id = []
        
        row_numbers = []

        for tick in self.ticados:
            self.ticados_id.append(tick[0])

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM riscos WHERE id_objetivo_origem = {tick[0]}")
            all_info = cursor.fetchall()
            qtd_risco = cursor.rowcount
            conn.close()
            row_numbers.append(qtd_risco)

        # checando se todas as tabelas tem o mesmo tanto de riscos
        if(len(row_numbers) == len(set(row_numbers))):
            messagebox.showwarning("showwarning", f"Os objetivos selecionados tem números de riscos diferentes {row_numbers}")
            return

        self.destroy()
        self.nova_tela()
    
    def wrong_data(self):
        messagebox.showwarning("showwarning", "Dados insuficientes")
    
    def nova_tela(self):
        nova_tela = telaPeso(self.ticados_id)
        nova_tela.mainloop()

class JanelaAddRisco(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Adicionar Risco")
        self.geometry("400x300")
        self.parent = parent

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome_objetivo FROM objetivos")
        objetivos_query = cursor.fetchall()

        objetivos_array = [list(item) for item in objetivos_query]
        nomes_objetivos = [risco[0] for risco in objetivos_array]

        lista_objetivos = nomes_objetivos

        self.lb_objetivos = Listbox(self)
        for objetivo in lista_objetivos:
            self.lb_objetivos.insert(END, objetivo)
        self.lb_objetivos.select_set(0)
        self.lb_objetivos.pack()

        self.entryRisco = Entry(self)
        self.entryRisco.pack(pady=5)

        self.botaoAdicionarRisco = tk.Button(self, text="Adicionar", command=self.adicionarRisco)
        self.botaoAdicionarRisco.pack(pady=10)

    def adicionarRisco(self):
        objetivo_marcado = self.lb_objetivos.get(ACTIVE)
        print(objetivo_marcado)
        novo_risco = self.entryRisco.get()
        print(novo_risco)

        if novo_risco.replace(" ", "") == "":
            messagebox.showwarning("showwarning", "Valores faltando")
            return
        #pegando o id do objetivo da lista
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM objetivos WHERE nome_objetivo = '{objetivo_marcado}'")
        id_objetivo = cursor.fetchall()
        id_objetivo = convert_to_int(id_objetivo)

        cursor.execute(f"INSERT INTO riscos (nome_risco, id_objetivo_origem) VALUES ('{novo_risco}', {id_objetivo})")
        conn.commit()
        conn.close()
        self.destroy()

class JanelaAddObjetivo(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Adicionar Objetivo")
        self.geometry("300x150")
        self.parent = parent

        self.label = tk.Label(self, text="Insira um novo objetivo:")
        self.label.pack(pady=10)

        self.entryObjetivo = tk.Entry(self)
        self.entryObjetivo.pack(pady=5)

        self.botaoAdicionar = tk.Button(self, text="Adicionar", command=self.adicionarObjetivo)
        self.botaoAdicionar.pack(pady=10)

    def adicionarObjetivo(self):
        novoObjetivo = self.entryObjetivo.get()
        try:
            conn = create_connection()
            cursor = conn.cursor()
            query = "SELECT id, nome_objetivo FROM objetivos"
            cursor.execute(query)
            dados = []

            for item in cursor.fetchall():
                dados.append(list(item))
            
            repetido = False

            for dado in dados:
                if novoObjetivo == dado[1]:
                    repetido = True
            
            if repetido == False:
                query = f"INSERT INTO objetivos (nome_objetivo) VALUES ('{novoObjetivo}')"
                cursor.execute(query)
            else:
                messagebox.showwarning("showwarning", "Objetivo já cadastrado")
                    
            conn.commit()

            cursor.execute(f"SELECT id FROM objetivos where nome_objetivo = '{novoObjetivo}'")
            id = cursor.fetchall()
            id = convert_to_int(id)
            print(f"id nova tabela: {id}")
            conn.commit()
            conn.close()
            self.parent.objetivos.append(novoObjetivo) 
            self.parent.atualizaObjetivos()
            default_values_column(id)
            self.destroy()
        except Exception as e:
            print(e)

class telaPeso(tk.Tk):
    def __init__(self, objetivos):
        super().__init__()
        self.resizable(False, False)
        self.title("Atribua pesos aos riscos")
        self.window_height = 600
        self.window_width = 800
        self.geometry(f"{self.window_width}x{self.window_height}")

        self.objetivos_id = objetivos

        self.total_pages = len(objetivos)
        self.page = 1
        self.current_page = 1

        self.page_frame = tk.Frame(self)
        self.page_frame.pack(fill=tk.BOTH, expand=True)

        self.show_page(self.page)
    
    def show_page(self, page):
        # Limpar o conteúdo da página anterior
        for widget in self.page_frame.winfo_children():
            widget.destroy()

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM riscos WHERE id_objetivo_origem = {self.objetivos_id[page - 1]}")
        all_risks = cursor.fetchall()
        conn.close()

        risks_array = [list(item) for item in all_risks]
        nomes_riscos_array = [risco[1] for risco in risks_array]

        combinacoes = []
        self.entries = {}

        # Checando todas as combinações
        for risco_primario in nomes_riscos_array:
            for risco_secundario in nomes_riscos_array:
                if risco_primario != risco_secundario:
                    comb = f"{risco_primario}X{risco_secundario}"
                    comb_inversa = f"{risco_secundario}X{risco_primario}"
                    if comb_inversa not in combinacoes:
                        combinacoes.append(comb)

        # Pegando a info de todas as combinações salvas no banco de dados
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT nome_combinacao, peso_combinacao FROM pesos WHERE id_objetivo_origem = {self.objetivos_id[page - 1]}")
        pesos_info_response = cursor.fetchall()
        conn.close()

        pesos_lista = {item[0]: item[1] for item in pesos_info_response}

        # Novamente uma checagem das combinações, criando ela caso não exista com o peso 1 (default)
        i = 0
        for combinacao in combinacoes:
            if combinacao not in pesos_lista:
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO pesos (nome_combinacao, peso_combinacao, id_objetivo_origem) VALUES ('{combinacao}', 1, {self.objetivos_id[page - 1]})")
                conn.commit()
                conn.close()

            peso = pesos_lista.get(combinacao, 1)

            risco1, risco2 = combinacao.split('X')
            tk.Label(self.page_frame, text=risco1).place(x=self.window_width/2 - 100, y=10 + (i * 50))
            
            entry = tk.Entry(self.page_frame, width=3)
            entry.place(x=self.window_width/2, y=10 + (i * 50))
            entry.insert(0, str(peso))
            
            tk.Label(self.page_frame, text=risco2).place(x=self.window_width/2 + 100, y=10 + (i * 50))
            
            self.entries[combinacao] = entry
            i += 1

        if self.current_page < self.total_pages:
            self.next_button = tk.Button(self.page_frame, text="Next", command=self.change_pages_next)
            self.next_button.place(x=self.window_width-300, y=self.window_height-100)
        if self.current_page > 1:
            self.back_button = tk.Button(self.page_frame, text="Previous", command=self.change_pages_previous)
            self.back_button.place(x=250, y=self.window_height-100)
        if self.current_page == self.total_pages:
            self.compute_button = tk.Button(self.page_frame, text="Finish", command=self.finish_settings)
            self.compute_button.place(x=self.window_width-300, y=self.window_height-100)

        self.peso_info = tk.Button(self.page_frame, text="Help", command=self.show_help_info)
        self.peso_info.place(x=self.window_width/2 - 10, y=self.window_height - 100)

    def change_pages_next(self):
        dados = self.get_entries_values()
        for valor in dados.values():
            if self.check_values(valor) == False:
                messagebox.showwarning("showwarning", "Dados incorretos")
                return
            
        if self.current_page < self.total_pages:
            self.update_database()
            self.current_page += 1
            self.show_page(self.current_page)

    def change_pages_previous(self):
        dados = self.get_entries_values()

        for valor in dados.values():
            if self.check_values(valor) == False:
                messagebox.showwarning("showwarning", "Dados incorretos")
                return

        if self.current_page > 1:
            self.update_database()
            self.current_page -= 1
            self.show_page(self.current_page)

    def show_help_info(self):
        help_window = tk.Toplevel(self)
        help_window.title("Informações de valores")
        help_window.geometry("400x200")
        help_window.resizable(False, False)
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(tk.END, 
        """
        1 → Igual importância
        3 → Pouco mais importante
        5 → Muito mais importante
        7 → Bastante mais importante
        9 → Extremamente mais importante
        2, 4, 6, 8 → Valores intermediários
        """)
        text_widget.configure(state='disabled')
        text_widget.pack(expand=True, fill=tk.BOTH)

        close_button = tk.Button(help_window, text="Fechar", command=help_window.destroy)
        close_button.pack(pady=10)

    def get_entries_values(self):
        valores = {}
        for combinacao, entry in self.entries.items():
            try:
                valor = int(entry.get())
                if self.check_values(valor):
                    valores[combinacao] = valor
                else:
                    valores[combinacao] = None
            except ValueError:
                valores[combinacao] = None
        return valores

    def update_database(self):
        values = self.get_entries_values()

        conn = create_connection()
        for key, value in values.items():
            cursor = conn.cursor()
            cursor.execute(f"UPDATE pesos SET peso_combinacao = {value} WHERE nome_combinacao = '{key}'")
            conn.commit()
        conn.close()
        return

    def check_values(self, value):
        range_aceito = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        return value in range_aceito

    def finish_settings(self):
        self.update_database()
        # Próxima página
        messagebox.showinfo("showinfo", "Próxima pagina!")
        self.destroy()

if __name__ == "__main__":
    create_tables()
    tela = telaObjetivos()
    tela.mainloop()
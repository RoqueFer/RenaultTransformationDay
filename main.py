import tkinter as tk
from tkinter import *
from tkinter import messagebox
import mysql.connector

def show_custom_messagebox(root, title, message, geometry=("300x150")):
    # Cria uma nova janela de diálogo
    dialog = tk.Toplevel(root)
    dialog.title(title)
    
    # Define o tamanho inicial da janela
    dialog.geometry(geometry)
    
    # Adiciona uma label para a mensagem
    label = tk.Label(dialog, text=message, wraplength=400)
    label.pack(padx=10, pady=10)
    
    # Adiciona um botão para fechar a janela
    button = tk.Button(dialog, text="OK", command=dialog.destroy)
    button.pack(pady=(0, 10))
    
    # Faz a janela modal, bloqueando a interação com a janela principal
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

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

def convert_to_str(tuple_list):
    return tuple_list[0][0]

def check_array_same_value(*arrays):
    # Verifica se a lista está vazia ou contém apenas um array
    if not arrays or len(arrays) == 1:
        return True

    # Compara cada array com o primeiro
    primeiro_array = arrays[0]
    return all(array == primeiro_array for array in arrays)

def default_values_column(id_objetivo):
    # Cria 3 riscos com nomes aleatorios
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            for i in range(3):
                cursor.execute(f"INSERT INTO riscos (nome_risco, id_objetivo_origem) VALUES ('risco{i}', {id_objetivo})")
    
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
        self.botaoRemover = tk.Button(self, text="Remover Objetivo", command=self.removerObjetivo)
        self.botaoRemover.pack(pady=10)

        self.objetivos = self.carregaObjetivos()
        self.ticados = []
        self.atualizaObjetivos()

        self.frame = tk.Frame(self)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.botaoRiscos = tk.Button(self, text="Adicionar Risco", command=self.adicionarRisco)
        self.botaoRiscos.pack(pady=10)

        self.removerRiscos = tk.Button(self, text="Remover Risco", command=self.removerRisco)
        self.removerRiscos.pack(pady=10)

        self.botaoProximo = tk.Button(self, text="🡆", command=self.excluiResto)
        self.botaoProximo.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

    def adicionarRisco(self):
        JanelaAddRisco(self)

    def removerRisco(self):
        JanelaRemoverRisco(self)

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
        self.atualizaObjetivos()
    
    def removerObjetivo(self):
        JanelaRemoverObjetivo(self)
        self.atualizaObjetivos()

    def excluiResto(self):
        self.ticados = [objetivo for objetivo, taTicado in zip(self.objetivos, self.ticados) if taTicado.get()]

        if len(self.ticados) < 1:
            self.atualizaObjetivos()
            self.wrong_data()
            return

        self.ticados_id = []
    
        infos = []

        for tick in self.ticados:
            self.ticados_id.append(tick[0])

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT nome_risco FROM riscos WHERE id_objetivo_origem = {tick[0]}")
            all_info = cursor.fetchall()
            transform_to_list = [item for final_info in all_info for item in final_info]
            infos.append(transform_to_list)
            conn.close()

        if not check_array_same_value(*infos):
            full_str = "Os objetivos possuem riscos diferentes: "

            for i in range(len(self.ticados_id)):
                full_str += f"\nRisco: {self.ticados[i][1]} - {infos[i]}"

            self.ticados = []
            self.atualizaObjetivos()

            show_custom_messagebox(self, "Erro de conflito", full_str, "400x150")
            return
        

        self.destroy()
        self.nova_tela()
    
    def wrong_data(self):
        messagebox.showwarning("showwarning", "Dados insuficientes")
    
    def nova_tela(self):
        nova_tela = telaPeso(self.ticados_id)
        nova_tela.mainloop()

class JanelaRemoverRisco(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Remover Risco")
        self.geometry("400x300")
        self.parent = parent

        self.show_first_window()

    def show_first_window(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome_objetivo FROM objetivos")
        objetivos_query = cursor.fetchall()

        objetivos_array = [list(item) for item in objetivos_query]
        nomes_objetivos = [risco[0] for risco in objetivos_array]

        lista_objetivos = nomes_objetivos
        conn.close()

        self.lb_objetivos = Listbox(self)
        for objetivos in lista_objetivos:
            self.lb_objetivos.insert(END, objetivos)
        self.lb_objetivos.select_set(0)
        self.lb_objetivos.pack()

        tk.Button(self, text="Selecionar Objetivo", command=self.select_risks).pack()

    def select_risks(self):
        objetivo_selecionado = self.lb_objetivos.get(ACTIVE)

        if objetivo_selecionado == "":
            show_custom_messagebox(self, "Erro", "Você precisa selecionar um objetivo")
            return

        self.clear_window()

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM objetivos WHERE nome_objetivo = '{objetivo_selecionado}'")
        self.id_objetivo_selecionado = cursor.fetchall()
        self.id_objetivo_selecionado = convert_to_int(self.id_objetivo_selecionado)
        conn.commit()
        cursor.execute(f"SELECT nome_risco FROM riscos WHERE id_objetivo_origem = {self.id_objetivo_selecionado}")
        riscos_query = cursor.fetchall()
        riscos_array = [list(item) for item in riscos_query]
        nomes_riscos = [risco[0] for risco in riscos_array]
        conn.commit()
        conn.close()

        self.lb_riscos = Listbox(self)
        for risco in nomes_riscos:
            self.lb_riscos.insert(END, risco)
        self.lb_riscos.select_set(0)
        self.lb_riscos.pack()

        tk.Button(self, text="Remover", command=self.remove_risk).pack()

    def remove_risk(self):
        
        risk_to_remove = self.lb_riscos.get(ACTIVE)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM riscos WHERE nome_risco = '{risk_to_remove}' AND id_objetivo_origem = {self.id_objetivo_selecionado}")
        conn.commit()
        conn.close()
        self.update_db_removing_old_risks(risk_to_remove)
        self.destroy()

    def update_db_removing_old_risks(self, risk):
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, nome_combinacao FROM pesos WHERE id_objetivo_origem = {self.id_objetivo_selecionado}")
        pesos_query = cursor.fetchall()
        pesos_array = [list(item) for item in pesos_query]

        if pesos_array == []:
            return

        for peso in pesos_array:
            peso_id = peso[0]
            nome_peso = peso[1]

            nome1, nome2 = nome_peso.split("X")

            if nome1 == risk or nome2 == risk:
                cursor.execute(f"DELETE FROM pesos WHERE id = {peso_id}")
                conn.commit()
        conn.close()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

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
        novo_risco = self.entryRisco.get()
        if objetivo_marcado == "" or novo_risco.replace(" ", "") == "":
            string = ""
            if objetivo_marcado == "":
                string = "Você precisa marcar um objetivo"
            else:
                string = "Você precisa preencher o nome do risco"

            show_custom_messagebox(self, "Erro", string)
            return
        
        if self.check_risk_exists(novo_risco):
            show_custom_messagebox(self, "Erro", "Já existe um risco com esse nome+")
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

    def check_risk_exists(self, risk):
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM riscos WHERE nome_risco = '{risk}'")
        cursor.fetchall()
        row = cursor.rowcount
        conn.close()
        
        return row > 0

class JanelaRemoverObjetivo(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizable(False, False)
        self.title("Remover Objetivo")
        self.geometry("300x250")
        self.parent = parent

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome_objetivo FROM objetivos")
        objetivos_query = cursor.fetchall()
        conn.close()

        objetivos_array = [list(item) for item in objetivos_query]
        nomes_objetivos = [risco[0] for risco in objetivos_array]
    
        self.lb_objetivos_remove = Listbox(self)
        for objetivo in nomes_objetivos:
            self.lb_objetivos_remove.insert(END, objetivo)
        self.lb_objetivos_remove.select_set(0)
        self.lb_objetivos_remove.pack()

        Button(self, text="Remover Objetivo", command=self.remove_objetivo).pack()

    def remove_objetivo(self):
        objetivo_to_remove = self.lb_objetivos_remove.get(ACTIVE)

        if objetivo_to_remove == "":
            show_custom_messagebox(self, "Erro", "Você precisa selecionar um objetivo")
            return
        
        self.remove_all_from_db(objetivo_to_remove)
        self.parent.atualizaObjetivos()

        self.destroy()

    def remove_all_from_db(self, nome_objetivo):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM objetivos WHERE nome_objetivo = '{nome_objetivo}'")
        id = cursor.fetchall()
        id = convert_to_int(id)
        cursor.execute(f"DELETE pesos, riscos FROM pesos INNER JOIN riscos WHERE pesos.id_objetivo_origem = riscos.id_objetivo_origem AND pesos.id_objetivo_origem = {id}")
        cursor.execute(f"DELETE FROM objetivos WHERE nome_objetivo = '{nome_objetivo}'")
        conn.commit()
        conn.close()

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

        if novoObjetivo.replace(" ", "") == "":
            show_custom_messagebox(self, "Erro", "Você precisa dar um nome ao objetivo")
            return

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
                return
                    
            conn.commit()

            cursor.execute(f"SELECT id FROM objetivos where nome_objetivo = '{novoObjetivo}'")
            id = cursor.fetchall()
            id = convert_to_int(id)
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

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT nome_objetivo FROM objetivos WHERE id = {self.objetivos_id[page-1]}")
        nome_obj = cursor.fetchall()
        conn.close()

        Label(self.page_frame, text=convert_to_str(nome_obj), font=("Arial", 24), wraplength=250).place(x=self.window_width/2 - 370, y=10)

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
                cursor.execute(f"INSERT INTO pesos (nome_combinacao, peso_combinacao, id_objetivo_origem) VALUES ('{combinacao}', 1, {self.objetivos_id[page - 1]}); ")
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

        if self.current_page <= self.total_pages:
            if self.total_pages != 1:
                self.next_button = tk.Button(self.page_frame, text="Next", command=self.change_pages_next)
                self.next_button.place(x=self.window_width-300, y=self.window_height-100)
            self.home_button = tk.Button(self.page_frame, text="Home", command=self.back_to_home)
            self.home_button.place(x=250, y=self.window_height-100)
        if self.current_page > 1:
            self.back_button = tk.Button(self.page_frame, text="Previous", command=self.change_pages_previous)
            self.back_button.place(x=250, y=self.window_height-100)
        if self.current_page == self.total_pages:
            self.compute_button = tk.Button(self.page_frame, text="Finish", command=self.finish_settings)
            self.compute_button.place(x=self.window_width-300, y=self.window_height-100)

        self.peso_info = tk.Button(self.page_frame, text="Help", command=self.show_help_info)
        self.peso_info.place(x=self.window_width/2 - 10, y=self.window_height - 100)

    def back_to_home(self):
        self.destroy()
        telaObjetivos()
        return

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
        cursor = conn.cursor()
        full_query = ""
        for key, value in values.items():
            full_query += f"UPDATE pesos SET peso_combinacao = {value} WHERE nome_combinacao = '{key}' AND id_objetivo_origem = {self.objetivos_id[self.current_page - 1]}; commit; "
        cursor.execute(full_query)
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
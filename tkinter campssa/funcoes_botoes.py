import logging
from openpyxl import load_workbook
import tkinter as tk
from tkinter import messagebox
from planilhas import Planilhas
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configurando logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def role_e_click(driver, xpath):
    """Rola a página até um elemento e clica nele.

    Args:
        driver: Instância do WebDriver do Selenium.
        xpath: XPath do elemento a ser clicado.
    """
    element = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.XPATH, xpath))
    )
    # Rola para o elemento
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    element.click()


class FuncoesBotoes:
    """Classe que encapsula as funções relacionadas aos botões da interface."""

    def __init__(self, master: tk, planilhas: Planilhas, file_path: str, app):
        """Inicializa a classe FuncoesBotoes.

        Args:
            master: Janela pai do Tkinter.
            planilhas: Instância da classe Planilhas.
            file_path: Caminho do arquivo de planilha.
            app: Instância da aplicação principal.
        """
        self.master = master
        self.planilhas = planilhas
        self.wb = self.planilhas.wb if self.planilhas else None
        self.file_path = file_path
        self.app = app
        self.login_frame = None
        self.criar_conta_frame = None

        # Variáveis para opções de pagamento
        self.forma_pagamento_var = tk.StringVar(value="")
        self.radio_var = tk.StringVar(value="")

        # Variáveis de controle para checkbuttons
        self.d_var = tk.IntVar()
        self.c_var = tk.IntVar()
        self.e_var = tk.IntVar()
        self.p_var = tk.IntVar()

        # Entradas para os campos de pagamento
        self.entry_d = tk.Entry(master)
        self.entry_c = tk.Entry(master)
        self.entry_e = tk.Entry(master)
        self.entry_p = tk.Entry(master)

        # Entradas para os valores associados
        self.entry_valor_d = tk.Entry(master)  # Entrada para valor de D
        self.entry_valor_c = tk.Entry(master)  # Entrada para valor de C
        self.entry_valor_e = tk.Entry(master)  # Entrada para valor de E
        self.entry_valor_p = tk.Entry(master)  # Entrada para valor de P

    def center(self, window):
        """Centraliza a janela na tela.

        Args:
            window: A instância da janela Tkinter que deve ser centralizada.
        """
        # Atualiza o tamanho solicitado pela janela
        window.update_idletasks()

        # Obtém as dimensões atuais da janela
        width = window.winfo_width()
        height = window.winfo_height()

        # Obtém as dimensões da tela
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calcula as coordenadas x e y para centralizar a janela
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Aplica a nova geometria à janela
        window.geometry(f"{width}x{height}+{x}+{y}")

        # Mostra a janela (se estiver oculta)
        window.deiconify()

    def adicionar_informacao(self):
        """Cria uma nova janela para adicionar informações de pacientes."""
        # Criação da nova janela
        self.adicionar_window = tk.Toplevel(self.master)
        self.adicionar_window.title("Adicionar Paciente")
        self.adicionar_window.geometry("400x380")
        self.adicionar_window.minsize(width=400, height=380)
        self.adicionar_window.maxsize(width=400, height=380)

        # Configuração das cores
        cor_fundo = self.master.cget("bg")
        cor_texto = "#ECF0F1"
        cor_selecionado = "#2C3E50"

        self.adicionar_window.configure(bg=cor_fundo)

        # Centraliza a nova janela
        self.center(self.adicionar_window)

        # Adicionando os componentes da interface
        tk.Label(
            self.adicionar_window,
            text="Preencha as informações:",
            bg=cor_fundo,
            fg=cor_texto,
            font=("Arial", 16, "bold"),
        ).pack(pady=(15, 5))

        # Frame para os RadioButtons
        frame_radios = tk.Frame(self.adicionar_window, bg=cor_fundo)
        frame_radios.pack(pady=5)

        # RadioButtons para seleção de tipo
        tipos = [("Médico", "medico"), ("Psicólogo", "psicologo"), ("Ambos", "ambos")]
        for tipo, valor in tipos:
            tk.Radiobutton(
                frame_radios,
                text=tipo,
                variable=self.radio_var,
                value=valor,
                bg=cor_fundo,
                fg=cor_texto,
                selectcolor=cor_selecionado,
                activebackground=cor_fundo,
                activeforeground=cor_texto,
                highlightthickness=0,
                font=("Arial", 12),
            ).pack(side=tk.LEFT, padx=2)

        # Frame para entrada de nome
        self.criar_entry(frame_nome="Nome:", var_name="nome_entry", parent=self.adicionar_window)

        # Frame para entrada de Renach
        self.criar_entry(frame_nome="Renach:", var_name="renach_entry", parent=self.adicionar_window)

        tk.Label(
            self.adicionar_window,
            text="Forma de Pagamento:",
            bg=cor_fundo,
            fg=cor_texto,
            font=("Arial", 16, "bold"),
        ).pack(pady=(15, 5))

        # Frame para opções de pagamento
        frame_pagamento = tk.Frame(self.adicionar_window, bg=cor_fundo)
        frame_pagamento.pack(pady=2)

        # Variáveis para checkbuttons
        self.d_var = tk.IntVar()
        self.c_var = tk.IntVar()
        self.e_var = tk.IntVar()
        self.p_var = tk.IntVar()

        # Lista de checkbuttons
        checkbuttons = [("D", self.d_var), ("C", self.c_var), ("E", self.e_var), ("P", self.p_var)]

        # Campos de entrada ao lado de cada checkbutton
        entry_widgets = [tk.Entry(frame_pagamento, width=10) for _ in range(4)]

        for i, (text, var) in enumerate(checkbuttons):
            tk.Checkbutton(
                frame_pagamento,
                text=text,
                variable=var,
                bg=cor_fundo,
                fg=cor_texto,
                selectcolor=cor_selecionado,
                activebackground=cor_fundo,
                activeforeground=cor_texto,
                highlightthickness=0,
            ).grid(row=i, column=0, padx=2, pady=2, sticky="w")
            entry_widgets[i].grid(row=i, column=1, padx=2, pady=2)

        # Frame para botões
        frame_botoes = tk.Frame(self.adicionar_window, bg=cor_fundo)
        frame_botoes.pack(pady=10)

        tk.Button(
            frame_botoes,
            text="Adicionar",
            command=self.salvar_informacao,
            highlightthickness=0,
            activebackground="#2C3E50",
            activeforeground="#ECF0F1",
        ).pack(side=tk.LEFT, padx=10, pady=10)

        tk.Button(
            frame_botoes,
            text="Voltar",
            command=self.adicionar_window.destroy,
            activebackground="#2C3E50",
            activeforeground="#ECF0F1",
        ).pack(side=tk.LEFT, padx=10, pady=10)

    def criar_entry(self, frame_nome, var_name, parent):
        """Cria um frame com label e entry para entradas de texto.

        Args:
            frame_nome: O texto do label.
            var_name: O nome da variável de entrada a ser criada.
            parent: O widget pai onde o frame será adicionado.
        """
        frame = tk.Frame(parent, bg=parent.cget("bg"))
        frame.pack(pady=2)

        tk.Label(
            frame, text=frame_nome, bg=parent.cget("bg"), fg="#ECF0F1", font=("Arial", 12)
        ).pack(side=tk.LEFT, anchor="w", padx=5)
        
        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT, padx=2)

        # Armazena a entrada na instância da classe
        setattr(self, var_name, entry)

    def salvar_informacao(self):
        # Obter dados dos campos de entrada
        nome = self.nome_entry.get().strip().upper()
        renach = self.renach_entry.get().strip()

        # Validar preenchimento do nome e RENACH
        if not nome or not renach:
            messagebox.showerror("Erro", "Por favor, preencha os campos de nome e RENACH.")
            return

        # Validar se RENACH é um número inteiro
        if not renach.isdigit():
            messagebox.showerror("Erro", "O RENACH deve ser um número inteiro.")
            return

        # Verificar se o RENACH já existe na planilha
        ws = self.wb.active
        for row in ws.iter_rows(min_row=3, max_row=ws.max_row):
            if str(row[2].value) == renach or str(row[8].value) == renach:
                messagebox.showerror("Erro", "Este RENACH já está registrado.")
                return

        # Obter dados dos checkbuttons de pagamento
        pagamentos_selecionados = [
            ("D", self.d_var.get(), self.entry_d.get().strip(), self.entry_valor_d.get().strip()),
            ("C", self.c_var.get(), self.entry_c.get().strip(), self.entry_valor_c.get().strip()),
            ("E", self.e_var.get(), self.entry_e.get().strip(), self.entry_valor_e.get().strip()),
            ("P", self.p_var.get(), self.entry_p.get().strip(), self.entry_valor_p.get().strip()),
        ]
        
        # Filtrar formas de pagamento selecionadas
        selecionados = [p for p in pagamentos_selecionados if p[1] == 1]

        # Verificar se ao menos uma forma de pagamento foi selecionada
        if not selecionados:
            messagebox.showerror("Erro", "Selecione pelo menos uma forma de pagamento.")
            return

        # Verificar escolha entre médico, psicólogo ou ambos
        escolha = self.radio_var.get()
        if escolha not in ["medico", "psicologo", "ambos"]:
            messagebox.showerror("Erro", "Selecione Médico, Psicólogo ou Ambos.")
            return

        # Encontrar a próxima linha vazia para médicos e psicólogos
        nova_linha_medico = next((row for row in range(3, ws.max_row + 2) if not ws[f"B{row}"].value), None)
        nova_linha_psicologo = next((row for row in range(3, ws.max_row + 2) if not ws[f"H{row}"].value), None)

        # Inserir informações na planilha com base na escolha
        if escolha == "medico":
            ws[f"B{nova_linha_medico}"] = nome
            ws[f"C{nova_linha_medico}"] = renach
            ws[f"F{nova_linha_medico}"] = ", ".join([f"{p[0]}: {p[2]} - {p[3]}" for p in selecionados])
            messagebox.showinfo("Paciente adicionado para se consultar com médico!")

        elif escolha == "psicologo":
            ws[f"H{nova_linha_psicologo}"] = nome
            ws[f"I{nova_linha_psicologo}"] = renach
            ws[f"L{nova_linha_psicologo}"] = ", ".join([f"{p[0]}: {p[2]} - {p[3]}" for p in selecionados])
            messagebox.showinfo("Paciente adicionado para se consultar com psicólogo!")

        elif escolha == "ambos":
            ws[f"B{nova_linha_medico}"] = nome
            ws[f"C{nova_linha_medico}"] = renach
            ws[f"F{nova_linha_medico}"] = ", ".join([f"{p[0]}: {p[2]} - {p[3]}" for p in selecionados])
            ws[f"H{nova_linha_psicologo}"] = nome
            ws[f"I{nova_linha_psicologo}"] = renach
            ws[f"L{nova_linha_psicologo}"] = ", ".join([f"{p[0]}: {p[2]} - {p[3]}" for p in selecionados])
            messagebox.showinfo("Paciente adicionado para se consultar com médico e psicólogo!")

        # Salvar na planilha
        self.wb.save(self.planilhas.file_path)

        # Limpar os campos de entrada
        self.nome_entry.delete(0, tk.END)
        self.renach_entry.delete(0, tk.END)
        self.radio_var.set("")
        self.d_var.set(0)
        self.c_var.set(0)
        self.e_var.set(0)
        self.p_var.set(0)
        self.entry_d.delete(0, tk.END)
        self.entry_c.delete(0, tk.END)
        self.entry_e.delete(0, tk.END)
        self.entry_p.delete(0, tk.END)
        self.entry_valor_d.delete(0, tk.END)
        self.entry_valor_c.delete(0, tk.END)
        self.entry_valor_e.delete(0, tk.END)
        self.entry_valor_p.delete(0, tk.END)


    def excluir(self):
            """Remove informações de pacientes da planilha com base no RENACH fornecido pelo usuário e reorganiza as linhas."""
            ws = self.wb.active
            pacientes_medicos = {}
            pacientes_psicologos = {}
    
            # Armazenar pacientes de médicos
            for row in ws.iter_rows(min_row=3, max_row=ws.max_row):
                if row[1].value and row[2].value:
                    try:
                        renach_medico = int(row[2].value)
                        pacientes_medicos.setdefault(renach_medico, []).append(row[0].row)
                    except ValueError:
                        print(f"RENACH inválido na linha {row[0].row}: {row[2].value}")
    
            # Armazenar pacientes psicólogos
            for row in ws.iter_rows(min_row=3, max_row=ws.max_row):
                if row[7].value and row[8].value:
                    try:
                        renach_psicologo = int(row[8].value)
                        pacientes_psicologos.setdefault(renach_psicologo, []).append(row[0].row)
                    except ValueError:
                        print(f"RENACH inválido na linha {row[0].row}: {row[8].value}")
    
            # Janela de exclusão
            excluir_window = tk.Toplevel(self.master)
            excluir_window.title("Excluir Paciente")
            excluir_window.geometry("400x150")
            excluir_window.configure(bg=self.master.cget("bg"))
    
            tk.Label(
                excluir_window,
                text="Informe o RENACH:",
                bg=self.master.cget("bg"),
                fg="#ECF0F1",
                font=("Arial", 14, "bold"),
            ).pack(pady=10)
            renach_entry = tk.Entry(excluir_window)
            renach_entry.pack(pady=5)
    
            def excluir_paciente():
                """Função para excluir o paciente com o RENACH fornecido"""
                try:
                    renach = int(renach_entry.get())
    
                    def reorganizar_linhas(linha_excluida):
                        """Função auxiliar para mover os dados de cada linha uma posição para cima"""
                        for row in range(linha_excluida, ws.max_row):
                            for col in range(1, ws.max_column + 1):
                                ws.cell(row=row, column=col).value = ws.cell(row=row + 1, column=col).value
                        # Limpar a última linha
                        for col in range(1, ws.max_column + 1):
                            ws.cell(row=ws.max_row, column=col).value = None
    
                    # Excluir paciente de médico
                    if renach in pacientes_medicos:
                        for linha in pacientes_medicos[renach]:
                            reorganizar_linhas(linha)
    
                    # Excluir paciente de psicólogo
                    if renach in pacientes_psicologos:
                        for linha in pacientes_psicologos[renach]:
                            reorganizar_linhas(linha)
    
                    self.wb.save("CAMPSSA.xlsx")
                    print("Paciente foi excluído com sucesso!")
                except ValueError:
                    print("RENACH inválido. Por favor, insira um número válido.")
    
            tk.Button(excluir_window, text="Excluir", command=excluir_paciente).pack(pady=10)
    
            self.center(excluir_window)

    def exibir_informacao(self):
        """Exibe informações dos pacientes em uma nova janela com barra de rolagem."""
        ws = self.wb.active
        medico, psi = [], []

        # Informações de médicos
        for row in ws.iter_rows(min_row=3, max_row=ws.max_row, min_col=2, max_col=6):
            linha = [
                cell.value
                for cell in row
                if isinstance(cell.value, (str, int)) and str(cell.value).strip()
            ]
            if linha:
                medico.append(linha)

        # Informações de psicólogos
        for row in ws.iter_rows(min_row=3, max_row=ws.max_row, min_col=8, max_col=12):
            linha = [
                cell.value
                for cell in row
                if isinstance(cell.value, (str, int)) and str(cell.value).strip()
            ]
            if linha:
                psi.append(linha)

        # Criando uma nova janela
        janela_informacao = tk.Toplevel(self.master)
        janela_informacao.title("Informação dos Pacientes")
        janela_informacao.geometry("600x600")
        janela_informacao.maxsize(width=600, height=600)
        janela_informacao.minsize(width=600, height=600)

        # Usando a cor de fundo da janela principal
        cor_fundo = self.master.cget("bg")
        janela_informacao.configure(bg=cor_fundo)

        # Configurando o Canvas e a barra de rolagem
        canvas = tk.Canvas(janela_informacao, bg=cor_fundo)
        scrollbar = tk.Scrollbar(
            janela_informacao, orient="vertical", command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas, bg=cor_fundo)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Adicionando a barra de rolagem ao canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Adicionando informações de médicos
        if medico:
            tk.Label(
                scrollable_frame,
                text="MÉDICO:",
                font=("Arial", 16, "bold"),
                bg=cor_fundo,
                fg="#ECF0F1",
            ).pack(pady=(10, 0))
            for i, paciente in enumerate(medico, start=1):
                tk.Label(
                    scrollable_frame,
                    text=f"{i} - {paciente}",
                    bg=cor_fundo,
                    fg="#ECF0F1",
                    font=("Arial", 12),
                ).pack(anchor="w", padx=10, pady=5)

        # Adicionando informações de psicólogos
        if psi:
            tk.Label(
                scrollable_frame,
                text="PSICÓLOGO:",
                font=("Arial", 16, "bold"),
                bg=cor_fundo,
                fg="#ECF0F1",
            ).pack(pady=(10, 0))
            for i, paciente in enumerate(psi, start=1):
                tk.Label(
                    scrollable_frame,
                    text=f"{i} - {paciente}",
                    bg=cor_fundo,
                    fg="#ECF0F1",
                    font=("Arial", 12),
                ).pack(anchor="w", padx=10, pady=5)

        # Adicionando o canvas e a barra de rolagem à janela
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Função para rolar o canvas com a roda do mouse
        def scroll(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Detectar o sistema operacional
        import sys

        if (
            sys.platform.startswith("win") or sys.platform == "darwin"
        ):  # Windows e MacOS
            janela_informacao.bind_all("<MouseWheel>", scroll)
        else:  # Linux
            janela_informacao.bind_all(
                "<Button-4>", lambda event: canvas.yview_scroll(-1, "units")
            )
            janela_informacao.bind_all(
                "<Button-5>", lambda event: canvas.yview_scroll(1, "units")
            )

        # Remover bindings do mouse quando a janela for fechada
        def on_closing():
            # Removendo os bindings
            janela_informacao.unbind_all("<MouseWheel>")
            janela_informacao.unbind_all("<Button-4>")
            janela_informacao.unbind_all("<Button-5>")
            janela_informacao.destroy()

        janela_informacao.protocol("WM_DELETE_WINDOW", on_closing)
        self.center(janela_informacao)

    def valores_totais(self):
        n_medico, pag_medico = self.planilhas.contar_medico()
        n_psicologo, pag_psicologo = self.planilhas.contar_psi()

        total_medico = n_medico * 148.65
        total_psicologo = n_psicologo * 192.61

        valor_medico = n_medico * 49
        valor_psicologo = n_psicologo * 63.50

        janela_contas = tk.Toplevel(self.master)
        janela_contas.geometry("250x220")
        janela_contas.maxsize(width=250, height=220)
        janela_contas.minsize(width=250, height=220)
        janela_contas.configure(bg="#2C3E50")

        tk.Label(
            janela_contas,
            text="Contas Médico:",
            font=("Arial", 16),
            bg="#2C3E50",
            fg="#ECF0F1",
        ).pack(pady=5)
        tk.Label(
            janela_contas,
            text=f"Valor Total: {total_medico:.2f}",
            bg="#2C3E50",
            fg="#ECF0F1",
            font=("Arial", 12),
        ).pack(pady=2)
        tk.Label(
            janela_contas,
            text=f"Pagar: {valor_medico:.2f}",
            bg="#2C3E50",
            fg="#ECF0F1",
            font=("Arial", 12),
        ).pack(pady=2)
        tk.Label(janela_contas, text="", bg="#2C3E50").pack()

        tk.Label(
            janela_contas,
            text="Contas Psicólogo:",
            font=("Arial", 16),
            bg="#2C3E50",
            fg="#ECF0F1",
        ).pack(pady=5)
        tk.Label(
            janela_contas,
            text=f"Valor Total: {total_psicologo:.2f}",
            bg="#2C3E50",
            fg="#ECF0F1",
            font=("Arial", 12),
        ).pack(pady=2)
        tk.Label(
            janela_contas,
            text=f"Pagar: {valor_psicologo:.2f}",
            bg="#2C3E50",
            fg="#ECF0F1",
            font=("Arial", 12),
        ).pack(pady=2)

        self.center(janela_contas)

    def processar_notas_fiscais(self):
        driver = webdriver.Chrome()
        cpfs = {"medico": [], "psicologo": [], "ambos": []}

        try:
            # Ler o arquivo Excel
            logging.info("Lendo o arquivo Excel")
            df = pd.read_excel(
                self.file_path, skiprows=1, sheet_name="17.10", dtype={"Renach": str}
            )
        except Exception as e:
            logging.error(f"Erro ao ler o arquivo Excel: {e}")
            messagebox.showerror("Erro", f"Erro ao ler o arquivo Excel: {e}")
            return

        # logging.info(f'DataFrame lido: {df.head()}')
        logging.info("DataFrame lido!")

        try:
            renach_c = df.iloc[:, 2].dropna().tolist()
            renach_i = df.iloc[:, 8].dropna().tolist()

            # Acessando o site e fazendo login
            logging.info("Acessando o site do DETRAN e fazendo login")
            driver.get("https://clinicas.detran.ba.gov.br/")
            usuario = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="documento"]'))
            )
            doc = "11599160000115"
            for numero in doc:
                usuario.send_keys(numero)

            actions = ActionChains(driver)
            actions.send_keys(Keys.TAB).perform()
            time.sleep(1)

            senha = "475869"
            campo_senha = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="senha"]'))
            )
            for numero in senha:
                campo_senha.send_keys(numero)

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="acessar"]'))
            ).click()
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/aside/section/ul/li[2]/a/span[1]")
                )
            ).click()
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/aside/section/ul/li[2]/ul/li/a/span")
                )
            ).click()

            barra_pesquisa = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="list_items_filter"]/label/input')
                )
            )

            # coletando informações do cliente
            logging.info("Coletando informações de CPFs")

            def coletar_cpf(dados, tipo):
                for dado in dados:
                    dado = str(dado).strip()
                    barra_pesquisa.clear()
                    barra_pesquisa.send_keys(dado)
                    time.sleep(2)
                    try:
                        paciente = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//*[@id="list_items"]/tbody/tr/td[3]')
                            )
                        )
                        cpf = paciente.text

                        print(f"coletado dado: {dado}, tipo: {tipo}")

                        if tipo == "medico" and dado in renach_i:
                            cpfs["ambos"].append(cpf)
                        elif tipo == "medico":
                            cpfs["medico"].append(cpf)
                        elif tipo == "psicologo" and cpf not in cpfs["ambos"]:
                            cpfs["psicologo"].append(cpf)
                    except Exception as e:
                        logging.error(f"Error ao coletar CPF: {e}")

            coletar_cpf(renach_c, "medico")
            coletar_cpf(renach_i, "psicologo")

            cpfs["medico"] = [cpf for cpf in cpfs["medico"] if cpf not in cpfs["ambos"]]
            cpfs["psicologo"] = [
                cpf for cpf in cpfs["psicologo"] if cpf not in cpfs["ambos"]
            ]

            logging.info("Acessando site para emissão de NTFS-e")
            driver.get("https://nfse.salvador.ba.gov.br/")

            # usuario
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="txtLogin"]'))
            ).send_keys("11599160000115")
            # senha
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="txtSenha"]'))
            ).send_keys("486258camp")
            # esperar resolver o captcha
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.XPATH, '//*[@id="img1"]'))
            )
            # emissao NFS-e
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="menu-lateral"]/li[1]/a')
                )
            ).click()

            def emitir_nota(cpf, tipo):
                try:
                    barra_pesquisa = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[@id="tbCPFCNPJTomador"]')
                        )
                    )
                    barra_pesquisa.clear()
                    barra_pesquisa.send_keys(cpf)
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="btAvancar"]'))
                    ).click()

                    # Complete as informações da nota fiscal
                    role_e_click(driver, '//*[@id="ddlCNAE_chosen"]/a')
                    print("cnae clicada")
                    # opcao cane
                    WebDriverWait(driver, 30).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, '//*[@id="ddlCNAE_chosen"]/div/ul/li[2]')
                        )
                    ).click()
                    print("opcao cnae visivel")
                    # aliq %
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="tbAliquota"]')
                        )
                    ).send_keys("2,5")

                    servicos = {
                        "ambos": "Exame de sanidade física e mental",
                        "psicologo": "Exame de sanidade mental",
                        "medico": "Exame de sanidade física",
                    }
                    # preenchendo o tipo de serviço
                    tipo_servico = servicos.get(
                        tipo, "Exame de sanidade física"
                    )  # valor padrao, caso 'tipo' nao esteja no dicionario

                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="tbDiscriminacao"]')
                        )
                    ).send_keys(tipo_servico)

                    valor_nota = (
                        "148,65"
                        if tipo == "medico"
                        else "192,61" if tipo == "psicolgo" else "341,26"
                    )
                    # valor pago na consulta
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="tbValor"]'))
                    ).send_keys(valor_nota)
                    # emitindo nota
                    WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="btEmitir"]'))
                    ).click()
                    # aceitando o alerta
                    WebDriverWait(driver, 20).until(EC.alert_is_present())
                    alert = Alert(driver)
                    alert.accept()
                    # botao voltar - voltando para emissao de nota fiscal por cpf
                    WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="btVoltar"]'))
                    ).click()
                    logging.info(f"Nota emitida para o CPF: {cpf}, Valor: {valor_nota}")

                except Exception as e:
                    logging.error("Erro ao emitir nota: {e}")

            # emitir notas
            try:
                for cpf in cpfs["medico"]:
                    emitir_nota(cpf, "medico")
                for cpf in cpfs["psicologo"]:
                    emitir_nota(cpf, "psicologo")
                for cpf in cpfs["ambos"]:
                    emitir_nota(cpf, "ambos")
            except Exception as e:
                logging.error(f"Erro na emissao das notas: {e}")
        finally:
            driver.quit()
            logging.info("Processo finalizado")
            return cpfs

    def exibir_resultado(self):
        """Exibe os resultados de contagem para médicos e psicólogos."""
        janela_exibir_resultado = tk.Toplevel(self.master)
        janela_exibir_resultado.geometry("300x210")
        janela_exibir_resultado.maxsize(width=300, height=210)
        janela_exibir_resultado.minsize(width=300, height=210)

        # usando a cor de fundo da janela principal
        cor_fundo = self.master.cget("bg")
        janela_exibir_resultado.configure(bg=cor_fundo)

        n_medico, pag_medico = self.planilhas.contar_medico()
        n_psicologo, pag_psicologo = self.planilhas.contar_psi()

        # Criando rótulos (Labels) e adicionando à janela
        tk.Label(
            janela_exibir_resultado,
            text="MÉDICO:",
            font=("Arial", 16, "bold"),
            bg=cor_fundo,
            fg="#ECF0F1",
        ).pack(pady=(15, 0))
        tk.Label(
            janela_exibir_resultado,
            text=f"Pacientes: {n_medico}",
            font=("Arial", 12),
            bg=cor_fundo,
            fg="#ECF0F1",
        ).pack()

        # Formatando as formas de pagamento
        texto_med = "  ".join(
            [
                f"{tipo_pagamento}: {quantidade}"
                for tipo_pagamento, quantidade in pag_medico.items()
            ]
        )
        label = tk.Label(
            janela_exibir_resultado,
            text=texto_med,
            font=("Arial", 12),
            bg=cor_fundo,
            fg="#ECF0F1",
        )
        label.pack()  # Adicionando o label com as formas de pagamento

        # Se você também quiser exibir informações sobre psicólogos, adicione aqui:
        tk.Label(
            janela_exibir_resultado,
            text="PSICÓLOGO:",
            font=("Arial", 16, "bold"),
            bg=cor_fundo,
            fg="#ECF0F1",
        ).pack(pady=(20, 0))
        tk.Label(
            janela_exibir_resultado,
            text=f"Pacientes: {n_psicologo}",
            font=("Arial", 12),
            bg=cor_fundo,
            fg="#ECF0F1",
        ).pack()

        texto_psic = "  ".join(
            [
                f"{tipo_pagamento}: {quantidade}"
                for tipo_pagamento, quantidade in pag_psicologo.items()
            ]
        )
        label_psic = tk.Label(
            janela_exibir_resultado,
            text=texto_psic,
            font=("Arial", 12),
            bg=cor_fundo,
            fg="#ECF0F1",
        )
        label_psic.pack()  # Adicionando o label com as formas de pagamento dos psicólogos

        self.center(janela_exibir_resultado)

    def enviar_whatsapp(self):
        # Janela número ou nome do grupo
        janela_wpp = tk.Toplevel(self.master)
        janela_wpp.geometry("300x210")
        cor_fundo = self.master.cget("bg")
        janela_wpp.configure(bg=cor_fundo)
        self.center(janela_wpp)

        tk.Label(
            janela_wpp,
            text="Enviar para:",
            font=("Arial", 16, "bold"),
            bg=cor_fundo,
            fg="#ECF0F1",
        ).pack(anchor="center", padx=5, pady=5)

        self.wpp_entry = tk.Entry(janela_wpp)
        self.wpp_entry.pack(padx=5, pady=5)

        # Checkbutton para salvar as informações
        tk.Button(
            janela_wpp, text="Enviar", command=self.processar_envio_whatsapp
        ).pack(pady=10)

    def processar_envio_whatsapp(self):
        # Captura o valor do campo de entrada
        group_name = self.wpp_entry.get().strip()

        if not group_name:
            messagebox.showerror("Erro", "Insira um número, grupo ou nome")
            return

        # Preparar as informações para enviar a mensagem
        n_medico, pag_medico = self.planilhas.contar_medico()
        n_psicologo, pag_psicologo = self.planilhas.contar_psi()

        valor_medico = n_medico * 49
        valor_psicologo = n_psicologo * 63.50

        message_medico = f"Valor medico: {valor_medico}"
        message_psicologo = f"Valor psicologo: {valor_psicologo}"

        dir_path = os.getcwd()
        profile = os.path.join(dir_path, "profile", "wpp")

        # Configurar opções do Chrome
        logging.info("Configurando Chrome...")
        options = Options()
        options.add_argument(r"user-data-dir={}".format(profile))
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Inicializar o WebDriver
        logging.info("Inicializando o WebDriver...")
        service = Service(executable_path="/usr/local/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)

        # Acessar o WhatsApp Web
        logging.info("Abrindo WhatsApp...")
        driver.get("https://web.whatsapp.com/")

        # Aguardar até que a página esteja totalmente carregada
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
            )
        except Exception as e:
            messagebox.showerror("Erro" f"Erro ao esnaear QR Code: {e}")
            logging.error(f"Erro ao escanear QR Code: {e}")
            driver.quit()
            return

        # Selecionar o grupo
        try:
            logging.info("Enviando mensagem...")
            barra_pesquisa = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div/p')
                )
            )
            barra_pesquisa.send_keys(group_name)
            time.sleep(1)
            barra_pesquisa.send_keys(Keys.ENTER)
        except Exception as e:
            messagebox.showerror(f"Erro ao selecionar grupo: {e}")
            logging.error(f"Erro ao seleconar o grupo: {e}")
            driver.quit()
            return

        # Enviar a mensagem
        try:
            logging.info("Enviando mensagem...")
            enviar_mensagem = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]/p',
                    )
                )
            )
            enviar_mensagem.send_keys(message_medico)
            time.sleep(1)
            enviar_mensagem.send_keys(Keys.ENTER)

            enviar_mensagem = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]/p',
                    )
                )
            )
            enviar_mensagem.send_keys(message_psicologo)
            time.sleep(1)
            enviar_mensagem.send_keys(Keys.ENTER)
            messagebox.showinfo("Mensagens enviadas")

            time.sleep(7)
        except Exception as e:
            messagebox.showerror(f"Erro ao enviar as mensagens: {e}")
        finally:
            driver.quit()

    def enviar_email(self):
        janela_email = tk.Toplevel(self.master)
        janela_email.geometry("300x400")
        cor_fundo = self.master.cget("bg")
        janela_email.configure(bg=cor_fundo)
        self.center(janela_email)

        tk.Label(
            janela_email,
            text="Email:",
            bg=cor_fundo,
            fg="#ECF0F1",
            font=("Arial", 14, "bold"),
        ).pack(pady=5)
        entry_email = tk.Entry(janela_email)
        entry_email.pack(pady=5)

        tk.Label(
            janela_email,
            text="Senha:",
            bg=cor_fundo,
            fg="#ECF0F1",
            font=("Arial", 14, "bold"),
        ).pack(pady=5)
        entry_senha = tk.Entry(janela_email, show="*")  # Ocultar senha
        entry_senha.pack(pady=5)

        tk.Label(
            janela_email,
            text="Destinatário:",
            bg=cor_fundo,
            fg="#ECF0F1",
            font=("Arial", 14, "bold"),
        ).pack(pady=5)
        entry_destinatario = tk.Entry(janela_email)
        entry_destinatario.pack(pady=5)

        tk.Label(
            janela_email,
            text="Assunto:",
            bg=cor_fundo,
            fg="#ECF0F1",
            font=("Arial", 14, "bold"),
        ).pack(pady=5)
        entry_assunto = tk.Entry(janela_email)
        entry_assunto.pack(pady=5)

        tk.Button(
            janela_email,
            text="Selecionar XLSX",
            command=lambda: self.selecionar_xlsx(
                entry_email.get(), 
                entry_senha.get(), 
                entry_destinatario.get(),
                entry_assunto.get()
            ),
        ).pack(pady=20)

    def selecionar_xlsx(self, email, senha, destinatario, assunto):
        """
        Abre diálogo para selecionar arquivo XLSX
        """
        if not all([email, senha, destinatario, assunto]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        arquivo_xlsx = filedialog.askopenfilename(
            title="Selecione o arquivo XLSX",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls")]
        )

        if arquivo_xlsx:
            self.enviar(
                email, 
                senha, 
                destinatario, 
                assunto, 
                arquivo_xlsx
            )

    def enviar(self, email, senha, destinatario, assunto, caminho_xlsx):
        """
        Envia e-mail com arquivo XLSX anexado
        """
        smtp_server = "smtp.gmail.com"  # Para Gmail
        smtp_port = 587

        try:
            # Criando a mensagem
            msg = MIMEMultipart()
            msg["From"] = email
            msg["To"] = destinatario
            msg["Subject"] = assunto

            # Corpo do e-mail padrão
            corpo = "Segue em anexo o arquivo XLSX conforme solicitado."
            msg.attach(MIMEText(corpo, "plain"))

            # Anexar arquivo XLSX
            with open(caminho_xlsx, "rb") as arquivo:
                parte_xlsx = MIMEApplication(arquivo.read(), _subtype="xlsx")
                parte_xlsx.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename=os.path.basename(caminho_xlsx)
                )
                msg.attach(parte_xlsx)

            # Contexto SSL para conexão segura
            context = ssl.create_default_context()

            # Enviando o e-mail
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)  # Inicia a segurança TLS
                server.login(email, senha)  # Faz login no servidor
                server.send_message(msg)  # Envia a mensagem
            
            # Mensagem de sucesso
            messagebox.showinfo(
                "Sucesso", 
                f"E-mail enviado com sucesso para {destinatario}!\nAnexo: {os.path.basename(caminho_xlsx)}"
            )

        except smtplib.SMTPAuthenticationError:
            messagebox.showerror(
                "Erro de Autenticação", 
                "Verifique seu email e senha. Use uma senha de aplicativo para o Gmail."
            )
        except Exception as e:
            messagebox.showerror(
                "Erro ao Enviar", 
                f"Ocorreu um erro: {str(e)}"
            )  

    def configurar_frames(self, login_frame, criar_conta_frame):
        self.login_frame = login_frame
        self.criar_conta_frame = criar_conta_frame

    def mostrar_criar_conta(self):
        self.login_frame.grid_forget()
        self.criar_conta_frame.grid()

    def voltar_para_login(self):
        self.criar_conta_frame.grid_forget()
        self.login_frame.grid()



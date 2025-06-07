import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from typing import List, Tuple, Optional
import os

class Banco:
    def __init__(self, arquivo_db="notas_alunos.db"):
        # VERIFICAR BANCO
        self.arquivo_db = arquivo_db
        self.conexao = sqlite3.connect(self.arquivo_db)
        self.cursor = self.conexao.cursor()
        self.criar_tabelas()
    
    def criar_tabelas(self):
        # TABELA DE ALUNOS
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            matricula TEXT PRIMARY KEY,
            nome TEXT NOT NULL
        )
        ''')
        
        # TABELA DE NOTAS
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disciplina TEXT NOT NULL,
            valor REAL NOT NULL,
            aluno_matricula TEXT NOT NULL,
            FOREIGN KEY (aluno_matricula) REFERENCES alunos (matricula),
            UNIQUE(disciplina, aluno_matricula)
        )
        ''')
        
        self.conexao.commit()
    
    def cadastrar_aluno(self, matricula: str, nome: str) -> bool:
        try:
            self.cursor.execute("INSERT INTO alunos VALUES (?, ?)", (matricula, nome))
            self.conexao.commit()
            return True
        except sqlite3.IntegrityError:
            # TESTA CHAVE DUPLICADA
            return False
        except Exception as e:
            print(f"Erro ao cadastrar aluno: {e}")
            return False
    
    def cadastrar_nota(self, disciplina: str, valor: float, aluno_matricula: str) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO notas (disciplina, valor, aluno_matricula) VALUES (?, ?, ?)",
                (disciplina, valor, aluno_matricula)
            )
            self.conexao.commit()
            return True
        except sqlite3.IntegrityError:
            # ERRO CHAVE DUPLICADA (ALUNO JÁ TEM ESSA DISCIPLINA)
            return False
        except Exception as e:
            print(f"Erro ao cadastrar nota: {e}")
            return False
    
    def excluir_aluno(self, matricula: str) -> bool:
        try:
            # EXCLUINDO DISCIPLINAS
            self.cursor.execute("DELETE FROM notas WHERE aluno_matricula = ?", (matricula,))
            
            # EXCLUINDO ALUNO
            self.cursor.execute("DELETE FROM alunos WHERE matricula = ?", (matricula,))
            
            self.conexao.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir aluno: {e}")
            return False
    
    def excluir_nota(self, disciplina: str, aluno_matricula: str) -> bool:
        try:
            self.cursor.execute(
                "DELETE FROM notas WHERE disciplina = ? AND aluno_matricula = ?", 
                (disciplina, aluno_matricula)
            )
            self.conexao.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir nota: {e}")
            return False
    
    def buscar_aluno(self, matricula: str) -> Optional[Tuple[str, str]]:
        try:
            self.cursor.execute("SELECT matricula, nome FROM alunos WHERE matricula = ?", (matricula,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar aluno: {e}")
            return None
    
    def listar_alunos(self) -> List[Tuple[str, str]]:
        try:
            self.cursor.execute("SELECT matricula, nome FROM alunos ORDER BY nome")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar alunos: {e}")
            return []
    
    def buscar_notas_aluno(self, matricula: str) -> List[Tuple[str, float]]:
        try:
            self.cursor.execute(
                "SELECT disciplina, valor FROM notas WHERE aluno_matricula = ? ORDER BY disciplina",
                (matricula,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar notas do aluno: {e}")
            return []
    
    def fechar(self):
        if self.conexao:
            self.conexao.close()


class Aplicacao:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Cadastro e Consulta de Notas")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # INICIANDO BANCCO DE DADOS
        self.banco = Banco()
        
        # CRIANDO ABAS
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # CRIANDO ABAS
        self.tab_cadastro_aluno = ttk.Frame(self.notebook)
        self.tab_cadastro_nota = ttk.Frame(self.notebook)
        self.tab_consulta = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_cadastro_aluno, text="Cadastro de Alunos")
        self.notebook.add(self.tab_cadastro_nota, text="Cadastro de Notas")
        self.notebook.add(self.tab_consulta, text="Consulta de Notas")
        
        # CONBFIGURANDO ABAS
        self.configurar_aba_cadastro_aluno()
        self.configurar_aba_cadastro_nota()
        self.configurar_aba_consulta()
        
        # INICIANDO TABELAS E COMBOBOX
        self.atualizar_tabela_alunos()
        self.atualizar_combobox_alunos()
        self.atualizar_combobox_consulta()
        
        # CONFIGURANDO FECHAMENTO
        self.root.protocol("WM_DELETE_WINDOW", self.fechar)
    
    def configurar_aba_cadastro_aluno(self):
        frame = ttk.LabelFrame(self.tab_cadastro_aluno, text="Dados do Aluno")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # MATRÍCULA
        ttk.Label(frame, text="Matrícula:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_matricula = ttk.Entry(frame, width=30)
        self.entry_matricula.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # NOME
        ttk.Label(frame, text="Nome:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_nome = ttk.Entry(frame, width=50)
        self.entry_nome.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # BOTÕES
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=2, column=0, columnspan=2, padx=10, pady=20)
        
        btn_cadastrar = ttk.Button(frame_botoes, text="Cadastrar Aluno", command=self.cadastrar_aluno)
        btn_cadastrar.pack(side=tk.LEFT, padx=5)
        
        btn_excluir = ttk.Button(frame_botoes, text="Excluir Aluno", command=self.excluir_aluno)
        btn_excluir.pack(side=tk.LEFT, padx=5)
        
        # LISTA DE ALUNOS CADASTRADOS
        ttk.Label(frame, text="Alunos Cadastrados:").grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # TABELA DE ALUNOS
        colunas = ("Matrícula", "Nome")
        self.tabela_alunos = ttk.Treeview(frame, columns=colunas, show="headings", height=10)
        
        for col in colunas:
            self.tabela_alunos.heading(col, text=col)
            self.tabela_alunos.column(col, width=100)
        
        self.tabela_alunos.column("Nome", width=300)
        self.tabela_alunos.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # SELEÇÃO DE TABELA
        self.tabela_alunos.bind("<<TreeviewSelect>>", self.selecionar_aluno)
        
        # SCROLLBAR PARA TABELA
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tabela_alunos.yview)
        scrollbar.grid(row=4, column=2, sticky="ns")
        self.tabela_alunos.configure(yscrollcommand=scrollbar.set)
        
        # EXPANSÃO DE TABELA
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
    
    def configurar_aba_cadastro_nota(self):
        frame = ttk.LabelFrame(self.tab_cadastro_nota, text="Cadastro de Notas")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # SELECIONANDO ALUNO
        ttk.Label(frame, text="Aluno:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.combo_alunos_notas = ttk.Combobox(frame, width=50, state="readonly")
        self.combo_alunos_notas.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.combo_alunos_notas.bind("<<ComboboxSelected>>", self.exibir_notas_aluno)
        
        # DISCIPLINA
        ttk.Label(frame, text="Disciplina:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_disciplina = ttk.Entry(frame, width=30)
        self.entry_disciplina.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # VALOR NOTA
        ttk.Label(frame, text="Valor da Nota:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_nota = ttk.Entry(frame, width=10)
        self.entry_nota.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # BOTÕES
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=3, column=0, columnspan=2, padx=10, pady=20)
        
        btn_cadastrar = ttk.Button(frame_botoes, text="Cadastrar Nota", command=self.cadastrar_nota)
        btn_cadastrar.pack(side=tk.LEFT, padx=5)
        
        btn_excluir = ttk.Button(frame_botoes, text="Excluir Nota", command=self.excluir_nota)
        btn_excluir.pack(side=tk.LEFT, padx=5)
        
        # NOTAS DO ALUNO SELECIONADO
        ttk.Label(frame, text="Notas do Aluno:").grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # TABELA DE NOTAS
        colunas = ("Disciplina", "Valor")
        self.tabela_notas = ttk.Treeview(frame, columns=colunas, show="headings", height=10)
        
        for col in colunas:
            self.tabela_notas.heading(col, text=col)
            self.tabela_notas.column(col, width=150)
        
        self.tabela_notas.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # SELEÇÃO DE TABELA
        self.tabela_notas.bind("<<TreeviewSelect>>", self.selecionar_nota)
        
        # SCROLLBAR PARA TABELA
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tabela_notas.yview)
        scrollbar.grid(row=5, column=2, sticky="ns")
        self.tabela_notas.configure(yscrollcommand=scrollbar.set)
        
        # EXPANSÃO DE TABELA
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)
    
    def configurar_aba_consulta(self):
        frame = ttk.LabelFrame(self.tab_consulta, text="Consulta de Notas por Aluno")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # SELEÇÃO DE ALUNO
        ttk.Label(frame, text="Selecione o Aluno:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.combo_alunos_consulta = ttk.Combobox(frame, width=50, state="readonly")
        self.combo_alunos_consulta.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.combo_alunos_consulta.bind("<<ComboboxSelected>>", self.consultar_notas_aluno)
        
        # TABELA DE NOTA DE ALUNO
        ttk.Label(frame, text="Notas do Aluno:").grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        colunas = ("Disciplina", "Valor")
        self.tabela_consulta = ttk.Treeview(frame, columns=colunas, show="headings", height=15)
        
        for col in colunas:
            self.tabela_consulta.heading(col, text=col)
            self.tabela_consulta.column(col, width=150)
        
        self.tabela_consulta.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # SCROLLBAR PARA TABELA
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tabela_consulta.yview)
        scrollbar.grid(row=2, column=2, sticky="ns")
        self.tabela_consulta.configure(yscrollcommand=scrollbar.set)
        
        # EXPANSÃO DE TABELA
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
    
    def selecionar_aluno(self, event):
        # PUXAR ITEM SELECIONADO DA TABELA
        selecao = self.tabela_alunos.selection()
        if not selecao:
            return
        
        # PUXAR O VALOR DO ITEM SELECIONADO DA TABELA
        item = self.tabela_alunos.item(selecao[0])
        matricula, nome = item['values']
        
        # PREENCHE COM OS VALORES DO ALUNO SELECIONADO
        self.entry_matricula.delete(0, tk.END)
        self.entry_matricula.insert(0, matricula)
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, nome)
    
    def selecionar_nota(self, event):
        # PUXA O ITEM SELECCIONADO DA TABELA NOTAS
        selecao = self.tabela_notas.selection()
        if not selecao:
            return
        
        # PUXA OS VALORES SELECIONADOS DA TABELA
        item = self.tabela_notas.item(selecao[0])
        disciplina, valor = item['values']
        
        # PREENCHE COM OS VALORES DA NOTA SELECIONADA
        self.entry_disciplina.delete(0, tk.END)
        self.entry_disciplina.insert(0, disciplina)
        self.entry_nota.delete(0, tk.END)
        self.entry_nota.insert(0, str(valor))
    
    def cadastrar_aluno(self):
        matricula = self.entry_matricula.get().strip()
        nome = self.entry_nome.get().strip()
        
        if not matricula or not nome:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        # VERIFICAÇÃO DE ALUNO JÁ EXISTENTE NO BANCO
        
        if self.banco.cadastrar_aluno(matricula, nome):
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
            self.entry_matricula.delete(0, tk.END)
            self.entry_nome.delete(0, tk.END)
            self.atualizar_tabela_alunos()
            self.atualizar_combobox_alunos()
            self.atualizar_combobox_consulta()
        else:
            messagebox.showerror("Erro", f"Já existe um aluno com a matrícula {matricula}!")
    
    def excluir_aluno(self):
        # VERIFICA ALUNO EXISTENTE NA TABELA
        selecao = self.tabela_alunos.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um aluno para excluir!")
            return
        
        # PUXA OS DADOS DO ALUNO SELECIONADO
        item = self.tabela_alunos.item(selecao[0])
        matricula, nome = item['values']
        
        # CONFIRMAÇÃO DE EXCLUSÃO
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o aluno {nome} (Matrícula: {matricula})?\n\n" +
            "ATENÇÃO: Todas as notas deste aluno também serão excluídas!"
        )
        
        if resposta:
            if self.banco.excluir_aluno(matricula):
                messagebox.showinfo("Sucesso", f"Aluno {nome} excluído com sucesso!")
                self.entry_matricula.delete(0, tk.END)
                self.entry_nome.delete(0, tk.END)
                self.atualizar_tabela_alunos()
                self.atualizar_combobox_alunos()
                self.atualizar_combobox_consulta()
            else:
                messagebox.showerror("Erro", f"Erro ao excluir o aluno {nome}!")
    
    def cadastrar_nota(self):
        if not self.combo_alunos_notas.get():
            messagebox.showerror("Erro", "Selecione um aluno!")
            return
        
        disciplina = self.entry_disciplina.get().strip()
        if not disciplina:
            messagebox.showerror("Erro", "Informe a disciplina!")
            return
        
        try:
            valor_nota = float(self.entry_nota.get().replace(',', '.'))
            if valor_nota < 0 or valor_nota > 10:
                messagebox.showerror("Erro", "A nota deve estar entre 0 e 10!")
                return
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor de nota válido!")
            return
        
        matricula = self.combo_alunos_notas.get().split(" - ")[0]
        
        # VERIFICAÇÃO DE NOTA DUPLICADA NO BANCO
        
        if self.banco.cadastrar_nota(disciplina, valor_nota, matricula):
            # LIMPAR CAMPO E ATUALIZAR TABELA
            self.entry_disciplina.delete(0, tk.END)
            self.entry_nota.delete(0, tk.END)
            self.exibir_notas_aluno(None)
            
            # CURSOR PERSISTENTE EM DISCIPLINA
            self.entry_disciplina.focus_set()
            
            # ATUALIZAR ALUNO NA VISUALIZAÇÃO
            if self.combo_alunos_consulta.get() and self.combo_alunos_consulta.get().split(" - ")[0] == matricula:
                self.consultar_notas_aluno(None)
        else:
            messagebox.showerror("Erro", f"Já existe uma nota para a disciplina '{disciplina}' para este aluno!")
    
    def excluir_nota(self):
        # VERIFICA ALUNO NO COMBOX
        if not self.combo_alunos_notas.get():
            messagebox.showwarning("Aviso", "Selecione um aluno!")
            return
        
        # VERIFICA SE TEM NOTA SELECIONADA NA TABELA
        selecao = self.tabela_notas.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma nota para excluir!")
            return
        
        # PUXA OS DADOS DA NOS SELECIONADA
        item = self.tabela_notas.item(selecao[0])
        disciplina, valor = item['values']
        
        # PUXA A MATRÍCULA DO ALUNO SELECIONADO
        matricula = self.combo_alunos_notas.get().split(" - ")[0]
        
        # CONFIRMA EXCCLUSÃO
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir a nota da disciplina '{disciplina}' (Valor: {valor})?"
        )
        
        if resposta:
            if self.banco.excluir_nota(disciplina, matricula):
                messagebox.showinfo("Sucesso", f"Nota da disciplina '{disciplina}' excluída com sucesso!")
                self.entry_disciplina.delete(0, tk.END)
                self.entry_nota.delete(0, tk.END)
                self.exibir_notas_aluno(None)
                
                # ATUALIZAR ALUNO NA VISUALIZAÇÃO
                if self.combo_alunos_consulta.get() and self.combo_alunos_consulta.get().split(" - ")[0] == matricula:
                    self.consultar_notas_aluno(None)
            else:
                messagebox.showerror("Erro", f"Erro ao excluir a nota da disciplina '{disciplina}'!")
    
    def atualizar_tabela_alunos(self):
        # LIMPAR TABELA
        for item in self.tabela_alunos.get_children():
            self.tabela_alunos.delete(item)
        
        # PREENCHER COM BANDO DE DADOS
        for aluno in self.banco.listar_alunos():
            self.tabela_alunos.insert("", "end", values=aluno)
    
    def atualizar_combobox_alunos(self):
        alunos = self.banco.listar_alunos()
        opcoes = [f"{a[0]} - {a[1]}" for a in alunos]
        self.combo_alunos_notas['values'] = opcoes
        
        # SELECIONAR PRIMEIRO ITEM
        if opcoes:
            self.combo_alunos_notas.current(0)
            self.exibir_notas_aluno(None)
    
    def atualizar_combobox_consulta(self):
        alunos = self.banco.listar_alunos()
        opcoes = [f"{a[0]} - {a[1]}" for a in alunos]
        self.combo_alunos_consulta['values'] = opcoes
        
        # SELECIONAR O PRIMEIRO ITEM
        if opcoes:
            self.combo_alunos_consulta.current(0)
            self.consultar_notas_aluno(None)
    
    def exibir_notas_aluno(self, event):
        if not self.combo_alunos_notas.get():
            return
        
        matricula = self.combo_alunos_notas.get().split(" - ")[0]
        
        # LIMPAR TABELA
        for item in self.tabela_notas.get_children():
            self.tabela_notas.delete(item)
        
        # PREENCHER COM DADOS DO ALUNO
        notas = self.banco.buscar_notas_aluno(matricula)
        for nota in notas:
            self.tabela_notas.insert("", "end", values=nota)
    
    def consultar_notas_aluno(self, event):
        if not self.combo_alunos_consulta.get():
            return
        
        matricula = self.combo_alunos_consulta.get().split(" - ")[0]
        
        # LIMPAR TABELA
        for item in self.tabela_consulta.get_children():
            self.tabela_consulta.delete(item)
        
        # PREENCHER COM DADOS DO ALUNO
        notas = self.banco.buscar_notas_aluno(matricula)
        for nota in notas:
            self.tabela_consulta.insert("", "end", values=nota)
    
    def fechar(self):
        # COMO O PROFESSOR ENSINOU FECHAR CONEXÃO COM O BANCO DE DADOS
        self.banco.fechar()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacao(root)
    root.mainloop()
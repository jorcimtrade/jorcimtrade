import sqlite3
import hashlib
import os
from datetime import datetime

def criar_banco_dados():
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nome_completo TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabela de vendas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        produto TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unitario REAL NOT NULL,
        total REAL NOT NULL,
        data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')
    
    # Tabela de anotações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anotacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        titulo TEXT NOT NULL,
        conteudo TEXT NOT NULL,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        data_modificacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')
    
    conn.commit()
    conn.close()

criar_banco_dados()

class SistemaAutenticacao:
    def __init__(self):
        self.conn = sqlite3.connect('sistema_vendas.db')
        self.usuario_logado = None
    
    def hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def cadastrar_usuario(self, username, senha, nome_completo, email):
        try:
            cursor = self.conn.cursor()
            password_hash = self.hash_senha(senha)
            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, nome_completo, email)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, nome_completo, email))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def login(self, username, senha):
        cursor = self.conn.cursor()
        password_hash = self.hash_senha(senha)
        cursor.execute('''
            SELECT id, username, nome_completo FROM usuarios 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        usuario = cursor.fetchone()
        if usuario:
            self.usuario_logado = {
                'id': usuario[0],
                'username': usuario[1],
                'nome_completo': usuario[2]
            }
            return True
        return False
    
    def logout(self):
        self.usuario_logado = None
    
    def __del__(self):
        self.conn.close()

class SistemaVendas:
    def __init__(self):
        self.conn = sqlite3.connect('sistema_vendas.db')
    
    def registrar_venda(self, usuario_id, produto, quantidade, preco_unitario):
        try:
            cursor = self.conn.cursor()
            total = quantidade * preco_unitario
            cursor.execute('''
                INSERT INTO vendas (usuario_id, produto, quantidade, preco_unitario, total)
                VALUES (?, ?, ?, ?, ?)
            ''', (usuario_id, produto, quantidade, preco_unitario, total))
            self.conn.commit()
            return cursor.lastrowid
        except:
            return None
    
    def listar_vendas(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, produto, quantidade, preco_unitario, total, data_venda
            FROM vendas WHERE usuario_id = ? ORDER BY data_venda DESC
        ''', (usuario_id,))
        return cursor.fetchall()
    
    def total_vendas(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(total) FROM vendas WHERE usuario_id = ?', (usuario_id,))
        return cursor.fetchone()[0] or 0
    
    def __del__(self):
        self.conn.close()
class SistemaAnotacoes:
    def __init__(self):
        self.conn = sqlite3.connect('sistema_vendas.db')
    
    def criar_anotacao(self, usuario_id, titulo, conteudo):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO anotacoes (usuario_id, titulo, conteudo)
                VALUES (?, ?, ?)
            ''', (usuario_id, titulo, conteudo))
            self.conn.commit()
            return cursor.lastrowid
        except:
            return None
    
    def listar_anotacoes(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, titulo, conteudo, data_criacao, data_modificacao
            FROM anotacoes WHERE usuario_id = ? ORDER BY data_modificacao DESC
        ''', (usuario_id,))
        return cursor.fetchall()
    
    def editar_anotacao(self, anotacao_id, titulo, conteudo, usuario_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE anotacoes 
                SET titulo = ?, conteudo = ?, data_modificacao = CURRENT_TIMESTAMP
                WHERE id = ? AND usuario_id = ?
            ''', (titulo, conteudo, anotacao_id, usuario_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except:
            return False
    
    def excluir_anotacao(self, anotacao_id, usuario_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM anotacoes WHERE id = ? AND usuario_id = ?', 
                          (anotacao_id, usuario_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except:
            return False
    
    def __del__(self):
        self.conn.close()
import tkinter as tk
from tkinter import ttk, messagebox

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Vendas e Anotações - Login")
        self.root.geometry("400x300")
        
        self.auth = SistemaAutenticacao()
        self.vendas = SistemaVendas()
        self.anotacoes = SistemaAnotacoes()
        
        self.criar_widgets_login()
    
    def criar_widgets_login(self):
        # Frame principal
        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        ttk.Label(frame, text="Login", font=('Arial', 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Campos de entrada
        ttk.Label(frame, text="Usuário:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_usuario = ttk.Entry(frame, width=25)
        self.entry_usuario.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Senha:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_senha = ttk.Entry(frame, width=25, show="*")
        self.entry_senha.grid(row=2, column=1, pady=5)
        
        # Botões
        ttk.Button(frame, text="Entrar", command=self.fazer_login).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Cadastrar", command=self.abrir_cadastro).grid(row=4, column=0, columnspan=2, pady=5)
    
    def fazer_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()
        
        if self.auth.login(usuario, senha):
            self.abrir_dashboard()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")
    
    def abrir_cadastro(self):
        CadastroWindow(self)
    
    def abrir_dashboard(self):
        self.root.withdraw()
        dashboard = tk.Toplevel(self.root)
        DashboardApp(dashboard, self.auth, self.vendas, self.anotacoes)
        dashboard.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)

    def fechar_aplicacao(self):
        self.root.quit()

class CadastroWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("Cadastro")
        self.window.geometry("400x400")
        
        self.criar_widgets_cadastro()
    
    def criar_widgets_cadastro(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Cadastro", font=('Arial', 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        campos = [
            ("Usuário:", "entry_usuario"),
            ("Senha:", "entry_senha", True),
            ("Confirmar Senha:", "entry_confirmar_senha", True),
            ("Nome Completo:", "entry_nome"),
            ("Email:", "entry_email")
        ]
        
        for i, (label, attr, *args) in enumerate(campos, 1):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame, width=25, show="*" if args and args[0] else "")
            entry.grid(row=i, column=1, pady=5)
            setattr(self, attr, entry)
        
        ttk.Button(frame, text="Cadastrar", command=self.cadastrar).grid(row=6, column=0, columnspan=2, pady=10)
    
    def cadastrar(self):
        # Validação dos campos
        if self.entry_senha.get() != self.entry_confirmar_senha.get():
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return
        
        if self.parent.auth.cadastrar_usuario(
            self.entry_usuario.get(),
            self.entry_senha.get(),
            self.entry_nome.get(),
            self.entry_email.get()
        ):
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            self.window.destroy()
        else:
            messagebox.showerror("Erro", "Erro ao cadastrar usuário!")

class DashboardApp:
    def __init__(self, root, auth, vendas, anotacoes):
        self.root = root
        self.root.title("Dashboard - Sistema de Vendas e Anotações")
        self.root.geometry("800x600")
        
        self.auth = auth
        self.vendas = vendas
        self.anotacoes = anotacoes
        
        self.criar_widgets_dashboard()
    
    def criar_widgets_dashboard(self):
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba de Vendas
        frame_vendas = ttk.Frame(self.notebook)
        self.notebook.add(frame_vendas, text="Vendas")
        self.criar_aba_vendas(frame_vendas)
        
        # Aba de Anotações
        frame_anotacoes = ttk.Frame(self.notebook)
        self.notebook.add(frame_anotacoes, text="Anotações")
        self.criar_aba_anotacoes(frame_anotacoes)
        
        # Botão de logout
        ttk.Button(self.root, text="Logout", command=self.logout).pack(pady=10)
    
    def criar_aba_vendas(self, frame):
        # Formulário de venda
        form_frame = ttk.LabelFrame(frame, text="Nova Venda", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Produto:").grid(row=0, column=0, sticky=tk.W)
        self.entry_produto = ttk.Entry(form_frame, width=30)
        self.entry_produto.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Quantidade:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.entry_quantidade = ttk.Spinbox(form_frame, from_=1, to=1000, width=10)
        self.entry_quantidade.grid(row=0, column=3, padx=5)
        
        ttk.Label(form_frame, text="Preço Unitário:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.entry_preco = ttk.Entry(form_frame, width=15)
        self.entry_preco.grid(row=1, column=1, padx=5, pady=10)
        
        ttk.Button(form_frame, text="Registrar Venda", command=self.registrar_venda).grid(row=1, column=2, columnspan=2, pady=10)
        
        # Lista de vendas
        list_frame = ttk.LabelFrame(frame, text="Vendas Registradas", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ('ID', 'Produto', 'Quantidade', 'Preço', 'Total', 'Data')
        self.tree_vendas = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree_vendas.heading(col, text=col)
            self.tree_vendas.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_vendas.yview)
        self.tree_vendas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_vendas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Total
        total_frame = ttk.Frame(frame)
        total_frame.pack(fill=tk.X, padx=10, pady=5)
        self.label_total = ttk.Label(total_frame, text="Total de Vendas: R$ 0.00", font=('Arial', 12, 'bold'))
        self.label_total.pack()
        
        self.carregar_vendas()
    
    def criar_aba_anotacoes(self, frame):
        # Formulário de anotação
        form_frame = ttk.LabelFrame(frame, text="Nova Anotação", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Título:").grid(row=0, column=0, sticky=tk.W)
        self.entry_titulo = ttk.Entry(form_frame, width=40)
        self.entry_titulo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Conteúdo:").grid(row=1, column=0, sticky=tk.NW, pady=10)
        self.text_conteudo = tk.Text(form_frame, width=50, height=5)
        self.text_conteudo.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)
        
        ttk.Button(form_frame, text="Salvar Anotação", command=self.salvar_anotacao).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Lista de anotações
        list_frame = ttk.LabelFrame(frame, text="Anotações", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ('ID', 'Título', 'Criação', 'Modificação')
        self.tree_anotacoes = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree_anotacoes.heading(col, text=col)
            self.tree_anotacoes.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_anotacoes.yview)
        self.tree_anotacoes.configure(yscrollcommand=scrollbar.set)
        
        self.tree_anotacoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões de ação
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(action_frame, text="Editar", command=self.editar_anotacao).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Excluir", command=self.excluir_anotacao).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Visualizar", command=self.visualizar_anotacao).pack(side=tk.LEFT, padx=5)
        
        self.carregar_anotacoes()
    
    def registrar_venda(self):
        try:
            produto = self.entry_produto.get()
            quantidade = int(self.entry_quantidade.get())
            preco = float(self.entry_preco.get())
            
            if produto and quantidade > 0 and preco > 0:
                venda_id = self.vendas.registrar_venda(
                    self.auth.usuario_logado['id'],
                    produto,
                    quantidade,
                    preco
                )
                
                if venda_id:
                    messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
                    self.entry_produto.delete(0, tk.END)
                    self.entry_quantidade.delete(0, tk.END)
                    self.entry_preco.delete(0, tk.END)
                    self.carregar_vendas()
                else:
                    messagebox.showerror("Erro", "Erro ao registrar venda!")
            else:
                messagebox.showwarning("Aviso", "Preencha todos os campos corretamente!")
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos!")
    
    def salvar_anotacao(self):
        titulo = self.entry_titulo.get()
        conteudo = self.text_conteudo.get("1.0", tk.END).strip()
        
        if titulo and conteudo:
            anotacao_id = self.anotacoes.criar_anotacao(
                self.auth.usuario_logado['id'],
                titulo,
                conteudo
            )
            
            if anotacao_id:
                messagebox.showinfo("Sucesso", "Anotação salva com sucesso!")
                self.entry_titulo.delete(0, tk.END)
                self.text_conteudo.delete("1.0", tk.END)
                self.carregar_anotacoes()
            else:
                messagebox.showerror("Erro", "Erro ao salvar anotação!")
        else:
            messagebox.showwarning("Aviso", "Preencha título e conteúdo!")
    
    def carregar_vendas(self):
        # Limpar treeview
        for item in self.tree_vendas.get_children():
            self.tree_vendas.delete(item)
        
        # Carregar vendas
        vendas = self.vendas.listar_vendas(self.auth.usuario_logado['id'])
        for venda in vendas:
            self.tree_vendas.insert('', 'end', values=(
                venda[0], venda[1], venda[2], 
                f"R$ {venda[3]:.2f}", f"R$ {venda[4]:.2f}", 
                venda[5]
            ))
        
        # Atualizar total
        total = self.vendas.total_vendas(self.auth.usuario_logado['id'])
        self.label_total.config(text=f"Total de Vendas: R$ {total:.2f}")
    
    def carregar_anotacoes(self):
        for item in self.tree_anotacoes.get_children():
            self.tree_anotacoes.delete(item)
        
        anotacoes = self.anotacoes.listar_anotacoes(self.auth.usuario_logado['id'])
        for anotacao in anotacoes:
            self.tree_anotacoes.insert('', 'end', values=(
                anotacao[0], anotacao[1], 
                anotacao[3][:10], anotacao[4][:10]
            ))
    
    def editar_anotacao(self):
        selecionado = self.tree_anotacoes.selection()
        if selecionado:
            anotacao_id = self.tree_anotacoes.item(selecionado[0])['values'][0]
            EditarAnotacaoWindow(self, anotacao_id)
        else:
            messagebox.showwarning("Aviso", "Selecione uma anotação para editar!")
    
    def excluir_anotacao(self):
        selecionado = self.tree_anotacoes.selection()
        if selecionado:
            anotacao_id = self.tree_anotacoes.item(selecionado[0])['values'][0]
            if messagebox.askyesno("Confirmar", "Deseja excluir esta anotação?"):
                if self.anotacoes.excluir_anotacao(anotacao_id, self.auth.usuario_logado['id']):
                    messagebox.showinfo("Sucesso", "Anotação excluída com sucesso!")
                    self.carregar_anotacoes()
                else:
                    messagebox.showerror("Erro", "Erro ao excluir anotação!")
        else:
            messagebox.showwarning("Aviso", "Selecione uma anotação para excluir!")
    
    def visualizar_anotacao(self):
        selecionado = self.tree_anotacoes.selection()
        if selecionado:
            anotacao_id = self.tree_anotacoes.item(selecionado[0])['values'][0]
            VisualizarAnotacaoWindow(self, anotacao_id)
        else:
            messagebox.showwarning("Aviso", "Selecione uma anotação para visualizar!")
    
    def logout(self):
        self.auth.logout()
        self.root.destroy()
        self.root.master.deiconify()

class EditarAnotacaoWindow:
    def __init__(self, parent, anotacao_id):
        self.parent = parent
        self.anotacao_id = anotacao_id
        self.window = tk.Toplevel(parent.root)
        self.window.title("Editar Anotação")
        self.window.geometry("500x400")
        
        self.carregar_anotacao()
        self.criar_widgets()
    
    def carregar_anotacao(self):
        anotacoes = self.parent.anotacoes.listar_anotacoes(self.parent.auth.usuario_logado['id'])
        for anotacao in anotacoes:
            if anotacao[0] == self.anotacao_id:
                self.anotacao = anotacao
                break
    
    def criar_widgets(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Editar Anotação", font=('Arial', 14)).pack(pady=10)
        
        ttk.Label(frame, text="Título:").pack(anchor=tk.W)
        self.entry_titulo = ttk.Entry(frame, width=50)
        self.entry_titulo.insert(0, self.anotacao[1])
        self.entry_titulo.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Conteúdo:").pack(anchor=tk.W, pady=(10,0))
        self.text_conteudo = tk.Text(frame, width=50, height=10)
        self.text_conteudo.insert("1.0", self.anotacao[2])
        self.text_conteudo.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Button(frame, text="Salvar", command=self.salvar).pack(pady=10)
    
    def salvar(self):
        titulo = self.entry_titulo.get()
        conteudo = self.text_conteudo.get("1.0", tk.END).strip()
        
        if self.parent.anotacoes.editar_anotacao(
            self.anotacao_id, titulo, conteudo, self.parent.auth.usuario_logado['id']
        ):
            messagebox.showinfo("Sucesso", "Anotação atualizada com sucesso!")
            self.window.destroy()
            self.parent.carregar_anotacoes()
        else:
            messagebox.showerror("Erro", "Erro ao atualizar anotação!")

class VisualizarAnotacaoWindow:
    def __init__(self, parent, anotacao_id):
        self.parent = parent
        self.anotacao_id = anotacao_id
        self.window = tk.Toplevel(parent.root)
        self.window.title("Visualizar Anotação")
        self.window.geometry("500x400")
        
        self.carregar_anotacao()
        self.criar_widgets()
    
    def carregar_anotacao(self):
        anotacoes = self.parent.anotacoes.listar_anotacoes(self.parent.auth.usuario_logado['id'])
        for anotacao in anotacoes:
            if anotacao[0] == self.anotacao_id:
                self.anotacao = anotacao
                break
    
    def criar_widgets(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=self.anotacao[1], font=('Arial', 14, 'bold')).pack(pady=10)
        
        texto_frame = ttk.Frame(frame)
        texto_frame.pack(fill=tk.BOTH, expand=True)
        
        texto = tk.Text(texto_frame, wrap=tk.WORD)
        texto.insert("1.0", self.anotacao[2])
        texto.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(texto_frame, orient=tk.VERTICAL, command=texto.yview)
        texto.configure(yscrollcommand=scrollbar.set)
        
        texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(frame, text=f"Criada em: {self.anotacao[3]}\nModificada em: {self.anotacao[4]}", 
                 font=('Arial', 8)).pack(pady=10)

# Executar aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

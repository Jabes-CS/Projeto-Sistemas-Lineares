import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import copy

class LinearSystemSolver:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Resolução de Sistemas Lineares - Método de Escalonamento")
        self.root.geometry("400x300")
        self.root.configure(bg="#f0f0f0")  # Fundo claro e moderno
        self.root.resizable(False, False)
        
        # Estilo moderno
        style = ttk.Style()
        style.theme_use("clam")  # Tema mais moderno
        style.configure("TLabel", background="#f0f0f0", foreground="#333333", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 11, "bold"), padding=10)
        style.map("TButton", background=[("active", "#4a90e2")])
        
        self.setup_size_window()
    
    def setup_size_window(self):
        # Limpar janela anterior
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Título
        title = tk.Label(self.root, text="Resolução de Sistemas Lineares", 
                         font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        title.pack(pady=30)
        
        # Instrução
        instr = tk.Label(self.root, text="Digite o tamanho do sistema (n x n, 1 ≤ n ≤ 10):", 
                         font=("Arial", 12), bg="#f0f0f0", fg="#333333")
        instr.pack(pady=10)
        
        # Entry para n
        self.n_var = tk.StringVar()
        n_entry = tk.Entry(self.root, textvariable=self.n_var, font=("Arial", 14), 
                           width=10, justify="center", relief="solid", bd=1)
        n_entry.pack(pady=10)
        n_entry.focus()
        
        # Botão prosseguir
        btn_proceed = ttk.Button(self.root, text="Prosseguir", command=self.get_size)
        btn_proceed.pack(pady=20)
        
        # Bind Enter
        self.root.bind("<Return>", lambda e: self.get_size())
    
    def get_size(self):
        try:
            n = int(self.n_var.get())
            if 1 <= n <= 10:
                self.n = n
                self.setup_input_window()
            else:
                messagebox.showerror("Erro", "Tamanho deve ser entre 1 e 10.")
                self.n_var.set("")
        except ValueError:
            messagebox.showerror("Erro", "Digite um número inteiro válido.")
            self.n_var.set("")
    
    def setup_input_window(self):
        # Nova janela para input
        self.input_window = tk.Toplevel(self.root)
        self.input_window.title("Inserir Coeficientes e Termos Independentes")
        self.input_window.geometry(f"{600 if self.n > 5 else 500}x{700 if self.n > 5 else 600}")
        self.input_window.configure(bg="#f0f0f0")
        self.input_window.resizable(False, False)
        self.input_window.grab_set()  # Modal
        
        # Título
        title = tk.Label(self.input_window, text=f"Sistema {self.n}x{self.n}", 
                         font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
        title.pack(pady=10)
        
        # Frame para matriz
        matrix_frame = tk.Frame(self.input_window, bg="#f0f0f0")
        matrix_frame.pack(pady=10)
        
        self.entries = [[None for _ in range(self.n)] for _ in range(self.n)]  # Coeficientes A
        self.b_entries = [None] * self.n  # Termos b
        
        # Labels para linhas
        for i in range(self.n):
            row_label = tk.Label(matrix_frame, text=f"Equação {i+1}:", font=("Arial", 10), bg="#f0f0f0", fg="#555555")
            row_label.grid(row=i, column=0, padx=5, pady=5, sticky="e")
            
            for j in range(self.n):
                label = tk.Label(matrix_frame, text=f"a_{i+1}{j+1}", font=("Arial", 9), bg="#f0f0f0", fg="#777777")
                label.grid(row=i, column=2*j + 1, padx=2, pady=5)
                
                entry = tk.Entry(matrix_frame, font=("Arial", 10), width=6, relief="solid", bd=1, bg="#ffffff")
                entry.grid(row=i, column=2*j + 2, padx=2, pady=5)
                self.entries[i][j] = entry
            
            # Termo independente
            b_label = tk.Label(matrix_frame, text="=", font=("Arial", 10, "bold"), bg="#f0f0f0", fg="#333333")
            b_label.grid(row=i, column=2*self.n + 1, padx=5, pady=5)
            
            b_entry = tk.Entry(matrix_frame, font=("Arial", 10), width=6, relief="solid", bd=1, bg="#ffffff")
            b_entry.grid(row=i, column=2*self.n + 2, padx=2, pady=5)
            self.b_entries[i] = b_entry
        
        # Botão processar
        btn_process = ttk.Button(self.input_window, text="Processar Sistema", command=self.process_system)
        btn_process.pack(pady=20)
    
    def process_system(self):
        try:
            # Ler matriz A e b
            A = np.zeros((self.n, self.n))
            b = np.zeros(self.n)
            
            for i in range(self.n):
                for j in range(self.n):
                    A[i, j] = float(self.entries[i][j].get())
                b[i] = float(self.b_entries[i].get())
            
            # Matriz aumentada
            augmented = np.column_stack((A, b))
            
            # Salvar original para exibição
            self.original_system = copy.deepcopy(augmented)
            
            # Escalonamento
            self.escalonado, self.solution, self.has_solution = self.gaussian_elimination(augmented)
            
            # Fechar input e mostrar original
            self.input_window.destroy()
            self.show_original_system()
            
        except ValueError:
            messagebox.showerror("Erro", "Todos os valores devem ser números.")
    
    def gaussian_elimination(self, matrix):
        m = self.n
        rows, cols = matrix.shape  # rows = m, cols = m+1
        
        # Forward elimination com pivotação parcial
        for i in range(m):
            # Encontrar pivot
            max_row = i
            for k in range(i+1, m):
                if abs(matrix[k, i]) > abs(matrix[max_row, i]):
                    max_row = k
            # Trocar linhas
            matrix[[i, max_row]] = matrix[[max_row, i]]
            
            # Se pivot zero, sistema pode ser inconsistente ou dependente
            if abs(matrix[i, i]) < 1e-10:
                # Verificar inconsistência
                if abs(matrix[i, m]) > 1e-10:
                    return matrix, None, False
                continue  # Linha zero, pular (para infinitas soluções, mas simplificamos)
            
            # Eliminar abaixo
            for k in range(i+1, m):
                c = -matrix[k, i] / matrix[i, i]
                matrix[k, i:m+1] += c * matrix[i, i:m+1]
        
        # Back substitution
        x = np.zeros(m)
        for i in range(m-1, -1, -1):
            if abs(matrix[i, i]) < 1e-10:
                if abs(matrix[i, m]) > 1e-10:
                    return matrix, None, False
                # Para infinitas, assumimos único ou inconsistente; aqui setamos x[i]=0 arbitrário
                x[i] = 0
                continue
            x[i] = matrix[i, m]
            for j in range(i+1, m):
                x[i] -= matrix[i, j] * x[j]
            x[i] /= matrix[i, i]
        
        return matrix, x, True
    
    def show_original_system(self):
        self.display_window = tk.Toplevel(self.root)
        self.display_window.title("Sistema Original")
        self.display_window.geometry("600x500")
        self.display_window.configure(bg="#f0f0f0")
        self.display_window.resizable(False, False)
        
        # Título
        title = tk.Label(self.display_window, text="Sistema Linear Original", 
                         font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
        title.pack(pady=10)
        
        # Text widget para exibir
        text = scrolledtext.ScrolledText(self.display_window, width=70, height=20, 
                                         font=("Courier", 11), bg="#ffffff", fg="#000000", relief="solid", bd=1)
        text.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Escrever sistema
        system_str = "Sistema Original:\n\n"
        for i in range(self.n):
            row = " ".join([f"{self.original_system[i,j]:.2f}" if j < self.n else f"| {self.original_system[i,j]:.2f}" 
                            for j in range(self.n + 1)])
            system_str += f"Equação {i+1}: {row}\n"
        
        text.insert(tk.END, system_str)
        text.config(state="disabled")
        
        # Botão próximo
        btn_next = ttk.Button(self.display_window, text="Ver Sistema Escalonado", command=self.show_escalonado_system)
        btn_next.pack(pady=10)
    
    def show_escalonado_system(self):
        self.display_window.destroy()
        
        self.display_window = tk.Toplevel(self.root)
        self.display_window.title("Sistema Escalonado")
        self.display_window.geometry("600x500")
        self.display_window.configure(bg="#f0f0f0")
        self.display_window.resizable(False, False)
        
        # Título
        title = tk.Label(self.display_window, text="Sistema Linear Escalonado", 
                         font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
        title.pack(pady=10)
        
        # Text widget
        text = scrolledtext.ScrolledText(self.display_window, width=70, height=20, 
                                         font=("Courier", 11), bg="#ffffff", fg="#000000", relief="solid", bd=1)
        text.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Escrever escalonado
        system_str = "Sistema Escalonado (Forma Escada):\n\n"
        for i in range(self.n):
            row = " ".join([f"{self.escalonado[i,j]:.2f}" if j < self.n else f"| {self.escalonado[i,j]:.2f}" 
                            for j in range(self.n + 1)])
            system_str += f"Equação {i+1}: {row}\n"
        
        text.insert(tk.END, system_str)
        text.config(state="disabled")
        
        # Botão solução
        if self.has_solution:
            btn_next = ttk.Button(self.display_window, text="Ver Solução", command=self.show_solution)
        else:
            btn_next = ttk.Button(self.display_window, text="Ver Status", command=self.show_no_solution)
        btn_next.pack(pady=10)
    
    def show_solution(self):
        self.display_window.destroy()
        
        self.display_window = tk.Toplevel(self.root)
        self.display_window.title("Solução do Sistema")
        self.display_window.geometry("500x400")
        self.display_window.configure(bg="#f0f0f0")
        self.display_window.resizable(False, False)
        
        # Título
        title = tk.Label(self.display_window, text="Solução Única Encontrada", 
                         font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#27ae60")  # Verde para sucesso
        title.pack(pady=10)
        
        # Text para solução
        text = scrolledtext.ScrolledText(self.display_window, width=50, height=15, 
                                         font=("Courier", 12), bg="#ffffff", fg="#000000", relief="solid", bd=1)
        text.pack(pady=10, padx=20, fill="both", expand=True)
        
        sol_str = "Solução:\n\n"
        for i in range(self.n):
            sol_str += f"x_{i+1} = {self.solution[i]:.4f}\n"
        
        text.insert(tk.END, sol_str)
        text.config(state="disabled")
        
        # Botão voltar ao início
        btn_restart = ttk.Button(self.display_window, text="Novo Sistema", command=self.restart)
        btn_restart.pack(pady=10)
    
    def show_no_solution(self):
        self.display_window.destroy()
        
        self.display_window = tk.Toplevel(self.root)
        self.display_window.title("Status do Sistema")
        self.display_window.geometry("500x300")
        self.display_window.configure(bg="#f0f0f0")
        self.display_window.resizable(False, False)
        
        # Título
        title = tk.Label(self.display_window, text="Sistema Inconsistente", 
                         font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#e74c3c")  # Vermelho para erro
        title.pack(pady=20)
        
        # Mensagem
        msg = tk.Label(self.display_window, 
                       text="O sistema não possui solução (inconsistente).\nVerifique os coeficientes.", 
                       font=("Arial", 12), bg="#f0f0f0", fg="#333333", justify="center")
        msg.pack(pady=20)
        
        # Botão voltar
        btn_restart = ttk.Button(self.display_window, text="Novo Sistema", command=self.restart)
        btn_restart.pack(pady=10)
    
    def restart(self):
        self.display_window.destroy()
        self.setup_size_window()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LinearSystemSolver()
    app.run()
# <====== BIBLIOTECAS ======> #
import customtkinter as ctk
from tkinter import messagebox
import numpy as np
from fractions import Fraction

# <========================= FUNÇÕES MATEMÁTICAS =========================> #

def escalonar_sistema(A, B):
    n = len(B)
    for i in range(n):
        max_index = i + np.argmax(np.abs(A[i:, i]))
        if A[max_index, i] == 0 and B[max_index] != 0:
            return None, None, "impossível"
        A[[i, max_index]], B[[i, max_index]] = A[[max_index, i]], B[[max_index, i]]
        for j in range(i + 1, n):
            fator = A[j, i] / A[i, i]
            A[j] -= fator * A[i]
            B[j] -= fator * B[i]
    return A, B, "possível"

def verificar_inconsistencia(A_escalonado, B_escalonado):
    for i in range(len(B_escalonado)):
        if all(A_escalonado[i, i:] == 0) and B_escalonado[i] != 0:
            return True
    return False

def resolver_sistema_determinado(A_escalonado, B_escalonado):
    n = len(B_escalonado)
    X = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if A_escalonado[i, i] == 0:
            return None
        X[i] = (B_escalonado[i] - np.dot(A_escalonado[i, i + 1:], X[i + 1:])) / A_escalonado[i, i]
    return X

def resolver_sistema_indeterminado(A_escalonado, B_escalonado):
    n = len(B_escalonado)
    X = np.zeros(n, dtype=object)
    variaveis_livres = []
    for i in range(n):
        if A_escalonado[i, i] == 0:
            variaveis_livres.append(i)
    for i in range(n - 1, -1, -1):
        if A_escalonado[i, i] != 0:
            expr = f"{Fraction(B_escalonado[i]).limit_denominator()}"
            for j in range(i + 1, n):
                if j in variaveis_livres:
                    expr += f" - {Fraction(A_escalonado[i, j]).limit_denominator()}*t{j + 1}"
                else:
                    expr += f" - {Fraction(A_escalonado[i, j]).limit_denominator()}*x{j + 1}"
            X[i] = f"({expr}) / {Fraction(A_escalonado[i, i]).limit_denominator()}"
        else:
            X[i] = f"t{i + 1}"
    return X

# <========================= INTERFACE =========================> #

class SistemaLinearApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Resolução de Sistemas Lineares - Método do Escalonamento")
        self.geometry("950x720")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.label_titulo = ctk.CTkLabel(self, text="🔢 Sistema Linear - Escalonamento", font=("Arial", 22, "bold"))
        self.label_titulo.pack(pady=15)

        # Frame de seleção
        frame_sel = ctk.CTkFrame(self)
        frame_sel.pack(pady=10)
        ctk.CTkLabel(frame_sel, text="Selecione o tamanho da matriz:", font=("Arial", 14)).pack(side="left", padx=10)
        self.combo_tamanho = ctk.CTkOptionMenu(frame_sel, values=[f"{i}x{i}" for i in range(1, 11)], command=self.gerar_campos)
        self.combo_tamanho.pack(side="left", padx=10)

        # Frame da matriz
        self.frame_matriz = ctk.CTkFrame(self)
        self.frame_matriz.pack(pady=15)
        self.campos_A = []
        self.campos_B = []

        # Botão resolver sistema
        self.btn_resolver = ctk.CTkButton(self, text="Resolver Sistema", command=self.resolver, width=200, height=40, font=("Arial", 14, "bold"))
        self.btn_resolver.pack(pady=10)

        # Área de resultado
        self.text_resultado = ctk.CTkTextbox(self, width=850, height=300, corner_radius=10, font=("Consolas", 12))
        self.text_resultado.pack(pady=20)

    def gerar_campos(self, value):
        for widget in self.frame_matriz.winfo_children():
            widget.destroy()

        n = int(value.split("x")[0])
        self.campos_A, self.campos_B = [], []

        for i in range(n):
            linha = []
            for j in range(n):
                entry = ctk.CTkEntry(self.frame_matriz, width=55, justify="center")
                entry.grid(row=i, column=j, padx=3, pady=3)
                linha.append(entry)
            self.campos_A.append(linha)

            sep = ctk.CTkLabel(self.frame_matriz, text="|")
            sep.grid(row=i, column=n)

            entry_b = ctk.CTkEntry(self.frame_matriz, width=55, justify="center")
            entry_b.grid(row=i, column=n + 1, padx=3)
            self.campos_B.append(entry_b)

    def resolver(self):
        try:
            n = int(self.combo_tamanho.get().split("x")[0])
        except:
            messagebox.showerror("Erro", "Selecione o tamanho do sistema primeiro!")
            return

        try:
            A = np.zeros((n, n))
            B = np.zeros(n)
            for i in range(n):
                for j in range(n):
                    A[i, j] = float(self.campos_A[i][j].get())
                B[i] = float(self.campos_B[i].get())
        except ValueError:
            messagebox.showerror("Erro", "Preencha todos os campos com números válidos!")
            return

        self.text_resultado.delete("1.0", "end")
        self.text_resultado.insert("end", f"Sistema Original:\n{np.column_stack((A, B))}\n\n")

        A_esc, B_esc, status = escalonar_sistema(A.copy(), B.copy())

        if status == "impossível" or verificar_inconsistencia(A_esc, B_esc):
            self.text_resultado.insert("end", "Sistema impossível e sem solução.\n")
            return

        self.text_resultado.insert("end", f"Sistema Escalonado:\n{np.column_stack((A_esc, B_esc))}\n\n")

        if all(A_esc[i, i] != 0 for i in range(n)):
            solucao = resolver_sistema_determinado(A_esc, B_esc)
            self.text_resultado.insert("end", "Solução Determinada:\n")
            for i, x in enumerate(solucao):
                self.text_resultado.insert("end", f"x{i + 1} = {Fraction(x).limit_denominator()}\n")
        else:
            solucao = resolver_sistema_indeterminado(A_esc, B_esc)
            self.text_resultado.insert("end", "Solução Indeterminada:\n")
            for i, x in enumerate(solucao):
                self.text_resultado.insert("end", f"x{i + 1} = {x}\n")

# <===== EXECUÇÃO =====> #
if __name__ == "__main__":
    app = SistemaLinearApp()
    app.mainloop()

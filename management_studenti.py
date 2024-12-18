import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import os


# Crearea bazei de date cu numele nou
def creeaza_baza_date():
    conexiune = sqlite3.connect("management_studenti.db")
    cursor = conexiune.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS studenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nume TEXT NOT NULL,
        varsta INTEGER NOT NULL,
        nota REAL NOT NULL,
        program TEXT NOT NULL,
        grupa TEXT NOT NULL,
        materia TEXT NOT NULL
    )
    """)
    conexiune.commit()
    conexiune.close()


# Adaugare student
def adauga_student():
    nume = intrare_nume.get().strip()
    varsta = intrare_varsta.get().strip()
    nota = intrare_nota.get().strip()
    program = intrare_program.get().strip()
    grupa = intrare_grupa.get().strip()
    materia = intrare_materia.get().strip()

    # Validare nume (doar litere si spatii)
    if not nume.replace(" ", "").isalpha():
        messagebox.showerror("Eroare Validare", "Numele trebuie să conțină doar litere și spații!")
        return

    # Validare vârstă (doar cifre)
    if not varsta.isdigit():
        messagebox.showerror("Eroare Validare", "Vârsta trebuie să conțină doar cifre!")
        return

    # Validare nota (doar numere float/intregi)
    try:
        nota = float(nota)
        if nota < 0 or nota > 10:
            messagebox.showerror("Eroare Validare", "Nota trebuie să fie între 0 și 10!")
            return
    except ValueError:
        messagebox.showerror("Eroare Validare", "Nota trebuie să fie un număr valid!")
        return

    # Verificare completare campuri
    if not all([nume, varsta, nota, program, grupa, materia]):
        messagebox.showwarning("Eroare Introducere", "Toate câmpurile sunt obligatorii!")
        return

    # Salvare date in baza de date
    try:
        conexiune = sqlite3.connect("management_studenti.db")
        cursor = conexiune.cursor()
        cursor.execute("""
            INSERT INTO studenti (nume, varsta, nota, program, grupa, materia) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nume, int(varsta), nota, program, grupa, materia))
        conexiune.commit()
        conexiune.close()
        incarca_studenti()
        sterge_campuri()
        messagebox.showinfo("Succes", "Studentul a fost adăugat cu succes!")
    except Exception as e:
        messagebox.showerror("Eroare", f"Eroare la adăugare: {e}")
    
# Stergere campuri dupa adaugare
def sterge_campuri():
    intrare_nume.delete(0, tk.END)
    intrare_varsta.delete(0, tk.END)
    intrare_nota.delete(0, tk.END)
    intrare_program.delete(0, tk.END)
    intrare_grupa.delete(0, tk.END)
    intrare_materia.delete(0, tk.END)


# Incarcare studenti in tabel
def incarca_studenti():
    conexiune = sqlite3.connect("management_studenti.db")
    cursor = conexiune.cursor()
    cursor.execute("SELECT * FROM studenti")
    randuri = cursor.fetchall()
    conexiune.close()

    tabel_studenti.delete(*tabel_studenti.get_children())
    for rand in randuri:
        tabel_studenti.insert("", tk.END, values=rand)


# Stergere student selectat
def sterge_student():
    selectie = tabel_studenti.selection()
    if not selectie:
        messagebox.showwarning("Eroare Selecție", "Selectați un student pentru a-l șterge!")
        return

    student_id = tabel_studenti.item(selectie, "values")[0]

    conexiune = sqlite3.connect("management_studenti.db")
    cursor = conexiune.cursor()

    # Stergere student selectat
    cursor.execute("DELETE FROM studenti WHERE id = ?", (student_id,))
    
    # Reordonare ID-uri
    cursor.execute("""
    CREATE TEMPORARY TABLE studenti_temp AS
    SELECT nume, varsta, nota, program, grupa, materia FROM studenti;
    """)
    cursor.execute("DROP TABLE studenti;")
    cursor.execute("""
    CREATE TABLE studenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nume TEXT NOT NULL,
        varsta INTEGER NOT NULL,
        nota REAL NOT NULL,
        program TEXT NOT NULL,
        grupa TEXT NOT NULL,
        materia TEXT NOT NULL
    );
    """)
    cursor.execute("""
    INSERT INTO studenti (nume, varsta, nota, program, grupa, materia)
    SELECT nume, varsta, nota, program, grupa, materia FROM studenti_temp;
    """)
    cursor.execute("DROP TABLE studenti_temp;")

    conexiune.commit()
    conexiune.close()

    incarca_studenti()
    messagebox.showinfo("Succes", "Studentul a fost șters și ID-urile au fost reordonate!")



# Export date in Excel
def export_excel():
    conexiune = sqlite3.connect("management_studenti.db")
    cursor = conexiune.cursor()
    cursor.execute("SELECT * FROM studenti")
    randuri = cursor.fetchall()
    conexiune.close()

    if randuri:
        df = pd.DataFrame(randuri, columns=["ID", "Nume", "Varsta", "Nota", "Program", "Grupa", "Materia"])
        file_path = "management_studenti_export.xlsx"
        df.to_excel(file_path, index=False)
        os.startfile(file_path)  # Deschide automat fișierul Excel
        messagebox.showinfo("Succes", "Datele au fost exportate în Excel!")
    else:
        messagebox.showwarning("Eroare", "Nu există date de exportat!")


# Creare grafic note
def grafic_note():
    conexiune = sqlite3.connect("management_studenti.db")
    cursor = conexiune.cursor()
    cursor.execute("SELECT nume, nota FROM studenti")
    randuri = cursor.fetchall()
    conexiune.close()

    if not randuri:
        messagebox.showwarning("Eroare", "Nu există date pentru a genera graficul!")
        return

    nume = [rand[0] for rand in randuri]
    note = [rand[1] for rand in randuri]

    plt.figure(figsize=(10, 6))
    plt.bar(nume, note, color='purple')
    plt.xlabel("Studenți")
    plt.ylabel("Note")
    plt.title("Grafic Note Studenți")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# Creare fereastra principala
root = tk.Tk()
root.title("Sistem de Management al Studenților")
root.geometry("1300x700")
root.configure(bg="#f8f9fa")

# Stiluri si design
font_titlu = ("Arial", 16, "bold")
font_label = ("Arial", 12)
bg_culoare = "#e6f7ff"

# Titlu
tk.Label(root, text="Sistem de Management al Studenților", font=font_titlu, bg="#6c757d", fg="white").pack(fill=tk.X)

# Sectiunea de introducere date
frame_date = tk.Frame(root, bg=bg_culoare, pady=10)
frame_date.pack(fill=tk.X)

tk.Label(frame_date, text="Nume:", font=font_label, bg=bg_culoare).grid(row=0, column=0, padx=5, pady=5)
intrare_nume = tk.Entry(frame_date, width=20)
intrare_nume.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_date, text="Vârstă:", font=font_label, bg=bg_culoare).grid(row=0, column=2, padx=5, pady=5)
intrare_varsta = tk.Entry(frame_date, width=10)
intrare_varsta.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_date, text="Notă:", font=font_label, bg=bg_culoare).grid(row=0, column=4, padx=5, pady=5)
intrare_nota = tk.Entry(frame_date, width=10)
intrare_nota.grid(row=0, column=5, padx=5, pady=5)

tk.Label(frame_date, text="Program:", font=font_label, bg=bg_culoare).grid(row=1, column=0, padx=5, pady=5)
intrare_program = tk.Entry(frame_date, width=20)
intrare_program.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_date, text="Grupă:", font=font_label, bg=bg_culoare).grid(row=1, column=2, padx=5, pady=5)
intrare_grupa = tk.Entry(frame_date, width=10)
intrare_grupa.grid(row=1, column=3, padx=5, pady=5)

tk.Label(frame_date, text="Materia:", font=font_label, bg=bg_culoare).grid(row=1, column=4, padx=5, pady=5)
intrare_materia = tk.Entry(frame_date, width=20)
intrare_materia.grid(row=1, column=5, padx=5, pady=5)

# Butoane functionale
tk.Button(frame_date, text="Adaugă", command=adauga_student, bg="#28a745", fg="white").grid(row=2, column=0, padx=5, pady=5)
tk.Button(frame_date, text="Șterge", command=sterge_student, bg="#dc3545", fg="white").grid(row=2, column=1, padx=5, pady=5)
tk.Button(frame_date, text="Export Excel", command=export_excel, bg="#6f42c1", fg="white").grid(row=2, column=2, padx=5, pady=5)
tk.Button(frame_date, text="Grafic Note", command=grafic_note, bg="#6f42c1", fg="white").grid(row=2, column=3, padx=5, pady=5)

# Tabel studenti
frame_tabel = tk.Frame(root)
frame_tabel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

coloane = ("ID", "Nume", "Varsta", "Nota", "Program", "Grupa", "Materia")
tabel_studenti = ttk.Treeview(frame_tabel, columns=coloane, show="headings", height=15)
tabel_studenti.pack(fill=tk.BOTH, expand=True)

for col in coloane:
    tabel_studenti.heading(col, text=col)
    tabel_studenti.column(col, width=150, anchor=tk.CENTER)

scrollbar = ttk.Scrollbar(frame_tabel, orient=tk.VERTICAL, command=tabel_studenti.yview)
tabel_studenti.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Creare baza de date si incarcare date
creeaza_baza_date()
incarca_studenti()

# Rularea aplicatiei
root.mainloop()

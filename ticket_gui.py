# simple_ticket_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import os
import time

class SimpleTicketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ticket System")
        self.root.geometry("600x500")
        
        # Загрузка DLL
        dll_path = r"C:\Users\Ольга\source\repos\TicketSystemDLL\x64\Debug\TicketSystemDLL.dll"
        
        if not os.path.exists(dll_path):
            messagebox.showerror("Error", f"DLL not found:\n{dll_path}")
            root.destroy()
            return
        
        try:
            self.dll = ctypes.CDLL(dll_path)
            print("DLL loaded")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load DLL:\n{e}")
            root.destroy()
            return
        
        # Настройка функций
        self.setup_functions()
        
        # Создаем реестр
        self.registry = self.dll.CreateTicketRegistry()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Добавляем несколько тестовых билетов
        self.add_test_tickets()
    
    def setup_functions(self):
        """Настройка функций DLL"""
        # Основные функции
        self.dll.CreateTicketRegistry.restype = ctypes.c_void_p
        self.dll.CreateTicketRegistry.argtypes = []
        
        self.dll.DeleteTicketRegistry.argtypes = [ctypes.c_void_p]
        
        self.dll.AddLimitedTicket.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        
        self.dll.AddUnlimitedTicket.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p
        ]
        
        self.dll.TryControl.restype = ctypes.c_int
        self.dll.TryControl.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int
        ]
        
        self.dll.GetTicketCount.restype = ctypes.c_int
        self.dll.GetTicketCount.argtypes = [ctypes.c_void_p]
        
        self.dll.RunSimpleTest.argtypes = []
    
    def create_widgets(self):
        """Создание интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title = ttk.Label(main_frame, text="Ticket Control System", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=(0, 20))
        
        # Вкладки
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка 1: Добавить билет
        tab1 = ttk.Frame(notebook, padding="10")
        notebook.add(tab1, text="Add Ticket")
        self.setup_add_tab(tab1)
        
        # Вкладка 2: Проверить билет
        tab2 = ttk.Frame(notebook, padding="10")
        notebook.add(tab2, text="Check Ticket")
        self.setup_check_tab(tab2)
        
        # Вкладка 3: Инфо
        tab3 = ttk.Frame(notebook, padding="10")
        notebook.add(tab3, text="Info")
        self.setup_info_tab(tab3)
        
        # Статус
        self.status = tk.StringVar()
        self.status.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status, 
                              relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_add_tab(self, parent):
        """Вкладка добавления билета"""
        # Тип билета
        ttk.Label(parent, text="Ticket Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ticket_type = tk.StringVar(value="limited")
        ttk.Radiobutton(parent, text="Limited", variable=self.ticket_type, 
                       value="limited").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(parent, text="Unlimited", variable=self.ticket_type, 
                       value="unlimited").grid(row=2, column=0, sticky=tk.W)
        
        # Номер билета
        ttk.Label(parent, text="Ticket Number:").grid(row=3, column=0, sticky=tk.W, pady=(10,5))
        self.ticket_num = ttk.Entry(parent, width=15)
        self.ticket_num.grid(row=3, column=1, pady=(10,5))
        self.ticket_num.insert(0, "100")
        
        # Параметры
        ttk.Label(parent, text="Max Rides:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.max_rides = ttk.Entry(parent, width=15)
        self.max_rides.grid(row=4, column=1, pady=5)
        self.max_rides.insert(0, "5")
        
        ttk.Label(parent, text="Reason (for unlimited):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.reason = ttk.Entry(parent, width=20)
        self.reason.grid(row=5, column=1, pady=5)
        self.reason.insert(0, "VIP")
        
        # Кнопка
        ttk.Button(parent, text="Add Ticket", command=self.add_ticket, 
                  width=15).grid(row=6, column=0, columnspan=2, pady=20)
    
    def setup_check_tab(self, parent):
        """Вкладка проверки билета"""
        # Ввод данных
        ttk.Label(parent, text="Ticket Number:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.check_num = ttk.Entry(parent, width=15)
        self.check_num.grid(row=0, column=1, pady=5)
        
        ttk.Label(parent, text="Current Time (seconds):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.check_time = ttk.Entry(parent, width=15)
        self.check_time.grid(row=1, column=1, pady=5)
        self.check_time.insert(0, str(int(time.time())))
        
        # Кнопка проверки
        ttk.Button(parent, text="Check Ticket", command=self.check_ticket, 
                  width=15).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Результат
        self.result_text = tk.StringVar()
        self.result_text.set("Result will appear here")
        result_label = ttk.Label(parent, textvariable=self.result_text, 
                                font=('Arial', 12), foreground="blue")
        result_label.grid(row=3, column=0, columnspan=2, pady=20)
    
    def setup_info_tab(self, parent):
        """Вкладка информации"""
        # Кнопки
        ttk.Button(parent, text="Run Test", command=self.run_test, 
                  width=20).pack(pady=10)
        
        ttk.Button(parent, text="Show Ticket Count", command=self.show_count, 
                  width=20).pack(pady=10)
        
        ttk.Button(parent, text="Clear All", command=self.clear_all, 
                  width=20).pack(pady=10)
        
        # Информация
        self.info_text = tk.StringVar()
        self.info_text.set("Ticket System v1.0\nClick buttons above")
        info_label = ttk.Label(parent, textvariable=self.info_text)
        info_label.pack(pady=20)
    
    def add_test_tickets(self):
        """Добавление тестовых билетов"""
        current_time = int(time.time())
        # Ограниченный билет
        self.dll.AddLimitedTicket(self.registry, 101, current_time, 3)
        # Бессрочный билет
        self.dll.AddUnlimitedTicket(self.registry, 102, b"VIP Client")
        print("Test tickets added: #101 (limited), #102 (unlimited)")
    
    def add_ticket(self):
        """Добавить билет"""
        try:
            num = int(self.ticket_num.get())
            ticket_type = self.ticket_type.get()
            
            if ticket_type == "limited":
                rides = int(self.max_rides.get())
                self.dll.AddLimitedTicket(self.registry, num, int(time.time()), rides)
                msg = f"Ticket #{num} added (limited, {rides} rides)"
            else:
                reason = self.reason.get().encode('ascii')
                self.dll.AddUnlimitedTicket(self.registry, num, reason)
                msg = f"Ticket #{num} added (unlimited)"
            
            self.status.set(msg)
            messagebox.showinfo("Success", msg)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def check_ticket(self):
        """Проверить билет"""
        try:
            num = int(self.check_num.get())
            current_time = int(self.check_time.get())
            
            result = self.dll.TryControl(self.registry, num, current_time)
            
            if result == 0:
                self.result_text.set(f"Ticket #{num}: ✓ ALLOWED")
                self.result_label_color("green")
            elif result == 1:
                self.result_text.set(f"Ticket #{num}: ✗ DENIED")
                self.result_label_color("red")
            elif result == 2:
                self.result_text.set(f"Ticket #{num}: ⚠ ALARM")
                self.result_label_color("orange")
            else:
                self.result_text.set(f"Ticket #{num}: ? UNKNOWN")
                self.result_label_color("black")
            
            self.status.set(f"Checked ticket #{num}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def result_label_color(self, color):
        """Обновить цвет результата"""
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab in widget.winfo_children():
                    for child in tab.winfo_children():
                        if isinstance(child, ttk.Label) and hasattr(child, 'tk'):
                            try:
                                child.configure(foreground=color)
                            except:
                                pass
    
    def run_test(self):
        """Запустить тест"""
        self.dll.RunSimpleTest()
        self.info_text.set("Test completed!\nCheck console for output.")
        self.status.set("Test executed")
    
    def show_count(self):
        """Показать количество билетов"""
        count = self.dll.GetTicketCount(self.registry)
        self.info_text.set(f"Total tickets: {count}")
        self.status.set(f"Ticket count: {count}")
    
    def clear_all(self):
        """Очистить все"""
        if messagebox.askyesno("Confirm", "Clear all tickets?"):
            # Удаляем старый реестр
            self.dll.DeleteTicketRegistry(self.registry)
            # Создаем новый
            self.registry = self.dll.CreateTicketRegistry()
            # Добавляем тестовые билеты снова
            self.add_test_tickets()
            
            self.info_text.set("All cleared!\nTest tickets added.")
            self.status.set("Registry cleared")
    
    def on_closing(self):
        """Очистка при закрытии"""
        if hasattr(self, 'registry'):
            self.dll.DeleteTicketRegistry(self.registry)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = SimpleTicketGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
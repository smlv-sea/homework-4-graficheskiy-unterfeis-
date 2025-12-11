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
            print("DLL loaded successfully")
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
        
        # Функции добавления с возвращаемыми значениями
        self.dll.AddLimitedTicket.restype = ctypes.c_int
        self.dll.AddLimitedTicket.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        
        self.dll.AddTimedTicket.restype = ctypes.c_int
        self.dll.AddTimedTicket.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        
        self.dll.AddUnlimitedTicket.restype = ctypes.c_int
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
        
        # Функция для получения сообщения об ошибке (если есть в DLL)
        if hasattr(self.dll, 'GetAddTicketErrorString'):
            self.dll.GetAddTicketErrorString.restype = ctypes.c_char_p
            self.dll.GetAddTicketErrorString.argtypes = [ctypes.c_int]
            print("GetAddTicketErrorString function available")
        
        # Также проверим русскую версию
        if hasattr(self.dll, 'GetAddTicketErrorStringRu'):
            self.dll.GetAddTicketErrorStringRu.restype = ctypes.c_char_p
            self.dll.GetAddTicketErrorStringRu.argtypes = [ctypes.c_int]
            print("GetAddTicketErrorStringRu function available")
    
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
        
        # Метка для отображения результата добавления
        self.add_result = tk.StringVar()
        self.add_result.set("")
        add_result_label = ttk.Label(parent, textvariable=self.add_result,
                                    font=('Arial', 10))
        add_result_label.grid(row=7, column=0, columnspan=2, pady=5)
    
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
        result1 = self.dll.AddLimitedTicket(self.registry, 101, current_time, 3)
        if result1 == 0:
            print("Test ticket added: #101 (limited)")
        else:
            error_msg = self.get_error_message(result1)
            print(f"Failed to add test ticket #101: {error_msg}")
        
        # Бессрочный билет
        result2 = self.dll.AddUnlimitedTicket(self.registry, 102, b"VIP Client")
        if result2 == 0:
            print("Test ticket added: #102 (unlimited)")
        else:
            error_msg = self.get_error_message(result2)
            print(f"Failed to add test ticket #102: {error_msg}")
    
    def get_error_message(self, error_code):
        """Получить текстовое сообщение об ошибке по коду"""
        # Сначала попробуем получить из DLL
        dll_message = self.try_get_dll_error_message(error_code)
        if dll_message:
            return dll_message
        
        # Если не получилось, используем стандартные сообщения
        error_messages = {
            0: "Success",
            1: "Ticket with this number already exists",
            2: "Invalid ticket number",
            3: "Invalid parameters",
            4: "Registry is full",
            5: "Memory allocation failed",
            6: "Unknown error"
        }
        return error_messages.get(error_code, f"Error code: {error_code}")
    
    def try_get_dll_error_message(self, error_code):
        """Попытаться получить сообщение об ошибке из DLL"""
        try:
            if hasattr(self.dll, 'GetAddTicketErrorString'):
                error_ptr = self.dll.GetAddTicketErrorString(error_code)
                if error_ptr:
                    return ctypes.string_at(error_ptr).decode('utf-8', errors='ignore')
        except:
            pass
        return None
    
    def add_ticket(self):
        """Добавить билет с проверкой ошибок"""
        try:
            num = int(self.ticket_num.get())
            ticket_type = self.ticket_type.get()
            
            success = False
            
            if ticket_type == "limited":
                rides = int(self.max_rides.get())
                if rides <= 0:
                    messagebox.showerror("Error", "Number of rides must be positive")
                    return
                    
                result = self.dll.AddLimitedTicket(self.registry, num, int(time.time()), rides)
                
                if result == 0:
                    success = True
                    msg = f"Ticket #{num} added (limited, {rides} rides)"
                    self.add_result.set(f"✓ Ticket #{num} added successfully")
                else:
                    error_msg = self.get_error_message(result)
                    msg = f"Failed to add ticket #{num}: {error_msg}"
                    self.add_result.set(f"✗ {error_msg}")
                    
            else:  # unlimited
                reason = self.reason.get()
                if not reason:
                    messagebox.showerror("Error", "Please enter a reason for unlimited ticket")
                    return
                    
                result = self.dll.AddUnlimitedTicket(self.registry, num, reason.encode('utf-8'))
                
                if result == 0:
                    success = True
                    msg = f"Ticket #{num} added (unlimited)"
                    self.add_result.set(f"✓ Ticket #{num} added successfully")
                else:
                    error_msg = self.get_error_message(result)
                    msg = f"Failed to add ticket #{num}: {error_msg}"
                    self.add_result.set(f"✗ {error_msg}")
            
            # Обновляем статус
            self.status.set(msg)
            
            # Показываем соответствующее сообщение
            if success:
                messagebox.showinfo("Success", msg)
                
                # Обновляем количество билетов в инфо-вкладке
                count = self.dll.GetTicketCount(self.registry)
                self.info_text.set(f"Ticket #{num} added successfully!\nTotal tickets: {count}")
                
                # Очищаем поле результата через 3 секунды
                self.root.after(3000, lambda: self.add_result.set(""))
            else:
                # Определяем заголовок и детализированное сообщение
                if result == 1:  # Дубликат
                    title = "Duplicate Ticket"
                    if num < 1000:
                        detailed_msg = f"Ticket #{num:03d} already exists!\n\nPlease use a different ticket number."
                    else:
                        detailed_msg = f"Ticket #{num} already exists!\n\nPlease use a different ticket number."
                else:
                    title = "Error"
                    detailed_msg = msg
                
                messagebox.showerror(title, detailed_msg)
                
                # Очищаем поле результата через 5 секунды
                self.root.after(5000, lambda: self.add_result.set(""))
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            self.add_result.set("✗ Invalid input values")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            self.add_result.set(f"✗ Error: {str(e)}")
    
    def check_ticket(self):
        """Проверить билет"""
        try:
            num = int(self.check_num.get())
            current_time = int(self.check_time.get())
            
            result = self.dll.TryControl(self.registry, num, current_time)
            
            if result == 0:
                self.result_text.set(f"Ticket #{num}: ✓ ALLOWED")
                self.set_result_label_color("green")
            elif result == 1:
                self.result_text.set(f"Ticket #{num}: ✗ DENIED")
                self.set_result_label_color("red")
            elif result == 2:
                self.result_text.set(f"Ticket #{num}: ⚠ ALARM")
                self.set_result_label_color("orange")
            else:
                self.result_text.set(f"Ticket #{num}: ? UNKNOWN (Code: {result})")
                self.set_result_label_color("black")
            
            self.status.set(f"Checked ticket #{num} at time {current_time}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def set_result_label_color(self, color):
        """Обновить цвет результата проверки"""
        try:
            # Находим все виджеты Label и обновляем цвет того, что содержит результат
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    for tab in widget.winfo_children():
                        for child in tab.winfo_children():
                            if isinstance(child, ttk.Label) and hasattr(child, 'cget'):
                                text = child.cget('textvariable')
                                if text == str(self.result_text):
                                    child.configure(foreground=color)
                                    return
        except:
            pass
    
    def run_test(self):
        """Запустить тест"""
        self.dll.RunSimpleTest()
        self.info_text.set("Test completed!\nCheck console for output.")
        self.status.set("Test executed")
        
        # Обновляем количество билетов после теста
        count = self.dll.GetTicketCount(self.registry)
        self.info_text.set(f"Test completed!\nTotal tickets: {count}")
    
    def show_count(self):
        """Показать количество билетов"""
        count = self.dll.GetTicketCount(self.registry)
        self.info_text.set(f"Total tickets in registry: {count}")
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
            
            # Очищаем поле результата добавления
            self.add_result.set("")
    
    def on_closing(self):
        """Очистка при закрытии"""
        if hasattr(self, 'registry'):
            try:
                self.dll.DeleteTicketRegistry(self.registry)
                print("Registry deleted on exit")
            except:
                pass
        self.root.destroy()

def main():
    root = tk.Tk()
    app = SimpleTicketGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
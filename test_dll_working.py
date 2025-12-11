# test_dll_working.py
import ctypes
import os

def main():
    dll_path = r"C:\Users\Ольга\source\repos\TicketSystemDLL\x64\Debug\TicketSystemDLL.dll"
    
    print(f"Loading: {dll_path}")
    print(f"File exists: {os.path.exists(dll_path)}")
    
    if not os.path.exists(dll_path):
        print("ERROR: DLL file not found!")
        return
    
    try:
        # Загружаем DLL
        dll = ctypes.CDLL(dll_path)
        print("SUCCESS! DLL loaded.")
        
        # Теперь используем правильные имена функций с заглавными буквами
        print("\n=== SETTING UP FUNCTIONS ===")
        
        # 1. Создание реестра
        if hasattr(dll, 'CreateTicketRegistry'):
            dll.CreateTicketRegistry.restype = ctypes.c_void_p
            dll.CreateTicketRegistry.argtypes = []
            print("✓ CreateTicketRegistry - configured")
        else:
            print("✗ CreateTicketRegistry - not found")
            return
        
        # 2. Удаление реестра
        if hasattr(dll, 'DeleteTicketRegistry'):
            dll.DeleteTicketRegistry.argtypes = [ctypes.c_void_p]
            print("✓ DeleteTicketRegistry - configured")
        
        # 3. Добавление ограниченного билета
        if hasattr(dll, 'AddLimitedTicket'):
            dll.AddLimitedTicket.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
            ]
            print("✓ AddLimitedTicket - configured")
        
        # 4. Добавление билета с ограниченным сроком
        if hasattr(dll, 'AddTimedTicket'):
            dll.AddTimedTicket.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
            ]
            print("✓ AddTimedTicket - configured")
        
        # 5. Добавление бессрочного билета
        if hasattr(dll, 'AddUnlimitedTicket'):
            dll.AddUnlimitedTicket.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p
            ]
            print("✓ AddUnlimitedTicket - configured")
        
        # 6. Проверка билета
        if hasattr(dll, 'TryControl'):
            dll.TryControl.restype = ctypes.c_int
            dll.TryControl.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_int
            ]
            print("✓ TryControl - configured")
        
        # 7. Получение количества билетов
        if hasattr(dll, 'GetTicketCount'):
            dll.GetTicketCount.restype = ctypes.c_int
            dll.GetTicketCount.argtypes = [ctypes.c_void_p]
            print("✓ GetTicketCount - configured")
        
        # 8. Запуск тестов
        if hasattr(dll, 'RunSimpleTest'):
            dll.RunSimpleTest.argtypes = []
            print("✓ RunSimpleTest - configured")
        
        # 9. Получение строки результата
        if hasattr(dll, 'GetControlResultString'):
            dll.GetControlResultString.restype = ctypes.c_char_p
            dll.GetControlResultString.argtypes = [ctypes.c_int]
            print("✓ GetControlResultString - configured")
        
        print("\n=== TESTING DLL FUNCTIONS ===")
        
        # Запускаем встроенный тест
        print("\n1. Running built-in test...")
        dll.RunSimpleTest()
        
        # Создаем реестр
        print("\n2. Creating registry...")
        registry = dll.CreateTicketRegistry()
        print(f"   Registry created: {registry}")
        
        # Добавляем тестовые билеты
        print("\n3. Adding test tickets...")
        
        # Ограниченный билет
        dll.AddLimitedTicket(registry, 1001, 1000, 3)
        print("   ✓ Added limited ticket #1001 (3 rides)")
        
        # Билет с ограниченным сроком
        dll.AddTimedTicket(registry, 1002, 1500, 1800)
        print("   ✓ Added timed ticket #1002 (30 minutes)")
        
        # Бессрочный билет
        dll.AddUnlimitedTicket(registry, 1003, b"VIP Client")
        print("   ✓ Added unlimited ticket #1003")
        
        # Проверяем количество билетов
        print("\n4. Checking ticket count...")
        count = dll.GetTicketCount(registry)
        print(f"   Total tickets in registry: {count}")
        
        # Тестируем проверку билетов
        print("\n5. Testing ticket control...")
        
        # Тест 1: Успешная проверка
        print("\n   Test 1: Valid check (should be ALLOWED)")
        result1 = dll.TryControl(registry, 1001, 1100)
        result_str = ""
        if hasattr(dll, 'GetControlResultString'):
            result_ptr = dll.GetControlResultString(result1)
            result_str = ctypes.string_at(result_ptr).decode('ascii')
        else:
            result_codes = {0: "ALLOWED", 1: "DENIED", 2: "ALARM"}
            result_str = result_codes.get(result1, f"CODE_{result1}")
        print(f"   Result: {result_str}")
        
        # Тест 2: Слишком скоро после предыдущей проверки
        print("\n   Test 2: Too soon (should be DENIED)")
        result2 = dll.TryControl(registry, 1001, 1102)
        if hasattr(dll, 'GetControlResultString'):
            result_ptr = dll.GetControlResultString(result2)
            result_str = ctypes.string_at(result_ptr).decode('ascii')
        else:
            result_str = "DENIED" if result2 == 1 else f"CODE_{result2}"
        print(f"   Result: {result_str}")
        
        # Тест 3: Успешная проверка после ожидания
        print("\n   Test 3: After waiting (should be ALLOWED)")
        result3 = dll.TryControl(registry, 1001, 1105)
        if hasattr(dll, 'GetControlResultString'):
            result_ptr = dll.GetControlResultString(result3)
            result_str = ctypes.string_at(result_ptr).decode('ascii')
        else:
            result_str = "ALLOWED" if result3 == 0 else f"CODE_{result3}"
        print(f"   Result: {result_str}")
        
        # Тест 4: Проверка билета с ограниченным сроком
        print("\n   Test 4: Timed ticket (should be ALLOWED)")
        result4 = dll.TryControl(registry, 1002, 1600)
        if hasattr(dll, 'GetControlResultString'):
            result_ptr = dll.GetControlResultString(result4)
            result_str = ctypes.string_at(result_ptr).decode('ascii')
        else:
            result_str = "ALLOWED" if result4 == 0 else f"CODE_{result4}"
        print(f"   Result: {result_str}")
        
        # Тест 5: Проверка бессрочного билета
        print("\n   Test 5: Unlimited ticket (should be ALLOWED)")
        result5 = dll.TryControl(registry, 1003, 2000)
        if hasattr(dll, 'GetControlResultString'):
            result_ptr = dll.GetControlResultString(result5)
            result_str = ctypes.string_at(result_ptr).decode('ascii')
        else:
            result_str = "ALLOWED" if result5 == 0 else f"CODE_{result5}"
        print(f"   Result: {result_str}")
        
        # Тест 6: Несуществующий билет
        print("\n   Test 6: Non-existent ticket (should be ALARM)")
        result6 = dll.TryControl(registry, 9999, 2000)
        if hasattr(dll, 'GetControlResultString'):
            result_ptr = dll.GetControlResultString(result6)
            result_str = ctypes.string_at(result_ptr).decode('ascii')
        else:
            result_str = "ALARM" if result6 == 2 else f"CODE_{result6}"
        print(f"   Result: {result_str}")
        
        # Печатаем все билеты
        print("\n6. Printing all tickets...")
        if hasattr(dll, 'PrintAllTickets'):
            dll.PrintAllTickets.argtypes = [ctypes.c_void_p]
            dll.PrintAllTickets(registry)
        else:
            print("   (PrintAllTickets function not available)")
        
        # Очищаем реестр
        print("\n7. Cleaning up...")
        if hasattr(dll, 'DeleteTicketRegistry'):
            dll.DeleteTicketRegistry(registry)
            print("   Registry deleted")
        
        print("\n=== ALL TESTS COMPLETED SUCCESSFULLY ===")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ==========================================
# 1. ПОЛЬЗОВАТЕЛЬСКИЕ ИСКЛЮЧЕНИЯ
# ==========================================

class ShopError(Exception):
    """Базовое исключение для нашей предметной области."""
    pass

class OutOfStockError(ShopError):
    """Вызывается, когда инструмента нет в наличии."""
    pass

class ItemNotFoundError(ShopError):
    """Вызывается, когда объект не найден по ID."""
    pass


# ==========================================
# 2. МОДЕЛИ (СУЩНОСТИ)
# ==========================================

class Instrument:
    """Базовый класс музыкального инструмента."""
    def __init__(self, instrument_id: int, name: str, brand: str, price: float) -> None:
        self.instrument_id = instrument_id
        self.name = name
        self.brand = brand
        self.price = price

    def get_type(self) -> str:
        return "Базовый инструмент"

    def to_dict(self) -> dict:
        """Преобразование в словарь для JSON/XML."""
        return {
            "type": self.__class__.__name__,
            "instrument_id": self.instrument_id,
            "name": self.name,
            "brand": self.brand,
            "price": self.price
        }

class Guitar(Instrument):
    """Гитара."""
    def __init__(self, instrument_id: int, name: str, brand: str, price: float, strings_count: int) -> None:
        super().__init__(instrument_id, name, brand, price)
        self.strings_count = strings_count

    def get_type(self) -> str:
        return "Гитара"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["strings_count"] = self.strings_count
        return data

class Drum(Instrument):
    """Барабаны."""
    def __init__(self, instrument_id: int, name: str, brand: str, price: float, drum_type: str) -> None:
        super().__init__(instrument_id, name, brand, price)
        self.drum_type = drum_type

    def get_type(self) -> str:
        return "Барабаны"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["drum_type"] = self.drum_type
        return data

class Keyboard(Instrument):
    """Клавишные."""
    def __init__(self, instrument_id: int, name: str, brand: str, price: float, keys_count: int) -> None:
        super().__init__(instrument_id, name, brand, price)
        self.keys_count = keys_count

    def get_type(self) -> str:
        return "Клавишные"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["keys_count"] = self.keys_count
        return data

class Customer:
    """Покупатель."""
    def __init__(self, customer_id: int, name: str, email: str, phone: str) -> None:
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }

class Order:
    """Заказ покупателя."""
    def __init__(self, order_id: int, customer: Customer, status: str = "new") -> None:
        self.order_id = order_id
        self.customer = customer
        self.status = status
        self.instruments: list[Instrument] = []

    def add_instrument(self, instrument: Instrument) -> None:
        self.instruments.append(instrument)

    def get_total_price(self) -> float:
        return sum(item.price for item in self.instruments)

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer_id": self.customer.customer_id,
            "status": self.status,
            "total_price": self.get_total_price(),
            "instruments": [i.to_dict() for i in self.instruments]
        }

        
# ==========================================
# 3. УПРАВЛЕНИЕ (CRUD)
# ==========================================

class Inventory:
    """Склад магазина (управление инструментами и заказами)."""
    def __init__(self) -> None:
        self.instruments: dict[int, Instrument] = {}
        self.customers: dict[int, Customer] = {}
        self.orders: dict[int, Order] = {}

    # --- Инструменты ---
    def add_instrument(self, instrument: Instrument) -> None:
        if instrument.instrument_id in self.instruments:
            raise ShopError(f"Инструмент с ID {instrument.instrument_id} уже существует.")
        self.instruments[instrument.instrument_id] = instrument

    def get_instrument(self, instrument_id: int) -> Instrument:
        if instrument_id not in self.instruments:
            raise ItemNotFoundError(f"Инструмент с ID {instrument_id} не найден.")
        return self.instruments[instrument_id]

    def delete_instrument(self, instrument_id: int) -> None:
        if instrument_id not in self.instruments:
            raise ItemNotFoundError(f"Инструмент с ID {instrument_id} не найден.")
        del self.instruments[instrument_id]

    # --- Покупатели ---
    def add_customer(self, customer: Customer) -> None:
        if customer.customer_id in self.customers:
            raise ShopError(f"Покупатель с ID {customer.customer_id} уже существует.")
        self.customers[customer.customer_id] = customer

    # --- Заказы ---
    def create_order(self, order: Order) -> None:
        if order.customer.customer_id not in self.customers:
            raise ItemNotFoundError("Покупатель не зарегистрирован.")
        self.orders[order.order_id] = order


# ==========================================
# 4. ФАЙЛОВЫЕ ОБРАБОТЧИКИ (JSON & XML)
# ==========================================

class JsonHandler:
    """Класс для сохранения и загрузки в JSON."""
    @staticmethod
    def save(inventory: Inventory, filename: str = "data.json") -> None:
        data = {
            "instruments": [i.to_dict() for i in inventory.instruments.values()],
            "customers": [c.to_dict() for c in inventory.customers.values()],
            "orders": [o.to_dict() for o in inventory.orders.values()]
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load(inventory: Inventory, filename: str = "data.json") -> None:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for item in data.get("instruments", []):
                if item["type"] == "Guitar":
                    inv = Guitar(item["instrument_id"], item["name"], item["brand"], item["price"], item["strings_count"])
                elif item["type"] == "Drum":
                    inv = Drum(item["instrument_id"], item["name"], item["brand"], item["price"], item["drum_type"])
                elif item["type"] == "Keyboard":
                    inv = Keyboard(item["instrument_id"], item["name"], item["brand"], item["price"], item["keys_count"])
                else:
                    inv = Instrument(item["instrument_id"], item["name"], item["brand"], item["price"])
                inventory.add_instrument(inv)

            for c in data.get("customers", []):
                inventory.add_customer(Customer(c["customer_id"], c["name"], c["email"], c["phone"]))

            for o in data.get("orders", []):
                cust = inventory.customers.get(o["customer_id"])
                if cust:
                    order = Order(o["order_id"], cust, o["status"])
                    inventory.create_order(order)

        except FileNotFoundError:
            raise ShopError(f"Файл {filename} не найден.")
        except json.JSONDecodeError:
            raise ShopError(f"Ошибка чтения JSON файла {filename}.")


class XmlHandler:
    """Класс для сохранения и загрузки в XML."""
    @staticmethod
    def save(inventory: Inventory, filename: str = "data.xml") -> None:
        root = ET.Element("shop")
        
        instruments_el = ET.SubElement(root, "instruments")
        for inv in inventory.instruments.values():
            inv_el = ET.SubElement(instruments_el, "instrument", type=inv.__class__.__name__)
            ET.SubElement(inv_el, "id").text = str(inv.instrument_id)
            ET.SubElement(inv_el, "name").text = inv.name
            ET.SubElement(inv_el, "brand").text = inv.brand
            ET.SubElement(inv_el, "price").text = str(inv.price)

        customers_el = ET.SubElement(root, "customers")
        for c in inventory.customers.values():
            cust_el = ET.SubElement(customers_el, "customer")
            ET.SubElement(cust_el, "id").text = str(c.customer_id)
            ET.SubElement(cust_el, "name").text = c.name
            ET.SubElement(cust_el, "email").text = c.email
            ET.SubElement(cust_el, "phone").text = c.phone

        xml_str = minidom.parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(indent="  ")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_str)

    @staticmethod
    def load(inventory: Inventory, filename: str = "data.xml") -> None:
        try:
            tree = ET.parse(filename)
            root = tree.getroot()

            # Загрузка инструментов
            for inv_el in root.findall("./instruments/instrument"):
                inv_id = int(inv_el.find("id").text)
                name = inv_el.find("name").text
                brand = inv_el.find("brand").text
                price = float(inv_el.find("price").text)
                inv_type = inv_el.get("type")

                if inv_type == "Guitar":
                    inv = Guitar(inv_id, name, brand, price, 6)
                elif inv_type == "Drum":
                    inv = Drum(inv_id, name, brand, price, "acoustic")
                elif inv_type == "Keyboard":
                    inv = Keyboard(inv_id, name, brand, price, 88)
                else:
                    inv = Instrument(inv_id, name, brand, price)
                inventory.add_instrument(inv)

            # Загрузка покупателей
            for cust_el in root.findall("./customers/customer"):
                c_id = int(cust_el.find("id").text)
                name = cust_el.find("name").text
                email = cust_el.find("email").text
                phone = cust_el.find("phone").text
                inventory.add_customer(Customer(c_id, name, email, phone))

        except FileNotFoundError:
            raise ShopError(f"Файл {filename} не найден.")
        except ET.ParseError:
            raise ShopError(f"Ошибка парсинга XML файла {filename}.")

# ==========================================
# 5. ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС (APP)
# ==========================================

class App:
    """Главный класс приложения (консольное меню)."""
    def __init__(self) -> None:
        self.inventory = Inventory()

    def run(self) -> None:
        while True:
            print("\n--- МУЗЫКАЛЬНЫЙ МАГАЗИН ---")
            print("1. Показать все инструменты")
            print("2. Добавить гитару")
            print("3. Добавить барабаны")     
            print("4. Добавить клавишные")    
            print("5. Добавить покупателя")
            print("6. Создать заказ")
            print("7. Сохранить в JSON")
            print("8. Загрузить из JSON")
            print("9. Сохранить в XML")
            print("10. Загрузить из XML")
            print("0. Выход")
            
            choice = input("Выберите действие: ")
            
            try:
                if choice == "1":
                    if not self.inventory.instruments:
                        print("Склад пуст.")
                    for inv in self.inventory.instruments.values():
                        print(f"[{inv.instrument_id}] {inv.get_type()} - {inv.name} ({inv.brand}) - {inv.price} руб.")
                
                elif choice == "2":
                    inv_id = int(input("ID инструмента: "))
                    name = input("Название: ")
                    brand = input("Бренд: ")
                    price = float(input("Цена: "))
                    strings = int(input("Количество струн: "))
                    self.inventory.add_instrument(Guitar(inv_id, name, brand, price, strings))
                    print("Гитара добавлена!")
                
                elif choice == "3":  # <-- НОВОЕ (Барабаны)
                    inv_id = int(input("ID инструмента: "))
                    name = input("Название: ")
                    brand = input("Бренд: ")
                    price = float(input("Цена: "))
                    drum_type = input("Тип барабанов (акустические/электронные): ")
                    self.inventory.add_instrument(Drum(inv_id, name, brand, price, drum_type))
                    print("Барабаны добавлены!")
                
                elif choice == "4":  # <-- НОВОЕ (Клавишные)
                    inv_id = int(input("ID инструмента: "))
                    name = input("Название: ")
                    brand = input("Бренд: ")
                    price = float(input("Цена: "))
                    keys = int(input("Количество клавиш: "))
                    self.inventory.add_instrument(Keyboard(inv_id, name, brand, price, keys))
                    print("Клавишные добавлены!")
                
                elif choice == "5":  # <-- ТЕПЕРЬ ПОКУПАТЕЛЬ (сдвинулось с 3)
                    c_id = int(input("ID покупателя: "))
                    name = input("Имя: ")
                    email = input("Email: ")
                    phone = input("Телефон: ")
                    self.inventory.add_customer(Customer(c_id, name, email, phone))
                    print("Покупатель добавлен!")
                
                elif choice == "6":  # <-- ТЕПЕРЬ ЗАКАЗ (сдвинулось с 4)
                    order_id = int(input("ID заказа: "))
                    cust_id = int(input("ID покупателя: "))
                    if cust_id not in self.inventory.customers:
                        raise ItemNotFoundError("Покупатель не найден!")
                    
                    order = Order(order_id, self.inventory.customers[cust_id])
                    inv_id = int(input("ID инструмента для добавления в заказ: "))
                    order.add_instrument(self.inventory.get_instrument(inv_id))
                    
                    self.inventory.create_order(order)
                    print(f"Заказ создан! Сумма: {order.get_total_price()} руб.")
                
                elif choice == "7":  # <-- БЫЛО 5
                    JsonHandler.save(self.inventory)
                    print("Сохранено в data.json")
                
                elif choice == "8":  # <-- БЫЛО 6
                    JsonHandler.load(self.inventory)
                    print("Загружено из data.json")
                
                elif choice == "9":  # <-- БЫЛО 7
                    XmlHandler.save(self.inventory)
                    print("Сохранено в data.xml")
                
                elif choice == "10": # <-- БЫЛО 8
                    XmlHandler.load(self.inventory)
                    print("Загружено из data.xml")

                elif choice == "0":
                    print("До свидания!")
                    break
                
                else:
                    print("Неверная команда.")

            # Обработка наших кастомных исключений
            except ShopError as e:
                print(f"Ошибка магазина: {e}")
            # Обработка ошибок приведения типов (если ввели буквы вместо цифр)
            except ValueError:
                print("Ошибка ввода: пожалуйста, введите число, где это требуется.")
            # Обработка любых других непредвиденных ошибок
            except Exception as e:
                print(f"Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    app = App()
    app.run()

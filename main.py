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

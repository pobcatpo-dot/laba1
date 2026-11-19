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
        return {
            "type": self.__class__.__name__,
            "instrument_id": self.instrument_id,
            "name": self.name,
            "brand": self.brand,
            "price": self.price
        }

class Guitar(Instrument):
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

    def add_customer(self, customer: Customer) -> None:
        if customer.customer_id in self.customers:
            raise ShopError(f"Покупатель с ID {customer.customer_id} уже существует.")
        self.customers[customer.customer_id] = customer

    def create_order(self, order: Order) -> None:
        if order.customer.customer_id not in self.customers:
            raise ItemNotFoundError("Покупатель не зарегистрирован.")
        self.orders[order.order_id] = order

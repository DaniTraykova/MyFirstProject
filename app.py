import streamlit as st
from abc import ABC, abstractmethod

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"],
    "България → Италия": ["София", "Скопие", "Рим", "Флоренция"],
    "България → Франция": ["София", "Белград", "Будапеща", "Париж"],
    "България → Испания": ["София", "Милано", "Барселона"],
    "България → Австрия": ["София", "Белград", "Виена"]
}

city_info = {
    "София": {
        "hotel": ("Hotel Sofia Center", 70),
        "food": ("Традиционна българска кухня", 20),
        "sight": "Катедралата Александър Невски"
    },
    "Белград": {
        "hotel": ("Belgrade Inn", 65),
        "food": ("Сръбска скара", 22),
        "sight": "Калемегдан"
    },
    "Виена": {
        "hotel": ("Vienna City Hotel", 90),
        "food": ("Виенски шницел", 30),
        "sight": "Дворецът Шьонбрун"
    },
    "Мюнхен": {
        "hotel": ("Munich Central Hotel", 95),
        "food": ("Немска кухня", 28),
        "sight": "Мариенплац"
    },
    "Скопие": {
        "hotel": ("Skopje City Hotel", 60),
        "food": ("Македонска кухня", 18),
        "sight": "Каменният мост"
    },
    "Рим": {
        "hotel": ("Rome Center Hotel", 100),
        "food": ("Италианска паста", 35),
        "sight": "Колизеумът"
    },
    "Флоренция": {
        "hotel": ("Florence Art Hotel", 95),
        "food": ("Тосканска кухня", 32),
        "sight": "Катедралата Санта Мария дел Фиоре"
    },
    "Будапеща": {
        "hotel": ("Budapest Danube Hotel", 85),
        "food": ("Унгарски гулаш", 25),
        "sight": "Парламентът"
    },
    "Париж": {
        "hotel": ("Paris Central Hotel", 110),
        "food": ("Френска кухня", 40),
        "sight": "Айфеловата кула"
    },
    "Милано": {
        "hotel": ("Milano Fashion Hotel", 105),
        "food": ("Италианска кухня", 34),
        "sight": "Катедралата Дуомо"
    },
    "Барселона": {
        "hotel": ("Barcelona Beach Hotel", 100),
        "food": ("Испански тапас", 30),
        "sight": "Саграда Фамилия"
    }
}

DISTANCE_BETWEEN_CITIES = 300  # км (опростено)

# ================== OOP ==================

class Transport(ABC):
    def __init__(self, price_per_km):
        self.price_per_km = price_per_km

    @abstractmethod
    def name(self):
        pass

    def travel_cost(self, distance):
        return distance * self.price_per_km


class Car(Transport):
    def __init__(self):
        super().__init__(0.25)

    def name(self):
        return "🚗 Кола"


class Train(Transport):
    def __init__(self):
        super().__init__(0.18)

    def name(self):
        return "🚆 Влак"


class Plane(Transport):
    def __init__(self):
        super().__init__(0.45)

    def name(self):
        return "✈️ Самолет"

# ================== UI ==================

st.title("🌍 Интерактивен туристически планер")

route_choice = st.selectbox(
    "Избери маршрут:",
    list(routes.keys())
)

transport_choice = st.selectbox(
    "Превозно средство:",
    ["Кола", "Влак", "Самолет"]
)

hotel_stars = st.selectbox(
    "Категория хотел:",
    ["⭐ Бюджетен", "⭐⭐ Стандартен", "⭐⭐⭐ Луксозен"]
)

days = st.slider("Брой дни за пътуването:", 1, 10, 4)
budget = st.number_input("Твоят бюджет (лв):", 300, 5000, 1500)

hotel_multiplier = {
    "⭐ Бюджетен": 0.8,
    "⭐⭐ Стандартен": 1.0,
    "⭐⭐⭐ Луксозен": 1.4
}

if st.button("Планирай пътуването 🧭"):
    cities = routes[route_choice]

    # Избор на транспорт (полиморфизъм)
    if transport_choice == "Кола":
        transport = Car()
    elif transport_choice == "Влак":
        transport = Train()
    else:
        transport = Plane()

    st.subheader("🗺️ Маршрут")
    st.write(" ➡️ ".join(cities))

    # ================== CITY DETAILS ==================
    st.subheader("🏙️ Спирки и предложения")

    total_food_cost = 0
    total_hotel_cost = 0

    for city in cities:
        info = city_info[city]

        hotel_price = info['hotel'][1] * hotel_multiplier[hotel_stars]

        st.markdown(f"### 📍 {city}")
        st.write(
            f"🏨 **Хотел ({hotel_stars}):** {info['hotel'][0]} – {hotel_price:.2f} лв/нощ"
        )
        st.write(f"🍽️ **Храна:** {info['food'][0]} – {info['food'][1]} лв/ден")
        st.write(f"🏛️ **Забележителност:** {info['sight']}")

        total_food_cost += info['food'][1] * days
        total_hotel_cost += hotel_price * days

    # ================== COST CALCULATION ==================
    total_distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(total_distance)

    total_cost = transport_cost + total_food_cost + total_hotel_cost

    # ================== RESULTS ==================
    st.subheader("💰 Разходи")

    st.write(f"{transport.name()} – транспорт: {transport_cost:.2f} лв")
    st.write(f"🍽️ Храна: {total_food_cost:.2f} лв")
    st.write(f"🏨 Хотели: {total_hotel_cost:.2f} лв")

    st.markdown("---")
    st.write(f"## 💵 Общ бюджет: **{total_cost:.2f} лв**")

    if total_cost <= budget:
        st.success("✅ Бюджетът е достатъчен! Приятно пътуване ✨")
    else:
        st.error("❌ Бюджетът не достига. Помисли за по-евтин транспорт, хотел или по-малко дни.")


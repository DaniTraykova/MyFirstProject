import streamlit as st
from abc import ABC, abstractmethod
import pydeck as pdk

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"],
    "България → Италия": ["София", "Скопие", "Рим", "Флоренция"],
    "България → Франция": ["София", "Белград", "Будапеща", "Париж"],
    "България → Испания": ["София", "Милано", "Барселона"],
    "България → Австрия": ["София", "Белград", "Виена"]
}

city_info = {
    "София": {"hotel": ("Hotel Sofia Center", 70), "food": ("Българска кухня", 20), "sight": "Катедралата Александър Невски"},
    "Белград": {"hotel": ("Belgrade Inn", 65), "food": ("Сръбска скара", 22), "sight": "Калемегдан"},
    "Виена": {"hotel": ("Vienna City Hotel", 90), "food": ("Виенски шницел", 30), "sight": "Дворецът Шьонбрун"},
    "Мюнхен": {"hotel": ("Munich Central Hotel", 95), "food": ("Немска кухня", 28), "sight": "Мариенплац"},
    "Скопие": {"hotel": ("Skopje City Hotel", 60), "food": ("Македонска кухня", 18), "sight": "Каменният мост"},
    "Рим": {"hotel": ("Rome Center Hotel", 100), "food": ("Италианска паста", 35), "sight": "Колизеумът"},
    "Флоренция": {"hotel": ("Florence Art Hotel", 95), "food": ("Тосканска кухня", 32), "sight": "Санта Мария дел Фиоре"},
    "Будапеща": {"hotel": ("Budapest Danube Hotel", 85), "food": ("Унгарски гулаш", 25), "sight": "Парламентът"},
    "Париж": {"hotel": ("Paris Central Hotel", 110), "food": ("Френска кухня", 40), "sight": "Айфеловата кула"},
    "Милано": {"hotel": ("Milano Fashion Hotel", 105), "food": ("Италианска кухня", 34), "sight": "Катедралата Дуомо"},
    "Барселона": {"hotel": ("Barcelona Beach Hotel", 100), "food": ("Испански тапас", 30), "sight": "Саграда Фамилия"}
}

city_coords = {
    "София": [23.3219, 42.6977],
    "Белград": [20.4489, 44.7866],
    "Виена": [16.3738, 48.2082],
    "Мюнхен": [11.5820, 48.1351],
    "Скопие": [21.4254, 41.9981],
    "Рим": [12.4964, 41.9028],
    "Флоренция": [11.2558, 43.7696],
    "Будапеща": [19.0402, 47.4979],
    "Париж": [2.3522, 48.8566],
    "Милано": [9.1900, 45.4642],
    "Барселона": [2.1734, 41.3851]
}

DISTANCE_BETWEEN_CITIES = 300

# ================== OOP ==================

class Transport(ABC):
    def __init__(self, price_per_km, icon):
        self.price_per_km = price_per_km
        self.icon = icon

    def travel_cost(self, distance):
        return distance * self.price_per_km

class Car(Transport):
    def __init__(self):
        super().__init__(0.25, "🚗")

class Train(Transport):
    def __init__(self):
        super().__init__(0.18, "🚆")

class Plane(Transport):
    def __init__(self):
        super().__init__(0.45, "✈️")

# ================== UI ==================

st.title("🌍 Интерактивен туристически планер")

route_choice = st.selectbox("Избери маршрут:", list(routes.keys()))
transport_choice = st.selectbox("Превозно средство:", ["Кола", "Влак", "Самолет"])
hotel_stars = st.selectbox("Категория хотел:", ["⭐ Бюджетен", "⭐⭐ Стандартен", "⭐⭐⭐ Луксозен"])

days = st.slider("Брой дни:", 1, 14, 7)
budget = st.number_input("Бюджет (лв):", 300, 8000, 2000)

hotel_multiplier = {
    "⭐ Бюджетен": 0.8,
    "⭐⭐ Стандартен": 1.0,
    "⭐⭐⭐ Луксозен": 1.4
}

if st.button("🧭 Планирай пътуването"):

    cities = routes[route_choice]
    transport = Car() if transport_choice == "Кола" else Train() if transport_choice == "Влак" else Plane()

    # ================== MAP ==================

    st.subheader("🗺️ Карта на маршрута")

    path = [city_coords[c] for c in cities]

    map_layer = pdk.Layer(
        "PathLayer",
        data=[{"path": path}],
        get_path="path",
        get_color=[255, 0, 0],
        width_scale=20,
        width_min_pixels=4
    )

    view_state = pdk.ViewState(
        longitude=path[0][0],
        latitude=path[0][1],
        zoom=4
    )

    st.pydeck_chart(pdk.Deck(
        layers=[map_layer],
        initial_view_state=view_state,
        tooltip={"text": f"Превоз: {transport.icon}"}
    ))

    # ================== COST ==================

    total_food = 0
    total_hotel = 0

    for city in cities:
        total_food += city_info[city]["food"][1] * days
        total_hotel += city_info[city]["hotel"][1] * hotel_multiplier[hotel_stars] * days

    total_distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(total_distance)
    total_cost = total_food + total_hotel + transport_cost

    # ================== DETAILED PLAN ==================

    st.subheader("📘 Подробен план на пътуването")

    st.markdown(f"""
### 🚦 Тръгване
- Начален град: **{cities[0]}**
- Превозно средство: {transport.icon} **{transport_choice}**
- Обща дистанция: **{total_distance} км**
    """)

    st.markdown("---")

    for i, city in enumerate(cities):
        info = city_info[city]
        hotel_price = info["hotel"][1] * hotel_multiplier[hotel_stars]

        st.markdown(f"""
### 📍 Ден {i + 1} – {city}

**🚍 Пътуване:**  
{transport.icon} от **{cities[i-1] if i > 0 else city} → {city}**

**🏨 Настаняване:**  
- Хотел: *{info['hotel'][0]}*  
- Категория: {hotel_stars}  
- Цена: **{hotel_price:.2f} лв / нощ**

**🍽️ Хранене:**  
- Тип кухня: {info['food'][0]}  
- Средна цена: **{info['food'][1]} лв / ден**

**🏛️ Забележителности:**  
- {info['sight']}

**🕒 Свободно време:**  
- Разходка в центъра  
- Посещение на местни заведения  
""")

        st.markdown("---")

    st.markdown(f"""
### 🏁 Пристигане
- Краен град: **{cities[-1]}**
- Продължителност: **{days} дни**
- Обща цена: **{total_cost:.2f} лв**
    """)

    # ================== RESULT ==================

    st.subheader("💰 Финансова справка")
    st.write(f"{transport.icon} Транспорт: {transport_cost:.2f} лв")
    st.write(f"🍽️ Храна: {total_food:.2f} лв")
    st.write(f"🏨 Хотели: {total_hotel:.2f} лв")

    if total_cost <= budget:
        st.success("✅ Бюджетът е достатъчен! Приятно пътуване ✨")
    else:
        st.error("❌ Бюджетът не достига. Помисли за по-евтин вариант.")

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
    "София": {"hotel": ("Hotel Sofia Center", 70), "food": ("Българска кухня", 20), "sight": "Александър Невски"},
    "Белград": {"hotel": ("Belgrade Inn", 65), "food": ("Сръбска скара", 22), "sight": "Калемегдан"},
    "Виена": {"hotel": ("Vienna City Hotel", 90), "food": ("Виенски шницел", 30), "sight": "Шьонбрун"},
    "Мюнхен": {"hotel": ("Munich Central Hotel", 95), "food": ("Немска кухня", 28), "sight": "Мариенплац"},
    "Скопие": {"hotel": ("Skopje City Hotel", 60), "food": ("Македонска кухня", 18), "sight": "Каменният мост"},
    "Рим": {"hotel": ("Rome Center Hotel", 100), "food": ("Паста", 35), "sight": "Колизеум"},
    "Флоренция": {"hotel": ("Florence Art Hotel", 95), "food": ("Тосканска кухня", 32), "sight": "Катедралата"},
    "Будапеща": {"hotel": ("Budapest Danube Hotel", 85), "food": ("Гулаш", 25), "sight": "Парламентът"},
    "Париж": {"hotel": ("Paris Central Hotel", 110), "food": ("Френска кухня", 40), "sight": "Айфеловата кула"},
    "Милано": {"hotel": ("Milano Fashion Hotel", 105), "food": ("Италианска кухня", 34), "sight": "Дуомо"},
    "Барселона": {"hotel": ("Barcelona Beach Hotel", 100), "food": ("Тапас", 30), "sight": "Саграда Фамилия"}
}

# Координати на градовете
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
hotel_stars = st.selectbox("Категория хотел:", ["⭐", "⭐⭐", "⭐⭐⭐"])

days = st.slider("Брой дни:", 1, 10, 4)
budget = st.number_input("Бюджет (лв):", 300, 5000, 1500)

hotel_multiplier = {"⭐": 0.8, "⭐⭐": 1.0, "⭐⭐⭐": 1.4}

if st.button("Планирай пътуването 🧭"):
    cities = routes[route_choice]

    transport = Car() if transport_choice == "Кола" else Train() if transport_choice == "Влак" else Plane()

    # ================== MAP ==================
    st.subheader("🗺️ Карта на маршрута")

    path = [city_coords[city] for city in cities]

    layer = pdk.Layer(
        "PathLayer",
        data=[{"path": path, "name": transport.icon}],
        get_path="path",
        get_color=[255, 0, 0],
        width_scale=20,
        width_min_pixels=4,
        pickable=True
    )

    view_state = pdk.ViewState(
        longitude=path[0][0],
        latitude=path[0][1],
        zoom=4,
        pitch=0
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": f"Превоз: {transport.icon}"}
    ))

    # ================== COST ==================
    total_food = 0
    total_hotel = 0

    for city in cities:
        info = city_info[city]
        total_food += info["food"][1] * days
        total_hotel += info["hotel"][1] * hotel_multiplier[hotel_stars] * days

    total_distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(total_distance)

    total_cost = total_food + total_hotel + transport_cost

    st.subheader("💰 Разходи")
    st.write(f"{transport.icon} Транспорт: {transport_cost:.2f} лв")
    st.write(f"🍽️ Храна: {total_food:.2f} лв")
    st.write(f"🏨 Хотели: {total_hotel:.2f} лв")
    st.write(f"## Общо: {total_cost:.2f} лв")

    if total_cost <= budget:
        st.success("✅ Бюджетът стига!")
    else:
        st.error("❌ Бюджетът не стига.")


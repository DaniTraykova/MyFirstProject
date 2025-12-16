import streamlit as st
from abc import ABC
import pydeck as pdk

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"],
    "България → Италия": ["София", "Скопие", "Рим", "Флоренция"],
    "България → Франция": ["София", "Белград", "Будапеща", "Париж"]
}

city_info = {
    "София": {"hotel": ("Hotel Sofia Center", 70), "food": ("Българска кухня", 20), "sight": "Александър Невски"},
    "Белград": {"hotel": ("Belgrade Inn", 65), "food": ("Сръбска скара", 22), "sight": "Калемегдан"},
    "Виена": {"hotel": ("Vienna City Hotel", 90), "food": ("Виенски шницел", 30), "sight": "Шьонбрун"},
    "Мюнхен": {"hotel": ("Munich Central Hotel", 95), "food": ("Немска кухня", 28), "sight": "Мариенплац"},
    "Скопие": {"hotel": ("Skopje City Hotel", 60), "food": ("Македонска кухня", 18), "sight": "Каменният мост"},
    "Рим": {"hotel": ("Rome Center Hotel", 100), "food": ("Паста", 35), "sight": "Колизеум"},
    "Флоренция": {"hotel": ("Florence Art Hotel", 95), "food": ("Тосканска кухня", 32), "sight": "Катедралата"},
    "Будапеща": {"hotel": ("Budapest Hotel", 85), "food": ("Гулаш", 25), "sight": "Парламентът"},
    "Париж": {"hotel": ("Paris Central", 110), "food": ("Френска кухня", 40), "sight": "Айфеловата кула"}
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
    "Париж": [2.3522, 48.8566]
}

DISTANCE = 300

# ================== TRANSPORT ==================

class Transport:
    def __init__(self, name, price, icon):
        self.name = name
        self.price = price
        self.icon = icon

    def cost(self, distance):
        return distance * self.price

transports = {
    "Кола": Transport("Кола", 0.25, "🚗"),
    "Влак": Transport("Влак", 0.18, "🚆"),
    "Самолет": Transport("Самолет", 0.45, "✈️")
}

# ================== SIDEBAR ==================

st.sidebar.title("🧭 Настройки")

route_choice = st.sidebar.selectbox("Маршрут:", list(routes.keys()))
hotel_stars = st.sidebar.selectbox("Хотел:", ["⭐", "⭐⭐", "⭐⭐⭐"])
days = st.sidebar.slider("Брой дни:", 1, 14, 7)
budget = st.sidebar.number_input("Бюджет (лв):", 500, 10000, 2500)

hotel_multiplier = {"⭐": 0.8, "⭐⭐": 1.0, "⭐⭐⭐": 1.4}

cities = routes[route_choice]

st.sidebar.markdown("### 🚍 Транспорт по етапи")

segment_transports = []
for i in range(len(cities) - 1):
    choice = st.sidebar.selectbox(
        f"{cities[i]} → {cities[i+1]}",
        list(transports.keys()),
        key=i
    )
    segment_transports.append(transports[choice])

# ================== MAIN ==================

st.title("🌍 Интерактивен туристически планер")

if st.button("Планирай пътуването"):

    # ================== MAP ==================

    path = [city_coords[c] for c in cities]

    path_layer = pdk.Layer(
        "PathLayer",
        data=[{"path": path}],
        get_path="path",
        get_color=[255, 0, 0],
        width_min_pixels=4
    )

    # Иконки по средата на всеки етап
    icons = []
    for i in range(len(path) - 1):
        mid_lon = (path[i][0] + path[i+1][0]) / 2
        mid_lat = (path[i][1] + path[i+1][1]) / 2
        icons.append({
            "position": [mid_lon, mid_lat],
            "text": segment_transports[i].icon
        })

    text_layer = pdk.Layer(
        "TextLayer",
        data=icons,
        get_position="position",
        get_text="text",
        get_size=24
    )

    view = pdk.ViewState(
        longitude=path[0][0],
        latitude=path[0][1],
        zoom=4
    )

    st.pydeck_chart(pdk.Deck(
        layers=[path_layer, text_layer],
        initial_view_state=view
    ))

    # ================== COST ==================

    transport_cost = sum(t.cost(DISTANCE) for t in segment_transports)
    food_cost = sum(city_info[c]["food"][1] for c in cities) * days
    hotel_cost = sum(city_info[c]["hotel"][1] for c in cities) * hotel_multiplier[hotel_stars] * days

    total_cost = transport_cost + food_cost + hotel_cost

    # ================== DETAILS ==================

    st.subheader("📘 Подробна информация")

    for i, city in enumerate(cities):
        info = city_info[city]
        st.markdown(f"""
### 📍 {city}

🏨 **Хотел:** {info['hotel'][0]} ({hotel_stars})  
🍽️ **Храна:** {info['food'][0]}  
🏛️ **Забележителност:** {info['sight']}
""")

        if i < len(segment_transports):
            st.markdown(
                f"➡️ **Следващ етап:** {segment_transports[i].icon} {segment_transports[i].name}"
            )

    # ================== RESULT ==================

    st.subheader("💰 Разходи")
    st.write(f"🚍 Транспорт: {transport_cost:.2f} лв")
    st.write(f"🍽️ Храна: {food_cost:.2f} лв")
    st.write(f"🏨 Хотели: {hotel_cost:.2f} лв")
    st.write(f"## Общо: {total_cost:.2f} лв")

    if total_cost <= budget:
        st.success("✅ Бюджетът е достатъчен!")
    else:
        st.error("❌ Бюджетът не достига.")

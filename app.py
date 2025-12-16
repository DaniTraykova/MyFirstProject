import streamlit as st
import pydeck as pdk

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"],
    "България → Италия": ["София", "Скопие", "Рим", "Флоренция"],
    "България → Франция": ["София", "Белград", "Будапеща", "Париж"]
}

city_info = {
    "София": {"hotel": ("Hotel Sofia Center", 70), "food": 20, "sight": "Александър Невски"},
    "Белград": {"hotel": ("Belgrade Inn", 65), "food": 22, "sight": "Калемегдан"},
    "Виена": {"hotel": ("Vienna City Hotel", 90), "food": 30, "sight": "Шьонбрун"},
    "Мюнхен": {"hotel": ("Munich Central Hotel", 95), "food": 28, "sight": "Мариенплац"},
    "Скопие": {"hotel": ("Skopje City Hotel", 60), "food": 18, "sight": "Каменният мост"},
    "Рим": {"hotel": ("Rome Center Hotel", 100), "food": 35, "sight": "Колизеум"},
    "Флоренция": {"hotel": ("Florence Art Hotel", 95), "food": 32, "sight": "Катедралата"},
    "Будапеща": {"hotel": ("Budapest Hotel", 85), "food": 25, "sight": "Парламентът"},
    "Париж": {"hotel": ("Paris Central", 110), "food": 40, "sight": "Айфеловата кула"}
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

hotel_multiplier = {"⭐": 0.8, "⭐⭐": 1.0, "⭐⭐⭐": 1.4}

transports = {
    "Кола": {"price": 0.25, "icon": "🚗"},
    "Влак": {"price": 0.18, "icon": "🚆"},
    "Самолет": {"price": 0.45, "icon": "✈️"}
}

# ================== SIDEBAR ==================

st.sidebar.title("🧭 Настройки")

route_choice = st.sidebar.selectbox("Маршрут:", list(routes.keys()))
days = st.sidebar.slider("Брой дни:", 1, 14, 7)
budget = st.sidebar.number_input("Бюджет (лв):", 500, 10000, 2500)

cities = routes[route_choice]

st.sidebar.markdown("### 🏨 Хотел по град")
city_hotels = {}
for city in cities:
    city_hotels[city] = st.sidebar.selectbox(
        f"{city}",
        ["⭐", "⭐⭐", "⭐⭐⭐"],
        key=f"hotel_{city}"
    )

st.sidebar.markdown("### 🚍 Транспорт по етапи")
segment_transports = []
for i in range(len(cities) - 1):
    t = st.sidebar.selectbox(
        f"{cities[i]} → {cities[i+1]}",
        list(transports.keys()),
        key=f"transport_{i}"
    )
    segment_transports.append(transports[t])

# ================== MAIN ==================

st.title("🌍 Интерактивен туристически планер")

if st.button("🧭 Планирай пътуването"):

    # ================== MAP ==================

    path = [city_coords[c] for c in cities]

    path_layer = pdk.Layer(
        "PathLayer",
        data=[{"path": path}],
        get_path="path",
        get_color=[255, 0, 0],
        width_min_pixels=4
    )

    # ИКОНКИ НА ТРАНСПОРТА (по средата на всеки етап)
    transport_icons = []
    for i in range(len(path) - 1):
        mid_lon = (path[i][0] + path[i + 1][0]) / 2
        mid_lat = (path[i][1] + path[i + 1][1]) / 2
        transport_icons.append({
            "position": [mid_lon, mid_lat],
            "icon": segment_transports[i]["icon"]
        })

    transport_layer = pdk.Layer(
        "TextLayer",
        data=transport_icons,
        get_position="position",
        get_text="icon",
        get_size=28,
        get_color=[0, 0, 0]
    )

    view = pdk.ViewState(
        longitude=path[0][0],
        latitude=path[0][1],
        zoom=4
    )

    st.pydeck_chart(pdk.Deck(
        layers=[path_layer, transport_layer],
        initial_view_state=view
    ))

    # ================== COST ==================

    transport_cost = sum(t["price"] * DISTANCE for t in segment_transports)

    food_cost = sum(city_info[c]["food"] for c in cities) * days

    hotel_cost = 0
    for city in cities:
        base_price = city_info[city]["hotel"][1]
        hotel_cost += base_price * hotel_multiplier[city_hotels[city]] * days

    total_cost = transport_cost + food_cost + hotel_cost

    # ================== DETAILS ==================

    st.subheader("📘 Подробна информация за пътуването")

    for i, city in enumerate(cities):
        info = city_info[city]
        st.markdown(f"""
### 📍 {city}

🏨 **Хотел:** {info['hotel'][0]} ({city_hotels[city]})  
🍽️ **Храна:** ~ {info['food']} лв / ден  
🏛️ **Забележителност:** {info['sight']}
""")
        if i < len(segment_transports):
            st.markdown(
                f"➡️ **Следващ етап:** {segment_transports[i]['icon']}"
            )

    # ================== RESULT ==================

    st.subheader("💰 Разходи")
    st.write(f"🚍 Транспорт: {transport_cost:.2f} лв")
    st.write(f"🍽️ Храна: {food_cost:.2f} лв")
    st.write(f"🏨 Хотели: {hotel_cost:.2f} лв")
    st.write(f"## Общо: {total_cost:.2f} лв")

    if total_cost <= budget:
        st.success("✅ Бюджетът е достатъчен! Приятно пътуване ✨")
    else:
        st.error("❌ Бюджетът не достига.")

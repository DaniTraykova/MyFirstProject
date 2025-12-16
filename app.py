import streamlit as st
import pydeck as pdk
from datetime import datetime

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"],
    "България → Италия": ["София", "Скопие", "Рим", "Флоренция"],
    "България → Франция": ["София", "Белград", "Будапеща", "Париж"],
    "България → Испания": ["София", "Милано", "Барселона"]
}

city_info = {
    "София": {
        "coords": [23.3219, 42.6977],
        "hotels": [
            ("Hotel Europe Sofia", 120, "https://www.booking.com/hotel/bg/europe-bg.html"),
            ("easyHotel Sofia", 40, "https://www.booking.com/hotel/bg/easyhotel-sofia.html")
        ],
        "food_price": 20,
        "sight": "Катедралата Александър Невски"
    },
    "Белград": {
        "coords": [20.4489, 44.7866],
        "hotels": [
            ("Hotel Moskva", 130, "https://www.booking.com/hotel/rs/moskva.html"),
            ("Square Nine Hotel", 220, "https://www.booking.com/hotel/rs/square-nine.html")
        ],
        "food_price": 22,
        "sight": "Калемегдан"
    },
    "Виена": {
        "coords": [16.3738, 48.2082],
        "hotels": [
            ("The Guesthouse Vienna", 350, "https://www.booking.com/hotel/at/the-guesthouse-vienna.html"),
            ("Hotel Sacher Wien", 500, "https://www.booking.com/hotel/at/sacher-wien.html")
        ],
        "food_price": 30,
        "sight": "Дворецът Шьонбрун"
    },
    "Мюнхен": {
        "coords": [11.5820, 48.1351],
        "hotels": [
            ("Hotel Bayerischer Hof", 420, "https://www.booking.com/hotel/de/bayerischer-hof.html"),
            ("Marc München", 150, "https://www.booking.com/hotel/de/marc-munchen.html")
        ],
        "food_price": 28,
        "sight": "Мариенплац"
    },
    "Рим": {
        "coords": [12.4964, 41.9028],
        "hotels": [
            ("Hotel Milano Castello", 330, "https://www.booking.com/hotel/it/milano-castello.html"),
            ("Navona Palace Luxury Inn", 280, "https://www.booking.com/hotel/it/navona-palace-luxury-inn.html")
        ],
        "food_price": 35,
        "sight": "Колизеум"
    },
    "Флоренция": {
        "coords": [11.2558, 43.7696],
        "hotels": [
            ("Hotel Davanzati", 240, "https://www.booking.com/hotel/it/davanzati.html"),
            ("FH Grand Hotel Mediterraneo", 210, "https://www.booking.com/hotel/it/grand-hotelfh-mediterraneo.html")
        ],
        "food_price": 32,
        "sight": "Катедралата Санта Мария дел Фиоре"
    },
    "Барселона": {
        "coords": [2.1734, 41.3851],
        "hotels": [
            ("Hotel 1898", 280, "https://www.booking.com/hotel/es/colon-1898.html"),
            ("H10 Cubik", 260, "https://www.booking.com/hotel/es/h10-cubik.html")
        ],
        "food_price": 30,
        "sight": "Саграда Фамилия"
    }
}

transports = {
    "Кола": {"price_per_km": 0.25, "icon": "🚗"},
    "Влак": {"price_per_km": 0.18, "icon": "🚆"},
    "Самолет": {"price_per_km": 0.45, "icon": "✈️"}
}

DISTANCE = 300  # базово

# ================== SIDEBAR ==================

st.sidebar.title("🧭 Туристически планер")

route_choice = st.sidebar.selectbox("Маршрут:", list(routes.keys()))

checkin = st.sidebar.date_input("Начална дата (Check‑in)", datetime.today())
checkout = st.sidebar.date_input("Крайна дата (Check‑out)", datetime.today())

days = (checkout - checkin).days
if days < 1:
    st.sidebar.error("Дата на напускане трябва да е след началната!")
    st.stop()

city_hotel_choices = {}
for city in routes[route_choice]:
    city_hotel_choices[city] = st.sidebar.selectbox(
        f"Хотел в {city}",
        [h[0] for h in city_info[city]["hotels"]],
        key=f"hotel_{city}"
    )

segment_transports = []
for i in range(len(routes[route_choice]) - 1):
    mode = st.sidebar.selectbox(
        f"{routes[route_choice][i]} → {routes[route_choice][i+1]}",
        list(transports.keys()),
        key=f"transp_{i}"
    )
    segment_transports.append(transports[mode])

# ================== MAIN ==================

st.title("🌍 Персонализиран туристически план")

if st.button("🎒 Създай план"):

    cities = routes[route_choice]
    path = [city_info[c]["coords"] for c in cities]

    # --- Map ---
    path_layer = pdk.Layer(
        "PathLayer",
        data=[{"path": path}],
        get_color=[255, 0, 0],
        width_min_pixels=4
    )

    icon_data = []
    for i in range(len(path)-1):
        mid_lon = (path[i][0] + path[i+1][0]) / 2
        mid_lat = (path[i][1] + path[i+1][1]) / 2
        icon_data.append({"position": [mid_lon, mid_lat], "icon": segment_transports[i]["icon"]})

    text_layer = pdk.Layer(
        "TextLayer",
        data=icon_data,
        get_position="position",
        get_text="icon",
        get_size=28,
        get_color=[0,0,0]
    )

    city_points = [
        {"position": city_info[c]["coords"], "city": c}
        for c in cities
    ]

    city_layer = pdk.Layer(
        "ScatterplotLayer",
        data=city_points,
        get_position="position",
        get_radius=50000,
        get_fill_color=[0,128,255],
        pickable=True
    )

    st.pydeck_chart(pdk.Deck(
        layers=[path_layer, text_layer, city_layer],
        initial_view_state=pdk.ViewState(
            longitude=path[0][0],
            latitude=path[0][1],
            zoom=4
        ),
        tooltip={
            "html": "<b>{city}</b>",
            "style": {"backgroundColor": "white"}
        }
    ))

    # --- Costs ---
    total_hotel = 0
    total_food = 0
    for city in cities:
        chosen_hotel = city_hotel_choices[city]
        hotel_data = next(h for h in city_info[city]["hotels"] if h[0]==chosen_hotel)
        total_hotel += hotel_data[1] * days
        total_food += city_info[city]["food_price"] * days

    total_transport = sum(t["price_per_km"]*DISTANCE for t in segment_transports)
    total_cost = total_hotel + total_food + total_transport

    # --- Output ---
    st.subheader("📅 Детайли за пътуването")
    st.write(f"📍 Маршрут: {' ➡ '.join(cities)}")
    st.write(f"📆 Дати: {checkin} → {checkout} ({days} дни)")
    st.write(f"🚍 Транспортна обща цена: {total_transport:.2f} лв")
    st.write(f"🍽️ Храна общо: {total_food:.2f} лв")
    st.write(f"🏨 Хотели общо: {total_hotel:.2f} лв")
    st.write(f"💰 Общо: {total_cost:.2f} лв")

    st.markdown("---")
    for city in cities:
        h = next(h for h in city_info[city]["hotels"] if h[0]==city_hotel_choices[city])
        st.markdown(f"### 📍 {city}")
        st.write(f"🏨 **{h[0]}** — ~{h[1]} лв/нощ — [Резервирай]({h[2]})")
        st.write(f"🍽️ Храна: ~{city_info[city]['food_price']} лв/ден")
        st.write(f"🏛️ Забележителност: {city_info[city]['sight']}")

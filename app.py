import streamlit as st
import pydeck as pdk

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
        "food": "Българска кухня",
        "sight": "Катедралата Александър Невски"
    },
    "Белград": {
        "coords": [20.4489, 44.7866],
        "hotels": [
            ("Hotel Moskva", 130, "https://www.booking.com/hotel/rs/moskva.html"),
            ("Square Nine Hotel", 220, "https://www.booking.com/hotel/rs/square-nine.html")
        ],
        "food": "Сръбска скара",
        "sight": "Калемегдан"
    },
    "Виена": {
        "coords": [16.3738, 48.2082],
        "hotels": [
            ("The Guesthouse Vienna", 350, "https://www.booking.com/hotel/at/the-guesthouse-vienna.html"),
            ("Hotel Sacher Wien", 500, "https://www.booking.com/hotel/at/sacher-wien.html")
        ],
        "food": "Виенски шницел",
        "sight": "Дворецът Шьонбрун"
    },
    "Мюнхен": {
        "coords": [11.5820, 48.1351],
        "hotels": [
            ("Hotel Bayerischer Hof", 420, "https://www.booking.com/hotel/de/bayerischer-hof.html"),
            ("Marc München", 150, "https://www.booking.com/hotel/de/marc-munchen.html")
        ],
        "food": "Немска кухня",
        "sight": "Мариенплац"
    },
    "Рим": {
        "coords": [12.4964, 41.9028],
        "hotels": [
            ("Hotel Milano Castello", 330, "https://www.booking.com/hotel/it/milano-castello.html"),
            ("Navona Palace Luxury Inn", 280, "https://www.booking.com/hotel/it/navona-palace-luxury-inn.html")
        ],
        "food": "Паста",
        "sight": "Колизеум"
    },
    "Флоренция": {
        "coords": [11.2558, 43.7696],
        "hotels": [
            ("Hotel Davanzati", 240, "https://www.booking.com/hotel/it/davanzati.html"),
            ("FH Grand Hotel Mediterraneo", 210, "https://www.booking.com/hotel/it/grand-hotelfh-mediterraneo.html")
        ],
        "food": "Тосканска кухня",
        "sight": "Катедралата Санта Мария дел Фиоре"
    },
    "Барселона": {
        "coords": [2.1734, 41.3851],
        "hotels": [
            ("Hotel 1898", 280, "https://www.booking.com/hotel/es/colon-1898.html"),
            ("H10 Cubik", 260, "https://www.booking.com/hotel/es/h10-cubik.html")
        ],
        "food": "Испански тапас",
        "sight": "Саграда Фамилия"
    }
}

transports = {
    "Кола": {"price": 0.25, "icon": "🚗"},
    "Влак": {"price": 0.18, "icon": "🚆"},
    "Самолет": {"price": 0.45, "icon": "✈️"}
}

# ================== SIDEBAR ==================

st.sidebar.title("🧭 Планиране")

route_choice = st.sidebar.selectbox("Маршрут:", list(routes.keys()))
days = st.sidebar.slider("Брой дни:", 1, 14, 7)

city_hotel_choices = {}
for city in routes[route_choice]:
    city_hotel_choices[city] = st.sidebar.selectbox(
        f"Хотел в {city}:",
        [hotel[0] for hotel in city_info[city]["hotels"]],
        key=f"hotel_{city}"
    )

segment_transports = []
for i in range(len(routes[route_choice]) - 1):
    t = st.sidebar.selectbox(
        f"{routes[route_choice][i]} → {routes[route_choice][i+1]}:",
        list(transports.keys()),
        key=f"trans_{i}"
    )
    segment_transports.append(transports[t])

# ================== MAIN ==================

st.title("🌍 Реален туристически планер")

if st.button("Планирай 🧭"):

    cities = routes[route_choice]
    path = [city_info[c]["coords"] for c in cities]

    # === MAP ===
    path_layer = pdk.Layer(
        "PathLayer",
        data=[{"path": path}],
        get_color=[255, 0, 0],
        width_min_pixels=4
    )

    icons = []
    for i in range(len(path) - 1):
        mid_lon = (path[i][0] + path[i+1][0]) / 2
        mid_lat = (path[i][1] + path[i+1][1]) / 2
        icons.append({"position": [mid_lon, mid_lat], "icon": segment_transports[i]["icon"]})

    text_layer = pdk.Layer(
        "TextLayer",
        data=icons,
        get_text="icon",
        get_position="position",
        get_size=28,
        get_color=[0, 0, 0]
    )

    city_points = [
        {"position": city_info[c]["coords"], "city": c}
        for c in cities
    ]

    city_layer = pdk.Layer(
        "ScatterplotLayer",
        data=city_points,
        get_position="position",
        get_fill_color=[0, 128, 255],
        get_radius=50000,
        pickable=True
    )

    view = pdk.ViewState(longitude=path[0][0], latitude=path[0][1], zoom=4)

    st.pydeck_chart(pdk.Deck(
        layers=[path_layer, text_layer, city_layer],
        initial_view_state=view,
        tooltip={"html": "<b>{city}</b>", "style": {"backgroundColor": "white"}}
    ))

    # === DETAILS ===

    st.subheader("🏨 ДЕТАЙЛИ ЗА ХОТЕЛИ И ЦЕНИ")
    total_hotel_cost = 0

    for city in cities:
        hotels = city_info[city]["hotels"]
        chosen_name = city_hotel_choices[city]
        chosen = next(h for h in hotels if h[0] == chosen_name)
        price = chosen[1]
        link = chosen[2]
        total_hotel_cost += price * days

        st.markdown(f"**{city}**")
        st.write(f"- 🏨 Хотел: [{chosen_name}]({link}) — ~{price} лв / нощ")  # реални Booking примери
        st.write(f"- 🍽️ Кухня: {city_info[city]['food']}")
        st.write(f"- 🏛️ Забележителност: {city_info[city]['sight']}")

    st.success(f"Общо за хотели: {total_hotel_cost:.2f} лв")

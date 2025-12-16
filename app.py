import streamlit as st
from abc import ABC, abstractmethod



# ================== DATA ==================



routes = {
  "България → Германия": ["София", "Белград", "Виена", "Мюнхен"]
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
  }
}



DISTANCE_BETWEEN_CITIES = 300 # км (опростено)



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

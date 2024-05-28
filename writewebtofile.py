import requests
import random as rng
import time
from bs4 import BeautifulSoup
from universalimports import TM, STOP, Dice, CombatPage
COMBATPAGES = {}
def grabCardsFromPage(page):
    webpage = requests.get(link + str(page)).text
    file = open(f"cardpages\\page{page}.html", "w+", encoding="utf-8")
    file.write(webpage)
    file.close()
link = "https://tiphereth.zasz.su/cards/?dc=1&dc=2&dc=3&dc=4&dc=5&av=Collectable&av=Obtainable&page=" # Add the page number at the end
page = 1 
while page <= 16: # After 16, all the cards are either E.G.O pages or ones used in the Keter Realization (which arn't useful.)
    grabCardsFromPage(page)
    page += 1
    time.sleep(0.5)

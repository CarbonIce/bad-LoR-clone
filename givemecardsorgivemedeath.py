import requests
import random as rng
import time
from bs4 import BeautifulSoup
from universalimports import TM, STOP, Dice, CombatPage
COMBATPAGES = {}
def grabCardsFromPage(page):
    webpage = requests.get(link + str(page)).text

    soup = BeautifulSoup(webpage, 'html.parser')

    cards = soup.find_all("lor-card")
    for p in cards:
        pageTitle = p.find("lor-card-name").find('a').find('span').string
        pageDiceTable = p.find("table")
        pageRarity = p['data-rarity']
        pageDescription = p.find("lor-card-desc").find("span", recursive=False)
        if pageDescription:
            onEvent = pageDescription.find("b")
            if onEvent: 
                if len(pageDescription.find_all("b")) > 1:# EDGE CASE... THERE MAY BE MULTIPLE OF THESE <B> TAGS AGGGGGGGGGGGGGG
                    '''
                    My solution: Just give up. Pass every string in tags in the page description to the CombatPage object and let it figure it out.
                    All of this parsing shit is AIDS, One can only write so many edge case catchers before they crack
                    Like look at this shit
                    Trash Disposal
                    <b>On Use</b> All Offensive dice of this page gain '<b>On Hit</b> Recover 2 HP'<hr>
                    WHY?!
                    final = ""
                    bolded = pageDescription.find_all("b")
                    for b in bolded: # EDGE CASE: FOR CARDS SUCH AS "TAKE THE SHOT", WHICH ARE SINGLE USE, THERE *IS* NO SIBLING
                        onEvent = b.string
                        if b.next_sibling.string:
                            action = b.next_sibling.string.strip()
                            final += onEvent + ":" + action + "; "
                        else:
                            final += onEvent + "; "    
                    onEvent = final
                    action = None 
                
                    '''
                    onEvent = pageDescription.text.strip()
                    action = None
                else:
                    action = onEvent.next_sibling.string
                    if action: # EDGE CASE: THERE MIGHT NOT BE A SIBLING
                        action = action.strip()
                    else:
                        action = None
                    onEvent = onEvent.string
            else:
                action = pageDescription.string # This is assuming that it's just a straight string. Hopefully no edge cases get out?
        else:
            onEvent = None
            action = None
        dices = pageDiceTable.findAll('tr')
        initializingPage = CombatPage(pageTitle, pageRarity, onEvent, action, [])
        for die in dices:
            dieRange = die.find(class_='range').string
            dieDesc = die.find(class_='desc').find('span')
            dieType = die['data-detail']
            dieCounter = die['data-type'] # Counter die are referred to as "Standby" dice on the site
            if dieCounter == "Standby":
                dieCounter = True
            else:
                dieCounter = False
            if dieDesc:
                beequestion = dieDesc.find('b')
                if beequestion:
                    dieDesc = beequestion.string + ": " + beequestion.next_sibling.string.strip()
                else:
                    dieDesc = dieDesc.string
            dieRange = [int(x) for x in dieRange.split(" - ")]
            initializingPage.addDie(Dice(dieType, dieRange[0], dieRange[1], dieCounter, dieDesc))
        COMBATPAGES[initializingPage.name] = initializingPage
# Look for all lor-card elements
# Light cost of card is in the element lor-card-icon
# Card name is under the link element of lor-card-name
# Dice are under lor-card-back -> lor-card-description
# Each individual die is in a table under lor-card-description, with range under tr of class range
link = "https://tiphereth.zasz.su/cards/?dc=1&dc=2&dc=3&dc=4&dc=5&av=Collectable&av=Obtainable&page=" # Add the page number at the end
page = 1 
rangecount = {}
while page <= 16: # After 16, all the cards are either E.G.O pages or ones used in the Keter Realization (which arn't useful.)
    grabCardsFromPage(page)
    page += 1
    time.sleep(0.5)

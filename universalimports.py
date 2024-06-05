from random import randint, choice
from math import ceil
from time import sleep
import os
import sys
from regex import sub, compile, findall
EmotionCoinRequirements = [3, 3, 5, 7, 9]   # From level index to index + 1

class TextModifiers:  # A class containing ANSI text modifiers to make text different colors or have different effects.
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"


# Aliases for TextModifiers because typing out TextModifiers every time is slow and TM.END is hard to type out
TM = TextModifiers
STOP = TM.END
def stripAnsi(inp): # https://stackoverflow.com/questions/37192606/python-regex-how-to-delete-all-matches-from-a-string https://www.tutorialspoint.com/How-can-I-remove-the-ANSI-escape-sequences-from-a-string-in-python#:~:text=You%20can%20use%20regexes%20to,%5B)%5B0%2D%3F%5D
    new = sub(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]", '', inp)
    return new
'''
diceIcons = {
    "Slash":"𐑠",
    "Pierce":"🜚",
    "Blunt":"⚙",
    "Guard":"⛉",
    "Evade":"☇"
}
'''
diceIcons = {
    "Slash":"S",
    "Pierce":"P",
    "Blunt":"B",
    "Guard":"G",
    "Evade":"E"
}

class Dice:
    '''
    Hello Matt!
    '''
    def __init__(self, diceType: str, lowerBound: int, upperBound: int, counter=False, description=None, onEvent=None, action=None):
        '''
        A single Die on a Combat Page.

        Arguments:

        [0] diceType: string, the type of die.
        Valid values are Slash, Pierce, Blunt, Guard, or Evade

        [1] lowerBound: integer, the lower bound on the die

        [2] upperBound: integer, the upper bound on the die

        [3] counter=False: boolean, specifies if the die is a counter die

        [4] description=None: string, specifies special actions to take when rolling, hitting, or winning a Clash with the die

        [5] onEvent=None: string, specifies the event to run action, actually used

        [6] action=None: callable, this function is run when event is called
        '''
        # Defining properties, boring
        self.type = diceType
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.counter = counter
        self.description = description  # UI friendly version of onEvent and action
        self.onEvent = onEvent  # I think all dice are on Hit, on Roll, and on Clash Win / Lose, (Hit should be handeled by the key page...) god i hope there arn't any dice with >1 effects
        self.action = action
        self.icon = diceIcons[self.type]

        if self.counter:  # All counter die are Yellow, regardless of type.
            self.primaryColor = TM.YELLOW  # Primary color is the color the dice type is highlighted in: the [S] part
            self.secondaryColor = TM.YELLOW  # Secondary color is the color used by the range: the 2 - 6 part
        elif self.type in ["Guard", "Evade"]:
            self.primaryColor = TM.LIGHT_CYAN
            self.secondaryColor = TM.CYAN
        else:
            self.primaryColor = TM.LIGHT_RED
            self.secondaryColor = TM.RED
        if self.description and ":" in self.description:  # A ":" in the description usually is a part of On Hit: do thing or On Clash Win: do thing
            parts = self.description.split(':')
            self.description = f"{TM.YELLOW}{parts[0]}:{STOP}{parts[1]}"
        self.currentValue = None    # Set when rolling die.
        self.naturalValue = None    # Set when rolling die.
    def onRoll(self, character, enemy, enemydie=None):
        if self.onEvent == "onRoll":
            return self.action(self, character, enemy, enemydie)

    def onClashEvent(self, character, enemy, enemydie, success=True):
        if self.onEvent == "onClashEvent":
            return self.action(self, character, enemy, enemydie, success)
    def onHit(self, character, enemy):
        if self.onEvent == "onHit":
            return self.action(self, character, enemy)
    @property
    def dieType(self):
        if self.type in ['Slash', 'Pierce', 'Blunt']:
            return "Offensive"
        else:
            return self.type    # Guard or Evade
    @property
    def miniStrRepr(self):
        '''
        A shortened string representation of the dice.
        Looks like this:
        [CB 2-6]
        '''
        return f"{self.primaryColor}[{self.icon} {self.secondaryColor}{self.lowerBound}-{self.upperBound}]{STOP}"

    def __str__(self):
        '''
        Standard string representation of the dice. Would look something like this:
        [Counter Block] 2 - 6 On Clash Win: Inflict 2 Burn
        '''
        typeModified = self.type
        if self.counter:
            typeModified = "Counter " + self.type
        if self.description:
            return f"{self.primaryColor}[{typeModified}] {self.secondaryColor}{self.lowerBound} - {self.upperBound}{STOP} | {self.description}"
        else:
            return f"{self.primaryColor}[{typeModified}] {self.secondaryColor}{self.lowerBound} - {self.upperBound}{STOP}"

    def roll(self):
        '''
        Simply rolls the die and returns the natural value.
        '''
        return randint(self.lowerBound, self.upperBound)
class SpeedDie:
    def __init__(self, mini, maxi):
        self.min = mini
        self.max = maxi
        self.value = self.roll()
        self.pageToUse = None
    def roll(self):
        return randint(self.min, self.max)


class CombatPage:
    def __init__(self, name: str, light: int, rarity: str, description: str, onEvent: str, action: callable, dice: list):
        '''
        A Combat Page.

        Arguments:

        [0] name: string, the name of the combat page.

        [1] light: int, the light cost of the page.

        [2] rarity: string, the rarity of the page, only affects the color of the name when the Combat Page is displayed.
        Valid values are Common, Uncommon, Rare, Unique. (These corrospond to Paperback, Hardcover, Limited, and Object of Art respectively).

        [3] onEvent: string, Special description of the Combat Page, detailing extra information such as action to take when the Page is played,
        action to take when the page is discarded, Mass Attack type, Single Use, etc. If automatic parsing fails, the entire description is dumped here.

        [4] action: callable, Action to take when onEvent condition is met. Only set if there is a single clear format of (Event) (Action)
        such as On Play: Regain 1 Light.

        [5] dice: list, Dice to initialize this page with. This is a queue, not a stack.
        '''
        self.name = name
        self.rarity = rarity  # Dictates the color of the page name. Nothing else.
        self.lightCost = light
        self.description = description
        self.onEvent = onEvent  # This is going to be a hellhole. Events are fine, but there are so many custom actions I need to account for.
        # Prob just going to focus on the ones most critical to gameplay, namely Light Restore and Page Draw
        self.action = action  # If onEvent is defined, but action is not, treat onEvent as the entire description.
        # This project already makes me want to die and it hasn't even been 3 hours yet.
        self.dice = dice
        match self.rarity:  # https://www.freecodecamp.org/news/python-switch-statement-switch-case-example/
            case "Unique":  # Object of Art
                self.color = TM.YELLOW
            case "Rare":  # Limited
                self.color = TM.BLUE
            case "Uncommon":  # Hardcover
                self.color = TM.CYAN
            case "Common":  # Paperback
                self.color = TM.GREEN
    def onPlay(self, user):
        if self.onEvent == "onPlay":
            self.action(self, user)

    def popTopDice(self):
        '''
        Removes and returns the first die in the queue. If there is none, return None
        '''
        if len(self.dice) > 0:
            using = self.dice[0]
            self.dice = self.dice[1:]
            return using
    def removeAllDice(self):
        self.dice = []
    def __len__(self) -> int:
        return len(self.dice)
    def addDie(self, die):
        '''
        Adds a die to the queue.
        '''
        self.dice.append(die)
    def buffDie(self, character, enemy, die):
        if self.onEvent == "buffDie":
            return self.action(self, character, enemy, die)
        
    def __str__(self):
        # OH GOD WHY
        '''
        if self.description is not None:
            return f"{self.description} | {self.color}{self.name}{STOP} | " + ' '.join([x.miniStrRepr for x in self.dice])
        else:
        '''
        return f"{self.color}{self.name}{STOP} | " + ' '.join([x.miniStrRepr for x in self.dice])
    def reverseStr(self):
        return f"{self.color}{self.name}{STOP} | " + ' '.join(reversed([x.miniStrRepr for x in self.dice]))
class Passive:  # This class handles everything about a passive ability that goes on a key page - namely, when to activate some arbitrary function that affects the Character using the Key Page.
    # Unfortunetly, due to the nature of many passive abilties, there will have to be a LOT of hard coding...
    # The most commmon events that I can find are OnAttribute (immedietly apply, do something simple like adding a speed die (Speed I through III)). Pass in 
    # rollDie (Wedge, Swordplay, Lions Fist, etc. that buff the value of dice)
    # OnHit (Deal extra damage, stagger, apply ailment, etc. depending on situation)
    # OnKill (Gain strength, gain health, etc.)
    # OnDeath (Maybe just make this event run whenever anything dies, given that there are passives on any death and on ally death)
    # OnSceneStart and OnSceneEnd (Usual stuff)
    def __init__(self, name, description, onAttribute=None, rollDie=None, onHit=None, onKill=None, onDeath=None, onSceneStart=None, onSceneEnd=None, onTakeDamage=None):
        self.name = name
        self.description = description
        self.onAttributeE = onAttribute
        self.rollDieE = rollDie
        self.onHitE = onHit
        self.onKillE = onKill
        self.onDeathE = onDeath
        self.onSceneStartE = onSceneStart
        self.onSceneEndE = onSceneEnd
        self.onTakeDamageE = onTakeDamage
    def onAttribute(self, kp):
        if self.onAttributeE: self.onAttributeE(kp)
    def rollDie(self, user, target, die):
        if self.rollDieE: mod = self.rollDieE(self, user, target, die); return mod
        return 0
    def onHit(self, enemy, die):    # onHit will double as onClashWin because i cant take it anymore
        mod = 0
        if self.onHitE: self.onHitE(self, enemy, die)
        return mod
    def onTakeDamage(self, damageType, amountPhysical, amountStagger):
        if self.onTakeDamageE:
            changes = [0, 0]
            resultingMods = self.onTakeDamageE(self, damageType, amountPhysical, amountStagger)
            changes[0] += resultingMods[0]
            changes[1] += resultingMods[1]
            return changes
        return [0, 0]
    def onKill(self):
        if self.onKillE: self.onKillE(self)
    def onDeath(self, ally=False): # Ally determines if it was an ally who died. Whaddaya know.
        if self.onDeathE: self.onDeathE(self, ally)
    def onSceneStart(self, first=False):
        if self.onSceneStartE: self.onSceneStartE(self, first)
    def onSceneEnd(self):
        if self.onSceneEndE: self.onSceneEndE(self)
class KeyPage:  # Key Pages are basically the character sheet; they dicate how much health, stagger resist, resistance to certain attacks, speed dice, etc. each character has.
    def __init__(self, name="Patron Librarian of Gen. Works", health=30, stagger=15, physicalResistances={'Slash':1,'Pierce':1.5,'Blunt':2}, staggerResistances={'Slash':1,'Pierce':1.5,'Blunt':2}, speedLower=1, speedUpper=4, passives=[], lightStart=3):     # Default stats based off of the Patron Librarian key page
        self.name = name
        self.health = health
        self.stagger = stagger
        self.physicalResistances = physicalResistances
        self.staggerResistances = staggerResistances
        self.speedLower = speedLower
        self.speedUpper = speedUpper
        self.passives = passives
        self.lightStart = lightStart    # Most likely 3 but can be 4 for high tier Star and Impurity Key Pages
        self.speedDieCount = 1 # 1 by default. Increased by the Speed I through III passives.
        self.user = None
    # I'm sorry to the CS gods, but this is how I worked it out.
    def onAttribute(self):
        for passive in self.passives:
            if passive.onAttribute: passive.onAttribute(self)
    def rollDie(self, target, die):
        modifier = 0
        for passive in self.passives:
            if passive.rollDie: modifier += passive.rollDie(self.user, target, die) # rollDie should return an integer, how much to change the dice value by.
        for status in self.user.statusEffects:
            if self.user.statusEffects[status].rollDie: modifier += self.user.statusEffects[status].rollDie(self.user, target, die)
        return modifier
    def onHit(self, enemy, die):    # onHit will double as onClashWin because i cant take it anymore
        mod = 0
        for passive in self.passives:
            if passive.onHit: mod = passive.onHit(enemy, die)
        return mod
    def onTakeDamage(self, damageType, amountPhysical, amountStagger):
        changes = [0, 0]
        for passive in self.passives:
            if passive.onTakeDamage:
                resultingMods = passive.onTakeDamage(damageType, amountPhysical, amountStagger)
                changes[0] += resultingMods[0]
                changes[1] += resultingMods[1]
        return changes
    def onKill(self):
        for passive in self.passives:
            if passive.onKill: passive.onKill()
    def onDeath(self, ally=False): # Ally determines if it was an ally who died. Whaddaya know.
        for passive in self.passives:
            if passive.onDeath: passive.onDeath(ally)
    def onSceneStart(self, first=False):
        for passive in self.passives:
            if passive.onSceneStart: passive.onSceneStart(first)
    def onSceneEnd(self):
        for passive in self.passives:
            if passive.onSceneEnd: passive.onSceneEnd()


class StatusEffect(Passive): #  I had to look up a tutorial for this because i forgor. This over having to rewrite all of those events. https://realpython.com/inheritance-composition-python/
    def __init__(self, name, description, stacks, rollDie=None, onSceneStart=None, onSceneEnd=None, onTakeDamage=None):
        # All status effects only use (I PRAY THAT THEY ONLY NEED) rollDie (Fairy, Bleed, Paralysis (Paral fucks with die bounds directly) and Erosion) onSceneEnd (Burn, Erosion, Fairy) onSceneStart (Haste and Bind), and onTakeDamage (Smoke, Commanders Mark)
        self.stacks = stacks # Stacks is how many times this status effect has been applied
        super().__init__(name, description, rollDie=rollDie, onSceneEnd=onSceneEnd, onSceneStart=onSceneStart, onTakeDamage=onTakeDamage)


class Character:    # The big one.
    def __init__(self, name, keyPage=KeyPage(), deck=[]):
        # The deck consists of 9 Combat Page elements. Most of the characters attributes are set by the Key Page.
        self.name = name
        self.keyPage = keyPage
        self.activeCombatPage = None    # Assume that activeCombatPage is the combat page currently being used.
        self.swapKeyPage(keyPage)
        self.deck = deck # Pages that need to be drawn. This is a Queue.
        self.damageandReasons = [[], []] # First list is physical damage and reason, second list is stagger and reason
        self.counterDice = []
    def beginAct(self):
        # Reinitialize health and stagger, purge status effects, run onSceneStart functions
        self.statusEffects = {}
        self.health = self.keyPage.maxHealth
        self.stagger = self.keyPage.maxStagger # Almost everything can be grabbed from the key page, as they don't change* (*They probably do, but i am sure as hell not dealing with that.)
        self.light = self.keyPage.lightStart
        self.lightCapacity = self.keyPage.lightStart
        self.Hand = []  # Pages readily accessable to use
        # Draw 4
        self.drawPages(4)
        self.keyPage.onSceneStart()
    def playCombatPage(self, page, target):
        self.activeCombatPage = page
        print(page)
        for die in page.dice:
            if die.counter:
                self.counterDice.append(die)
                page.dice.remove(die)
        self.target = target
    def swapKeyPage(self, newKeyPage):
        self.keyPage = newKeyPage
        self.speedDiceCount = newKeyPage.speedDieCount
        self.speedDice = []
        for _ in range(self.speedDiceCount):
            self.speedDice.append(SpeedDie(self.keyPage.speedLower, self.keyPage.speedUpper))
        self.emotionCoins = 0
        self.emotionLevel = 0 # Fucking kill me now I forgot about emotion and emotion coins
        self.light = self.keyPage.lightStart
        self.lightCapacity = self.keyPage.lightStart
        newKeyPage.user = self  # This seems like a disaster waiting to happen. Oh well...
        self.health = self.keyPage.health
        self.stagger = self.keyPage.stagger # Almost everything can be grabbed from the key page, as they don't change* (*They probably do, but i am sure as hell not dealing with that.)
        self.statusEffects = {}
        self.keyPage.onAttribute()
    
    def drawPages(self, amount):
        for _ in range(amount):
            if len(self.deck) > 0:
                self.Hand.append(self.deck[0]) # Draw a card
                deck = deck[1:] # Pop that card from the deck
    
    def gainEmotionCoins(self, count):    # Ignoring distinction between Positive and Negative coins because fuck no i'm not doing abno pages
        self.emotionCoins = min(self.emotionCoins + count, EmotionCoinRequirements[self.emotionLevel])

    def checkForIncrementEmotionLevel(self):
        if self.emotionLevel < 5 and self.emotionCoins == EmotionCoinRequirements[self.emotionLevel]:
            self.emotionCoins = 0
            self.emotionLevel += 1
        self.lightCapacity += 1 # Increase max light by 1
        self.light = self.lightCapacity # Regain all light
        if self.emotionLevel == 4: # Gain an additional Speed die at Emotion Level 4
            self.speedDiceCount += 1
            self.speedDice.append(SpeedDie(self.keyPage.speedLower, self.keyPage.speedUpper))
        # Not including an event for passives that activate on emotion level change because fuck you
        # At emotion 5, playing 2+ combat pages in a scene causes an extra draw at the start of the next scene
    def cleanStatusEffects(self):
        for status in self.statusEffects:
            if statusEffects[status].stacks == 0:
                statusEffects.pop(status)
    def takeDamage(self, damageType, amountPhysical, amountStagger, truePhysical=0, trueStagger=0, physicalReason=None, staggerReason=None):   # Yes, all of these distinctions are neccesary. Yes I hate this.
        if damageType in ["Slash", "Pierce", "Blunt"]:
            mods = self.keyPage.onTakeDamage(damageType, amountPhysical, amountStagger)
            amountPhysical += mods[0]   # I think this is proper order of operations on the stagger and physical damage???
            amountStagger += mods[1]
            physicalDamage = int(self.keyPage.physicalResistances[damageType] * amountPhysical) # Rounded down.
            staggerDamage = int(self.keyPage.staggerResistances[damageType] * amountStagger)
            self.health -= max(physicalDamage, 0)
            self.stagger -= max(staggerDamage, 0)
            if not physicalReason:
                physicalReason = resistanceToText[self.keyPage.physicalResistances[damageType]]
            if not staggerReason:
                staggerReason = resistanceToText[self.keyPage.staggerResistances[damageType]]
            self.damageandReasons[0].append([physicalDamage, physicalReason])
            self.damageandReasons[1].append([staggerDamage, staggerReason])
        elif not (amountPhysical == 0 and amountStagger == 0):
            raise AssertionError(f"What? {amountPhysical} {amountStagger}")
        else:
            self.health -= truePhysical
            self.stagger -= trueStagger # Let's just... not... get into the abno cards that reduce max stagger. Actually, lets just not with abno cards altogether.
            if not physicalReason:
                self.damageandReasons[0].append([truePhysical, ""])
            else:
                self.damageandReasons[0].append([truePhysical, physicalReason])
            if not staggerReason:
                self.damageandReasons[1].append([trueStagger, ""])
            else:
                self.damageandReasons[1].append([trueStagger, staggerReason])
        # Insert death and stagger logic here i actually wanna die

    def regainLight(self, amount):
        self.light = min(self.light + amount, self.lightCapacity)
    def regainStats(self, health, stagger):
        if stagger > 0:
            self.stagger = min(self.stagger + stagger, self.keyPage.stagger)
        self.health = min(self.health + health, self.keyPage.health)
    def outputData(self):
        print(f"{self.name} - {self.keyPage.name}'s Key Page")
        print(f"{TM.LIGHT_RED}{self.health}/{self.keyPage.health} HP{STOP}")
        print(f"{TM.YELLOW}{self.stagger}/{self.keyPage.stagger} STGR{STOP}")
        print(f"{TM.LIGHT_PURPLE}{self.emotionCoins}/{EmotionCoinRequirements[self.emotionLevel]} EMOTION COINS (EMOTION LEVEL {self.emotionLevel}){STOP}")
        print(f"{TM.YELLOW}{self.light}/{self.lightCapacity} Light{STOP}")
        for status in self.statusEffects:
            print(f"{self.statusEffects[status].stacks} {status}")
    def miniOutputData(self):
        statusString = ""
        for status in self.statusEffects:
            statusString += f" {statusEffectColors[status]}{status}({self.statusEffects[status].stacks}){STOP}"
        physicalDamageReason = ""
        staggerDamageReason = ""
        if len(self.damageandReasons[0]) > 0:
            physicalDamageReason = " ".join([f"({x[1]} {x[0]})" for x in self.damageandReasons[0] if x[0] != 0])
        if len(self.damageandReasons[1]) > 0:
            staggerDamageReason = " ".join([f"({x[1]} {x[0]})" for x in self.damageandReasons[1] if x[0] != 0])
        toReturn = [f"{self.name} | {TM.LIGHT_RED}{self.health}{physicalDamageReason} {TM.YELLOW}{self.stagger}{staggerDamageReason}{STOP} | {TM.LIGHT_PURPLE}({self.emotionLevel}) {self.emotionCoins * 'O'}{(EmotionCoinRequirements[self.emotionLevel] - self.emotionCoins) * '-'}{STOP}", f"{TM.YELLOW}{u'◆ ' * self.light}{u' ◇' * (self.lightCapacity-self.light)}{STOP} |" + statusString]
        self.damageandReasons = [[], []]
        return toReturn
# Constants
def reverseOutput(text):
    textSplat = text.split(" | ")
    textSplat.reverse()
    return " | ".join(textSplat)
def bleedOut(effect, me, target, die):
    if die.dieType == "Offensive":
        me.takeDamage("Bleed", 0, 0, effect.stacks, 0, "Bleed")
        effect.stacks = ceil(effect.stacks * (2 / 3))
    return 0

def strCheck(die):
    if die.dieType == "Offensive":
        return 1
    return 0

def removeStacks(effect, amount):
    effect.stacks -= amount

def Bind(target, amount):
    for SpeedDie in target.speedDice:
        SpeedDie.value = max(1, SpeedDie.value - amount)
statusEffects = {
    "Bleed":StatusEffect("Bleed", 
                         "Take damage equal to the number of Bleed stacks on character when rolling an Offensive die, then reduce the number of stacks by 1/3.", 
                         1, rollDie=lambda me,usr,target,die:bleedOut(me,usr,target,die),
                         onSceneEnd=lambda me:removeStacks(me, me.stacks)),
    "Strength":StatusEffect("Strength",
                             "All Offensive dice gain power equal to the number of stacks",
                             1, rollDie=lambda me,usr,target,die: me.stacks * strCheck(die),
                             onSceneEnd=lambda me:removeStacks(me, me.stacks)),
    "Fragile":StatusEffect("Fragile", "Take extra true damage equal to the number of stacks from attacks",
                           1, onTakeDamage=lambda me,usr,type,physical,stagger : (me.stacks, 0), onSceneEnd=lambda me:removeStacks(me, me.stacks)),
    "Bind":StatusEffect("Bind", "Lowers speed value of all speed die by number of stacks", 1, 
                        onSceneStart=lambda me : Bind(me.target, me.stacks), onSceneEnd=lambda me:removeStacks(me, me.stacks))
}
statusEffectColors = {
    "Bleed": f"{TM.RED}",
    "Strength": f"{TM.RED}",
    "Fragile": f"{TM.RED}",
    "Bind": f"{TM.GREEN}",
    "Haste": f"{TM.GREEN}",
    "Feeble": f"{TM.RED}"
}
resistanceToText = {
    0.25: "Ineff.",
    0.5: "Endure",
    1: "Normal",
    1.5: "Weak",
    2: "Fatal"
}
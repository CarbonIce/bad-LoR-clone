from random import randint
class TextModifiers:
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
# Aliases for TM

TM = TextModifiers
STOP = TM.END

class Dice:
    def __init__(self, diceType, lowerBound, upperBound, counter=False, description=None):
        '''

        Dice types
        Offensive: Slash Pierce Blunt, the damage types
        Defencive: Block and Evade
        Counter: Any Offensive or Defensive die can be a Counter die, which is played when facing a one sided attack against 
        a character that played a page containing a counter die, or has a passive that gives a counter die
        oh god this entire project is just me nerding out isnt it
        Additionally, every die could have a variaty of effects, such as On Hit: Inflict 1 Bleed. I'll try to make singular functions
        for the most common patterns but it's going to be basically impossible.

        '''
        self.type = diceType
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.counter = counter
        self.description = description
        self.initial = ""
        if self.counter: # All counter die are Yellow, regardless of type.
            self.initial = "C"
            self.primaryColor = TM.YELLOW
            self.secondaryColor = TM.YELLOW
        elif self.type in ["Guard", "Evade"]: # Guard is the term used by the website so thats what I'm going with
            self.primaryColor = TM.LIGHT_CYAN
            self.secondaryColor = TM.CYAN
        else:
            self.primaryColor = TM.LIGHT_RED
            self.secondaryColor = TM.RED
        if self.description and ":" in self.description: # Usually means its something like On Hit: do thing
            parts = self.description.split(':')
            self.description = f"{TM.YELLOW}{parts[0]}:{STOP}{parts[1]}"        
        self.initial += self.type[0]
    @property
    def miniStrRepr(self):
        if self.description:
            return f"{self.primaryColor}[{self.initial} {self.lowerBound}-{self.upperBound}]{STOP} | {self.description[:min(15, len(self.description))]}..."
        else:
            return f"{self.primaryColor}[{self.initial} {self.lowerBound}-{self.upperBound}]{STOP}"
    def __str__(self):
        typeModified = self.type
        if self.counter:
            typeModified = "Counter " + self.type
        if self.description:
            return f"{self.primaryColor}[{typeModified}] {self.secondaryColor}{self.lowerBound} - {self.upperBound}{STOP} | {self.description}"
        else:
            return f"{self.primaryColor}[{typeModified}] {self.secondaryColor}{self.lowerBound} - {self.upperBound}{STOP}"
    def roll(self):
        return randint(self.lowerBound, self.upperBound)
class CombatPage:
    def __init__(self, name, rarity, onEvent, action, dice):
        self.name = name
        self.rarity = rarity # Dictates the color of the page name. Nothing else.
        self.onEvent = onEvent # This is going to be a hellhole. Events are fine, but there are so many custom actions I need to account for.
        # Prob just going to focus on the ones most critical to gameplay, namely Light Restore and Page Draw
        self.action = action
        self.dice = dice
        match self.rarity:
            case "Unique": # Object of Art
                self.color = TM.YELLOW
            case "Rare": # Limited
                self.color = TM.BLUE
            case "Uncommon": # Hardcover
                self.color = TM.CYAN
            case "Common": # Paperback
                self.color = TM.GREEN
    def popTopDice(self):
        using = self.dice[0]
        self.dice = self.dice[1:]
        return using
    def addDie(self, die):
        self.dice.append(die)
    def __str__(self):
        # OH GOD WHY
        if self.action: 
            return f"{self.color}{self.name} | {TM.YELLOW}{self.onEvent}: {STOP}{self.action}\n" + '\n'.join([str(x) for x in self.dice])
        else:
            return f"{self.color}{self.name}{STOP}\n" + '\n'.join([str(x) for x in self.dice])
# Constants


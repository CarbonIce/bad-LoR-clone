from random import randint


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


class Dice:
    '''
    Hello Matt!
    '''
    def __init__(self, diceType: str, lowerBound: int, upperBound: int, counter=False, description=None):
        '''
        A single Die on a Combat Page.

        Arguments:

        [0] diceType: string, the type of die.
        Valid values are Slash, Pierce, Blunt, Guard, or Evade

        [1] lowerBound: integer, the lower bound on the die

        [2] upperBound: integer, the upper bound on the die

        [3] counter=False: boolean, specifies if the die is a counter die

        [4] description=None: string, specifies special actions to take when rolling, hitting, or winning a Clash with the die
        '''
        # Defining properties, boring
        self.type = diceType
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.counter = counter
        self.description = description
        self.initial = ""

        if self.counter:  # All counter die are Yellow, regardless of type.
            self.initial = "C"  # Starts the intial with C, so a Counter Block dice shows as CB when viewed in mini mode
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
        self.initial += self.type[0]

    @property
    def miniStrRepr(self):
        '''
        A shortened string representation of the dice.
        Looks like this:
        [CB 2-6] On Clash Win: I...
        '''
        if self.description:
            return f"{self.primaryColor}[{self.initial} {self.lowerBound}-{self.upperBound}]{STOP} | {self.description[:min(15, len(self.description))]}..."
        else:
            return f"{self.primaryColor}[{self.initial} {self.lowerBound}-{self.upperBound}]{STOP}"

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


Dice()


class CombatPage:
    def __init__(self, name: str, rarity: str, onEvent: str, action: str, dice: list):
        '''
        A Combat Page.

        Arguments:

        [0] name: string, the name of the combat page.

        [1] rarity: string, the rarity of the page, only affects the color of the name when the Combat Page is displayed.
        Valid values are Common, Uncommon, Rare, Unique. (These corrospond to Paperback, Hardcover, Limited, and Object of Art respectively).

        [2] onEvent: string, Special description of the Combat Page, detailing extra information such as action to take when the Page is played,
        action to take when the page is discarded, Mass Attack type, Single Use, etc. If automatic parsing fails, the entire description is dumped here.

        [3] action: Action to take when onEvent condition is met. Only set if there is a single clear format of (Event) (Action)
        such as On Play: Regain 1 Light.

        [4] dice: Dice to initialize this page with. This is a queue, not a stack.
        '''
        self.name = name
        self.rarity = rarity  # Dictates the color of the page name. Nothing else.
        self.onEvent = onEvent  # This is going to be a hellhole. Events are fine, but there are so many custom actions I need to account for.
        # Prob just going to focus on the ones most critical to gameplay, namely Light Restore and Page Draw
        self.action = action  # If onEvent is defined, but action is not, treat onEvent as the entire description.
        # This project already makes me want to die and it hasn't even been 3 hours yet.
        self.dice = dice
        match self.rarity:
            case "Unique":  # Object of Art
                self.color = TM.YELLOW
            case "Rare":  # Limited
                self.color = TM.BLUE
            case "Uncommon":  # Hardcover
                self.color = TM.CYAN
            case "Common":  # Paperback
                self.color = TM.GREEN

    def popTopDice(self):
        '''
        Removes and returns the first die in the queue.
        '''
        using = self.dice[0]
        self.dice = self.dice[1:]
        return using

    def addDie(self, die):
        '''
        Adds a die to the queue.
        '''
        self.dice.append(die)

    def __str__(self):
        # OH GOD WHY
        if self.onEvent is not None and self.action is not None:
            return f"{self.color}{self.name} | {TM.YELLOW}{self.onEvent}: {STOP}{self.action}\n" + '\n'.join([str(x) for x in self.dice])
        elif self.onEvent:
            return f"{self.color}{self.name} | {self.onEvent}\n" + '\n'.join([str(x) for x in self.dice])
        else:
            return f"{self.color}{self.name}{STOP}\n" + '\n'.join([str(x) for x in self.dice])


# Constants
CombatPage()

from universalimports import *
class Screen:   # If you want something to work, do it yourself. Actually, don't do that.
    def __init__(self):
        size = os.get_terminal_size()
    def clearScreen():
        os.system("clear")
    def printRightAligned(toPrint):
        size = os.get_terminal_size() # https://www.w3schools.com/python/ref_os_get_terminal_size.asp#:~:text=Python%20os.,-get_terminal_size()%20Method&text=The%20os.,the%20terminal%20window%20in%20characters.
        columns = size.columns
        toPrintLen = len(toPrint)
        print(" " * (columns - toPrintLen) + toPrint)
    def printRightandLeft(toPrintLeft, toPrintRight):
        size = os.get_terminal_size() # https://www.w3schools.com/python/ref_os_get_terminal_size.asp#:~:text=Python%20os.,-get_terminal_size()%20Method&text=The%20os.,the%20terminal%20window%20in%20characters.

        columns = size.columns
        toPrintLen = len(toPrintRight) + len(toPrintLeft)
        
        print(toPrintLen)
        print(len(toPrintLeft), len(toPrintRight))
        print(toPrintLeft, end="")
        print(f"{columns - toPrintLen}" + " " * (columns - toPrintLen) + toPrintRight)
class ReceptionHandler:     # I lied. This is the big one.
    def __init__(self, players, enemies):
        # Players and Enemies are lists of Character objects.
        self.players = players
        self.enemies = enemies
        self.act = 1
        self.scene = 1
    def Clash(self, character1, character2, dice1, dice2):    # NO DISTINCTION BETWEEN RANGED AND MELEE AND MASS ATTACK PAGES BECAUSE FUCK NO
        # CLASH BETWEEN DICE:
        # Step 1: Roll both die.
        d1 = dice1.roll()
        d2 = dice2.roll()
        dice1.naturalValue = d1
        dice2.naturalValue = d2
        dice1.currentValue = 0
        dice2.currentValue = 0  # This is so that enemy dice effects that lower dice value can be run at onRoll without overwriting it
        if d1 == dice1.upperBound or d1 == dice1.lowerBound:
            character1.gainEmotionCoins(1)
        if d2 == dice2.upperBound or d2 == dice2.lowerBound:
            character2.gainEmotionCoins(1)
        character1.gainEmotionCoins(1)  # 1 gained from clashing
        character2.gainEmotionCoins(1)  # 1 gained from clashing
        # Step 2: Run             rollDice from the Key Page + StatusEffects      buffDice events from the Combat Page,                        and onRoll events from the Dice itself
        dice1Modifier = int(character1.keyPage.rollDie(character2, dice1) or 0) + int(character1.activeCombatPage.buffDie(character1, character2, dice1) or 0) + int(dice1.onRoll(character1, character2, dice2) or 0)
        dice2Modifier = int(character2.keyPage.rollDie(character1, dice2) or 0) + int(character2.activeCombatPage.buffDie(character2, character1, dice2) or 0) + int(dice1.onRoll(character2, character1, dice1) or 0)
        dice1.currentValue += d1 + dice1Modifier
        dice2.currentValue += d2 + dice2Modifier
        # Int conversions are to turn the None values to 0
        # Step 3: Compare the dice
        d1 = dice1.currentValue
        d2 = dice2.currentValue
        draw = False
        if d1 > d2:
            winner = character1
            winDice = dice1
            winVal = d1
            loser = character2
            loseDice = dice2
            loseVal = d2
        elif d2 > d1:
            winner = character2
            winDice = dice2
            winVal = d2
            loser = character1
            loseDice = dice1
            loseVal = d1
        else:
            # On a draw, both dice are consumed.
            draw = True
        d1c2 = TM.DARK_GRAY
        d2c2 = TM.DARK_GRAY
        if dice1Modifier > 0:
            d1c2 = dice1.primaryColor
        elif dice1Modifier == 0:
            d1c2 = dice1.secondaryColor
        if dice2Modifier > 0:
            d2c2 = dice2.primaryColor
        elif dice2Modifier == 0:
            d2c2 = dice2.secondaryColor
        Screen.print_at((0, 0), f"{character1.name} | {dice1.secondaryColor}[{dice1.icon}]{dice1.naturalValue}{STOP} >< {dice2.secondaryColor}[{dice2.icon}]{dice2.naturalValue}{STOP} | {character2.name}", end="\r") # https://stackoverflow.com/questions/18692617/how-does-r-carriage-return-work-in-python https://stackoverflow.com/questions/5419389/how-to-overwrite-the-previous-print-to-stdout
        sleep(1)
        Screen.print_at((40, 0), f"{character1.name} | {d1c2}[{dice1.icon}] {dice1.currentValue}{STOP} >< {d2c2}[{dice2.icon}]{dice2.currentValue}{STOP} | {character2.name}", end='\033[K\n')
        sleep(0.2)
        if not draw:
            winDice.onClashEvent(winner, loser, loseDice, True)
            loseDice.onClashEvent(loser, winner, winDice, True)
            match winDice.dieType:
                case "Offensive":
                    mods = winDice.onHit(winner, loser)
                    if mods is None or mods == 0:
                        mods = [0, 0]
                    mods2 = winner.keyPage.onHit(loser, winDice)
                    if mods2 is None or mods2 == 0:
                        mods2 = [0, 0]
                    match loseDice.dieType:
                        case "Offensive": # Offensive > Offensive: Full damage is dealt by die 1, and die 2 is destroyed.
                            loser.takeDamage(winDice.type, winVal + mods[0] + mods2[0], winVal + mods[1] + mods2[1])
                            winner.keyPage.onHit(loser, winDice)
                        case "Guard": # Offensive > Guard: Die 1 deals damage reduced by die 2's value
                            loser.takeDamage(winDice.type, winVal - loseVal + mods[0] + mods2[0], winVal - loseVal+ mods[1] + mods2[1])
                            winner.keyPage.onHit(loser, winDice)
                        case "Evade": # Offensive > Evade: Full damage is dealt by die 1, and die 2 is destroyed.
                            loser.takeDamage(winDice.type, winVal + mods[0] + mods2[0], winVal + mods[1] + mods2[1])
                            winner.keyPage.onHit(loser, winDice)
                case "Guard":
                    match loseDice.dieType:
                        case "Offensive": # Guard > Offensive: Guard value - Offensive value true stagger damage is dealt to loser
                            loser.takeDamage(winDice.type, 0, 0, 0, winVal - loseVal)
                        case "Guard": # Guard > Guard: Die 1 value true stagger damage is dealt to character 2
                            loser.takeDamage(winDice.type, 0, 0, 0, winVal)
                        case "Evade": # Guard > Evade: Die 1 value true stagger damage is dealt to character 2
                            loser.takeDamage(winDice.type, 0, 0, 0, winVal)
                case "Evade":
                    match loseDice.dieType:
                        case "Offensive": # Evade > Offensive: Die2 is destroyed; character 1 regains stagger equal to Evade dice value, EVADE DIE IS RECYCLED
                            winner.regainStats(0, winVal)
                        case "Guard": # Evade > Guard: Die2 is destroyed; character 1 regains stagger equal to Evade die value. THE DIE IS NOT RECYCLED
                            winner.regainStats(0, winVal)
                        case "Evade": # Nothing happens. Both die are destroyed.
                            pass
            # Blow up both die, unles the winning die was an Evade die and the losing die was an Offensive die
            if winDice.dieType == "Evade" and loseDice.dieType == "Offensive":
                loser.activeCombatPage.popTopDice()
            else:
                winner.activeCombatPage.popTopDice()
                loser.activeCombatPage.popTopDice()
        else:
            character1.activeCombatPage.popTopDice()
            character2.activeCombatPage.popTopDice()
        sleep(1)
    def drawScene(self):
        playerYindex = 10
        enemyYindex = 10
        for player in range(len(self.players)):
            dataP = self.players[player].miniOutputData()
            if player < len(self.enemies):
                dataE = self.enemies[player].miniOutputData()
                Screen.printRightandLeft(dataP[0], dataE[0])
                Screen.printRightandLeft(dataP[1], dataE[1])
                print()
            else:
                print(dataP[0])
                print(dataP[1])
        if len(self.enemies) > len(self.players):
            for enemy in range(len(self.enemies) - len(self.players)): # enemies [0, 1, 2, 3], ally [0, 1, 2], len 4 - 3 = 1, first number will be enemy #3, then #4... 
                data = [enemy + len(self.players) + 1].miniOutputData()
                Screen.printRightAligned(data[0])
                Screen.printRightAligned(data[1])
                enemyYindex += 3
    def main(self):
        pass
        # Initialize Scene
        # for player in self.players:
        #     player.

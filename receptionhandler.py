from universalimports import *
class Screen:   # If you want something to work, do it yourself. Actually, don't do that.
    def __init__(self):
        size = os.get_terminal_size()
    def clearScreen():
        if os.name == 'nt':
            os.system("cls")
        else:
            os.system("clear")
    def printRightAligned(toPrint, end='\n'):
        size = os.get_terminal_size() # https://www.w3schools.com/python/ref_os_get_terminal_size.asp#:~:text=Python%20os.,-get_terminal_size()%20Method&text=The%20os.,the%20terminal%20window%20in%20characters.
        columns = size.columns
        if "<-" not in toPrint: # Awful workaround, but I'm dying over here
            toPrint = reverseOutput(toPrint)
        toPrintLen = len(stripAnsi(toPrint))
        print(" " * (columns - toPrintLen) + toPrint, end=end)
    def printRightandLeft(toPrintLeft, toPrintRight, end='\n'):
        size = os.get_terminal_size() # https://www.w3schools.com/python/ref_os_get_terminal_size.asp#:~:text=Python%20os.,-get_terminal_size()%20Method&text=The%20os.,the%20terminal%20window%20in%20characters.
        columns = size.columns
        toPrintLen = len(stripAnsi(toPrintRight)) + len(stripAnsi(toPrintLeft))
        toPrintRight = reverseOutput(toPrintRight)
        print(toPrintLeft, end='')
        print(" " * (columns - toPrintLen) + toPrintRight, end=end)
    def printMiddle(toPrintMiddle, end='\n'):
        size = os.get_terminal_size() # https://www.w3schools.com/python/ref_os_get_terminal_size.asp#:~:text=Python%20os.,-get_terminal_size()%20Method&text=The%20os.,the%20terminal%20window%20in%20characters.
        columns = size.columns
        toPrintLen = columns - len(stripAnsi(toPrintMiddle))
        print(" " * (toPrintLen // 2) + toPrintMiddle + " " * (toPrintLen // 2), end=end)
    def printDivider():
        size = os.get_terminal_size() # https://www.w3schools.com/python/ref_os_get_terminal_size.asp#:~:text=Python%20os.,-get_terminal_size()%20Method&text=The%20os.,the%20terminal%20window%20in%20characters.
        columns = size.columns
        print("-" * columns)
class ReceptionHandler:     # I lied. This is the big one.
    def __init__(self, players, enemies):
        # Players and Enemies are lists of Character objects.
        self.players = players
        self.enemies = enemies
        self.act = 0
        self.scene = 0

    def calculateTargeting(self):
        CharacterDiceSortedBySpeed = []
        EnemyDiceSortedBySpeed = []
        for character in range(len(self.characters)):
                index = 0
                for speedDie in self.characters[character].speedDice:
                    CharacterDiceSortedBySpeed.append([speedDie, character, index]) # These lists are the SpeedDie Object, the index of the User of the speed die, and the index of the speed die of the user.
                    index += 1
        for enemy in range(len(self.enemies)):
            index = 0
            for speedDie in self.enemies[enemy].speedDice:
                EnemyDiceSortedBySpeed.append([speedDie, enemy, index])
                index += 1
        CharacterDiceSortedBySpeed.sort(key=lambda x: x[0].value)
        EnemyDiceSortedBySpeed.sort(key=lambda x: x[0].value)
        testedCharacterDice = []    # lIST OF SPEEDDICE OBJECTS
        testedEnemyDice = []
        Clashes = []
        OneSidedAttacks = []
        clashingDice = []
        oneSidedDice = []
        '''
        1. Check for dice that target each other. These dice clash, no matter what.
        2. Check for dice that target a dice that has a lower speed and an assigned page. These dice clash, and if multiple dice are targetting the same lower speed die, the higher speed targetting dice will clash.
        3. Check for one sided attacks
        '''
        for die in CharacterDiceSortedBySpeed:
            if die[0] not in testedCharacterDice:
                if die[0].target is not None and die[0].target.target == die[0] and die[0].target not in testedEnemyDice:   # Both dice are clashing against each other. This is a clash, and thats that (and this is this).
                    testedCharacterDice.append(die[0])
                    testedEnemyDice.append(die[0].target)
                    Clashes.append([die[0], die[0].target])
                    clashingDice.append(die[0])
                    clashingDice.append(die[0].target)
                elif die[0].target is not None and die[0].target.value < die[0].value and die[0].target not in testedEnemyDice:  # Enemy die is slower, redirection of Clash
                    testedCharacterDice.append(die[0])
                    testedEnemyDice.append(die[0].target)
                    Clashes.append([die[0], die[0].target])
                    clashingDice.append(die[0])
                    clashingDice.append(die[0].target)
                elif die[0].target is not None:
                    testedCharacterDice.append(die[0])  # The biggest advantage the player has over the enemy is that the enemy cannot redirect.
                    OneSidedAttacks.append([die[0], True]) # The second bool is a indication of if the one sided attack is from a Character or an Enemy
                    oneSidedDice.append(die[0])
        for die in EnemyDiceSortedBySpeed:
            if die[0] not in testedEnemyDice and die[0].target is not None:
                OneSidedAttacks.append([die[0], False]) # The second bool is a indication of if the one sided attack is from a Character or an Enemy
                oneSidedDice.append(die[0])
        return Clashes, OneSidedAttacks, clashingDice, oneSidedDice
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
        combatString = f"{character1.name} | {dice1.miniStrRepr} {dice1.secondaryColor}{dice1.naturalValue}{STOP} >< {dice2.secondaryColor}{dice2.naturalValue} {dice2.miniStrRepr}{STOP} | {character2.name}"
        if dice1.description:
            combatString = TM.YELLOW + dice1.description + STOP + " | " + combatString
        if dice2.description:
            combatString = combatString + " | " + TM.YELLOW + dice2.description + STOP
        Screen.printMiddle(combatString, end="\r") # https://stackoverflow.com/questions/18692617/how-does-r-carriage-return-work-in-python https://stackoverflow.com/questions/5419389/how-to-overwrite-the-previous-print-to-stdout
        sleep(0.5)
        cS2 = f"{character1.name} | {dice1.miniStrRepr} {d1c2}{dice1.currentValue}{STOP} >< {d2c2}{dice2.currentValue} {dice2.miniStrRepr}{STOP} | {character2.name}"
        if dice1.description:
            cS2 = TM.YELLOW + dice1.description + STOP + " | " + cS2
        if dice2.description:
            cS2 = cS2 + " | " + TM.YELLOW + dice2.description + STOP
        Screen.printMiddle(cS2, end= '\033[K\n')
        if not draw:
            Screen.printMiddle(winner.name[0].upper() + winner.name[1:] + " wins the clash")
        else:
            Screen.printMiddle("Draw")
        sleep(2)
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
                    mods3 = winner.activeCombatPage.onHit(winner, loser)
                    match loseDice.dieType:
                        case "Offensive": # Offensive > Offensive: Full damage is dealt by die 1, and die 2 is destroyed.
                            loser.takeDamage(winDice.type, winVal + mods[0] + mods2[0] + mods3[0], winVal + mods[1] + mods2[1] + mods3[1])
                            winner.keyPage.onHit(loser, winDice)
                        case "Guard": # Offensive > Guard: Die 1 deals damage reduced by die 2's value
                            loser.takeDamage(winDice.type, winVal - loseVal + mods[0] + mods2[0] + mods3[0], winVal - loseVal+ mods[1] + mods2[1] + mods3[1])
                            winner.keyPage.onHit(loser, winDice)
                        case "Evade": # Offensive > Evade: Full damage is dealt by die 1, and die 2 is destroyed.
                            loser.takeDamage(winDice.type, winVal + mods[0] + mods2[0] + mods3[0], winVal + mods[1] + mods2[1] + mods3[1])
                            winner.keyPage.onHit(loser, winDice)
                case "Guard":
                    match loseDice.dieType:
                        case "Offensive": # Guard > Offensive: Guard value - Offensive value true stagger damage is dealt to loser
                            loser.takeDamage(winDice.type, 0, 0, 0, winVal - loseVal, staggerReason="Blocked")
                        case "Guard": # Guard > Guard: Die 1 value true stagger damage is dealt to character 2
                            loser.takeDamage(winDice.type, 0, 0, 0, winVal, staggerReason="Blocked")
                        case "Evade": # Guard > Evade: Die 1 value true stagger damage is dealt to character 2
                            loser.takeDamage(winDice.type, 0, 0, 0, winVal, staggerReason="Blocked")
                case "Evade":
                    match loseDice.dieType:
                        case "Offensive": # Evade > Offensive: Die2 is destroyed; character 1 regains stagger equal to Evade dice value, EVADE DIE IS RECYCLED
                            winner.regainStats(0, winVal)
                            winner.damageandReasons[1].append([f"+{winVal}", "Evade"])
                        case "Guard": # Evade > Guard: Die2 is destroyed; character 1 regains stagger equal to Evade die value. THE DIE IS NOT RECYCLED
                            winner.regainStats(0, winVal)
                            winner.damageandReasons[1].append([f"+{winVal}", "Evade"])
                        case "Evade": # Nothing happens. Both die are destroyed.
                            pass
            # Blow up both die, unles the winning die was an Evade die and the losing die was an Offensive die (or if the winning die was a Counter die)
            if (winDice.dieType == "Evade" and loseDice.dieType == "Offensive") or winDice.counter:
                loser.activeCombatPage.popTopDice()
            else:
                winner.activeCombatPage.popTopDice()
                loser.activeCombatPage.popTopDice()
        else:
            character1.activeCombatPage.popTopDice()
            character2.activeCombatPage.popTopDice()
        self.drawSceneExtendedData()
        # Screen.printMiddle(cS2, end= '\n')
        sleep(2)
        self.drawSceneExtendedData()
    def drawScene(self):
        Screen.clearScreen()
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
                data = self.enemies[enemy + len(self.players) + 1].miniOutputData()
                Screen.printRightAligned(data[0])
                Screen.printRightAligned(data[1])
    def drawSceneExtendedData(self, selectedCharIndex=-1, enemyTrueelseFalse=False, hoverDie=-1):
        Clashes, oneSided, _, _ = self.calculateTargeting()
        Screen.clearScreen()
        pindex = 0
        for player in range(len(self.players)):
            if not enemyTrueelseFalse and selectedCharIndex == pindex:
                dataP = self.players[player].outputData(hoverDie)
            else:
                dataP = self.players[player].outputData(-1)
            if player < len(self.enemies):
                if enemyTrueelseFalse and selectedCharIndex == pindex:
                    dataE = self.enemies[player].outputData(hoverDie)
                else:
                    dataE = self.enemies[player].outputData(-1)
                Screen.printRightandLeft(dataP[0], dataE[0])
                Screen.printRightandLeft(dataP[1], dataE[1])
                print()
            else:
                print(dataP[0])
                print(dataP[1])
            pindex += 1
        if len(self.enemies) > len(self.players):
            for enemy in range(len(self.enemies) - len(self.players)): # enemies [0, 1, 2, 3], ally [0, 1, 2], len 4 - 3 = 1, first number will be enemy #3, then #4... 
                if enemyTrueelseFalse and selectedCharIndex == pindex:
                    data = self.enemies[enemy + len(self.players) + 1].outputData(hoverDie)
                else:
                    data = self.enemies[enemy + len(self.players) + 1].outputData(-1)
                Screen.printRightAligned(data[0])
                Screen.printRightAligned(data[1])
            pindex += 1
        Screen.printMiddle(f"{TM.YELLOW}TARGETING{STOP}")
        Screen.printDivider()
        for Clash in Clashes:
            Screen.printMiddle(f"{Clash[0].owner.name}'s die {TM.YELLOW}#{Clash[0].owner.speedDice.index(Clash[0])} (Speed {Clash[0]}){STOP} ({Clash[0].pageToUse}){TM.YELLOW} -> <- {STOP}{Clash[1].owner.name}'s die {TM.YELLOW}#{Clash[1].owner.speedDice.index(Clash[1])} (Speed {Clash[1]}){STOP} ({Clash[1].pageToUse})")
        for oneSidedAttack in oneSided:
            if oneSidedAttack[1]:
                print(f"{TM.LIGHT_CYAN if oneSidedAttack[1] else TM.LIGHT_RED}{oneSidedAttack[0].owner.name}'s die {TM.YELLOW}#{oneSidedAttack[0].owner.speedDice.index(oneSidedAttack[0])} (Speed {oneSidedAttack[0]}) {STOP}({oneSidedAttack[0].pageToUse}){TM.LIGHT_CYAN if oneSidedAttack[1] else TM.LIGHT_RED} -> {oneSidedAttack[0].target.owner.name}'s die {TM.YELLOW}#{oneSidedAttack[0].target.owner.speedDice.index(oneSidedAttack[0].target)}{STOP}")
            else:
                # print(f"{TM.LIGHT_RED}{oneSidedAttack[0].target.owner.name}'s die {TM.YELLOW}#{oneSidedAttack[0].target.owner.speedDice.index(oneSidedAttack[0].target)}{TM.LIGHT_RED} <- {STOP}({oneSidedAttack[0].pageToUse.reverseStr()}){TM.LIGHT_RED} {oneSidedAttack[0].owner.name}'s die {TM.YELLOW}#{oneSidedAttack[0].owner.speedDice.index(oneSidedAttack[0])}{STOP}")
                Screen.printRightAligned(f"{TM.LIGHT_RED}{oneSidedAttack[0].target.owner.name}'s die {TM.YELLOW}#{oneSidedAttack[0].target.owner.speedDice.index(oneSidedAttack[0].target)}{TM.LIGHT_RED} <- {STOP}({oneSidedAttack[0].pageToUse.reverseStr()}){TM.LIGHT_RED} (Speed {oneSidedAttack[0]}) {oneSidedAttack[0].owner.name}'s die {TM.YELLOW}#{oneSidedAttack[0].owner.speedDice.index(oneSidedAttack[0])}{STOP}")
        Screen.printDivider()
    def pageClash(self, p1, p2, page1, page2):
        while len(page1) > 0 or len(page2) > 0:
            if p1.stagger == 0: # If either character is staggaered, destroy all dice on their page.
                page1.dice = []
            if p2.stagger == 0:
                page2.dice = []
            Screen.printMiddle(f"{page1.reverseStr()} >< {reverseOutput(str(page2))}")
            sleep(1)
            if len(page1) == 0:
                dice = page2.popTopDice() 
                if dice.dieType != "Offensive":
                    continue
                else:
                    d1 = dice.roll()
                    dice.naturalValue = d1
                    dice.currentValue = 0
                    if d1 == dice.upperBound or d1 == dice.lowerBound:
                        p2.gainEmotionCoins(1)
                    # Step 2: Run             rollDice from the Key Page + StatusEffects      buffDice events from the Combat Page,                        and onRoll events from the Dice itself
                    diceModifier = int(p2.keyPage.rollDie(p1, dice) or 0) + int(p2.activeCombatPage.buffDie(p2, p1, dice) or 0) + int(dice.onRoll(p2, p1, dice) or 0)
                    dice.currentValue += d1 + diceModifier
                    # Int conversions are to turn the None values to 0
                    d1 = dice.currentValue
                    mods = dice.onHit(p2, p1)
                    if mods is None or mods == 0:
                        mods = [0, 0]
                    mods2 = p2.keyPage.onHit(p1, dice)
                    if mods2 is None or mods2 == 0:
                        mods2 = [0, 0]
                    mods3 = page1.onHit(p2, p1) # Returns [0, 0] if invalid output from the lambda function
                    # Print
                    c2 = TM.DARK_GRAY
                    if diceModifier > 0:
                        c2 = dice.primaryColor
                    elif diceModifier == 0:
                        c2 = dice.secondaryColor
                    combatString = f"{dice.miniStrRepr} {dice.secondaryColor}{dice.naturalValue}{STOP} | {p2.name}"
                    if dice.description:
                        combatString = combatString + " | " + TM.YELLOW + dice.description + STOP
                    # self.drawScene()
                    Screen.printMiddle(combatString, end="\r") # https://stackoverflow.com/questions/18692617/how-does-r-carriage-return-work-in-python https://stackoverflow.com/questions/5419389/how-to-overwrite-the-previous-print-to-stdout
                    sleep(1)
                    cS2 = f"{dice.miniStrRepr} {c2}{dice.currentValue}{STOP} | {p2.name}"
                    if dice.description:
                        cS2 = cS2 + " | " + TM.YELLOW + dice.description + STOP
                    Screen.printMiddle(cS2, end= '\033[K\n')
                    page2.onHit(p2, p1)
                    p1.takeDamage(dice.type, d1 + mods[0] + mods2[0] + mods3[0], d1 + mods[1] + mods2[1] + mods3[1])
                    sleep(2)
                #    Page 2 Unapposed
            elif len(page2) == 0:
                dice = page1.popTopDice()
                if dice.dieType != "Offensive":
                    continue
                else:
                    d1 = dice.roll()
                    dice.naturalValue = d1
                    dice.currentValue = 0
                    if d1 == dice.upperBound or d1 == dice.lowerBound:
                        p1.gainEmotionCoins(1)
                    # Step 2: Run             rollDice from the Key Page + StatusEffects      buffDice events from the Combat Page,                        and onRoll events from the Dice itself
                    diceModifier = int(p1.keyPage.rollDie(p2, dice) or 0) + int(p1.activeCombatPage.buffDie(p1, p2, dice) or 0) + int(dice.onRoll(p1, p2, dice) or 0)
                    dice.currentValue += d1 + diceModifier
                    # Int conversions are to turn the None values to 0
                    d1 = dice.currentValue
                    mods = dice.onHit(p1, p2)
                    if mods is None or mods == 0:
                        mods = [0, 0]
                    mods2 = p1.keyPage.onHit(p2, dice)
                    if mods2 is None or mods2 == 0:
                        mods2 = [0, 0]
                    mods3 = page1.onHit(p2, p1)
                    # Print
                    c2 = TM.DARK_GRAY
                    if diceModifier > 0:
                        c2 = dice.primaryColor
                    elif diceModifier == 0:
                        c2 = dice.secondaryColor
                    combatString = f"{p1.name} | {dice.miniStrRepr} {dice.secondaryColor}{dice.naturalValue}{STOP}"
                    if dice.description:
                        combatString = combatString + " | " + TM.YELLOW + dice.description + STOP
                    # self.drawScene()
                    Screen.printMiddle(combatString, end="\r") # https://stackoverflow.com/questions/18692617/how-does-r-carriage-return-work-in-python https://stackoverflow.com/questions/5419389/how-to-overwrite-the-previous-print-to-stdout
                    sleep(1)
                    cS2 = f"{p1.name} | {dice.miniStrRepr} {c2}{dice.currentValue}{STOP}"
                    if dice.description:
                        cS2 = cS2 + " | " + TM.YELLOW + dice.description + STOP
                    Screen.printMiddle(cS2, end= '\033[K\n')
                    p2.takeDamage(dice.type, d1 + mods[0] + mods2[0] + mods3[0], d1 + mods[1] + mods2[1] + mods3[0])
                    sleep(2)
                #    Page 1 Unapposed
            else:
                self.Clash(p1, p2, page1.dice[0], page2.dice[0])
            self.drawSceneExtendedData()
    def dieClash(self, die1, die2):
        p1 = die1.owner
        p2 = die2.owner
        p1.playCombatPage(die1.pageToUse, p2)
        if die2.target != None:
            p2.playCombatPage(die2.pageToUse, p1)
            self.pageClash(p1, p2, die1.pageToUse, die2.pageToUse)
            die2.pageTouse = None
            die2.target = None
        else:
            self.pageClash(p1, p2, die1.pageToUse, p2.counterDice)
        die1.pageTouse = None
        die1.target = None
    def Scene(self):
        self.scene += 1
        # Roll Speed
        for character in self.players:
            character.rollSpeedDice()
            # All characters draw a page, restore a light
            character.drawPages(1)
            character.regainLight(1)
            # Run OnSceneStart effects from KeyPage passives and Status Effects
            character.keyPage.onSceneStart(self.scene == 1)
        for character in self.enemies:
            character.rollSpeedDice()
            character.drawPages(1)
            character.regainLight(1)
            character.keyPage.onSceneStart(self.scene == 1)
        # Have enemies target random speed die of yours
        for enemy in self.enemies:
            # Just chooses a random page that can be used and puts it in the fastest speed die (and target a random speed die of an ally)
            speedDiceSelected = 0
            index = 0
            for page in enemy.Hand:
                if speedDiceSelected < enemy.speedDiceCount - 1:
                    if page.lightCost <= enemy.light:
                        target = choice(self.characters)
                        targetDie = randint(0, target.speedDiceCount - 1)
                        enemy.assignPageToSpeedDice(speedDiceSelected, index, target.speedDice[targetDie])
                else:
                    break
                index += 1
                speedDiceSelected += 1

        # Redraw Scene
        # Have user choose combat pages and target them
        event = None
        while True:
            selectedCharacter = 0
            selectedDie = 0
            option = 0
            COMBATTIME = False
            REMOVEPAGE = False
            char = self.characters[selectedCharacter]
            while True:
                self.drawSceneExtendedData()
                print(f"{TM.DARK_GRAY if option != 0 else TM.LIGHT_GRAY}Assign Combat Page {STOP}| {TM.DARK_GRAY if option != 1 else TM.LIGHT_GRAY}Remove Combat Page{STOP} | {TM.DARK_GRAY if option != 2 else TM.LIGHT_GRAY}Begin Scene{STOP}")
                print("(Use right and left arrows to select options, press space to confirm)")
                while not event or event.event_type != 'down' or event.name not in 'right left space'.split(" "):
                    event = keyboard.read_event()
                if event.name == 'space':
                    if option == 2:
                        COMBATTIME = True
                    elif option == 1:
                        REMOVEPAGE = True
                    break
                else:
                    if event.name == 'left':
                        option -= 1
                    else:
                        option += 1
                option = option % 3
                event = None
            event = None
            StopTime = True
            if COMBATTIME:
                break
            if REMOVEPAGE:
                stoptime = True
                while stoptime:
                    self.drawSceneExtendedData(selectedCharacter, False, selectedDie)
                    print("(Use arrow keys to navigate speed dice, press space to select the die, or escape to go back)")
                    print(f"Removing combat page from {TM.YELLOW}{self.characters[selectedCharacter].name}{STOP}'s dice number {TM.YELLOW}{selectedDie}{STOP} (Die numbers are the numbers outside of the paranthases within the square brackets)")
                    while not event or event.event_type != 'down' or event.name not in 'up down right left space esc'.split(" "):
                        event = keyboard.read_event()
                    if event.event_type == "down":
                        if event.name == 'up':
                            selectedCharacter -= 1
                        if event.name == 'down':
                            selectedCharacter += 1
                        if event.name == 'right':
                            selectedDie += 1
                        if event.name == 'left':
                            selectedDie -= 1
                        if event.name == 'space':
                            if char.speedDice[selectedDie].target is None:
                                print("There is no combat page assigned to that die.")
                                sleep(1)
                                continue
                            break
                        if event.name == 'esc':
                            stoptime = False
                            break
                    selectedCharacter = selectedCharacter % len(self.characters)
                    selectedDie = selectedDie % self.characters[selectedCharacter].speedDiceCount
                    event=None
                if stoptime:
                    char.removePageFromSpeedDice(selectedDie)
                event = None
                continue
            while StopTime: # https://stackoverflow.com/questions/24072790/how-to-detect-key-presses
                self.drawSceneExtendedData(selectedCharacter, False, selectedDie)
                print("(Use arrow keys to navigate speed dice, press space to select the die, or escape to go back)")
                print(f"Currently selecting {TM.YELLOW}{self.characters[selectedCharacter].name}{STOP}'s dice number {TM.YELLOW}{selectedDie} (Speed {self.characters[selectedCharacter].speedDice[selectedDie]}){STOP} (Die numbers are the numbers outside of the paranthases within the square brackets)")
                while not event or event.event_type != 'down' or event.name not in 'up down right left space esc'.split(" "):
                    event = keyboard.read_event()
                if event.event_type == "down":
                    if event.name == 'up':
                        selectedCharacter -= 1
                    if event.name == 'down':
                        selectedCharacter += 1
                    if event.name == 'right':
                        selectedDie += 1
                    if event.name == 'left':
                        selectedDie -= 1
                    if event.name == 'space':
                        break
                    if event.name == 'esc':
                        StopTime = False
                        break
                selectedCharacter = selectedCharacter % len(self.characters)
                selectedDie = selectedDie % self.characters[selectedCharacter].speedDiceCount
                event=None

            char = self.characters[selectedCharacter]
            selectedPage = 0
            event=None
            while StopTime: # Page select
                self.drawSceneExtendedData()
                print(f"{TM.YELLOW}{self.characters[selectedCharacter].name}{STOP}'s dice number {TM.YELLOW}{selectedDie} (Speed {self.characters[selectedCharacter].speedDice[selectedDie]}){STOP},")
                print("Selected:", char.Hand[selectedPage].longPrint())
                index = 0
                for page in char.Hand:
                    if index == selectedPage:
                        print(f"{page.color}{page.name}{STOP} {TM.YELLOW}{page.lightCost}{STOP}", end=" | ")
                    else:
                        print(f"{TM.DARK_GRAY}{page.name} {page.lightCost}{STOP}", end=" | ")
                    index += 1
                print("Use right and left arrow to navigate combat pages, space to select, escape to cancel")
                while not event or event.event_type != 'down' or event.name not in 'right left space esc'.split(" "):
                    event = keyboard.read_event()
                if event.name == 'right':
                    selectedPage += 1
                if event.name == 'left':
                    selectedPage -= 1
                if event.name == 'space':
                    add = 0
                    if char.speedDice[selectedDie].pageToUse != None:
                        add = char.speedDice[selectedDie].pageToUse.lightCost
                    if char.Hand[selectedPage].lightCost > char.light + add:
                        print("Not enough light...")
                        event = None
                        sleep(1)
                        continue
                    break
                if event.name == 'esc':
                    StopTime = False
                    break
                selectedPage = selectedPage % len(char.Hand)
                event = None
            event = None
            selectedEnemy = 0
            selectedEnemyDie = 0
            while StopTime: # https://stackoverflow.com/questions/24072790/how-to-detect-key-presses
                self.drawSceneExtendedData(selectedEnemy, True, selectedEnemyDie)
                print(f"{TM.YELLOW}{self.characters[selectedCharacter].name}{STOP}'s dice number {TM.YELLOW}{selectedDie} (Speed {self.characters[selectedCharacter].speedDice[selectedDie]}){STOP}, using {char.Hand[selectedPage]}")
                print("(Use arrow keys to navigate enemy speed dice, space to select, escape to go back)")
                print(f"Currently selecting {TM.YELLOW}{self.enemies[selectedEnemy].name}{STOP}'s dice number {TM.YELLOW}{selectedEnemyDie} (Speed {self.enemies[selectedEnemy].speedDice[selectedEnemyDie]}){STOP} (Die numbers are the numbers outside of the paranthases within the square brackets)")
                while not event or event.event_type != 'down' or event.name not in 'up down right left space'.split(" "):
                    event = keyboard.read_event()
                if event.event_type == "down":
                    if event.name == 'up':
                        selectedEnemy -= 1
                    if event.name == 'down':
                        selectedEnemy += 1
                    if event.name == 'right':
                        selectedEnemyDie += 1
                    if event.name == 'left':
                        selectedEnemyDie -= 1
                    if event.name == 'space':
                        break
                selectedEnemy = selectedEnemy % len(self.enemies)
                selectedEnemyDie = selectedEnemyDie % self.enemies[selectedEnemy].speedDiceCount
                event=None
            if StopTime:
                char.assignPageToSpeedDice(selectedDie, selectedPage, self.enemies[selectedEnemy].speedDice[selectedEnemyDie])
            event = None
        # Begin Combat
        ClashesFinal, OneSidedFinal, ClashingDice, OneSidedDice = self.calculateTargeting()
        AllDiceSortedBySpeed = []
        for character in range(len(self.characters)):
                index = 0
                for speedDie in self.characters[character].speedDice:
                    AllDiceSortedBySpeed.append(speedDie)
                    index += 1
        for enemy in range(len(self.enemies)):
            index = 0
            for speedDie in self.enemies[enemy].speedDice:
                AllDiceSortedBySpeed.append(speedDie)
                index += 1
        AllDiceSortedBySpeed.sort(key=lambda x: x.value)
        usedDice = []
        
        # Fastest speed die goes first, and prompt the targeted die to play it's combat page
        
        for die in AllDiceSortedBySpeed:
            if die not in usedDice:
                if die in ClashingDice:
                    clashFinal = None
                    for clash in ClashesFinal:
                        if die in clash:
                            clashFinal = clash
                            break
                    clashFinal[0].target = clashFinal[1]
                    clashFinal[1].target = clashFinal[0]
                    usedDice.append(clashFinal[0])
                    usedDice.append(clashFinal[1])
                    self.dieClash(clashFinal[0], clashFinal[1])
                elif die in OneSidedDice:
                    usedDice.append(die)
                    self.dieClash(die, die.target)
        # Continue until all speed die with pages attributed have clashed or one sided attacked (or failed to do anything due to stagger)


        # Run OnSceneEnd effects from KeyPage, Character, Status Effects, etc.
        for chara in self.characters:
            chara.keyPage.onSceneEnd()
            if not chara.startingStaggered and chara.stagger == 0:
                chara.startingStaggered = True
            elif chara.startingStaggered:
                chara.startingStaggered = False
                chara.stagger = chara.keyPage.maxStagger
            chara.checkForIncrementEmotionLevel()
        for chara in self.enemies:
            chara.keyPage.onSceneEnd()
            if not chara.startingStaggered and chara.stagger == 0:
                chara.startingStaggered = True
            elif chara.startingStaggered:
                chara.startingStaggered = False
                chara.stagger = chara.keyPage.maxStagger
            chara.checkForIncrementEmotionLevel()
    def Act(self, characters, enemies):
        self.act += 1
        self.characters = characters
        self.enemies = enemies
        for char in self.characters:
            char.beginAct()
        for enemy in self.enemies:
            enemy.beginAct()
        while True in [x.health > 0 for x in self.characters] and True in [x.health > 0 for x in self.enemies]:
            self.Scene()
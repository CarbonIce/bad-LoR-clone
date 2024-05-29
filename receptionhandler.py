from universalimports import *


class ReceptionHandler:     # I lied. This is the big one.
    def __init__(self, players, enemies):
        # Players and Enemies are lists of Character objects.
        self.player = players
        self.enemies = enemies
    def Clash(self, character1, character2, dice1, dice2):    # NO DISTINCTION BETWEEN RANGED AND MELEE AND MASS ATTACK PAGES BECAUSE FUCK NO
        # CLASH BETWEEN DICE:
        # Step 1: Roll both die.
        d1 = dice1.roll()
        d2 = dice2.roll()
        dice1.naturalValue = d1
        dice2.naturalValue = d2
        # Step 2: Run             rollDice from the Key Page + StatusEffects      buffDice events from the Combat Page,                        and onRoll events from the Dice itself
        dice1.currentValue = d1 + int(character1.keyPage.rollDie(character2, dice1) or 0) + int(character1.activeCombatPage.buffDie(character1, character2, dice1) or 0) + int(dice1.onRoll(character1, character2, dice2) or 0)
        dice2.currentValue = d2 + int(character2.keyPage.rollDie(character1, dice2) or 0) + int(character2.activeCombatPage.buffDie(character2, character1, dice2) or 0) + int(dice1.onRoll(character2, character1, dice1) or 0)
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
        print(d1, d2)
        if not draw:
            winDice.onClashEvent(winner, loser, loseDice, True)
            loseDice.onClashEvent(loser, winner, winDice, True)
            match winDice.dieType:
                case "Offensive":
                    mods = dice1.onHit(winner, loser)
                    if mods is None or mods == 0:
                        mods = [0, 0]
                    mods2 = winner.keyPage.onHit(loser, winDice)
                    if mods2 is None or mods2 == 0:
                        mods2 = [0, 0]
                    print(mods, mods2)
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
    def main(self):
        pass

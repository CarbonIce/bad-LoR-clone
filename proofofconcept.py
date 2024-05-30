from universalimports import *
from receptionhandler import *
from copy import deepcopy

def reduceEnemyDieValue(me, them, enemyDie, amount):
    enemyDie.currentValue = max(1, enemyDie.currentValue - amount)
    return 0
def inflictStatusEffects(target, effecttype, amount):
    if target.statusEffects.get(effecttype, False):
        target.statusEffects[effecttype].stacks += amount
    else:
        target.statusEffects[effecttype] = statusEffects[effecttype]
        target.statusEffects[effecttype].stacks = amount    # Some status effects should apply the scene after but nope because fuck you
# Combat Pages (TESTING)
AllasWorkshop = CombatPage(
    "Allas Workshop",
    2,
    "Uncommon",
    "Start of Clash: Reduce power of target's dice by 2",   # It should reduce ALL die on the enemy combat page but fuck you
    None,
    None,
    [
        Dice(
            "Pierce",
            5, 9,
            False, None,
            "onRoll",
            lambda me,them,die: reduceEnemyDieValue(me,them,die,2)
        ),
        Dice(
            "Pierce",
            5, 8,
            False, None,
            "onRoll",
            lambda me,them,die: reduceEnemyDieValue(me,them,die,2)
        )
    ]

)
ZelkovaWorkshop = CombatPage(
    "Zelkova Workshop",
    0,
    "Common",
    "On Use: Draw 1 page",
    "onPlay", lambda me,user: user.drawPage(1),
    [
        Dice(
            "Slash",
            4, 8
        ),
        Dice(
            "Blunt",
            3, 8
        )
    ]
)
OldBoysWorkshop = CombatPage(
    "Old Boys Workshop",
    1,
    "Common", "On Use: Restore 3 Light; draw 1 page",
    "onPlay", lambda me,user: (user.regainLight(3), user.drawPage(1)), #  used chatGPT to figure out how the hell to do this stuff using lambda functions,
    # This solution is extremely stupid (returns a tuple of the return values from regainLight and drawPage, but whatever)
    [
        Dice(
            "Guard",
            5,9
        ),
        Dice(
            "Blunt",
            4,8,
            False,
            "On Hit: Deal 3 damage to target"
            "onHit",
            lambda a,b: a.recoverStats(0, 5)
        )
    ]
)
MookWorkshop = CombatPage(
    "Mook Workshop",
    2,
    "Uncommon",
    "On Use: Restore 3 Light; draw 1 page",
    "onPlay", lambda me,user: (user.regainLight(3), user.drawPage(1)),
    [
        Dice(
            "Slash",
            8,13,
            False
        )
    ]
)
RangaWorkshop = CombatPage(
    "Ranga Workshop",
    0,
    "Common",
    None,None,None,
    [
        Dice("Pierce", 3, 7),
        Dice("Pierce", 3, 7),
        Dice("Slash", 
             3, 7,
             False, "On Hit: Inflict 5 Bleed this scene",
             "onHit", lambda me,them: inflictStatusEffects(them,"Bleed",5)
             )
    ]
)
WheelsIndustry = CombatPage(
    "Wheels Industry",
    4,
    "Rare",
    None,
    None,
    None,
    [
        Dice("Blunt",
            14,24,
            False,
            "On Hit: Destroy target's next die",
            'onHit',
            lambda me,enemy,enemydie : enemy.activeCombatPage.popTopDice()
            ),
        Dice(
            "Guard",
            5,8)
    ]
)
CrystalAtelier = CombatPage(
    "Crystal Altelier",
    3,
    "Uncommon",
    None,None,None,
    [
        Dice("Evade",8,11),
        Dice("Slash",7,11),
        Dice("Slash",7,11),
        Dice("Slash",4,8,True)
    ]
)
AtelierLogic = CombatPage(
    "Atelier Logic",
    2,
    "Uncommon",
    None,None,None,
    [
        Dice("Pierce",4,8),
        Dice("Pierce",5,8),
        Dice("Blunt",7,12)
    ]
)
Durandal = CombatPage(
    "Durandal",
    2,
    "Rare",
    None,None,None,
    [
        Dice(
            "Slash",
            5,9,
            False,
            "On Hit: Gain 1 Strength",
            "onHit",
            lambda me,char,enemy : inflictStatusEffects(char, "Strength", 1)
        ),
        Dice(
            "Slash",
            5,9,
            False,
            "On Hit: Gain 1 Strength",
            "onHit",
            lambda me,char,enemy : inflictStatusEffects(char, "Strength", 1)
        )
    ]
)
def obliterateDice(me,char,enemy,enemydice,result):
    if result:
        enemy.activeCombatPage.removeAllDice()
Furioso = CombatPage(
    "Furioso",
    5,  # This page is normally only usable after using all 9 other pages at least once
    # Trading that in for a +2 cost
    "Unique",
    "On Hit: Inflict 5 Bleed, 3 Bind, and 3 Fragile",
    "onHit",
    lambda me,char,enemy : (inflictStatusEffects(enemy, "Bleed", 5), inflictStatusEffects(enemy, "Bind", 3), inflictStatusEffects(enemy, "Fragile", 3)),
    Dice(
        "Slash",
        20,39,
        False,
        "On Clash Win: Destroy all of the enemies Dice",
        "onClashEvent",
        lambda me,char,enemy,enemydie,result : obliterateDice(me,char,enemy,enemydie,result)
    )
)
BlackSilenceDeck = [AllasWorkshop, CrystalAtelier, AtelierLogic, WheelsIndustry, RangaWorkshop, Furioso, Durandal, OldBoysWorkshop, MookWorkshop, ZelkovaWorkshop]
# Key Pages (TESTING)]
def gainDice(user, amount):
    user.speedDiceCount += amount
def blackSilenceDraw(kp, first):
    if first: kp.user.drawPages(2)
SpeedII = Passive("Speed II", "Gain 2 Speed dice", onAttribute=lambda KP: gainDice(KP.user, 2))
TheBlackSilencePassive = Passive("The Black Silence", "Draw 2 additional pages at the start of the Act. All dice gain +2 Power.", # This should be on every 3rd page but no because fuck you
                                 onSceneStart=lambda kp,first : blackSilenceDraw(kp,first),
                                 rollDie=lambda a,b,c: 2)
TheBlackSilence = KeyPage("The Black Silence",
                          106, 56, 
                          {'Slash':1, "Pierce":1, "Blunt":0.5}, 
                          {'Slash':1, "Pierce":1, "Blunt":0.5},
                          2, 7,
                          [SpeedII, TheBlackSilencePassive],
                          4) # 208 lines of work for a single key page. Fucking hell
char1 = Character("Roland", deepcopy(TheBlackSilence), deepcopy(BlackSilenceDeck))
char2 = Character("Loland", deepcopy(TheBlackSilence), deepcopy(BlackSilenceDeck))
reception = ReceptionHandler([char1], [char2])
char1.outputData()
char1.playCombatPage(deepcopy(RangaWorkshop), char2)
char2.playCombatPage(deepcopy(OldBoysWorkshop), char1)
reception.Clash(char1, char2, Dice("Slash", 
             3, 7,
             False, 
             "On Hit: Inflict 5 Bleed this scene",
             "onHit", lambda die,me,them: inflictStatusEffects(them,"Bleed",5)
             ), Dice(
            "Blunt",
            4,8,
            False,
            "On Hit: Deal 3 damage to target",
            "onHit",
            lambda a,b,c: c.takeDamage("Slash", 0, 0, 3, 0)
        ))
reception.Clash(char1, char2, Dice(
            "Guard",
            5,8), Dice(
            "Pierce",
            5, 8,
            False, None,
            "onRoll",
            lambda me,them,die: reduceEnemyDieValue(me,them,die,2)
        )
        )
char1.miniOutputData()
char2.miniOutputData()
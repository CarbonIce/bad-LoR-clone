from universalimports import *
from receptionhandler import *
from copy import deepcopy

def reduceEnemyDieValue(me, them, enemyDie, amount):
    enemyDie.currentValue = max(1, enemyDie.currentValue - amount)
    return 0
# Combat Pages (TESTING)
AllasWorkshop = CombatPage(
    "Allas Workshop",
    2,
    "Uncommon",
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
    "Common", False,
    "onPlay", lambda me,user: (user.regainLight(3), user.drawPage(1)) #  used chatGPT to figure out how the hell to do this stuff using lambda functions,
    # This solution is extremely stupid (returns a tuple of the return values from regainLight and drawPage, but whatever)
    [
        Dice(
            "Guard",
            5,9
        ),
        Dice(
            "Blunt",
            4,8
        )
    ]
)
# Key Pages (TESTING)
TheBlackSilence = KeyPage()
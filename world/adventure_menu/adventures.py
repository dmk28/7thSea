import random
from evennia import create_script
from evennia.utils import evmenu
from world.combat_script.roll_utils import roll_keep
from evennia.utils.search import search_object

PORTS = ["Kirk", "San Cristobal", "Dionna", "Bucca", "Midnight Archipelago"]

def adventure_start(caller):
    if caller.attributes.has("last_escort_adventure"):
        last_time = caller.db.last_escort_adventure
        current_time = caller.sessions.get()[0].conn_time
        if (current_time - last_time).days < 14:
            caller.msg("You must wait 2 weeks between escort adventures.")
            return

    text = "You've been hired as an armed escort by the local Guild. There are many missions to choose from.Choose your destination port:"
    options = []
    for port in PORTS:
        options.append({"key": port, "desc": f"Travel to {port}", "goto": "adventure_setup"})
    return text, options

def adventure_setup(caller, raw_string):
    destination = raw_string.strip()
    caller.ndb._adventure_destination = destination
    caller.ndb._adventure_phase = 0
    caller.ndb._adventure_success = 0
    caller.ndb._participants = [caller]
    
    text = f"You've chosen to escort a noble to {destination}. How many other participants (1-3)?"
    options = [
        {"key": str(i), "desc": f"{i} additional participant(s)", "goto": "add_participants"}
        for i in range(1, 4)
    ]
    return text, options

def add_participants(caller, raw_string):
    num_participants = int(raw_string.strip())
    text = f"Enter the names of {num_participants} participant(s), one at a time:"
    caller.ndb._participants_to_add = num_participants
    return text, "get_participant"

def get_participant(caller, raw_string):
    participant = search_object(raw_string.strip())[0]
    if participant:
        caller.ndb._participants.append(participant)
        caller.ndb._participants_to_add -= 1
        if caller.ndb._participants_to_add > 0:
            return f"Enter next participant ({caller.ndb._participants_to_add} remaining):", "get_participant"
        else:
            return "All participants added. Ready to begin?", "start_adventure"
    else:
        return "Participant not found. Try again:", "get_participant"

def start_adventure(caller, raw_string):
    caller.msg("The adventure begins!")
    return adventure_phase(caller)

def adventure_phase(caller):
    phase = caller.ndb._adventure_phase
    
    if phase >= 5:  # Adventure complete after 5 phases
        return adventure_end(caller)
    
    caller.ndb._adventure_phase += 1
    
    challenges = [
        ship_tossing_challenge,
        thug_assassination_challenge,
        smuggler_ship_challenge,
        port_arrival_challenge,
        final_phase
    ]
    
    return challenges[phase](caller)

def ship_tossing_challenge(caller):
    text = "The ship tosses and turns in rough seas. Roll Brawn + Footwork vs 30 or Brawn + Balance vs 20."
    options = [
        {"key": "Footwork", "desc": "Use Brawn + Footwork (TN 30)", "goto": "resolve_ship_tossing"},
        {"key": "Balance", "desc": "Use Brawn + Balance (TN 20)", "goto": "resolve_ship_tossing"}
    ]
    return text, options

def resolve_ship_tossing(caller, raw_string):
    choice = raw_string.strip().lower()
    brawn = caller.db.traits.get('brawn', 1)
    
    if choice == 'footwork':
        skill = caller.character_sheet.get_knack_value("Footwork")
        tn = 30
    else:  # Balance
        skill = caller.character_sheet.get_knack_value("Balance")
        tn = 20
    
    roll_result = roll_keep(brawn + skill, brawn)
    success = roll_result >= tn
    
    if success:
        text = f"Success! You rolled {roll_result} vs TN {tn}. You maintain your footing."
    else:
        text = f"Failure. You rolled {roll_result} vs TN {tn}. You take 2 flesh wounds."
        caller.character_sheet.flesh_wounds += 2
    
    return text, "adventure_phase"

def thug_assassination_challenge(caller):
    text = "A gang of thugs attempts to assassinate your escort. Protect them for 3 rounds!"
    caller.ndb._thug_rounds = 3
    caller.ndb._thug_successes = 0
    return text, "resolve_thug_round"

def resolve_thug_round(caller, raw_string):
    rounds = caller.ndb._thug_rounds
    successes = caller.ndb._thug_successes
    
    if rounds > 0:
        text = f"Round {4 - rounds}: Roll Finesse + Attack (Fencing) or Wits + Parry (Fencing) vs TN 15."
        options = [
            {"key": "Attack", "desc": "Use Finesse + Attack (Fencing)", "goto": "process_thug_round"},
            {"key": "Parry", "desc": "Use Wits + Parry (Fencing)", "goto": "process_thug_round"}
        ]
        return text, options
    else:
        if successes >= 45:  # 15 per round for 3 rounds
            text = "You successfully protected your escort from the thugs!"
        else:
            text = "You failed to fully protect your escort. They are injured but alive."
        return text, "adventure_phase"

def process_thug_round(caller, raw_string):
    choice = raw_string.strip().lower()
    
    if choice == 'attack':
        trait = caller.db.traits.get('finesse', 1)
        skill = caller.character_sheet.get_knack_value("Attack (Fencing)")
    else:  # Parry
        trait = caller.db.traits.get('wits', 1)
        skill = caller.character_sheet.get_knack_value("Parry (Fencing)")
    
    roll_result = roll_keep(trait + skill, trait)
    success = roll_result >= 15
    
    if success:
        caller.ndb._thug_successes += roll_result
        text = f"Success! You rolled {roll_result}. Total successes: {caller.ndb._thug_successes}"
    else:
        text = f"Failure. You rolled {roll_result}."
    
    caller.ndb._thug_rounds -= 1
    return text, "resolve_thug_round"

def smuggler_ship_challenge(caller):
    text = "The ship turns out to be a smuggler's ship and gets hailed by a hostile Navy. Choose your action:"
    options = [
        {"key": "Diplomacy", "desc": "Use Panache + Diplomacy vs TN 20", "goto": "resolve_smuggler_challenge"},
        {"key": "Strategy", "desc": "Use Wits + Strategy vs TN 25", "goto": "resolve_smuggler_challenge"},
        {"key": "Combat", "desc": "Fight them (Finesse + Weapon Attack vs TN 15, need 25 successes)", "goto": "resolve_smuggler_combat"},
        {"key": "Navigation", "desc": "Use Wits + Navigation to outpace them", "goto": "resolve_smuggler_challenge"}
    ]
    return text, options

def resolve_smuggler_challenge(caller, raw_string):
    choice = raw_string.strip().lower()
    
    if choice == 'diplomacy':
        trait = caller.db.traits.get('panache', 1)
        skill = caller.character_sheet.get_knack_value("Diplomacy")
        tn = 20
    elif choice == 'strategy':
        trait = caller.db.traits.get('wits', 1)
        skill = caller.character_sheet.get_knack_value("Strategy")
        tn = 25
    else:  # Navigation
        trait = caller.db.traits.get('wits', 1)
        skill = caller.character_sheet.get_knack_value("Navigation")
        tn = 20
    
    roll_result = roll_keep(trait + skill, trait)
    success = roll_result >= tn
    
    if success:
        if choice != 'navigation':
            caller.db.xp = caller.db.xp + 2 if hasattr(caller.db, 'xp') else 2
            text = f"Success! You rolled {roll_result} vs TN {tn}. You've resolved the situation and gained 2 XP."
            return text, "adventure_end"
        else:
            text = f"Success! You rolled {roll_result} vs TN {tn}. You've outpaced the hostile Navy."
            return text, "adventure_phase"
    else:
        text = f"Failure. You rolled {roll_result} vs TN {tn}. The situation escalates."
        return text, "smuggler_ship_challenge"

def resolve_smuggler_combat(caller):
    weapon = caller.db.wielded_weapon
    trait = caller.db.traits.get('finesse', 1)
    skill = caller.character_sheet.get_knack_value(weapon.db.attack_skill if weapon else "Attack (Fencing)")
    
    roll_result = roll_keep(trait + skill, trait)
    success = roll_result >= 15
    
    if success:
        caller.ndb._combat_successes = caller.ndb.get('_combat_successes', 0) + roll_result
        if caller.ndb._combat_successes >= 25:
            caller.db.xp = caller.db.xp + 2 if hasattr(caller.db, 'xp') else 2
            text = f"Victory! You've defeated the hostile Navy and gained 2 XP."
            return text, "adventure_end"
        else:
            text = f"You scored {roll_result} successes. Total: {caller.ndb._combat_successes}/25. Continue fighting?"
            options = [
                {"key": "Yes", "goto": "resolve_smuggler_combat"},
                {"key": "No", "goto": "smuggler_ship_challenge"}
            ]
            return text, options
    else:
        text = f"You failed to score any successes this round. Continue fighting?"
        options = [
            {"key": "Yes", "goto": "resolve_smuggler_combat"},
            {"key": "No", "goto": "smuggler_ship_challenge"}
        ]
        return text, options

def port_arrival_challenge(caller):
    text = "You've arrived at the port. While escorting your guest to their Guildhouse, a gang of goons attempts to bar your way. Choose your action:"
    options = [
        {"key": "Fight", "desc": "Engage in combat", "goto": "resolve_port_challenge"},
        {"key": "Bribe", "desc": "Attempt to bribe them (25 guilders)", "goto": "resolve_port_challenge"},
        {"key": "Intimidate", "desc": "Try to scare them off", "goto": "resolve_port_challenge"}
    ]
    return text, options

def resolve_port_challenge(caller, raw_string):
    choice = raw_string.strip().lower()
    
    if choice == 'fight':
        weapon = caller.db.wielded_weapon
        trait = caller.db.traits.get('finesse', 1)
        skill = caller.character_sheet.get_knack_value(weapon.db.attack_skill if weapon else "Attack (Fencing)")
        roll_result = roll_keep(trait + skill, trait)
        text = f"You engage in combat and roll {roll_result}."
    elif choice == 'bribe':
        if caller.db.guilders >= 25:
            caller.db.guilders -= 25
            text = "You successfully bribe the goons, spending 25 guilders."
        else:
            text = "You don't have enough guilders to bribe them. Choose another option."
            return text, "port_arrival_challenge"
    else:  # Intimidate
        trait = caller.db.traits.get('panache', 1)
        weapon = caller.db.wielded_weapon
        skill = caller.character_sheet.get_knack_value(weapon.db.attack_skill if weapon else "Attack (Fencing)")
        roll_result = roll_keep(trait + skill, trait)
        text = f"You attempt to intimidate the goons and roll {roll_result}."
    
    text += " You successfully pass through with your escort."
    return text, "adventure_phase"

def final_phase(caller):
    text = "You've successfully escorted the noble to their destination!"
    return text, "adventure_end"

def adventure_end(caller):
    caller.db.xp = caller.db.xp + 3 if hasattr(caller.db, 'xp') else 3
    caller.db.guilders = caller.db.guilders + 1000 if hasattr(caller.db, 'guilders') else 1000
    caller.db.last_escort_adventure = caller.sessions.get()[0].conn_time
    
    text = f"""
    Adventure complete!
    You've gained:
    - 3 XP
    - 1000 Guilders
    
    You can undertake another escort mission in 2 weeks.
    """
    
    # Clean up ndb attributes
    del caller.ndb._adventure_destination
    del caller.ndb._adventure_phase
    del caller.ndb._adventure_success
    del caller.ndb._participants
    if hasattr(caller.ndb, '_thug_rounds'):
        del caller.ndb._thug_rounds
    if hasattr(caller.ndb, '_thug_successes'):
        del caller.ndb._thug_successes
    if hasattr(caller.ndb, '_combat_successes'):
        del caller.ndb._combat_successes
    
    caller.msg(text)
    return "", None

# Run the adventure
def start_sea_escort_adventure(caller):
    evmenu.EvMenu(caller, "world.adventure_menu", 
                  startnode="adventure_start",
                  cmdset_mergetype="Union",
                  cmdset_priority=1,
                  auto_quit=True,
                  cmd_on_exit="look")




WARES = [
    "Alcoholic beverages",
    "Linen clothes",
    "Fishing rods",
    "Tools"
]

THREATS = [
    "Roving ghouls",
    "A gang of Vesten bandits",
    "An angry, mad member of Sophia's Daughters",
    "Crescent buccaneers"
]

def start_caravan_adventure(caller):
    evmenu.EvMenu(caller, "world.adventure_menu", 
                  startnode="caravan_adventure_start",
                  cmdset_mergetype="Replace",
                  cmdset_priority=1,
                  auto_quit=True,
                  cmd_on_exit="look")

def caravan_adventure_start(caller):
    caller.ndb._adventure_phase = 0
    caller.ndb._adventure_success = 0
    caller.ndb._participants = [caller]
    caller.ndb._wares = random.choice(WARES)
    caller.ndb._threat = random.choice(THREATS)
    
    text = f"""Welcome to the Caravan Adventure!
    You're tasked with escorting a shipment of {caller.ndb._wares} from Dragon's Cove to Esperanza.
    How many other participants (1-3)?"""
    
    options = [
        {"key": str(i), "desc": f"{i} additional participant(s)", "goto": "add_participants"}
        for i in range(1, 4)
    ]
    return text, options

def add_participants(caller, raw_string):
    num_participants = int(raw_string.strip())
    text = f"Enter the names of {num_participants} participant(s), one at a time:"
    caller.ndb._participants_to_add = num_participants
    return text, "get_participant"

def get_participant(caller, raw_string):
    participant = search_object(raw_string.strip())[0]
    if participant:
        caller.ndb._participants.append(participant)
        caller.ndb._participants_to_add -= 1
        if caller.ndb._participants_to_add > 0:
            return f"Enter next participant ({caller.ndb._participants_to_add} remaining):", "get_participant"
        else:
            return "All participants added. Ready to begin the journey?", "start_journey"
    else:
        return "Participant not found. Try again:", "get_participant"

def start_journey(caller, raw_string):
    caller.msg("The caravan sets out from Dragon's Cove!")
    return caravan_adventure_phase(caller)

def caravan_adventure_phase(caller):
    phase = caller.ndb._adventure_phase
    
    if phase >= 3:  # Adventure complete after 3 phases
        return caravan_adventure_end(caller)
    
    caller.ndb._adventure_phase += 1
    
    challenges = [
        road_challenge,
        mid_journey_challenge,
        final_challenge
    ]
    
    return challenges[phase](caller)

def road_challenge(caller):
    if caller.ndb._threat == "Roving ghouls":
        text = "Roving ghouls appear on the road! Prepare for combat!"
        return text, "resolve_ghoul_combat"
    else:
        text = "The road seems clear for now. Roll Wits + Tracking to spot any potential dangers."
        return text, "resolve_road_check"

def resolve_ghoul_combat(caller):
    text = "Roll Finesse + Attack (Fencing) to fight off the ghouls. TN 20 required to succeed."
    return text, "process_ghoul_combat"

def process_ghoul_combat(caller, raw_string):
    trait = caller.db.traits.get('finesse', 1)
    skill = caller.character_sheet.get_knack_value("Attack (Fencing)")
    
    roll_result = roll_keep(trait + skill, trait)
    success = roll_result >= 20
    
    if success:
        text = f"Success! You rolled {roll_result}. The ghouls are defeated, and the caravan can proceed safely."
        caller.ndb._adventure_success += 1
    else:
        text = f"Failure. You rolled {roll_result}. The ghouls cause some damage before retreating. The caravan suffers losses."
    
    return text, "caravan_adventure_phase"

def resolve_road_check(caller, raw_string):
    trait = caller.db.traits.get('wits', 1)
    skill = caller.character_sheet.get_knack_value("Tracking")
    
    roll_result = roll_keep(trait + skill, trait)
    success = roll_result >= 15
    
    if success:
        text = f"Success! You rolled {roll_result}. You spot potential dangers and guide the caravan safely."
        caller.ndb._adventure_success += 1
    else:
        text = f"Failure. You rolled {roll_result}. You miss some signs of danger, and the caravan faces minor setbacks."
    
    return text, "caravan_adventure_phase"

def mid_journey_challenge(caller):
    text = "The caravan reaches a crossroads. Choose your path:"
    options = [
        {"key": "Safe", "desc": "Take the longer, safer route", "goto": "resolve_mid_journey"},
        {"key": "Risky", "desc": "Take the shorter, riskier path", "goto": "resolve_mid_journey"}
    ]
    return text, options

def resolve_mid_journey(caller, raw_string):
    choice = raw_string.strip().lower()
    
    if choice == "safe":
        text = "You choose the safer route. Roll Wits + Navigation to find the best path. TN 15."
        trait = caller.db.traits.get('wits', 1)
        skill = caller.character_sheet.get_knack_value("Navigation")
    else:  # Risky
        text = "You choose the riskier path. Roll Panache + Notice to navigate quickly. TN 20."
        trait = caller.db.traits.get('panache', 1)
        skill = caller.character_sheet.get_knack_value("Notice  ")
    
    roll_result = roll_keep(trait + skill, trait)
    success = roll_result >= (15 if choice == "safe" else 20)
    
    if success:
        text += f"\nSuccess! You rolled {roll_result}. The caravan makes good progress."
        caller.ndb._adventure_success += 1
    else:
        text += f"\nFailure. You rolled {roll_result}. The caravan faces delays and minor obstacles."
    
    return text, "caravan_adventure_phase"

def final_challenge(caller):
    threat = caller.ndb._threat
    if threat == "A gang of Vesten bandits":
        text = "A gang of Vesten bandits ambushes the caravan near Esperanza!"
    elif threat == "Crescent buccaneers":
        text = "Crescent buccaneers attempt to raid the caravan just outside Esperanza!"
    elif threat == "An angry, mad member of Sophia's Daughters":
        text = "An enraged member of Sophia's Daughters confronts the caravan at Esperanza's gates!"
    else:
        text = "You reach Esperanza without further incident."
        return text, "caravan_adventure_end"
    
    text += "\nHow will you handle this final challenge?"
    options = [
        {"key": "Combat", "desc": "Engage in combat", "goto": "resolve_final_challenge"},
        {"key": "Negotiate", "desc": "Attempt to negotiate", "goto": "resolve_final_challenge"},
        {"key": "Deceive", "desc": "Try to deceive or misdirect", "goto": "resolve_final_challenge"}
    ]
    return text, options

def resolve_final_challenge(caller, raw_string):
    choice = raw_string.strip().lower()
    threat = caller.ndb._threat
    
    if choice == "combat":
        trait = caller.db.traits.get('finesse', 1)
        skill = caller.character_sheet.get_knack_value("Attack (Fencing)")
        tn = 25
    elif choice == "negotiate":
        trait = caller.db.traits.get('panache', 1)
        skill = caller.character_sheet.get_knack_value("Diplomacy")
        tn = 20
    else:  # Deceive
        trait = caller.db.traits.get('wits', 1)
        skill = caller.character_sheet.get_knack_value("Deception")
        tn = 22
    
    roll_result = roll_keep(trait + skill, trait)
    success = roll_result >= tn
    
    if success:
        text = f"Success! You rolled {roll_result} vs TN {tn}. "
        if choice == "combat":
            text += f"You defeat the {threat} and secure the caravan's safety."
        elif choice == "negotiate":
            text += f"You successfully negotiate with the {threat}, avoiding conflict."
        else:
            text += f"You cleverly deceive the {threat}, allowing the caravan to slip by unharmed."
        caller.ndb._adventure_success += 1
    else:
        text = f"Failure. You rolled {roll_result} vs TN {tn}. "
        if choice == "combat":
            text += f"The {threat} overwhelms you, causing significant damage to the caravan before retreating."
        elif choice == "negotiate":
            text += f"Your attempts at negotiation fail, and the {threat} attacks, causing some damage before being driven off."
        else:
            text += f"Your deception is seen through, and the {threat} retaliates, causing harm to the caravan."
    
    return text, "caravan_adventure_end"

def caravan_adventure_end(caller):
    success_count = caller.ndb._adventure_success
    
    # Calculate rewards
    xp_reward = 2
    guilder_reward = 1000
    
    # Apply rewards
    caller.db.xp = caller.db.xp + xp_reward if hasattr(caller.db, 'xp') else xp_reward
    caller.db.guilders = caller.db.guilders + guilder_reward if hasattr(caller.db, 'guilders') else guilder_reward
    
    text = f"""
    Caravan Adventure complete!
    You successfully delivered the shipment of {caller.ndb._wares} to Esperanza.
    Successful challenges: {success_count}/3
    
    Rewards:
    XP: {xp_reward}
    Guilders: {guilder_reward}
    """
    
    # Clean up ndb attributes
    del caller.ndb._adventure_phase
    del caller.ndb._adventure_success
    del caller.ndb._participants
    del caller.ndb._wares
    del caller.ndb._threat
    
    caller.msg(text)
    return "", None
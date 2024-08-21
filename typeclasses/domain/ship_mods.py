MODIFICATIONS = {
    "light": {
        "Oars": {"cost": 5, "positive_trait": ["maneuverable"], "effect": "Allows movement when becalmed or sailing into wind. Wits -2 when using oars."},
        "Hidden Towline": {"cost": 5, "positive_trait": ["concealed_hold"], "effect": "Increases Draft by 1"},
        "Prow Ram": {"cost": 5, "positive_trait": ["powerful_ram"], "effect": "Target suffers one additional Critical Hit, ramming ship one fewer"},
        "Reinforced Masts": {"cost": 5, "positive_trait": ["resilient"], "effect": "Roll two extra unkept dice for Wound Checks against chain shot"},
    },
    "medium": {
        "Concealed Gunports": {"cost": 10, "positive_trait": ["sneak_attack"], "effect": "Brawn can be kept secret until used"},
        "Overgunned": {"cost": 10, "positive_trait": ["extra_guns"], "effect": "Increases Brawn by 1"},
        "Silk Sails": {"cost": 10, "positive_trait": ["extra_mobility"], "effect": "Increases Panache by 1"},
        "Sturdy Hull": {"cost": 10, "positive_trait": ["extra_hull"], "effect": "Increases Resolve by 1"},
        "Well-Trained Crew": {"cost": 10, "positive_trait": ["extra_speed"], "effect": "Increases Finesse by 1"},
        "Wide Rudder": {"cost": 10, "positive_trait": ["extra_helm"], "effect": "Increases Wits by 1"}
    },
    "large": {
        "Extended Keel": {"cost": 15, "positive_trait": ["stable"], "effect": "Roll two extra unkept dice when checking for capsizing, Draft +1"},
        "Lucky": {"cost": 15, "positive_trait": ["extra_drama"], "effect": "Ship gains one extra Drama die"},
        "Smuggling Compartments": {"cost": 15, "positive_trait": ["extra_concealed_hold"], "effect": "Can hide up to 1 Cargo"},
        "Extra Cargo Space": {"cost": 20, "positive_trait": ["extra_cargo"], "effect": "Increases Cargo by 1"},
        "Extra Crew Quarters": {"cost": 20, "positive_trait": ["extra_crew"], "effect": "Increases Crew by 1"},
        "Good Captain": {"cost": 20, "positive_trait": ["skilled_captain"], "effect": "Add one unkept die to any roll once per Round"},
        "Narrow Hull": {"cost": 20, "positive_trait": ["agile"], "effect": "One Free Raise on Piloting checks through narrow openings"},
        "Boarding Party": {"cost": 25, "positive_trait": ["boarding_expert"], "effect": "Move up one result on Boarding chart"},
        "Extra Boarding Guns": {"cost": 25, "positive_trait": ["anti_boarding"], "effect": "Boarding attempts move down one result on Boarding chart"},
        "Friendly Spirit": {"cost": 25, "positive_trait": ["supernatural_aid"], "effect": "Roll two extra Kept dice on any one check once per Scene"},
        "Slight Draft": {"cost": 25, "positive_trait": ["shallow_sailing"], "effect": "Reduces Draft by 1 (minimum 1)"},
        "Swivel Cannon": {"cost": 25, "positive_trait": ["flexible_guns"], "effect": "Can fire outside normal arc with Brawn 2 once per Round"},
        "Retractable Keel": {"cost": 30, "positive_trait": ["adaptable"], "effect": "Can reduce Draft by 2, but -1 unkept die when checking for capsizing"}
    }
}

FLAWS = {
    "light": {
        "Flimsy Masts": {"points": 1, "effect": "Roll one fewer unkept die for Wound Checks against chainshot"},
        "Old": {"points": 1, "effect": "Requires maintenance every six months instead of yearly"},
        "Sluggish": {"points": 1, "effect": "Travels one less hex when moving forward"}
    },
    "medium": {
        "Brittle Hull": {"points": 2, "effect": "Wound Check dice do not explode"},
        "Leaky Hull": {"points": 2, "effect": "Resolve-related check dice do not explode"},
        "Poorly Trained Crew": {"points": 2, "effect": "Brawn-related check dice do not explode"},
        "Small Keel": {"points": 2, "effect": "Roll one fewer unkept die when checking for capsizing"},
        "Small Rudder": {"points": 2, "effect": "Wits-related check dice do not explode"},
        "Tattered Sails": {"points": 2, "effect": "Panache-related check dice do not explode"},
        "Undergunned": {"points": 2, "effect": "Brawn-related check dice (except Wound Checks) do not explode"}
    },
    "large": {
        "Incompetent Bosun": {"points": 3, "effect": "Travel speed reduced by 25%"},
        "Unlucky": {"points": 3, "effect": "Ship receives one fewer Drama die"},
        "Vermin": {"points": 3, "effect": "Provisions only last three weeks for every month's worth purchased"},
        "Awkward Cargo Space": {"points": 4, "effect": "Cargo is reduced by 1"},
        "Bad Captain": {"points": 4, "effect": "Subtract one unkept die from the first roll each Round"},
        "Cramped": {"points": 4, "effect": "Crew is reduced by 1"},
        "Disgruntled Crew": {"points": 4, "effect": "GM may spend one Drama die to have one Crew refuse to act for the rest of the Scene"},
        "Deep Draft": {"points": 5, "effect": "Draft is increased by 1"},
        "Haunted": {"points": 5, "effect": "GM may spend two Drama dice to control ship's actions for one Round"},
        "Warped Rudder": {"points": 5, "effect": "Ship turns 60 degrees to port or starboard at the end of each Round"}
    }
}
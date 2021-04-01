import importlib
import json
import traceback
import time

import modular


def trackTimeStart(mud, _):
    if 'honing' in mud.state:
        skill, counter = mud.state['honing']
        mud.send(skill)
        mud.state['honing'] = (skill, counter + 1)
        return

    mud.state['task_start_time'] = time.time()


def hone(mud, groups):
    skill = groups[0]
    mud.state['honing'] = (skill, 1)
    mud.send(skill)


honeToType = {
	'Achilles Armor': 'spell',
	'Acid Arrow': 'spell',
	'Acid Fog': 'spell',
	'Acid Spray': 'spell',
	'Add Limb': 'spell',
	'Advancement': 'spell',
	'Alarm': 'spell',
	'Alternate Reality': 'spell',
	'Alter Substance': 'spell',
	'Analyze Item': 'spell',
	'Anchor': 'spell',
	'Animate Item': 'spell',
	'Animate Weapon': 'spell',
	'Anti Plant Shell': 'spell',
	'Arcane Mark': 'spell',
	'Arcane Possession': 'spell',
	'Arms Length': 'spell',
	'a Spell': 'spell',
	'Astral Step': 'spell',
	'Augury': 'spell',
	'Awe': 'spell',
	'Awe Other': 'spell',
	'Big Mouth': 'spell',
	'Blademouth': 'spell',
	'Blind': 'spell',
	'Blink': 'spell',
	'Blur': 'spell',
	'Brainwash': 'spell',
	'Breadcrumbs': 'spell',
	'Burning Hands': 'spell',
	'Cause Stink': 'spell',
	'Chain Lightning': 'spell',
	'Change Sex': 'spell',
	'Channeled Missiles': 'spell',
	'Chant Shield': 'spell',
	'Charm': 'spell',
	'Charm Ward': 'spell',
	'Choke': 'spell',
	'Claireaudience': 'spell',
	'Clairevoyance': 'spell',
	'Clan Donate': 'spell',
	'ClanEnchant Acid': 'spell',
	'ClanEnchant Cold': 'spell',
	'ClanEnchant Disease': 'spell',
	'ClanEnchant Electric': 'spell',
	'ClanEnchant Fire': 'spell',
	'ClanEnchant Gas': 'spell',
	'ClanEnchant Mind': 'spell',
	'ClanEnchant Paralysis': 'spell',
	'ClanEnchant Poison': 'spell',
	'ClanEnchant Water': 'spell',
	'Clan Experience': 'spell',
	'Clan Home': 'spell',
	'Clan Ward': 'spell',
	'Clarify Scroll': 'spell',
	'Clog Mouth': 'spell',
	'Clone': 'spell',
	'Cloudkill': 'spell',
	'Cogniportive': 'spell',
	'Color Spray': 'spell',
	'Combat Precognition': 'spell',
	'Command': 'spell',
	'Comprehend Languages': 'spell',
	'Confusion': 'spell',
	'Conjure Ammunition': 'spell',
	'Conjure Nexus': 'spell',
	'Continual Light': 'spell',
	'Counterspell': 'spell',
	'Darkness': 'spell',
	'Darkness Globe': 'spell',
	'Daydream': 'spell',
	'Deaden Smell': 'spell',
	'Deafen': 'spell',
	'Death Warning': 'spell',
	'Delay': 'spell',
	'Delirium': 'spell',
	'Delude': 'spell',
	'Demon Gate': 'spell',
	'Destroy Object': 'spell',
	'Detect Ambush': 'spell',
	'Detect Gold': 'spell',
	'Detect Hidden': 'spell',
	'Detect Invisible': 'spell',
	'Detect Magic': 'spell',
	'Detect Metal': 'spell',
	'Detect Poison': 'spell',
	'Detect Scrying': 'spell',
	'Detect Sentience': 'spell',
	'Detect Traps': 'spell',
	'Detect Undead': 'spell',
	'Detect Water': 'spell',
	'Detect Weaknesses': 'spell',
	'Disenchant': 'spell',
	'Disenchant Wand': 'spell',
	'Disguise Other': 'spell',
	'Disguise Self': 'spell',
	'Disguise Undead': 'spell',
	'Disintegrate': 'spell',
	'Dismissal': 'spell',
	'Dispel Divination': 'spell',
	'Dispel Magic': 'spell',
	'Distant Vision': 'spell',
	'Divine Beauty': 'spell',
	'Divining Eye': 'spell',
	'Dragonfire': 'spell',
	'Dream': 'spell',
	'Duplicate': 'spell',
	'Earthquake': 'spell',
	'Elemental Storm': 'spell',
	'Enchant Armor': 'spell',
	'Enchant Arrows': 'spell',
	'Enchant Clan Equipment Base Model': 'spell',
	'Enchant Wand': 'spell',
	'Enchant Weapon': 'spell',
	'Endless Hunger': 'spell',
	'Endless Road': 'spell',
	'Enlarge Object': 'spell',
	'Enlightenment': 'spell',
	'Ensnare': 'spell',
	'Enthrall': 'spell',
	'Erase Scroll': 'spell',
	'Exhaustion': 'spell',
	'Fabricate': 'spell',
	'Faerie Fire': 'spell',
	'Faerie Fog': 'spell',
	'Fake Armor': 'spell',
	'Fake Food': 'spell',
	'Fake Spring': 'spell',
	'Fake Weapon': 'spell',
	'Farsight': 'spell',
	'Fatigue': 'spell',
	'Fear': 'spell',
	'Feather Fall': 'spell',
	'Feeblemind': 'spell',
	'Feel The Void': 'spell',
	'Feign Death': 'spell',
	'Feign Invisibility': 'spell',
	'Find Directions': 'spell',
	'Find Familiar': 'spell',
	'Fireball': 'spell',
	'Flagportation': 'spell',
	'Flameshield': 'spell',
	'Flaming Arrows': 'spell',
	'Flaming Ensnarement': 'spell',
	'Flaming Sword': 'spell',
	'Flesh Stone': 'spell',
	'Floating Disc': 'spell',
	'Fly': 'spell',
	'Fools Gold': 'spell',
	'Forceful Hand': 'spell',
	'Forecast Weather': 'spell',
	'Forget': 'spell',
	'Forked Lightning': 'spell',
	'Frailty': 'spell',
	'Free Movement': 'spell',
	'Frenzy': 'spell',
	'Friends': 'spell',
	'Frost': 'spell',
	'Future Death': 'spell',
	'Gate': 'spell',
	'Geas': 'spell',
	'Ghost Sound': 'spell',
	'Giant Strength': 'spell',
	'Globe': 'spell',
	'Grace Of The Cat': 'spell',
	'Gravity Slam': 'spell',
	'Grease': 'spell',
	'Greater Enchant Armor': 'spell',
	'Greater Enchant Weapon': 'spell',
	'Greater Globe': 'spell',
	'Greater Image': 'spell',
	'Greater Invisibility': 'spell',
	'Group Status': 'spell',
	'Grow': 'spell',
	'Gust of Wind': 'spell',
	'Harden Bullets': 'spell',
	'Haste': 'spell',
	'Hear Thoughts': 'spell',
	'Heat Metal': 'spell',
	'Helping Hand': 'spell',
	'Hold': 'spell',
	'Hungerless': 'spell',
	'Ice Lance': 'spell',
	'Ice Sheet': 'spell',
	'Ice Storm': 'spell',
	'Identify Object': 'spell',
	'Ignite': 'spell',
	'Illusory Disease': 'spell',
	'Illusory Wall': 'spell',
	'Immunity': 'spell',
	'Imprisonment': 'spell',
	'Improved Clan Ward': 'spell',
	'Improved Invisibility': 'spell',
	'Improved Planarmorph': 'spell',
	'Improved Polymorph': 'spell',
	'Improved Repairing Aura': 'spell',
	'Increase Gravity': 'spell',
	'Infravision': 'spell',
	'Insatiable Thirst': 'spell',
	'Insect Plague': 'spell',
	'Invisibility': 'spell',
	'Invisibility Sphere': 'spell',
	'Iron Grip': 'spell',
	'Irritation': 'spell',
	'Keen Edge': 'spell',
	'Kinetic Bubble': 'spell',
	'Knock': 'spell',
	'Know Alignment': 'spell',
	'Know Bliss': 'spell',
	'Know Fate': 'spell',
	'Know Origin': 'spell',
	'Know Pain': 'spell',
	'Know Value': 'spell',
	'Laughter': 'spell',
	'Lead Foot': 'spell',
	'Lesser Image': 'spell',
	'Levitate': 'spell',
	'Light': 'spell',
	'Light Blindness': 'spell',
	'Lighten Item': 'spell',
	'Lighthouse': 'spell',
	'Lightning Bolt': 'spell',
	'Light Sensitivity': 'spell',
	'Limb Rack': 'spell',
	'Limited Wish': 'spell',
	'Locate Object': 'spell',
	'Lower Resistance': 'spell',
	'Mage Armor': 'spell',
	'Mage Claws': 'spell',
	'Magical Aura': 'spell',
	'Magic Bullets': 'spell',
	'Magic Item': 'spell',
	'Magic Missile': 'spell',
	'Magic Mouth': 'spell',
	'Major Mana Shield': 'spell',
	'Mana Burn': 'spell',
	'Mana Shield': 'spell',
	'Marker Portal': 'spell',
	'Marker Summoning': 'spell',
	'Mass Disintegrate': 'spell',
	'Mass FeatherFall': 'spell',
	'Mass Fly': 'spell',
	'Mass Haste': 'spell',
	'Mass Hold': 'spell',
	'Mass Invisibility': 'spell',
	'Mass Repairing Aura': 'spell',
	'Mass Sleep': 'spell',
	'Mass Slow': 'spell',
	'Mass Waterbreath': 'spell',
	'Meld': 'spell',
	'Mend': 'spell',
	'Meteor Storm': 'spell',
	'Mind Block': 'spell',
	'Mind Fog': 'spell',
	'Mind Light': 'spell',
	'Minor Image': 'spell',
	'Minor Mana Shield': 'spell',
	'Mirage': 'spell',
	'Mirror Image': 'spell',
	'Misstep': 'spell',
	'Monster Summoning': 'spell',
	'Mute': 'spell',
	'Mystic Loom': 'spell',
	'Mystic Shine': 'spell',
	'Natural Communion': 'spell',
	'Nightmare': 'spell',
	'Obscure Self': 'spell',
	'Pass Door': 'spell',
	'Permanency': 'spell',
	'Phantasm': 'spell',
	'Phantom Hound': 'spell',
	'Planar Banish': 'spell',
	'Planar Block': 'spell',
	'Planar Bubble': 'spell',
	'Planar Burst': 'spell',
	'Planar Extension': 'spell',
	'Planarmorph': 'spell',
	'Planarmorph Self': 'spell',
	'Planar Timer': 'spell',
	'Planeshift': 'spell',
	'Pocket': 'spell',
	'Polymorph': 'spell',
	'Polymorph Object': 'spell',
	'Polymorph Self': 'spell',
	'Portal': 'spell',
	'Portal Other': 'spell',
	'Prayer Shield': 'spell',
	'Prestidigitation': 'spell',
	'Produce Flame': 'spell',
	'Prying Eye': 'spell',
	'Purge Invisibility': 'spell',
	'Read Magic': 'spell',
	'Recharge Wand': 'spell',
	'Refit': 'spell',
	'Reinforce': 'spell',
	'Repairing Aura': 'spell',
	'Repulsion': 'spell',
	'Resist Acid': 'spell',
	'Resist Arrows': 'spell',
	'Resist Bludgeoning': 'spell',
	'Resist Cold': 'spell',
	'Resist Disease': 'spell',
	'Resist Divination': 'spell',
	'Resist Electricity': 'spell',
	'Resist Fire': 'spell',
	'Resist Gas': 'spell',
	'Resist Indignities': 'spell',
	'Resist Magic Missiles': 'spell',
	'Resist Paralysis': 'spell',
	'Resist Petrification': 'spell',
	'Resist Piercing': 'spell',
	'Resist Poison': 'spell',
	'Resist Slashing': 'spell',
	'Returning': 'spell',
	'Reverse Gravity': 'spell',
	'Rogue Limb': 'spell',
	'Scatter': 'spell',
	'Scribe': 'spell',
	'Scry': 'spell',
	'See Aura': 'spell',
	'Shape Object': 'spell',
	'Shatter': 'spell',
	'Shelter': 'spell',
	'Shield': 'spell',
	'Shocking Grasp': 'spell',
	'Shockshield': 'spell',
	'Shoddy Aura': 'spell',
	'Shove': 'spell',
	'Shrink': 'spell',
	'Shrink Mouth': 'spell',
	'Silence': 'spell',
	'Simulacrum': 'spell',
	'Siphon': 'spell',
	'Sleep': 'spell',
	'Slow': 'spell',
	'Slow Projectiles': 'spell',
	'Solve Maze': 'spell',
	'Sonar': 'spell',
	'Song Shield': 'spell',
	'Spellbinding': 'spell',
	'Spell Turning': 'spell',
	'Spider Climb': 'spell',
	'Spook': 'spell',
	'Spotters Orders': 'spell',
	'Spying Stone': 'spell',
	'Stinking Cloud': 'spell',
	'Stone Flesh': 'spell',
	'Stoneskin': 'spell',
	'Summon': 'spell',
	'Summon Army': 'spell',
	'Summon Companion': 'spell',
	'Summon Enemy': 'spell',
	'Summon Flyer': 'spell',
	'Summoning Ward': 'spell',
	'Summon Marker': 'spell',
	'Summon Steed': 'spell',
	'Superior Image': 'spell',
	'Telepathy': 'spell',
	'Teleport': 'spell',
	'Teleportation Ward': 'spell',
	'Teleport Object': 'spell',
	'Thirstless': 'spell',
	'Timeport': 'spell',
	'Time Stop': 'spell',
	'Toadstool': 'spell',
	'Torture': 'spell',
	'Tourettes': 'spell',
	'Transformation': 'spell',
	'True Sight': 'spell',
	'Ugliness': 'spell',
	'Untraceable': 'spell',
	'Ventriloquate': 'spell',
	'Wall of Air': 'spell',
	'Wall of Darkness': 'spell',
	'Wall of Fire': 'spell',
	'Wall of Force': 'spell',
	'Wall of Ice': 'spell',
	'Wall of Stone': 'spell',
	'Ward Area': 'spell',
	'Watchful Hound': 'spell',
	'Water Breathing': 'spell',
	'Water Cannon': 'spell',
	'Weaken': 'spell',
	'Weakness to Acid': 'spell',
	'Weakness to Cold': 'spell',
	'Weakness to Electricity': 'spell',
	'Weakness to Fire': 'spell',
	'Weakness to Gas': 'spell',
	'Web': 'spell',
	'Well Dressed': 'spell',
	'Wish': 'spell',
	'Wizard Lock': 'spell',
	'Wizards Chest': 'spell',
	'Word of Recall': 'spell',
	'Youth': 'spell',
	'Acid Rain': 'chants',
	'Acid Ward': 'chants',
	'Air Wall': 'chants',
	'Airy Aura': 'chants',
	'Alter Time': 'chants',
	'Animal Companion': 'chants',
	'Animal Friendship': 'chants',
	'Animal Growth': 'chants',
	'Animal Spy': 'chants',
	'Ant Train': 'chants',
	'Aquatic Pass': 'chants',
	'Astral Projection': 'chants',
	'Barkskin': 'chants',
	'Bestow Name': 'chants',
	'Bite': 'chants',
	'Blight': 'chants',
	'Bloodhound': 'chants',
	'Bloody Water': 'chants',
	'Blue Moon': 'chants',
	'Boulderbash': 'chants',
	'Brittle': 'chants',
	'Brown Mold': 'chants',
	'Bull Strength': 'chants',
	'Burrowspeak': 'chants',
	'Call Companion': 'chants',
	'Call Mate': 'chants',
	'Calm Animal': 'chants',
	'Calm Seas': 'chants',
	'Calm Weather': 'chants',
	'Calm Wind': 'chants',
	'Camelback': 'chants',
	'Capsize': 'chants',
	'Cats Grace': 'chants',
	'Cave Fishing': 'chants',
	'Cave-In': 'chants',
	'Chant Ward': 'chants',
	'Charge Metal': 'chants',
	'Charm Animal': 'chants',
	'Charm Area': 'chants',
	'Cheetah Burst': 'chants',
	'Chlorophyll': 'chants',
	'Clear Moon': 'chants',
	'Cloud Walk': 'chants',
	'Cold Moon': 'chants',
	'Cold Ward': 'chants',
	'Control Fire': 'chants',
	'Control Plant': 'chants',
	'Control Weather': 'chants',
	'Crossbreed': 'chants',
	'Crystal Growth': 'chants',
	'Darkvision': 'chants',
	'Death Moon': 'chants',
	'Deep Darkness': 'chants',
	'Deep Thoughts': 'chants',
	'Dehydrate': 'chants',
	'Delay Poison': 'chants',
	'Den': 'chants',
	'Distant Fungal Growth': 'chants',
	'Distant Growth': 'chants',
	'Distant Ingrowth': 'chants',
	'Distant Overgrowth': 'chants',
	'Distant Wind Color': 'chants',
	'Dragonsight': 'chants',
	'Drifting': 'chants',
	'Drown': 'chants',
	'Druidic Connection': 'chants',
	'Druidic Pass': 'chants',
	'Eaglesight': 'chants',
	'Earthfeed': 'chants',
	'Earthpocket': 'chants',
	'Eel Shock': 'chants',
	'Eighth Totem': 'chants',
	'Eleventh Totem': 'chants',
	'Enchant Shards': 'chants',
	'Endure Rust': 'chants',
	'Enhance Body': 'chants',
	'Explosive Decompression': 'chants',
	'Favorable Winds': 'chants',
	'Feeding Frenzy': 'chants',
	'Feel Cold': 'chants',
	'Feel Electricity': 'chants',
	'Feel Heat': 'chants',
	'Feel Hunger': 'chants',
	'Feralness': 'chants',
	'Fertile Cavern': 'chants',
	'Fertility': 'chants',
	'Fertilization': 'chants',
	'Fifth Totem': 'chants',
	'Filter Water': 'chants',
	'Find Driftwood': 'chants',
	'Find Gem': 'chants',
	'Find Mate': 'chants',
	'Find Ore': 'chants',
	'Find Plant': 'chants',
	'Fire Ward': 'chants',
	'Fish Gills': 'chants',
	'Flippers': 'chants',
	'Flood': 'chants',
	'Fodder Signal': 'chants',
	'Fortify Food': 'chants',
	'Fourth Totem': 'chants',
	'Free Vine': 'chants',
	'Fungal Bloom': 'chants',
	'Fungus Feet': 'chants',
	'Fur Coat': 'chants',
	'Gas Ward': 'chants',
	'Give Life': 'chants',
	'Golem Form': 'chants',
	'Goodberry': 'chants',
	'Grapevine': 'chants',
	'Grove Walk': 'chants',
	'Grow Club': 'chants',
	'Grow Food': 'chants',
	'Grow Forest': 'chants',
	'Grow Item': 'chants',
	'Grow Oak': 'chants',
	'Harden Skin': 'chants',
	'Hawkeye': 'chants',
	'Healing Moon': 'chants',
	'Hibernation': 'chants',
	'High Tide': 'chants',
	'Hippieness': 'chants',
	'Hold Animal': 'chants',
	'Homeopathy': 'chants',
	'Honey Moon': 'chants',
	'Howlers Moon': 'chants',
	'Illusionary Forest': 'chants',
	'Killer Vine': 'chants',
	# 'Know Plants': 'chants', - scholar
	'Labyrinth': 'chants',
	'Land Legs': 'chants',
	'Land Lungs': 'chants',
	'Life Echoes': 'chants',
	'Lightning Ward': 'chants',
	'Locate Animals': 'chants',
	'Locate Plants': 'chants',
	'Love Moon': 'chants',
	'Magma Cannon': 'chants',
	'Magnetic Earth': 'chants',
	'Magnetic Field': 'chants',
	'Manic Moon': 'chants',
	'Mass Fungal Growth': 'chants',
	'Metal Mold': 'chants',
	'Meteor Strike': 'chants',
	'Mold': 'chants',
	'Moonbeam': 'chants',
	'Moon Calf': 'chants',
	'Move The Sky': 'chants',
	'Muddy Grounds': 'chants',
	'My Plants': 'chants',
	'Natural Balance': 'chants',
	'Natural Order': 'chants',
	'Nectar': 'chants',
	'Neutralize Poison': 'chants',
	'Ninth Totem': 'chants',
	'Pack Call': 'chants',
	'Pale Moon': 'chants',
	'Peace Moon': 'chants',
	'Phosphorescence': 'chants',
	'Piercing Moon': 'chants',
	'Plane Walking': 'chants',
	'Plant Bed': 'chants',
	'Plant Choke': 'chants',
	'Plant Constriction': 'chants',
	'Plant Form': 'chants',
	'Plant Maze': 'chants',
	'Plant Pass': 'chants',
	'Plant Self': 'chants',
	'Plant Snare': 'chants',
	'Plant Trap': 'chants',
	'Plant Wall': 'chants',
	'Poisonous Vine': 'chants',
	'Prayer Ward': 'chants',
	'Predict Phase': 'chants',
	'Predict Tides': 'chants',
	'Predict Weather': 'chants',
	'Purple Moon': 'chants',
	'Quake': 'chants',
	'Reabsorb': 'chants',
	'Read Runes': 'chants',
	'Recharge Shards': 'chants',
	'Recover Voice': 'chants',
	'Red Moon': 'chants',
	'Reef Walking': 'chants',
	'Refresh Runes': 'chants',
	'Reincarnation': 'chants',
	'Rend': 'chants',
	'Repel Vermin': 'chants',
	'Restore Mana': 'chants',
	'Resuscitate Companion': 'chants',
	'Rockfeet': 'chants',
	'Rockthought': 'chants',
	'Root': 'chants',
	'Rust Curse': 'chants',
	'Sacred Earth': 'chants',
	'Sapling Workers': 'chants',
	'Sea Lore': 'chants',
	'Second Totem': 'chants',
	'Sense Age': 'chants',
	'Sense Fluids': 'chants',
	'Sense Gems': 'chants',
	'Sense Metal': 'chants',
	'Sense Ores': 'chants',
	'Sense Plants': 'chants',
	'Sense Poison': 'chants',
	'Sense Pregnancy': 'chants',
	'Sense Sentience': 'chants',
	'Sense Water': 'chants',
	'Seventh Totem': 'chants',
	'Shamblermorph': 'chants',
	'Shapelessness': 'chants',
	'Shape Shift': 'chants',
	'Shillelagh': 'chants',
	'Sift Wrecks': 'chants',
	'Sixth Totem': 'chants',
	'Snatch Light': 'chants',
	'Snuff Flame': 'chants',
	'Soaring Eagle': 'chants',
	'Song Ward': 'chants',
	'Speak With Animals': 'chants',
	'Speed Aging': 'chants',
	'Speed Birth': 'chants',
	'Speed Time': 'chants',
	'Spell Ward': 'chants',
	'Star Gazing': 'chants',
	'Stone Friend': 'chants',
	'Stonewalking': 'chants',
	'Strike Barren': 'chants',
	'Summon Animal': 'chants',
	'Summon Chum': 'chants',
	'Summon Cold': 'chants',
	'Summon Coral': 'chants',
	'Summon Dustdevil': 'chants',
	'Summon Elemental': 'chants',
	'Summon Fear': 'chants',
	'Summon Fire': 'chants',
	'Summon Flower': 'chants',
	'Summon FlyTrap': 'chants',
	'Summon Food': 'chants',
	'Summon Fungus': 'chants',
	'Summon Heat': 'chants',
	'Summon Herbs': 'chants',
	'Summon Houseplant': 'chants',
	'Summon Insects': 'chants',
	'Summon Ivy': 'chants',
	'Summon Jellyfish': 'chants',
	'Summon Moon': 'chants',
	'Summon Mount': 'chants',
	'Summon Peace': 'chants',
	'Summon Plague': 'chants',
	'Summon Plants': 'chants',
	'Summon Pool': 'chants',
	'Summon Rain': 'chants',
	'Summon Rock Golem': 'chants',
	'Summon Sapling': 'chants',
	'Summon School': 'chants',
	'Summon Seaweed': 'chants',
	'Summon Seeds': 'chants',
	'Summon Sun': 'chants',
	'Summon Tree': 'chants',
	'Summon Vine': 'chants',
	'Summon Water': 'chants',
	'Summon Wind': 'chants',
	'Sunbeam': 'chants',
	'Sunray': 'chants',
	'Sweet Scent': 'chants',
	'Tangle': 'chants',
	'Tap Grapevine': 'chants',
	'Tenth Totem': 'chants',
	'Tether': 'chants',
	'Third Totem': 'chants',
	'Thorns': 'chants',
	'Tidal Wave': 'chants',
	'Tide Moon': 'chants',
	'Treeform': 'chants',
	'Treehouse': 'chants',
	'Treemind': 'chants',
	'Treemorph': 'chants',
	'Tremor Sense': 'chants',
	'Tsunami': 'chants',
	'Unbreakable': 'chants',
	'Underwater Action': 'chants',
	'Unicorns Health': 'chants',
	'Uplift': 'chants',
	'Vampire Vine': 'chants',
	'Venomous Bite': 'chants',
	'Venom Ward': 'chants',
	'Vine Mass': 'chants',
	'Vine Weave': 'chants',
	'Volcanic Chasm': 'chants',
	'Waking Moon': 'chants',
	'Warning Winds': 'chants',
	'Warp Wood': 'chants',
	'Water Cover': 'chants',
	'Waterguard': 'chants',
	'Water Hammer': 'chants',
	'Waterspout': 'chants',
	'Water Walking': 'chants',
	'Whirlpool': 'chants',
	'Whisperward': 'chants',
	'White Moon': 'chants',
	'Wind Color': 'chants',
	'Wind Shape': 'chants',
	'Wind Snatcher': 'chants',
	'Worms': 'chants',
	'Yearning': 'chants',
        }

def honed(mud, groups):
    skill = groups[0]
    if 'honing' in mud.state:
        mud.log("Honed {} in {} tries".format(skill, mud.state['honing'][1]))
        del mud.state['honing']

    if skill in honeToType:
        honeType = honeToType[skill]
    else:
        honeType = 'skill'

    mud.timers["honed_skill_scrape_" + skill] = mud.mkdelay(1, lambda m: mud.send(honeType + ' ' + skill))

    if 'hones' not in mud.state:
        mud.state['hones'] = {}
    mud.state['hones'][skill] = time.time()

    if 'hone_on_success' in mud.state:
        mud.state['hone_on_success'](skill)

    if skill in mud.state['skillLevels'] and mud.state['skillLevels'][skill] > 99:
        return
    mud.timers["hone_again_notification_for_" + skill] = mud.mkdelay(301, lambda m: mud.log("You can now hone " + skill))


def showHones(mud, _):
    found = False
    if 'hones' in mud.state:
        remove = set()
        now = time.time()
        for skill, honetime in mud.state['hones'].items():
            if now - honetime > 300:
                remove.add(skill)
            else:
                found = True
                mud.show("{}: {}s remaining\n".format(skill, 300 - int(now - honetime)))
        for skill in remove:
            del mud.state['hones'][skill]
        if not mud.state['hones']:
            del mud.state['hones']
    if not found:
        mud.show("No skills honed recently")


def setSkillLevel(mud, groups):
    if 'skillLevels' not in mud.state:
        mud.state['skillLevels'] = {}

    level = int(groups[0])
    skill = groups[1]

    mud.state['skillLevels'][skill] = level

ALIASES = {
        'newcharsetup': 'prompt %T ^N^h%h/%Hh^q ^m%m/%Mm^q ^v%v/%Vv^q %aa %-LEVELL %Xtnl %z^N %E %B\ny\ncolorset\n16\nblue\nwhite\n\nautodraw on\nautoimprove on\nautogold on\nalias define on open n~n\nalias define oe open e~e\nalias define ow open w~w\nalias define os open s~s\nalias define od open d~d\nalias define ou open u~u',
        'home': lambda mud, _: mud.modules['mapper'].go('1115504774', 'go'),
        'rt vassendar': 'run 4s d w d 2w d 2n 2e\nopen s\ns\nopen d\nrun 5d\nopen w\nw\nrun 8n w 2s 6w\nopen w\nrun 11w 3n 3w\nopen w\nrun 5w\nrun 3n 5w',
        'rt wgate': 'run 2s 3w\nopen w\nw',
        'rt sehaire': 'run w u 6w 2n 3w s 6w s 6w 2n 5w 5n w n w n 4w n e',
        'rt magic-forest': 'go 2S  3w\n open w\n go 2W  U  W  S  6W  9N W  U  N  E  N  W  2D  N  E  3N  W  5N  W  N  W  N  4W  N  E',
        'rt sengalion': 'go 2S  3w\n open w\n go 2w U  6W  2N  3W  S  6W  S  3W  7S  6E  S',
        '#hone (.+)': hone,
        '#hones': showHones,
        }

TRIGGERS = {
        'You slip on the cold wet ground.': 'stand',
        'You fall asleep from exhaustion!!': 'stand\nsleep',
        r'(Grumpy|Grumpier|Grumpiest) wants to teach you .*\.  Is this Ok .y.N..': 'y',
        '.* is DEAD!!!': 'look in body',
        'You parry ': 'disarm',
        'You attempt to disarm .* and fail!': 'disarm',
	'A floating log gets caught on the bank.  It is large enough to enter and ride': 'enter log\ne',
	'A turtle shell gets caught on the rock.  It is large enough to enter.': 'enter shell\nn',
        # "A set of wooden footholds lead up to the top of the coach": 'u\nsay high road',
        'Midgaard, a most excellent small city to start in.': 'say Midgaard',
        "Mrs. Pippet says to you 'If ye're still wanting to go to Midgaard then say": 'say Ready to go!',
        'Grumpy wants you to try to teach him about .*\. It will': 'y',
        'You feel a little cleaner, but are still very dirty.': 'bathe',
        'You feel a little cleaner.': 'bathe',
        'You feel a little cleaner; almost perfect.': 'bathe',
        'You are no longer hungry.': '!',
        'You are no longer thirsty.': '!',
        'You are starved, and near death.  EAT SOMETHING!': 'sta\neat bread\nquit\ny',
        'You are dehydrated, and near death.  DRINK SOMETHING!': 'sta\ndrink sink\nquit\ny',
        'YOU ARE DYING OF THIRST!': 'sta\ndrink barrel\nquit\ny',
        'YOU ARE DYING OF HUNGER!': 'sta\neat bread\nquit\ny',
        'Quit -- are you sure .y.N..': 'y',
        'You start .*\.': trackTimeStart,
        'You study .*\.': trackTimeStart,
        'You are done (.*)\.': lambda mud, matches: mud.mud.log("The task took {}s".format(time.time() - (mud.state['task_start_time'] if 'task_start_time' in mud.state else 0))),
        'You become better at (.+).': honed,
        '.* subtly sets something on the ground.': 'get bag\nput bag box\nexam box',
        "The mayor says, 'I'll give you 1 minute.  Go ahead....ask for your reward.'": 'say reward',
        "The mayor says 'Hello .*. Hope you are enjoying your stay.'": 'drop box\nThese obligations have been met.',
        '^\[(\d  |\d\d |\d\d\d)%\] ([^[]+)$': setSkillLevel,
        }
with open('passwords.json', 'rb') as pws:
    TRIGGERS.update(json.load(pws))


class Coffee(modular.ModularClient):
    def __init__(self, mud, name):

        self.name = name
        self.logfname = '{}.log'.format(name)
        self.mapfname = 'coffee.map'

        import modules.logging
        import modules.eval
        import modules.mapper
        importlib.reload(modular)
        importlib.reload(modules.logging)
        importlib.reload(modules.eval)
        importlib.reload(modules.mapper)

        self.modules = {}
        mods = {
                'eval': (modules.eval.Eval, []),
                'logging': (modules.logging.Logging, [self.logfname]),
                'mapper': (modules.mapper.Mapper, [False, self.mapfname]),
                }
        if name == 'grumpy' or (False and name == 'grumpier') or name == 'grumpiest' or name == 'dhtnseriao' or name == 'dhtnserioa' or name == 'dhtnseroia':
            import modules.scholar
            importlib.reload(modules.scholar)
            mods['scholar'] = (modules.scholar.Scholar, [])
        elif name == 'vassal' or name == 'robot' or name == 'landscapegoat':
            import modules.autosmith
            importlib.reload(modules.autosmith)
            mods['autosmith'] = (modules.autosmith.AutoSmith, [])
        elif name == 'magus':
            import modules.mage
            importlib.reload(modules.mage)
            mods['mage'] = (modules.mage.Mage, [])

        for modname, module in mods.items():
            try:
                constructor, args = module
                args = [mud] + args
                print("Constructing", constructor, "with", repr(args))
                self.modules[modname] = constructor(*args)
            except Exception:
                traceback.print_exc()

        super().__init__(mud)

        self.aliases.update(ALIASES)
        self.aliases.update({
            '#autohone ([^,]+), (.+)': lambda mud, groups: self.startAutoHone(groups[0], groups[1]),
                })
        self.triggers.update(TRIGGERS)
        self.triggers.update({r'\(Enter your character name to login\)': name})

        if name == 'zerleha':
            self.triggers.update({
                'You are now listed as AFK.': 'sc',
                'You are hungry.': 'eat bread',
                'You are thirsty.': 'drink drum',
                })
        elif name == 'grumpier':  # monk
            self.aliases.update({
                'kk( +.+)?': lambda mud, groups: self.stackToLag('gouge\ntrip\ndirt\nax\nkick\nbodyflip\natemi\nbodytoss\nemote is done with stacking `kk`.', groups[0]),
                })
            # self.triggers.update({
             #    'You is done with stacking `(.+)`.': lambda mud, groups: self.stackToLag('gouge\ntrip\nax\nkick\nbodyflip\nbodytoss\nemote is done with stacking `kk`.', groups[0]),
              #   })
        elif name == 'punchee':  # group leader
            self.aliases.update({
                'waa': 'sta\nwake cizra\nwake basso',
                })
        elif name == 'basso' or name == 'cizra':  # followers
            self.triggers.update({
                    'Punchee lays down and takes a nap.': 'sleep',
                    })
        elif name == 'cizra':
            self.triggers.update({
                    '(\w+): A closed door': lambda mud, matches: 'open ' + matches[0],
                    '(\w+) : A closed door': lambda mud, matches: 'open ' + matches[0],
                    'You point at .*, shooting forth a magic missile!': 'mm',
                    'You point at .*, shooting forth a blazing fireball!': 'ff',
                    'You are too close to .* to use Fireball.': 'mm',

                    # spell failures
                    'You point at .*, but nothing more happens.': 'ff',
                    'You point at .*, but fizzle the spell.': 'mm',
                    'You attempt to invoke magical protection, but fail.': 'cast mage armor',
                    'You shout combatively, but nothing more happens.': 'cast combat precognition',
                    'You cast a spell on yourself, but the magic fizzles.': 'cast fly',
                    'You attempt to invoke a spell, but fail miserably.': 'cast shield',

                    # recasts
                    'Your magical armor fades away.': 'cast mage armor',
                    'You begin to feel a bit more vulnerable.': 'cast shield',
                    'The light above you dims.': 'cast light',
                    'Your combat precognition fades away.': 'cast combat prec',
                    'You begin to float back down.': 'cast fly',
                    'Your skin softens.': 'cast stoneskin',
                    })

    def stackToLag(self, cmds, target):
        lag = 0
        cmd = cmds.split('\n')[0]
        if target:
            cmd = cmd + target
        self.send(cmd)
        for cmd in cmds.split('\n')[1:]:
            self.timers["stackToLag" + cmd] = self.mkdelay(lag, lambda m, cmd=cmd: self.mud.send(cmd))
            lag += 2.6

    def getHostPort(self):
        return 'coffeemud.net', 2324

    def level(self):
        return self.gmcp['char']['status']['level']

    def exprate(self, mud):
        if 'char' not in self.gmcp or 'status' not in self.gmcp['char'] or 'tnl' not in self.gmcp['char']['status']:
            return

        if 'exprate_prev' not in self.state:
            self.state['exprate_prev'] = self.gmcp['char']['base']['perlevel'] - self.gmcp['char']['status']['tnl']
        else:
            now = self.gmcp['char']['base']['perlevel'] - self.gmcp['char']['status']['tnl']
            self.log("Exp per hour: {}".format(now - self.state['exprate_prev']))
            self.state['exprate_prev'] = now


    def getTimers(self):
        return {
                "exprate": (False, 60*60, 30, self.exprate),
                }

    def onMaxMana(self):
        if 'mage' in self.modules:
            self.modules['mage'].onMaxMana()

    def handleGmcp(self, cmd, value):
        super().handleGmcp(cmd, value)
        if cmd == 'char.status' and 'pos' in value and 'fatigue' in value and 'maxstats' in self.gmcp['char']:
            if value['pos'] == 'Sleeping' and value['fatigue'] == 0 and self.gmcp['char']['vitals']['moves'] == self.gmcp['char']['maxstats']['maxmoves']:
                self.log("Rested!")
        if cmd == 'char.vitals' and 'status' in self.gmcp['char'] and 'maxstats' in self.gmcp['char']:
            if self.gmcp['char']['status']['pos'] == 'Sleeping' and value['mana'] == self.gmcp['char']['maxstats']['maxmana']:
                self.onMaxMana()

        if cmd == 'char.vitals' and 'maxstats' in self.gmcp['char']:
            if 'prevhp' in self.state and self.gmcp['char']['status']['pos'] == 'Sleeping':
                hp = self.gmcp['char']['vitals']['hp']
                maxhp = self.gmcp['char']['maxstats']['maxhp']
                if hp == maxhp and self.state['prevhp'] < maxhp:
                    self.log("Healed!")
                self.state['prevhp'] = hp
                pass

        if cmd == 'char.vitals' and 'maxstats' in self.gmcp['char']:
            if self.gmcp['char']['status']['pos'] == 'Sleeping' and self.gmcp['char']['vitals']['mana'] > 100:
                # self.log("Full mana!")
                if self.name == 'hippie':
                    self.send("sta\nchant speed time\ndrink sink\nsleep")

    def startAutoHone(self, skill, cmd):
        self.log("Autohoning {} as {}".format(skill, cmd))
        self.timers['autohone_' + cmd] = self.mktimernow(60*5 + 1, lambda mud: self.honeTimer(skill, cmd))

    def honeTimer(self, skill, cmd):
        def onHoneSuccess(skillHoned):
            if skill == skillHoned:
                if skill in self.state['skillLevels'] and self.state['skillLevels'][skill] >= 99:
                    self.log("Removing " + skill + " from autohone")
                    del self.timers['autohone_' + cmd]
                else:
                    self.setTimerRemaining('autohone_' + cmd, 301)
                    self.send('sleep')

        # multi-hone timers need work
        self.state['hone_on_success'] = onHoneSuccess
        self.state['honing'] = (cmd, 1)
        self.send('sta\n{}'.format(cmd))


def getClass():
    return Coffee

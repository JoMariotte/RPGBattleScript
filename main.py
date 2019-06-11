from classes.core import Character, bcolors
from classes.magic import Spell
from classes.inventory import Item
import random
import re

# TODO Backtracking in  the menu (items and magic)
#   Add the possibility of reviving a character
#   State alteration (Sleep, poison, slow...)
#   Balance the game
#   Leveling system (How to handle the scalability though ?)
#   Save File (JSON ?)
#   Random encounter with predifined enemies loaded via a JSON file


def valid_input(userinput, length):
    if re.match("[0-9]", userinput):
        if 1 <= int(userinput) <= length:
            return True
    return False


def perform_action(character):
    userInput = "0"
    actionCheck = False
    while not actionCheck:
        character.choose_action()
        userInput = input("    Choose action: ")
        if valid_input(userInput, len(character.actions)):
            if int(userInput) == 2 and character.get_mp() < 14:
                print("        You don't have enough MP to cast any magic, please choose another action !")
            else:
                actionCheck = True
    return int(userInput) - 1


def check_battle_status():
    global running
    if len(characters) == 0:
        print(bcolors.FAIL + "\nYOU DIED" + bcolors.ENDC)
        running = False

    if len(enemies) == 0:
        print(bcolors.OKGREEN + "\nYOU WON" + bcolors.ENDC)
        running = False


def acquire_target(character):
    character.choose_target(enemies)
    userInput = input("    Choose target:")
    while not valid_input(userInput, len(enemies)):
        character.choose_target(enemies)
        userInput = input("    Choose target:")
    return int(userInput) - 1


def attack(character):
    dmg = character.generate_damage()
    enemy = acquire_target(character)
    enemies[enemy].take_damage(dmg)
    print("You attacked " + enemies[enemy].name.replace(" ", "") + " for", dmg, "points of damage.")

    if enemies[enemy].get_hp() == 0:
        print(enemies[enemy].name.replace(" ", "") + " has died.")
        del enemies[enemy]
        check_battle_status()


def use_magic(character):
    userInput = "0"
    magicCheck = False
    while not magicCheck:
        character.choose_magic()
        userInput = input("    Choose magic: ")
        if valid_input(userInput, len(character.magic)):
            if character.get_mp() < character.magic[int(userInput) - 1].cost:
                print("        You don't have enough MP to cast that spell, please choose another one !")
            else:
                magicCheck = True
    magic_choice = int(userInput) - 1
    spell = character.magic[magic_choice]
    magic_hp = spell.generate_hp()
    character.reduce_mp(spell.cost)
    if spell.type == "white":
        character.heal(magic_hp)
        print(bcolors.OKBLUE + "\n" + spell.name + " heals for", str(magic_hp), "HP." + bcolors.ENDC)
    elif spell.type == "black":
        enemy = acquire_target(character)
        enemies[enemy].take_damage(magic_hp)
        print(bcolors.OKBLUE + "\n" + spell.name + " deals", str(magic_hp),
              "points of damage to " + enemies[enemy].name.replace(" ", "") + bcolors.ENDC)

        if enemies[enemy].get_hp() == 0:
            print(enemies[enemy].name.replace(" ", "") + " has died.")
            del enemies[enemy]
            check_battle_status()


def use_item(character):
    userInput = "0"
    itemCheck = False
    while not itemCheck:
        character.choose_item()
        userInput = input("    Choose item: ")
        if valid_input(userInput, len(character.items)):
            if character.items[int(userInput) - 1].quantity == 0:
                print("        You don't have any occurence of this object left, please choose another one !")
            else:
                itemCheck = True
    item_choice = int(userInput) - 1
    item = character.items[item_choice]
    character.items[item_choice].quantity -= 1
    if item.type == "potion":
        character.heal(item.prop)
        print(bcolors.OKGREEN + "\n" + item.name + " heals for", str(item.prop), "HP" + bcolors.ENDC)
    elif item.type == "elixir":
        if item.name == "MegaElixir":
            for i in characters:
                i.hp = i.maxhp
                i.mp = i.maxmp
        else:
            character.hp = character.maxhp
            character.mp = character.maxmp
        print(bcolors.OKGREEN + "\n" + item.name + " fully restores HP/MP" + bcolors.ENDC)
    elif item.type == "attack":
        enemy = acquire_target(character)
        enemies[enemy].take_damage(item.prop)
        print(bcolors.FAIL + "\n" + item.name + " deals", str(item.prop),
              "points of damage to " + enemies[enemy].name + bcolors.ENDC)

        if enemies[enemy].get_hp() == 0:
            print(enemies[enemy].name.replace(" ", "") + " has died.")
            del enemies[enemy]
            check_battle_status()


def perform_character_turn(character):
    actionIndex = perform_action(character)
    if actionIndex == 0:
        attack(character)
    elif actionIndex == 1:
        use_magic(character)
    elif actionIndex == 2:
        use_item(character)


def perform_enemies_turn(enemy):
    enemy_choice = random.randrange(0, 2)
    if enemy_choice == 0:
        # attack
        target = random.randrange(0, len(characters))
        enemy_dmg = enemy.generate_damage()
        characters[target].take_damage(enemy_dmg)
        print(enemy.name.replace(" ", "") + " attacks " + characters[target].name.replace(" ", "") + " for", enemy_dmg)
        if characters[target].get_hp() == 0:
            print(characters[target].name.replace(" ", "") + " has died.")
            del characters[target]
            check_battle_status()
    elif enemy_choice == 1:
        # magic
        spell, magic_dmg = enemy.choose_enemy_spell()
        enemy.reduce_mp(spell.cost)
        if spell.type == "white":
            enemy.heal(magic_dmg)
            print(bcolors.OKBLUE + spell.name + " heals " + enemy.name + " for", str(magic_dmg), "HP." + bcolors.ENDC)
        elif spell.type == "black":
            target = random.randrange(0, len(characters))
            characters[target].take_damage(magic_dmg)
            print(bcolors.OKBLUE + "\n" + enemy.name.replace(" ", "") + "'s " + spell.name + " deals", str(magic_dmg),
                  "points of damage to " + characters[target].name.replace(" ", "") + bcolors.ENDC)
            if characters[target].get_hp() == 0:
                print(characters[target].name.replace(" ", "") + " has died.")
                del characters[target]
                check_battle_status()


# Black Magic
fire = Spell("Fire", 25, 600, "black")
thunder = Spell("Thunder", 25, 600, "black")
blizzard = Spell("Blizzard", 25, 600, "black")
meteor = Spell("Meteor", 40, 1200, "black")
quake = Spell("Quake", 30, 900, "black")

# White Magic
cure = Spell("Cure", 25, 620, "white")
cura = Spell("Cura", 32, 1500, "white")
curaga = Spell("Curaga", 50, 6000, "white")

# Items
potion = Item("Potion", "potion", "Heals 50 HP", 50, 15)
hipotion = Item("Hi-Potion", "potion", "Heals 100 HP", 100, 5)
superpotion = Item("Super Potion", "potion", "Heals 1000 HP", 1000, 5)
elixir = Item("Elixir", "elixir", "Fully restores HP/MP of one party member", 9999, 5)
megaelixir = Item("MegaElixir", "elixir", "Fully restores party's HP/MP", 9999, 5)
grenade = Item("Grenade", "attack", "Deals 500 damage", 300, 5)

player_spells = [fire, thunder, blizzard, meteor, quake, cure, cura]
enemy_spells = [fire, meteor, curaga]
player_items = [potion, hipotion, superpotion, elixir, megaelixir, grenade]

# Instantiate People
player1 = Character("Kaz :", 3260, 132, 300, 34, player_spells, player_items)
player2 = Character("Jo  :", 4160, 188, 311, 34, player_spells, player_items)
player3 = Character("Morg:", 3089, 174, 288, 34, player_spells, player_items)

enemy1 = Character("Peon ", 1250, 130, 560, 325, enemy_spells, [])
enemy2 = Character("Ruler", 18200, 701, 525, 25, enemy_spells, [])
enemy3 = Character("Peon ", 1250, 130, 560, 325, enemy_spells, [])

characters = [player1, player2, player3]
enemies = [enemy1, enemy2, enemy3]

running = True

print(bcolors.FAIL + bcolors.BOLD + "ENEMIES ATTACK !" + bcolors.ENDC)

while running:
    print("======================")
    print("\n\n")

    print("NAME                 HP                                     MP")
    for character in characters:
        character.get_stats()
    print("\n")
    for enemy in enemies:
        enemy.get_enemy_stats()

    for character in characters:
        perform_character_turn(character)
    print("\n")
    for enemy in enemies:
        perform_enemies_turn(enemy)

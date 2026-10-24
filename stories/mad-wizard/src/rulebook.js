var all_spells = [
	{name: "Windstorm", level: 2},
	{name: "Snowdrift", level: 3},
	{name: "Flamestrike", level: 4},
	{name: "Undergrowth", level: 2},
	{name: "Levitation", level: 4},
];

window.all_buffs = ["muscle", "stamina", "agility", "speed", "focus"];

window.all_monsters = {
	"armor": {
		name: "Clockwork armor",
		size: 12,
		
		muscle: 3,
		stamina: 4,
		agility: 2,
		speed: 2,
		focus: 1,
		
		weapon: {
			name: "whirling blades",
			attack: 6,
			damage: 6
		},
	},

	"roaches": {
		name: "Giant cockroaches",
		size: 4,
		
		muscle: 2,
		stamina: 5,
		agility: 5,
		speed: 5,
		focus: 2,
		
		weapon: {
			name: "mandibles",
			attack: 2,
			damage: 4
		},
	},

	"plants": {
		name: "Carnivorous plants",
		size: 6,
		
		muscle: 4,
		stamina: 4,
		agility: 4,
		speed: 1,
		focus: 1,
		
		weapon: {
			name: "toothy flowers",
			attack: 3,
			damage: 6
		},
	},

	"shadows": {
		name: "Living shadows",
		size: 8,
		
		muscle: 3,
		stamina: 3,
		agility: 3,
		speed: 3,
		focus: 3,
		
		weapon: {
			name: "bloody fangs",
			attack: 4,
			damage: 6
		},
	},

	"tentacles": {
		name: "Mass of tentacles",
		size: 10,
		
		muscle: 5,
		stamina: 4,
		agility: 3,
		speed: 2,
		focus: 1,
		
		weapon: {
			name: "suction cups",
			attack: 6,
			damage: 4
		},
	},
};

window.create_character = function (char_name, size_die) {
	return {
		name: char_name, // Mirrored for debugging.
		size: size_die,
		
		muscle: 2,
		stamina: 2,
		agility: 2,
		speed: 2,
		focus: 2,
		
		wounds: 0,
		blessings: 0,
		experience: 0,
		
		weapon: null,
		armor: null,
		
		buffs: {
			muscle: 0,
			stamina: 0,
			agility: 0,
			speed: 0,
			focus: 0,
		},
		
		inventory: {
			rations: 0,
			potions: {
				muscle: 0,
				stamina: 0,
				agility: 0,
				speed: 0,
				focus: 0,
			},
		},
		
		spellbook: {},
	};
};

window.equip_character = function (character, archetype) {
	character.inventory.rations = 3;
	if (archetype === "fighter") {
		character.weapon = {
			name: "double axe",
			attack: 6,
			damage: 6
		};
		character.armor = {
			name: "chain mail",
			protection: 8
		};
		character.inventory.potions.agility = 1;
		character.inventory.potions.speed = 1;
		var spell = all_spells.random();  // SugarCube 2 feature.
		character.spellbook[spell.name] = {
			level: spell.level,
			charges: 1
		};
	} else if (archetype === "rogue") {
		character.weapon = {
			name: "pair of daggers",
			attack: 4,
			damage: 4
		};
		character.armor = {
			name: "studded leather",
			protection: 6
		};
		character.inventory.potions.muscle = 1;
		character.inventory.potions.stamina = 1;
		var spell = all_spells.random();  // SugarCube 2 feature.
		character.spellbook[spell.name] = {
			level: spell.level,
			charges: 1
		};
	} else if (archetype === "mage") {
		character.weapon = {
			name: "mage staff",
			attack: 6,
			damage: 4
		};
		character.armor = {
			name: "thick robes",
			protection: 4
		};
		var potions = ["muscle", "stamina", "agility", "speed"];
		potions = potions.randomMany(3); // SugarCube 2 feature.
		for (var i = 0; i < potions.length; i++) {
			var p = potions[i];
			character.inventory.potions[p] = 1;
		}
		var spells = all_spells.randomMany(3);  // SugarCube 2 feature.
		for (var i = 0; i < spells.length; i++) {
			var s = spells[i];
			character.spellbook[s.name] = {
				level: s.level,
				charges: 1
			};
		}
	}
};

window.roll_dice = function (count, sides, modifier) {
	var modifier = modifier || 0;
	var sum = 0;
	for (var i = 0; i < count; i++)
		sum += random(1, sides); // SugarCube 2 feature.
	return sum + modifier;
};

window.roll_challenge = function (character, attribute) {
	var sum = 0;
	
	if (character.buffs[attribute] > 0)
		var dice_pool = character[attribute] + 1;
	else
		var dice_pool = character[attribute];
		
	for (var i = 0; i < 3; i++)
		sum += roll_dice(dice_pool, character.size);
			
	if (character.blessings > 0) {
		character.blessings--;
		var sum2 = 0;
		for (var i = 0; i < 3; i++)
			sum2 += roll_dice(dice_pool, character.size);
		return Math.max(sum, sum2);
	} else {
		return sum;
	}
};

window.roll_attack = function (attacker, defender) {
	if (attacker.buffs !== undefined && attacker.buffs.agility > 0)
		var dice_pool = attacker.agility + 1;
	else
		var dice_pool = attacker.agility;

	var base_roll = roll_dice(dice_pool, attacker.size);
	if (attacker.blessings > 0) {
		attacker.blessings--;
		var new_roll = roll_dice(dice_pool, attacker.size);
		if (new_roll > base_roll)
			base_roll = new_roll;
	}
	
	if (attacker.size < defender.size)
		var size_bonus = (defender.size - attacker.size) / 2;
	else
		var size_bonus = 0;
	
	if (attacker.weapon !== null)
		var weapon_bonus = attacker.weapon.attack;
	else
		var weapon_bonus = 0;
	
	console.log(attacker.name
		+ " rolls " + base_roll
		+ "+" + size_bonus
		+ "+" + weapon_bonus);
	
	return base_roll + size_bonus + weapon_bonus;
};

window.roll_damage = function (attacker, defender, margin) {
	if (attacker.buffs !== undefined && attacker.buffs.muscle > 0)
		var dice_pool = attacker.muscle + 1;
	else
		var dice_pool = attacker.muscle;

	margin += (attacker.muscle - 3) * attacker.size / 2;
	
	if (attacker.weapon !== null)
		var damage_bonus = roll_dice(1, attacker.weapon.damage);
	else
		var damage_bonus = 0;
	
	var damage = Math.max(0, margin + damage_bonus);
	
	if (defender.armor === null)
		var soak_up = 0;
	else if (defender.armor.protection > damage)
		var soak_up = 0;
	else
		var soak_up = defender.armor.protection;
	
	console.log(attacker.name
		+ " deals " + margin
		+ "+" + damage_bonus
		+ "-" + soak_up
		+ " damage to " + defender.name);
	
	return damage - soak_up;
};

window.heal_wounds = function (character, amount) {
	character.wounds -= amount;
	if (character.wounds < 0)
		character.wounds = 0;
};

window.refresh_spells = function (character) {
	var spells = character.spellbook;
	var refreshed = [];
	for (var i in spells) {
		if (spells[i].charges > 0) continue;
		
		var roll = roll_challenge(character, "focus");
		
		if (roll >= spells[i].level * 10) {
			spells[i].charges += 1;
			refreshed.push({name: i, success: true});
		} else {
			refreshed.push({name: i, success: false});
		}
	}
	return refreshed;
};

window.refresh_energy = function (character) {
	if (character.buffs.speed > 0)
		character.energy += (character.speed + 1) * character.size;
	else
		character.energy += character.speed * character.size;
	for (var i in character.buffs)
		if (character.buffs[i] > 0)
			character.buffs[i]--;
};

window.give_random_potion = function (character) {
	var potion = all_buffs.random();
	character.inventory.potions[potion]++;
	return potion;
};

window.give_random_spell = function (character) {
	var spell = all_spells.random();
	if (character.spellbook[spell.name] === undefined) {
		character.spellbook[spell.name] = {
			level: spell.level,
			charges: 1
		};
	} else {
		character.spellbook[spell.name].charges++;
	}
	return spell.name;
};

window.buff_attribute = function (character, attribute) {
	if (character.buffs[attribute] > 0)
		character.buffs[attribute] += 2;
	else
		character.buffs[attribute] += 3;
	return character.buffs[attribute];
};

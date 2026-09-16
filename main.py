import copy

factorial_dict = {}


def factorial(x):
	if x in factorial_dict:
		return factorial_dict[x]
	if x == 0 or x == 1:
		return 1
	else:
		result = x * factorial(x - 1)
		factorial_dict[x] = result
		return result


combination_dict = {}


def combination(n, r):
	if (n, r) in combination_dict:
		return combination_dict[(n, r)]
	else:
		ans = factorial(n) / factorial(n - r) / factorial(r)
		combination_dict[(n, r)] = ans
		return ans


class Skill:
	def __init__(
		self, base_power, coin_count, coin_power, sanity, paralysis=0
	):
		self._base_power = base_power
		self._coin_count = coin_count
		self._coin_power = coin_power
		self._sanity = sanity
		self._paralysis = paralysis

	@property
	def base_power(self):
		return self._base_power

	@property
	def coin_count(self):
		return self._coin_count

	@property
	def coin_power(self):
		return self._coin_power

	@property
	def sanity(self):
		return self._sanity

	@property
	def paralysis(self):
		return self._paralysis

	@property
	def divisible(self):
		if self.base_power > 0 and self.coin_power > 0:
			return True
		if self.paralysis > 0:
			return True
		return False

	@property
	def static_id(self):
		return (self.base_power, self.coin_count, self.coin_power, self.sanity)

	@property
	def dynamic_id(self):
		return (
			self.base_power,
			self.coin_count,
			self.coin_power, 
			self.sanity,
			self.paralysis,
		)

	@property
	def effective_dynamic_id(self):
		return (
			self.base_power,
			self.coin_count,
			self.coin_power,
			self.sanity,
			min(self.paralysis, self.coin_count),
		)

	@property
	def lose_skill(self):
		return Skill(self.base_power,
					self.coin_count - 1,
					self.coin_power,
					self.sanity,
					max(self.paralysis - self.coin_count, 0))

	@property
	def next_skill(self):
		return Skill(self.base_power,
					self.coin_count,
					self.coin_power,
					self.sanity,
					max(self.paralysis - self.coin_count, 0))

	def __str__(self):
		return f"{self.base_power}+{self.coin_power}x{self.coin_count} at {self.sanity} SP and {self.paralysis} paralysis"


def get_divided_skill(skill):
	# divides a skill into base power, and paralyzed and non paralyzed coins if possible
	paralysis = skill.paralysis
	state = {}

	result = []
	result.append(Skill(skill.base_power, 1, 0, 0, -50))
	consecutive_coins = 0

	def append_skill():
		if state["paralyzed"]:
			result.append(Skill(0, consecutive_coins, 0, -50))
		else:
			result.append(
				Skill(
					0, consecutive_coins, skill.coin_power, skill.sanity
				)
			)

	for coin in range(skill.coin_count):
		new_state = {}
		if paralysis > 0:
			new_state["paralyzed"] = True
		else:
			new_state["paralyzed"] = False

		if state == {}:
			state = new_state
			consecutive_coins = 1
		elif state == new_state:
			consecutive_coins += 1
		else:
			append_skill()

			consecutive_coins = 1
			state = new_state

		paralysis = max(paralysis - 1, 0)

	append_skill()

	return result


combined_power_probabilities_dict = {}


def get_combined_power_probabilities(
	power_probabilities1, power_probabilities2
):
	key = (frozenset(power_probabilities1.items()), frozenset(power_probabilities2.items()))
	if key in combined_power_probabilities_dict:
		return combined_power_probabilities_dict[key]

	result = {}

	for power1 in power_probabilities1:
		for power2 in power_probabilities2:
			combined_power = power1 + power2
			combined_probability = (
				power_probabilities1[power1] * power_probabilities2[power2]
			)
			if combined_power not in result:
				result[combined_power] = 0.0

			result[combined_power] += combined_probability

	combined_power_probabilities_dict[key] = result
	return result


power_probabilities_dict = {}


def get_power_probabilities(skill):
	if skill.effective_dynamic_id in power_probabilities_dict:
		return power_probabilities_dict[skill.effective_dynamic_id]
	elif skill.divisible:
		divided_skills = get_divided_skill(skill)
		
		power_probabilities = []
		for skill in divided_skills:
			power_probabilities.append(get_power_probabilities(skill))

		combined_power_probabilities = power_probabilities[0]
		for i in range(1, len(power_probabilities)):
			combined_power_probabilities = get_combined_power_probabilities(combined_power_probabilities, power_probabilities[i])

		return combined_power_probabilities

	heads_probability = skill.sanity / 100 + 0.5
	tails_probability = 1 - heads_probability

	result = {}

	for head_count in range(0, skill.coin_count + 1):
		tail_count = skill.coin_count - head_count

		power = skill.base_power + skill.coin_power * head_count
		power = max(power, 0)
		probability = (
			heads_probability**head_count
			* tails_probability**tail_count
			* combination(skill.coin_count, head_count)
		)
		if power not in result:
			result[power] = 0.0

		result[power] += probability

	power_probabilities_dict[skill.effective_dynamic_id] = result
	return result


outcome_probabilities_dict = {}


def get_parry_outcome_probabilities(skill1, skill2):
	effective_dynamic_key = (skill1.effective_dynamic_id, skill2.effective_dynamic_id)
	if effective_dynamic_key in outcome_probabilities_dict:
		return outcome_probabilities_dict[effective_dynamic_key]

	power_probabilities1 = get_power_probabilities(skill1)
	power_probabilities2 = get_power_probabilities(skill2)

	result = {"win": 0.0, "tie": 0.0, "lose": 0.0}
	for power1 in power_probabilities1:
		power1_probability = power_probabilities1[power1]
		for power2 in power_probabilities2:
			power2_probability = power_probabilities2[power2]

			combined_probability = power1_probability * power2_probability
			if power1 > power2:
				result["win"] += combined_probability
			elif power1 < power2:
				result["lose"] += combined_probability
			else:
				result["tie"] += combined_probability

	outcome_probabilities_dict[effective_dynamic_key] = result
	return result


clash_dict = {}


def clash(skill1, skill2, parry):
	dynamic_key = (skill1.dynamic_id, skill2.dynamic_id, parry)
	if dynamic_key in clash_dict:
		return clash_dict[dynamic_key]

	result = {"win": 0.0, "tie": 0.0, "lose": 0.0}
	if skill2.coin_count == 0:
		result["win"] = 1.0
		return result
	elif skill1.coin_count == 0:
		result["lose"] = 1.0
		return result
	elif parry == 99:
		result["tie"] = 1.0
		return result

	parry_outcome_probabilities = get_parry_outcome_probabilities(
		skill1, skill2
	)

	if parry_outcome_probabilities["win"] == 0.0:
		parry_win_clash_outcomes = {"win": 0.0, "tie": 0.0, "lose": 0.0}
	else:
		parry_win_clash_outcomes = clash(skill1.next_skill, skill2.lose_skill, parry + 1)

	if parry_outcome_probabilities["lose"] == 0.0:
		parry_lose_clash_outcomes = {"win": 0.0, "tie": 0.0, "lose": 0.0}
	else:
		parry_lose_clash_outcomes = clash(skill1.lose_skill, skill2.next_skill, parry + 1)

	if parry_outcome_probabilities["tie"] == 0.0:
		parry_tie_clash_outcomes = {"win": 0.0, "tie": 0.0, "lose": 0.0}
	else:
		parry_tie_clash_outcomes = clash(skill1.next_skill, skill2.next_skill, parry + 1)

	
	result["win"] = (
		parry_outcome_probabilities["win"] * parry_win_clash_outcomes["win"]
		+ parry_outcome_probabilities["tie"] * parry_tie_clash_outcomes["win"]
		+ parry_outcome_probabilities["lose"]
		* parry_lose_clash_outcomes["win"]
	)
	result["tie"] = (
		parry_outcome_probabilities["win"] * parry_win_clash_outcomes["tie"]
		+ parry_outcome_probabilities["tie"] * parry_tie_clash_outcomes["tie"]
		+ parry_outcome_probabilities["lose"]
		* parry_lose_clash_outcomes["tie"]
	)
	result["lose"] = (
		parry_outcome_probabilities["win"] * parry_win_clash_outcomes["lose"]
		+ parry_outcome_probabilities["tie"] * parry_tie_clash_outcomes["lose"]
		+ parry_outcome_probabilities["lose"]
		* parry_lose_clash_outcomes["lose"]
	)

	clash_dict[dynamic_key] = result
	return result

import time
start_time = time.time()
skill1 = Skill(1, 20, 1, 0, 300)
skill2 = Skill(1, 20, 1, 0, 300)
print(clash(skill1, skill2, 0))
print("Unique Clashes:", len(clash_dict))
print("--- %s seconds ---" % (time.time() - start_time))
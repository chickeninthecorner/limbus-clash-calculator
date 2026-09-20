from pyscript import when, document
from main import clash, Skill

@when("click", "#clash")
def calculate_clash(event=None):
	try:
		base_power_1 = int(document.querySelector("#base-power-1").value)
		coin_power_1 = int(document.querySelector("#coin-power-1").value)
		coin_count_1 = int(document.querySelector("#coin-count-1").value)
		sanity_1 = int(document.querySelector("#sanity-1").value)
		paralysis_1 = int(document.querySelector("#paralysis-1").value)
	
		coins_1 = []
	
		container = document.querySelector("#circle-container-1")
		contained_coins = container.querySelectorAll(".coin")
	
		for coin in contained_coins:
			if coin.classList.contains("normal"):
				coins_1.append('N')
			elif coin.classList.contains("red"):
				coins_1.append('R')
	
		base_power_2 = int(document.querySelector("#base-power-2").value)
		coin_power_2 = int(document.querySelector("#coin-power-2").value)
		coin_count_2 = int(document.querySelector("#coin-count-2").value)
		sanity_2 = int(document.querySelector("#sanity-2").value)
		paralysis_2 = int(document.querySelector("#paralysis-2").value)
	
		coins_2 = []
		
		container = document.querySelector("#circle-container-2")
		contained_coins = container.querySelectorAll(".coin")
	
		for coin in contained_coins:
			if coin.classList.contains("normal"):
				coins_2.append('N')
			elif coin.classList.contains("red"):
				coins_2.append('R')
	
		skill1 = Skill(base_power_1, tuple(coins_1), coin_power_1, sanity_1, paralysis_1)
		skill2 = Skill(base_power_2, tuple(coins_2), coin_power_2, sanity_2, paralysis_2)
		
		result = clash(skill1, skill2, 0)
		
		document.querySelector("#win-rate").innerHTML = f"{result.win_rates.overall_rate * 100:.2f}%"
		document.querySelector("#tie-rate").innerHTML = f"{result.tie_rates.overall_rate * 100:.2f}%"
		document.querySelector("#lose-rate").innerHTML = f"{result.lose_rates.overall_rate * 100:.2f}%"

		container = document.querySelector("#win-line-container")
		container.innerHTML = ""

		for key, value in result.win_rates.rates.items():
			new_line = document.createElement("p")
			new_line.innerHTML = f"{key} intact coins left: {value * 100:.3f}%"
			container.appendChild(new_line)

		container = document.querySelector("#lose-line-container")
		container.innerHTML = ""

		for key, value in dict(reversed(list(result.lose_rates.rates.items()))).items():
			new_line = document.createElement("p")
			new_line.innerHTML = f"{key} intact coins left: {value * 100:.3f}%"
			container.appendChild(new_line)

		document.querySelector("button").disabled = True
		document.querySelector(".all-result-container").style.opacity = 1

	except Exception as e:
		document.querySelector("clash").innerHTML = "Something went wrong! Are your inputs valid?"

@when("click", ".circle-container")
@when("input", "input")
def undisable_button(event=None):
	document.querySelector("button").disabled = False
	document.querySelector(".all-result-container").style.opacity = 0.5


@when("input", "#coin-count-1")
@when("input", "#coin-count-2")
def update_coins(event=None, id=None):
	try:
		if (id is None and event.target.id == "coin-count-1") or id == "coin-count-1":
			coin_count_input = min(max(int(document.querySelector("#coin-count-1").value), 1), 50)
			container = document.querySelector("#circle-container-1")
		else:
			coin_count_input = min(max(int(document.querySelector("#coin-count-2").value), 1), 50)
			container = document.querySelector("#circle-container-2")
		
		current_circles = container.querySelectorAll(".coin")
		current_count = len(current_circles)

		if coin_count_input > current_count:
			coins_to_add = coin_count_input - current_count
			for _ in range(coins_to_add):
				new_coin = document.createElement("img")
				new_coin.src = "normal_coin.webp"
				new_coin.className = "coin normal"
				container.appendChild(new_coin)

		elif coin_count_input < current_count:
			coins_to_remove = current_count - coin_count_input
			for _ in range(coins_to_remove):
				container.lastElementChild.remove()
	except:
		pass

@when("click", ".circle-container")
def toggle_circle_color(event):
	clicked_element = event.target
	
	if clicked_element.classList.contains("coin"):
		if clicked_element.classList.contains("normal"):
			clicked_element.src = "unbreakable_coin.webp"
			clicked_element.className = "coin red"
		else:
			clicked_element.src = "normal_coin.webp"
			clicked_element.className = "coin normal"

update_coins(id="coin-count-1")
update_coins(id="coin-count-2")
calculate_clash()
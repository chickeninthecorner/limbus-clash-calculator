from pyscript import when, document
from main import clash, Skill

@when("click", "#clash")
def update_all(event=None):
	base_power_1 = int(document.querySelector("#base-power-1").value)
	coin_power_1 = int(document.querySelector("#coin-power-1").value)
	coin_count_1 = int(document.querySelector("#coin-count-1").value)
	sanity_1 = int(document.querySelector("#sanity-1").value)
	paralysis_1 = int(document.querySelector("#paralysis-1").value)

	base_power_2 = int(document.querySelector("#base-power-2").value)
	coin_power_2 = int(document.querySelector("#coin-power-2").value)
	coin_count_2 = int(document.querySelector("#coin-count-2").value)
	sanity_2 = int(document.querySelector("#sanity-2").value)
	paralysis_2 = int(document.querySelector("#paralysis-2").value)

	skill1 = Skill(base_power_1, ('N') * coin_count_1, coin_power_1, sanity_1, paralysis_1)
	skill2 = Skill(base_power_2, ('N') * coin_count_2, coin_power_2, sanity_2, paralysis_2)

	try:
		result = clash(skill1, skill2, 0)
		
		document.querySelector("#overall-win-rate").innerHTML = f"{result.win_rates.overall_rate * 100:.2f}%"
		document.querySelector("#overall-tie-rate").innerHTML = f"{result.tie_rates.overall_rate * 100:.2f}%"
		document.querySelector("#overall-lose-rate").innerHTML = f"{result.lose_rates.overall_rate * 100:.2f}%"

	except Exception as e:
		print(e)

@when("input", "#coin-count-1")
@when("input", "#coin-count-2")
def update_coins(event=None, id=None):
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
			new_coin.className = "coin yellow"
			container.appendChild(new_coin)

	elif coin_count_input < current_count:
		coins_to_remove = current_count - coin_count_input
		for _ in range(coins_to_remove):
			container.lastElementChild.remove()

@when("click", ".circle-container")
def toggle_circle_color(event):
	clicked_element = event.target
	
	if clicked_element.classList.contains("coin"):
		if clicked_element.classList.contains("yellow"):
			clicked_element.src = "unbreakable_coin.webp"
			clicked_element.className = "coin red"
		else:
			clicked_element.src = "normal_coin.webp"
			clicked_element.className = "coin yellow"

update_coins(id="coin-count-1")
update_coins(id="coin-count-2")
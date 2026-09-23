// Expose the Emscripten Module object globally so the WebAssembly file can attach to it
window.Module = {
    onRuntimeInitialized: function() {
        console.log("C++ Engine Ready!");
    }
};


// Wait for the HTML to finish loading before trying to grab elements
document.addEventListener("DOMContentLoaded", () => {
    

    // --- Helper Functions ---
    function sumRates(ratesObj) {
        let sum = 0;
        for (let val of Object.values(ratesObj)) {
            sum += val;
        }
        return sum;
    }


    function isInputValid(selectorStr, min, max) {
        const el = document.querySelector(selectorStr);
        if (!el || el.value.trim() === "") return false;
        
        const num = parseInt(el.value, 10);
        if (isNaN(num)) return false;
        
        if (min !== null && min !== undefined && num < min) return false;
        if (max !== null && max !== undefined && num > max) return false;
        
        return true;
    }


    // --- UI Update Functions ---
    function undisableButton(event) {
        const inputsToCheck = [
            isInputValid("#base-power-1", 0, null),
            isInputValid("#coin-count-1", 1, 50),
            isInputValid("#sanity-1", -50, 50),
            isInputValid("#final-power-modifier-1", null, null),
            isInputValid("#paralysis-1", 0, null),
            isInputValid("#base-power-2", 0, null),
            isInputValid("#coin-count-2", 1, 50),
            isInputValid("#sanity-2", -50, 50),
            isInputValid("#paralysis-2", 0, null),
            isInputValid("#final-power-modifier-2", null, null)
        ];

        let resultContainer = document.querySelector(".all-result-container");
        if (resultContainer) resultContainer.style.opacity = "0.5";
        
        let button = document.querySelector("#clash"); 
        if (button) {
            if (inputsToCheck.includes(false)) {
                button.disabled = true;
            } else {
                button.disabled = false;
            }
        }
    }


    // Direct translation of `update_coins`
    function updateCoins(event, passedId) {
        try {
            let id = passedId || (event && event.target ? event.target.id : null);
            if (!id) return;
            
            let inputElement = document.querySelector("#" + id);

            if (isInputValid("#" + id, 1, 50))
            {
                let inputElement = document.querySelector("#" + id);
                let coin_count_input = parseInt(inputElement.value, 10);
                let container = document.querySelector(id === "coin-count-1" ? "#circle-container-1" : "#circle-container-2");
                
                let current_circles = container.querySelectorAll(".coin-button");
                let current_count = current_circles.length;

                if (coin_count_input > current_count) {
                    let coins_to_add = coin_count_input - current_count;
                    for (let i = 0; i < coins_to_add; i++) {
                        let new_coin = document.createElement("button");
                        new_coin.className = "coin-button normal";
                        new_coin.setAttribute("form", "")
                        new_coin.innerHTML = '<img src="normal_coin.webp"></img>';
                        new_coin.addEventListener("click", (e) => {
                            toggleCircleColor(e);
                            undisableButton(e); 
                        });
                        container.appendChild(new_coin);
                    }
                } else if (coin_count_input < current_count) {
                    let coins_to_remove = current_count - coin_count_input;
                    for (let i = 0; i < coins_to_remove; i++) {
                        if (container.lastElementChild) {
                            container.lastElementChild.remove();
                        }
                    }
                }
            }
        } catch (e) {
            // pass
        }
    }


    function toggleCircleColor(event) {
        let clicked_element = event.target;
        
        if (clicked_element.classList.contains("coin-button")) {
            if (clicked_element.classList.contains("normal")) {
                clicked_element.innerHTML = '<img src="unbreakable_coin.webp"></img>';
                clicked_element.className = "coin-button red";
            } else {
                clicked_element.innerHTML = '<img src="normal_coin.webp"></img>';
                clicked_element.className = "coin-button normal";
            }
        }
    }


    // --- Core Calculation ---
    function calculateClash(event) {
        if (event) event.preventDefault();

        try {
            document.querySelector(".all-result-container").style.opacity = "0.5";

            // Skill 1 inputs
            let base_power_1 = parseInt(document.querySelector("#base-power-1").value, 10);
            let coin_power_1 = parseInt(document.querySelector("#coin-power-1").value, 10);
            let sanity_1 = parseInt(document.querySelector("#sanity-1").value, 10);
            let paralysis_1 = parseInt(document.querySelector("#paralysis-1").value, 10);
            let final_power_modifier_1 = parseInt(document.querySelector("#final-power-modifier-1").value, 10);
            
            let coins_1_arr = [];
            document.querySelector("#circle-container-1").querySelectorAll(".coin-button").forEach(coin => {
                if (coin.classList.contains("normal")) coins_1_arr.push('N');
                else if (coin.classList.contains("red")) coins_1_arr.push('R');
            });
            let coins_1 = coins_1_arr.join(""); 

            // Skill 2 inputs
            let base_power_2 = parseInt(document.querySelector("#base-power-2").value, 10);
            let coin_power_2 = parseInt(document.querySelector("#coin-power-2").value, 10);
            let sanity_2 = parseInt(document.querySelector("#sanity-2").value, 10);
            let paralysis_2 = parseInt(document.querySelector("#paralysis-2").value, 10);
            let final_power_modifier_2 = parseInt(document.querySelector("#final-power-modifier-2").value, 10);
            
            let coins_2_arr = [];
            document.querySelector("#circle-container-2").querySelectorAll(".coin-button").forEach(coin => {
                if (coin.classList.contains("normal")) coins_2_arr.push('N');
                else if (coin.classList.contains("red")) coins_2_arr.push('R');
            });
            let coins_2 = coins_2_arr.join("");

            // Call the ultra-fast C++ WebAssembly module
            let jsonString = window.Module.clash(
                base_power_1, coins_1, coin_power_1, sanity_1, paralysis_1, final_power_modifier_1,
                base_power_2, coins_2, coin_power_2, sanity_2, paralysis_2, final_power_modifier_2,
                0 // Starting parry
            );

            // Parse the returned JSON string back into a JS Object
            let result = JSON.parse(jsonString);

            // Update Overall Rates
            document.querySelector("#win-rate").innerHTML = (sumRates(result.win_rates) * 100).toFixed(2) + "%";
            document.querySelector("#tie-rate").innerHTML = (sumRates(result.tie_rates) * 100).toFixed(2) + "%";
            document.querySelector("#lose-rate").innerHTML = (sumRates(result.lose_rates) * 100).toFixed(2) + "%";

            // Populate Win Lines
            let winContainer = document.querySelector("#win-line-container");
            winContainer.innerHTML = "";
            let winEntries = Object.entries(result.win_rates).reverse();
            for (let [key, value] of winEntries) {
                if (key === "overall") continue;
                let newLine = document.createElement("p");
                newLine.innerHTML = `${key} intact coins left: ${(value * 100).toFixed(3)}%`;
                winContainer.appendChild(newLine);
            }

            // Populate Lose Line
            let loseContainer = document.querySelector("#lose-line-container");
            loseContainer.innerHTML = "";
            let loseEntries = Object.entries(result.lose_rates).reverse();
            for (let [key, value] of loseEntries) {
                if (key === "overall") continue;
                let newLine = document.createElement("p");
                newLine.innerHTML = `${key} intact coins left: ${(value * 100).toFixed(3)}%`;
                loseContainer.appendChild(newLine);
            }

            // Disable button and reset opacity
            let btn = document.querySelector("#clash");
            btn.disabled = true;
            document.querySelector(".all-result-container").style.opacity = "1";

        } catch (e) {
            console.error(e);
            let btn = document.querySelector("#clash");
            btn.innerHTML = "Something went wrong! Are your inputs valid?";
        }
    }


    // --- Event Bindings --
    // 1. Clash Button
    let clashBtn = document.querySelector("#clash");
    if (clashBtn) clashBtn.addEventListener("click", calculateClash);

    // 2. Input validation
    document.querySelectorAll("input").forEach(input => {
        input.addEventListener("input", undisableButton);
    });

    // 3. Coin count specific updaters
    let cc1 = document.querySelector("#coin-count-1");
    if (cc1) cc1.addEventListener("input", (e) => updateCoins(e, "coin-count-1"));
    
    let cc2 = document.querySelector("#coin-count-2");
    if (cc2) cc2.addEventListener("input", (e) => updateCoins(e, "coin-count-2"));

    // 4. Clicking circles toggles color AND checks validation
    document.querySelectorAll(".coin-button").forEach(container => {
        container.addEventListener("click", (e) => {
            toggleCircleColor(e);
            undisableButton(e); 
        });
    });

    // 5. Run initial updates on page load to match Python script behavior
    updateCoins(null, "coin-count-1");
    updateCoins(null, "coin-count-2");
    undisableButton(); 
});
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <tuple>
#include <cmath>
#include <cstdlib>
#include <algorithm>
#include <sstream>
#include <emscripten/bind.h>

using namespace emscripten;

// --- Fast Math Caches ---
long long comb_cache[64][64] = {0};
bool comb_init = false;

void init_comb() {
    if (comb_init) return;
    for (int i = 0; i < 64; ++i) {
        comb_cache[i][0] = 1;
        for (int j = 1; j <= i; ++j) {
            comb_cache[i][j] = comb_cache[i-1][j-1] + comb_cache[i-1][j];
        }
    }
    comb_init = true;
}

// --- Memory-Optimized Structs ---
struct ClashRates {
    float rates[55] = {0.0f}; 

    void add_mul(const ClashRates& other, float multiplier) {
        for (int i = 0; i < 55; ++i) {
            rates[i] += other.rates[i] * multiplier;
        }
    }
};

struct ClashRatesTrio {
    ClashRates win;
    ClashRates tie;
    ClashRates lose;

    ClashRatesTrio reversed_rates() const {
        ClashRatesTrio res;
        res.win = lose;
        res.tie = tie;
        res.lose = win;
        return res;
    }
};

struct ParryOutcomes {
    float win = 0.0f;
    float tie = 0.0f;
    float lose = 0.0f;
};

// --- Custom Hashers ---
inline void hash_combine(std::size_t& seed, std::size_t hash) {
    seed ^= hash + 0x9e3779b9 + (seed << 6) + (seed >> 2);
}

struct IDState {
    int base, cp, sanity, p;
    char num_coins;
    char coins[55];

    IDState(int b, int c, int s, int p_, const std::string& str) {
        base = b; cp = c; sanity = s; p = p_;
        num_coins = std::min((int)str.length(), 55);
        for(int i = 0; i < num_coins; ++i) coins[i] = str[i];
    }

    bool operator==(const IDState& o) const {
        if (base != o.base || cp != o.cp || sanity != o.sanity || p != o.p || num_coins != o.num_coins) return false;
        for(int i = 0; i < num_coins; ++i) {
            if (coins[i] != o.coins[i]) return false;
        }
        return true;
    }
};

struct IDHash {
    std::size_t operator()(const IDState& t) const {
        std::size_t seed = 0;
        hash_combine(seed, std::hash<int>()(t.base));
        hash_combine(seed, std::hash<int>()(t.cp));
        hash_combine(seed, std::hash<int>()(t.sanity));
        hash_combine(seed, std::hash<int>()(t.p));
        
        std::size_t coin_hash = 0;
        for(int i = 0; i < t.num_coins; ++i) coin_hash = coin_hash * 31 + t.coins[i];
        hash_combine(seed, coin_hash);
        return seed;
    }
};

struct ParryKey {
    IDState s1, s2;
    bool operator==(const ParryKey& o) const { return s1 == o.s1 && s2 == o.s2; }
};

struct ParryKeyHash {
    std::size_t operator()(const ParryKey& k) const {
        std::size_t seed = 0;
        IDHash hasher;
        hash_combine(seed, hasher(k.s1));
        hash_combine(seed, hasher(k.s2));
        return seed;
    }
};

struct ClashKey {
    IDState s1, s2;
    int parry;
    bool operator==(const ClashKey& o) const { return s1 == o.s1 && s2 == o.s2 && parry == o.parry; }
};

struct ClashKeyHash {
    std::size_t operator()(const ClashKey& k) const {
        std::size_t seed = 0;
        IDHash hasher;
        hash_combine(seed, hasher(k.s1));
        hash_combine(seed, hasher(k.s2));
        hash_combine(seed, std::hash<int>()(k.parry));
        return seed;
    }
};

// --- Global Dicts ---
using ProbMap = std::unordered_map<int, float>;
std::unordered_map<IDState, ProbMap, IDHash> power_probabilities_dict;
std::unordered_map<ParryKey, ParryOutcomes, ParryKeyHash> outcome_probabilities_dict;
std::unordered_map<ClashKey, ClashRatesTrio, ClashKeyHash> clash_dict;

// --- Skill Class ---
class Skill {
public:
    int base_power;
    std::string coins;
    int coin_power;
    int sanity;
    int paralysis;
    int final_power_modifier;
    
    int intact_coin_count;
    int all_coin_count;

    Skill(int bp, const std::string& c, int cp, int s = 0, int p = 0, int fpm = 0)
        : base_power(bp), coins(c), coin_power(cp), sanity(s), paralysis(p), final_power_modifier(fpm) {
        
        intact_coin_count = 0;
        int c_count = 0;
        for (char ch : coins) {
            if (ch == 'N' || ch == 'R') intact_coin_count++;
            else if (ch == 'C') c_count++;
        }
        all_coin_count = intact_coin_count + c_count;
    }

    bool reducible() const {
        if (base_power > 0 && coin_power > 0) return true;
        if (paralysis > 0) return true;
        if (coins.find('C') != std::string::npos) return true;
        return false;
    }

    IDState dynamic_id() const {
        return IDState(base_power, coin_power, sanity, paralysis, coins);
    }

    IDState effective_rolling_id() const {
        std::string eff_coins = "";
        eff_coins.reserve(coins.size());
        for (char ch : coins) eff_coins += (ch == 'C') ? 'C' : 'N';
        return IDState(base_power, coin_power, sanity, std::min(paralysis, all_coin_count), eff_coins);
    }

    Skill lose_skill() const {
        std::string coins_after = coins;
        bool broken = false;
        
        for (int i = all_coin_count - 1; i > 0; --i) {
            if (coins_after[i] == 'N') {
                coins_after.erase(i, 1);
                broken = true; break;
            }
            if (coins_after[i] == 'R') {
                coins_after[i] = 'C';
                broken = true; break;
            }
        }
        if (!broken) coins_after = "";
        return Skill(base_power, coins_after, coin_power, sanity, std::max(paralysis - all_coin_count, 0), final_power_modifier);
    }

    Skill next_skill() const {
        return Skill(base_power, coins, coin_power, sanity, std::max(paralysis - all_coin_count, 0), final_power_modifier);
    }
};

// --- Core Logic ---
ProbMap get_combined_power_probabilities(const ProbMap& p1, const ProbMap& p2) {
    ProbMap result;
    for (const auto& kv1 : p1) {
        for (const auto& kv2 : p2) {
            int combined = std::max(kv1.first + kv2.first, 0);
            result[combined] += kv1.second * kv2.second;
        }
    }
    return result;
}

ProbMap get_power_probabilities(const Skill& skill);

ProbMap sum_reduced_rolling_components(const Skill& skill, bool) {
    int paralysis = skill.paralysis;
    int last_cp = 0;
    bool has_last = false;
    int consecutive = 0;

    ProbMap result = get_power_probabilities(Skill(skill.base_power, "N", 0, 0, 0));

    for (char coin : skill.coins) {
        int eff_cp = skill.coin_power;
        if (paralysis > 0) eff_cp = 0;
        else if (coin == 'C') eff_cp = (skill.coin_power == 0) ? 0 : (skill.coin_power / std::abs(skill.coin_power));

        if (!has_last) {
            last_cp = eff_cp; consecutive = 1; has_last = true;
        } else if (last_cp == eff_cp) {
            consecutive++;
        } else {
            result = get_combined_power_probabilities(
                result, get_power_probabilities(Skill(0, std::string(consecutive, 'N'), last_cp, skill.sanity, 0))
            );
            consecutive = 1; last_cp = eff_cp;
        }
        paralysis = std::max(paralysis - 1, 0);
    }

    if (has_last) {
        result = get_combined_power_probabilities(
            result, get_power_probabilities(Skill(0, std::string(consecutive, 'N'), last_cp, skill.sanity, 0))
        );
    }
    return result;
}

ProbMap get_power_probabilities(const Skill& skill) {
    IDState eff_id = skill.effective_rolling_id();
    auto it = power_probabilities_dict.find(eff_id);
    if (it != power_probabilities_dict.end()) return it->second;

    if (skill.reducible()) {
        ProbMap result = sum_reduced_rolling_components(skill);
        power_probabilities_dict[eff_id] = result;
        return result;
    }

    float heads_prob = skill.sanity / 100.0f + 0.5f;
    float tails_prob = 1.0f - heads_prob;
    ProbMap result;

    for (int head_count = 0; head_count <= skill.all_coin_count; ++head_count) {
        int tail_count = skill.all_coin_count - head_count;
        int power = std::max(skill.base_power + skill.coin_power * head_count, 0);
        
        float prob = std::pow(heads_prob, head_count) * 
                     std::pow(tails_prob, tail_count) * 
                     (float)comb_cache[skill.all_coin_count][head_count];
        result[power] += prob;
    }
    power_probabilities_dict[eff_id] = result;
    return result;
}

ParryOutcomes get_parry_outcome_probabilities(const Skill& skill1, const Skill& skill2) {
    ParryKey key = {skill1.effective_rolling_id(), skill2.effective_rolling_id()};
    auto it = outcome_probabilities_dict.find(key);
    if (it != outcome_probabilities_dict.end()) return it->second;

    ParryKey rev_key = {key.s2, key.s1};
    auto rev_it = outcome_probabilities_dict.find(rev_key);
    if (rev_it != outcome_probabilities_dict.end()) {
        return {rev_it->second.lose, rev_it->second.tie, rev_it->second.win};
    }

    // A hacky solution to add final power modifier last
    ProbMap FPM_1_PP = {{skill1.final_power_modifier, 1.0f}};
    ProbMap FPM_2_PP = {{skill2.final_power_modifier, 1.0f}};

    ProbMap p1 = get_combined_power_probabilities(
        get_power_probabilities(skill1), 
        FPM_1_PP
    );
    ProbMap p2 = get_combined_power_probabilities(
        get_power_probabilities(skill2), 
        FPM_2_PP
    );

    ParryOutcomes result;

    for (const auto& kv1 : p1) {
        for (const auto& kv2 : p2) {
            float prob = kv1.second * kv2.second;
            if (kv1.first > kv2.first) result.win += prob;
            else if (kv1.first < kv2.first) result.lose += prob;
            else result.tie += prob;
        }
    }
    outcome_probabilities_dict[key] = result;
    return result;
}

ClashRatesTrio core_clash(const Skill& skill1, const Skill& skill2, int parry) {
    ClashKey dynamic_key = {skill1.dynamic_id(), skill2.dynamic_id(), parry};

    auto it = clash_dict.find(dynamic_key);
    if (it != clash_dict.end()) return it->second;

    ClashKey reversed_key = {dynamic_key.s2, dynamic_key.s1, parry};
    auto rev_it = clash_dict.find(reversed_key);
    if (rev_it != clash_dict.end()) return rev_it->second.reversed_rates();

    ClashRatesTrio res;
    if (skill2.all_coin_count == 0) {
        if(skill1.intact_coin_count < 55) res.win.rates[skill1.intact_coin_count] = 1.0f;
        return res;
    } else if (skill1.all_coin_count == 0) {
        if(skill2.intact_coin_count < 55) res.lose.rates[skill2.intact_coin_count] = 1.0f;
        return res;
    } else if (std::min(skill1.intact_coin_count, skill2.intact_coin_count) > 99 - parry) {
        res.tie.rates[0] = 1.0f; // Index 0 represents "overall"
        return res;
    }

    ParryOutcomes parry_probs = get_parry_outcome_probabilities(skill1, skill2);

    if (parry_probs.win > 0.0f) {
        ClashRatesTrio w = core_clash(skill1.next_skill(), skill2.lose_skill(), parry + 1);
        res.win.add_mul(w.win, parry_probs.win);
        res.tie.add_mul(w.tie, parry_probs.win);
        res.lose.add_mul(w.lose, parry_probs.win);
    }
    if (parry_probs.tie > 0.0f) {
        ClashRatesTrio t = core_clash(skill1.next_skill(), skill2.next_skill(), parry + 1);
        res.win.add_mul(t.win, parry_probs.tie);
        res.tie.add_mul(t.tie, parry_probs.tie);
        res.lose.add_mul(t.lose, parry_probs.tie);
    }
    if (parry_probs.lose > 0.0f) {
        ClashRatesTrio l = core_clash(skill1.lose_skill(), skill2.next_skill(), parry + 1);
        res.win.add_mul(l.win, parry_probs.lose);
        res.tie.add_mul(l.tie, parry_probs.lose);
        res.lose.add_mul(l.lose, parry_probs.lose);
    }

    clash_dict[dynamic_key] = res;
    return res;
}

// --- The Javascript Binding Interface ---
std::string toJsonObj(const ClashRates& cr) {
    std::stringstream ss;
    ss << "{";
    bool first = true;
    for (int i = 0; i < 55; ++i) {
        if (cr.rates[i] > 0.0f) {
            if (!first) ss << ", ";
            if (i == 0) ss << "\"overall\": " << cr.rates[i];
            else ss << "\"" << i << "\": " << cr.rates[i];
            first = false;
        }
    }
    ss << "}";
    return ss.str();
}

std::string clash(
    int bp1, std::string c1, int cp1, int s1, int p1, int fpm1,
    int bp2, std::string c2, int cp2, int s2, int p2, int fpm2,
    int parry
) {
    init_comb();
    
    // Memory Swap Trick to keep Wasm RAM at absolute minimum
    if (parry == 0) {
        std::unordered_map<IDState, ProbMap, IDHash>().swap(power_probabilities_dict);
        std::unordered_map<ParryKey, ParryOutcomes, ParryKeyHash>().swap(outcome_probabilities_dict);
        std::unordered_map<ClashKey, ClashRatesTrio, ClashKeyHash>().swap(clash_dict);
    }
    
    Skill skill1(bp1, c1, cp1, s1, p1, fpm1);
    Skill skill2(bp2, c2, cp2, s2, p2, fpm2);
    
    ClashRatesTrio result = core_clash(skill1, skill2, parry);

    std::stringstream json;
    json << "{\"win_rates\": " << toJsonObj(result.win) 
         << ", \"tie_rates\": " << toJsonObj(result.tie) 
         << ", \"lose_rates\": " << toJsonObj(result.lose) << "}";
    
    return json.str();
}

EMSCRIPTEN_BINDINGS(my_module) {
    emscripten::function("clash", &clash);
}
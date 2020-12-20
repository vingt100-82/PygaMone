from typing import Dict, List, Tuple, Any, Optional, NoReturn, Union
from random import randint
import pokemon.pokemon as pokemon
import pokemon.ability as p_ability
import pokemon.abilitys_ as abilitys_
import item.items as items
import item.item as item
import item.pokeball as poke_item
import pokemon.status.pokemon_status as pokemon_status
import pokemon.status.pokemon_stats_modifier as psm
import random
import displayer
import pygame
import utils
import uuid


class PokemonAbility(object):

    def __init__(self, id_: str, pp: int, max_pp: int):
        self.id_: str = id_
        self.ability: 'p_ability.AbstractAbility' = abilitys_.ABILITYS[id_]
        self.pp: int = pp
        self.max_pp: int = max_pp

    def serialisation(self) -> Dict[str, Any]:
        return {
            "_id": self.id_,
            "pp": self.pp,
            "max_pp": self.max_pp,
        }

    @staticmethod
    def new_ability(_id: str) -> 'PokemonAbility':
        """

        :rtype: PokemonAbility
        """
        ab = abilitys_.ABILITYS[_id]
        return PokemonAbility(_id, ab.pp, ab.pp)

    @staticmethod
    def deserialisation(data: Dict[str, Any]) -> 'PokemonAbility':
        """

        :rtype: PokemonAbility
        """
        return PokemonAbility(
            data["_id"],
            data["pp"],
            data["max_pp"]
        )


C_S_CRITICAL = "C_S_CRITICAL"
C_S_ACCURACY = "C_S_ACCURACY"

NOT_CLASSIC = [C_S_CRITICAL, C_S_ACCURACY]


class PlayerPokemon(object):

    def __init__(self, _id: int, xp: int, ivs: Dict[str, int], heal: int,
                 ability: List[PokemonAbility], poke_ball: 'item.Item', shiny: bool, female: bool, status: list[str],
                 uuid_: Optional[uuid.UUID]):
        self.id_ = _id
        self.xp = xp
        self.poke = pokemon.get_pokemon(self.id_)
        self.lvl = self.get_lvl()
        self.ivs = ivs
        self.heal = heal
        self.shiny = shiny
        self.female = female
        self.uuid = uuid_ if uuid_ else uuid.uuid4()

        self.front_image = f'assets/textures/pokemon/{("shiny/" if shiny else "")}{("female/" if female and self.poke.have_female_image else "")}{(self.id_)}.png'
        self.back_image = f'assets/textures/pokemon/back/{("shiny/" if shiny else "")}{("female/" if female and self.poke.have_female_image else "")}{(self.id_)}.png'
        self.front_image_y = self.get_first_color(self.front_image)
        self.back_image_y = self.get_first_color(self.back_image)

        self.stats = {}
        #combat_stats
        self.combat_status: 'pokemon_status.PokeStatus' = pokemon_status.PokeStatus(self, status)
        self.pokemon_stats_modifier: 'psm.PokeStatsModifier' = psm.PokeStatsModifier(self)
        self.calculate_stats()
        self.ability: List[PokemonAbility] = ability

        self.poke_ball: 'poke_item.Pokeball' = poke_ball
        self.use = False
        self.ram_data = {}

        # heal check
        if self.heal == -1 or self.heal > self.get_max_heal():
            self.heal = self.get_max_heal()

    def can_evolve(self) -> Optional[int]:
        li = self.poke.get_evolution_under(self.lvl)
        if len(li) > 0:
            return li[0]
        return None

    def get_stats(self, name: str, with_edit: bool = True):
        v = self.stats[name] if name in self.stats else 1
        if with_edit:
            b = 3 if v in NOT_CLASSIC else 2
            l = self.pokemon_stats_modifier.get(name)
            v *= (b if l <= 0 else (b + l)) // (b if l >= 0 else (b + abs(l)))
            print("stats debug", name, b,  l, v)
        return v

    def set_use(self, value: bool):
        self.use = value

    def get_first_color(self, path):
        poke = displayer.get_poke(path)

        for y in range(poke.get_size()[1] - 1, -1, -1):
            for x in range(0, poke.get_size()[1]):
                if poke.get_at((x, y))[3] != 0:
                    return y
        return 0

    def get_front_image(self, scale=1) -> pygame.Surface:
        return displayer.get_poke(self.front_image, scale)

    def get_front_image_colored(self, color: Union[tuple[int, int, int], tuple[int, int, int, int]], scale=1) -> pygame.Surface:
        surface = displayer.get_poke(self.front_image, 1).copy()
        utils.color_image(surface, color)
        size = surface.get_size()
        if scale != 1:
            surface = pygame.transform.scale(surface, (int(size[0] * scale), int(size[1] * scale)))
        return surface

    def get_back_image_colored(self, color: Union[tuple[int, int, int], tuple[int, int, int, int]], scale=1) -> pygame.Surface:
        surface = displayer.get_poke(self.back_image, 1).copy()
        utils.color_image(surface, color)
        size = surface.get_size()
        if scale != 1:
            surface = pygame.transform.scale(surface, (int(size[0] * scale), int(size[1] * scale)))
        return surface

    def get_back_image(self, scale=1) -> pygame.Surface:
        return displayer.get_poke(self.back_image, scale)

    def reset_combat_status(self):
        self.ram_data = {}
        self.pokemon_stats_modifier.reset()
        self.combat_status.reset()

    def ge_rdm_ability(self) -> Optional['p_ability.AbstractAbility']:
        le = len(self.ability)
        if le == 0:
            return None
        if le == 1:
            return self.ability[0].ability
        return self.ability[random.randint(0, le - 1)].ability

    def get_ability(self, slot: int) -> Optional[PokemonAbility]:
        if slot < 0 or slot > 4:
            raise ValueError("Slot need be in [0:4]")
        if len(self.ability) - 1 >= slot:
            return self.ability[slot]
        return None

    def get_max_heal(self) -> int:
        return self.get_stats(pokemon.HEAL, False)

    def calculate_stats(self) -> NoReturn:
        for st in pokemon.STATS:
            self.stats[st] = calculate_stats(self.lvl, self.poke.base_stats[st], self.ivs[st], st == pokemon.STATS[0])

    def get_lvl(self) -> int:
        return self.poke.get_lvl(self.xp)

    def current_xp_status(self) -> Tuple[int, int]:
        if self.lvl < 100:
            this_l = self.poke.get_xp(self.lvl)
            return self.xp - this_l, self.poke.get_xp(self.lvl + 1) - this_l
        else:
            return 0, 0

    def add_ability(self, slot: int, ability_name: str) -> NoReturn:
        if slot < 0 or slot > 4:
            raise ValueError("Slot need be in [0:4]")
        if len(self.ability) >= 4:
            self.ability[slot] = PokemonAbility.new_ability(ability_name)
        else:
            self.ability.append(PokemonAbility.new_ability(ability_name))

    def get_name(self, upper_first=False) -> str:
        return self.poke.get_name(upper_first)

    def add_xp(self, amount: int) -> Tuple[bool, int, int]:
        if amount < 0:
            raise ValueError("negative xp amount")
        if self.lvl == 100:
            return False, 100, 100
        self.xp += amount
        n = self.get_lvl()
        if (old := self.lvl) != n:
            self.lvl = n
            self.calculate_stats()
            return True, old, self.lvl
        return False, n, n

    def __eq__(self, other):
        if isinstance(other, PlayerPokemon):
            return self.uuid == other.uuid
        return NotImplemented

    def serialisation(self) -> Dict[str, Any]:
        return {
            "_id": self.id_,
            "xp": self.xp,
            "ivs": ivs_to_int(self.ivs),
            "heal": self.heal,
            "ability": [a.serialisation() for a in self.ability],
            "pokeball": self.poke_ball.identifier,
            "shiny": self.shiny,
            "female": self.female,
            "status": self.combat_status.get_save(),
            "uuid": str(self.uuid)
        }

    @staticmethod
    def create_pokemon(_id: int, lvl: int, poke_ball: 'item.Item' = items.POKE_BALL):
        poke = pokemon.get_pokemon(_id)
        xp = poke.get_xp(lvl)
        ivs = random_ivs()
        # shiny = random.randint(0, 9191) == 0
        shiny = random.random() <= 0.0001220703125
        female = random.random() <= poke.female_rate
        ability = poke.get_4_last_ability(lvl)
        _ability = []
        for i in range(min(len(ability), 4)):
            _ability.append(PokemonAbility.new_ability(ability[i]))
        return PlayerPokemon(_id, xp, ivs, -1, _ability, poke_ball, shiny, female, [], None)
        pass

    @staticmethod
    def from_json(data) -> 'PlayerPokemon':
        return PlayerPokemon(data["_id"], data["xp"],
                             ivs_from_int(data["ivs"]), data["heal"],
                             [PokemonAbility.deserialisation(a) for a in data["ability"]],
                             items.ITEMS[data["pokeball"]],
                             data["shiny"],
                             data["female"],
                             data["status"],
                             uuid.UUID(data["uuid"]) if "uuid" in data else uuid.uuid4()
                             )


class PCPlayerPokemon(PlayerPokemon):

    def __init__(self, _id: int, xp: int, ivs: Dict[str, int], heal: int,
                 ability: List[PokemonAbility], poke_ball: 'item.Item', box: int, case: int):
        super().__init__(_id, xp, ivs, heal, ability, poke_ball)
        self.box: int = box
        self.case: int = case

    def to_none_pc(self) -> PlayerPokemon:
        return PlayerPokemon(self.id_, self.xp, self.ivs, self.heal, self.ability, self.poke_ball)

    def serialisation(self) -> Dict[str, Any]:
        su = super().serialisation()
        su["case"] = self.case
        su["box"] = self.box
        return su

    @staticmethod
    def from_none_pc(poke: PlayerPokemon, box: int, case: int):
        return PCPlayerPokemon(poke.id_, poke.xp, poke.ivs, poke.heal, poke.ability, poke.poke_ball, box, case)

    @staticmethod
    def from_json(data) -> 'PCPlayerPokemon':
        return PCPlayerPokemon(data["_id"], data["xp"],
                             ivs_from_int(data["ivs"]), data["heal"],
                             [PokemonAbility.deserialisation(a) for a in data["ability"]],
                             items.ITEMS[data["pokeball"]]
                             )

# IVS =
# 0000-0000-0000-0000-0000-0000-0000-0000
#                     ATTA/DEF/SPEED/SPECIAL



def calculate_stats(level: int, base: int, iv: int, is_hp: bool) -> int:
    n = ((((base + iv) * 2) * level) / 100) + 10
    if is_hp:
        n += level
    return int(n)


def ivs_from_int(ivs: int) -> Dict[str, int]:
    back = {
        pokemon.STATS[1]: (ivs & (0b1111 << 12)) >> 12,
        pokemon.STATS[2]: (ivs & (0b1111 << 8)) >> 8,
        pokemon.STATS[3]: (ivs & (0b1111 << 4)) >> 4,
        pokemon.STATS[4]: ivs & 0b1111,
        pokemon.STATS[5]: ivs & 0b1111,
        pokemon.STATS[0]: ((((ivs & (0b1111 << 12)) >> 12) & 0b1) << 3) +
                          ((((ivs & (0b1111 << 8)) >> 8) & 0b1) << 2) +
                          ((((ivs & (0b1111 << 4)) >> 4) & 0b1) << 1) +
                          ((ivs & 0b1111) & 0b1)
    }
    return back


def random_ivs() -> Dict[str, int]:
    return ivs_from_int((randint(0, 15) << 12) + (randint(0, 15) << 8) + (randint(0, 15) << 4) + randint(0, 15))


def ivs_to_int(ivs_dic: dict) -> int:
    return (ivs_dic[pokemon.STATS[1]] << 12) +\
           (ivs_dic[pokemon.STATS[2]] << 8) +\
           (ivs_dic[pokemon.STATS[3]] << 4) +\
           ivs_dic[pokemon.STATS[4]]

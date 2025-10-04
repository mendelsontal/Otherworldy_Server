from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password_hash = Column(String)
    characters = relationship("Character", back_populates="user")


class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    title = Column(String, default="Human")
    gold = Column(Integer, default=0)
    x = Column(Integer, default=100)
    y = Column(Integer, default=100)
    map_id = Column(Integer, default=100001)
    level = Column(Integer, default=0)
    exp = Column(Integer, default=0)
    appearance = Column(JSON, default=lambda: {})
    gear = Column(JSON, default=lambda: {})

    # Base stats
    hp = Column(Integer, default=50)
    mp = Column(Integer, default=0)
    str = Column(Integer, default=0)
    int = Column(Integer, default=0)
    dex = Column(Integer, default=0)
    vit = Column(Integer, default=0)
    agi = Column(Integer, default=0)
    end = Column(Integer, default=0)

    user = relationship("User", back_populates="characters")

    # Derived / enforced limits
    BASE_SPD = 1
    MAX_SPD = 10
    BASE_JMP = 1
    MAX_JMP = 15
    BASE_ATT = 1
    MAX_ATT = 1000
    BASE_ATT_SPD = 1
    MAX_ATT_SPD = 100
    BASE_HP = 50
    MAX_HP = 1000
    BASE_MP = 0
    MAX_MP = 1000
    BASE_DEF = 0
    MAX_DEF = 1000
    BASE_GRAVITY = 0.6
    MIN_GRAVITY = 0.1
    MAX_GRAVITY = 1.2

    # -------------------------
    # Derived stats calculation
    # -------------------------
    def calculate_derived_stats(self) -> dict:
        # Gear multipliers
        spd_mult = 1.0
        jmp_mult = 1.0
        hp_mult = 1.0
        att_spd_mult = 1.0
        def_bonus = 0
        mp_bonus = 0
        att_bonus = 0
        gravity_bonus = 0.0

        if self.gear:
            for item in self.gear.values():
                if not item:
                    continue
                spd_mult += item.get("spd", 0) / 100
                jmp_mult += item.get("jmp", 0) / 100
                hp_mult += item.get("hp", 0) / 100
                att_spd_mult += item.get("att_spd", 0) / 100
                def_bonus += item.get("def", 0)
                mp_bonus += item.get("mp", 0)
                att_bonus += item.get("att", 0)
                gravity_bonus += item.get("gravity", 0)

        # Base calculations
        base_spd = self.BASE_SPD + self.agi * 0.05
        base_jmp = self.BASE_JMP + self.dex * 0.05
        base_att = self.BASE_ATT + (self.dex + self.agi + self.str) * 0.05
        base_att_spd = self.BASE_ATT_SPD + self.str * 0.05
        base_hp = self.BASE_HP + self.vit * 0.05
        base_mp = self.BASE_MP + self.int * 0.05
        base_def = self.BASE_DEF + self.end * 0.05
        base_gravity = self.BASE_GRAVITY

        # Apply modifiers and clamp
        derived = {
            "SPD": min(round(base_spd * spd_mult,2), self.MAX_SPD),
            "JMP": min(round(base_jmp * jmp_mult,2), self.MAX_JMP),
            "ATT": min(round(base_att + att_bonus,2), self.MAX_ATT),
            "ATT_SPD": min(round(base_att_spd * att_spd_mult, 2), self.MAX_ATT_SPD),
            "HP": min(round(base_hp * hp_mult,2), self.MAX_HP),
            "MP": min(round(base_mp + mp_bonus,2), self.MAX_MP),
            "DEF": min(round(base_def + def_bonus,2), self.MAX_DEF),
            "GRAVITY": max(self.MIN_GRAVITY, min(base_gravity + gravity_bonus, self.MAX_GRAVITY))
        }

        # -------------------------
        # Attack range calculation
        # -------------------------
        # Base ATT and DEX
        base_att = derived["ATT"]
        dex_factor = self.dex
        # Add min/max attack
        spread = 0.3 / (1 + 0.05 * dex_factor) # 0.3 is max 30% spread for low DEX
        ATT_MIN = max(base_att * (1 - spread), 0)
        ATT_MAX = base_att * (1 + spread)

        # Add to derived stats
        derived["ATT_MIN"] = round(ATT_MIN, 2)
        derived["ATT_MAX"] = round(ATT_MAX, 2)

        return derived

    # -------------------------
    # Convert character to dict for client
    # -------------------------
    def as_dict(self) -> dict:
        derived = self.calculate_derived_stats()
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "map_id": self.map_id,
            "appearance": self.appearance,
            "stats": {
                "Level": self.level,
                "Exp": self.exp,
                "HP": derived["HP"],
                "MP": derived["MP"],
                "STR": self.str,
                "DEX": self.dex,
                "AGI": self.agi,
                "VIT": self.vit,
                "INT": self.int,
                "END": self.end,
                "ATT": derived["ATT"],
                "ATT_MIN": derived["ATT_MIN"],
                "ATT_MAX": derived["ATT_MAX"],
                "ATT_SPD": derived["ATT_SPD"],
                "SPD": derived["SPD"],
                "JMP": derived["JMP"],
                "DEF": derived["DEF"],
                "GRAVITY": derived["GRAVITY"],
                "GOLD": self.gold
            }
        }


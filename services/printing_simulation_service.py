
from dataclasses import dataclass
import math


MATERIALS = {
    "PLA": {
        "temperature": (190, 230, 210, 5),
        "speed": (30, 150, 60, 5),
        "layer": (0.10, 0.30, 0.20, 0.05),
        "base": (0.06, 0.03),
    },
    "PETG": {
        "temperature": (220, 250, 235, 5),
        "speed": (25, 120, 55, 5),
        "layer": (0.10, 0.30, 0.20, 0.05),
        "base": (0.09, 0.04),
    },
    "ABS": {
        "temperature": (230, 260, 245, 5),
        "speed": (25, 110, 50, 5),
        "layer": (0.10, 0.30, 0.20, 0.05),
        "base": (0.16, 0.05),
    },
}


@dataclass(frozen=True)
class PrintingSettings:
    material: str = "PLA"
    temperature: float = 210.0
    print_speed: float = 60.0
    layer_height: float = 0.20


class PrintingSimulationService:
    CUBE_HEIGHT_MM = 20.0

    def __init__(self, settings: PrintingSettings):
        self.settings = settings
        self._validate()

    def _validate(self):
        s = self.settings

        if s.material not in MATERIALS:
            raise ValueError("Unbekanntes Druckmaterial.")

        material = MATERIALS[s.material]

        for value, key in (
            (s.temperature, "temperature"),
            (s.print_speed, "speed"),
            (s.layer_height, "layer"),
        ):
            minimum, maximum, _, _ = material[key]

            if not math.isfinite(value) or not minimum <= value <= maximum:
                raise ValueError(
                    f"Ungültiger Wert für {key}: "
                    f"{minimum} bis {maximum}."
                )

    def calculate_defects(self):
        s = self.settings
        material = MATERIALS[s.material]

        tlo, thi, _, _ = material["temperature"]
        slo, shi, _, _ = material["speed"]
        llo, lhi, _, _ = material["layer"]

        tn = (s.temperature - tlo) / (thi - tlo)
        sn = (s.print_speed - slo) / (shi - slo)
        ln = (s.layer_height - llo) / (lhi - llo)

        base_warp, base_shift = material["base"]

        warping = (
            base_warp
            + 0.27 * tn
            + 0.10 * ln
            + 0.10 * tn * ln
        )

        shifting = (
            base_shift
            + 0.42 * sn
            + 0.12 * ln
            + 0.08 * sn * ln
        )

        return {
            "warping_mm": round(warping, 4),
            "layer_shifting_mm": round(shifting, 4),
        }

    def calculate_quality(self, defects):
        warping_penalty = defects["warping_mm"] / 0.85 * 45.0
        shifting_penalty = defects["layer_shifting_mm"] / 0.77 * 45.0

        quality = max(
            0.0,
            100.0 - warping_penalty - shifting_penalty,
        )

        return round(quality, 2)

    def run(self):
        defects = self.calculate_defects()

        layer_count = math.ceil(
            self.CUBE_HEIGHT_MM / self.settings.layer_height
        )

        return {
            "material": self.settings.material,
            "temperature": self.settings.temperature,
            "print_speed": self.settings.print_speed,
            "layer_height": self.settings.layer_height,
            "layer_count": layer_count,
            "warping_mm": defects["warping_mm"],
            "layer_shifting_mm": defects["layer_shifting_mm"],
            "quality_score": self.calculate_quality(defects),
        }

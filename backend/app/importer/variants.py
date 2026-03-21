from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional

from app.models.block_exercise_raw import BlockExerciseRaw
from app.models.block_item_canonical import BlockItemCanonical
from app.models.session_block import SessionBlock

EXTERNAL_REFERENCE_KEYWORDS = [
    "truecoach",
    "ver datos",
    "datos completos",
    "consulta allí",
    "link externo",
]


class VariantAdapter(ABC):
    """Adaptador base que transforma bloques en modelos canónicos."""

    name: str
    content_mode: str
    default_confidence: int

    def matches(self, blocks: Iterable[Dict[str, Any]]) -> bool:
        raise NotImplementedError

    def build_block(self, block_payload: Dict[str, Any], block_order: int) -> SessionBlock:
        raw_text = self.build_raw_text(block_payload)
        coach_notes = block_payload.get("coach_notes") or block_payload.get("notes")
        has_ext, ext_text = self.inspect_external_reference(raw_text, coach_notes)

        block = SessionBlock(
            block_order=block_order,
            original_block_id=str(block_payload.get("id") or block_payload.get("block_id") or ""),
            title=block_payload.get("title") or block_payload.get("name"),
            type=block_payload.get("type") or block_payload.get("category"),
            is_optional=bool(block_payload.get("optional") or block_payload.get("is_optional")),
            content_mode=self.content_mode,
            raw_text=raw_text,
            coach_notes=coach_notes,
            has_external_reference=has_ext,
            external_reference_text=ext_text,
            parsed_confidence=self.default_confidence,
        )

        self.attach_exercises(block, block_payload)
        return block

    def inspect_external_reference(self, *texts: Optional[str]) -> tuple[bool, Optional[str]]:
        aggregate = " ".join(filter(None, (text.lower() for text in texts if text)))
        if not aggregate:
            return False, None
        hits = [keyword for keyword in EXTERNAL_REFERENCE_KEYWORDS if keyword in aggregate]
        return bool(hits), aggregate if hits else None

    def attach_exercises(self, block: SessionBlock, block_payload: Dict[str, Any]) -> None:
        exercises = block_payload.get("exercises") or []
        for exercise in exercises:
            raw_ex = BlockExerciseRaw(
                name=exercise.get("name"),
                format=exercise.get("format") or exercise.get("type"),
                notes=exercise.get("notes") or exercise.get("description"),
                raw_payload=exercise,
            )
            block.exercises_raw.append(raw_ex)
            canonical = self.canonical_from_exercise(exercise)
            if canonical:
                block.items_canonical.append(canonical)

        if not exercises:
            fallback = self.canonical_from_block(block, block_payload)
            if fallback:
                block.items_canonical.append(fallback)

    def canonical_from_exercise(self, exercise: Dict[str, Any]) -> Optional[BlockItemCanonical]:
        text = exercise.get("notes") or exercise.get("description") or exercise.get("name")
        return BlockItemCanonical(
            movement_name=exercise.get("name"),
            movement_family=exercise.get("family") or exercise.get("category"),
            pattern_primary=exercise.get("pattern"),
            pattern_secondary=exercise.get("pattern_secondary"),
            modality=exercise.get("modality"),
            sets=exercise.get("sets"),
            reps=exercise.get("reps"),
            intensity_type=exercise.get("intensity_type"),
            intensity_value_json=exercise.get("intensity") if isinstance(exercise.get("intensity"), dict) else None,
            execution_notes=exercise.get("notes") or exercise.get("description"),
            raw_origin_text=text,
        )

    def canonical_from_block(
        self, block: SessionBlock, payload: Dict[str, Any]
    ) -> Optional[BlockItemCanonical]:
        raw_text = block.raw_text or payload.get("description")
        if not raw_text:
            return None
        return BlockItemCanonical(
            movement_name=payload.get("title") or payload.get("name"),
            movement_family=payload.get("family"),
            pattern_primary=payload.get("pattern"),
            modality=payload.get("modality"),
            execution_notes=block.coach_notes,
            raw_origin_text=raw_text,
        )

    @abstractmethod
    def build_raw_text(self, payload: Dict[str, Any]) -> Optional[str]:
        ...


class OctoberAdapter(VariantAdapter):
    name = "october"
    content_mode = "exercise_notes"
    default_confidence = 80

    def matches(self, blocks: Iterable[Dict[str, Any]]) -> bool:
        return any(block.get("exercises") for block in blocks)

    def build_raw_text(self, payload: Dict[str, Any]) -> Optional[str]:
        notes = payload.get("notes")
        exercises = payload.get("exercises") or []
        if notes:
            return notes
        if exercises:
            phrases = []
            for exercise in exercises:
                detail = exercise.get("notes") or exercise.get("description")
                if detail:
                    phrases.append(detail)
            return "\n".join(phrases) if phrases else None
        return None


class NovDecAdapter(VariantAdapter):
    name = "novdec"
    content_mode = "prescription"
    default_confidence = 60

    def matches(self, blocks: Iterable[Dict[str, Any]]) -> bool:
        return any(block.get("prescription") or block.get("coach_notes") for block in blocks)

    def build_raw_text(self, payload: Dict[str, Any]) -> Optional[str]:
        text = payload.get("prescription")
        if text:
            return text
        return payload.get("notes") or payload.get("description")

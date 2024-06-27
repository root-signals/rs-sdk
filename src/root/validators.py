from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from root.generated.openapi_client.models.skill_validator_request import SkillValidatorRequest

if TYPE_CHECKING:
    from .skills import ModelName, Skills


class Validator:
    def __init__(
        self,
        *,
        evaluator_id: Optional[str] = None,
        evaluator_name: Optional[str] = None,
        prompt: Optional[str] = None,
        model: Optional[ModelName] = None,
        threshold: float = 0.0,
    ):
        """Validator describes a single Evaluator and an optional guard value (threshold) used within an Objective

        Note that at most one of evaluator_id and evaluator_name must be provided.

        Args:

          evaluator_id: Skill ID of the evaluator to be used within
            the validator. It must have is_evaluator=True.

          evaluator_name: Name of the evaluator to be used within the validator.


          prompt: Prompt to be used. This is only used if
            evaluator_id/evaluator_name are not supplied.

          model: Model to be used with the prompt. This is only used if
            evaluator_id/evaluator_name are not supplied.

          threshold: The result from the evaluator below which the
            validator will fail. If threshold is 0.0, the Validator
            instance does not validate the results, only providing the
            evaluator values for later study.
        """
        if evaluator_id:
            if evaluator_name or prompt:
                raise ValueError("If evaluator_id is specified, evaluator_name and prompt are not used")
        elif not evaluator_name:
            raise ValueError("evaluator_id or evaluator_name must be provided")
        if prompt is None and model is not None:
            raise ValueError("Model can be only provided alongside prompt")
        self.evaluator_id = evaluator_id
        self.evaluator_name = evaluator_name
        self.model = model
        self.prompt = prompt
        self.threshold = threshold

    def _to_request(self, skills: Skills) -> SkillValidatorRequest:
        if not self.evaluator_id:
            # Iterate through existing skills with matching evaluator_name and that are accessible to the user
            for skill in skills.list(self.prompt, name=self.evaluator_name, only_evaluators=True):
                if self.prompt is not None and self.prompt != skill.prompt:
                    continue
                self.evaluator_id = skill.id
                break
            else:
                # Implicitly create the evaluator
                self.evaluator_id = skills.create(
                    self.prompt or "", model=self.model, name=self.evaluator_name, is_evaluator=True
                ).id
        return SkillValidatorRequest(
            evaluator_id=self.evaluator_id, evaluator_name=self.evaluator_name, threshold=self.threshold
        )


# TODO: Deprecate later, drop in 1.0
def PredicateValidator(evaluator_id: str, threshold: float) -> Validator:  # noqa: N802
    """Deprecated name for Validator; please use Validator."""
    return Validator(evaluator_id=evaluator_id, threshold=threshold)

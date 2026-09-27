"""Official per-entity macro F0.5 (P2-003/004). Single verified implementation — every
score in this project must go through this function, never a re-derivation.

F0.5 = (1.25 * P * R) / (0.25 * P + R), per Source-1 entity, then macro-averaged
(arithmetic mean) across all entities including singletons.

Convention (from the official worked example / singleton rule, problem statement p.4/p.6):
  - true=empty, pred=empty  -> F0.5 = 1.0  (correct singleton)
  - true=empty, pred=nonempty -> F0.5 = 0.0 (false merge on a true singleton)
  - true=nonempty, pred=empty -> F0.5 = 0.0 (total miss, precision undefined -> 0 contribution)
  - true=nonempty, pred=nonempty, no overlap -> F0.5 = 0.0
"""
from __future__ import annotations

from typing import Iterable


def entity_f05(true_ids: set, pred_ids: set) -> float:
    """F0.5 for one Source-1 entity. true_ids/pred_ids: sets of matched S2-/S3- id strings
    (empty set = singleton, i.e. no match)."""
    if not true_ids and not pred_ids:
        return 1.0
    if not pred_ids or not true_ids:
        return 0.0
    tp = len(true_ids & pred_ids)
    if tp == 0:
        return 0.0
    precision = tp / len(pred_ids)
    recall = tp / len(true_ids)
    beta2 = 0.25  # beta=0.5 -> beta^2=0.25
    denom = beta2 * precision + recall
    if denom == 0:
        return 0.0
    return (1 + beta2) * precision * recall / denom


def macro_f05(true_map: dict, pred_map: dict) -> float:
    """true_map/pred_map: {source1_entity_id: set(matched ids)}. Every key in true_map must
    be scored (missing from pred_map counts as an empty prediction, per output-completeness
    rule); a key in pred_map absent from true_map is ignored here (that is a submission-
    format violation, checked separately by validate_submission.py)."""
    if not true_map:
        return float("nan")
    total = 0.0
    for s1_id, true_ids in true_map.items():
        pred_ids = pred_map.get(s1_id, set())
        total += entity_f05(true_ids, pred_ids)
    return total / len(true_map)


def _self_check():
    """Hand-verified cases (P2-004): official worked example + edge cases."""
    # Official worked example: P=2/3, R=1.0 -> F0.5 = 0.714 (true has 2 ids, pred has 3,
    # both true ids are among the 3 predicted -> tp=2, P=2/3, R=2/2=1.0)
    f = entity_f05({"S2-1", "S2-2"}, {"S2-1", "S2-2", "S3-9"})
    assert abs(f - 0.7142857142857143) < 1e-9, f
    assert entity_f05(set(), set()) == 1.0                     # correct singleton
    assert entity_f05(set(), {"S2-1"}) == 0.0                  # false merge on singleton
    assert entity_f05({"S2-1"}, set()) == 0.0                  # total miss
    assert entity_f05({"S2-1"}, {"S2-1"}) == 1.0               # perfect
    assert entity_f05({"S2-1", "S2-2"}, {"S2-1"}) == pytestish(0.25, 1.0)  # partial: P=1,R=0.5
    assert macro_f05({"a": set(), "b": {"S2-1"}}, {"a": set(), "b": {"S2-1"}}) == 1.0
    print("f05_metric self-check OK")


def pytestish(beta2, p_times_something):
    # helper only for the partial-overlap hand check below (P=1.0, R=0.5)
    p, r = 1.0, 0.5
    return (1 + beta2) * p * r / (beta2 * p + r)


if __name__ == "__main__":
    _self_check()

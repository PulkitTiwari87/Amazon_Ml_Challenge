"""Text normalisation and heuristic noise / script flags used by the Phase 1 census.

These are CENSUS heuristics (regexes that count how often a pattern appears). They are not
a matching normaliser and make no claim about being the final preprocessing (Phase 5).
All functions take and return pandas Series so they run vectorised over chunks.
"""
import re
import unicodedata
import warnings

import numpy as np
import pandas as pd

# Punctuation/symbol chars -> space, except apostrophes and '.' which are deleted so that
# "Pvt." == "Pvt" and "Orelee's" -> "orelees". Combining marks (Devanagari matras) are kept.
_DELETE = set("'’`.")
_TABLE = None


def _table():
    global _TABLE
    if _TABLE is None:
        t = {}
        for cp in range(0x3000):  # covers Latin, Indic, punctuation blocks
            ch = chr(cp)
            if ch in _DELETE:
                t[cp] = None
            elif unicodedata.category(ch)[0] in "PS":
                t[cp] = " "
        _TABLE = t
    return _TABLE


def norm(s: pd.Series) -> pd.Series:
    """NFKC, casefold, '&'->' and ', drop punctuation, collapse whitespace."""
    out = (s.str.normalize("NFKC").str.casefold().str.replace("&", " and ", regex=False)
           .str.translate(_table()).str.replace(r"\s+", " ", regex=True).str.strip())
    return out


# abbreviation -> canonical long form (English/US/India/France census only)
CANON = {
    "corp": "corporation", "inc": "incorporated", "ltd": "limited", "pvt": "private",
    "co": "company", "rd": "road", "st": "street", "ave": "avenue", "blvd": "boulevard",
    "dr": "drive", "ln": "lane", "hwy": "highway", "ste": "suite", "apt": "apartment",
    "nr": "near", "opp": "opposite", "r": "rue", "av": "avenue", "bd": "boulevard",
}


def canon_tokens(normed: str):
    return [CANON.get(t, t) for t in normed.split()]


NAME_FLAGS = {
    "legal_abbr": r"\b(?:corp|inc|ltd|pvt|co|llc|llp|pty|plc|sarl|sas|sa|gmbh)\b",
    "legal_full": r"\b(?:corporation|incorporated|limited|private|company|partnership)\b",
    "has_ampersand": r"&",
    "has_and_word": r"\band\b",
    "dba_marker": r"\b(?:dba|d/b/a|t/a|trading as|a\.?k\.?a)\b",
    "leading_junk": r"^[^\w]",
    "has_digit": r"\d",
    "repeated_char4": r"(.)\1{3,}",
    "double_space": r"\s{2,}",
    "paren": r"[()\[\]]",
}
ADDR_FLAGS = {
    "abbr_street": r"\b(?:rd|st|ave|blvd|dr|ln|hwy|ste|apt|nr|opp)\b",
    "full_street": r"\b(?:road|street|avenue|boulevard|drive|lane|highway|suite)\b",
    "landmark": r"\b(?:near|opp|opposite|behind|beside|next to|adjacent|landmark)\b",
    "pin6": r"\b\d{6}\b",
    "zip5": r"\b\d{5}(?:-\d{4})?\b",
    "has_digit": r"\d",
    "double_space": r"\s{2,}",
    "fr_street_word": r"\b(?:rue|avenue|boulevard|chemin|place|impasse|allée|allee)\b",
    "fr_street_abbr": r"\b(?:r|av|bd|ch|pl|imp)\.?\s",
}
_NAME_RX = {k: re.compile(v, re.IGNORECASE) for k, v in NAME_FLAGS.items()}
_ADDR_RX = {k: re.compile(v, re.IGNORECASE) for k, v in ADDR_FLAGS.items()}

SCRIPT_RX = {
    "nonascii": r"[^\x00-\x7f]",
    "latin_ext": r"[À-ɏḀ-ỿ]",
    "devanagari": r"[ऀ-ॿ]",
    "other_indic": r"[ঀ-෿]",
    "cjk": r"[぀-ヿ㐀-鿿가-힯]",
    "arabic": r"[؀-ۿ]",
    "cyrillic": r"[Ѐ-ӿ]",
    "ascii_letter": r"[A-Za-z]",
}
HYGIENE_RX = {
    "control_char": r"[\x00-\x08\x0b-\x1f\x7f]",
    "replacement_char": "�",
    "zero_width": r"[​-‏⁠﻿]",
    "nbsp": " ",
    "mojibake_hint": r"Ã.|â€|Â",
    "leading_trailing_ws": r"^\s|\s$",
    "html_entity": r"&(?:amp|lt|gt|quot|#\d+);",
}
_SCRIPT_C = {k: re.compile(v) for k, v in SCRIPT_RX.items()}
_HYG_C = {k: re.compile(v) for k, v in HYGIENE_RX.items()}
NA_TOKENS = {"", "na", "n/a", "nan", "null", "none", "nil", "-", "--", "?", "unknown", "#n/a"}


def _has(s: pd.Series, rx) -> pd.Series:
    with warnings.catch_warnings():  # one flag (repeated_char4) needs a capture group for its backreference
        warnings.simplefilter("ignore", UserWarning)
        return s.str.contains(rx, regex=True)


def name_flags(s: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({k: _has(s, rx) for k, rx in _NAME_RX.items()})
    df["all_upper"] = s.str.isupper()
    df["all_lower"] = s.str.islower()
    return df


def addr_flags(s: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({k: _has(s, rx) for k, rx in _ADDR_RX.items()})
    df["all_upper"] = s.str.isupper()
    df["comma_count_ge3"] = s.str.count(",") >= 3
    return df


def script_flags(s: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({k: _has(s, rx) for k, rx in _SCRIPT_C.items()})
    df["nonlatin"] = df[["devanagari", "other_indic", "cjk", "arabic", "cyrillic"]].any(axis=1)
    df["mixed_script"] = df["nonlatin"] & df["ascii_letter"]
    return df


def hygiene_flags(s: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({k: _has(s, rx) for k, rx in _HYG_C.items()})
    df["na_token"] = s.str.strip().str.casefold().isin(NA_TOKENS) & (s != "")
    return df


def parse_ids(s: pd.Series, prefix: str):
    """Return (int64 array with -1 where invalid, bool valid mask). ID format: '<prefix>-<digits>'."""
    valid = s.str.fullmatch(prefix + r"-\d{1,18}").to_numpy()
    num = s.str.slice(len(prefix) + 1).where(valid, "-1")
    return pd.to_numeric(num).to_numpy(dtype=np.int64), valid


def pair_flags(a_name, b_name, a_addr, b_addr, an=None, bn=None, aan=None, ban=None):
    """Per-pair noise flags for one (S1 record, matched record). Scalars in, dict out.
    Pass pre-normalised an/bn/aan/ban (from `norm`) when calling in bulk."""
    from difflib import SequenceMatcher
    out = {}
    an = _norm1(a_name) if an is None else an
    bn = _norm1(b_name) if bn is None else bn
    out["name_exact"] = a_name == b_name
    out["name_case_only"] = a_name != b_name and a_name.casefold() == b_name.casefold()
    out["name_norm_equal"] = an == bn
    ac, bc = canon_tokens(an), canon_tokens(bn)
    out["name_canon_equal"] = ac == bc
    out["name_token_set_equal_reordered"] = ac != bc and sorted(ac) == sorted(bc)
    b_nonlatin = bool(_SCRIPT_C["devanagari"].search(b_name) or _SCRIPT_C["other_indic"].search(b_name)
                      or _SCRIPT_C["cjk"].search(b_name) or _SCRIPT_C["arabic"].search(b_name)
                      or _SCRIPT_C["cyrillic"].search(b_name))
    out["name_match_is_nonlatin"] = b_nonlatin
    out["name_amp_mismatch"] = ("&" in a_name) != ("&" in b_name)
    out["name_legal_form_differs"] = (
        bool(_NAME_RX["legal_abbr"].search(a_name)) != bool(_NAME_RX["legal_abbr"].search(b_name)))
    out["name_dba_in_match"] = bool(_NAME_RX["dba_marker"].search(b_name))
    ats, bts = set(ac), set(bc)
    out["name_token_overlap_zero"] = not (ats & bts)
    out["name_sim"] = SequenceMatcher(None, an, bn).ratio() if an and bn else 0.0
    aan = _norm1(a_addr) if aan is None else aan
    ban = _norm1(b_addr) if ban is None else ban
    aac, bac = canon_tokens(aan), canon_tokens(ban)
    out["addr_exact"] = a_addr == b_addr
    out["addr_norm_equal"] = aan == ban
    out["addr_canon_equal"] = aac == bac
    out["addr_token_set_equal_reordered"] = aac != bac and sorted(aac) == sorted(bac)
    out["addr_match_empty"] = b_addr.strip() == ""
    out["addr_s1_empty"] = a_addr.strip() == ""
    out["addr_token_overlap_zero"] = not (set(aac) & set(bac))
    out["addr_pin_dropped"] = bool(_ADDR_RX["pin6"].search(a_addr) or _ADDR_RX["zip5"].search(a_addr)) and not (
        _ADDR_RX["pin6"].search(b_addr) or _ADDR_RX["zip5"].search(b_addr))
    out["addr_landmark_in_match"] = bool(_ADDR_RX["landmark"].search(b_addr))
    out["addr_sim"] = SequenceMatcher(None, aan, ban).ratio() if aan and ban else 0.0
    out["both_token_overlap_zero"] = out["name_token_overlap_zero"] and out["addr_token_overlap_zero"]
    return out


def _norm1(x: str) -> str:
    return norm(pd.Series([x])).iloc[0]

"""P1-001 / P1-012: byte-level structural scan of a TSV, independent of any CSV parser.

Why raw: pandas' default quoting can silently merge or drop lines when a field contains a
double quote, so the parser cannot be used to audit itself.
"""
from collections import Counter

MAX_EXAMPLES = 10
BLOCK = 64 * 1024 * 1024


def scan_tsv(path, expected_header, id_prefix=None):
    """Return structural metrics for one TSV. Streams the file in 64 MB blocks."""
    n_cols = len(expected_header)
    hdr_line = "\t".join(expected_header)
    res = {
        "path": str(path), "expected_columns": n_cols, "lines_total": 0, "data_lines": 0,
        "header_ok": None, "header_found": None, "bom": False,
        "tab_count_hist": Counter(), "wrong_column_lines": 0, "wrong_column_examples": [],
        "invalid_utf8_lines": 0, "invalid_utf8_examples": [], "crlf_lines": 0, "cr_in_line": 0,
        "blank_lines": 0, "nul_lines": 0, "quote_lines": 0, "quote_examples": [],
        "id_prefix_bad": 0, "id_prefix_bad_examples": [],
        "final_newline": None, "bytes": 0,
    }
    tail = b""
    line_no = 0
    prefix = (id_prefix + "-").encode() if id_prefix else None
    with open(path, "rb") as f:
        first = True
        while True:
            block = f.read(BLOCK)
            if not block:
                break
            res["bytes"] += len(block)
            data = tail + block
            cut = data.rfind(b"\n")
            if cut < 0:
                tail = data
                continue
            body, tail = data[:cut + 1], data[cut + 1:]
            if first:
                first = False
                if body.startswith(b"\xef\xbb\xbf"):
                    res["bom"] = True
                    body = body[3:]
            lines = body.split(b"\n")[:-1]
            for raw in lines:
                line_no += 1
                _scan_line(raw, line_no, n_cols, hdr_line, prefix, res)
    if tail:  # last line without a trailing newline
        line_no += 1
        _scan_line(tail, line_no, n_cols, hdr_line, prefix, res)
        res["final_newline"] = False
    else:
        res["final_newline"] = True
    res["lines_total"] = line_no
    res["data_lines"] = max(line_no - 1, 0)
    res["tab_count_hist"] = dict(sorted(res["tab_count_hist"].items()))
    return res


def _scan_line(raw, line_no, n_cols, hdr_line, prefix, res):
    if raw.endswith(b"\r"):
        res["crlf_lines"] += 1
        raw = raw[:-1]
    if b"\r" in raw:
        res["cr_in_line"] += 1
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        res["invalid_utf8_lines"] += 1
        if len(res["invalid_utf8_examples"]) < MAX_EXAMPLES:
            res["invalid_utf8_examples"].append(line_no)
        text = raw.decode("utf-8", errors="replace")
    if line_no == 1:
        res["header_found"] = text
        res["header_ok"] = text == hdr_line
        return
    if not raw:
        res["blank_lines"] += 1
        return
    if b"\x00" in raw:
        res["nul_lines"] += 1
    tabs = raw.count(b"\t")
    res["tab_count_hist"][tabs] += 1
    if tabs != n_cols - 1:
        res["wrong_column_lines"] += 1
        if len(res["wrong_column_examples"]) < MAX_EXAMPLES:
            res["wrong_column_examples"].append([line_no, text[:120]])
    if b'"' in raw:
        res["quote_lines"] += 1
        if len(res["quote_examples"]) < MAX_EXAMPLES:
            res["quote_examples"].append([line_no, text[:120]])
    if prefix is not None and not raw.startswith(prefix):
        res["id_prefix_bad"] += 1
        if len(res["id_prefix_bad_examples"]) < MAX_EXAMPLES:
            res["id_prefix_bad_examples"].append([line_no, text[:60]])


def pandas_default_read_check(path, cols, chunk_rows=1_000_000):
    """What the README's own one-liner (pd.read_csv(path, sep=tab), default quoting and NA
    handling) does to this file: row count and cells silently turned into NaN per column."""
    import pandas as pd
    rows, na = 0, Counter()
    for ch in pd.read_csv(path, sep="\t", chunksize=chunk_rows, encoding_errors="replace",
                          on_bad_lines="skip", usecols=cols):
        rows += len(ch)
        for c in cols:
            na[c] += int(ch[c].isna().sum())
    return {"rows_default_parse": rows, "nan_cells_default_parse": dict(na)}

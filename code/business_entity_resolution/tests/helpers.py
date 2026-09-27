"""Synthetic mini-dataset with hand-known properties (used by all Phase 1 tests)."""
from pathlib import Path

H = "entity_id\tbusiness_name\tbusiness_address\tcountry\n"


def _w(path, text, mode="w"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode + "b") as f:
        f.write(text.encode("utf-8") if isinstance(text, str) else text)


def build(root):
    root = Path(root)
    tr, te = root / "train", root / "test"
    _w(tr / "train_source1.tsv", H + (
        "S1-1\tAcme Corporation\t1 Main Street, Austin, TX\tUS\n"
        "S1-2\tRam Marketing Private Limited\tKH 5, NEW DELHI, Delhi 110001\tIndia\n"
        "S1-3\tLonely Cafe\t9 Oak Rd, Reno, NV\tUS\n"
        "S1-4\tBeta & Sons\t2 Elm St, Boston, MA\tUS\n"
        "S1-5\tSingle Shop\t\tIndia\n"
        "S1-6\tGamma \"Quoted\" Ltd\t3 Pine Ave, Miami, FL\tUS\n"))
    _w(tr / "train_ground_truth.tsv", "source1_entity_id\tmatched_entity_ids\n"
       "S1-1\tS2-11,S2-12,S3-21\nS1-2\tS3-22\nS1-3\t\nS1-4\tS2-13\nS1-5\t\nS1-6\tS2-14,S2-15\n")
    _w(tr / "train_source2.tsv", H + (
        "S2-11\tACME CORP\t1 MAIN ST, AUSTIN, TX\tUS\n"
        "S2-12\tAcme Corp.\t1 Main St, Austin\tUS\n"
        "S2-13\tSons & Beta\t2 ELM STREET, BOSTON, MA\tUS\n"
        "S2-14\tGamma \"Quoted\" Limited\t3 Pine Avenue, Miami, FL\tUS\n"
        "S2-15\tGamma Quoted Ltd\t3 PINE AVE, MIAMI\tUS\n"
        "S2-16\tOrphan Books\t7 Nowhere Ln, Tulsa, OK\tUS\n"
        "S2-17\tACME CORP\t1 MAIN ST, AUSTIN, TX\tUS\n"
        "S2-18\tNA\tsomewhere\tIndia\n"))
    _w(tr / "train_source3.tsv", H + (
        "S3-21\tAcme Co\t1 Main Street\tUS\n"
        "S3-22\tराम मार्केटिंग प्राइवेट लिमिटेड\tKH 5, NEW DELHI, Delhi\tIndia\n"
        "S3-23\tOrphan Traders\t\tIndia\n"))
    _w(te / "test_source1.tsv", H + (
        "S1-101\tDelta Bakery\t5 Fir Rd, Dallas, TX\tUS\n"
        "S1-102\tÉcole Marina Sarl\t63 R. DE DIEPPE, LILLE\tFrance\n"))
    _w(te / "test_source2.tsv", H + (
        "S2-201\tDELTA BAKERY\t5 FIR ROAD, DALLAS\tUS\n"
        "S2-202\tMarina Ecole France Sarl\t63 R. DE DIEPPE, LILLE, Hauts-de-France\tFrance\n"))
    _w(te / "test_source3.tsv", H + "S3-301\tEcole Marina\tLille\tFrance\n")
    return root

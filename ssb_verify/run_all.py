#!/usr/bin/env python3

import csv
import subprocess
import time

from collections import Counter
from pathlib import Path


import argparse

# Project paths
# Read the scale factor from the command line.
# Defaults to SF1, so the old command still works.
parser = argparse.ArgumentParser(
    description="Compare Rubicon SSB results against DuckDB."
)

parser.add_argument(
    "--sf",
    type=int,
    default=1,
    help="SSB scale factor to verify, e.g. 1 or 10"
)

args = parser.parse_args()

if args.sf <= 0:
    parser.error("--sf must be greater than 0")

SF = args.sf


# Project paths.
ROOT = Path.home() / "Rubicon"
VERIFY = ROOT / "ssb_verify"
RESULTS = VERIFY / "results"

# Select the DuckDB database for this scale factor
DB = VERIFY / f"ssb_sf{SF}.duckdb"

# Keep all verification output in one directory
# Prefix filenames so e.g. SF1 and SF10 results do not overwrite each other
RESULT_PREFIX = f"sf{SF}_"

# Rubicon executable and its result file
OPTIMIZER = ROOT / "build/bin/optimizer-unit"
RUBICON_RESULT = ROOT / "results" / "result_.tsv"

RESULTS.mkdir(parents=True, exist_ok=True)


# SSB queries as Rubicon expects them
#
# DuckDB uses the same queries with two schema differences:
#   "date"  -> dim_date
#   p_brand -> p_brand1
QUERIES = {
    "q1.1": """
SELECT SUM(lo.lo_extendedprice * lo.lo_discount) AS revenue
FROM lineorder AS lo
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE d.d_year = 1993
  AND lo.lo_discount BETWEEN 1 AND 3
  AND lo.lo_quantity < 25;
""",

    "q1.2": """
SELECT SUM(lo.lo_extendedprice * lo.lo_discount) AS revenue
FROM lineorder AS lo
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE d.d_yearmonthnum = 199401
  AND lo.lo_discount BETWEEN 4 AND 6
  AND lo.lo_quantity BETWEEN 26 AND 35;
""",

    "q1.3": """
SELECT SUM(lo.lo_extendedprice * lo.lo_discount) AS revenue
FROM lineorder AS lo
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE d.d_weeknuminyear = 6
  AND d.d_year = 1994
  AND lo.lo_discount BETWEEN 5 AND 7
  AND lo.lo_quantity BETWEEN 26 AND 35;
""",

    "q2.1": """
SELECT SUM(lo.lo_revenue) AS revenue, d.d_year, p.p_brand
FROM lineorder AS lo
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
JOIN part AS p ON lo.lo_partkey = p.p_partkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
WHERE p.p_category = 'MFGR#12'
  AND s.s_region = 'AMERICA'
GROUP BY d.d_year, p.p_brand
ORDER BY d.d_year, p.p_brand;
""",

    "q2.2": """
SELECT SUM(lo.lo_revenue) AS revenue, d.d_year, p.p_brand
FROM lineorder AS lo
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
JOIN part AS p ON lo.lo_partkey = p.p_partkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
WHERE p.p_brand BETWEEN 'MFGR#2221' AND 'MFGR#2228'
  AND s.s_region = 'ASIA'
GROUP BY d.d_year, p.p_brand
ORDER BY d.d_year, p.p_brand;
""",

    "q2.3": """
SELECT SUM(lo.lo_revenue) AS revenue, d.d_year, p.p_brand
FROM lineorder AS lo
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
JOIN part AS p ON lo.lo_partkey = p.p_partkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
WHERE p.p_brand = 'MFGR#2239'
  AND s.s_region = 'EUROPE'
GROUP BY d.d_year, p.p_brand
ORDER BY d.d_year, p.p_brand;
""",

    "q3.1": """
SELECT c.c_nation, s.s_nation, d.d_year, SUM(lo.lo_revenue) AS revenue
FROM lineorder AS lo
JOIN customer AS c ON lo.lo_custkey = c.c_custkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE c.c_region = 'ASIA'
  AND s.s_region = 'ASIA'
  AND d.d_year BETWEEN 1992 AND 1997
GROUP BY c.c_nation, s.s_nation, d.d_year
ORDER BY d.d_year, revenue;
""",

    "q3.2": """
SELECT c.c_city, s.s_city, d.d_year, SUM(lo.lo_revenue) AS revenue
FROM lineorder AS lo
JOIN customer AS c ON lo.lo_custkey = c.c_custkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE c.c_nation = 'UNITED STATES'
  AND s.s_nation = 'UNITED STATES'
  AND d.d_year BETWEEN 1992 AND 1997
GROUP BY c.c_city, s.s_city, d.d_year
ORDER BY d.d_year, revenue;
""",

    "q3.3": """
SELECT c.c_city, s.s_city, d.d_year, SUM(lo.lo_revenue) AS revenue
FROM lineorder AS lo
JOIN customer AS c ON lo.lo_custkey = c.c_custkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE c.c_city IN ('UNITED KI1','UNITED KI5')
  AND s.s_city IN ('UNITED KI1','UNITED KI5')
  AND d.d_year BETWEEN 1992 AND 1997
GROUP BY c.c_city, s.s_city, d.d_year
ORDER BY d.d_year, revenue;
""",

    "q3.4": """
SELECT c.c_city, s.s_city, d.d_year, SUM(lo.lo_revenue) AS revenue
FROM lineorder AS lo
JOIN customer AS c ON lo.lo_custkey = c.c_custkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE c.c_city IN ('UNITED KI1','UNITED KI5')
  AND s.s_city IN ('UNITED KI1','UNITED KI5')
  AND d.d_yearmonth = 'Dec1997'
GROUP BY c.c_city, s.s_city, d.d_year
ORDER BY d.d_year, revenue;
""",

    "q4.1": """
SELECT d.d_year, c.c_nation,
       SUM(lo.lo_revenue - lo.lo_supplycost) AS profit
FROM lineorder AS lo
JOIN customer AS c ON lo.lo_custkey = c.c_custkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
JOIN part AS p ON lo.lo_partkey = p.p_partkey
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE c.c_region = 'AMERICA'
  AND s.s_region = 'AMERICA'
  AND p.p_mfgr IN ('MFGR#1','MFGR#2')
GROUP BY d.d_year, c.c_nation
ORDER BY d.d_year, c.c_nation;
""",

    "q4.2": """
SELECT d.d_year, s.s_nation, p.p_category,
       SUM(lo.lo_revenue - lo.lo_supplycost) AS profit
FROM lineorder AS lo
JOIN customer AS c ON lo.lo_custkey = c.c_custkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
JOIN part AS p ON lo.lo_partkey = p.p_partkey
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE c.c_region = 'AMERICA'
  AND s.s_region = 'AMERICA'
  AND d.d_year IN (1997,1998)
  AND p.p_mfgr IN ('MFGR#1','MFGR#2')
GROUP BY d.d_year, s.s_nation, p.p_category
ORDER BY d.d_year, s.s_nation, p.p_category;
""",

    "q4.3": """
SELECT d.d_year, s.s_city, p.p_brand,
       SUM(lo.lo_revenue - lo.lo_supplycost) AS profit
FROM lineorder AS lo
JOIN customer AS c ON lo.lo_custkey = c.c_custkey
JOIN supplier AS s ON lo.lo_suppkey = s.s_suppkey
JOIN part AS p ON lo.lo_partkey = p.p_partkey
JOIN "date" AS d ON lo.lo_orderdate = d.d_datekey
WHERE s.s_nation = 'UNITED STATES'
  AND d.d_year IN (1997,1998)
  AND p.p_category = 'MFGR#14'
GROUP BY d.d_year, s.s_city, p.p_brand
ORDER BY d.d_year, s.s_city, p.p_brand;
"""
}


def duckdb_query(sql):
    """Adjust the Rubicon query for the DuckDB schema."""

    return (
        sql
        .replace('JOIN "date" AS d', 'JOIN dim_date AS d')
        .replace('p.p_brand', 'p.p_brand1')
    )


def normalize(src, dst):
    """
    Put both result files into the same format.

    Rubicon can return columns in a different order than the SELECT.
    We order columns by name, then sort all result rows.
    Duplicate rows are kept.
    """

    with open(src, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter="\t"))

    if not rows:
        raise RuntimeError(f"Empty result file: {src}")

    header = rows[0]
    data = rows[1:]

    # Same SSB column, different name in the two schemas.
    header = [
        "p_brand" if column == "p_brand1" else column
        for column in header
    ]

    # Use one fixed column order for both engines.
    order = sorted(
        range(len(header)),
        key=lambda i: header[i]
    )

    normalized_header = [
        header[i]
        for i in order
    ]

    normalized_rows = [
        [row[i] for i in order]
        for row in data
    ]

    # Row order is not relevant for this correctness check.
    # This is a lexicographical sort over the complete row.
    normalized_rows.sort()

    with open(dst, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(
            f,
            delimiter="\t",
            lineterminator="\n"
        )

        writer.writerow(normalized_header)
        writer.writerows(normalized_rows)


def run_duckdb(name, sql):
    """Run one query in DuckDB and save the normalized result."""

    raw = RESULTS / f"{RESULT_PREFIX}{name}_duckdb_raw.tsv"
    normalized = RESULTS / f"{RESULT_PREFIX}{name}_duckdb.tsv"

    query = duckdb_query(sql).strip().rstrip(";")
    output_path = str(raw).replace("'", "''")

    # COPY gives us a clean TSV file including the column names.
    command = (
        f"COPY ({query}) "
        f"TO '{output_path}' "
        f"(FORMAT CSV, DELIMITER '\\t', HEADER TRUE);"
    )

    result = subprocess.run(
        [
            "duckdb",
            str(DB),
            "-c",
            command
        ],
        cwd=ROOT,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            "DuckDB failed:\n"
            + result.stderr.strip()
        )

    if not raw.exists():
        raise RuntimeError(
            f"DuckDB did not produce {raw}"
        )

    normalize(raw, normalized)

    # Only keep the normalized result.
    raw.unlink(missing_ok=True)

    return normalized


def run_rubicon(name, sql):
    """Run one query through Rubicon and save the normalized result."""

    normalized = RESULTS / f"{name}_rubicon.tsv"
    log = RESULTS / f"{name}_rubicon.log"

    # Remove the previous result so stale data cannot be used.
    RUBICON_RESULT.unlink(missing_ok=True)

    with log.open("w", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            [
                str(OPTIMIZER),
                "-q",
                " ".join(sql.split())
            ],
            cwd=ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True
        )

        try:
            # Give Rubicon up to two minutes per query.
            deadline = time.time() + 120

            last_size = -1
            stable_checks = 0

            while time.time() < deadline:
                if RUBICON_RESULT.exists():
                    size = RUBICON_RESULT.stat().st_size

                    # Wait until ResultOperator has stopped writing.
                    if size > 0 and size == last_size:
                        stable_checks += 1
                    else:
                        stable_checks = 0

                    last_size = size

                    # File unchanged for about one second.
                    if stable_checks >= 4:
                        break

                # optimizer-unit should not exit before producing a result.
                if (
                    proc.poll() is not None
                    and not RUBICON_RESULT.exists()
                ):
                    raise RuntimeError(
                        f"optimizer-unit exited before producing "
                        f"a result; see {log}"
                    )

                time.sleep(0.25)

            else:
                raise RuntimeError(
                    f"Timed out waiting for Rubicon result; "
                    f"see {log}"
                )

        finally:
            # optimizer-unit stays alive after submitting the query.
            # Stop this instance once the result is done.
            if proc.poll() is None:
                proc.terminate()

                try:
                    proc.wait(timeout=3)

                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()

    if not RUBICON_RESULT.exists():
        raise RuntimeError(
            f"Rubicon result file missing; see {log}"
        )

    normalize(
        RUBICON_RESULT,
        normalized
    )

    return normalized


def debug_difference(duckdb_file, rubicon_file, limit=5):
    """
    Show useful differences

    Counter is used so duplicate rows still matter.
    """

    with open(
        duckdb_file,
        newline="",
        encoding="utf-8"
    ) as f:
        duck_rows = list(csv.reader(f, delimiter="\t"))

    with open(
        rubicon_file,
        newline="",
        encoding="utf-8"
    ) as f:
        rubicon_rows = list(csv.reader(f, delimiter="\t"))

    if not duck_rows:
        print("     DuckDB result is empty")
        return

    if not rubicon_rows:
        print("     Rubicon result is empty")
        return

    duck_header = duck_rows[0]
    rubicon_header = rubicon_rows[0]

    duck_data = [
        tuple(row)
        for row in duck_rows[1:]
    ]

    rubicon_data = [
        tuple(row)
        for row in rubicon_rows[1:]
    ]

    print(f"     DuckDB rows : {len(duck_data)}")
    print(f"     Rubicon rows: {len(rubicon_data)}")

    # Headers should already be normalized, but print them if they differ.
    if duck_header != rubicon_header:
        print(f"     DuckDB columns : {duck_header}")
        print(f"     Rubicon columns: {rubicon_header}")

    # Count rows instead of converting to a set
    # This catches missing or extra duplicates too
    duck_count = Counter(duck_data)
    rubicon_count = Counter(rubicon_data)

    missing = duck_count - rubicon_count
    extra = rubicon_count - duck_count

    if missing:
        print("     Missing from Rubicon:")

        shown = 0

        for row, count in missing.items():
            suffix = f" x{count}" if count > 1 else ""
            print(f"       {row}{suffix}")

            shown += 1

            if shown >= limit:
                break

        if len(missing) > limit:
            print(
                f"       ... {len(missing) - limit} more"
            )

    if extra:
        print("     Extra in Rubicon:")

        shown = 0

        for row, count in extra.items():
            suffix = f" x{count}" if count > 1 else ""
            print(f"       {row}{suffix}")

            shown += 1

            if shown >= limit:
                break

        if len(extra) > limit:
            print(
                f"       ... {len(extra) - limit} more"
            )

    # Only happens if the files differ in some unexpected way.
    if not missing and not extra and duck_header == rubicon_header:
        print(
            "     Results contain the same rows, "
            "but the normalized files differ"
        )


def main():
    """Run all SSB queries and compare Rubicon against DuckDB."""

    if not DB.exists():
        raise SystemExit(
            f"DuckDB database not found: {DB}"
        )

    if not OPTIMIZER.exists():
        raise SystemExit(
            f"optimizer-unit not found: {OPTIMIZER}"
        )

    passed = 0
    failed = 0

    print(f"SSB SF{SF} verification")
    print("PASS means DuckDB and Rubicon produced the same normalized result.")
    print("Columns are aligned, rows are sorted, and duplicates are preserved.")
    print(f"Rubicon must be running against data/binary/sf{SF}.")
    print("====================")
    print()
    for name, sql in QUERIES.items():
        print(
            f"{name:4} ",
            end="",
            flush=True
        )

        try:
            # DuckDB is the reference result.
            duckdb_result = run_duckdb(
                name,
                sql
            )

            # Run the same query through Rubicon.
            rubicon_result = run_rubicon(
                name,
                sql
            )

        except Exception as error:
            failed += 1

            print("ERROR")
            print(f"     {error}")

            continue

        # Normalized files must be byte-for-byte equal.
        if (
            duckdb_result.read_bytes()
            == rubicon_result.read_bytes()
        ):
            passed += 1
            print("PASS")

        else:
            failed += 1
            print("FAIL")

            debug_difference(
                duckdb_result,
                rubicon_result
            )

    print()
    print("====================")
    print(f"{passed}/{len(QUERIES)} passed")

    # Non-zero exit code is useful when this gets used in CI.
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

# SSB Verification

This folder contains the DuckDB setup and comparison script used to verify Rubicon against the SSB queries.

Both systems use data from the same SSB generation.

## Setup on a new server

### 1. Pull Rubicon

```bash
cd ~/Rubicon
git pull
```

### 2. Install DuckDB

```bash
curl https://install.duckdb.org | DUCKDB_VERSION=1.5.6 bash
```

Add DuckDB to the current shell:

```bash
export PATH="$HOME/.duckdb/cli/1.5.6:$PATH"
```

Check:

```bash
duckdb --version
```

To keep the path after reconnecting:

```bash
echo 'export PATH="$HOME/.duckdb/cli/1.5.6:$PATH"' >> ~/.bashrc
```

## Generate SSB data

Set the scale factor in:

```text
data/setup.sh
```

For example:

```bash
SCALE_FACTORS=(50)
```

Then run:

```bash
cd ~/Rubicon/data
bash setup.sh
```

The script generates one SSB dataset and keeps it in two formats:

```text
~/ssb_sf50/
```

contains the original `.tbl` files used for DuckDB.

```text
~/Rubicon/data/binary/sf50/
```

contains the converted binary data used by Rubicon.

Both come from the same `dbgen` run.

## Check the generated data

For SF50:

```bash
wc -l ~/ssb_sf50/*.tbl
```

Expected:

```text
customer       1500000
date              2556
lineorder     300005884
part            1200000
supplier          100000
```

Also check that the Rubicon schema was copied:

```bash
ls -lh ~/Rubicon/data/binary/sf50/schema.txt
```

## Build the DuckDB database

From the Rubicon root:

```bash
cd ~/Rubicon
python3 ssb_verify/build_duckdb.py --sf 50
```

This reads:

```text
~/ssb_sf50/*.tbl
```

and creates:

```text
ssb_verify/ssb_sf50.duckdb
```

The `.duckdb` files are generated locally and are not committed to Git.

## Run Rubicon

Start Grouper:

```bash
cd ~/Rubicon
./build/bin/grouper
```

Start ComputeUnit in another terminal:

```bash
cd ~/Rubicon

./build/bin/computeUnit \
    -ip 127.0.0.1 \
    -port 23232 \
    -path data/binary/sf50 \
    -basedata bin \
    -worker 48 \
    -node 0 \
    -cxl_node 1
```

Make sure the binary path matches the scale factor being tested.

## Run the verification

In another terminal:

```bash
cd ~/Rubicon
python3 ssb_verify/run_all.py --sf 50
```

The script runs all 13 SSB queries on DuckDB and Rubicon and compares the results.

Before comparing:

- equivalent column names are aligned
- columns are put into the same order
- rows are sorted lexicographically
- duplicate rows are kept

`PASS` means both systems returned the same normalized result.

On failure, the script prints missing and extra rows to make debugging easier.

## Other scale factors

The same scripts work for other scale factors:

```bash
python3 ssb_verify/build_duckdb.py --sf 1
python3 ssb_verify/run_all.py --sf 1
```

or:

```bash
python3 ssb_verify/build_duckdb.py --sf 50
python3 ssb_verify/run_all.py --sf 50
```

The ComputeUnit path has to use the same scale factor:

```text
data/binary/sf1
data/binary/sf50
```

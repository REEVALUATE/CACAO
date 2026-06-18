# Competency-question queries

`cq01.rq` through `cq35.rq` implement the 35 competency questions defined in the CACAO ontology paper. Each query returns at most 20 representative rows so it can be inspected safely on the public ARTKB endpoint.

Run all queries with:

```sh
./queries/run.sh
```

By default the runner targets the public ARTKB endpoint at `https://loki.linksfoundation.com/reevaluate-graphdb/repositories/art`. Pass a different endpoint URL as the first argument to override.

The runner prints `answered` when a query returns at least one row, `empty` when the query is valid but ARTKB has no matching data, and `error` when execution fails. An empty result assesses the current ARTKB population, not necessarily the expressiveness of CACAO.

`results-2026-06-18.tsv` records the execution against the public `art` repository on June 18, 2026.

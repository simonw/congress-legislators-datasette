#!/bin/bash
datasette publish cloudrun legislators.db \
  --service congress-legislators \
  --metadata metadata.yml \
  --install datasette-graphql \
  --install datasette-cluster-map \
  --install datasette-pretty-json \
  --install datasette-copyable \
  --branch main \
  --extra-options="--setting sql_time_limit_ms 3000"

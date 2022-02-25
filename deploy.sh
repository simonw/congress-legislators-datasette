#!/bin/bash
datasette publish cloudrun legislators.db \
  --service congress-legislators \
  --metadata metadata.yml \
  --install datasette-graphql \
  --install datasette-cluster-map

#!/bin/bash

echo "waiting for kafka and executing"
wait-for-it $KAFKA_SERVER_IP:$KAFKA_SERVER_PORT -- $@
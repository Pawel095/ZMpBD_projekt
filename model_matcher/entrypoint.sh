
echo "waiting for kafka"
wait-for-it $KAFKA_SERVER_IP:$KAFKA_SERVER_PORT

echo "Executing command"
exec "$@"
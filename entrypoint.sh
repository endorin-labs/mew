ip addr add 127.0.0.1/32 dev lo
ip addr add 127.0.0.2/32 dev lo
ip link set dev lo up

touch /app/libnsm.so
echo "Starting sockets"
echo "127.0.0.2   aws-0-us-east-1.pooler.supabase.com" >> /etc/hosts
socat vsock-listen:8000,fork,reuseaddr tcp-connect:localhost:50051 & # when the enclave is a server
socat tcp-listen:5432,fork,bind=127.0.0.2,reuseaddr,su=nobody vsock-connect:3:8001 & # when the enclave is a client
. /app/.venv/bin/activate
python3.8 /app/server.py
# On host for database
# open a new terminal and add
# sudo socat VSOCK-LISTEN:8001,fork,reuseaddr tcp-connect:aws-0-us-east-1.pooler.supabase.com:5432 & # when ec2 is listening from outside (server)
# sudo socat tcp-listen:50051,fork,reuseaddr VSOCK-CONNECT:19:8000 & # when the ec2 instance is a forwarding outside (client)
# DB_HOST=127.0.0.2 for enclave
# DB_PORT=5432
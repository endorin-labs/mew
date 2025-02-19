ip addr add 127.0.0.1/32 dev lo
ip addr add 127.0.0.2/32 dev lo
ip addr add 127.0.0.3/32 dev lo
ip link set dev lo up

touch /app/libnsm.so
#echo "About to start a socat bridge from 443 to vsock 8000"
echo "127.0.0.2   aws-0-us-east-1.pooler.supabase.com" >> /etc/hosts
echo "127.0.0.3    kms.us-east-1.amazonaws.com" >> /etc/hosts
socat vsock-listen:8000,fork,reuseaddr tcp-connect:localhost:50051 &
socat tcp-listen:5432,fork,bind=127.0.0.2,reuseaddr,su=nobody vsock-connect:3:8001 &
socat tcp-listen:443,fork,bind=127.0.0.3,reuseaddr,su=nobody vsock-connect:3:8002 &
. /app/.venv/bin/activate
python3.8 /app/server.py
# On host for database
# open a new terminal and add
# sudo socat TCP-LISTEN:5432,reuseaddr,fork VSOCK:16:8001
# sudo socat TCP-LISTEN:50051,reuseaddr,fork VSOCK:16:8000
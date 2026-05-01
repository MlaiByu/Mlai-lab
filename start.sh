#!/bin/bash
cd /root/Mlai-lab
setsid bash -c 'cd /root/Mlai-lab/backend && python3 app.py </dev/null >/dev/null 2>&1' &
setsid bash -c 'cd /root/Mlai-lab/frontend && npm run dev </dev/null >/dev/null 2>&1' &
sleep 3
echo "已启动！前端: http://8.136.148.183:3000"
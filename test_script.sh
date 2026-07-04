#!/bin/bash

BASE_URL="http://127.0.0.1:8000"

echo "1) Login user"
USER_TOKEN=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" -d '{"username":"user1","password":"test1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "USER_TOKEN=$USER_TOKEN"

echo "2) Login admin"
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "ADMIN_TOKEN=$ADMIN_TOKEN"

echo "3) User creates appointment"
APPOINTMENT_ID=$(curl -s -X POST "$BASE_URL/appointments" -H "Content-Type: application/json" -H "Authorization: Bearer $USER_TOKEN" -d '{"slot":"10am-11am"}' | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('id') or data.get('appointmentId'))")

echo "APPOINTMENT_ID=$APPOINTMENT_ID"

echo "4) User views own appointments"
curl -s -X GET "$BASE_URL/appointments" -H "Authorization: Bearer $USER_TOKEN"
echo ""

echo "5) Admin views all appointments"
curl -s -X GET "$BASE_URL/appointments" -H "Authorization: Bearer $ADMIN_TOKEN"
echo ""

echo "6) User updates own appointment"
curl -s -X PUT "$BASE_URL/appointments/$APPOINTMENT_ID" -H "Content-Type: application/json" -H "Authorization: Bearer $USER_TOKEN" -d '{"slot":"2pm-3pm"}'
echo ""

echo "7) Admin deletes appointment"
curl -s -X DELETE "$BASE_URL/appointments/$APPOINTMENT_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
echo ""

echo "Done"
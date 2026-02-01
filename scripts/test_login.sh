#!/bin/bash
# 测试登录流程

echo "🧪 测试登录流程..."
echo ""

# 1. 测试登录 API
echo "1. 测试登录 API..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@medicare.ai",
    "password": "medicare123456"
  }')

echo "$LOGIN_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'tokens' in data:
    print('   ✅ Login successful!')
    token = data['tokens']['access_token']
    print(f'   Token: {token[:50]}...')
    # Save token for next test
    with open('/tmp/test_token.txt', 'w') as f:
        f.write(token)
else:
    print('   ❌ Login failed!')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Login test failed!"
    exit 1
fi

echo ""

# 2. 测试获取患者列表（需要登录 token）
echo "2. 测试获取患者列表..."
TOKEN=$(cat /tmp/test_token.txt)
PATIENTS_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/patients/ \
  -H "Authorization: Bearer $TOKEN")

echo "$PATIENTS_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        print(f'   ✅ Got {len(data)} patient(s)')
        for patient in data:
            print(f'   - {patient[\"name\"]} ({patient[\"date_of_birth\"]})')
    else:
        print('   ❌ Unexpected response format')
        print(json.dumps(data, indent=2))
except:
    print('   ❌ Failed to parse response')
    print(sys.argv[1] if len(sys.argv) > 1 else '')
" "$PATIENTS_RESPONSE"

echo ""
echo "✅ 登录流程测试完成！"

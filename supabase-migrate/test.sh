export SOURCE_REF="wsljomxsvaxzweooixbv"
export SOURCE_PASSWORD="hr-dashboafd123"

hosts=(
  "db.${SOURCE_REF}.supabase.co"
  "db.${SOURCE_REF}.aws-ap-northeast-1.supabase.co" # Tokyo
  "db.${SOURCE_REF}.aws-ap-southeast-1.supabase.co" # Singapore
  "db.${SOURCE_REF}.aws-us-east-1.supabase.co"
  "db.${SOURCE_REF}.aws-us-west-1.supabase.co"
  "db.${SOURCE_REF}.aws-eu-central-1.supabase.co"
)

ok=""
for h in "${hosts[@]}"; do
  echo "== Trying $h =="
  if pg_dump "postgresql://postgres:${SOURCE_PASSWORD}@${h}:5432/postgres?sslmode=require" \
      --schema-only --no-owner --no-privileges -f schema.sql 2>/dev/null; then
    echo "✅ Dumped schema.sql from $h"
    ok="yes"
    break
  else
    echo "…failed on $h"
  fi
done

if [ -z "$ok" ]; then
  echo "❌ 全候補で接続失敗。ネットワーク/DNS設定の影響が濃厚です。"
fi

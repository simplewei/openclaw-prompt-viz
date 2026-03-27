#!/bin/bash
# 分批次获取钉钉AI表格数据（每批20条，最多10批）
BASE_ID="l6Pm2Db8D4Xdo9lYUGL3lXy48xLq0Ee4"
TABLE_ID="d7FEhge"

> all_records.json
> batch_summary.txt

for i in 1 2 3 4 5 6 7 8 9 10; do
  echo "=== 批次 $i ===" >> batch_summary.txt
  
  if [ $i -eq 1 ]; then
    CMD=(mcporter call dingtalk-ai-table.query_records baseId:"$BASE_ID" tableId:"$TABLE_ID" limit:20)
  else
    PREV_FILE="batch_$((i-1)).json"
    if [ ! -f "$PREV_FILE" ]; then break; fi
    CURSOR=$(python3 -c "import json; d=json.load(open('$PREV_FILE')); print(d.get('nextCursor',''))" 2>/dev/null)
    if [ -z "$CURSOR" ]; then
      echo "无更多cursor，停止" >> batch_summary.txt
      break
    fi
    CMD=(mcporter call dingtalk-ai-table.query_records baseId:"$BASE_ID" tableId:"$TABLE_ID" limit:20 cursor:"$CURSOR")
  fi
  
  echo "执行: ${CMD[@]}" >> batch_summary.txt
  "${CMD[@]}" > batch_$i.json 2>&1
  
  if [ $? -ne 0 ]; then
    echo "执行失败" >> batch_summary.txt
    break
  fi
  
  # 验证JSON格式
  python3 -m json.tool batch_$i.json > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "JSON格式错误，停止" >> batch_summary.txt
    break
  fi
  
  REC_COUNT=$(python3 -c "import json; print(len(json.load(open('batch_$i.json')).get('records',[])))" 2>/dev/null)
  echo "记录数: $REC_COUNT" >> batch_summary.txt
  
  # 合并
  python3 -c "
import json, sys
with open('all_records.json','r') as f:
  try: all_data = json.load(f)
  except: all_data = {'records':[]}
with open('batch_$i.json') as b:
  batch = json.load(b)
all_data['records'].extend(batch.get('records',[]))
json.dump(all_data, open('all_records.json','w'), ensure_ascii=False)
" 2>/dev/null
  
  echo "" >> batch_summary.txt
  
  sleep 0.5
done

echo "总计记录: $(python3 -c "import json; print(len(json.load(open('all_records.json',errors='ignore')).get('records',[])))" 2>/dev/null)"

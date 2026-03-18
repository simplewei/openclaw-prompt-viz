#!/usr/bin/env node
/**
 * AI助手业务自动化 - 收入统计与到期提醒 (本地过滤版)
 */

const { exec } = require('child_process');

const CONFIG = {
  BASE_ID: 'G53mjyd80pq9kDovCld6RKan86zbX04v',
  TABLES: {
    orders: 'GPPInsK',
    stats: 'rLs7pGI',
    customers: 'YoSJP1q'
  },
  DINGTALK_WEBHOOK: process.env.DINGTALK_WEBHOOK || '',
  WORKSPACE: process.env.OPENCLAW_WORKSPACE || '/root/.openclaw/workspace'
};

// 字段ID映射
const FIELD = {
  orders: {
    amount: 'paWPW0p',
    packageName: 'QEb9FaU',
    purchaseDate: 'ZETRGXm',
    expireDate: '9HWmHGX',
    status: '2m1xVEp'
  }
};

function mcporterCall(method, params = []) {
  return new Promise((resolve, reject) => {
    const paramStr = params.map(p => {
      if (typeof p === 'object') {
        return Object.entries(p).map(([k, v]) => `${k}='${v}'`).join(' ');
      }
      return p;
    }).join(' ');
    
    const cmd = `mcporter call dingtalk-ai-table ${method} ${paramStr} --output json`;
    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(`mcporter error: ${stderr || error.message}\nCommand: ${cmd}`));
        return;
      }
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        reject(new Error(`JSON parse error: ${stdout}`));
      }
    });
  });
}

function parseDate(dateStr) {
  // 处理 "2026-03-14T16:00:00Z" 格式
  return new Date(dateStr);
}

function isAfter(date, compareStr) {
  const d = parseDate(date);
  const c = new Date(compareStr + 'T00:00:00Z');
  return d > c;
}

function isBeforeOrEqual(date, compareStr) {
  const d = parseDate(date);
  const c = new Date(compareStr + 'T00:00:00Z');
  return d <= c;
}

function isStatusCompleted(statusObj) {
  return statusObj?.name === '已完成';
}

async function calculateStats() {
  const today = new Date().toISOString().split('T')[0];
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  
  console.log(`查询所有订单，本地筛选 ${sevenDaysAgo} 至 ${today} 的已完成订单...`);
  
  const result = await mcporterCall('query_records', [
    `baseId=${CONFIG.BASE_ID}`,
    `tableId=${CONFIG.TABLES.orders}`,
    'limit=1000'
  ]);
  
  console.log('Raw result:', JSON.stringify(result).substring(0, 500));
  
  if (!result.data || !result.data.records) {
    console.log('没有找到订单记录');
    return;
  }
  
  const allRecords = result.data.records;
  console.log(`总订单数: ${allRecords.length}`);
  
  // 本地筛选
  const filtered = allRecords.filter(record => {
    const cells = record.cells;
    const purchaseDate = cells[FIELD.orders.purchaseDate]?.value;
    const status = cells[FIELD.orders.status];
    
    if (!purchaseDate || !status) return false;
    if (status.name !== '已完成') return false;
    
    return isAfter(purchaseDate, sevenDaysAgo) && isBeforeOrEqual(purchaseDate, today);
  });
  
  console.log(`筛选后: ${filtered.length} 个已完成订单`);
  
  let totalSales = 0;
  let orderCount = 0;
  const salesByPackage = {};
  
  for (const record of filtered) {
    const cells = record.cells;
    const amount = parseFloat(cells[FIELD.orders.amount]?.value || 0);
    const packageName = cells[FIELD.orders.packageName]?.value || '未知';
    
    totalSales += amount;
    orderCount++;
    
    salesByPackage[packageName] = (salesByPackage[packageName] || 0) + amount;
  }
  
  const topPackage = Object.entries(salesByPackage)
    .sort((a, b) => b[1] - a[1])[0];
  
  const statsMonth = today.substring(0, 7);
  
  console.log(`统计结果：月份=${statsMonth}, 销售额=${totalSales}, 订单数=${orderCount}, 热门=${topPackage?.[0] || '无'}`);
  
  // TODO: 写入收入统计表
  
  return { statsMonth, totalSales, orderCount, topPackage: topPackage?.[0] };
}

async function checkExpiringOrders() {
  const today = new Date().toISOString().split('T')[0];
  const threeDaysLater = new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  
  console.log(`检查所有订单，筛选 ${today} 至 ${threeDaysLater} 到期的已完成订单...`);
  
  const result = await mcporterCall('query_records', [
    `baseId=${CONFIG.BASE_ID}`,
    `tableId=${CONFIG.TABLES.orders}`,
    'limit=1000'
  ]);
  
  if (!result.data || !result.data.records) {
    console.log('没有订单记录');
    return [];
  }
  
  const allRecords = result.data.records;
  
  const expiring = allRecords.filter(record => {
    const cells = record.cells;
    const expireDate = cells[FIELD.orders.expireDate]?.value;
    const status = cells[FIELD.orders.status];
    
    if (!expireDate || !status) return false;
    if (status.name !== '已完成') return false;
    
    const e = parseDate(expireDate);
    const t = new Date(today + 'T00:00:00Z');
    const t3 = new Date(threeDaysLater + 'T00:00:00Z');
    
    return e >= t && e <= t3;
  });
  
  console.log(`找到 ${expiring.length} 个即将到期的订单`);
  
  let message = `📢 **到期提醒** (${today})\n\n`;
  
  for (const record of expiring) {
    const cells = record.cells;
    const expireDate = cells[FIELD.orders.expireDate]?.value;
    const packageName = cells[FIELD.orders.packageName]?.value;
    const customerId = cells['DgakkR6']?.value;
    const orderId = record.recordId;
    
    message += `- 到期日：${expireDate}\n`;
    message += `  套餐：${packageName}\n`;
    message += `  客户ID：${customerId}\n`;
    message += `  订单ID：${orderId}\n\n`;
  }
  
  message += `⏰ 请及时联系客户续费！\n`;
  
  console.log(message);
  
  if (CONFIG.DINGTALK_WEBHOOK) {
    sendDingTalkNotification(message);
  }
  
  return expiring;
}

function sendDingTalkNotification(message) {
  const escaped = message.replace(/"/g, '\\"').replace(/\n/g, '\\n');
  exec(`curl -s -X POST "${CONFIG.DINGTALK_WEBHOOK}" \
    -H "Content-Type: application/json" \
    -d '{"msgtype":"markdown","markdown":{"title":"AI助手业务提醒","text":"${escaped}"}}'`, (err, stdout, stderr) => {
    if (err) {
      console.error('钉钉通知发送失败:', stderr);
    } else {
      console.log('钉钉通知已发送');
    }
  });
}

async function main() {
  console.log('=== AI助手业务自动化开始 ===');
  
  try {
    const stats = await calculateStats();
    const expiring = await checkExpiringOrders();
    
    console.log('=== 完成 ===');
    console.log(JSON.stringify({ stats, expiringCount: expiring.length }, null, 2));
    
  } catch (error) {
    console.error('自动化执行失败:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { calculateStats, checkExpiringOrders };

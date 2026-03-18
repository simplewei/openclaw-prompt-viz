#!/usr/bin/env node
/**
 * AI助手业务自动化 - 收入统计与到期提醒
 * 
 * 功能：
 * 1. 每日从订单表统计收入，更新收入统计表
 * 2. 查找3天内到期的订单，生成提醒
 * 3. 自动发送钉钉通知（需配置钉钉机器人）
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  // CRM Base ID
  BASE_ID: 'G53mjyd80pq9kDovCld6RKan86zbX04v',
  // 表ID
  TABLES: {
    orders: 'GPPInsK',      // 订单表
    stats: 'rLs7pGI',       // 收入统计
    customers: 'YoSJP1q'    // 客户表
  },
  // 钉钉机器人Webhook（可选）
  DINGTALK_WEBHOOK: process.env.DINGTALK_WEBHOOK || '',
  // 工作区路径
  WORKSPACE: process.env.OPENCLAW_WORKSPACE || '/root/.openclaw/workspace'
};

// 工具函数：执行mcporter命令
function mcporterCall(method, args) {
  return new Promise((resolve, reject) => {
    const argsJson = JSON.stringify(args);
    const cmd = `mcporter call dingtalk-ai-table ${method} --args '${argsJson}' --output json`;
    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(`mcporter error: ${stderr || error.message}`));
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

// 1. 统计今日收入（最近7天内的订单）
async function calculateStats() {
  const today = new Date().toISOString().split('T')[0];
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  
  console.log(`查询 ${sevenDaysAgo} 至 ${today} 的订单...`);
  
  // 查询最近的订单
  const result = await mcporterCall('query_records', {
    baseId: CONFIG.BASE_ID,
    tableId: CONFIG.TABLES.orders,
    filter: {
      formula: `AND(IS_AFTER(购买时间, "${sevenDaysAgo}"), IS_BEFORE_OR_EQUAL(购买时间, "${today}"), 订单状态="已完成")`
    },
    limit: 1000
  });
  
  if (!result.data || !result.data.records) {
    console.log('没有找到订单记录');
    return;
  }
  
  const records = result.data.records;
  console.log(`找到 ${records.length} 个订单`);
  
  // 统计
  let totalSales = 0;
  let orderCount = 0;
  const salesByPackage = {};
  
  for (const record of records) {
    const cells = record.cells;
    const amount = parseFloat(cells['购买金额(元)']?.value || 0);
    const packageName = cells['套餐名称']?.value || '未知';
    
    totalSales += amount;
    orderCount++;
    
    salesByPackage[packageName] = (salesByPackage[packageName] || 0) + amount;
  }
  
  // 找出热门套餐
  const topPackage = Object.entries(salesByPackage)
    .sort((a, b) => b[1] - a[1])[0];
  
  const statsMonth = today.substring(0, 7); // YYYY-MM
  
  console.log(`统计结果：月份=${statsMonth}, 销售额=${totalSales}, 订单数=${orderCount}, 热门=${topPackage?.[0]}`);
  
  // 检查是否已有该月统计
  const checkResult = await mcporterCall('query_records', {
    baseId: CONFIG.BASE_ID,
    tableId: CONFIG.TABLES.stats,
    filter: {
      formula: `统计月份="${statsMonth}"`
    },
    limit: 1
  });
  
  const existingRecord = checkResult.data?.records?.[0];
  
  if (existingRecord) {
    // 更新现有统计
    const recordId = existingRecord.recordId;
    await mcporterCall('update_records', {
      baseId: CONFIG.BASE_ID,
      tableId: CONFIG.TABLES.stats,
      records: [{
        recordId,
        cells: {
          '总销售额(元)': { value: totalSales },
          '订单数量': { value: orderCount },
          '热门套餐': { value: topPackage?.[0] || '' },
          '备注': { value: `最后更新：${today}` }
        }
      }]
    });
    console.log(`已更新统计记录 ${recordId}`);
  } else {
    // 创建新统计
    const result = await mcporterCall('create_records', {
      baseId: CONFIG.BASE_ID,
      tableId: CONFIG.TABLES.stats,
      records: [{
        cells: {
          '统计月份': { value: statsMonth },
          '总销售额(元)': { value: totalSales },
          '订单数量': { value: orderCount },
          '热门套餐': { value: topPackage?.[0] || '' },
          '备注': { value: `创建日期：${today}` }
        }
      }]
    });
    console.log(`已创建统计记录 ${result.newRecordIds[0]}`);
  }
  
  return { statsMonth, totalSales, orderCount, topPackage: topPackage?.[0] };
}

// 2. 检查即将到期的订单（3天内）
async function checkExpiringOrders() {
  const today = new Date().toISOString().split('T')[0];
  const threeDaysLater = new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  
  console.log(`检查 ${today} 至 ${threeDaysLater} 到期的订单...`);
  
  const result = await mcporterCall('query_records', {
    baseId: CONFIG.BASE_ID,
    tableId: CONFIG.TABLES.orders,
    filter: {
      formula: `AND(IS_AFTER_OR_EQUAL(到期日期, "${today}"), IS_BEFORE_OR_EQUAL(到期日期, "${threeDaysLater}"), 订单状态="已完成")`
    },
    limit: 100
  });
  
  if (!result.data || !result.data.records) {
    console.log('没有即将到期的订单');
    return [];
  }
  
  const expiringOrders = result.data.records;
  console.log(`找到 ${expiringOrders.length} 个即将到期的订单`);
  
  // 生成提醒消息
  let message = `📢 **到期提醒** (${today})\n\n`;
  
  for (const record of expiringOrders) {
    const cells = record.cells;
    const expireDate = cells['到期日期']?.value;
    const packageName = cells['套餐名称']?.value;
    const customerId = cells['客户ID']?.value;
    const orderId = record.recordId;
    
    message += `- 到期日：${expireDate}\n`;
    message += `  套餐：${packageName}\n`;
    message += `  客户ID：${customerId}\n`;
    message += `  订单ID：${orderId}\n\n`;
  }
  
  message += `⏰ 请及时联系客户续费！\n`;
  message += `[查看CRM](${CONFIG.WORKSPACE})`;
  
  console.log(message);
  
  // 发送钉钉通知（如果配置了webhook）
  if (CONFIG.DINGTALK_WEBHOOK) {
    sendDingTalkNotification(message);
  }
  
  return expiringOrders;
}

// 发送钉钉通知
async function sendDingTalkNotification(message) {
  exec(`curl -X POST "${CONFIG.DINGTALK_WEBHOOK}" \
    -H "Content-Type: application/json" \
    -d '{"msgtype":"markdown","markdown":{"title":"AI助手业务提醒","text":"${message.replace(/"/g, '\\"')}"}}'`, (err, stdout, stderr) => {
    if (err) {
      console.error('钉钉通知发送失败:', stderr);
    } else {
      console.log('钉钉通知已发送');
    }
  });
}

// 主函数
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

// 如果直接运行此脚本
if (require.main === module) {
  main();
}

module.exports = { calculateStats, checkExpiringOrders };

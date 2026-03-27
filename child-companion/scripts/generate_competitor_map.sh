#!/bin/bash
# 橙发运动竞品地图生成脚本
# 使用：bash generate_competitor_map.sh

CONFIG_FILE="橙发运动竞品数据收集表.md"
OUTPUT_KML="橙发运动竞品地图.kml"
OUTPUT_REPORT="橙发运动竞品分析报告.md"

echo "=========================================="
echo "🏸 橙发运动周边竞品地图生成工具"
echo "=========================================="
echo ""

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误：找不到数据收集表 $CONFIG_FILE"
    echo "请先按照'橙发运动竞品数据收集表.md'填写数据"
    exit 1
fi

echo "✅ 找到数据文件：$CONFIG_FILE"
echo ""
echo "请确保你已经："
echo "1. 填写了'竞品基础信息'表格（至少填写球馆名称、距离、地址）"
echo "2. 填写了'价格明细'表格"
echo "3. 确认了橙发运动中心的确切坐标（经纬度）"
echo ""

read -p "继续生成地图和报告？(y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# TODO: 这里应该解析Markdown表格并生成KML
# 由于Markdown解析复杂，建议手动将数据转为CSV后使用工具

echo "⚠️  注意：当前版本为框架脚本"
echo ""
echo "下一步操作："
echo "1. 将数据表格转换为CSV格式（Excel另存为CSV）"
echo "2. 使用在线工具或Python脚本生成KML"
echo "3. 或手动在高德地图标注平台输入数据"
echo ""
echo "📊 推荐工具："
echo "- 在线KML生成：https://kmlplanet.com/creating-kml"
echo "- Python库：simplekml"
echo "- QGIS：专业地图制作"
echo ""
echo "📞 需要我帮你："
echo " - 制作Excel数据收集模板（带公式）"
echo " - 生成KML转换脚本（Python）"
echo " - 输出完整分析报告（Word格式）"
echo ""
echo "请告诉我你的选择。"
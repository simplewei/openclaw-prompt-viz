const ExcelJS = require('exceljs');

async function createWorkbook() {
  const wb = new ExcelJS.Workbook();
  const ws = wb.addWorksheet('窗帘报价');

  // 设置列宽
  ws.columns = [
    { width: 30 },
    { width: 20 },
    { width: 15 },
    { width: 20 }
  ];

  // 标题合并单元格
  ws.mergeCells('A1:D1');
  const title = ws.getCell('A1');
  title.value = '窗帘报价计算表';
  title.font = { size: 16, bold: true };
  title.alignment = { horizontal: 'center' };

  // 输入参数区域
  ws.getCell('A3').value = '输入参数';
  ws.getCell('A3').font = { bold: true };

  const inputs = [
    ['纱帘单价（元/米）', 'B4', 0],
    ['布帘单价（元/米）', 'B5', 0],
    ['轨道单价（元/米）', 'B6', 0],
    ['电机价格（元/个）', 'B7', 0],
    ['罗马帘平方单价（元/平方米）', 'B8', 0],
    ['日夜蜂巢帘平方单价（元/平方米）', 'B9', 0],
    ['百叶帘平方单价（元/平方米）', 'B10', 0],
  ];

  inputs.forEach(([text, cell, val], idx) => {
    const row = 4 + idx;
    ws.getCell(`A${row}`).value = text;
    ws.getCell('B' + row).value = val;
    ws.getCell('B' + row).numFmt = '"¥"#,##0.00';
  });

  // 尺寸固定值
  ws.getCell('A12').value = '尺寸固定值（mm）';
  ws.getCell('A12').font = { bold: true };

  const sizes = [
    ['客厅宽度', 'B13', 4200],
    ['客厅高度', 'B14', 2700],
    ['主卧飘窗内宽度', 'B15', 2700],
    ['主卧飘窗内高度', 'B16', 2100],
    ['主卧外围宽度', 'B17', 3500],
    ['主卧外围高度', 'B18', 2700],
    ['次卧宽度', 'B19', 3200],
    ['次卧高度', 'B20', 2700],
    ['儿童房飘窗内宽度', 'B21', 1950],
    ['儿童房飘窗内高度', 'B22', 2100],
    ['书房宽度', 'B23', 2500],
    ['书房高度', 'B24', 2700],
    ['卫生间1宽度', 'B25', 800],
    ['卫生间1高度', 'B26', 2500],
    ['卫生间2宽度', 'B27', 900],
    ['卫生间2高度', 'B28', 1200],
  ];

  sizes.forEach(([text, cell, val]) => {
    const row = parseInt(cell.substring(1));
    ws.getCell(`A${row}`).value = text;
    ws.getCell(cell).value = val;
  });

  // 计算结果
  ws.getCell('A30').value = '各房间价格';
  ws.getCell('A30').font = { bold: true };

  // 客厅价格: =B4*(B13/1000) + B6*(B13/1000) + B7
  ws.getCell('A31').value = '客厅价格';
  ws.getCell('B31').value = { formula: 'B$4*(B13/1000) + B$6*(B13/1000) + B$7', result: 0 };
  ws.getCell('B31').numFmt = '"¥"#,##0.00';

  // 主卧价格: =B8*(B15/1000)*(B16/1000) + B6*(B15/1000) + B7 + B5*(B17/1000)
  ws.getCell('A32').value = '主卧价格';
  ws.getCell('B32').value = { formula: 'B$8*(B15/1000)*(B16/1000) + B$6*(B15/1000) + B$7 + B$5*(B17/1000)', result: 0 };
  ws.getCell('B32').numFmt = '"¥"#,##0.00';

  // 次卧价格: =(B4+B5)*(B19/1000) + B6*(B19/1000) + B7
  ws.getCell('A33').value = '次卧价格';
  ws.getCell('B33').value = { formula: '(B$4+B$5)*(B19/1000) + B$6*(B19/1000) + B$7', result: 0 };
  ws.getCell('B33').numFmt = '"¥"#,##0.00';

  // 儿童房价格: =B9*(B21/1000)*(B22/1000) + B6*(B21/1000) + B7
  ws.getCell('A34').value = '儿童房价格';
  ws.getCell('B34').value = { formula: 'B$9*(B21/1000)*(B22/1000) + B$6*(B21/1000) + B$7', result: 0 };
  ws.getCell('B34').numFmt = '"¥"#,##0.00';

  // 书房价格: =B4*(B23/1000) + B6*(B23/1000) + B7
  ws.getCell('A35').value = '书房价格';
  ws.getCell('B35').value = { formula: 'B$4*(B23/1000) + B$6*(B23/1000) + B$7', result: 0 };
  ws.getCell('B35').numFmt = '"¥"#,##0.00';

  // 卫生间价格: =((B25*B26 + B27*B28)/1000000) * B10
  ws.getCell('A36').value = '卫生间价格';
  ws.getCell('B36').value = { formula: '((B25*B26 + B27*B28)/1000000) * B$10', result: 0 };
  ws.getCell('B36').numFmt = '"¥"#,##0.00';

  // 总价
  ws.getCell('A38').value = '总价';
  ws.getCell('A38').font = { bold: true };
  ws.getCell('B38').value = { formula: 'SUM(B31:B36)', result: 0 };
  ws.getCell('B38').numFmt = '"¥"#,##0.00';
  ws.getCell('B38').font = { bold: true };

  // 添加备注
  ws.getCell('A40').value = '备注：';
  ws.getCell('A41').value = '1. 所有长度单位：mm，转换米需除以1000';
  ws.getCell('A42').value = '2. 面积计算：mm² 转换为 m² 需除以1,000,000';
  ws.getCell('A43').value = '3. 轨道单价按每米计算，布料按每米或每平方米分别计算';
  ws.getCell('A44').value = '4. 每个房间均包含一个电机（卫生间除外）';

  // 保存文件
  await wb.xlsx.writeFile('/root/.openclaw/workspace/窗帘报价计算.xlsx');
  console.log('Excel file created successfully');
}

createWorkbook().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});

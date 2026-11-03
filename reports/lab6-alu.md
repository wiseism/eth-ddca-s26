# ETH DDCA Spring2026 Lab6：测试和修复ALU

依据当期Lab5表1与Lab6手册，补全给定ALU_test.v的100位testvec数组、readmemh、exp_zero、UUT实例。保留原12个输入，按独立Python整数模型填写输出，再添加175组边界与1000组随机输入，共1187组，覆盖七种有效操作与zero标志。

bad_ALU按手册要求做小范围修复：逻辑选择应使用aluop低两位；原1010计算却1011选出的slt操作码不一致；diff使用非阻塞赋值导致读旧值，组合块缺省赋值导致锁存。现用完整组合块和阻塞赋值，slt扩展为32位。

注意当期Lab5表1明确定义slt=(A-B)[31]，不是完整带溢出修正的MIPS有符号比较。本实现严格遵守课程表格，边界oracle也检查这个语义，未擅自替换为$signed(a)<$signed(b)。其他无效操作码按课程不作语义保证。

原错误ALU与不完整向量保存在lab6/reference，独立yml要求原错误版本被同一测试台拒绝（>=7错误），修正版本1187组零错误，Yosys不产生$dlatch。测试错误会$fatal返回非零，不能只有打印错误仍绿。所有模拟、综合在GitHub Actions完成；没有运行Vivado时序/利用率或FPGA实板，也没有进行课程要求的现场TA展示，因此只验收Lab6软件功能验证部分。

官方来源：https://safari.ethz.ch/ddca/spring2026/doku.php?id=labs 。Lab6手册仍残留spring2025下载URL，但当期网页直接提供spring2026归档，SOURCE.json记录实际下载来源。

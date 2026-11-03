# Lab7：MIPS 汇编实验报告

本实验采用 [Spring2026 官方 Lab7 手册](https://safari.ethz.ch/ddca/spring2026/lib/exe/fetch.php?media=ddca_ss26_lab7_manual.pdf)、[报告要求](https://safari.ethz.ch/ddca/spring2026/lib/exe/fetch.php?media=ddca_ss26_lab7_report.pdf)，使用官方发行包内 Mars.jar。手册内部仍引用2025下载链接，实际框架来自2026实验页和 SOURCE.json 中的归档哈希。未运行助教现场展示或提交 Moodle。

## 范围求和

`lab7/lab7.asm` 从 A 到 B 逐项相加，包含两端，结果留在 `$t2`；输入由 ADDI 装入，使用的指令严格属于 ADD/SUB/SLT/XOR/AND/OR/NOR/J/ADDI/BEQ 集合。没有乘除、访存或伪指令。循环加法后的 BEQ 检查当前整数是否已为 B，避免边界遗漏；原手册的终止无限循环保留。无害的 `add $zero,$zero,$zero` 保证延迟分支开启或关闭时均正确。

## 灰度 SAD

`lab7/lab7_sad.asm` 补齐全部输入、循环、绝对差函数和递归求和，保留了原始 starter 到 `lab7/reference/`。内存配置为 CompactDataAtZero：left_image 九个32位值在0～32字节，right_image在36～68，sad_array在72～104。手册输入每对像素差均为1，因此 sad_array 为九个1，`$t2=9`。

abs_diff 用符号掩码、异或和减法取绝对值，不使用 abs 伪指令，支持课程灰度0～16和报告中的RGB字节范围，不声称对不可表示的有符号绝对值/溢出也有效。循环变量置于 `$s0～$s3`；函数调用后重新计算临时地址，不依赖 `$t` 寄存器保持。

recursive_sum 的零长度分支返回0。非零分支使用32字节栈帧，保留16字节传出参数区，保存数组基址、长度和 `$ra`，递归返回后再加最后一项并恢复栈。主程序将课程模拟器的初始栈从非8字节对齐的0x2ffc明确设为0x2ff8，再为调用预留16字节参数区。

## 报告附加题：六参数 RGB 函数

`lab7/abs_diff_color.asm` 实现 `abs(R1-R2)+abs(G1-G2)+abs(B1-B2)`，调用上述 abs_diff 三次。依据 [System V MIPS ABI](https://refspecs.linuxbase.org/elf/mipsabi.pdf) 的参数归位区约定，前四个整数使用 `$a0～$a3`，第5/6个参数位于**入口** `$sp+16/$sp+20`。这不是 `$sp+0/$sp+4`。

函数分配48字节且保持8字节对齐，包含16字节传出参数区、`$s0～$s6` 与 `$ra` 保存区。因此入口第五/六参数在新栈帧中从 `$sp+64/$sp+68` 读取。所有颜色参数和累加值跨调用保存在需恢复的 `$s` 寄存器，返回结果在 `$v0`。返回前恢复全部使用的保存寄存器及栈指针。

## 验证与边界

独立工作流 `lab7-mips.yml` 只在 GitHub Actions 使用 JDK17 执行课程原始 MARS；本项目没有新增 Java 源码/Java 构建工程。Python 是可独立运行的远程验收入口 `scripts/check_lab7.py`。

测试关闭伪指令（np），按课程内存配置运行，并分别测试延迟分支开启/关闭。原始空 starter 必须不能得到45，防止无效绿色；生产程序的终端无限循环只在测试副本中替换为模拟器退出 syscall，不修改计算路径。

- 范围求和：边界和随机正16位范围，共80次运行，对照整数公式。
- 3×3 SAD：手册输入、相同图像、灰度边界和随机输入，共60次；检查全部27个内存字、总和及栈恢复。
- abs_diff：全部17×17灰度对，双分支模式共578例。
- RGB：相等/极值及随机六参数，共200例；检查返回值、原始输入内存、`$s0～$s7/$fp/$gp`、栈平衡及参数区之后的保护字。
- 递归求和：空向量、负数、随机数组及96层递归，共50例，同样检查保存寄存器、输入未修改和栈保护字。

共968个逻辑案例，实际日志、MARS导出的内存十六进制与 summary.json 上传为产物。最深96层选择依据课程32KB紧凑地址空间的可用栈容量，不把模拟器地址限制当成硬件或算法无限制保证。最终通过状态以实验分支最终提交的完成态 CI 为准；现场TA展示及Moodle评分未验收，本地未编译或运行实验。

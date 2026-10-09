# 虚拟机部署与演示视频操作手册

本手册给负责虚拟机部署和演示视频的同学使用。请严格按照顺序执行，并按截图清单保存证据。截图文件统一放在 `evidence/screenshots/`，命名为 `S01-环境.png`、`S02-安装.png` 等。

## 一、虚拟机准备

建议使用 Windows 10/11 或 Ubuntu 22.04，Python 3.10 及以上版本。将整个仓库复制或克隆到虚拟机中，不要只复制 `src` 目录。

### Windows

```powershell
git clone https://github.com/Dong-zan/lab0-crypto-experiment.git
cd lab0-crypto-experiment
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

如果 PowerShell 禁止激活脚本，可以不激活环境，直接使用：

```powershell
.\.venv\Scripts\python.exe src\crypto_demo.py
```

### Ubuntu

```bash
git clone https://github.com/Dong-zan/lab0-crypto-experiment.git
cd lab0-crypto-experiment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 二、部署截图清单

截图时确保终端中能看到命令和结果，避免只截代码编辑器。每张截图按下面的编号保存：

| 编号 | 截图内容 | 建议文件名 | 用途 |
|---|---|---|---|
| S01 | 仓库根目录，能看到 `src`、`tests`、`report`、`evidence` | `S01-项目目录.png` | 证明项目结构 |
| S02 | Python 版本和 `cryptography` 安装成功 | `S02-环境依赖.png` | 证明环境可复现 |
| S03 | AES-256-GCM 运行结果 | `S03-AES结果.png` | 报告 AES 实验 |
| S04 | RSA-OAEP-SHA256 运行结果 | `S04-RSA结果.png` | 报告 RSA 实验 |
| S05 | RSA+AES 混合加密结果 | `S05-混合加密结果.png` | 报告混合方案 |
| S06 | 篡改检测结果为 `true` | `S06-篡改检测.png` | 证明完整性保护 |
| S07 | X.509 证书主题、签发者和公钥长度 | `S07-公钥证书.png` | 证明证书扩展 |
| S08 | 4 个自动化测试全部通过 | `S08-测试通过.png` | 证明可复现 |
| S09 | RSA 190/191 字节长度边界 | `S09-RSA长度边界.png` | 解释混合加密必要性 |

截图后检查：文字清楚、命令行没有敏感信息、没有展示真实私钥、文件名与编号一致。

## 三、演示命令

在仓库根目录、虚拟环境激活后执行：

```powershell
python src\crypto_demo.py
```

录制扩展实验：

```powershell
python src\experiment_suite.py
```

录制证书扩展：

```powershell
python src\certificate_demo.py
```

录制测试：

```powershell
python -m unittest discover -s tests -v
```

生成报告数据文件：

```powershell
python src\crypto_demo.py --json --message "Big Data Security Lab0: cryptography experiment" > evidence\sample-output.json
python src\experiment_suite.py > evidence\extended-results.json
python src\certificate_demo.py > evidence\certificate-output.json
```

仓库中的证据文件是一次实际运行的样例。重新生成时，密钥、证书序列号和耗时会变化；如果替换证据文件，应重新截取对应截图，并确认报告中的数据仍然对应本次运行。

## 四、视频录制顺序

1. 说明项目用途，并展示 `README.md` 和项目目录。
2. 展示 Python 版本、依赖安装和 `requirements.txt`。
3. 运行 AES：说明 256 位密钥、12 字节 nonce、GCM 标签和解密结果。
4. 运行 RSA：说明 RSA-2048、OAEP-SHA256、公钥加密和私钥解密。
5. 运行混合加密：说明 RSA 只封装 AES 会话密钥，AES 加密实际明文。
6. 运行证书扩展：说明 Alice 的 X.509 证书如何提供公钥及身份信息。
7. 运行扩展实验：展示 RSA 190 字节成功、191 字节失败。
8. 运行自动化测试，展示所有测试为 `ok` 和最终 `OK`。
9. 打开报告，展示原理、流程图、实验表格和安全性分析。

每个步骤停留 3 至 5 秒，保证视频中命令、关键参数和结果可读。视频中可以使用实验专用密钥，但不得展示个人账号、密码或其他项目私钥。

## 五、报告材料对应关系

- S03、S04、S05：放在报告“实验结果”章节。
- S06：放在“完整性分析”章节。
- S07：放在“公钥证书扩展”章节。
- S08：放在“测试与证据”章节。
- S09：放在“RSA 长度限制与混合加密必要性”章节。
- 所有截图都要在报告正文附近加一句解释，不能只堆截图。

## 六、常见问题

- `cryptography` 找不到：确认虚拟环境已激活，再执行 `python -m pip install -r requirements.txt`。
- PowerShell 无法激活：直接使用 `.venv\Scripts\python.exe` 执行命令。
- 中文显示乱码：录屏时可使用英文测试明文，或先执行 `chcp 65001`。
- 测试失败：确认当前目录是仓库根目录，并重新安装依赖。
- 不要把 `private-key.pem`、账号密码和大型虚拟机镜像提交到 GitHub。

## 七、交付前检查

- [ ] `S01` 至 `S09` 截图已保存并命名正确。
- [ ] 视频包含基础实验、证书扩展、长度边界和测试通过。
- [ ] 虚拟机可以从全新环境按照本手册运行。
- [ ] 报告中已插入截图并解释实验现象。
- [ ] 视频、虚拟机、报告链接已写入报告和 README。

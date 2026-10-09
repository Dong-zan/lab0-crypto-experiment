# Lab0 密码学基础实验

本仓库用于完成 AES、RSA 和 RSA+AES 混合加密实验，并提供虚拟机部署与演示视频制作手册。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src\crypto_demo.py
```

Linux/macOS 将激活命令替换为 `source .venv/bin/activate`。

程序会依次演示 AES-256-GCM、RSA-OAEP（SHA-256）和混合加密，并验证篡改密文时会失败。

## 目录

- `src/crypto_demo.py`：可直接运行的基础实验演示程序。
- `src/experiment_suite.py`：不同明文长度、RSA 长度边界和扩展实验程序。
- `src/certificate_demo.py`：Alice 自签名 X.509 公钥证书扩展实验。
- `tests/`：自动化正确性测试。
- `docs/VM-and-demo-guide.md`：给部署虚拟机和录制视频同学的操作手册，包含截图清单。
- `report/experiment-report.md`：实验报告正文，实验数据来自实际运行。
- `evidence/`：运行输出、截图、视频链接等实验证据。

## 安全说明

程序每次运行都会随机生成密钥；实验私钥仅用于本地演示，不应上传到公开仓库。视频、虚拟机镜像等大文件请放在网盘或课程指定平台，并将公开链接补充到报告和本 README。

## 提交前检查

```powershell
python -m unittest discover -s tests -v
python src\crypto_demo.py --json --message "Big Data Security Lab0: cryptography experiment" > evidence\sample-output.json
python src\experiment_suite.py > evidence\extended-results.json
python src\certificate_demo.py > evidence\certificate-output.json
```

> 仓库中的证据文件是一次实际运行的样例。重新运行脚本时，密钥、证书序列号和耗时会变化；如要替换证据，应同时更新报告中的对应数据。

## 文件用途速查

| 文件/目录 | 用途 | 主要使用者 |
|---|---|---|
| `src/crypto_demo.py` | AES、RSA、RSA+AES 基础演示 | 演示同学、报告同学 |
| `src/experiment_suite.py` | 多种明文长度与 RSA 长度边界实验 | 报告同学 |
| `src/certificate_demo.py` | Alice X.509 公钥证书扩展 | 演示同学、报告同学 |
| `tests/` | 自动化正确性与篡改检测测试 | 全体成员 |
| `docs/VM-and-demo-guide.md` | 虚拟机部署、录屏和截图流程 | 虚拟机/视频同学 |
| `report/` | 实验报告正文 | 报告同学 |
| `evidence/` | 截图、JSON 输出、测试记录 | 全体成员 |

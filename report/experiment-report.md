# Lab0 密码学基础实验报告

## 摘要

本实验围绕对称加密、非对称加密和混合加密展开。实验分别使用 AES-256-GCM 完成数据加密，使用 RSA-OAEP-SHA256 完成短消息加密，再设计 RSA 封装 AES 会话密钥的混合加密协议。实验结果表明：AES 适合高效处理实际数据，RSA 适合保护短数据或会话密钥，混合加密能够同时获得对称加密的效率和非对称加密的密钥分发能力。篡改测试还验证了 GCM 的完整性保护作用。

## 一、实验目的

1. 理解对称密码和非对称密码解决的问题及其差异。
2. 掌握 AES 的分组加密、认证加密和 nonce 使用原则。
3. 掌握 RSA 密钥生成、公钥加密、私钥解密以及 OAEP 填充的作用。
4. 设计并实现一个 RSA+AES 混合加密流程。
5. 通过不同长度明文、篡改数据和 RSA 长度限制实验验证理论分析。

## 二、实验环境与工具

| 项目 | 内容 |
|---|---|
| 操作系统 | Windows（本地实验环境） |
| Python | 3.12.14 |
| 密码库 | cryptography 50.0.2 |
| 主要实现 | `src/crypto_demo.py` |
| 扩展实验 | `src/experiment_suite.py` |

本实验使用密码学库实现标准算法，不自行实现底层 AES 轮函数或大整数运算。这样可以避免教学演示代码引入不安全实现，同时在报告中解释算法内部结构、参数选择和安全性质。

## 三、密码学原理

### 3.1 对称加密与非对称加密

对称加密使用同一个秘密密钥完成加密和解密，优点是速度快、适合大量数据，难点是通信双方需要安全地共享密钥。非对称加密使用公钥和私钥：公钥可以公开，私钥必须保密，优点是可以解决密钥分发问题，缺点是计算开销大、可处理的明文长度有限。

因此，实际系统通常采用混合加密：用对称算法加密数据，用非对称算法保护对称会话密钥。

### 3.2 AES 原理

AES 是分组密码，固定处理 128 位明文分组。AES-256 使用 256 位密钥，经过密钥扩展得到各轮轮密钥，并进行 14 轮变换。每轮主要包含：

1. **SubBytes**：通过非线性 S 盒替换字节，提供非线性混淆。
2. **ShiftRows**：循环移动状态矩阵中的行，打散字节位置。
3. **MixColumns**：在有限域上混合每一列，扩散局部变化。
4. **AddRoundKey**：将状态与当前轮密钥异或。

最后一轮省略 MixColumns。单独使用 AES 分组加密还需要工作模式处理多个分组。本实验选择 GCM（Galois/Counter Mode）：计数器模式负责加密，GHASH 负责根据密文和附加数据计算认证标签。因此解密不仅要恢复明文，还必须验证标签；密文被修改时，验证失败而不会返回可信明文。

GCM 的 nonce 在同一个密钥下必须唯一。本实验每次随机生成 12 字节 nonce，不把 nonce 当作秘密信息；传输时可以和密文一起发送。

### 3.3 RSA 原理

RSA 的密钥生成过程如下：选择两个大素数 `p` 和 `q`，计算 `n=pq`，再计算 `φ(n)=(p-1)(q-1)`。选择与 `φ(n)` 互素的公钥指数 `e`，计算满足 `ed ≡ 1 (mod φ(n))` 的私钥指数 `d`。公钥为 `(n,e)`，私钥为 `(n,d)`。

对经过安全填充的消息 `m`，RSA 加密和解密的数学形式为：

```text
c = m^e mod n
m = c^d mod n
```

实验使用 2048 位 RSA，因此模数和密文长度均为 256 字节。直接使用裸 RSA 是不安全的：相同明文会产生相同密文，也容易受到结构性攻击。本实验使用 RSA-OAEP-SHA256，通过随机填充提高安全性。

RSA 的可加密明文长度受密钥长度和 OAEP 哈希算法限制。2048 位 RSA 配合 SHA-256 时，单次最多只能加密 190 字节，因此不适合直接加密大文件。

## 四、方案设计

### 4.1 AES 基础实验

```text
随机生成 256 位 AES 密钥和 12 字节 nonce
        ↓
AES-GCM 加密明文，得到 ciphertext 和 authentication tag
        ↓
使用同一密钥、nonce 和 tag 解密
        ↓
验证明文恢复；修改 ciphertext 后验证失败
```

### 4.2 RSA 基础实验

```text
生成 Alice 的 RSA-2048 密钥对
        ↓
使用公钥和 OAEP-SHA256 加密短明文
        ↓
使用私钥解密
        ↓
验证恢复原始明文
```

### 4.3 RSA+AES 混合加密

```text
Alice：生成 RSA 密钥对并发布公钥
Bob：随机生成 AES-256 会话密钥和 nonce
Bob：用 AES-GCM 加密实际明文
Bob：用 Alice 公钥和 RSA-OAEP 加密 AES 会话密钥
Bob：发送 encrypted_key、nonce、ciphertext、tag
Alice：用 RSA 私钥恢复 AES 密钥
Alice：验证 GCM 标签并解密明文
```

RSA 只处理短小的会话密钥，AES 负责真正的数据内容，避免 RSA 的长度限制和高计算成本。

### 4.4 公钥证书扩展

在扩展模块 `src/certificate_demo.py` 中，Alice 使用 RSA-2048 私钥生成一张自签名 X.509 证书。证书包含 Alice 的身份名称、有效期、序列号和 RSA 公钥。Bob 从证书读取公钥，再使用同样的 RSA-OAEP-SHA256 + AES-256-GCM 流程完成加密。

自签名证书只能证明“证书中的公钥与签发该证书的私钥匹配”，不能自动证明 Alice 的现实身份。生产环境应由可信 CA 签发证书，或由通信双方预先固定并校验证书指纹。

## 五、实现说明

核心实现位于 `src/crypto_demo.py`。AES 使用 `AESGCM`，RSA 使用 `rsa.generate_private_key`、OAEP 和 SHA-256。扩展实验位于 `src/experiment_suite.py`，用于比较不同长度明文并验证 RSA-OAEP 的长度边界。

AES 核心调用：

```python
aes = AESGCM(aes_key)
ciphertext = aes.encrypt(nonce, plaintext, None)
plaintext = aes.decrypt(nonce, ciphertext, None)
```

混合加密核心调用：

```python
encrypted_key = public_key.encrypt(aes_key, oaep_sha256)
recovered_key = private_key.decrypt(encrypted_key, oaep_sha256)
plaintext = AESGCM(recovered_key).decrypt(nonce, ciphertext, None)
```

## 六、实验步骤

1. 创建 Python 虚拟环境并安装 `requirements.txt`。
2. 运行基础演示：`python src/crypto_demo.py`。
3. 运行扩展实验：`python src/experiment_suite.py`。
4. 运行测试：`python -m unittest discover -s tests -v`。
5. 记录明文长度、密文长度、算法参数、耗时和解密结果。
6. 修改 AES 或混合加密密文的一个字节，观察认证失败。
7. 测试 RSA 加密 190 字节和 191 字节明文，观察长度边界。
8. 运行 `python src/certificate_demo.py`，观察证书主题、签发者、序列号和公钥参数。

## 七、实验结果

### 7.1 基础运行结果

本次使用明文 `Big Data Security Lab0: cryptography experiment`，UTF-8 编码长度为 47 字节。

| 方案 | 参数 | 明文 | 输出长度 | 单次耗时 | 解密 | 篡改检测 |
|---|---|---:|---:|---:|---|---|
| AES-256-GCM | 12 字节 nonce | 47 字节 | 63 字节 | 0.038 ms | 成功 | 成功 |
| RSA-OAEP-SHA256 | RSA-2048 | 47 字节 | 256 字节 | 2.330 ms | 成功 | 不适用 |
| RSA+AES | RSA-2048 + AES-256-GCM | 47 字节 | 密文 63 字节，封装密钥 256 字节 | 1.692 ms | 成功 | 成功 |

AES-GCM 的密文比明文多出认证标签长度；RSA 密文固定为 RSA 模数长度；混合方案同时携带 AES 密文和 RSA 封装后的会话密钥。

### 7.2 长度边界实验

2048 位 RSA-OAEP-SHA256 最多接受 190 字节明文。实验中 190 字节加密成功并产生 256 字节密文，191 字节输入被库以 `ValueError` 拒绝。这验证了 RSA 只适合处理短数据，也说明混合加密是必要的。

扩展实验进一步比较了不同数据规模：

| 案例 | 明文长度 | AES 密文长度 | AES 耗时 | 混合密文长度 | 混合耗时 |
|---|---:|---:|---:|---:|---:|
| short | 4 字节 | 20 字节 | 0.031 ms | 20 字节 | 1.773 ms |
| medium | 384 字节 | 400 字节 | 0.020 ms | 400 字节 | 1.661 ms |
| long | 1024 字节 | 1040 字节 | 0.009 ms | 1040 字节 | 1.668 ms |

AES-GCM 的输出长度始终比输入多 16 字节认证标签；混合方案的数据密文长度保持相同，只额外增加 256 字节 RSA 封装密钥。RSA 对 384 字节和 1024 字节案例不再适用。

### 7.3 完整性实验

将 AES-GCM 密文最后一个字节翻转后，解密抛出认证错误；混合方案中的 AES 密文被翻转后同样失败。说明 GCM 能发现传输过程中的篡改，但它不等同于身份认证：实际系统仍需要可信的 RSA 公钥来源或证书体系。

## 八、安全性分析

### 8.1 机密性

AES 会话密钥由随机数生成，实际数据不以明文传输；会话密钥再由 Alice 的 RSA 公钥封装，只有持有私钥的 Alice 能恢复。攻击者即使看到 AES 密文和 RSA 封装结果，也不能直接得到明文。

### 8.2 完整性

GCM 标签覆盖密文。攻击者修改密文、nonce 或附加认证数据时，标签验证失败。程序通过将密文最后一个字节翻转并运行自动化测试验证了这一性质。

### 8.3 密钥与 nonce 管理

AES 会话密钥应随机生成并尽量一次一密；同一 AES 密钥下不得重复使用 GCM nonce。RSA 私钥不能提交到公开仓库，Alice 的公钥必须通过可信渠道分发，否则攻击者可以替换公钥实施中间人攻击。

### 8.4 方案局限

本实验没有实现数字签名、证书校验、密钥轮换、重放保护和网络传输协议。因而它验证的是加密核心流程，不是完整生产级通信系统。

## 九、测试与证据

- 4 个自动化测试全部通过：AES 往返与篡改检测、RSA 往返、混合加密往返与篡改检测、证书封装往返。
- 基础实验 JSON 数据：`evidence/sample-output.json`（生成命令 `python src\crypto_demo.py --json --message "Big Data Security Lab0: cryptography experiment"`）。
- 扩展长度和 RSA 边界数据：`evidence/extended-results.json`（生成命令 `python src\experiment_suite.py`）。
- 公钥证书扩展代码与输出：`src/certificate_demo.py`、`evidence/certificate-output.json`。
- 测试运行记录：`evidence/test-run.txt`。
- 完整运行命令和录屏顺序见 `docs/VM-and-demo-guide.md`。

## 十、AI 辅助开发与验证说明

本实验使用 AI 作为开发辅助工具，介入范围包括实验方案梳理、密码库 API 样例生成、测试用例设计和报告结构整理。AES、RSA 及混合加密的算法选型、密钥参数、实验数据和安全性结论均由实验要求、密码库文档和实际运行结果共同确定。

| 工作内容 | AI 辅助范围 | 人工确认方式 |
|---|---|---|
| 方案设计 | 整理 AES、RSA 和 RSA+AES 的流程及参数候选 | 对照实验要求，确认 RSA 仅封装 AES 会话密钥 |
| 程序实现 | 提供 `cryptography` 库的调用框架和异常处理建议 | 在本地运行基础实验、扩展实验和证书实验 |
| 安全验证 | 提议 GCM 篡改测试、OAEP 长度边界测试 | 通过测试断言和实际异常结果确认 |
| 报告编写 | 协助组织原理、实现、结果和分析章节 | 使用实际 JSON 输出和测试记录回填数据 |

AI 输出不作为实验事实或安全结论的直接依据。代码经过本地运行和自动化测试后才纳入仓库；密钥长度、GCM nonce 使用、OAEP 明文上限、篡改检测结果等关键内容均以实验输出和官方 API 行为为准。AI 未参与私钥管理、证书信任决策或最终附件发布。

## 十一、附件链接

- 源代码仓库：待填写。
- 实验演示视频：待填写。
- 部署运行的虚拟机：待填写。
- 10 分钟实验报告汇报视频：待填写。

## 十二、结论

本实验验证了三种密码学使用方式的适用范围。AES-GCM 适合高效加密大量数据并检测篡改；RSA-OAEP 能利用公钥机制保护短消息和会话密钥，但受长度和性能限制；RSA+AES 混合加密通过分工同时解决数据加密效率和会话密钥传输问题。实验结果与 AES、RSA 和混合加密的理论性质一致。

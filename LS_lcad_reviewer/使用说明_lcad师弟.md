# lcad 训练集 10,000 张人工核验操作说明

这套文件专门给师弟使用。任务是审核 V4 版本的 lcad 训练集预标注，不要修改原始图片、原始 JSON 或任务文件。

## 一、先确认 U 盘目录结构

把 U 盘根目录保持成下面这样，两个目录都必须在 U 盘根目录：

```text
U盘根目录├─ LS_lcad_reviewer│  ├─ tasks_lcad_10000.json
│  ├─ interface_dual_v4.xml
│  ├─ 01_install_lcad.cmd
│  ├─ 02_start_lcad.cmd
│  ├─ 03_export_lcad.cmd
│  └─ export_reviewed_lcad.py
└─ 9_14_10000GT_V1   ├─ image\                 # 10,000 张 GT
   └─ model\lcad\            # 10,000 张 lcad 结果
```

不要把 `LS_lcad_reviewer` 放到 `9_14_10000GT_V1` 里面。U 盘盘符可能是 E、G、H 等，脚本会自动使用当前盘符，不要手动把盘符写死。

任务 JSON 是 U 盘专用版，已将图片地址改成：

```text
/data/local-files/?d=9_14_10000GT_V1/model/lcad/...
/data/local-files/?d=9_14_10000GT_V1/image/...
```

不要使用原电脑生成的 `tasks_v4_train_lcad_10000.json`，因为其中仍是 `data-result/coco/...` 路径。

## 二、两台电脑能否同时使用

可以同时使用，但要分清两种情况：

### 情况 A：各自本地运行

你的电脑和师弟电脑分别双击各自的启动脚本，浏览器访问各自的 `http://localhost:8080`。这是两个独立 Label Studio 实例，数据和账号互不相通。师弟需要在自己的电脑首次注册一个本地账号。

这也是本说明推荐的方式。师弟做完后导出 JSON，通过 U 盘交回给你。

### 情况 B：共用一台服务器

只有当两台电脑访问同一台电脑的局域网地址或同一台云服务器时，才是“共用同一个 Label Studio 项目”。这时可以同时标注，但不要共用你的账号，应该让师弟使用自己的账号，以便区分操作者和避免任务重复分配。

不要让两台电脑同时运行两个实例并指望它们自动同步；`localhost` 永远指当前电脑。

## 三、第一次安装

在师弟电脑上：

1. 安装脚本优先使用本目录 `.python` 中的 Python 3.11；如果该目录不存在，需要先安装 `uv`，脚本会自动下载 Python 3.11 到本目录。不需要系统的 `py -3.11`。
2. 保持 U 盘连接，打开 `LS_lcad_reviewer` 文件夹。
3. 双击 `01_install_lcad.cmd`。
4. 等待窗口显示 `Installation completed`。

`.venv` 必须在师弟电脑上重新创建，不能直接复制你电脑的 `.venv`。虚拟环境会记录原电脑的 Python 路径，跨电脑复制容易失效。

首次安装需要联网，Label Studio 1.23.0 及依赖会占用一些时间和磁盘空间。Python 放在 `LS_lcad_reviewer\.python`，Label Studio 环境放在 `LS_lcad_reviewer\.venv`；安装缓存和临时文件可能在其他磁盘。

## 四、启动

每次使用前：

1. 保持 U 盘连接。
2. 双击 `02_start_lcad.cmd`。
3. 不要关闭黑色命令窗口。
4. 浏览器打开 <http://localhost:8080>。
5. 首次进入注册或登录师弟自己的本地账号。

脚本会把本地图片根目录自动设置为 `LS_lcad_reviewer` 所在的上一级目录，并把 Label Studio 数据库存到：

```text
LS_lcad_reviewer\data
```

如果 U 盘盘符改变，不需要修改脚本。

## 五、创建项目

在 Label Studio 页面点击 **Create Project**，项目名填写：

```text
QInsight_V4_Train_LCAD_师弟审核
```

### 配置标注界面

1. 打开项目的 **Labeling Setup**。
2. 切换到 **Code** 编辑模式。
3. 打开 `interface_dual_v4.xml`。
4. 全选复制，粘贴覆盖 Label Studio 的代码。
5. 保存配置。

这个模板包含：

- GT 参考图；
- lcad 上色图；
- A 缺色：未命中／命中；
- B 溢色、C 错色、D 偏色、E1 过饱和、E2 欠饱和、F 视觉自然度：无此缺陷／L1／L2／L3；
- 每个缺陷的描述框；
- 已核验／待复核状态；
- V4 的视觉自然度规则。

标注页面会隐藏左右两侧的任务列表和详情面板。两张图片并排放在相同的 260 × 260 展示框中，保持各自原始比例并完整显示；下方直接显示全部八组选项。需要查看判定规则或修改缺陷描述时，展开对应选项卡的「规则与描述」（审核状态为「规则与备注」）。

## 六、配置本地图片存储

这一步必须做，否则图片可能无法显示。

进入：

```text
Settings → Cloud Storage → Add Source Storage → Local Files
```

填写：

```text
Storage Title: U盘本地图片
Absolute local path: 实际存放图片的 9_14_10000GT_V1 文件夹的完整路径
```

例如 U 盘当前是 `E:`，就填：

```text
E:\9_14_10000GT_V1
```

如果当前是 `G:`，就填：

```text
G:\9_14_10000GT_V1
```

如果文件和本机一样放在 `D:\学业文件\MCL\上色评价_数据集标注` 下，就填：

```text
D:\学业文件\MCL\上色评价_数据集标注\9_14_10000GT_V1
```

点击 **Test Connection**，测试成功后点击 **Save / Add Storage**。只保存连接，不要点击 Save & Sync，因为任务将通过 JSON 导入，避免生成重复任务。

如果 Label Studio 要求选择 Import Method，选择 **Tasks**；不要让它扫描图片自动创建任务。

## 七、导入 10,000 条任务

1. 点击项目里的 **Import**。
2. 选择 `tasks_lcad_10000.json`。
3. 等待导入完成。
4. 确认任务数量约为 10,000。

不要重复点击 Import。同一个 JSON 导入两次，会产生重复任务。

## 八、显示 AI 预标注

在项目 Settings → Machine Learning 中，启用类似以下选项：

```text
Show predictions to annotators in the Label Stream and Quick View
```

模型版本选择 `V4`。Label Studio 的 prediction 是只读预标注，需要复制为人工 annotation 后再修改。若看不到可修改的表单，寻找 **Copy prediction / Create annotation from prediction** 按钮。

## 九、每张图片的核验方式

上方并排对比 GT 和 lcad 结果，下方修改预填结果。

### A 缺色

只选择：

- 未命中；
- 命中。

A 不分 L1-L3。命中 A 后最终评分按熔断规则为 1 分。

### B、C、D、E1、E2、F

每项选择：

- 无此缺陷；
- L1；
- L2；
- L3。

F 的名称是 **视觉自然度**，用于评估算法修复后的图片整体观感是否自然真实。L1-L3 的严重程度含义保持 V4 规则。

### 修改原则

- AI 误报：改为“无此缺陷”，描述可以清空。
- AI 漏报：选择对应严重程度，补充描述。
- 等级错误：直接改成正确的 L1、L2 或 L3。
- 不确定：选择“待复核”，在备注中写明原因。
- 已检查完成：选择“已核验”，再点击 **Submit**。

不要直接编辑原始 JSON。所有修改都在 Label Studio 页面完成。

## 十、每天保存和退出

每提交一张，确认页面显示提交成功。当天结束：

1. 提交当前任务；
2. 在黑色窗口按 Ctrl+C；
3. 等服务停止后再拔出 U 盘。

不要在 Label Studio 运行时直接拔出 U 盘，否则图片和数据库可能损坏。

## 十一、审核完成后的导出

1. 项目中点击 **Export**。
2. 选择完整 **JSON** 格式。
3. 不要选择 JSON_MIN、CSV、COCO 或 YOLO。
4. 下载完整 JSON 到 U 盘的 `LS_lcad_reviewer` 文件夹。
5. 把导出的 JSON 文件拖到 `03_export_lcad.cmd` 上。

转换后结果会放在：

```text
LS_lcad_reviewer\exports├─ reviewed_时间.json
└─ pending_时间.json
```

把以下文件交回给我或交回给师姐：

- 原始 Label Studio 完整导出 JSON；
- `reviewed_时间.json`；
- `pending_时间.json`（如果存在）；
- 如有争议，附上备注。

`reviewed` 文件中：

- A 命中会保留 A，severity 为空字符串，reviewed_score 为 1；
- 其他情况保留 B、C、D、E1、E2、F 的人工结果；
- `needs_rescoring=true` 表示需要使用原离线规则重新计算分数；
- 原始 AI 记录会保留在每条记录中。

## 十二、必须交回哪些文件

最低要求：

```text
reviewed_时间.json
```

建议同时交回：

```text
原始 Label Studio 完整 JSON 导出
pending_时间.json
```

不要只交截图，也不要只交修改后的几条记录。完整导出用于确认哪些图片已完成、哪些图片待复核。

## 十三、常见问题

### 图片不显示

检查：

1. U 盘是否仍连接；
2. 是否从 `02_start_lcad.cmd` 启动；
3. Local Files 路径是否填写当前 U 盘盘符下的 `9_14_10000GT_V1`；
4. 是否误用了原来的 `tasks_v4_train_lcad_10000.json`；
5. 是否把 `LS_lcad_reviewer` 放进了 `9_14_10000GT_V1` 内部。

### 启动时报 Python 路径错误

不要复制 `.venv`。删除或改名 `LS_lcad_reviewer\.venv` 后，重新双击 `01_install_lcad.cmd`。

### 任务数量重复

说明同一 JSON 被导入了两次。停止继续标注，先在项目数据列表确认重复情况，不要继续导入。

### 两台电脑看不到对方进度

这是正常的，因为两台电脑运行的是两个本地实例。完成后通过导出 JSON 合并，不会自动同步。

### 能否共享你的账号

各自本地实例不存在共享账号的必要。即使共用同一套远程 Label Studio 服务，也建议师弟使用独立账号；这样导出和审核历史能区分操作者。

## 十四、给师弟的最短流程

```text
确认 U 盘目录
→ 双击 01_install_lcad.cmd（只做一次）
→ 双击 02_start_lcad.cmd
→ 浏览器打开 localhost:8080
→ 创建项目
→ 粘贴 interface_dual_v4.xml
→ 配置 Local Files 到 9_14_10000GT_V1
→ 导入 tasks_lcad_10000.json
→ 复制 prediction 为 annotation
→ 逐张核验并选择“已核验”
→ Export 完整 JSON
→ 拖到 03_export_lcad.cmd
→ 交回 reviewed、pending 和完整导出 JSON
```

# 在线评测系统 - 架构与工作流

## 一、系统架构

技术栈
```
前端: Jinja2模板 + Bootstrap 5 + Font Awesome
后端: FastAPI + Starlette Session
数据: CSV文件 (无数据库)
执行: subprocess (Python/GCC)
```

### 核心模块

| 模块 | 文件 | 职责 |
|------|------|------|
| 路由层 | `main.py` | 8个API端点，处理所有HTTP请求 |
| 配置层 | `config.py` | 考生数据、目录路径、题型定义 |
| 评测引擎 | `utils/judge.py` | Python/C代码执行与结果比对 |
| 测试用例 | `testcase/` | JSON格式题目和测试数据 |
| 前端模板 | `templates/` | 登录页+主页，表单提交 |


### 工作流概览

```
考生登录 → 身份验证 → 进入主页
                ↓
        ┌───────┴───────┐
        ↓               ↓
    下载题目         上传代码
        ↓               ↓
    阅读题目      ┌──────┴──────┐
        ↓         ↓             ↓
    编写代码   文件上传      在线测试
        ↓         ↓             ↓
        └────→ 保存到       评测引擎
               uploads/         ↓
                          执行+比对结果
```


## 二、用户登录时序图

```mermaid
sequenceDiagram
    participant U as 考生
    participant F as 前端
    participant B as 后端
    participant D as 数据层

    U->>F: 1. 访问登录页 GET /
    F-->>U: 2. 返回登录表单

    U->>F: 3. 输入学号/密码/题型
    F->>B: 4. POST /login
    B->>D: 5. 查询 data.csv
    D-->>B: 6. 返回考生列表

    alt 验证通过
        B->>B: 7. 创建Session
        B-->>F: 8. 303重定向 /home
        F-->>U: 9. 显示主页面
    else 验证失败
        B-->>F: 7. 返回错误信息
        F-->>U: 8. 显示错误提示
    end
```

## 三、代码评测时序图

```mermaid
sequenceDiagram
    participant U as 考生
    participant F as 前端
    participant B as 后端
    participant J as 评测引擎
    participant E as 代码执行

    U->>F: 1. 输入代码+选择题目
    F->>B: 2. POST /test-code

    B->>B: 3. 验证Session
    B->>J: 4. 调用 test_code()

    J->>J: 5. 加载测试用例

    loop 遍历每个测试用例
        J->>E: 6. 执行代码(stdin输入)
        E-->>J: 7. 返回输出/错误/超时
        J->>J: 8. 比较输出与预期
    end

    J-->>B: 9. 返回评测结果列表
    B-->>F: 10. JSON响应
    F-->>U: 11. 显示评测结果
```

## 四、完整考试流程图

```mermaid
flowchart TD
    Start([开始]) --> Visit[访问系统首页]
    Visit --> Login[输入学号/密码/题型]
    Login --> Auth{验证身份}

    Auth -->|失败| Error[显示错误信息]
    Error --> Login

    Auth -->|成功| Home[进入主页面]
    Home --> Download[下载题目文件]
    Download --> Read[阅读题目要求]
    Read --> Solve[编写代码]

    Solve --> Submit{选择提交方式}

    Submit -->|文件上传| UploadFile[上传代码文件]
    UploadFile --> SaveFile[保存到 uploads/目录]
    SaveFile --> Message1[显示上传成功]

    Submit -->|在线代码| InputCode[在文本框输入代码]
    InputCode --> TestCode[点击测试代码]
    TestCode --> Judge[调用评测引擎]
    Judge --> Result{评测结果}

    Result -->|全部通过| Pass[显示AC状态]
    Result -->|部分失败| Fail[显示错误详情]
    Result -->|超时| TLE[显示超时]

    Fail --> Fix[修改代码]
    TLE --> Fix
    Fix --> Submit

    Pass --> Next{还有题目?}
    Message1 --> Next

    Next -->|是| Solve
    Next -->|否| Logout[退出登录]
    Logout --> End([结束])
```

## 五、数据流图

```mermaid
flowchart LR
    subgraph 外部实体
        Student[考生]
    end

    subgraph 处理过程
        P1[登录验证]
        P2[题目管理]
        P3[代码提交]
        P4[代码评测]
    end

    subgraph 数据存储
        D1[(考生数据<br/>data.csv)]
        D2[(测试用例<br/>testcase/)]
        D3[(提交记录<br/>uploads/)]
        D4[(题目文件<br/>downloads/)]
    end

    Student -->|学号/密码| P1
    P1 -->|查询| D1
    P1 -->|Session| Student

    Student -->|下载请求| P2
    P2 -->|读取| D4
    P2 -->|题目文件| Student

    Student -->|代码/文件| P3
    P3 -->|存储| D3

    Student -->|测试请求| P4
    P4 -->|读取| D2
    P4 -->|评测结果| Student
```

## 六、目录结构与文件映射

```
fastapi-oj/
├── main.py                  # 主应用入口 (路由定义)
│   ├── GET  /               # 登录页面
│   ├── POST /login          # 登录验证
│   ├── GET  /home           # 主页面
│   ├── GET  /download/{file}# 文件下载
│   ├── POST /upload-file    # 文件上传
│   ├── POST /upload-code    # 代码上传
│   ├── POST /test-code      # 代码评测
│   └── GET  /logout         # 退出登录
│
├── config.py                # 配置文件
│   ├── UPLOAD_DIR           # 上传目录: "uploads"
│   ├── DOWNLOAD_DIR         # 下载目录: "downloads"
│   ├── roles                # 题型: ["Python", "C", "MCU"]
│   ├── data                 # 考生数据 (pandas)
│   ├── ids                  # 考生ID集合
│   ├── prefix               # 学号前缀: "2"
│   └── size                 # 学号长度: 10
│
├── utils/
│   └── judge.py             # 评测引擎
│       ├── run_python_code()# Python代码执行
│       ├── run_c_code()     # C代码编译执行
│       └── test_code()      # 多测试用例评测
│
├── testcase/
│   ├── __init__.py          # 加载测试用例
│   ├── C.json               # C语言测试用例
│   └── Python.json          # Python测试用例
│
├── templates/
│   ├── login.html           # 登录页面模板
│   └── home.html            # 主页面模板
│
├── data.csv                 # 考生数据 (学号列表)
│
├── uploads/                 # 考生提交目录 (运行时创建)
│   ├── Python/
│   │   └── {id[3:7]}/
│   │       └── {id[7:]}/
│   │           ├── A.py
│   │           ├── B.py
│   │           └── Python_code.txt
│   ├── C/
│   └── MCU/
│
└── downloads/               # 题目文件目录 (需手动创建)
    ├── instruction.pdf      # 考试说明
    ├── Python.zip           # Python题目
    ├── C.zip                # C题目
    └── MCU.zip              # MCU题目
```

## 七、核心数据结构

### 测试用例格式 (testcase/*.json)
```json
{
    "name": "Python",
    "questions": {
        "A": {
            "name": "题目名称",
            "description": "题目描述",
            "test_cases": [
                {
                    "input": "输入数据",
                    "expected": "期望输出",
                    "time_limit": 1.0
                }
            ]
        }
    }
}
```

### 评测结果格式
```json
{
    "status": "success",
    "results": [
        {
            "test_case": 1,
            "status": "Passed|Failed|Time Limit Exceeded|Error",
            "message": "详细信息",
            "time": 0.123
        }
    ],
    "question_name": "题目名称"
}
```

### 文件上传路径规则
```
uploads/{role}/{id[3:7]}/{id[7:]}/{question}{extension}

示例:
uploads/Python/2222/2222/A.py
uploads/C/2222/2222/B.c
```
